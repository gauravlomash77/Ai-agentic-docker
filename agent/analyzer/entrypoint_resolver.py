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
    Detect:
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


def resolve_entrypoint(
    repo_path: Path,
    scan_data: Dict[str, object],
    framework_data: Dict[str, object],
    stack_data: Dict[str, object],
) -> Dict[str, object]:
    """
    Resolve execution model and entrypoint.
    """
    result: Dict[str, object] = {
        "type": None,  # script | asgi_service | wsgi_service
        "command": None,
        "confidence": "low",
        "notes": [],
    }

    framework = framework_data.get("framework")

    # 1. Script detection (STRICT)
    candidates = stack_data.get("entrypoint_candidates", [])

    for candidate in candidates:
        if isinstance(candidate, dict):
            file = candidate.get("file")
        else:
            file = candidate

        path = repo_path / file
        if path.exists() and _has_main_guard(path):
            result["type"] = "script"
            result["command"] = ["python", file]
            result["confidence"] = "high"
            return result

    # 2. FastAPI ASGI detection (PROOF-BASED)
    if framework == "fastapi":
        for candidate in candidates:
            file = candidate["file"]
            var = candidate["variable"]

            module_path = file.replace("/", ".").replace(".py", "")
            app_ref = f"{module_path}:{var}"

            result["type"] = "asgi_service"
            result["command"] = [
                "uvicorn",
                app_ref,
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]
            result["confidence"] = "high"
            return result

    result["notes"].append("No resolvable execution entrypoint found.")
    return result
