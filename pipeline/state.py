"""
State definition for the Self-Evaluating Lesson Content Generator LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional
from pipeline.rubric import EvaluationReport

class RejectionEntry(TypedDict):
    iteration: int
    failed_checkpoints: List[str]
    critiques: Dict[str, str]
    suggested_fixes: Dict[str, str]
    timestamp: str

class PipelineState(TypedDict):
    topic: str
    target_audience: str
    current_draft: str
    iteration: int
    max_retries: int
    evaluation: Optional[Dict[str, Any]]
    overall_passed: bool
    rejection_log: List[Dict[str, Any]]
    persistent_learnings: List[str]
    injected_error: Optional[str]  # e.g., 'unexplained_jargon', 'missing_analogy', 'dense_language'
    final_lesson: Optional[str]
    status: str
    log_messages: List[str]
