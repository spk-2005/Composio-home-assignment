import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from .schemas import AppResearch
from .prompts import (
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_WITH_SOURCES_USER_PROMPT,
)
from .search import search
from .web import fetch_page


# ---------------------------------------------------------
# Environment / Ollama client
# ---------------------------------------------------------

load_dotenv()

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# Keep these small because we are using a local 1.7B model.
MAX_SOURCES = 2
MAX_RESULTS_PER_QUERY = 1
MAX_CONTENT_PER_SOURCE = 3000


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_url(url: str) -> str:
    """
    Convert a bare domain into a usable URL.

    Example:
        salesforce.com
        ->
        https://salesforce.com
    """

    if not url:
        return url

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return "https://" + url

    return url


def _search_queries(app: dict) -> list[str]:
    """
    Generate search queries for the application.
    """

    name = app["name"]

    return [
        f"{name} API authentication OAuth",
        f"{name} API documentation",
        f"{name} MCP server",
        f"{name} developer credentials",
    ]


def _dedupe_urls(candidates: list[dict]) -> list[dict]:
    """
    Remove duplicate URLs.
    """

    seen = set()
    unique = []

    for item in candidates:
        url = normalize_url(item["url"])

        if url in seen:
            continue

        seen.add(url)

        # Store normalized URL back into the candidate.
        item["url"] = url

        unique.append(item)

    return unique


# ---------------------------------------------------------
# Source collection
# ---------------------------------------------------------

def collect_sources(app: dict) -> list[dict]:
    """
    Search for documentation, fetch pages,
    and return a small amount of useful evidence.
    """

    print(">>> Building candidates", flush=True)

    candidates = [
        {
            "url": normalize_url(app["website"]),
            "title": f"{app['name']} website",
        },
        {
            "url": normalize_url(app["docs_hint"]),
            "title": f"{app['name']} developer hint",
        },
    ]

    # -----------------------------------------------------
    # Search web
    # -----------------------------------------------------

    for query in _search_queries(app):

        print(
            f">>> SEARCHING: {query}",
            flush=True,
        )

        results = search(
            query,
            max_results=MAX_RESULTS_PER_QUERY,
        )

        print(
            f">>> SEARCH RESULT COUNT: {len(results)}",
            flush=True,
        )

        candidates.extend(results)

    # -----------------------------------------------------
    # Remove duplicate URLs
    # -----------------------------------------------------

    candidates = _dedupe_urls(candidates)

    print(
        f">>> UNIQUE CANDIDATES: {len(candidates)}",
        flush=True,
    )

    # -----------------------------------------------------
    # Fetch sources
    # -----------------------------------------------------

    sources = []

    for item in candidates:

        if len(sources) >= MAX_SOURCES:
            break

        url = normalize_url(item["url"])

        print(
            f">>> FETCHING: {url}",
            flush=True,
        )

        try:
            content = fetch_page(url)

        except Exception as e:

            print(
                f">>> FETCH ERROR: {url}",
                flush=True,
            )

            print(
                f">>> ERROR: {e}",
                flush=True,
            )

            continue

        print(
            f">>> FETCH COMPLETE: {url}",
            flush=True,
        )

        # Ignore failed pages.
        if not content:
            print(
                f">>> EMPTY CONTENT: {url}",
                flush=True,
            )
            continue

        if content.startswith("ERROR:"):
            print(
                f">>> SKIPPING ERROR SOURCE: {url}",
                flush=True,
            )
            continue

        # -------------------------------------------------
        # Limit source content.
        #
        # This is important for qwen3:1.7b because
        # sending huge webpages makes local inference slow.
        # -------------------------------------------------

        content = content[:MAX_CONTENT_PER_SOURCE]

        sources.append(
            {
                "url": url,
                "title": item.get(
                    "title",
                    f"{app['name']} source",
                ),
                "content": content,
            }
        )

        print(
            f">>> SOURCE ADDED: {url}",
            flush=True,
        )

    print(
        f">>> FINAL SOURCES: {len(sources)}",
        flush=True,
    )

    return sources


# ---------------------------------------------------------
# LLM research
# ---------------------------------------------------------

def research_app(app: dict) -> AppResearch:

    print(
        ">>> START collect_sources()",
        flush=True,
    )

    # -----------------------------------------------------
    # Step 1: collect evidence
    # -----------------------------------------------------

    sources = collect_sources(app)

    print(
        f">>> SOURCES COLLECTED: {len(sources)}",
        flush=True,
    )

    # -----------------------------------------------------
    # Step 2: build prompt
    # -----------------------------------------------------

    print(
        ">>> BUILDING PROMPT",
        flush=True,
    )

    prompt = RESEARCH_WITH_SOURCES_USER_PROMPT.format(
        name=app["name"],
        category=app["category"],
        website=app["website"],
        hint=app["docs_hint"],
        sources_json=json.dumps(
            sources,
            indent=2,
        ),
        schema_json=json.dumps(
            AppResearch.model_json_schema(),
            indent=2,
        ),
    )

    print(
        f">>> PROMPT SIZE: {len(prompt):,} characters",
        flush=True,
    )

    # -----------------------------------------------------
    # Step 3: send to Ollama
    # -----------------------------------------------------

    print(
        ">>> START LLM",
        flush=True,
    )

    try:

        response = client.chat.completions.create(
            model="qwen3:1.7b",

            temperature=0,

            response_format={
                "type": "json_object",
            },

            messages=[
                {
                    "role": "system",
                    "content": RESEARCH_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            # Limit output because we only need structured JSON.
            max_tokens=1500,
        )

    except Exception as e:

        print(
            ">>> LLM ERROR",
            flush=True,
        )

        print(
            str(e),
            flush=True,
        )

        raise

    # -----------------------------------------------------
    # Step 4: receive response
    # -----------------------------------------------------

    print(
        ">>> LLM RESPONSE RECEIVED",
        flush=True,
    )

    raw = response.choices[0].message.content

    if not raw:
        raise ValueError(
            "Ollama returned an empty response."
        )

    print(
        f">>> RESPONSE SIZE: {len(raw):,} characters",
        flush=True,
    )

    # -----------------------------------------------------
    # Step 5: parse JSON
    # -----------------------------------------------------

    print(
        ">>> PARSING JSON",
        flush=True,
    )

    try:

        data = json.loads(raw)

    except json.JSONDecodeError as e:

        print(
            ">>> INVALID JSON FROM MODEL",
            flush=True,
        )

        print(
            ">>> RAW MODEL RESPONSE:",
            flush=True,
        )

        print(
            raw,
            flush=True,
        )

        raise e

    # -----------------------------------------------------
    # Step 6: validate Pydantic schema
    # -----------------------------------------------------

    print(
        ">>> VALIDATING SCHEMA",
        flush=True,
    )

    result = AppResearch.model_validate(data)

    # -----------------------------------------------------
    # Done
    # -----------------------------------------------------

    print(
        ">>> RESEARCH COMPLETE",
        flush=True,
    )

    return result