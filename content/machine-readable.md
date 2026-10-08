## Machine-readable index

Agents should be able to read this list without scraping HTML. These files exist for that:

| File | What it contains |
|---|---|
| [`data/agents.json`](data/agents.json) | Every entry with category, description, kind, tags, stars, latest release and last-push date. |
| [`data/catalog.json`](data/catalog.json) | The curated source of truth (no volatile metadata). |
| [`llms.txt`](llms.txt) | The `llms.txt` convention index, following the [proposal](https://llmstxt.org/). |
| [`AGENTS.md`](AGENTS.md) | Instructions for coding agents working *on this repository*. |

Example — ask an agent to find a sandbox runtime without reading the README:

```bash
curl -s https://raw.githubusercontent.com/kyliesparks/Awesome-ai-agents/main/data/agents.json \
  | jq -r '.categories[] | select(.id=="runtimes") | .entries[] | "\(.name)\t\(.stars)\t\(.description)"'
```

Every entry also carries a `verified_at` stamp in `data/verified.json`, so consumers can tell
how fresh the metadata is.