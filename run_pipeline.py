"""
CLI Runner for the Self-Evaluating Lesson Content Generator.
Executes the LangGraph agentic workflow with rich console output,
supporting deliberate failure injection for live testing and Loom video demonstrations.
"""

import os
import sys
import argparse
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pipeline.graph import create_lesson_pipeline
from pipeline.memory import MemoryEngine

def print_banner():
    print("=" * 75)
    print("  [*] NEXTWAVE: SELF-EVALUATING LESSON CONTENT GENERATOR")
    print("  Target Audience: 12th-grade graduate from India (Non-English background)")
    print("  Orchestrator: LangGraph State Machine (Generate -> Evaluate -> Regenerate)")
    print("=" * 75)

def run(topic: str, inject_error: str = None, provider: str = "auto", max_retries: int = 2):
    print_banner()
    print(f"\n[CONFIG] Topic: '{topic}'")
    print(f"[CONFIG] LLM Provider: {provider}")
    print(f"[CONFIG] Injected Error Mode: {inject_error if inject_error else 'None (Clean Run)'}")
    print(f"[CONFIG] Max Retry Bounds: {max_retries}")
    print("-" * 75)

    pipeline = create_lesson_pipeline(provider=provider)

    initial_state = {
        "topic": topic,
        "target_audience": "12th-grade graduate from India, limited English vocabulary, non-English-medium background, wants to kickstart an AI career",
        "current_draft": "",
        "iteration": 0,
        "max_retries": max_retries,
        "evaluation": None,
        "overall_passed": False,
        "rejection_log": [],
        "persistent_learnings": [],
        "injected_error": inject_error,
        "final_lesson": None,
        "status": "initialized",
        "log_messages": []
    }

    print("\n▶ Starting Agentic Pipeline...\n")
    final_output = pipeline.invoke(initial_state)

    print("\n" + "=" * 75)
    print("  SUMMARY REPORT")
    print("=" * 75)
    print(f"Final Status:       {final_output['status']}")
    print(f"Total Iterations:   {final_output['iteration']}")
    print(f"Evaluation Cleared: {'[PASS] (SHIPPED)' if final_output['overall_passed'] else '[FAIL] (BOUND TERMINATION)'}")
    print(f"Rejections Logged:  {len(final_output['rejection_log'])}")

    if final_output["rejection_log"]:
        print("\n" + "-" * 75)
        print("  REJECTION AUDIT TRAIL:")
        print("-" * 75)
        for entry in final_output["rejection_log"]:
            print(f"Iteration {entry['iteration']}:")
            print(f"  * Failed Checkpoints: {', '.join(entry['failed_checkpoints'])}")
            for cp, crit in entry["critiques"].items():
                print(f"    - [{cp}]: {crit}")
                print(f"      Suggested Fix: {entry['suggested_fixes'].get(cp, '')}")

    print("\n" + "-" * 75)
    print("  EVALUATOR RUBRIC CHECKPOINTS:")
    print("-" * 75)
    if final_output["evaluation"]:
        for cp_id, cp_data in final_output["evaluation"]["checkpoints"].items():
            icon = "[PASS]" if cp_data["passed"] else "[FAIL]"
            print(f"{icon} | {cp_data['name']}")
            print(f"       Critique: {cp_data['critique']}")

    print("\n" + "=" * 75)
    print(f"📁 Artifacts Saved:")
    print(f"  - Final Lesson:   data/outputs/rag_lesson_final.md")
    print(f"  - Rejection Log:  data/outputs/rag_rejection_log.json")
    print(f"  - Memory Store:   data/memory_store.json")
    print("=" * 75 + "\n")

    return final_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Self-Evaluating Lesson Generator Pipeline")
    parser.add_argument("--topic", type=str, default="Introduction to RAG (Retrieval-Augmented Generation)", help="Topic for the lesson")
    parser.add_argument("--inject-error", type=str, choices=["unexplained_jargon", "missing_analogy", "dense_academic"], default=None, help="Inject deliberate error for Loom demo")
    parser.add_argument("--provider", type=str, default="auto", choices=["auto", "gemini", "openai", "simulation"], help="LLM Provider")
    parser.add_argument("--retries", type=int, default=2, help="Max retry limit")
    
    args = parser.parse_args()
    run(topic=args.topic, inject_error=args.inject_error, provider=args.provider, max_retries=args.retries)
