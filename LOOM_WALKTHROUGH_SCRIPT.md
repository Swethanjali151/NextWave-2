# 🎬 NextWave Loom Video Walkthrough Script (15–20 Minutes)
## GenAI Engineer - Content Systems | Self-Evaluating Lesson Generator

> **Video Duration:** 15 – 20 minutes  
> **Requirement:** Face-visible walkthrough covering:  
> 1. Your agentic workflow running end-to-end.  
> 2. Your evaluator catching a deliberate error.  
> 3. A face-visible walkthrough of how your workflow works and architectural reasoning.  

---

## 🛠️ Recording Setup Checklist Before You Hit Record
1. **Face-Visible Camera:** Enable your webcam bubble in the corner of Loom (make sure your face is clearly visible, well-lit, and good microphone audio).
2. **Tabs Ready:**
   - Tab 1: NextWave Web Dashboard running at `http://127.0.0.1:5000`
   - Tab 2: VS Code / IDE showing the project structure (`pipeline/graph.py`, `evaluator.py`, `generator.py`, `rubric.py`, `memory.py`)
   - Tab 3: Terminal window ready to run `python run_pipeline.py --inject-error unexplained_jargon` and `python -m unittest discover tests`
   - Tab 4: The `SUBMISSION_DOCUMENT.md` / `README.md`
3. **Pacing:** Aim for a steady, confident conversational pace (~130 words per minute).

---

## ⏱️ Minute-by-Minute Timeline Overview

| Timestamp | Segment | Key Focus / What to Show on Screen |
|---|---|---|
| **00:00 – 02:30** | Introduction & Problem Framing | Face on screen + Dashboard hero. Explain the role, target audience (12th-grade Indian student), and why single prompts fail. |
| **02:30 – 06:00** | Architecture & LangGraph Design Choices | Show IDE code (`pipeline/graph.py`) + Dashboard DAG diagram. Explain why LangGraph, bounded retries, and state machines. |
| **06:00 – 09:30** | The 6 Hard Pass/Fail Rubric | Show `pipeline/rubric.py` and `pipeline/evaluator.py`. Explain binary gates vs fuzzy scores. |
| **09:30 – 13:00** | **Live Demo 1: Evaluator Catching a Deliberate Error** | Click `"Demo Catch Deliberate Error"`. Show Iteration 1 rejection, inspect rejection audit trail, show Iteration 2 pass! |
| **13:00 – 15:30** | **Live Demo 2: Self-Evolving Memory & Dynamic Prompts** | Switch to Memory Tab. Show failure tracking, flagged jargon bank, and how evolved rules sharpen future prompts. |
| **15:30 – 18:00** | Code Walkthrough & Unit Test Suite | Run `python -m unittest discover tests` in terminal. Show clean tests passing. |
| **18:00 – 20:00** | Final Lesson Review & Conclusion | Review the generated RAG lesson, wrap up design trade-offs, thank the NextWave team. |

---

## 🎙️ Verbatim Speaking Script & Step-by-Step Directions

---

### PART 1: Introduction & Problem Framing (00:00 – 02:30)
**[Screen: Web Dashboard `http://127.0.0.1:5000` with Webcam in corner]**

> *"Hi everyone, my name is [Your Name], and today I am thrilled to present my submission for the GenAI Engineer - Content Systems role at NextWave.*
>
> *The assignment asks us to build an autonomous, self-evaluating lesson content generator for the topic: 'Introduction to RAG (Retrieval-Augmented Generation)'.*
>
> *Before showing any code, I want to emphasize our target audience: A 12th-grade graduate from India, from a non-English medium background, who wants to kickstart a career in AI.*
>
> *This audience persona completely shaped my engineering decisions. A student from this background doesn't need dense academic jargon like 'multi-dimensional latent embeddings' or complex Latinate vocabulary. What they need is cognitive scaffolding—an intuitive hook, a culturally familiar analogy like an open-book exam, short sentences, and crystal-clear explanations.*
>
> *More importantly, this role isn't about writing a clever single-shot prompt. In a production educational system, if an AI generates content with a hallucinated fact or unexplained jargon, a beginner student loses confidence and drops out. We need a system that acts as its own editor and quality inspector—evaluating its own drafts against hard checkpoints, rejecting sub-par content, regenerating with targeted feedback, and learning across runs. Let's see how this works."*

---

### PART 2: Architecture & LangGraph State Machine (02:30 – 06:00)
**[Screen: Switch to IDE `pipeline/graph.py` and point out the DAG diagram]**

> *"To orchestrate this workflow, I chose LangGraph over linear prompt chains or simple Python while-loops.*
>
> *Why LangGraph? Three critical reasons:*
> *1. **Deterministic State Machine:** Pedagogical generation is a multi-step cycle: loading past failure memory $\rightarrow$ generating draft $\rightarrow$ evaluating rubric $\rightarrow$ conditional routing $\rightarrow$ regenerating with critique $\rightarrow$ persisting to memory. LangGraph models each step as an explicit node with strongly typed state.*
> *2. **Guaranteed Bounded Termination:** In an autonomous agentic loop, runaway recursion is a real production danger. In `pipeline/graph.py`, our conditional edge enforces `max_retries = 2`. The loop is mathematically guaranteed to terminate.*
> *3. **Complete State Auditability:** Because the state is preserved across transitions, we have a complete audit trail of every draft, rejection reason, and corrective guidance.*
>
> *Let's look at the LangGraph graph construction here in `pipeline/graph.py`:*
> - `load_memory` *retrieves distilled guidelines from previous runs.*
> - `generate_lesson` *crafts the draft adapted to our 12th-grade Indian persona.*
> - `evaluate_lesson` *runs our 6 hard checkpoints.*
> - `route_evaluation` *decides whether to ship or retry.*
> - `regenerate_lesson` *feeds the exact rejection critiques back into the generator.*
> - `persist_memory` *updates failure statistics and saves outputs.*"

---

### PART 3: The 6-Checkpoint Hard Pass/Fail Rubric (06:00 – 09:30)
**[Screen: Show `pipeline/rubric.py` and `pipeline/evaluator.py`]**

> *"Now let's examine the heart of the system: the Evaluator Agent and our 6-Checkpoint Rubric in `pipeline/rubric.py`.*
>
> *A major design choice I made is: **Zero Partial Credit. Strict Binary Pass/Fail.** If a lesson scores 5 out of 6, it is rejected. Why? Because if a lesson is 90% brilliant but drops unexplained jargon like 'cosine distance' without a definition, it fails our beginner learner.*
>
> *The 6 dimensions are:*
> 1. **Accurate & Grounded:** Checks that RAG is correctly explained as external retrieval into context without claiming model weights are retrained.
> 2. **Teaches by Example:** Demands an intuitive real-world analogy—specifically the 'Open-Book vs Closed-Book Exam'—and traces an actual question step-by-step.
> 3. **Covers Key Points:** Enforces all 5 pillars: what RAG is, why LLMs hallucinate or lack fresh knowledge, the retriever role, the generator role, and the end-to-end workflow.
> 4. **Beginner-Friendly Language:** Calculates average sentence length. If it exceeds 22 words or uses dense academic terms, it fails.
> 5. **Clear, No Unexplained Jargon:** Scans for technical buzzwords like 'embeddings', 'vector database', or 'tokens'. If any word is dropped without an immediate, simple plain-English explanation, it is instantly flagged and rejected.
> 6. **Coherent Teaching Flow & Quiz:** Enforces a 6-stage progression ending in a 3-question self-test practice quiz with clear answers.
>
> *In `pipeline/evaluator.py`, I implemented a hybrid evaluation approach: deterministic lexical scanners and sentence readability metrics combined with semantic validation."*

---

### PART 4: LIVE DEMO 1 — Evaluator Catching a Deliberate Error (09:30 – 13:00)
**[Screen: Switch to Web Dashboard at `http://127.0.0.1:5000`]**

> *"Now, let's watch the system in action. To satisfy the prompt's requirement of demonstrating the evaluator catching a deliberate error, I built a dedicated one-click demo trigger right here.*
>
> *I am going to click this red button: **'Demo Catch Deliberate Error'**.*
>
> *Notice what happens in real time:*
> 1. *The status changes to 'Running Agentic Loop...'*
> 2. *The DAG node visualizer lights up: `Memory Engine` $\rightarrow$ `Generator Agent`.*
> 3. *The Generator deliberately injects complex unexplained jargon: 'dense vector embeddings in 1536-dimensional latent space' and skips the analogy.*
> 4. *Now look at the `Evaluator Agent` node:*
>    - *It catches the failure!*
>    - *`overall_passed` evaluates to FALSE.*
>    - *The Router node routes to `Regenerator` instead of ending.*
> 5. *Now let's switch to the **'Rejection Audit Trail'** tab on screen!*
>    - *Look at this audit entry: Iteration 1 failed `NO_UNEXPLAINED_JARGON`, `TEACHES_BY_EXAMPLE`, and `BEGINNER_FRIENDLY_LANGUAGE`.*
>    - *Critique: 'Dropped unexplained technical jargon: vector embeddings, latent space without simple contextual definitions.'*
>    - *Suggested Fix: 'Define or replace the following terms in plain English: vector embeddings, latent space.'*
> 6. *Now look at Iteration 2:*
>    - *The Regenerator took this exact feedback, cleared the mathematical jargon, and substituted the relatable Open-Book Exam analogy!*
>    - *The Evaluator re-inspected Iteration 2: All 6 checkpoints passed with a perfect 6/6 score!*
>    - *The lesson is marked as **PASSED (SHIPPED)**!*
>
> *This confirms that the quality loop is fully autonomous: no human had to step in; the system caught its own mistake, audited the reason, and corrected itself."*

---

### PART 5: LIVE DEMO 2 — Self-Evolving Memory & Dynamic Prompts (13:00 – 15:30)
**[Screen: Click on 'Self-Evolving Memory' Tab on Dashboard]**

> *"Next, let's look at the **'Self-Evolving Memory'** tab.*
>
> *In production, we don't want an AI system making the same mistake 100 times. Our system maintains persistent memory in `data/memory_store.json`.*
>
> *Look at these metrics:*
> - *Total Pipeline Runs: 7*
> - *Pass Rate: 71.4%*
> - *Corrective Retries: 3*
>
> *Notice the **'High-Risk Jargon Watchlist'**: terms like 'vector embeddings', 'latent space', and 'parametric weights' are stored in a persistent bank.*
>
> *More excitingly, look at the **'Distilled Guidelines'**:*
> *When the evaluator rejected drafts due to jargon or dense language, the memory engine automatically synthesized new rules, such as:*
> - *'EVOLVED RULE: Strictly forbid dropping acronyms without inline bracket definitions on first mention.'*
> - *'EVOLVED RULE: Break down compound sentences into bullet points and short conversational remarks.'*
>
> *These distilled rules are loaded on every subsequent execution and directly prepended to the Generator's system prompt. The system is literally self-evolving."*

---

### PART 6: Code Walkthrough & Test Suite (15:30 – 18:00)
**[Screen: Switch to Terminal and run commands]**

> *"Let's verify code quality and test coverage. I'll open my terminal and run our automated test suite:*
> ```bash
> python -m unittest discover tests
> ```
> *9 out of 9 tests pass in approximately 0.1 seconds.*
>
> *These tests cover:*
> 1. `test_clean_lesson_passes_all_checkpoints`: *verifies that a valid lesson scores 6/6.*
> 2. `test_deliberate_jargon_is_caught_and_fails`: *proves the evaluator fails ungrounded vector terminology.*
> 3. `test_missing_analogy_fails`: *proves the evaluator catches missing pedagogical analogies.*
> 4. `test_bounded_loop_termination`: *proves the state machine terminates cleanly without infinite looping.*
> 5. `test_evolution_triggers_on_repeated_rejection`: *proves memory synthesis functions under repeated stress.*
>
> *We also support a headless CLI runner:*
> ```bash
> python run_pipeline.py --inject-error unexplained_jargon
> ```
> *Which prints a rich, ASCII-compatible summary report directly in your console."*

---

### PART 7: Review of the Final Lesson & Conclusion (18:00 – 20:00)
**[Screen: Switch to 'Final Lesson' Tab on Dashboard]**

> *"Finally, let's review the final lesson content that cleared all 6 checkpoints:*
>
> *Look at how it opens:*
> - *'Namaste! Welcome to your first step into Artificial Intelligence. You do not need any coding or computer science background to understand this lesson.'*
> - *Section 1 introduces the real problem: Knowledge Cutoff and Hallucinations, clearly defining both in brackets.*
> - *Section 2 uses the **Open-Book Exam vs. Closed-Book Exam** analogy. The student immediately understands that regular AI is writing from memory, while RAG is flipping open the textbook.*
> - *Section 3 breaks down R-A-G into Retrieval, Augmented, and Generation in simple words.*
> - *Section 4 shows the 3-step diagram with the Retriever as the detective and the Generator as the writer.*
> - *Section 5 walks through a local clinic hospital roster in Jaipur.*
> - *And Section 6 concludes with a 3-question self-test practice quiz with complete answers.*
>
> *To summarize:*
> *We have built a robust, self-evaluating content system using LangGraph, equipped with a 6-dimension binary pass/fail evaluator, an automated rejection-correction loop, and persistent self-evolving memory.*
>
> *All code, artifacts, and documentation are committed to the GitHub repository, and the final lesson and rejection logs are linked in the submission document.*
>
> *Thank you so much to the NextWave team for this inspiring assessment. I look forward to discussing how we can scale this in production!"*

---

## 💡 Quick Tips for a Flawless Recording
- Keep your camera bubble active the entire time (face-visible requirement).
- When clicking `"Demo Catch Deliberate Error"`, speak through what is happening on screen so the viewer can follow your thought process.
- Smile, be enthusiastic, and highlight your engineering rationale!
