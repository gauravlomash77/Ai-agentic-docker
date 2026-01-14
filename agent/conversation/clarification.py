from typing import Dict, List


def build_clarification_questions(
    analyzer_output: Dict[str, object],
) -> List[Dict[str, object]]:
    """
    Build clarification questions based on analyzer output.

    Returns a list of structured questions.
    """
    questions: List[Dict[str, object]] = []

    entrypoint = analyzer_output.get("entrypoint", {})
    python_stack = analyzer_output.get("python_stack", {})

    # Case 1: Entrypoint confidence is not high
    if entrypoint.get("confidence") != "high":
        candidates = python_stack.get("entrypoint_candidates", [])

        if candidates:
            options = [
                f"{c['file']}:{c['variable']}" for c in candidates
            ]

            questions.append(
                {
                    "id": "entrypoint_selection",
                    "question": (
                        "Multiple possible application entrypoints were detected. "
                        "Which one should be used as the production entrypoint?"
                    ),
                    "options": options,
                }
            )

    return questions
