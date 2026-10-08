## Contributing

Contributions are welcome and reviewed on a rolling basis — see [CONTRIBUTING.md](CONTRIBUTING.md)
for the full rules. The short version:

- **Add an entry by editing `data/catalog.json`**, not `README.md` (the README is generated).
- One entry = one JSON object with a verified `url`, a one-line `description` written in your
  own words, a `kind`, and — if it's a GitHub project — `repo: "owner/name"`.
- Run `make check` locally, then commit the regenerated README (`python3 scripts/build_readme.py`).
- Something is listable if it works, is documented, and someone other than its author uses it.
- Corrections to *facts* (wrong licence, renamed product, dead link, archived project) are the
  most valuable PRs of all.

Missing something? Open an issue with the
[add-entry template](https://github.com/kyliesparks/Awesome-ai-agents/issues/new?template=add-entry.yml)
and it will be verified before it lands.
