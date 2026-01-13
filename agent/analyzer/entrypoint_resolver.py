"""
Entrypoint Resolver
===================

Determines how a Python project is executed:
- Script (python main.py)
- ASGI service (uvicorn module:app)
- WSGI service (gunicorn module:app)

Uses AST inspection to avoid false positives.
"""

import ast
from pathlib import Path
from typing import Dict, List


def _has_main_guard(file_path: Path) -> bool:
    """
    Detects if file contains:
        if __name__ == "__main__":
    """
    try:
        tree = ast.parse(file_path.read_text())
    except Exception:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                condition = ast.unparse(node.test)
            except Exception:
                continue
            if '__name__ == "__main__"' in condition:
                return True
    return False


def _detect_app_object(file_path: Path) -> bool:
    """
    Detects ASGI / WSGI app object.
    Example:
        app = FastAPI()
        app = Flask(__name__)
    """
    try:
        tree = ast.parse(file_path.read_text())
    except Exception:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "app":
                    return True
    return False


def resolve_entrypoint(
    repo_path: Path,
    scan_data: Dict[str, object],
    framework_data: Dict[str, object],
    stack_data: Dict[str, object],
) -> Dict[str, object]:
    """
    Resolve execution model and entrypoint.
    """
    result = {
        "type": None,          # script | asgi_service | wsgi_service
        "command": None,
        "confidence": "low",
        "notes": [],
    }

    # ONLY user-level entrypoint candidates (never agent internals)
    entrypoint_candidates: List[str] = stack_data.get("entrypoint_candidates", [])

    # 1. Script detection (STRICT)
    for file in entrypoint_candidates:
        path = repo_path / file
        if path.exists() and _has_main_guard(path):
            result["type"] = "script"
            result["command"] = ["python", file]
            result["confidence"] = "high"
            return result

    # 2. Service detection
    framework = framework_data.get("framework")
    interface = framework_data.get("interface")

    if framework and interface:
        for file in entrypoint_candidates:
            path = repo_path / file
            if path.exists() and _detect_app_object(path):
                module_path = file.replace("/", ".").replace(".py", "")
                app_ref = f"{module_path}:app"

                if interface == "ASGI":
                    result["type"] = "asgi_service"
                    result["command"] = [
                        "uvicorn",
                        app_ref,
                        "--host",
                        "0.0.0.0",
                    ]
                else:
                    result["type"] = "wsgi_service"
                    result["command"] = ["gunicorn", app_ref]

                result["confidence"] = "high"
                return result

    result["notes"].append("No resolvable execution entrypoint found.")
    return result
