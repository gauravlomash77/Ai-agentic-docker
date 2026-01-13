"""
Framework Detector
==================

Detects Python web frameworks and runtime characteristics
using import inspection and structural evidence.

This module is:
- Deterministic
- Evidence-based
- Conservative in conclusions
"""

from pathlib import Path
from typing import Dict, List, Optional


FRAMEWORK_IMPORTS = {
    "fastapi": "fastapi",
    "django": "django",
    "flask": "flask",
}

RUNTIME_IMPORTS = {
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
}

DEFAULT_PORTS = {
    "fastapi": 8000,
    "flask": 5000,
    "django": 8000,
}


def _scan_imports(repo_path: Path, files: List[str]) -> Dict[str, List[str]]:
    """
    Scan Python files for framework/runtime imports.

    Returns:
        Dict[str, List[str]]: Found imports by category
    """
    found = {
        "frameworks": [],
        "runtimes": [],
    }

    for file in files:
        if not file.endswith(".py"):
            continue

        try:
            content = (repo_path / file).read_text(errors="ignore")
        except Exception:
            continue

        for name, token in FRAMEWORK_IMPORTS.items():
            if f"import {token}" in content or f"from {token}" in content:
                found["frameworks"].append(name)

        for name, token in RUNTIME_IMPORTS.items():
            if f"import {token}" in content or f"from {token}" in content:
                found["runtimes"].append(name)

    return found


def detect_framework(
    repo_path: Path,
    scan_data: Dict[str, object],
    stack_data: Dict[str, object],
) -> Dict[str, object]:
    """
    Detect Python web framework and runtime characteristics.

    Args:
        repo_path (Path): Repository root
        scan_data (Dict): Repository scan output
        stack_data (Dict): Python stack detection output

    Returns:
        Dict[str, object]: Framework analysis
    """
    files: List[str] = scan_data.get("files", [])

    result = {
        "framework": None,
        "interface": None,  # ASGI / WSGI
        "runtime_server": None,
        "default_port": None,
        "confidence": "low",
        "notes": [],
    }

    if not stack_data.get("is_python_project"):
        result["notes"].append("Not a Python project.")
        return result

    imports = _scan_imports(repo_path, files)

    # Framework detection
    detected_frameworks = list(set(imports["frameworks"]))
    if len(detected_frameworks) == 1:
        framework = detected_frameworks[0]
        result["framework"] = framework
        result["confidence"] = "medium"

        if framework == "fastapi":
            result["interface"] = "ASGI"
        elif framework == "django":
            result["interface"] = "ASGI/WSGI"
        elif framework == "flask":
            result["interface"] = "WSGI"

        result["default_port"] = DEFAULT_PORTS.get(framework)

    elif len(detected_frameworks) > 1:
        result["notes"].append(
            f"Multiple frameworks detected: {detected_frameworks}. Manual review required."
        )
        return result
    else:
        result["notes"].append("No known Python web framework imports detected.")
        return result

    # Runtime server detection
    detected_runtimes = list(set(imports["runtimes"]))
    if detected_runtimes:
        if len(detected_runtimes) == 1:
            result["runtime_server"] = detected_runtimes[0]
            result["confidence"] = "high"
        else:
            result["notes"].append(
                f"Multiple runtime servers detected: {detected_runtimes}."
            )

    return result
