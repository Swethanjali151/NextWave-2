"""
LangGraph StateGraph Workflow Orchestrator.
Coordinates the Generate -> Evaluate -> Regenerate feedback loop
with guaranteed bounded termination, self-evolving memory, and rejection auditing.
"""

import os
import json
import datetime
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from pipeline.state import PipelineState
from pipeline.generator import GeneratorAgent
from pipeline.evaluator import EvaluatorAgent
from pipeline.memory import MemoryEngine

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "outputs")

def create_lesson_pipeline(provider: str = "auto"):
    """Constructs and compiles the self-evaluating LangGraph pipeline."""
    memory_engine = MemoryEngine()
    generator = GeneratorAgent(provider=provider)
    evaluator = EvaluatorAgent(flagged_jargon_bank=memory_engine.get_flagged_jargon())

    # 1. Node Definitions
    def load_memory_node(state: PipelineState) -> Dict[str, Any]:
        distilled = memory_engine.get_distilled_rules()
        logs = state.get("log_messages", [])
        logs.append(f"Loaded {len(distilled)} distilled rules from persistent memory.")
        return {
            "persistent_learnings": distilled,
            "log_messages": logs,
            "status": "memory_loaded"
        }

    def generate_lesson_node(state: PipelineState) -> Dict[str, Any]:
        logs = state.get("log_messages", [])
        logs.append(f"Generating initial lesson draft for topic: '{state['topic']}'...")

        draft = generator.generate_draft(
            topic=state["topic"],
            target_audience=state["target_audience"],
            persistent_learnings=state.get("persistent_learnings", []),
            iteration=1,
            rejection_feedback=None,
            injected_error=state.get("injected_error")
        )

        logs.append("Initial draft generated successfully.")
        return {
            "current_draft": draft,
            "iteration": 1,
            "log_messages": logs,
            "status": "draft_generated"
        }

    def evaluate_lesson_node(state: PipelineState) -> Dict[str, Any]:
        logs = state.get("log_messages", [])
        logs.append(f"Running Evaluator Agent on Iteration {state['iteration']} draft against 6 hard checkpoints...")

        report = evaluator.evaluate(state["current_draft"], topic=state["topic"])
        overall_passed = report.overall_passed
        rejection_log = list(state.get("rejection_log", []))

        if overall_passed:
            logs.append(f"EVALUATOR PASSED: 6/6 checkpoints cleared! Ready for shipping.")
        else:
            failed = [cp_id for cp_id, cp in report.checkpoints.items() if not cp.passed]
            logs.append(f"EVALUATOR REJECTED: Failed checkpoints: {', '.join(failed)}. Recording feedback.")
            
            rejection_entry = {
                "iteration": state["iteration"],
                "timestamp": datetime.datetime.now().isoformat(),
                "failed_checkpoints": failed,
                "critiques": {cp_id: cp.critique for cp_id, cp in report.checkpoints.items() if not cp.passed},
                "suggested_fixes": {cp_id: cp.suggested_fix for cp_id, cp in report.checkpoints.items() if not cp.passed},
                "total_score": report.total_score,
                "average_sentence_length": report.average_sentence_length
            }
            rejection_log.append(rejection_entry)

        return {
            "evaluation": report.model_dump(),
            "overall_passed": overall_passed,
            "rejection_log": rejection_log,
            "log_messages": logs,
            "status": "evaluation_completed"
        }

    def regenerate_lesson_node(state: PipelineState) -> Dict[str, Any]:
        logs = state.get("log_messages", [])
        next_iter = state["iteration"] + 1
        latest_rejection = state["rejection_log"][-1]

        logs.append(f"Initiating Targeted Regeneration (Iteration {next_iter}/{state['max_retries']})...")
        logs.append(f"Feeding rejection feedback back to Generator: {list(latest_rejection['critiques'].keys())}")

        # Corrective regeneration clears injected demonstration errors
        revised_draft = generator.generate_draft(
            topic=state["topic"],
            target_audience=state["target_audience"],
            persistent_learnings=state.get("persistent_learnings", []),
            iteration=next_iter,
            rejection_feedback=latest_rejection,
            injected_error=None
        )

        logs.append(f"Iteration {next_iter} revised draft generated.")
        return {
            "current_draft": revised_draft,
            "iteration": next_iter,
            "log_messages": logs,
            "status": "regenerated"
        }

    def persist_memory_node(state: PipelineState) -> Dict[str, Any]:
        logs = state.get("log_messages", [])
        logs.append("Persisting evaluation outcomes, updating failure statistics, and storing outputs.")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 1. Update persistent memory
        identified_jargon = state.get("evaluation", {}).get("identified_jargon", [])
        memory_engine.record_run(
            topic=state["topic"],
            overall_passed=state["overall_passed"],
            iterations=state["iteration"],
            rejection_log=state.get("rejection_log", []),
            identified_jargon=identified_jargon
        )

        # 2. Save final lesson to disk
        lesson_file = os.path.join(OUTPUT_DIR, "rag_lesson_final.md")
        with open(lesson_file, "w", encoding="utf-8") as f:
            f.write(state["current_draft"])

        # 3. Save rejection log to disk
        log_file = os.path.join(OUTPUT_DIR, "rag_rejection_log.json")
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(state.get("rejection_log", []), f, indent=2)

        logs.append(f"Saved artifacts to {OUTPUT_DIR}")
        return {
            "final_lesson": state["current_draft"],
            "log_messages": logs,
            "status": "completed"
        }

    # 2. Router Function
    def route_evaluation(state: PipelineState) -> Literal["persist_memory", "regenerate_lesson"]:
        if state["overall_passed"]:
            return "persist_memory"
        
        # Bounded retry: Maximum retries allowed (e.g. max_retries = 2)
        if state["iteration"] < state["max_retries"]:
            return "regenerate_lesson"
        else:
            return "persist_memory"

    # 3. Graph Assembly
    workflow = StateGraph(PipelineState)

    workflow.add_node("load_memory", load_memory_node)
    workflow.add_node("generate_lesson", generate_lesson_node)
    workflow.add_node("evaluate_lesson", evaluate_lesson_node)
    workflow.add_node("regenerate_lesson", regenerate_lesson_node)
    workflow.add_node("persist_memory", persist_memory_node)

    # Edges
    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "generate_lesson")
    workflow.add_edge("generate_lesson", "evaluate_lesson")
    
    workflow.add_conditional_edges(
        "evaluate_lesson",
        route_evaluation,
        {
            "persist_memory": "persist_memory",
            "regenerate_lesson": "regenerate_lesson"
        }
    )
    workflow.add_edge("regenerate_lesson", "evaluate_lesson")
    workflow.add_edge("persist_memory", END)

    return workflow.compile()
