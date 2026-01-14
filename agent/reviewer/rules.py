"""
Dockerfile Review Rules
=======================

Defines static best-practice rules for Dockerfile review.
Rules are deterministic and versioned.
"""

from typing import Dict, List


def review_base_image(dockerfile: str) -> List[Dict[str, str]]:
    issues = []

    if "FROM python" in dockerfile and "slim" not in dockerfile:
        issues.append({
            "level": "warning",
            "message": "Base image is not slim. Consider using python:X.Y-slim for smaller image size."
        })

    if ":latest" in dockerfile:
        issues.append({
            "level": "warning",
            "message": "Avoid using 'latest' tag for base images. Pin a specific version."
        })

    return issues


def review_user_security(dockerfile: str) -> List[Dict[str, str]]:
    issues = []

    if "USER" not in dockerfile:
        issues.append({
            "level": "warning",
            "message": "Container runs as root. Consider adding a non-root USER for security."
        })

    return issues


def review_dependency_installation(dockerfile: str) -> List[Dict[str, str]]:
    issues = []

    if "pip install" in dockerfile and "--no-cache-dir" not in dockerfile:
        issues.append({
            "level": "warning",
            "message": "pip install should use --no-cache-dir to reduce image size."
        })

    if "requirements.txt" in dockerfile and "COPY requirements.txt" not in dockerfile:
        issues.append({
            "level": "error",
            "message": "requirements.txt is referenced but not copied explicitly before installation."
        })

    return issues


def review_entrypoint(dockerfile: str) -> List[Dict[str, str]]:
    issues = []

    if "CMD" not in dockerfile and "ENTRYPOINT" not in dockerfile:
        issues.append({
            "level": "error",
            "message": "No CMD or ENTRYPOINT found. Container will not start."
        })

    return issues
