
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentRuntime — Console</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: "Segoe UI", system-ui, sans-serif;
      background: #111315;
      color: #d9dddf;
      font-size: 14px;
    }

    * { box-sizing: border-box; }

    body { margin: 0; }

    header {
      height: 54px;
      padding: 0 28px;
      display: flex;
      align-items: center;
      gap: 24px;
      border-bottom: 1px solid #303438;
      background: #181a1c;
    }

    .brand {
      font-size: 14px;
      font-weight: 700;
      letter-spacing: .07em;
      color: #f1f3f4;
    }

    .nav { color: #92999e; font-size: 13px; }
    .nav strong { color: #e0e4e6; font-weight: 500; }
    .spacer { flex: 1; }

    .environment {
      color: #b5c9b9;
      border: 1px solid #3b5944;
      background: #202b23;
      padding: 4px 8px;
      font-size: 11px;
      letter-spacing: .05em;
    }

    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 28px 48px;
    }

    .page-heading {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 24px;
    }

    h1 { font-size: 23px; font-weight: 600; margin: 0 0 5px; }
    h2 { font-size: 14px; font-weight: 600; margin: 0; }
    h3 { font-size: 12px; font-weight: 600; margin: 0 0 12px; }
    p { line-height: 1.5; }
    .muted { color: #8f989e; }
    .small { font-size: 12px; }

    .status-strip {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      border: 1px solid #34393d;
      background: #191c1e;
      margin-bottom: 24px;
    }

    .status-item {
      min-width: 0;
      padding: 15px 17px;
      border-right: 1px solid #34393d;
    }

    .status-item:last-child { border-right: 0; }

    .label {
      color: #929ba0;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .07em;
    }

    .value {
      margin-top: 9px;
      font-size: 20px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    .healthy { color: #a8c9ae; }
    .unhealthy { color: #e5a09a; }
    .neutral { color: #e0e4e6; }

    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr);
      gap: 24px;
      align-items: start;
    }

    .section { min-width: 0; }
    .section-heading {
      padding-bottom: 12px;
      border-bottom: 1px solid #34393d;
      margin-bottom: 18px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      font-size: 12px;
      color: #b8c0c4;
    }

    input, textarea {
      width: 100%;
      color: #e3e7e9;
      background: #17191b;
      border: 1px solid #3a4044;
      border-radius: 3px;
      padding: 10px 11px;
      font: inherit;
    }

    input:focus, textarea:focus {
      outline: 1px solid #91ad9a;
      border-color: #91ad9a;
    }

    textarea { min-height: 112px; resize: vertical; line-height: 1.5; }

    button {
      border: 1px solid #637e6a;
      border-radius: 3px;
      background: #344b3a;
      color: #edf4ee;
      padding: 9px 13px;
      font: inherit;
      cursor: pointer;
    }

    button:hover { background: #405b47; }
    button:disabled { opacity: .55; cursor: wait; }

    button.secondary {
      border-color: #42484c;
      background: #202326;
      color: #c9d0d3;
    }

    button.secondary:hover { background: #2a2e31; }

    .form-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }

    .result-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 22px 0 10px;
    }

    .run-status {
      display: inline-block;
      font-size: 11px;
      letter-spacing: .04em;
      border: 1px solid #42484c;
      padding: 4px 7px;
      color: #bdc5c9;
    }

    .run-status.completed { color: #b1d0b5; border-color: #42604a; }
    .run-status.failed { color: #e5a09a; border-color: #70433f; }

    pre {
      margin: 0;
      min-height: 130px;
      max-height: 360px;
      overflow: auto;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #17191b;
      border: 1px solid #34393d;
      padding: 14px;
      color: #c7d4c9;
      font: 12px/1.65 Consolas, "Courier New", monospace;
    }

    .connection {
      margin-top: 30px;
      padding-top: 18px;
      border-top: 1px solid #303538;
    }

    .connection-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      max-width: 620px;
    }

    #message { min-height: 18px; margin: 10px 0 0; }

    @media (max-width: 760px) {
      header { padding: 0 16px; gap: 14px; }
      main { padding: 22px 16px 36px; }
      .workspace { grid-template-columns: 1fr; }
      .status-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .status-item { border-bottom: 1px solid #34393d; }
      .status-item:nth-child(2n) { border-right: 0; }
      .status-item:last-child { border-bottom: 0; }
      .page-heading { align-items: start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">AGENTRUNTIME</div>
    <div class="nav"><strong>Console</strong> &nbsp;/&nbsp; Runs &nbsp;/&nbsp; Observability</div>
    <div class="spacer"></div>
    <span class="environment">DEVELOPMENT</span>
  </header>

  <main>
    <div class="page-heading">
      <div>
        <h1>Runtime console</h1>
        <div class="muted small">Inspect service health and execute agent runs.</div>
      </div>
      <button id="refresh" class="secondary" type="button">Refresh status</button>
    </div>

    <section class="status-strip" aria-label="Runtime status">
      <div class="status-item">
        <div class="label">API</div>
        <div id="health" class="value neutral">Checking</div>
      </div>
      <div class="status-item">
        <div class="label">Database</div>
        <div id="ready" class="value neutral">Checking</div>
      </div>
      <div class="status-item">
        <div class="label">Runs started</div>
        <div id="started" class="value">—</div>
      </div>
      <div class="status-item">
        <div class="label">Completed</div>
        <div id="completed" class="value">—</div>
      </div>
      <div class="status-item">
        <div class="label">Failed</div>
        <div id="failed" class="value">—</div>
      </div>
    </section>

    <div class="workspace">
      <section class="section">
        <div class="section-heading">
          <h2>New run</h2>
          <p class="muted small">Submit a task to the agent runtime.</p>
        </div>

        <form id="taskForm">
          <label for="task">Task description</label>
          <textarea id="task" required minlength="1"
            placeholder="Describe the task you want the agent to perform…"></textarea>
          <div class="form-actions">
            <span class="muted small">POST /runs</span>
            <button id="submitRun" type="submit">Create run →</button>
          </div>
        </form>
      </section>

      <section class="section">
        <div class="section-heading">
          <h2>Run inspector</h2>
          <p class="muted small">Result from your latest submission.</p>
        </div>

        <div class="result-meta">
          <span class="label">Latest response</span>
          <span id="runStatus" class="run-status">NO RUN</span>
        </div>
        <pre id="result">No run submitted in this session.</pre>
        <p id="runId" class="muted small">Run ID: —</p>
      </section>
    </div>

    <section class="connection">
      <h3>Connection settings</h3>
      <label for="apiKey">API key</label>
      <div class="connection-row">
        <input id="apiKey" type="password" autocomplete="off"
          placeholder="Enter API key">
        <button id="saveKey" class="secondary" type="button">Apply key</button>
      </div>
      <p class="muted small">Kept in this page's memory only. Sent in the
        X-API-Key header for protected API requests.</p>
      <p id="message" class="muted small" role="status" aria-live="polite"></p>
    </section>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    let latestRunId = null;

    async function request(path, options = {}) {
      const headers = { ...(options.headers || {}) };

      if (path === "/metrics" || path === "/runs" || path.startsWith("/runs/")) {
        headers["X-API-Key"] = $("apiKey").value.trim();
      }

      if (options.body) headers["Content-Type"] = "application/json";

      return fetch(path, { ...options, headers });
    }

    async function readJson(path, options = {}) {
      const response = await request(path, options);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
      }

      return data;
    }

    function setHealth(id, ok, goodText, badText) {
      $(id).textContent = ok ? goodText : badText;
      $(id).className = "value " + (ok ? "healthy" : "unhealthy");
    }

    async function refreshStatus() {
      $("message").textContent = "Refreshing service status…";

      const checks = await Promise.allSettled([
        readJson("/health"),
        readJson("/ready"),
        readJson("/metrics")
      ]);

      setHealth("health", checks[0].status === "fulfilled", "Online", "Offline");
      setHealth("ready", checks[1].status === "fulfilled", "Ready", "Unavailable");

      if (checks[2].status === "fulfilled") {
        const runs = checks[2].value.runs;
        $("started").textContent = runs.started;
        $("completed").textContent = runs.completed;
        $("failed").textContent = runs.failed;
        $("message").textContent = "Status updated.";
      } else {
        $("started").textContent = "—";
        $("completed").textContent = "—";
        $("failed").textContent = "—";
        $("message").textContent =
          "Metrics unavailable. Check the API key and server.";
      }
    }

    $("taskForm").addEventListener("submit", async (event) => {
      event.preventDefault();

      const button = $("submitRun");
      button.disabled = true;
      button.textContent = "Running…";
      $("result").textContent = "Waiting for response…";
      $("runStatus").textContent = "IN PROGRESS";
      $("runStatus").className = "run-status";
      $("runId").textContent = "Run ID: pending";

      try {
        const run = await readJson("/runs", {
          method: "POST",
          body: JSON.stringify({ task: $("task").value })
        });

        latestRunId = run.id;
        $("result").textContent = JSON.stringify(run, null, 2);
        $("runId").textContent = "Run ID: " + run.id;
        $("runStatus").textContent = run.status.toUpperCase();
        $("runStatus").className = "run-status " +
          (run.status === "completed" ? "completed" :
           run.status === "failed" ? "failed" : "");

        await refreshStatus();
      } catch (error) {
        $("result").textContent = error.message;
        $("runStatus").textContent = "REQUEST ERROR";
        $("runStatus").className = "run-status failed";
        $("runId").textContent = "Run ID: —";
        $("message").textContent = "Could not create run.";
      } finally {
        button.disabled = false;
        button.textContent = "Create run →";
      }
    });

    $("refresh").addEventListener("click", refreshStatus);
    $("saveKey").addEventListener("click", refreshStatus);

    refreshStatus();
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML)
