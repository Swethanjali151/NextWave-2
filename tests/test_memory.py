"""
Unit Tests for Persistent Memory & Self-Evolving Engine.
"""

import os
import unittest
import tempfile
from pipeline.memory import MemoryEngine

class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.memory = MemoryEngine(storage_path=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            try:
                os.remove(self.temp_file.name)
            except Exception:
                pass

    def test_record_run_updates_stats(self):
        self.memory.record_run(
            topic="Introduction to RAG",
            overall_passed=True,
            iterations=1,
            rejection_log=[],
            identified_jargon=[]
        )
        stats = self.memory.get_stats()
        self.assertEqual(stats["total_runs"], 1)
        self.assertEqual(stats["passed_runs"], 1)
        self.assertEqual(stats["pass_rate"], 100.0)

    def test_evolution_triggers_on_repeated_rejection(self):
        # Trigger multiple NO_UNEXPLAINED_JARGON failures
        dummy_rejection = [{
            "iteration": 1,
            "failed_checkpoints": ["NO_UNEXPLAINED_JARGON"],
            "critiques": {"NO_UNEXPLAINED_JARGON": "dense jargon found"},
            "suggested_fixes": {}
        }]

        for _ in range(4):
            self.memory.record_run(
                topic="Introduction to RAG",
                overall_passed=False,
                iterations=2,
                rejection_log=dummy_rejection,
                identified_jargon=["new_unexplained_term"]
            )

        rules = self.memory.get_distilled_rules()
        self.assertTrue(any("EVOLVED RULE" in r for r in rules))
        self.assertIn("new_unexplained_term", self.memory.get_flagged_jargon())

if __name__ == "__main__":
    unittest.main()
