"""
Rubric Definition for Self-Evaluating Lesson Content Generator.
Enforces hard pass/fail checkpoints across 6 dimensions tailored for
a 12th-grade graduate from India (non-English medium background, starting from zero).
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class CheckpointResult(BaseModel):
    checkpoint_id: str
    name: str
    passed: bool = Field(description="Strict boolean pass (True) or fail (False). No partial credit.")
    score: int = Field(description="1 for Pass, 0 for Fail.")
    critique: str = Field(description="Specific evidence or reason for passing or failing.")
    suggested_fix: str = Field(default="", description="Concrete guidance for the generator if failed.")

class EvaluationReport(BaseModel):
    overall_passed: bool = Field(description="True ONLY if all 6 checkpoints pass.")
    total_score: int = Field(description="Number of passed checkpoints out of 6.")
    checkpoints: Dict[str, CheckpointResult]
    summary: str
    identified_jargon: List[str] = Field(default_factory=list)
    average_sentence_length: float = Field(default=0.0)

RUBRIC_CHECKPOINTS: Dict[str, Dict[str, Any]] = {
    "ACCURATE_AND_GROUNDED": {
        "id": "ACCURATE_AND_GROUNDED",
        "name": "Accurate & Grounded",
        "description": "Technical mechanics of RAG are factually correct. No false claims or misconceptions.",
        "pass_criteria": (
            "Must correctly explain that RAG combines a search/retrieval system with a generative LLM. "
            "Must clarify that RAG does NOT retrain or update the base model weights, but injects retrieved "
            "context into the prompt. Factual statements about LLMs (static cutoff, hallucinations) must be true."
        ),
        "fail_criteria": (
            "Claims that RAG permanently retrains the LLM, hallucinates false facts, or mischaracterizes "
            "how retrieval and generation interact."
        )
    },
    "TEACHES_BY_EXAMPLE": {
        "id": "TEACHES_BY_EXAMPLE",
        "name": "Teaches by Example (Relatable Analogy)",
        "description": "Uses an intuitive, culturally accessible, real-world analogy and walks through a concrete query.",
        "pass_criteria": (
            "Must use a clear real-world analogy relatable to a 12th-grade student (e.g., an Open-Book Exam "
            "where you don't memorize everything but look up the textbook chapter, or a hospital doctor checking patient records). "
            "Must trace a step-by-step example with an actual question and answer."
        ),
        "fail_criteria": (
            "Teaches purely through abstract theory without a grounding analogy, or the analogy is confusing, "
            "foreign, or disconnected from the core concept."
        )
    },
    "COVERS_KEY_POINTS": {
        "id": "COVERS_KEY_POINTS",
        "name": "Covers Key Points",
        "description": "Must thoroughly cover the 5 essential pillars of RAG.",
        "pass_criteria": (
            "Must cover: (1) What RAG stands for and simple definition; (2) Why it is needed (LLM knowledge cutoff "
            "and hallucination/making up facts); (3) The Retriever role (finding relevant info); (4) The Generator "
            "role (synthesizing the final answer); (5) End-to-end flow from user query to verified response."
        ),
        "fail_criteria": (
            "Omits any of the 5 pillars (e.g. fails to explain why hallucination happens, or omits the retriever's exact role)."
        )
    },
    "BEGINNER_FRIENDLY_LANGUAGE": {
        "id": "BEGINNER_FRIENDLY_LANGUAGE",
        "name": "Beginner-Friendly Language",
        "description": "Adapted for a 12th-grade Indian student from a non-English-medium background.",
        "pass_criteria": (
            "Sentences are simple, crisp, and direct (average sentence length <= 20 words). Uses conversational, "
            "encouraging, and accessible phrasing. Uses Indian cultural familiarity where helpful (e.g., school exam, library, diary)."
        ),
        "fail_criteria": (
            "Dense, academic, convoluted sentences. Heavy Latinate vocabulary (e.g., 'concomitant', 'obviate', 'epistemological', 'juxtapose')."
        )
    },
    "NO_UNEXPLAINED_JARGON": {
        "id": "NO_UNEXPLAINED_JARGON",
        "name": "Clear, No Unexplained Jargon",
        "description": "Zero unexplained technical buzzwords. Every technical term introduced must be immediately defined in plain words.",
        "pass_criteria": (
            "If technical terms appear (e.g. 'LLM', 'Hallucination', 'Retriever', 'Embeddings', 'Vector Database', "
            "'Prompt', 'Knowledge Cutoff'), each is explicitly defined in plain words at the exact place it appears."
        ),
        "fail_criteria": (
            "Drops technical buzzwords without explanation (e.g. 'uses dense vector embeddings with cosine similarity', "
            "'tokenized context window', 'parametric memory') leaving the student confused."
        )
    },
    "COHERENT_TEACHING_FLOW": {
        "id": "COHERENT_TEACHING_FLOW",
        "name": "Coherent Teaching Flow & Knowledge Check",
        "description": "Pedagogical structure follows a clear progression with an interactive check for understanding.",
        "pass_criteria": (
            "Structured in 6 clear stages: (1) The Hook / Problem; (2) The Relatable Analogy; (3) Plain English Definition; "
            "(4) Step-by-Step Mechanism (Retrieve -> Augment -> Generate); (5) Concrete Walkthrough Example; "
            "(6) Knowledge Check / 3-question practice quiz with clear answers."
        ),
        "fail_criteria": (
            "Disorganized structure, abrupt jumps between concepts, missing the problem context, or omitting the knowledge check."
        )
    }
}
