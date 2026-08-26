import os
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "AppScout Research Agent/1.0"


def search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search for URLs related to a query.

    Uses Tavily when TAVILY_API_KEY is set, otherwise DuckDuckGo HTML.
    Returns [{"url": "...", "title": "..."}].
    """
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        return _search_tavily(query, max_results, tavily_key)

    return _search_duckduckgo(query, max_results)


def _search_tavily(query: str, max_results: int, api_key: str) -> list[dict]:
    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": False,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return [
            {"url": r["url"], "title": r.get("title", r["url"])}
            for r in data.get("results", [])
            if r.get("url")
        ]
    except Exception:
        return []


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    try:
        response = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for link in soup.select("a.result__a"):
            href = link.get("href", "")
            title = link.get_text(strip=True)
            url = _resolve_duckduckgo_url(href)
            if not url:
                continue
            results.append({"url": url, "title": title or url})
            if len(results) >= max_results:
                break

        return results
    except Exception:
        return []


def _resolve_duckduckgo_url(href: str) -> str | None:
    if not href:
        return None

    if href.startswith("//"):
        href = "https:" + href

    parsed = urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg", [None])[0]
        return unquote(target) if target else None

    if parsed.scheme in ("http", "https"):
        return href

    return None
