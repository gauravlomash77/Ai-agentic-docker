"""
Conversation Orchestrator
=========================

Controls the flow of:
1. Repository analysis
2. Clarification (if required)
3. Dockerfile generation

This is the SINGLE authority for agent flow.
"""

import uuid
from typing import Dict, List

from agent.conversation.state import ConversationState
from agent.conversation.clarification import build_clarification_questions
from agent.scanner.repo_scanner import scan_repository
from agent.analyzer.stack_detector import detect_python_stack
from agent.analyzer.framework_detector import detect_framework
from agent.analyzer.entrypoint_resolver import resolve_entrypoint
from agent.generator.registry import GeneratorRegistry
from agent.generator.types import GeneratorInput


class ConversationOrchestrator:
    """
    Controls the flow of analysis, clarification, and generation.
    This is the brain of the agent.
    """

    def __init__(self) -> None:
        self.state = ConversationState(session_id=str(uuid.uuid4()))

    # -------------------------
    # Step 1: Input handling
    # -------------------------

    def set_repo_path(self, repo_path: str) -> None:
        self.state.repo_path = repo_path

    # -------------------------
    # Step 2: Deterministic analysis
    # -------------------------

    def run_analysis(self) -> Dict[str, object]:
        if not self.state.repo_path:
            raise RuntimeError("Repository path not set")

        scan_data = scan_repository(self.state.repo_path)

        stack = detect_python_stack(self.state.repo_path, scan_data)

        framework = detect_framework(
            repo_path=self.state.repo_path,
            scan_data=scan_data,
            stack_data=stack,
        )

        entrypoint = resolve_entrypoint(
            repo_path=self.state.repo_path,
            scan_data=scan_data,
            framework_data=framework,
            stack_data=stack,
        )

        analyzer_output = {
            "repository": scan_data,
            "python_stack": stack,
            "framework": framework,
            "entrypoint": entrypoint,
        }

        self.state.analyzer_output = analyzer_output
        self.state.analysis_completed = True

        confidences = [
            stack.get("confidence", "low"),
            framework.get("confidence", "low"),
            entrypoint.get("confidence", "low"),
        ]

        self.state.analysis_confidence = self._lowest_confidence(confidences)

        return analyzer_output

    # -------------------------
    # Step 3: Confidence helper
    # -------------------------

    def _lowest_confidence(self, values: List[str]) -> str:
        """
        Determine the lowest confidence level.
        PRIVATE helper.
        """
        order = {"low": 0, "medium": 1, "high": 2}
        return min(values, key=lambda v: order.get(v, 0))

    # -------------------------
    # Step 4: Flow decision
    # -------------------------

    def evaluate_next_action(self) -> str:
        """
        Decide what the agent should do next.
        This is the SINGLE flow authority.
        """
        if not self.state.analysis_completed:
            return "NEEDS_ANALYSIS"

        if self.state.analysis_confidence != "high":
            questions = build_clarification_questions(
                self.state.analyzer_output or {}
            )

            if questions:
                self.state.pending_questions = questions
                self.state.clarifications_required = True
                return "NEEDS_CLARIFICATION"

            return "REFUSED"

        if not self.state.generation_requested:
            return "READY_FOR_GENERATION"

        return "DONE"

    # -------------------------
    # Step 5: Clarification answers
    # -------------------------

    def submit_clarification_answers(self, answers: Dict[str, str]) -> None:
        """
        Accept clarification answers and update state.
        """
        for qid, answer in answers.items():
            self.state.answered_questions[qid] = answer

        pending_ids = {q["id"] for q in self.state.pending_questions}
        answered_ids = set(self.state.answered_questions.keys())

        if pending_ids.issubset(answered_ids):
            self.state.pending_questions = []
            self.state.clarifications_required = False
            self.state.analysis_confidence = "high"

    # -------------------------
    # Step 6: Generator execution
    # -------------------------

    def run_generation(self) -> Dict[str, object]:
        """
        Execute Dockerfile generation using selected generator.
        """
        if not self.state.analysis_completed:
            raise RuntimeError("Analysis not completed")

        if self.state.analysis_confidence != "high":
            raise RuntimeError("Generation not allowed due to low confidence")

        # Mark intent (important for flow correctness)
        self.state.generation_requested = True

        input_data = GeneratorInput(
            analyzer_output=self.state.analyzer_output or {},
            answered_questions=self.state.answered_questions,
        )

        registry = GeneratorRegistry()
        generator = registry.select(input_data)

        if not generator:
            self.state.generation_error = "No suitable generator found"
            self.state.generation_completed = True
            return {
                "status": "refused",
                "reason": "No suitable generator available for this project",
            }

        result = generator.generate(input_data)

        self.state.generator_result = {
            "dockerfile": result.dockerfile,
            "confidence": result.confidence,
            "warnings": result.warnings,
            "refused": result.refused,
            "refusal_reason": result.refusal_reason,
        }

        self.state.generation_completed = True

        if result.refused:
            return {
                "status": "refused",
                "reason": result.refusal_reason,
            }

        return {
            "status": "generated",
            "dockerfile": result.dockerfile,
            "confidence": result.confidence,
        }
