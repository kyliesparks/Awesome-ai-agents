# Research Brief — Awesome AI Agents (2026 edition)

**Today's date is 2026-10-08.** The repository must describe the state of the art *as of now*.
Training-data knowledge is stale: **every factual claim must be verified against a live source
fetched during this session.** If you cannot verify something, mark it `UNVERIFIED` or omit it.

## Ground rules

1. **Never invent a URL, star count, version number, release date or benchmark score.**
   Fetch it. If the fetch fails, say so explicitly.
2. Prefer primary sources: official docs, official blogs/changelogs, the GitHub API,
   the Hugging Face API, npm/PyPI registries, arXiv.
3. Record for every item: name, canonical URL, one-line description, and *why it matters in 2026*.
4. Note the **as-of date** of every claim (e.g. "stars as of 2026-10-08").

## Tooling available in this workspace

```bash
# GitHub API (authenticated transparently through the egress proxy; core limit 5000/h)
curl -s 'https://api.github.com/repos/OWNER/REPO' | python3 -m json.tool | head -40
curl -s 'https://api.github.com/repos/OWNER/REPO/releases/latest'
curl -s 'https://api.github.com/search/repositories?q=QUERY&sort=stars&per_page=20'

# Fetch + read any web page as text (falls back to r.jina.ai renderer)
python3 scripts/websearch.py fetch https://example.com/some/doc

# Hacker News (Algolia) — great for 2026 signal, no key needed
curl -s 'https://hn.algolia.com/api/v1/search?query=agent%20protocol&tags=story&numericFilters=created_at_i>1735689600' | python3 -m json.tool | head -60

# Hugging Face models/datasets (what actually exists in 2026)
curl -s 'https://huggingface.co/api/models?search=agent&sort=trendingScore&limit=20' | python3 -m json.tool

# arXiv papers
curl -s 'https://export.arxiv.org/api/query?search_query=all:%22agent%22&sortBy=submittedDate&sortOrder=descending&max_results=20'

# npm / PyPI package metadata (latest version + release date)
curl -s 'https://registry.npmjs.org/-/v1/search?text=ai%20agent&size=20'
curl -s 'https://pypi.org/pypi/PACKAGE/json' | python3 -c "import json,sys;d=json.load(sys.stdin)['info'];print(d['version'], d['summary'])"
```

Notes:
* Bing scraping (`websearch.py search`) is **unreliable** in this sandbox — prefer direct
  fetches of known URLs, the APIs above, and `r.jina.ai/<url>` for JS-heavy pages.
* Rate limits: GitHub search = 30 requests/minute, core = 5000/hour. Sleep ~2s between
  search calls.

## Required output format

Write ONE markdown file per task, in `research/`, structured as:

```markdown
# <Topic>
_Research date: 2026-10-08_

## Key findings (2026)
- <finding> — source: <url> (fetched 2026-10-08)

## Verified entries
| Name | URL | Category | What it is (1 line) | 2026 relevance / status | Verified |
|------|-----|----------|---------------------|-------------------------|----------|
| ... | https://github.com/... | framework | ... | v1.2 released 2026-03; 12.3k stars | ✅ 2026-10-08 |

## Uncertain / could not verify
- ...

## Sources fetched
- <url> (status 200, 2026-10-08)
```

Keep it dense and factual. No filler prose. Include exact star counts and latest release
versions where relevant — they will be cited in the final README.
