"""
Integration Tests for End-to-End LangGraph Pipeline.
Validates the Generate -> Evaluate -> Regenerate state transitions,
rejection audit logging, and bounded loop termination.
"""

import unittest
from pipeline.graph import create_lesson_pipeline

class TestPipelineWorkflow(unittest.TestCase):
    def setUp(self):
        self.pipeline = create_lesson_pipeline(provider="simulation")

    def test_clean_pipeline_execution(self):
        initial_state = {
            "topic": "Introduction to RAG",
            "target_audience": "12th-grade graduate from India",
            "current_draft": "",
            "iteration": 0,
            "max_retries": 2,
            "evaluation": None,
            "overall_passed": False,
            "rejection_log": [],
            "persistent_learnings": [],
            "injected_error": None,
            "final_lesson": None,
            "status": "init",
            "log_messages": []
        }

        output = self.pipeline.invoke(initial_state)
        self.assertTrue(output["overall_passed"])
        self.assertEqual(output["iteration"], 1)
        self.assertEqual(len(output["rejection_log"]), 0)
        self.assertIsNotNone(output["final_lesson"])

    def test_error_injection_triggers_retry_and_passes(self):
        initial_state = {
            "topic": "Introduction to RAG",
            "target_audience": "12th-grade graduate from India",
            "current_draft": "",
            "iteration": 0,
            "max_retries": 2,
            "evaluation": None,
            "overall_passed": False,
            "rejection_log": [],
            "persistent_learnings": [],
            "injected_error": "unexplained_jargon",
            "final_lesson": None,
            "status": "init",
            "log_messages": []
        }

        output = self.pipeline.invoke(initial_state)
        # Should catch error in iteration 1, record rejection, regenerate in iteration 2, and pass!
        self.assertTrue(output["overall_passed"])
        self.assertEqual(output["iteration"], 2)
        self.assertEqual(len(output["rejection_log"]), 1)
        self.assertIn("NO_UNEXPLAINED_JARGON", output["rejection_log"][0]["failed_checkpoints"])

    def test_bounded_loop_termination(self):
        # Setting max_retries = 1 with injected error must terminate at iteration 1 without infinite looping
        initial_state = {
            "topic": "Introduction to RAG",
            "target_audience": "12th-grade graduate from India",
            "current_draft": "",
            "iteration": 0,
            "max_retries": 1,
            "evaluation": None,
            "overall_passed": False,
            "rejection_log": [],
            "persistent_learnings": [],
            "injected_error": "unexplained_jargon",
            "final_lesson": None,
            "status": "init",
            "log_messages": []
        }

        output = self.pipeline.invoke(initial_state)
        self.assertEqual(output["iteration"], 1)
        self.assertFalse(output["overall_passed"])
        self.assertEqual(output["status"], "completed")

if __name__ == "__main__":
    unittest.main()
