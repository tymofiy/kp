# KP Reference Implementation

> **Status:** One implemented subcommand (`kpack lint`); every other `kpack` subcommand is a contract-pointer.

Reference parser, serializer, and linter for KP:1. Eventually this directory will hold the canonical tooling that:

- Parses `.kpack/` directories into structured objects
- Serializes structured objects back to `.kpack/` format
- Validates packs against the conformance suite
- Lints packs for authoring quality

Must pass the conformance suite. Cannot redefine the spec.

## What ships today

- **`kpack lint <path/to/pack.kpack>`** — implemented. Delegates to [`conformance/run.py`](../conformance/run.py) `--pack` with identical output and exit codes (0 pass / 1 fail / 2 usage). Supports `--strict` (parse `claims.md` through the normative PEG grammar), `--json` for a machine-readable result, and `--no-color`.
- **[`kpack`](kpack)** as a contract-pointer for everything else. Run `./kpack` to list the subcommands the spec describes and which spec section defines each one's contract; run `./kpack <subcommand>` for a one-paragraph summary.

The CLI is argparse end-to-end: unknown subcommands and unknown flags fail
loudly with exit code 2 — nothing is silently ignored. The implementation
lives in [`kpack_cli.py`](kpack_cli.py); [`kpack`](kpack) is a thin launcher
that keeps the no-install invocation working.

### Install as a console script (optional)

From a repository checkout:

```bash
pip install -e .
kpack lint examples/hello-world.kpack
```

`pip install -e .` (editable) is the supported install: `kpack lint` runs
the conformance runner from the repository tree, so the checkout must stay
present. A plain site-packages install will refuse `lint` with a message
saying exactly that.

```bash
$ ./kpack lint ../examples/hello-world.kpack
../examples/hello-world.kpack: PASS

$ ./kpack
kpack — KP:1 reference CLI (v0.8.2-preview)

Implemented today: kpack lint <pack>  (delegates to conformance/run.py)
Every other subcommand is a contract pointer to its spec section.

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

The actual implementations of `render`, `bundle`, `archive`, `new`, `reconcile`, `compose`, `patrol`, `promote`, `restore`, `play` are planned. The contract for each lives in the spec section the stub names.
