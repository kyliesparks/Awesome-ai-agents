import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
KINDS = {"oss", "commercial", "spec", "paper", "resource", "dataset", "model", "infra"}
REQUIRED = {"id", "name", "description", "kind"}


def fail(msgs: list[str]) -> int:
    for m in msgs:
        print(f"  ✗ {m}")
    print(f"\n{len(msgs)} problem(s) found")
    return 1


def main() -> int:
    with open(os.path.join(DATA, "catalog.json")) as fh:
        cat = json.load(fh)
    problems: list[str] = []
    ids: dict[str, str] = {}
    urls: dict[str, str] = {}
    n = 0

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cat["meta"].get("updated", "")):
        problems.append("meta.updated must be YYYY-MM-DD")

    seen_cat_ids = set()
    for c in cat["categories"]:
        for key in ("id", "title", "emoji", "sections"):
            if not c.get(key):
                problems.append(f"category {c.get('id')!r} missing {key}")
        if c["id"] in seen_cat_ids:
            problems.append(f"duplicate category id {c['id']}")
        seen_cat_ids.add(c["id"])
        for sec in c["sections"]:
            if not sec.get("entries"):
                problems.append(f"category {c['id']} has an empty section")
            for e in sec["entries"]:
                n += 1
                eid = e.get("id", "?")
                missing = REQUIRED - set(e)
                if missing:
                    problems.append(f"entry {eid}: missing {sorted(missing)}")
                if eid in ids:
                    problems.append(f"duplicate entry id {eid}")
                ids[eid] = c["id"]
                if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", eid or ""):
                    problems.append(f"entry {eid}: id must be lowercase slug")
                if e.get("kind") not in KINDS:
                    problems.append(f"entry {eid}: kind must be one of {sorted(KINDS)}")
                url = e.get("url") or (
                    f"https://github.com/{e['repo']}" if e.get("repo") else "")
                if not url.startswith("http"):
                    problems.append(f"entry {eid}: needs an http(s) url or repo")
                key = url.rstrip("/").lower()
                if key in urls:
                    problems.append(f"duplicate url {url} ({eid} vs {urls[key]})")
                urls[key] = eid
                if e.get("repo") and not re.fullmatch(r"[\w.-]+/[\w.-]+", e["repo"]):
                    problems.append(f"entry {eid}: repo must be owner/name")
                if e.get("kind") == "oss" and not e.get("repo") and not e.get("url"):
                    problems.append(f"entry {eid}: OSS entry should link somewhere")
                d = e.get("description", "")
                if len(d) < 20:
                    problems.append(f"entry {eid}: description too short")
                if len(d) > 300:
                    problems.append(f"entry {eid}: description too long ({len(d)} chars)")
                if d.endswith((".", " ", "\n")):
                    e["description"] = d.rstrip(". \n")
                if e.get("added") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["added"]):
                    problems.append(f"entry {eid}: added must be YYYY-MM-DD")

    if problems:
        return fail(problems)
    print(f"✓ catalog valid: {len(cat['categories'])} categories, {n} entries, "
          f"{len(urls)} unique URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())