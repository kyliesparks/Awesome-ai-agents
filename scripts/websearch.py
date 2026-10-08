#!/usr/bin/env python3
"""Tiny web-search + page-fetch helper (no API keys needed).

Usage:
    python3 scripts/websearch.py search "best ai agent frameworks 2026"
    python3 scripts/websearch.py fetch https://example.com/page
"""
from __future__ import annotations

import html
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def search(query: str, count: int = 15) -> list[tuple[str, str, str]]:
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(query) + f"&count={count}&setlang=en"
    page = get(url)
    out: list[tuple[str, str, str]] = []
    for block in re.findall(r'<li class="b_algo".*?</li>', page, re.S):
        m = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not m:
            continue
        link, title = m.group(1), strip_tags(m.group(2))
        sn = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
        snippet = strip_tags(sn.group(1)) if sn else ""
        out.append((title, link, snippet[:400]))
    return out


def fetch_text(url: str, limit: int = 12000) -> str:
    try:
        page = get(url, timeout=45)
    except Exception as e:  # noqa: BLE001
        page = get("https://r.jina.ai/" + url, timeout=60) if "r.jina.ai" not in url else ""
        if not page:
            return f"[fetch failed: {e!r}]"
    if "<html" in page[:2000].lower() or "<!doctype" in page[:200].lower():
        page = re.sub(r"(?is)<(script|style|nav|footer|svg)[^>]*>.*?</\1>", " ", page)
        page = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", page)
        page = strip_tags(page)
        page = re.sub(r"\n{3,}", "\n\n", page)
        page = re.sub(r"[ \t]{2,}", " ", page)
    return page[:limit]


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "search":
        for i, (t, l, s) in enumerate(search(sys.argv[2]), 1):
            print(f"{i}. {t}\n   {l}\n   {s}\n")
    elif cmd == "fetch":
        print(fetch_text(sys.argv[2]))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
