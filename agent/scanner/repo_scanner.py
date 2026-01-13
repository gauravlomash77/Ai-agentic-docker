"""
Repository Scanner
==================

Senior-grade deterministic scanner.
Collects structural facts from a repository while
explicitly excluding irrelevant and dangerous paths.
"""

from pathlib import Path
from typing import Dict, List, Set


IGNORED_DIRS: Set[str] = {
     ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
    ".ruff_cache",
}


IGNORED_EXTENSIONS: Set[str] = {
    ".pyc",
    ".log",
}


CONFIG_FILE_NAMES: Set[str] = {
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "Dockerfile",
    "docker-compose.yml",
    ".env",
}


def scan_repository(repo_path: Path) -> Dict[str, object]:
    """
    Scan a repository and collect deterministic facts.

    Args:
        repo_path (Path): Validated repository path

    Returns:
        Dict[str, object]: Structured repository metadata
    """
    files: List[str] = []
    extensions: Dict[str, int] = {}
    config_files: List[str] = []

    def walk(directory: Path):
        for item in directory.iterdir():
            if item.is_dir():
                if item.name in IGNORED_DIRS:
                    continue
                walk(item)
            elif item.is_file():
                if item.suffix in IGNORED_EXTENSIONS:
                    continue

                relative_path = str(item.relative_to(repo_path))
                files.append(relative_path)

                if item.suffix:
                    extensions[item.suffix] = extensions.get(item.suffix, 0) + 1

                if item.name in CONFIG_FILE_NAMES:
                    config_files.append(relative_path)

    walk(repo_path)

    return {
        "total_files": len(files),
        "files": sorted(files),
        "file_extensions": dict(sorted(extensions.items())),
        "config_files": sorted(config_files),
    }

