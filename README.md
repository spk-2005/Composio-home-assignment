# Composio AI Product Ops — App Research Agent

An agent-driven research pipeline for evaluating whether software applications are suitable for integration into an AI agent platform.

The assignment involves researching 100 applications across multiple categories and determining:

- What the application does
- Authentication methods
- Whether developer credentials are self-serve or gated
- Public API availability
- API breadth
- MCP availability
- Buildability for an AI toolkit
- Main blockers
- Evidence supporting the findings
- Confidence and uncertainty

The project also includes a research-analysis layer and a case-study interface for presenting the findings.

---

## 1. Problem

Composio needs to evaluate hundreds of applications before deciding whether to build integrations/toolkits for them.

Doing this manually requires repeatedly answering questions such as:

> Does this application have a public API?

> What authentication does it support?

> Can a developer obtain credentials without contacting sales?

> Is OAuth required?

> Does an MCP server already exist?

> Are there meaningful restrictions?

> Can this application realistically become an AI-agent tool?

The goal of this project is to automate as much of this research process as possible while keeping the results evidence-driven and verifiable.

---

# 2. Approach

The project uses a multi-stage pipeline:

```text
                apps.json
                    |
                    v
          +--------------------+
          | Research Agent     |
          +--------------------+
                    |
          +---------+---------+
          |                   |
          v                   v
    Web Search            App Website
          |                   |
          +---------+---------+
                    |
                    v
            Source Collection
                    |
                    v
             LLM Research
                    |
                    v
             Structured JSON
                    |
                    v
          Verification Layer
                    |
                    v
          Analysis / Insights
                    |
                    v
             Case Study