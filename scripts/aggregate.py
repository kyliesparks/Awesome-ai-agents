#!/usr/bin/env python3
"""Aggregate raw GitHub search results into a single ranked candidate list.

Input : data/raw_search.json
Output: data/candidates.json
        { "generated": "<iso date>", "total": N, "repos": [ {..normalised..} ] }
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# Repos that plausibly belong in an *agent* list: the word must appear in the name,
# description or topics (not merely in a README).
STRONG = re.compile(r"\b(agent|agents|agentic|multi-agent|mcp)\b", re.I)
HINT = re.compile(
    r"\b(agent|agents|agentic|mcp|model context protocol|autonomous|autogpt|"
    r"copilot|tool[- ]?use|tool[- ]?calling|function[- ]?calling|swarm|"
    r"computer use|browser use|deep research)\b",
    re.I,
)
# Noise: non-agent repos that happen to match, plus non-English interview dumps.
EXCLUDE_NAME = re.compile(
    r"^(awesome-.*|.*-roadmap|.*-cheatsheet|interview|leetcode|.*-ctf|hacktoberfest|"
    r"javaguide|.*-guide-zh|.*-notes|free-.*-books)$", re.I
)
NON_AGENT = re.compile(
    r"(面试|八股|curriculum vitae|mybatis|spring boot 教程|kubernetes 教程)", re.I
)


def normalise(it: dict) -> dict:
    lic = (it.get("license") or {}).get("spdx_id")
    return {
        "full_name": it["full_name"],
        "name": it["name"],
        "owner": it["owner"]["login"],
        "url": it["html_url"],
        "description": (it.get("description") or "").strip(),
        "homepage": it.get("homepage") or "",
        "stars": it.get("stargazers_count", 0),
        "forks": it.get("forks_count", 0),
        "issues": it.get("open_issues_count", 0),
        "language": it.get("language") or "",
        "license": "" if lic in (None, "NOASSERTION") else lic,
        "topics": sorted(it.get("topics") or []),
        "created_at": (it.get("created_at") or "")[:10],
        "pushed_at": (it.get("pushed_at") or "")[:10],
        "updated_at": (it.get("updated_at") or "")[:10],
        "archived": bool(it.get("archived")),
        "fork": bool(it.get("fork")),
        "size_kb": it.get("size", 0),
    }


def main() -> None:
    with open(os.path.join(DATA, "raw_search.json")) as fh:
        raw = json.load(fh)

    repos: dict[str, dict] = {}
    seen_in: dict[str, list[str]] = {}
    for query, items in raw.items():
        for it in items:
            if it.get("fork"):
                continue
            r = normalise(it)
            key = r["full_name"].lower()
            if key not in repos or r["stars"] > repos[key]["stars"]:
                repos[key] = r
            seen_in.setdefault(key, []).append(query)

    kept = []
    for key, r in repos.items():
        r["matched_queries"] = sorted(set(seen_in[key]))
        r["acm"] = len(r["matched_queries"])
        haystack = f'{r["name"]} {r["description"]} {" ".join(r["topics"])}'
        mq = r["matched_queries"]
        # A repo found through a specific agent/MCP topic query is relevant by construction.
        topic_hit = any(
            q.startswith("topic:") and re.search(r"agent|mcp|llmops|computer-use|browser-agent",
                                                 q, re.I)
            for q in mq
        )
        text_hit = bool(STRONG.search(haystack) and HINT.search(haystack))
        if not (topic_hit or text_hit or len(mq) >= 3):
            continue
        if EXCLUDE_NAME.match(r["name"]) and r["stars"] < 20000:
            continue
        if NON_AGENT.search(haystack):
            continue
        kept.append(r)

    kept.sort(key=lambda r: (-r["stars"], r["full_name"]))

    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(kept),
        "repos": kept,
    }
    with open(os.path.join(DATA, "candidates.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    print(f"queries: {len(raw)}  unique repos: {len(repos)}  agent-relevant: {len(kept)}")
    for r in kept[:40]:
        print(f'{r["stars"]:>7}  {r["full_name"]:<45} {r["description"][:70]}')


if __name__ == "__main__":
    main()