# Decision: A `selection` composition type for lenses over a single collection

**Date:** 2026-08-22
**Status:** Editor’s draft — proposed for public discussion
**Editor:** Timothy Kompanchenko

## Question

`composition.yaml` declares a `type` from a closed vocabulary — `meeting-prep`,
`briefing`, `research`, `presentation`. Each existing type composes knowledge
drawn from *several* packs for a *temporal* purpose: a meeting happens, a
briefing is delivered, a presentation is given.

A recurring shape in collection-holding domains does not fit any of them. An
exhibition catalogue, a loan agreement, an insurance schedule and a valuation
report are each a **lens over a subset of items that already live in exactly one
collection**. The items do not move. Nothing is duplicated. The composition is
not an event — it is a selection, and the same items may appear in several
selections at once and over many years.

Does KP:1 need a fifth composition type for this, or is it adequately served by
an existing one?

## Options considered

- **Model it as `presentation`.** An exhibition is presented, so the type is not
  absurd. But `presentation` carries an implied occasion and an implied audience,
  and an insurance schedule has neither. Using it would make the type name mean
  two different things depending on domain, which is the failure a closed
  vocabulary exists to prevent.

- **Model it as `briefing`.** A briefing is one-directional knowledge transfer to
  a recipient, which fits a loan agreement's counterparty but not an inventory
  held for the owner's own record. It also implies the composition is *about*
  bringing someone up to speed, where a selection is *about* the items.

- **Use a hub pack with `sub_packs`.** Hub/detail expresses membership, and
  membership is exactly what a selection is not: the works already belong to a
  collection, and a selection asserts no ownership relation. Two hubs claiming
  the same detail pack also invites the reading that membership is contested.

- **Add `selection` to the type vocabulary.** A composition whose members are
  chosen from one collection for a stated purpose, with no temporal occasion and
  no transfer of membership.

## Choice

Add `selection` to the `composition.yaml` type vocabulary.

## Rationale

Three properties distinguish it from every existing type, and all three are
already expressible in the composition machinery:

1. **The membership relation is unchanged.** A work in an exhibition is still
   held by its collection. The selection references; it does not re-home. This
   is precisely what the **No Duplication Rule** already requires of every
   composite pack: *"A composite pack MUST NOT duplicate claims from its
   referenced packs."* A selection is the case where that rule is not a
   constraint to be worked around but the whole point of the type.

2. **There is no occasion.** `meeting-prep` has a date and participants;
   `presentation` has an audience; `briefing` has a recipient. An insurance
   schedule has a purpose and a scope and no event. Modelling it under a
   temporal type forces authors to invent an occasion that does not exist, and
   invented metadata degrades every consumer that reads it as real.

3. **Selections overlap and persist.** The same work may sit in a loan, an
   insurance schedule and a catalogue simultaneously, for different durations,
   without any of them conflicting. The existing types are each singular and
   bounded in time; nothing in them expresses concurrent, long-lived,
   overlapping lenses.

The type earns its place because it changes what a consumer may infer. Reading
`type: presentation`, a consumer may reasonably expect an audience and an
occasion. Reading `type: selection`, it may expect a stable purpose, a scope,
and members that belong elsewhere — which is a different set of guarantees, and
guarantees are what a closed vocabulary is for.

## Consequences

- The type vocabulary in `spec/COMPOSITION.md` and the `type` enum in
  `conformance/grammar/kp-composition.schema.json` are normative and must move
  **together**; a decision recorded without both is inert.
- `selection` composes over one collection. A composition drawing from several
  collections is not a selection, and the distinction should be stated where the
  type is documented so the two do not blur.
- The No Duplication Rule needs no exception for this type. If a selection ever
  requires one, that is evidence the type has been mis-scoped.
- Open: whether a selection should declare its purpose in a closed vocabulary
  (exhibition, loan, insurance, valuation) or as free text. A closed vocabulary
  would make consumers able to reason about purpose; free text would not
  constrain domains the editor has not seen. This decision does not settle it.

## Worked example

```yaml
type: selection
selection:
  purpose: "Group exhibition at the fictional Example Gallery"
  collection: "example-gallery"
  scope: "Works displayed in the east room"
  prepared_for: "Example Gallery exhibition team"
  date: "2026-08-22"
members:
  - reference: "example-work-001"
  - reference: "example-work-002"
  - reference: "example-work-003"
pre_load:
  - "example-work-001"
  - "example-work-002"
  - "example-work-003"
```

Every member is a reference to a pack that already exists in the collection. The
selection pack carries claims *about the selection* — its scope, its date of
preparation, what it excludes and why — and restates nothing from the works
themselves.

## References

- `spec/COMPOSITION.md` — composition types, the No Duplication Rule
- `conformance/grammar/kp-composition.schema.json` — the `type` enum
