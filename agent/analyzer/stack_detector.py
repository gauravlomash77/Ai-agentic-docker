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

import ast
from pathlib import Path
from typing import Dict, List


PYTHON_DEP_FILES = {
    "requirements.txt",
    "pyproject.toml",
}


def _detect_fastapi_apps(repo_path: Path, files: List[str]) -> List[Dict[str, str]]:
    """
    Detect FastAPI app instantiations using AST.

    Returns:
        List of dicts with keys: file, variable
    """
    apps: List[Dict[str, str]] = []

    for file in files:
        if not file.endswith(".py"):
            continue

        path = repo_path / file
        try:
            tree = ast.parse(path.read_text())
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "FastAPI":
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            apps.append(
                                {
                                    "file": file,
                                    "variable": target.id,
                                }
                            )
    return apps


def detect_python_stack(
    repo_path: Path,
    scan_data: Dict[str, object],
) -> Dict[str, object]:
    """
    Detect Python backend characteristics.
    """
    files: List[str] = scan_data.get("files", [])
    extensions: Dict[str, int] = scan_data.get("file_extensions", {})

    result: Dict[str, object] = {
        "is_python_project": False,
        "confidence": "low",
        "dependency_management": None,
        "entrypoint_candidates": [],
        "notes": [],
    }

    # 1. Detect Python presence
    if ".py" not in extensions:
        result["notes"].append("No Python source files detected.")
        return result

    result["is_python_project"] = True
    result["confidence"] = "medium"

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

    # 3. Detect FastAPI app definitions (PROOF-BASED)
    fastapi_apps = _detect_fastapi_apps(repo_path, files)

    if fastapi_apps:
        # Prefer apps under app/
        sorted_apps = sorted(
            fastapi_apps,
            key=lambda x: (not x["file"].startswith("app/"), x["file"]),
        )

        result["entrypoint_candidates"] = sorted_apps
        result["confidence"] = "high"
    else:
        result["notes"].append("No FastAPI app instantiation found.")

    return result
