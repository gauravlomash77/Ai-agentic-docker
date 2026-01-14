# agent/generator/fastapi_generator.py

"""
FastAPI Dockerfile Generator (Rules-Only)
=========================================

Deterministic Dockerfile generator for FastAPI applications.

- No LLM
- No guessing
- Enforces analyzer + policy outputs
"""

from typing import List

from agent.generator.contract import DockerfileGenerator
from agent.generator.types import GeneratorInput, GeneratorResult
from agent.policy.generator_policy import evaluate_generation_safety


class FastAPIDockerfileGenerator(DockerfileGenerator):
    """
    Production-grade Dockerfile generator for FastAPI apps.
    """

    def can_generate(self, input: GeneratorInput) -> bool:
        allowed, _ = evaluate_generation_safety(
            analyzer_output=input.analyzer_output,
            answered_questions=input.answered_questions,
        )

        framework = input.analyzer_output.get("framework", {})
        return (
            allowed
            and framework.get("framework") == "fastapi"
            and framework.get("interface") == "ASGI"
        )

    def generate(self, input: GeneratorInput) -> GeneratorResult:
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

        framework = input.analyzer_output.get("framework", {})
        entrypoint = input.analyzer_output.get("entrypoint", {})
        python_stack = input.analyzer_output.get("python_stack", {})

        if framework.get("framework") != "fastapi":
            return self._refuse("Not a FastAPI project")

        if framework.get("interface") != "ASGI":
            return self._refuse("FastAPI app is not ASGI")

        dependency_file = python_stack.get("dependency_management")
        if not dependency_file:
            return self._refuse("Dependency file not detected")

        command: List[str] = entrypoint.get("command", [])
        if not command:
            return self._refuse("Entrypoint command missing")

        dockerfile = self._build_dockerfile(
            dependency_file=dependency_file,
            command=command,
            port=framework.get("default_port", 8000),
        )

        return GeneratorResult(
            dockerfile=dockerfile,
            confidence="high",
            warnings=[],
            refused=False,
        )

    # -------------------------
    # Internal helpers
    # -------------------------

    def _build_dockerfile(
        self, dependency_file: str, command: List[str], port: int
    ) -> str:
        """
        Build deterministic FastAPI Dockerfile.
        """
        cmd_json = ", ".join(f'"{c}"' for c in command)

        return f"""
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY {dependency_file} .
RUN pip install --no-cache-dir -r {dependency_file}

COPY . .

EXPOSE {port}

CMD [{cmd_json}]
""".strip()

    def _refuse(self, reason: str) -> GeneratorResult:
        return GeneratorResult(
            dockerfile=None,
            confidence="low",
            warnings=[],
            refused=True,
            refusal_reason=reason,
        )
