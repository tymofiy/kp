# Evidence — Encoded Evidence Fixture

## E001
> **type:** document | **captured:** 2026-07-11
> **source:** https://example.com/source-payload
> **kp-content-encoding:** markdown-backslash-v1

Captured source payload:
\## Claims
- [C001] This source-local claim is content, not a KP claim.
\## Evidence
\## E001
\- [E001] This source-local evidence bullet is content, not a sibling record.
\## E001 appendix
\##
  \## Indented source headings preserve their indentation.
\\## A source-authored leading backslash survives one decode pass.
\> **kp-content-encoding:** markdown-backslash-v1
