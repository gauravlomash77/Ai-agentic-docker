# agent/generator/contract.py

from abc import ABC, abstractmethod
from agent.generator.types import GeneratorInput, GeneratorResult


class DockerfileGenerator(ABC):
    """
    Abstract contract for Dockerfile generators.

    Implementations MAY use LLMs, but this interface is LLM-agnostic.
    """

    @abstractmethod
    def can_generate(self, input: GeneratorInput) -> bool:
        """
        Return True if generator has enough confidence to attempt generation.
        MUST be deterministic.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, input: GeneratorInput) -> GeneratorResult:
        """
        Generate a Dockerfile or refuse safely.

        MUST:
        - Never guess
        - Never hallucinate defaults
        - Refuse if unsafe
        """
        raise NotImplementedError
