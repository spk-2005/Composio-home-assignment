# Composio App Research Agent

An agentic research pipeline for evaluating whether software applications are suitable for integration into an AI-agent toolkit.

Built as part of the **AI Product Ops Intern take-home assignment**.

> Before building a toolkit for an application, we need to understand its authentication, credential access, API surface, MCP availability, buildability, and integration blockers.

Doing this manually across hundreds of applications does not scale. This project automates the first-pass research process and structures the findings so they can later be verified, analyzed, and presented.

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [Project Structure](#2-project-structure)
3. [Requirements](#3-requirements)
4. [Clone the Repository](#4-clone-the-repository)
5. [Create a Python Virtual Environment](#5-create-a-python-virtual-environment)
6. [Install Python Dependencies](#6-install-python-dependencies)
7. [Install and Configure Ollama](#7-install-and-configure-ollama)
8. [Pull the Research Model](#8-pull-the-research-model)
9. [Ollama API](#9-ollama-api)
10. [Configure the Applications](#10-configure-the-applications)
11. [Run the Research Agent](#11-run-the-research-agent)
12. [How the Researcher Works](#12-how-the-researcher-works)
13. [Evidence-First Research](#13-evidence-first-research)
14. [Structured Output](#14-structured-output)
15. [Research Output](#15-research-output)
16. [Important Limitation](#16-important-limitation)
17. [Verification](#17-verification)
18. [Human Verification](#18-human-verification)
19. [Analysis](#19-analysis)
20. [Pattern Analysis](#20-pattern-analysis)
21. [Buildability Model](#21-buildability-model)
22. [Web Research Layer](#22-web-research-layer)
23. [Why Local Ollama Was Used](#23-why-local-ollama-was-used)
24. [Performance Considerations](#24-performance-considerations)
25. [Case Study](#25-case-study)
26. [Running the Case Study Locally](#26-running-the-case-study-locally)
27. [Running the Web UI](#27-running-the-web-ui)
28. [Re-running the Pipeline](#28-re-running-the-pipeline)
29. [Troubleshooting](#29-troubleshooting)
30. [Design Principles](#30-design-principles)
31. [What the Agent Can and Cannot Do](#31-what-the-agent-can-and-cannot-do)
32. [Honest Status of This Repository](#32-honest-status-of-this-repository)
33. [Example End-to-End Run](#33-example-end-to-end-run)
34. [Submission](#34-submission)

---

## 1. What This Project Does

For each application, the research pipeline attempts to collect:

- Application category
- One-line description
- Authentication methods
- Credential access model
- Public API availability
- API type
- Approximate API breadth
- MCP availability
- Buildability
- Main blocker
- Supporting evidence
- Confidence
- Uncertainty

The pipeline follows an evidence-first approach:

```
Application
     |
     v
Generate research queries
     |
     v
Search the web
     |
     v
Collect candidate URLs
     |
     v
Fetch source pages
     |
     v
Build evidence-based prompt
     |
     v
LLM structured research
     |
     v
Pydantic schema validation
     |
     v
Structured JSON result
     |
     v
Analysis / verification
     |
     v
Case-study presentation
```

---

## 2. Project Structure

```
Composio-home-assignment/
│
├── agent/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── config.py
│   ├── models.py
│   ├── pipeline.py
│   ├── prompts.py
│   ├── researcher.py
│   ├── schemas.py
│   ├── search.py
│   ├── verifier.py
│   ├── web.py
│   └── web_research.py
│
├── analysis/
│   └── analyze.py
│
├── case-study/
│   └── index.html
│
├── data/
│   ├── apps.json
│   ├── first_pass.json
│   ├── verification.json
│   └── verified.json
│
├── results/
│   └── .gitkeep
│
├── scripts/
│   ├── analyze_results.py
│   ├── run.py
│   ├── run_research.py
│   ├── test_composio.py
│   └── verify_results.py
│
├── web/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 3. Requirements

- Python 3.10+
- Git
- Ollama
- A locally available LLM model
- Internet access for web search and page fetching

The current implementation uses Ollama locally, so an OpenAI API key is **not** required for the research pass.

---

## 4. Clone the Repository

```bash
git clone https://github.com/spk-2005/Composio-home-assignment.git
cd Composio-home-assignment
```

Repository: https://github.com/spk-2005/Composio-home-assignment

---

## 5. Create a Python Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```
(.venv) PS B:\Composio-app>
```

---

## 6. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you need to upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

## 7. Install and Configure Ollama

This project runs the research LLM locally using Ollama.

Check whether Ollama is installed:

```bash
ollama --version
```

Expected output looks similar to:

```
ollama version is 0.33.0
```

If Ollama is not installed, install it from the [official Ollama website](https://ollama.com).

After installation, verify the Ollama service is available:

```bash
ollama list
```

---

## 8. Pull the Research Model

The current implementation uses:

```
qwen3:1.7b
```

Pull it with:

```bash
ollama pull qwen3:1.7b
```

Verify:

```bash
ollama list
```

You should see something similar to:

```
NAME          ID              SIZE
qwen3:1.7b    ...             ...
```

You can also test the model manually:

```bash
ollama run qwen3:1.7b
```

Then try:

```
Return only this JSON: {"name":"Salesforce","category":"CRM"}
```

The model should return JSON. Exit Ollama with `/bye`.

---

## 9. Ollama API

The Python application communicates with Ollama through its OpenAI-compatible API:

```
http://localhost:11434/v1
```

The researcher uses:

```python
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

The API key is only a placeholder required by the OpenAI-compatible client. The research request is handled by the local Ollama server.

---

## 10. Configure the Applications

The research set is stored in `data/apps.json`. Each application contains:

```json
{
  "id": 1,
  "name": "Salesforce",
  "category": "CRM and Sales",
  "website": "https://salesforce.com",
  "docs_hint": "salesforce.com"
}
```

The provided dataset contains the assignment's application research set. To add another application, add another JSON object following the same structure.

---

## 11. Run the Research Agent

Make sure the virtual environment is activated:

```powershell
.\.venv\Scripts\Activate.ps1
```

Make sure Ollama is running and the model is available:

```bash
ollama list
```

Then run:

```bash
python scripts/run.py
```

The pipeline starts processing the applications one by one. Example output:

```
Researching Salesforce...
>>> START collect_sources()
>>> Building candidates
>>> SEARCHING: Salesforce API authentication OAuth
>>> SEARCH RESULT COUNT: 1
>>> SEARCHING: Salesforce API documentation
>>> SEARCH RESULT COUNT: 1
>>> SEARCHING: Salesforce MCP server
>>> SEARCH RESULT COUNT: 1
>>> SEARCHING: Salesforce developer credentials
>>> SEARCH RESULT COUNT: 1
>>> UNIQUE CANDIDATES: 5
>>> FETCHING: https://salesforce.com
>>> FETCH COMPLETE: https://salesforce.com
>>> SOURCE ADDED: https://salesforce.com
>>> SOURCES COLLECTED: 2
>>> BUILDING PROMPT
>>> PROMPT SIZE: 10,137 characters
>>> START LLM
>>> LLM RESPONSE RECEIVED
>>> PARSING JSON
>>> VALIDATING SCHEMA
>>> RESEARCH COMPLETE
```

The debug output is intentionally verbose so the research process can be inspected rather than treated as a black box.

---

## 12. How the Researcher Works

The main implementation is in `agent/researcher.py`.

For every application, the researcher generates several targeted queries, for example:

```
Salesforce API authentication OAuth
Salesforce API documentation
Salesforce MCP server
Salesforce developer credentials
```

Results are collected and deduplicated. Candidate sources include:

- Application website
- Developer documentation hint
- Search results

The pipeline then fetches the pages and supplies the available evidence to the LLM.

---

## 13. Evidence-First Research

The research prompt explicitly instructs the model to:

- Prefer official documentation
- Prefer official API documentation
- Prefer authentication documentation
- Avoid unsupported claims
- Distinguish official MCP implementations from community implementations
- Distinguish self-serve access from paid or enterprise access
- Mark unavailable information as unknown
- Attach evidence to important conclusions

This is important because the objective is not simply to generate plausible descriptions — the objective is to produce **auditable research**.

---

## 14. Structured Output

Research results are validated against `agent/schemas.py`. The main schema is:

```python
class AppResearch(BaseModel):
    app: str
    category: str
    description: str

    auth_methods: List[str]

    credential_access: str

    api: APIInfo

    mcp: MCPInfo

    buildability: str

    blocker: Optional[str]

    evidence: List[Evidence]

    confidence: float

    uncertainty: List[str]
```

This prevents the pipeline from silently accepting arbitrary LLM output.

```
LLM
 |
 v
JSON parsing
 |
 v
Pydantic validation
 |
 v
AppResearch
```

If the model produces invalid JSON or violates the schema, the run fails instead of silently producing malformed research.

---

## 15. Research Output

The first-pass output is written to `data/first_pass.json`. Example structure:

```json
[
  {
    "app": "Salesforce",
    "category": "CRM and Sales",
    "description": "AI CRM platform for businesses",
    "auth_methods": [],
    "credential_access": "self-serve",
    "api": {
      "public": true,
      "type": "public",
      "breadth": "broad"
    },
    "mcp": {
      "available": false,
      "source": "https://salesforce.com",
      "url": "https://salesforce.com"
    },
    "buildability": "EASY",
    "blocker": "unknown",
    "evidence": [],
    "confidence": 70.0,
    "uncertainty": []
  }
]
```

The exact results depend on the sources successfully retrieved and the model output at runtime.

---

## 16. Important Limitation

The research agent is deliberately **not** treated as automatically correct. Search engines, websites, authentication documentation, dynamic pages, and LLM interpretation can all introduce errors. For example:

- A website may not expose API documentation in its HTML.
- A developer documentation page may reject automated requests.
- Search results may point to outdated information.
- An MCP implementation may be community-maintained rather than official.
- An API may technically exist but require approval or a paid plan.
- The LLM may incorrectly interpret incomplete evidence.

**A generated result is a research hypothesis until it is verified.** This is why the repository includes a verification stage, and the case study explicitly separates first-pass research from verified findings.

---

## 17. Verification

Verification code is located in `agent/verifier.py`. The intended verification process is:

```
First-pass research
        |
        v
Select sample
        |
        v
Fetch fresh evidence
        |
        v
Verification agent
        |
        v
Compare claims
        |
        v
Identify errors
        |
        v
Correct fields
```

The verifier checks:

- Authentication
- Credential access
- API availability
- API breadth
- MCP availability
- Buildability
- Evidence quality

The verification output is intended to be stored in `data/verification.json` and subsequently `data/verified.json`.

> **Note:** `agent/verifier.py` is currently configured to use `model="gpt-5-mini"` with an OpenAI API key, while the researcher uses Ollama. Do not claim the verification loop has been completed unless it has actually been run successfully with valid API access.

---

## 18. Human Verification

The assignment specifically requires human checks. Recommended process:

1. Select a sample of applications from the research set.
2. Open the official developer documentation manually.
3. Check the agent's claims.
4. Record correct and incorrect claims.
5. Correct unsupported findings.
6. Calculate accuracy before and after verification.

The case study should report the actual sample and actual results. **Do not interpret an unverified first-pass result as ground truth.**

---

## 19. Analysis

Analysis utilities are located under `analysis/` and `scripts/`. The purpose of the analysis stage is to identify patterns across applications rather than simply display 100 rows.

Useful dimensions include:

**Authentication**
- OAuth2
- API Key
- Bearer Token
- Basic Auth
- Other
- Unknown

**Credential Access**
- Self-serve
- Free
- Trial
- Paid
- Admin approval
- Enterprise
- Partner
- Contact sales
- Unknown

**API Surface**
- REST
- GraphQL
- REST + GraphQL
- Other
- Unknown

**Buildability**
- EASY
- MODERATE
- HARD

---

## 20. Pattern Analysis

The goal of the assignment is not merely "here are 100 applications." The more useful output is "here are the patterns across the 100 applications." Examples of questions the analysis should answer:

- **Authentication** — Which mechanism appears most frequently?
- **Self-serve access** — How many applications can a developer access without contacting sales?
- **Gating** — What percentage require paid plans, admin approval, enterprise access, partner approval, or contact-sales workflows?
- **API surface** — How many have public REST APIs, GraphQL APIs, both, limited APIs, or no meaningful public API?
- **MCP** — How many have an official MCP, community MCP, no MCP found, or uncertain MCP status?
- **Buildability** — Which applications are EASY, MODERATE, or HARD, and why?

---

## 21. Buildability Model

The research prompt uses three broad classifications.

**EASY**
- Public API
- Self-serve credentials
- Standard authentication
- Useful API surface
- No significant approval barrier

**MODERATE**
- Public API with meaningful restrictions
- Paid plan
- OAuth approval
- Limited API surface
- Additional configuration required

**HARD**
- Partner-only access
- Contact-sales requirement
- Enterprise-only access
- No meaningful public API
- Strong platform restrictions

The classification is intentionally conservative.

---

## 22. Web Research Layer

The web research functionality is implemented through `agent/search.py`, `agent/web.py`, and `agent/web_research.py`.

The research pipeline separates **search** from **page fetching**, making it possible to inspect where information came from before passing it to the model.

---

## 23. Why Local Ollama Was Used

The initial implementation used the OpenAI-compatible Python client. However, direct OpenAI API usage requires an account with available API quota/billing. For this assignment, the research pipeline was switched to local Ollama:

```python
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

This allows the LLM portion of the research pipeline to run locally. The tradeoff is that a small local model can be slower or less capable than a larger hosted model, especially when processing long evidence-heavy prompts.

---

## 24. Performance Considerations

The research pipeline can be slow because each application may require:

```
4 search queries
        +
multiple page fetches
        +
large evidence prompt
        +
LLM inference
```

For faster local execution, the researcher currently limits:

```
MAX_SOURCES = 3
MAX_RESULTS_PER_QUERY = 1
```

This is a deliberate tradeoff between research breadth and runtime. Increasing these values improves potential evidence coverage but increases runtime and prompt size.

---

## 25. Case Study

The reviewer-facing case study is `case-study/index.html`. It is designed to communicate:

- Problem
- Approach
- Research workflow
- Findings
- Agent architecture
- Human-in-the-loop process
- Verification
- Limitations
- Output

The case study is intentionally separate from the research implementation. The implementation answers *"How was the research generated?"* The case study answers *"What did the research reveal, and how trustworthy is it?"*

---

## 26. Running the Case Study Locally

From the repository root:

```bash
python -m http.server 8000
```

Then open: `http://localhost:8000/case-study/`

Alternatively, open `case-study/index.html` directly in a browser. Using a local HTTP server is recommended because browsers may apply restrictions when opening local files directly.

---

## 27. Running the Web UI

The project also contains `web/index.html`, `web/app.js`, and `web/style.css`.

To serve the repository:

```bash
python -m http.server 8000
```

Then open: `http://localhost:8000/web/`

The web interface is intended as a lightweight presentation layer for the generated research.

---

## 28. Re-running the Pipeline

To run the research again:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/run.py
```

The generated first-pass research will update `data/first_pass.json`. If verification and analysis are run separately, their outputs can be stored in `data/verification.json` and `data/verified.json`.

---

## 29. Troubleshooting

**Problem: `KeyError: 'hint'`**

The application dataset uses `"docs_hint"`, not `"hint"`. The researcher therefore accesses `app["docs_hint"]` instead of `app["hint"]`.

**Problem: `OpenAI 429 insufficient_quota`**

```
openai.RateLimitError:
Error code: 429
insufficient_quota
```

This means the OpenAI API account does not have sufficient API quota. The local configuration should instead use Ollama:

```python
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

**Problem: Ollama takes a long time**

Check `ollama list` and make sure `qwen3:1.7b` exists. Test it independently with `ollama run qwen3:1.7b`. If the model responds slowly, the limitation is local inference performance rather than the Python search pipeline. Reducing `MAX_SOURCES` and `MAX_RESULTS_PER_QUERY` can reduce the amount of context sent to the model.

**Problem: Research gets stuck at `START LLM`**

If the console shows `>>> START LLM` and nothing immediately follows, the program is waiting for Ollama to complete inference. Check another terminal with `ollama ps`, or test with `ollama run qwen3:1.7b`.

**Problem: A web page returns an error**

Some developer sites do not expose content cleanly to automated fetchers. The pipeline intentionally skips failed sources instead of inventing information. You may see `>>> SKIPPING ERROR SOURCE` — this is expected behavior.

**Problem: `first_pass.json` is empty**

If the pipeline has not completed an application successfully, the output may still be empty or incomplete. Run `python scripts/run.py` and wait until an application reports `>>> RESEARCH COMPLETE`. The output file is written by the pipeline after the research loop completes.

---

## 30. Design Principles

1. **Evidence over guessing** — The agent should prefer documentation over model knowledge.
2. **Structured output** — LLM output is validated using Pydantic.
3. **Conservative classification** — Unknown information should remain unknown.
4. **Human verification** — The LLM is not treated as the final authority.
5. **Reproducibility** — Research can be rerun from the application dataset.
6. **Separation of concerns** — The repository separates research, verification, analysis, and presentation.

---

## 31. What the Agent Can and Cannot Do

**It can:**
- Generate targeted research queries
- Search for relevant sources
- Collect candidate URLs
- Fetch available web pages
- Build evidence-grounded prompts
- Generate structured research
- Validate the result against a schema
- Produce machine-readable JSON
- Support downstream analysis and verification

**It cannot guarantee:**
- That every web page is accessible
- That every API claim is current
- That every search result is authoritative
- That the LLM interprets every source correctly
- That an MCP implementation is official unless the evidence establishes it
- That a generated result is correct without verification

This distinction is important for production use.

---

## 32. Honest Status of This Repository

The repository contains the implementation of the research pipeline and the reviewer-facing case-study presentation. The research output should be interpreted according to the actual contents of `data/first_pass.json`, `data/verification.json`, and `data/verified.json`. Only results that have actually been generated and verified should be presented as verified findings.

Two points worth flagging explicitly before submission:

- **Do not claim all 100 applications were successfully researched and verified** unless the pipeline actually completed a full run over the full dataset. A partial or in-progress run should be reported as partial.
- **Do not claim the verification loop was completed** using `agent/verifier.py` unless it was actually run successfully — it is currently configured to call `model="gpt-5-mini"` via the OpenAI API (a different provider/model than the Ollama-based researcher), which requires a valid OpenAI API key and quota.

The case study intentionally avoids presenting unverified model output as ground truth.

---

## 33. Example End-to-End Run

```bash
git clone https://github.com/spk-2005/Composio-home-assignment.git
cd Composio-home-assignment

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

ollama pull qwen3:1.7b
ollama list

python scripts/run.py
```

After the research completes, `data/first_pass.json` contains the generated structured research. The case study can then be viewed with:

```bash
python -m http.server 8000
```

and opening `http://localhost:8000/case-study/`.

---

## 34. Submission

- **Repository:** https://github.com/spk-2005/Composio-home-assignment
- **Case study:** `case-study/index.html`

For final submission, deploy the `case-study/` directory as a static website and submit the deployed URL along with the GitHub repository link.

---

## Summary

This project treats application integration research as an agentic pipeline rather than a manually maintained spreadsheet.

```
100 Applications
       |
       v
Targeted Search
       |
       v
Source Collection
       |
       v
Evidence Extraction
       |
       v
Local LLM Research
       |
       v
Structured Schema
       |
       v
Verification
       |
       v
Pattern Analysis
       |
       v
Integration Priorities
```

The key output is not just a list of applications. It is a repeatable system for answering: **Which applications are easiest to turn into reliable AI-agent integrations, what prevents the others from being easy wins, and how confident are we in those conclusions?**