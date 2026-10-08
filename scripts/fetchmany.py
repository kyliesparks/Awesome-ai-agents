#!/usr/bin/env python3
"""Batch-fetch URLs to /tmp/fetch/<slug>.txt for grepping.

Usage:
    python3 scripts/fetchmany.py url1 url2 ...
    python3 scripts/fetchmany.py --list urls.txt
"""
from __future__ import annotations

import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from websearch import fetch_text  # noqa: E402

OUT = "/tmp/fetch"


def slug(url: str) -> str:
    s = re.sub(r"^https?://", "", url)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:150]


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == "--list":
        with open(args[1]) as fh:
            args = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    for url in args:
        path = os.path.join(OUT, slug(url))
        try:
            txt = fetch_text(url, limit=60000)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            txt, status = f"[fetch failed: {e!r}]", "FAIL"
        with open(path, "w") as fh:
            fh.write(f"### URL: {url}\n### status: {status}\n\n{txt}")
        print(f"{status:4} {len(txt):7d} {path}  <- {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())