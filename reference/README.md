# KP Reference Implementation

> **Status:** Stub — `kpack` CLI is a contract-pointer; no real tooling yet.

Reference parser, serializer, and linter for KP:1. Eventually this directory will hold the canonical tooling that:

- Parses `.kpack/` directories into structured objects
- Serializes structured objects back to `.kpack/` format
- Validates packs against the conformance suite
- Lints packs for authoring quality

Must pass the conformance suite. Cannot redefine the spec.

## What ships today

- **[`kpack`](kpack)** — a contract-pointer stub. Run `./kpack` (or `python3 kpack`) to see the list of subcommands the spec describes and which spec section defines each one's contract. Run `./kpack <subcommand>` for a one-paragraph summary of that command's spec contract. This stub does not implement any command; it tells a fresh agent or human reader where to look when they expect a `kpack <subcommand>` to exist. The only currently-implemented validator in this repository is [`conformance/run.py`](../conformance/run.py).

```bash
$ ./kpack
kpack — KP:1 reference CLI stub (v0.8.1-preview)

This is a contract-pointer, not a runnable tool.
The only command that ships today is: python3 conformance/run.py

Subcommands and the spec sections that define them:

  lint        → spec/SPEC.md §13 Tooling
  test        → spec/SPEC.md §10 validation.yaml — Test Questions
  ...

$ ./kpack reconcile
kpack reconcile
  Spec contract: spec/RECONCILIATION.md (stub — design deferred to v0.9 / v1.0)
  ...
```

## What does not ship yet

The actual implementations of `lint`, `render`, `bundle`, `archive`, `new`, `reconcile`, `compose`, `patrol`, `promote`, `restore`, `play` are planned. The contract for each lives in the spec section the stub names.
