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

# Repos that match an agent keyword somewhere in name/description/topics.
AGENT_HINT = re.compile(
    r"\b(agent|agents|agentic|mcp|model context protocol|autonomous|autogpt|crew|"
    r"copilot|assistant|tool[- ]?use|tool[- ]?calling|function[- ]?calling|"
    r"multi[- ]?agent|swarm|sandbox|llmops|rag|orchestrat|workflow autom|"
    r"computer use|browser use|deep research|memory for llm|eval)\b",
    re.I,
)

# Noise: repos that merely mention "agent" in passing.
EXCLUDE_NAME = re.compile(
    r"^(awesome-.*|.*-roadmap|.*-cheatsheet|interview|leetcode|.*-ctf|hacktoberfest)$", re.I
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
        haystack = f'{r["name"]} {r["description"]} {" ".join(r["topics"])}'
        if not AGENT_HINT.search(haystack):
            continue
        if EXCLUDE_NAME.match(r["name"]) and r["stars"] < 20000:
            continue
        r["matched_queries"] = sorted(set(seen_in[key]))
        r["acm"] = len(r["matched_queries"])
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