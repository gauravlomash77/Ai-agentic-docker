from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConversationState:
    """
    Explicit, controlled memory for a single agent session.
    """

    session_id: str
    repo_path: Optional[str] = None

    analysis_completed: bool = False
    analysis_confidence: Optional[str] = None

    analyzer_output: Optional[Dict[str, object]] = None

    clarifications_required: bool = False
    pending_questions: List[Dict[str, object]] = field(default_factory=list) 
    answered_questions: Dict[str, str] = field(default_factory=dict) 

    generation_requested: bool = False
    generation_completed: bool = False

    # Adding  fields to ConversationState

    generator_result: Optional[Dict[str, object]] = None
    generation_error: Optional[str] = None

