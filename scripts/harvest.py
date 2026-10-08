#!/usr/bin/env python3
"""Harvest candidate AI-agent repositories from the GitHub Search API.

Writes data/raw_search.json  -> {query: [repo objects]}
All requests go through the authenticated egress proxy (no tokens handled here).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw_search.json")
UA = "awesome-ai-agents-harvester/1.0"

# Query set: topics first (precise), then free-text (broad).
TOPIC_QUERIES = [
    "topic:ai-agents",
    "topic:ai-agent",
    "topic:agents",
    "topic:llm-agent",
    "topic:llm-agents",
    "topic:agentic",
    "topic:agentic-ai",
    "topic:agent-framework",
    "topic:autonomous-agents",
    "topic:multi-agent",
    "topic:multi-agent-systems",
    "topic:mcp",
    "topic:model-context-protocol",
    "topic:mcp-server",
    "topic:ai-agent-framework",
    "topic:agentic-workflow",
    "topic:computer-use",
    "topic:browser-agent",
    "topic:coding-agent",
    "topic:agent-memory",
    "topic:llmops",
    "topic:agent-evaluation",
]

TEXT_QUERIES = [
    "ai agent framework",
    "llm agent framework",
    "autonomous agent llm",
    "multi-agent orchestration",
    "agentic ai",
    "llm agent memory",
    "agent observability llm",
    "browser automation agent llm",
    "computer use agent",
    "coding agent cli",
    "deep research agent",
    "rag agent",
    "agent evaluation benchmark llm",
    "tool calling llm",
    "workflow automation ai agent",
    "voice ai agent",
    "gui agent",
    "web agent llm",
    "agent protocol",
    "agent sandbox",
    "llm agent tutorial",
    "awesome ai agents",
]

MIN_STARS = 200
PAGES = 2  # 100 per page


def fetch(url: str, tries: int = 4) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                wait = 20 * (attempt + 1)
                print(f"  rate-limited ({e.code}); sleeping {wait}s", flush=True)
                time.sleep(wait)
                continue
            if e.code == 422:
                return {"items": []}
            print(f"  HTTP {e.code} for {url}", flush=True)
            return None
        except Exception as e:  # noqa: BLE001
            print(f"  error {e!r}; retrying", flush=True)
            time.sleep(5)
    return None


def search(q: str) -> list[dict]:
    items: list[dict] = []
    for page in range(1, PAGES + 1):
        if q.startswith("topic:"):
            query = f"{q} stars:>={MIN_STARS}"
        else:
            query = f'{q} in:name,description,readme stars:>={MIN_STARS}'
        url = f"{API}/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=100&page={page}"
        data = fetch(url)
        if not data:
            break
        batch = data.get("items", [])
        items.extend(batch)
        if len(batch) < 100:
            break
        time.sleep(2.5)
    return items


def main() -> int:
    results: dict[str, list[dict]] = {}
    if os.path.exists(OUT):
        with open(OUT) as fh:
            results = json.load(fh)

    queries = [q for q in TOPIC_QUERIES + TEXT_QUERIES if q not in results]
    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {q}", flush=True)
        items = search(q)
        results[q] = items
        print(f"    -> {len(items)} repos", flush=True)
        time.sleep(2.5)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(results, fh, indent=1)

    seen = {it["full_name"] for items in results.values() for it in items}
    print(f"\nunique repos: {len(seen)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
