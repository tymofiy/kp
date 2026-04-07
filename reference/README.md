# KP Reference Implementation

> **Status:** Not started

Reference parser, serializer, and linter for KP:1.

This will be the canonical tooling that:

- Parses `.kpack/` directories into structured objects
- Serializes structured objects back to `.kpack/` format
- Validates packs against the conformance suite
- Lints packs for authoring quality

Must pass the conformance suite. Cannot redefine the spec.
