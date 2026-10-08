#!/usr/bin/env python3
"""Render README.md, llms.txt and data/agents.json from data/catalog.json
plus live metadata in data/verified.json.

The catalog is the single source of truth: edit data/catalog.json + content/*.md,
never README.md (it is generated).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
CONTENT = os.path.join(ROOT, "content")

KIND_BADGE = {
    "oss": "OSS", "commercial": "SaaS", "spec": "Spec", "paper": "Paper",
    "resource": "Guide", "dataset": "Data", "model": "Model", "infra": "Infra",
}


def load(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as fh:
        return json.load(fh)


def slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", s).strip("-")


def fmt_stars(n) -> str:
    if not n:
        return "—"
    if n >= 1000:
        v = n / 1000
        return f"{v:.1f}k".replace(".0k", "k") if v < 100 else f"{round(v)}k"
    return str(n)


def read_content(name: str) -> str:
    p = os.path.join(CONTENT, name)
    if not os.path.exists(p):
        return ""
    with open(p) as fh:
        return fh.read().strip()


def status_cell(e: dict, v: dict) -> str:
    bits = []
    if e.get("version"):
        bits.append(f"`{e['version']}`")
    if v.get("latest_release"):
        d = v.get("latest_release_date") or ""
        bits.append(f"`{v['latest_release']}`" + (f" · {d}" if d else ""))
    if v.get("npm_version"):
        bits.append(f"npm `{v['npm_version']}`")
    if v.get("pypi_version"):
        bits.append(f"pypi `{v['pypi_version']}`")
    if not bits and e.get("status"):
        bits.append(e["status"])
    if v.get("archived"):
        bits.append("⚠️ archived")
    if v.get("http_status") and v["http_status"] >= 400:
        bits.append(f"⚠️ link {v['http_status']}")
    return " · ".join(bits) if bits else "—"


def entry_cell(e: dict, v: dict) -> str:
    url = e.get("url") or (f"https://github.com/{e['repo']}" if e.get("repo") else "")
    link = f"[{e['name']}]({url})" if url else e["name"]
    badge = KIND_BADGE.get(e.get("kind", "oss"), "")
    if e.get("kind") == "oss" and v.get("license"):
        badge = f"OSS · {v['license']}"
    tags = " ".join(f"`{t}`" for t in e.get("tags", []))
    return f"{link}{f' <sub>{badge}</sub>' if badge else ''}{(' ' + tags) if tags else ''}"


def render_table(entries: list[dict], verified: dict) -> str:
    rows = ["| Project | What it does | Stars | Release |", "|---|---|---|---|"]
    for e in entries:
        v = verified.get(e["id"], {})
        desc = e.get("description", "").strip().replace("\n", " ")
        if e.get("note"):
            desc = f"{desc} <br><sub>{e['note']}</sub>"
        rows.append(f"| {entry_cell(e, v)} | {desc} | {fmt_stars(v.get('stars'))} | {status_cell(e, v)} |")
    return "\n".join(rows)


def main() -> int:
    catalog = load(os.path.join(DATA, "catalog.json"))
    verified = load(os.path.join(DATA, "verified.json"), {}) or {}
    stats = load(os.path.join(DATA, "stats.json"), {}) or {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo_slug = catalog["meta"].get("repo", "kyliesparks/Awesome-ai-agents")

    cats = [c for c in catalog["categories"] if any(s.get("entries") for s in c.get("sections", []))]
    n_entries = sum(len(s.get("entries", [])) for c in cats for s in c.get("sections", []))
    n_repos = sum(1 for c in cats for s in c.get("sections", [])
                  for e in s.get("entries", []) if e.get("repo"))
    stars = {k: v.get("stars", 0) for k, v in verified.items() if v.get("stars")}
    total_stars = sum(stars.values())

    out: list[str] = [read_content("header.md"), ""]
    out.append(
        f"<sub>**{n_entries} curated entries** · **{n_repos}** open-source repositories · "
        f"**{fmt_stars(total_stars)}** combined GitHub stars · metadata re-verified **{today}**</sub>"
    )
    out.append("")
    out.append(read_content("state-of-2026.md"))
    out.append("")

    toc = ["## Contents", "", "- [How to read this list](#how-to-read-this-list)"]
    for c in cats:
        toc.append(f"- [{c['emoji']} {c['title']}](#{slug(c['emoji'] + ' ' + c['title'])})")
        sub = [s for s in c.get("sections", []) if s.get("entries")]
        if len(sub) > 1:
            for s in sub:
                if s.get("title"):
                    toc.append(f"  - [{s['title']}](#{slug(s['title'])})")
    for tail in ("Just getting started? Start here", "Related awesome lists",
                 "Contributing", "Machine-readable index", "Licence"):
        toc.append(f"- [{tail}](#{slug(tail)})")
    out.append("\n".join(toc))
    out.append("")
    out.append(read_content("how-to-read.md"))
    out.append("")

    for c in cats:
        out.append(f"## {c['emoji']} {c['title']}")
        out.append("")
        if c.get("description"):
            out.append(c["description"].strip())
            out.append("")
        sub = [s for s in c.get("sections", []) if s.get("entries")]
        for s in sub:
            if len(sub) > 1 and s.get("title"):
                out.append(f"### {s['title']}")
                out.append("")
                if s.get("blurb"):
                    out.append(s["blurb"].strip())
                    out.append("")
            out.append(render_table(s["entries"], verified))
            out.append("")

    for frag in ("start-here.md", "related-lists.md", "contributing-section.md",
                 "machine-readable.md", "footer.md"):
        body = read_content(frag)
        if body:
            out.append(body)
            out.append("")

    readme = re.sub(r"\n{4,}", "\n\n\n", "\n".join(out))
    with open(os.path.join(ROOT, "README.md"), "w") as fh:
        fh.write(readme)
    print(f"README.md written: {len(readme):,} chars, {n_entries} entries, "
          f"{fmt_stars(total_stars)} stars")

    agents = {
        "name": catalog["meta"].get("title", "Awesome AI Agents"),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verified_at": today,
        "count": n_entries,
        "stats": {k: stats.get(k) for k in ("repos_tracked", "total_stars", "categories")},
        "categories": [
            {
                "id": c["id"],
                "title": c["title"],
                "description": c.get("description", ""),
                "entries": [
                    dict(
                        {k: e[k] for k in ("id", "name", "description", "kind", "repo", "url",
                                           "tags", "license", "added") if k in e},
                        **{k: verified.get(e["id"], {})[k]
                           for k in ("stars", "latest_release", "latest_release_date",
                                     "pushed_at", "archived")
                           if verified.get(e["id"], {}).get(k)},
                    )
                    for s in c.get("sections", []) for e in s.get("entries", [])
                ],
            }
            for c in cats
        ],
    }
    with open(os.path.join(DATA, "agents.json"), "w") as fh:
        json.dump(agents, fh, indent=1)

    lines = [
        f"# {catalog['meta'].get('title', 'Awesome AI Agents')}",
        "",
        f"> Curated index of AI-agent frameworks, tools, protocols, benchmarks, papers and "
        f"products. {n_entries} entries · {n_repos} open-source projects · data verified {today}.",
        "",
        f"Machine-readable index: https://raw.githubusercontent.com/{repo_slug}/main/data/agents.json",
        "",
        "## Categories",
    ]
    for c in cats:
        n = sum(len(s.get("entries", [])) for s in c.get("sections", []))
        lines.append(f"- {c['title']} ({n} entries): "
                     f"https://github.com/{repo_slug}#{slug(c['emoji'] + ' ' + c['title'])}")
    lines += ["", "## Top 40 projects by GitHub stars"]
    for eid, st in sorted(stars.items(), key=lambda kv: -kv[1])[:40]:
        nm = verified.get(eid, {}).get("name", eid)
        lines.append(f"- {nm}: {st:,} stars")
    with open(os.path.join(ROOT, "llms.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("data/agents.json + llms.txt written")
    return 0


if __name__ == "__main__":
    sys.exit(main())