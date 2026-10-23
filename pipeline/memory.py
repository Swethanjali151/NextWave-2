"""
Persistent Memory & Self-Evolving Engine.
Persists across runs, learns from evaluation feedback and rejection logs,
and automatically sharpens system prompts and rubric guidance.
"""

import os
import json
import datetime
from typing import Dict, Any, List

DEFAULT_MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory_store.json")

class MemoryEngine:
    def __init__(self, storage_path: str = DEFAULT_MEMORY_FILE):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.memory = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initial baseline memory state
        return {
            "total_runs": 0,
            "passed_runs": 0,
            "total_retries": 0,
            "checkpoint_failure_counts": {
                "ACCURATE_AND_GROUNDED": 0,
                "TEACHES_BY_EXAMPLE": 0,
                "COVERS_KEY_POINTS": 0,
                "BEGINNER_FRIENDLY_LANGUAGE": 1,
                "NO_UNEXPLAINED_JARGON": 2,
                "COHERENT_TEACHING_FLOW": 0
            },
            "flagged_jargon_bank": [
                "vector embeddings",
                "cosine similarity",
                "latent space",
                "parametric memory",
                "tokenized context window"
            ],
            "distilled_rules": [
                "RULE 1 (From Prior Rejection): Always define 'Embeddings' as 'a digital fingerprint or library catalog card' immediately upon mention.",
                "RULE 2 (From Prior Rejection): Ensure sentences remain under 20 words on average to accommodate non-English medium students.",
                "RULE 3 (From Prior Rejection): Use the 'Open-Book Exam' analogy to contrast memorized AI vs reference-checking AI."
            ],
            "run_history": []
        }

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def get_distilled_rules(self) -> List[str]:
        """Returns the current list of distilled guidelines derived from past failures."""
        return self.memory.get("distilled_rules", [])

    def get_flagged_jargon(self) -> List[str]:
        """Returns recurring jargon terms that have previously caused evaluation failures."""
        return self.memory.get("flagged_jargon_bank", [])

    def record_run(
        self,
        topic: str,
        overall_passed: bool,
        iterations: int,
        rejection_log: List[Dict[str, Any]],
        identified_jargon: List[str]
    ):
        """Updates persistent memory statistics, stores run history, and synthesizes new rules."""
        self.memory["total_runs"] += 1
        if overall_passed:
            self.memory["passed_runs"] += 1
        self.memory["total_retries"] += (iterations - 1) if iterations > 1 else 0

        # Update failure frequencies
        for entry in rejection_log:
            failed_cps = entry.get("failed_checkpoints", [])
            for cp in failed_cps:
                if cp in self.memory["checkpoint_failure_counts"]:
                    self.memory["checkpoint_failure_counts"][cp] += 1
                else:
                    self.memory["checkpoint_failure_counts"][cp] = 1

        # Track new jargon traps
        current_jargon = set(self.memory.get("flagged_jargon_bank", []))
        for word in identified_jargon:
            current_jargon.add(word.lower())
        self.memory["flagged_jargon_bank"] = sorted(list(current_jargon))

        # Dynamically synthesize evolved rules if specific checkpoints trigger repeatedly
        counts = self.memory["checkpoint_failure_counts"]
        existing_rules = self.memory.get("distilled_rules", [])

        if counts.get("NO_UNEXPLAINED_JARGON", 0) >= 3:
            new_rule = "EVOLVED RULE: Strictly forbid dropping acronyms (RAG, LLM, API) without inline bracket definitions on first mention."
            if new_rule not in existing_rules:
                existing_rules.append(new_rule)

        if counts.get("BEGINNER_FRIENDLY_LANGUAGE", 0) >= 2:
            new_rule = "EVOLVED RULE: Break down compound sentences into bullet points and short conversational remarks."
            if new_rule not in existing_rules:
                existing_rules.append(new_rule)

        self.memory["distilled_rules"] = existing_rules

        # Add run to history
        self.memory["run_history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "topic": topic,
            "overall_passed": overall_passed,
            "iterations": iterations,
            "rejections_count": len(rejection_log)
        })

        # Save to disk
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        """Returns snapshot of memory statistics for UI and logging."""
        return {
            "total_runs": self.memory.get("total_runs", 0),
            "passed_runs": self.memory.get("passed_runs", 0),
            "pass_rate": (
                round((self.memory.get("passed_runs", 0) / max(1, self.memory.get("total_runs", 0))) * 100, 1)
            ),
            "total_retries": self.memory.get("total_retries", 0),
            "checkpoint_failure_counts": self.memory.get("checkpoint_failure_counts", {}),
            "active_rules_count": len(self.memory.get("distilled_rules", [])),
            "distilled_rules": self.memory.get("distilled_rules", []),
            "flagged_jargon_count": len(self.memory.get("flagged_jargon_bank", []))
        }
