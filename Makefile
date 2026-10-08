.PHONY: help harvest aggregate verify build check new-entry linkcheck all

help:
	@echo "make harvest     # query the GitHub Search API -> data/raw_search.json"
	@echo "make aggregate   # raw_search.json -> data/candidates.json (ranked)"
	@echo "make verify      # live stars/releases/links -> data/verified.json"
	@echo "make build       # catalog.json + verified.json -> README.md, llms.txt, data/agents.json"
	@echo "make check       # validate catalog, check README is in sync"
	@echo "make linkcheck   # report dead links in the catalog"
	@echo "make all         # harvest, aggregate, verify, build"

harvest:
	python3 scripts/harvest.py

aggregate:
	python3 scripts/aggregate.py

verify:
	python3 scripts/verify.py

build:
	python3 scripts/build_readme.py

check:
	python3 scripts/validate.py
	python3 scripts/build_readme.py
	@git diff --quiet -- README.md llms.txt data/agents.json \
		|| (echo "✗ README/agents.json out of sync with the catalog - run 'make build' and commit" && exit 1)
	python3 scripts/validate.py --readme

linkcheck:
	python3 scripts/linkcheck.py

all: harvest aggregate verify build