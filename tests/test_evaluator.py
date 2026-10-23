"""
Unit Tests for Evaluator Agent.
Validates strict binary pass/fail enforcement across all 6 checkpoints,
deliberate jargon detection, and analogy requirement verification.
"""

import unittest
from pipeline.evaluator import EvaluatorAgent

class TestEvaluatorAgent(unittest.TestCase):
    def setUp(self):
        self.evaluator = EvaluatorAgent()

    def test_clean_lesson_passes_all_checkpoints(self):
        from pipeline.llm_factory import LLMProvider
        llm = LLMProvider(provider="simulation")
        perfect_lesson = llm._get_perfect_rag_lesson(corrected_mode=False)

        report = self.evaluator.evaluate(perfect_lesson)
        self.assertTrue(report.overall_passed, "Clean lesson must pass all 6 checkpoints.")
        self.assertEqual(report.total_score, 6, "Total score must be 6/6.")
        for cp_id, cp in report.checkpoints.items():
            self.assertTrue(cp.passed, f"Checkpoint {cp_id} failed unexpectedly: {cp.critique}")

    def test_deliberate_jargon_is_caught_and_fails(self):
        from pipeline.llm_factory import LLMProvider
        llm = LLMProvider(provider="simulation")
        flawed_lesson = llm._get_jargon_flawed_draft()

        report = self.evaluator.evaluate(flawed_lesson)
        self.assertFalse(report.overall_passed, "Flawed jargon lesson must not pass overall.")
        self.assertFalse(
            report.checkpoints["NO_UNEXPLAINED_JARGON"].passed,
            "Evaluator must fail NO_UNEXPLAINED_JARGON checkpoint."
        )
        self.assertTrue(any("vector embeddings" in j for j in report.identified_jargon))

    def test_missing_analogy_fails(self):
        from pipeline.llm_factory import LLMProvider
        llm = LLMProvider(provider="simulation")
        flawed_lesson = llm._get_missing_analogy_flawed_draft()

        report = self.evaluator.evaluate(flawed_lesson)
        self.assertFalse(report.overall_passed)
        self.assertFalse(
            report.checkpoints["TEACHES_BY_EXAMPLE"].passed,
            "Evaluator must fail TEACHES_BY_EXAMPLE when analogy is missing."
        )

    def test_dense_academic_language_fails(self):
        from pipeline.llm_factory import LLMProvider
        llm = LLMProvider(provider="simulation")
        flawed_lesson = llm._get_academic_flawed_draft()

        report = self.evaluator.evaluate(flawed_lesson)
        self.assertFalse(report.overall_passed)
        self.assertFalse(
            report.checkpoints["BEGINNER_FRIENDLY_LANGUAGE"].passed,
            "Evaluator must fail BEGINNER_FRIENDLY_LANGUAGE for dense academic language."
        )

if __name__ == "__main__":
    unittest.main()
