"""
Generator Agent for Beginner AI Lessons.
Generates structured, highly accessible lessons adapted for a 12th-grade
Indian student from a non-English-medium background.
"""

from typing import List, Dict, Any, Optional
from pipeline.llm_factory import LLMProvider

class GeneratorAgent:
    def __init__(self, provider: str = "auto"):
        self.llm = LLMProvider(provider=provider)

    def generate_draft(
        self,
        topic: str,
        target_audience: str,
        persistent_learnings: List[str],
        iteration: int = 1,
        rejection_feedback: Optional[Dict[str, Any]] = None,
        injected_error: Optional[str] = None
    ) -> str:
        """
        Generates a lesson draft.
        If rejection_feedback is provided, integrates specific failure critiques to correct the draft.
        If injected_error is specified, deliberately includes that failure mode for demonstration purposes.
        """
        system_prompt = self._build_system_prompt(target_audience, persistent_learnings)
        user_prompt = self._build_user_prompt(
            topic=topic,
            iteration=iteration,
            rejection_feedback=rejection_feedback,
            injected_error=injected_error
        )

        return self.llm.generate(prompt=user_prompt, system_prompt=system_prompt)

    def _build_system_prompt(self, target_audience: str, persistent_learnings: List[str]) -> str:
        learned_rules_block = "\n".join([f"- {rule}" for rule in persistent_learnings]) if persistent_learnings else "- None yet."

        return f"""You are an elite GenAI Content Engineer specializing in beginner pedagogical systems.
Your job is to teach advanced AI concepts to:
Target Audience: {target_audience}
(12th-grade graduate from India, limited English vocabulary, non-English-medium background, eager to start an AI career).

CORE PEDAGOGICAL GUIDELINES:
1. Plain, Crisp English: Average sentence length must be under 20 words. No complex academic jargon.
2. Relatable Analogy: Anchor the concept in a familiar Indian student experience (e.g. Open-Book vs Closed-Book Exam, library, clinic).
3. Zero Unexplained Jargon: If introducing any technical acronym or term (e.g. LLM, Hallucination, Retriever, Vector), explain it immediately in plain words in brackets.
4. Structured Flow:
   - 1. The Hook / Problem (Why AI makes mistakes)
   - 2. The Analogy (Open-Book Exam)
   - 3. Definition (What RAG stands for)
   - 4. How It Works (Retrieve -> Augment -> Generate)
   - 5. Real-World Walkthrough (A clinic or school example)
   - 6. Quick Knowledge Check (3 test-yourself questions with answers)

SHARPENED RULES LEARNED FROM PRIOR SYSTEM FAILURES:
{learned_rules_block}
"""

    def _build_user_prompt(
        self,
        topic: str,
        iteration: int,
        rejection_feedback: Optional[Dict[str, Any]],
        injected_error: Optional[str]
    ) -> str:
        base_prompt = f"Write a complete, standalone beginner lesson on the topic: '{topic}'."

        if injected_error == "unexplained_jargon":
            return base_prompt + "\n\nINJECT_ERROR: UNEXPLAINED_JARGON. (Demonstration mode: Include complex unexplained mathematical vector terms without definitions)."
        elif injected_error == "missing_analogy":
            return base_prompt + "\n\nINJECT_ERROR: MISSING_ANALOGY. (Demonstration mode: Skip the real-world exam analogy)."
        elif injected_error == "dense_academic":
            return base_prompt + "\n\nINJECT_ERROR: DENSE_ACADEMIC. (Demonstration mode: Use dense, Latinate academic vocabulary)."

        if iteration > 1 and rejection_feedback:
            failed_cps = rejection_feedback.get("failed_checkpoints", [])
            critiques = rejection_feedback.get("critiques", {})
            suggested_fixes = rejection_feedback.get("suggested_fixes", {})

            feedback_block = []
            for cp in failed_cps:
                feedback_block.append(f"FAILED CHECKPOINT: {cp}")
                feedback_block.append(f"Critique: {critiques.get(cp, '')}")
                feedback_block.append(f"Suggested Fix: {suggested_fixes.get(cp, '')}")

            feedback_str = "\n".join(feedback_block)

            return f"""RETRY_CORRECTION (Iteration {iteration}):
The previous draft was REJECTED by the automated evaluator. You must fix the following issues:

{feedback_str}

Please generate an updated, perfected lesson on '{topic}' resolving every single critique above. Keep the lesson engaging, simple, and strictly aligned with the target audience.
"""

        return base_prompt
