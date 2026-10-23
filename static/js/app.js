/**
 * NextWave GenAI Content Systems - Client Application Controller
 * Handles interactive pipeline triggering, LangGraph DAG node animation,
 * rubric card rendering, and self-evolving memory inspection.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const btnRunPipeline = document.getElementById('btnRunPipeline');
  const btnDemoCatchError = document.getElementById('btnDemoCatchError');
  const topicInput = document.getElementById('topicInput');
  const providerSelect = document.getElementById('providerSelect');
  const errorInjectionSelect = document.getElementById('errorInjectionSelect');
  const maxRetriesInput = document.getElementById('maxRetriesInput');
  const systemStatus = document.getElementById('systemStatus');
  const logStream = document.getElementById('logStream');
  const iterBadge = document.getElementById('iterBadge');
  
  const lessonViewer = document.getElementById('lessonViewer');
  const rubricGrid = document.getElementById('rubricGrid');
  const rubricScoreBadge = document.getElementById('rubricScoreBadge');
  const rejectionCountBadge = document.getElementById('rejectionCountBadge');
  const overallDecisionBanner = document.getElementById('overallDecisionBanner');
  const rejectionsTimeline = document.getElementById('rejectionsTimeline');

  const btnCopyLesson = document.getElementById('btnCopyLesson');
  const btnExportDoc = document.getElementById('btnExportDoc');

  let currentRawLesson = "";

  // 1. Tab Switching
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // 2. Fetch Initial Memory & Artifacts
  fetchInitialState();

  // 3. Event Listeners
  btnRunPipeline.addEventListener('click', () => {
    executePipeline();
  });

  btnDemoCatchError.addEventListener('click', () => {
    errorInjectionSelect.value = "unexplained_jargon";
    executePipeline();
  });

  btnCopyLesson.addEventListener('click', () => {
    if (!currentRawLesson) return;
    navigator.clipboard.writeText(currentRawLesson).then(() => {
      btnCopyLesson.textContent = "Copied!";
      setTimeout(() => btnCopyLesson.textContent = "Copy Markdown", 2000);
    });
  });

  btnExportDoc.addEventListener('click', () => {
    if (!currentRawLesson) return;
    const blob = new Blob([currentRawLesson], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "NextWave_RAG_Beginner_Lesson.md";
    a.click();
    URL.revokeObjectURL(url);
  });

  // 4. Pipeline Execution Function
  async function executePipeline() {
    setSystemStatus("Running Agentic Loop...", "running");
    btnRunPipeline.disabled = true;
    btnDemoCatchError.disabled = true;

    resetNodeHighlights();
    logStream.innerHTML = "";
    addLogLine("Initializing LangGraph State Machine...", "info");

    const payload = {
      topic: topicInput.value.trim() || "Introduction to RAG (Retrieval-Augmented Generation)",
      provider: providerSelect.value,
      inject_error: errorInjectionSelect.value,
      max_retries: parseInt(maxRetriesInput.value, 10)
    };

    // Node Animation simulation while awaiting API
    highlightNode("node-load_memory");
    addLogLine("Loading distilled rules & past failure memory...", "info");
    await sleep(400);

    highlightNode("node-generate_lesson");
    addLogLine(`Generating draft for topic: "${payload.topic}"...`, "info");

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!data.success) {
        addLogLine(`Execution Error: ${data.error}`, "danger");
        setSystemStatus("Pipeline Error", "error");
        btnRunPipeline.disabled = false;
        btnDemoCatchError.disabled = false;
        return;
      }

      // Progress animation
      highlightNode("node-evaluate_lesson");
      addLogLine("Evaluating draft across 6 strict pass/fail checkpoints...", "info");
      await sleep(400);

      highlightNode("node-router");
      if (data.rejection_log && data.rejection_log.length > 0) {
        addLogLine(`Router decision: Rejection detected. Retries needed: ${data.rejection_log.length}`, "warning");
        highlightNode("node-regenerate_lesson");
        addLogLine("Targeted regeneration triggered with evaluator critiques...", "info");
        await sleep(500);
      }

      highlightNode("node-persist_memory");
      addLogLine("Persisting outputs, updating memory store, and completing run.", "success");

      // Update UI with results
      renderResults(data);
      setSystemStatus("Completed (Shipped)", "ready");

    } catch (err) {
      addLogLine(`Network Error: ${err.message}`, "danger");
      setSystemStatus("Network Error", "error");
    } finally {
      btnRunPipeline.disabled = false;
      btnDemoCatchError.disabled = false;
    }
  }

  // 5. Render Results onto Dashboard
  function renderResults(data) {
    iterBadge.textContent = `Iteration: ${data.iteration}`;
    currentRawLesson = data.final_lesson || "";

    // 1. Render Markdown Lesson
    if (currentRawLesson) {
      lessonViewer.innerHTML = marked.parse(currentRawLesson);
    }

    // 2. Render Evaluation Report
    const evalReport = data.evaluation;
    if (evalReport) {
      rubricScoreBadge.textContent = `${evalReport.total_score}/6`;
      
      if (evalReport.overall_passed) {
        overallDecisionBanner.innerHTML = `<span class="status-chip chip-passed">✅ PASSED (SHIPPED) - Score ${evalReport.total_score}/6</span>`;
      } else {
        overallDecisionBanner.innerHTML = `<span class="status-chip chip-failed">❌ REJECTED - Score ${evalReport.total_score}/6</span>`;
      }

      renderRubricGrid(evalReport.checkpoints);
    }

    // 3. Render Rejection Log
    const rejections = data.rejection_log || [];
    rejectionCountBadge.textContent = rejections.length;
    renderRejectionTimeline(rejections);

    // 4. Update Memory Stats
    if (data.memory_stats) {
      updateMemoryView(data.memory_stats);
    }

    // Automatically switch to rejections tab if an error was caught, to highlight the evaluator!
    if (rejections.length > 0 && errorInjectionSelect.value !== "none") {
      switchTab('tab-rejections');
      addLogLine("Flaw successfully caught! Showing rejection audit trail.", "warning");
    } else {
      switchTab('tab-lesson');
    }
  }

  function renderRubricGrid(checkpoints) {
    rubricGrid.innerHTML = "";
    for (const [cpId, cp] of Object.entries(checkpoints)) {
      const card = document.createElement('div');
      card.className = `checkpoint-card ${cp.passed ? 'cp-passed' : 'cp-failed'}`;

      const badgeClass = cp.passed ? 'badge-pass' : 'badge-fail';
      const badgeText = cp.passed ? 'PASS (1/1)' : 'FAIL (0/1)';
      const critiqueClass = cp.passed ? '' : 'fail-critique';

      card.innerHTML = `
        <div class="cp-header">
          <span class="cp-title">${escapeHtml(cp.name)}</span>
          <span class="cp-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="cp-critique ${critiqueClass}">
          <strong>Critique:</strong> ${escapeHtml(cp.critique)}
        </div>
        ${cp.suggested_fix ? `<div class="cp-fix"><strong>Guidance:</strong> ${escapeHtml(cp.suggested_fix)}</div>` : ''}
      `;
      rubricGrid.appendChild(card);
    }
  }

  function renderRejectionTimeline(rejections) {
    if (!rejections || rejections.length === 0) {
      rejectionsTimeline.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">✅</div>
          <h4>Zero Rejections Recorded</h4>
          <p>The lesson draft passed all 6 checkpoints on its first attempt.</p>
        </div>
      `;
      return;
    }

    rejectionsTimeline.innerHTML = "";
    rejections.forEach(entry => {
      const item = document.createElement('div');
      item.className = "rejection-item";

      const failedTags = entry.failed_checkpoints.map(cp => `<span class="failed-tag">❌ ${escapeHtml(cp)}</span>`).join(' ');

      let critiquesHtml = "";
      for (const [cp, crit] of Object.entries(entry.critiques || {})) {
        critiquesHtml += `
          <div class="critique-box">
            <span style="color: #fb7185; font-weight: 700;">[${escapeHtml(cp)}]</span>: ${escapeHtml(crit)}
            <br>
            <span style="color: #f59e0b;">Fix: ${escapeHtml(entry.suggested_fixes[cp] || '')}</span>
          </div>
        `;
      }

      item.innerHTML = `
        <div class="rejection-meta">
          <span class="rejection-iter">Iteration ${entry.iteration} Rejection</span>
          <span class="rejection-time">${entry.timestamp || ''}</span>
        </div>
        <div class="rejection-checkpoints">
          ${failedTags}
        </div>
        <div class="rejection-details">
          ${critiquesHtml}
        </div>
      `;
      rejectionsTimeline.appendChild(item);
    });
  }

  function updateMemoryView(stats) {
    document.getElementById('statTotalRuns').textContent = stats.total_runs || 0;
    document.getElementById('statPassRate').textContent = `${stats.pass_rate || 100}%`;
    document.getElementById('statRetries').textContent = stats.total_retries || 0;
    document.getElementById('statActiveRules').textContent = stats.active_rules_count || 0;

    const ruleList = document.getElementById('ruleList');
    ruleList.innerHTML = "";
    (stats.distilled_rules || []).forEach(rule => {
      const li = document.createElement('li');
      li.textContent = rule;
      ruleList.appendChild(li);
    });

    const jargonCloud = document.getElementById('jargonCloud');
    jargonCloud.innerHTML = "";
    const jargons = [
      "vector database", "dense embeddings", "latent space",
      "cosine similarity", "parametric weights", "contrastive bi-encoder"
    ];
    jargons.forEach(j => {
      const chip = document.createElement('span');
      chip.className = "jargon-chip";
      chip.textContent = j;
      jargonCloud.appendChild(chip);
    });
  }

  async function fetchInitialState() {
    try {
      const res = await fetch('/api/artifacts');
      const artifacts = await res.json();
      if (artifacts.final_lesson) {
        currentRawLesson = artifacts.final_lesson;
        lessonViewer.innerHTML = marked.parse(currentRawLesson);
      }
      if (artifacts.rejection_log) {
        rejectionCountBadge.textContent = artifacts.rejection_log.length;
        renderRejectionTimeline(artifacts.rejection_log);
      }

      const memRes = await fetch('/api/memory');
      const memStats = await memRes.json();
      updateMemoryView(memStats);
    } catch (e) {
      console.log("Initial state load note:", e);
    }
  }

  // Helpers
  function switchTab(tabId) {
    tabButtons.forEach(b => {
      if (b.getAttribute('data-tab') === tabId) b.classList.add('active');
      else b.classList.remove('active');
    });
    tabContents.forEach(c => {
      if (c.id === tabId) c.classList.add('active');
      else c.classList.remove('active');
    });
  }

  function setSystemStatus(label, type) {
    const dot = systemStatus.querySelector('.status-dot');
    const text = systemStatus.querySelector('.status-label');
    text.textContent = label;

    if (type === "running") {
      dot.style.background = "var(--accent-amber)";
      dot.style.boxShadow = "0 0 8px var(--accent-amber)";
      text.style.color = "var(--accent-amber)";
    } else if (type === "error") {
      dot.style.background = "var(--accent-rose)";
      dot.style.boxShadow = "0 0 8px var(--accent-rose)";
      text.style.color = "var(--accent-rose)";
    } else {
      dot.style.background = "var(--accent-emerald)";
      dot.style.boxShadow = "0 0 8px var(--accent-emerald)";
      text.style.color = "var(--accent-emerald)";
    }
  }

  function addLogLine(msg, type = "normal") {
    const line = document.createElement('div');
    line.className = `log-line log-${type}`;
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${msg}`;
    logStream.appendChild(line);
    logStream.scrollTop = logStream.scrollHeight;
  }

  function highlightNode(nodeId) {
    resetNodeHighlights();
    const node = document.getElementById(nodeId);
    if (node) node.classList.add('active-node');
  }

  function resetNodeHighlights() {
    document.querySelectorAll('.dag-node').forEach(n => n.classList.remove('active-node'));
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
});
