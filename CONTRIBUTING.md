# Contributing to Awesome AI Agents

Thanks for helping. This list is a **build artifact**, so contributing means editing data, not
markdown. That keeps the star counts, licences and links honest for everybody.

## TL;DR

```bash
git clone https://github.com/kyliesparks/Awesome-ai-agents
cd Awesome-ai-agents
$EDITOR data/catalog.json          # add or fix one entry
python3 scripts/verify.py          # pull live metadata for it (optional but encouraged)
python3 scripts/build_readme.py    # regenerate README.md, llms.txt, data/agents.json
make check                         # validate + confirm everything is in sync
git commit -am "Add <project>" && git push
```

Open a pull request. CI will run the same checks.

## What belongs here

An entry earns a place if **all** of these are true:

1. **It is about agents**, not generic LLM tooling. "An agent" means a model given tools,
   memory and a goal, executing over multiple steps. Prompt templates, plain chatbots and
   model-serving stacks belong in other lists (see [README § Related awesome lists](README.md)).
2. **It actually works and is documented.** A README with usage, an install path, a licence.
3. **Someone other than the author uses it.** Popularity signals we accept: GitHub stars,
   npm/PyPI downloads, sustained release cadence, or adoption as a dependency/standard.
4. **It is current.** Open-source entries should have commits within roughly the last 18 months.
   Archived projects are marked ⚠️ archived rather than silently deleted, so people can find
   the successor.

We deliberately include a small number of **commercial products** (categories
*Commercial Platforms* and *Voice & Realtime Agents*) because that is where a lot of agent work
actually happens. Commercial entries must be generally available or in public beta, must have a
public pricing or docs page, and must be described neutrally — no marketing copy.

We do not list: link farms, SEO blog posts, "top 10 prompts" collections, projects that only
wrap a single API call, dead products, or anything whose primary purpose is to sell a course.

## Entry format

Add an object to the right `sections[].entries` array in `data/catalog.json`:

```json
{
  "id": "my-project",
  "name": "My Project",
  "repo": "owner/my-project",
  "url": "https://github.com/owner/my-project",
  "npm": "my-project",
  "description": "One sentence: what it is and what it is for, in your own words.",
  "kind": "oss",
  "license": "Apache-2.0",
  "tags": ["python", "orchestration"],
  "note": "Optional 2026-specific context, e.g. 'v2 rewrite shipped 2026-05'.",
  "added": "2026-10-08"
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | ✅ | lowercase slug, unique across the whole file |
| `name` | ✅ | as the project spells it, including capitalisation |
| `description` | ✅ | 20–300 chars, no trailing full stop, no marketing adjectives |
| `kind` | ✅ | `oss`, `commercial`, `spec`, `paper`, `resource`, `dataset`, `model`, `infra` |
| `repo` | for OSS | `owner/name`; enables automatic star/release tracking |
| `url` | recommended | canonical link. If it differs from the repo URL, give both |
| `npm` / `pypi` | optional | package name; enables version tracking |
| `tags` | optional | max 3, lowercase |
| `note` | optional | use for "renamed from X", "successor to Y", "acquired by Z" |
| `added` | ✅ | today's date |

`description` must be written by you. Do not paste the repo's tagline verbatim if it is
marketing copy — say what the thing *is* and who should use it.

## Style

- One sentence per entry. Present tense. Lead with the category noun
  ("Orchestration framework for…", "Sandboxed runtime for…").
- No "revolutionary", "blazingly fast", "the best", no emoji in descriptions.
- Prefer the project's own vocabulary for its concepts.
- If a project was renamed, keep the old name searchable in `note`.

## Correcting facts

The most valuable contributions are corrections: wrong licence, dead link, renamed product,
acquired company, abandoned repo, benchmark score that has moved on. Fix `data/catalog.json`,
regenerate, and say what you verified and where in the PR description.

## For coding agents

See [AGENTS.md](AGENTS.md) — it contains the exact commands and invariants to follow, plus the
policy that agents must not fabricate metadata.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

By contributing you agree to release your contribution under [CC0-1.0](LICENSE).