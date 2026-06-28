# Decision: Claims carry one identifier in their file form

**Date:** 2026-06-22
**Status:** accepted
**Editor:** Timothy Kompanchenko

## Question

Does a claim's canonical file form (`claims.md`) carry a single identifier, or a
separate stable id distinct from its human-readable display id?

## Options considered

- **One id:** the `[C…]` in the claim line is the claim's sole identifier within the
  pack — both the reference target and the display id. No second canonical id in the file.
- **Two ids:** the file carries a separate stable id alongside the display id (e.g. an
  extra inline token), so the display id can be renumbered without breaking references.

## Choice

One identifier per claim in the file form.

## Rationale

The canonical file already models one id per claim: CORE.md §6.1 defines the id as
`[C` + digits `]`, and relations + evidence references resolve against that same id
(`→C002`, `⊗~C003`). There is no second id slot in the grammar. The globally unique
`claim_id` (ULID/UUIDv7) in STORAGE.md is an *operational* identifier for cross-pack
indexes — assigned at index time, derived from the pack, rebuildable — consistent with
the pack-as-master principle that no canonical knowledge lives only in an index. Carrying
a second id inside `claims.md` would put operational state into the canonical file and
create a format one conformant serializer can emit but another cannot read.

## Consequences

- A claim's `[C…]` id is stable within the pack and is the reference target; renaming it
  is a content edit that updates all references (there is no decoupled display id to
  renumber independently).
- An implementation whose in-memory model distinguishes a canonical `id` from a
  `display_id` MUST treat them as equal for the file form; a divergence is an error, not
  data to preserve — a serializer SHOULD reject `id ≠ display_id` rather than invent a
  file representation for it.
- The operational `claim_id` (STORAGE.md) is assigned at index time and is never
  serialized into `claims.md`.

## References

- spec/CORE.md §6.1 (Claim Syntax — Dense Form)
- spec/STORAGE.md (claim_index — operational identifiers)
