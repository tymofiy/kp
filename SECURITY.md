<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Security Policy

KP:1 is a specification repository: spec text, JSON Schemas, a PEG grammar,
conformance fixtures, and a small Python conformance runner. There is no
hosted service here — but security reports are still welcome and taken
seriously.

## What counts as a security issue here

- **Conformance tooling** — anything that makes `conformance/run.py` or
  `reference/kpack` unsafe to run against an untrusted pack: path traversal
  via crafted pack contents, resource exhaustion, code execution through
  YAML loading, and the like.
- **Schemas / grammar** — a flaw that causes a validator built from these
  artifacts to accept something the spec forbids in a security-relevant way.
- **Spec-level vectors** — weaknesses in the format's own security guidance,
  e.g. the `spec_uri` onboarding pointer (see the security note in
  [`spec/CORE.md`](spec/CORE.md) §3) or sealed-archive handling defined in
  [`spec/ARCHIVE.md`](spec/ARCHIVE.md).
- **CI / repository workflows** — injection or privilege issues in
  `.github/workflows/`.

## How to report

- **Preferred:** GitHub private vulnerability reporting — the
  ["Report a vulnerability"](https://github.com/tymofiy/kp/security/advisories/new)
  button under this repository's Security tab.
- Or email the editor: <tymofi@mac.com> with `[kp security]` in the subject.

Please do not open a public issue for anything you believe is exploitable
before it is fixed.

## What to expect

Best-effort acknowledgment within a few days. This is a single-editor
project in its preview phase; there is no bug bounty. Confirmed fixes land
as ordinary public commits, with credit to the reporter if wanted.

Non-security bugs in the conformance suite, grammar, or schemas should go
through a normal GitHub issue (label `bug`) per
[CONTRIBUTING.md](CONTRIBUTING.md).
