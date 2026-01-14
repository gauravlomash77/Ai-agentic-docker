# agent/policy/generator_policy.py

"""
Generator Safety Policy
=======================

Authoritative refusal and safety rules for Dockerfile generation.

This module:
- Is deterministic
- Never calls LLMs
- Never guesses
- Produces explicit refusal reasons
"""

from typing import Dict, List, Tuple


def evaluate_generation_safety(
    analyzer_output: Dict[str, object],
    answered_questions: Dict[str, str],
) -> Tuple[bool, List[str]]:
    """
    Evaluate whether Dockerfile generation is SAFE.

    Returns:
        (allowed, reasons)

    If allowed is False, reasons MUST explain why.
    """
    reasons: List[str] = []

    python_stack = analyzer_output.get("python_stack", {})
    framework = analyzer_output.get("framework", {})
    entrypoint = analyzer_output.get("entrypoint", {})

    # 1. Python project certainty
    if not python_stack.get("is_python_project"):
        reasons.append("Repository is not a confirmed Python project.")

    if python_stack.get("confidence") != "high":
        reasons.append("Python stack confidence is not high.")

    # 2. Dependency management must be known
    if not python_stack.get("dependency_management"):
        reasons.append("Python dependency management is unknown.")

    # 3. Framework certainty
    if framework.get("confidence") != "high":
        reasons.append("Framework detection confidence is not high.")

    if not framework.get("framework"):
        reasons.append("Application framework is not detected.")

    if not framework.get("interface"):
        reasons.append("Application interface (ASGI/WSGI) is not detected.")

    # 4. Entrypoint certainty
    if entrypoint.get("confidence") != "high":
        reasons.append("Entrypoint resolution confidence is not high.")

    if not entrypoint.get("command"):
        reasons.append("Entrypoint command is missing.")

    # 5. Clarification completeness
    if answered_questions is None:
        reasons.append("Clarification answers missing.")

    # 6. No conflicting answers
    if answered_questions:
        for key, value in answered_questions.items():
            if not value:
                reasons.append(f"Clarification '{key}' has no answer.")

    allowed = len(reasons) == 0
    return allowed, reasons
