#!/usr/bin/env python3
"""Harvest HN Algolia stories for a set of queries since 2025-01-01, dedupe, print TSV."""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

SINCE = 1735689600  # 2025-01-01
QUERIES = [
    "agent", "AI agent", "agentic", "MCP", "model context protocol", "A2A",
    "agent protocol", "Claude", "OpenAI", "Gemini", "LangGraph", "CrewAI",
    "computer use", "browser agent", "coding agent", "Claude Code", "Codex",
    "Codex CLI", "agent SDK", "agent framework", "LLM", "GPT", "Qwen",
    "DeepSeek", "Llama", "Mistral", "Grok", "Kimi", "GLM", "MiniMax",
    "agent evaluation", "evals", "sandbox", "agent memory", "AGI",
    "open model", "reasoning model", "tool use", "function calling",
    "agent payments", "agentic commerce", "x402", "skills", "subagent",
    "SWE-bench", "terminal-bench", "OSWorld", "tau-bench", "context engineering",
    "verifier", "RL environment", "agent harness", "inference cost",
]


def fetch(q: str, min_points: int) -> list[dict]:
    url = (
        "https://hn.algolia.com/api/v1/search?query="
        + urllib.parse.quote(q)
        + f"&tags=story&numericFilters=created_at_i>{SINCE},points>{min_points}"
        + "&hitsPerPage=100"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r).get("hits", [])


def main() -> int:
    min_points = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seen: dict[str, dict] = {}
    for q in QUERIES:
        try:
            hits = fetch(q, min_points)
        except Exception as e:  # noqa: BLE001
            print(f"# FAIL {q}: {e!r}", file=sys.stderr)
            continue
        for h in hits:
            oid = h.get("objectID")
            if oid and oid not in seen:
                h["_q"] = q
                seen[oid] = h
        time.sleep(1.2)
    rows = sorted(seen.values(), key=lambda h: h["created_at"])
    for h in rows:
        d = h["created_at"][:10]
        print("\t".join([d, str(h.get("points")), str(h.get("num_comments")), h.get("title", "").replace("\t", " "), h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}"]))
    print(f"# total {len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())