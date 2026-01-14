# agent/generator/base_generator.py

"""
Base Dockerfile Generator
=========================

Wires generator contract with safety policy.

This class:
- Enforces safety rules
- Never generates Dockerfiles yet
- Acts as a stable foundation for LLM or rule-based generators
"""

from agent.generator.contract import DockerfileGenerator
from agent.generator.types import GeneratorInput, GeneratorResult
from agent.policy.generator_policy import evaluate_generation_safety


class BaseDockerfileGenerator(DockerfileGenerator):
    """
    Canonical generator skeleton.

    This generator only:
    - Evaluates safety
    - Refuses or allows generation
    """

    def can_generate(self, input: GeneratorInput) -> bool:
        """
        Deterministically check if generation is allowed.
        """
        allowed, _ = evaluate_generation_safety(
            analyzer_output=input.analyzer_output,
            answered_questions=input.answered_questions,
        )
        return allowed

    def generate(self, input: GeneratorInput) -> GeneratorResult:
        """
        Enforce safety policy and return refusal or placeholder.
        """
        allowed, reasons = evaluate_generation_safety(
            analyzer_output=input.analyzer_output,
            answered_questions=input.answered_questions,
        )

        if not allowed:
            return GeneratorResult(
                dockerfile=None,
                confidence="low",
                warnings=[],
                refused=True,
                refusal_reason="; ".join(reasons),
            )

        # Placeholder success (NO Dockerfile yet)
        return GeneratorResult(
            dockerfile=None,
            confidence="high",
            warnings=[
                "Generation allowed, but no concrete generator is implemented yet."
            ],
            refused=False,
        )
