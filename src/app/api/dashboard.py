
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentRuntime Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: system-ui, sans-serif;
      background: #10131a;
      color: #e8ecf4;
    }
    body { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
    h1 { margin-bottom: 6px; }
    .muted { color: #9ba7ba; }
    .panel {
      background: #191f2b; border: 1px solid #30394a;
      border-radius: 12px; padding: 20px; margin: 18px 0;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap: 12px; }
    .metric { font-size: 26px; font-weight: 650; margin-top: 8px; }
    input, textarea, button {
      font: inherit; border-radius: 7px; padding: 10px;
      border: 1px solid #39465b; background: #111722; color: inherit;
      box-sizing: border-box; width: 100%;
    }
    textarea { min-height: 90px; resize: vertical; }
    button { cursor: pointer; background: #315bd6; border: 0; margin-top: 10px; }
    button.secondary { background: #30394a; }
    .row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }

    .row input {
      width: 100%;
      min-width: 0;
    }

    .row button {
      width: auto;
      margin-top: 0;
    }
    pre {
      white-space: pre-wrap; overflow-wrap: anywhere;
      background: #111722; padding: 14px; border-radius: 8px;
    }
    #message { min-height: 24px; }
  </style>
</head>
<body>
  <h1>AgentRuntime</h1>
  <p class="muted">Runtime operations · local development dashboard</p>

  <section class="panel">
    <h2>Connection</h2>
    <label for="apiKey">API key</label>
    <div class="row">
      <input id="apiKey" type="password" autocomplete="off"
             placeholder="Enter your API key">
      <button id="refresh" type="button">Refresh</button>
    </div>
    <p class="muted">The key stays in this page's memory and is sent in the
       X-API-Key header for protected API calls.</p>
    <p id="message" role="status" aria-live="polite"></p>
  </section>

  <section class="panel">
    <h2>Service status</h2>
    <div class="grid">
      <div><span class="muted">API liveness</span><div id="health" class="metric">—</div></div>
      <div><span class="muted">Database readiness</span><div id="ready" class="metric">—</div></div>
      <div><span class="muted">Runs started</span><div id="started" class="metric">—</div></div>
      <div><span class="muted">Runs completed</span><div id="completed" class="metric">—</div></div>
      <div><span class="muted">Runs failed</span><div id="failed" class="metric">—</div></div>
    </div>
    <button id="refreshStatus" class="secondary" type="button">Refresh status</button>
  </section>

  <section class="panel">
    <h2>Submit a task</h2>
    <form id="taskForm">
      <label for="task">Task description</label>
      <textarea id="task" required minlength="1"
                placeholder="Describe a task for the agent"></textarea>
      <button type="submit">Create run</button>
    </form>
    <h3>Latest result</h3>
    <pre id="result">No run submitted in this session.</pre>
  </section>

  <script>
    const $ = (id) => document.getElementById(id);
    const apiKey = () => $("apiKey").value.trim();

    async function request(path, options = {}) {
      const headers = { ...(options.headers || {}) };
      if (path === "/runs" || path.startsWith("/runs/") || path === "/metrics") {
        headers["X-API-Key"] = apiKey();
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

    async function refreshStatus() {
      $("message").textContent = "Checking services…";

      const checks = await Promise.allSettled([
        readJson("/health"),
        readJson("/ready"),
        readJson("/metrics")
      ]);

      $("health").textContent =
        checks[0].status === "fulfilled" ? "OK" : "Unavailable";
      $("ready").textContent =
        checks[1].status === "fulfilled" ? "Ready" : "Unavailable";

      if (checks[2].status === "fulfilled") {
        const runs = checks[2].value.runs;
        $("started").textContent = runs.started;
        $("completed").textContent = runs.completed;
        $("failed").textContent = runs.failed;
        $("message").textContent = "Status refreshed.";
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
      $("result").textContent = "Creating run…";

      try {
        const result = await readJson("/runs", {
          method: "POST",
          body: JSON.stringify({ task: $("task").value })
        });
        $("result").textContent = JSON.stringify(result, null, 2);
        await refreshStatus();
      } catch (error) {
        $("result").textContent = error.message;
      }
    });

    $("refresh").addEventListener("click", refreshStatus);
    $("refreshStatus").addEventListener("click", refreshStatus);
    refreshStatus();
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML)
