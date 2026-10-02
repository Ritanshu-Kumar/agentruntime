# AgentRuntime

A production-oriented AI agent runtime built from first principles.

## Current milestone

**M0 — Project foundation**

This milestone provides:
- a Python package layout
- configuration management
- structured application logging
- a minimal FastAPI application
- pytest configuration and a health endpoint test
- a Docker image definition

No agent loop, model integration, tools, persistence, or orchestration is implemented yet.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
uvicorn app.main:app --reload
```

The health endpoint is available at `GET /health`.

## Architecture

The initial boundary is intentionally small:

`HTTP/API -> application -> domain`

Infrastructure such as logging and configuration supports the application but does not contain agent behavior.

Later milestones will add tool execution, agent orchestration, persistence, reliability, observability, evaluation, and safety as separate capabilities.
