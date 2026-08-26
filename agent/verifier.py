import json

from openai import OpenAI

from .schemas import AppResearch


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


VERIFICATION_PROMPT = """
You are a verification agent.

You are given an AI-generated research result about a software application.

Your job is to verify whether the claims are supported by the supplied evidence.

Check:

1. Authentication
2. Credential access
3. API availability
4. API breadth
5. MCP availability
6. Buildability
7. Evidence quality

Rules:

- Official documentation has highest priority.
- Do not accept unsupported claims.
- If evidence does not support a claim, identify it as an issue.
- If evidence is ambiguous, identify it as uncertain.
- Do not invent facts.
- Do not invent URLs.
- Return ONLY valid JSON.

Return exactly this structure:

{
  "correct": true,
  "issues": [],
  "corrected_fields": {},
  "reasoning": "",
  "confidence": 0.0
}
"""


def verify_result(
    research: AppResearch,
    fresh_sources: list,
):
    payload = {
        "research": research.model_dump(),
        "sources": fresh_sources,
    }

    response = client.chat.completions.create(
        model="qwen3:1.7b",
        temperature=0,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content": VERIFICATION_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    payload,
                    indent=2,
                ),
            },
        ],
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(">>> INVALID JSON FROM VERIFIER")
        print(raw)
        raise