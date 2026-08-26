# Composio App Research Agent

Take-home assignment for the Composio AI Product Ops Intern role.

Research 100 applications for auth, API surface, MCP availability, buildability, and evidence-backed findings.

## Status

Scaffold only — research logic not yet implemented.

## Project structure

```
agent/          Research agent modules
data/apps.json  100-app research set
results/        Pipeline output (JSON)
scripts/        CLI entry points
web/            Self-contained HTML case study deliverable
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create `.env` in the project root (never commit it):

```
COMPOSIO_API_KEY=...
OPENAI_API_KEY=...
```

## Run (coming soon)

```bash
python scripts/run_research.py
python scripts/verify_results.py
python scripts/analyze_results.py
```

Open `web/index.html` in a browser for the case study deliverable.
