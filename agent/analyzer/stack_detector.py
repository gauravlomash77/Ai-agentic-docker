"""
Python Stack Detector
=====================

Senior-grade deterministic analyzer that infers Python backend
characteristics from repository scan metadata.

This module:
- Makes evidence-based conclusions only
- Assigns confidence levels
- Never guesses entrypoints
"""

from pathlib import Path
from typing import Dict, List


PYTHON_DEP_FILES = {
    "requirements.txt",
    "pyproject.toml",
}

COMMON_ENTRY_FILES = {
    "main.py",
    "app.py",
    "wsgi.py",
    "asgi.py",
}


def detect_python_stack(repo_path: Path, scan_data: Dict[str, object]) -> Dict[str, object]:
    """
    Detect Python backend characteristics.

    Args:
        repo_path (Path): Repository root
        scan_data (Dict): Output from repository scanner

    Returns:
        Dict[str, object]: Python stack analysis
    """
    files: List[str] = scan_data.get("files", [])
    extensions: Dict[str, int] = scan_data.get("file_extensions", {})

    result = {
        "is_python_project": False,
        "confidence": "low",
        "dependency_management": None,
        "entrypoint_candidates": [],
        "notes": [],
    }

    # 1. Detect Python presence
    if ".py" in extensions:
        result["is_python_project"] = True
        result["confidence"] = "medium"
    else:
        result["notes"].append("No Python source files detected.")
        return result

    # 2. Detect dependency management
    for dep_file in PYTHON_DEP_FILES:
        if dep_file in files:
            result["dependency_management"] = dep_file
            result["confidence"] = "high"
            break

    if result["dependency_management"] is None:
        result["notes"].append(
            "No standard Python dependency file found (requirements.txt / pyproject.toml)."
        )

    # 3. Detect entrypoint candidates (non-guessing)
    for file in files:
        filename = Path(file).name
        if filename in COMMON_ENTRY_FILES:
            result["entrypoint_candidates"].append(file)

    if not result["entrypoint_candidates"]:
        result["notes"].append(
            "No common Python entrypoint files found."
        )

    return result
