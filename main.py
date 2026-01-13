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
import json
from pathlib import Path
from typing import NoReturn
from agent.analyzer.stack_detector import detect_python_stack
from agent.scanner.repo_scanner import scan_repository
from agent.analyzer.framework_detector import detect_framework


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
    """
    print("[INFO] Dockerization Agent initialized")
    print(f"[INFO] Analyzing repository: {repo_path}")

    scan_data = scan_repository(repo_path)
    print("[INFO] Repository scan completed")

    stack_analysis = detect_python_stack(repo_path, scan_data)
    print("[INFO] Python stack analysis completed")

    framework_analysis = detect_framework(
        repo_path=repo_path,
        scan_data=scan_data,
        stack_data=stack_analysis,
    )
    print("[INFO] Framework analysis completed")

    print(json.dumps(
        {
            "repository": scan_data,
            "python_stack": stack_analysis,
            "framework": framework_analysis,
        },
        indent=2
    ))

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
