"""
Clarification Question Builder
==============================

Builds deterministic clarification questions when analyzer output
is insufficient for safe Dockerfile generation.

This module:
- Never guesses
- Never mutates state
- Produces structured, answerable questions
"""

from typing import Dict, List


def build_clarification_questions(
    analyzer_output: Dict[str, object],
) -> List[Dict[str, object]]:
    """
    Build clarification questions based on analyzer output.

    Args:
        analyzer_output (dict): Full analyzer result

    Returns:
        List of clarification question objects
    """
    questions: List[Dict[str, object]] = []

    python_stack = analyzer_output.get("python_stack", {})
    entrypoint = analyzer_output.get("entrypoint", {})

    # Case 1: Entrypoint ambiguity
    if entrypoint.get("confidence") != "high":
        candidates = python_stack.get("entrypoint_candidates", [])

        if candidates:
            options = [
                f"{c['file']}:{c['variable']}"
                for c in candidates
                if "file" in c and "variable" in c
            ]

            if options:
                questions.append(
                    {
                        "id": "entrypoint_selection",
                        "type": "selection",
                        "question": (
                            "Multiple possible FastAPI application entrypoints were detected. "
                            "Which one should be used as the production entrypoint?"
                        ),
                        "options": options,
                    }
                )

    return questions
