# agent/generator/types.py

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class GeneratorInput:
    """
    Immutable input provided to the Dockerfile generator.
    """

    analyzer_output: Dict[str, object]
    answered_questions: Dict[str, str]


@dataclass
class GeneratorResult:
    """
    Result returned by a generator attempt.
    """

    dockerfile: Optional[str]
    confidence: str                 # low | medium | high
    warnings: List[str]
    refused: bool
    refusal_reason: Optional[str] = None
