"""
Dockerization Agent
===================

Senior-grade DevOps assistant that analyzes backend repositories
and prepares deterministic metadata for Dockerization.

Phase-1:
- Repository analysis only
- No Dockerfile generation
"""

import argparse
import sys
from pathlib import Path
from typing import NoReturn


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Senior-grade Dockerization Agent"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a backend repository and detect stack details"
    )
    analyze_parser.add_argument(
        "repo_path",
        type=str,
        help="Absolute or relative path to backend repository"
    )

    return parser.parse_args()


def validate_repo_path(repo_path: str) -> Path:
    """
    Validate repository path.

    Args:
        repo_path (str): Path provided by user

    Returns:
        Path: Validated Path object

    Raises:
        SystemExit: If path is invalid
    """
    path = Path(repo_path).resolve()

    if not path.exists():
        print(f"[ERROR] Repository path does not exist: {path}")
        sys.exit(1)

    if not path.is_dir():
        print(f"[ERROR] Repository path is not a directory: {path}")
        sys.exit(1)

    return path


def run_analysis(repo_path: Path) -> NoReturn:
    """
    Run repository analysis.

    Phase-1 behavior:
    - Placeholder for deterministic scanning
    - Will be replaced with real scanner module

    Args:
        repo_path (Path): Validated repository path
    """
    print("[INFO] Dockerization Agent initialized")
    print(f"[INFO] Analyzing repository: {repo_path}")

    # Placeholder until scanner is implemented
    print("[INFO] Phase-1 analysis not yet implemented")
    print("[INFO] Next step: repository scanning and stack detection")

    sys.exit(0)


def main() -> NoReturn:
    """
    Main entry point.
    """
    args = parse_args()

    if args.command == "analyze":
        repo_path = validate_repo_path(args.repo_path)
        run_analysis(repo_path)

    # Defensive fallback (should never happen)
    print("[ERROR] Unknown command")
    sys.exit(1)


if __name__ == "__main__":
    main()
