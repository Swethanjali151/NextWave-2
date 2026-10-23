"""
Flask Web Application & Interactive Control Dashboard.
Provides a visual interface for running the agentic workflow,
visualizing real-time node state transitions, inspecting the 6-checkpoint rubric,
demonstrating deliberate error catching, and viewing persistent self-evolving memory.
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pipeline.graph import create_lesson_pipeline
from pipeline.memory import MemoryEngine

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "outputs")
memory_engine = MemoryEngine()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/run", methods=["POST"])
def run_pipeline_api():
    try:
        data = request.json or {}
        topic = data.get("topic", "Introduction to RAG (Retrieval-Augmented Generation)")
        inject_error = data.get("inject_error", None)
        if inject_error == "none" or inject_error == "":
            inject_error = None
        provider = data.get("provider", "auto")
        max_retries = int(data.get("max_retries", 2))

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

        result = pipeline.invoke(initial_state)

        return jsonify({
            "success": True,
            "status": result["status"],
            "iteration": result["iteration"],
            "overall_passed": result["overall_passed"],
            "evaluation": result.get("evaluation"),
            "rejection_log": result.get("rejection_log", []),
            "final_lesson": result.get("final_lesson", ""),
            "log_messages": result.get("log_messages", []),
            "memory_stats": memory_engine.get_stats()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/memory", methods=["GET"])
def get_memory_api():
    return jsonify(memory_engine.get_stats())

@app.route("/api/artifacts", methods=["GET"])
def get_artifacts_api():
    lesson_path = os.path.join(OUTPUT_DIR, "rag_lesson_final.md")
    log_path = os.path.join(OUTPUT_DIR, "rag_rejection_log.json")

    lesson_content = ""
    rejection_content = []

    if os.path.exists(lesson_path):
        with open(lesson_path, "r", encoding="utf-8") as f:
            lesson_content = f.read()

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                rejection_content = json.load(f)
            except Exception:
                pass

    return jsonify({
        "final_lesson": lesson_content,
        "rejection_log": rejection_content
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"[*] Starting NextWave GenAI Dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
