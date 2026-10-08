#!/usr/bin/env python3
"""Enrich every catalog entry with live, verifiable metadata.

* GitHub repos  -> stars, forks, open issues, latest release tag + date, last push, archived
* npm packages  -> latest version + publish date
* PyPI packages -> latest version + release date
* everything    -> HTTP status of the canonical URL

Output: data/verified.json  (keyed by entry id) + data/stats.json
Usage:  python3 scripts/verify.py [--only category-id] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
UA = "awesome-ai-agents-verify/1.0"


def http_json(url: str, tries: int = 3, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r), r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(10 * (attempt + 1))
                continue
            return None, e.code
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None, 0


def http_status(url: str, timeout: int = 25) -> int:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 405, 501):
                continue  # many sites reject HEAD; retry with GET
            return e.code
        except Exception:  # noqa: BLE001
            if method == "GET":
                return 0
    return 0


def strip_v(tag: str) -> str:
    return re.sub(r"^(v|release[-/])", "", tag.strip(), flags=re.I)


def verify_github(repo: str, out: dict) -> None:
    meta, status = http_json(f"https://api.github.com/repos/{repo}")
    out["gh_status"] = status
    if not meta:
        return
    out.update(
        {
            "full_name": meta["full_name"],
            "stars": meta["stargazers_count"],
            "forks": meta["forks_count"],
            "open_issues": meta["open_issues_count"],
            "language": meta.get("language") or "",
            "license": ((meta.get("license") or {}).get("spdx_id") or "").replace("NOASSERTION", ""),
            "archived": bool(meta.get("archived")),
            "created_at": (meta.get("created_at") or "")[:10],
            "pushed_at": (meta.get("pushed_at") or "")[:10],
            "default_branch": meta.get("default_branch") or "main",
        }
    )
    rel, rstatus = http_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        out["latest_release"] = strip_v(rel["tag_name"])
        out["latest_release_date"] = (rel.get("published_at") or "")[:10]
    elif rstatus == 404:
        tag, _ = http_json(f"https://api.github.com/repos/{repo}/tags")
        if isinstance(tag, list) and tag:
            out["latest_release"] = strip_v(tag[0]["name"])


def verify_pkg(entry: dict, out: dict) -> None:
    npm = entry.get("npm")
    pypi = entry.get("pypi")
    if npm:
        d, _ = http_json(f"https://registry.npmjs.org/{urllib.parse.quote(npm, safe='@')}")
        if isinstance(d, dict) and d.get("dist-tags", {}).get("latest"):
            v = d["dist-tags"]["latest"]
            out["npm_version"] = v
            out["npm_date"] = (d.get("time", {}).get(v) or "")[:10]
    if pypi:
        d, _ = http_json(f"https://pypi.org/pypi/{pypi}/json")
        if isinstance(d, dict):
            v = d.get("info", {}).get("version")
            if v:
                out["pypi_version"] = v
                out["pypi_date"] = (d.get("releases", {}).get(v) or [{}])[0].get("upload_time", "")[:10]


def load_catalog() -> dict:
    with open(os.path.join(DATA, "catalog.json")) as fh:
        return json.load(fh)


def iter_entries(catalog: dict, only: str | None):
    for cat in catalog["categories"]:
        if only and cat["id"] != only:
            continue
        for sec in cat.get("sections", []):
            for e in sec.get("entries", []):
                yield e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="restrict to one category id")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    catalog = load_catalog()
    vpath = os.path.join(DATA, "verified.json")
    verified: dict[str, dict] = {}
    if os.path.exists(vpath):
        with open(vpath) as fh:
            verified = json.load(fh)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries = list(iter_entries(catalog, args.only))
    if args.limit:
        entries = entries[: args.limit]

    checked = 0
    for i, e in enumerate(entries, 1):
        eid = e["id"]
        prev = verified.get(eid, {})
        if prev.get("verified_at") == today:
            continue
        out: dict = {"verified_at": today, "name": e["name"], "url": e.get("url") or e.get("repo")}
        if e.get("repo"):
            verify_github(e["repo"], out)
        verify_pkg(e, out)
        if e.get("url"):
            out["http_status"] = http_status(e["url"])
        verified[eid] = out
        checked += 1
        if checked % 25 == 0:
            print(f"  ...{checked} verified", flush=True)
            with open(vpath, "w") as fh:
                json.dump(verified, fh, indent=1, sort_keys=True)
        time.sleep(0.15)

    with open(vpath, "w") as fh:
        json.dump(verified, fh, indent=1, sort_keys=True)

    stars = {k: v.get("stars", 0) for k, v in verified.items() if v.get("stars")}
    stats = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entries_total": sum(1 for _ in iter_entries(catalog, None)),
        "entries_verified": len(verified),
        "categories": len(catalog["categories"]),
        "repos_tracked": len(stars),
        "total_stars": sum(stars.values()),
        "top_25": sorted(stars.items(), key=lambda kv: -kv[1])[:25],
        "broken_links": sorted(k for k, v in verified.items()
                               if v.get("http_status") and v["http_status"] >= 400),
        "archived": sorted(k for k, v in verified.items() if v.get("archived")),
    }
    with open(os.path.join(DATA, "stats.json"), "w") as fh:
        json.dump(stats, fh, indent=1)
    print(json.dumps({k: v for k, v in stats.items()
                      if k not in ("top_25", "broken_links", "archived")}, indent=1))
    print(f"broken links: {len(stats['broken_links'])}  archived: {len(stats['archived'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())