## Related awesome lists

The agent ecosystem is too big for one file. These sibling lists go deeper on specific layers,
and they were used as discovery inputs (then re-verified) when building this one:

- [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) — runnable agent & RAG app examples.
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — the MCP server directory.
- [awesome-langchain](https://github.com/kyrolabs/awesome-langchain) — LangChain/LangGraph ecosystem.
- [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) — the broader LLM literature index.
- [awesome-llm-agents](https://github.com/kaushikb11/awesome-llm-agents) — research-oriented agent papers.
- [awesome-ai-agents (e2b)](https://github.com/e2b-dev/awesome-ai-agents) — the original, product-heavy list.
- [awesome-rag](https://github.com/awesome-rag/awesome-rag) — retrieval-augmented generation.
- [awesome-ai-coding](https://github.com/ai-for-developers/awesome-ai-coding-tools) — AI coding tools.
- [awesome-copilots](https://github.com/ericciarla/awesome-copilots) — copilot-style assistants.
- [awesome-ai-safety](https://github.com/keneth80/awesome-ai-safety) — safety, alignment and governance.

---

## How this list is maintained

Most awesome lists rot. This one is a build artifact:

```text
data/raw_search.json   ← harvested from the GitHub Search API across ~44 agent queries
        │  scripts/aggregate.py
        ▼
data/candidates.json   ← ~1,500 agent-relevant repos, ranked by stars
        │  human curation (descriptions, categories, non-GitHub entries)
        ▼
data/catalog.json      ← the single source of truth you edit
        │  scripts/verify.py         (GitHub/npm/PyPI + HTTP status, live)
        ▼
data/verified.json     ← stars, licences, latest releases, dead links
        │  scripts/build_readme.py
        ▼
README.md · llms.txt · data/agents.json
```

* **Weekly** (`.github/workflows/refresh-data.yml`): re-verify stars, releases and links, then
  rebuild `README.md`, `llms.txt` and `data/agents.json` and open a PR if anything changed.
* **On every push/PR** (`.github/workflows/ci.yml`): validate `data/catalog.json` against its
  JSON schema, fail on duplicate ids/URLs, check that `README.md` is in sync with the catalog,
  and run a link checker.
* **`data/agents.json` and `llms.txt`** are there so agents (and other tools) can consume this
  list directly. That felt like the right 2026 default.
* **`AGENTS.md`** documents how to update this repo if you're an agent, not a human.