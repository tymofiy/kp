# KP:1 — convenience targets
#
# The conformance runner is the only fully-implemented validator in this repo
# (per AGENTS.md). This Makefile is a convenience wrapper, not a build system.
# All targets are reproducible from a fresh clone after `pip install -r
# requirements.txt`.

PYTHON ?= python3
PACK   ?=

.PHONY: help install conformance pack lint clean

help:
	@echo "KP:1 conformance targets"
	@echo ""
	@echo "  make install        Install Python dependencies (pyyaml, jsonschema)"
	@echo "  make conformance    Run the full conformance suite (expects 19/19)"
	@echo "  make pack PACK=path Validate a single pack at PATH"
	@echo "  make lint           Same as conformance (alias)"
	@echo "  make clean          Remove __pycache__ and .pyc files"
	@echo ""
	@echo "Examples:"
	@echo "  make conformance"
	@echo "  make pack PACK=examples/solar-energy-market.kpack"

install:
	$(PYTHON) -m pip install -r requirements.txt

conformance:
	$(PYTHON) conformance/run.py

lint: conformance

pack:
	@if [ -z "$(PACK)" ]; then \
		echo "error: PACK is required. Usage: make pack PACK=path/to/your-pack.kpack"; \
		exit 2; \
	fi
	$(PYTHON) conformance/run.py --pack $(PACK)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
