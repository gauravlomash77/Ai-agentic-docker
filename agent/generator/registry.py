# agent/generator/registry.py

"""
Generator Registry
==================

Selects the appropriate Dockerfile generator
based on analyzer output.

No orchestration. No LLM. No side effects.
"""

from typing import List, Optional

from agent.generator.contract import DockerfileGenerator
from agent.generator.fastapi_generator import FastAPIDockerfileGenerator
from agent.generator.types import GeneratorInput


class GeneratorRegistry:
    """
    Registry for available Dockerfile generators.
    """

    def __init__(self) -> None:
        self._generators: List[DockerfileGenerator] = [
            FastAPIDockerfileGenerator(),
        ]

    def select(self, input: GeneratorInput) -> Optional[DockerfileGenerator]:
        """
        Select the first generator that can handle the input.
        """
        for generator in self._generators:
            if generator.can_generate(input):
                return generator
        return None
