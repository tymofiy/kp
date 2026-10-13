<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Archive Format — Knowledge Pack Companion Spec

> **Date:** 2026-04-12
> **Status:** Draft
> **Resolves:** AR-14 — `signatures.yaml` schema (formal artifact: [`conformance/grammar/kp-signatures.schema.json`](../conformance/grammar/kp-signatures.schema.json))

> **`kpack` CLI invocations in this document describe planned reference tooling.** `python3 conformance/run.py`, `./reference/kpack lint` and `./reference/kpack new` ship today. See [SPEC.md §13](SPEC.md) and the reference launcher at [`reference/kpack`](../reference/kpack) for status.

---

## 1. Purpose

A Knowledge Pack is a directory of plain text files. This is correct for editing, version control, and the Voyager Principle — any intelligence can read the files without tooling.

But directories cannot travel. When a pack moves between systems — client to server, server to client, backup to archive — a single-file format is needed. This companion spec defines the **archive format**: a sealed, hashed, versioned single-file representation of a Knowledge Pack.

### Relationship to BUNDLE.md and STORAGE.md

Three companion specs address three questions about pack representation:

| Spec | Question | Target | Properties |
|------|----------|--------|------------|
| **STORAGE.md** | How does a pack *exist*? | Databases, caches, file systems | File / JSON / Compact serializations |
| **BUNDLE.md** | How does a pack travel to an *intelligence*? | AI chat windows, email, human readers | Markdown concatenation, AI-readable, Voyager-compliant |
| **ARCHIVE.md** | How does a pack travel between *systems*? | Client-server transfer, backup, integrity chain | Zip container, hashed, signed, versioned |

BUNDLE is infrastructure-free and human-readable. ARCHIVE is infrastructure-aware and machine-targeted. Both are single-file representations of the same directory. They serve different purposes and neither replaces the other.

---

## 2. Format Definition

A Knowledge Pack archive is a **ZIP file** containing the pack's directory contents.

### File extension

The `.kpack` extension is used for both directory and archive forms:

| Context | Form | Example |
|---------|------|---------|
| On disk, in git, during editing | Directory | `marquet-le-passeur.kpack/` |
| In transit, in storage, in backup | ZIP file | `marquet-le-passeur.kpack` |

Tools distinguish the two forms by checking whether the path is a file or directory. This mirrors macOS bundle conventions (`.app/` is a directory that behaves as a unit).

**Filesystem coexistence.** A file and a directory cannot share the same path. When sealing a pack, the archive MUST be written to a different location than the source directory — either a specified output path (`-o`) or the current working directory. The naming convention describes how the artifact is *identified*, not that both forms coexist at the same path. See §7 for CLI examples.

### Archive contents

The ZIP file contains the pack directory's contents at the root level — not nested inside a subdirectory:

```text
marquet-le-passeur.kpack (ZIP)
├── PACK.yaml
├── claims.md
├── evidence.md
├── signatures.yaml        # REQUIRED in sealed archives — integrity metadata (absent in export archives)
├── entities.md             # if present in pack (deprecated — legacy packs only)
├── history.md              # if present in pack
├── composition.yaml        # if present in pack
├── validation.yaml         # if present in pack
├── views/
│   ├── overview.md
│   └── briefing.md
├── definitions/            # if present in pack
│   └── *.yaml
├── policies/               # if present in pack
│   └── *.yaml
└── attachments/            # if present in pack
    └── *
```

### Requirements

1. The archive MUST be a valid ZIP file (PKZIP format, per APPNOTE.TXT).
2. Entries MUST be rooted at the pack directory level — no extra wrapper subdirectory. (Nested paths like `views/overview.md` and `attachments/photo.jpg` are expected; the rule prohibits wrapping the entire pack in a subdirectory like `marquet-le-passeur/PACK.yaml`.)
3. `PACK.yaml` and the files required for the declared kind MUST be present (per [CORE.md §2](CORE.md#2-pack-structure)). Claim-bearing and composition packs require `claims.md`; definition/policy packs use their companion documents.
4. `signatures.yaml` MUST be present in any archive that participates in an integrity chain (§4). It MAY be absent in archives created for convenience (e.g., manual export). See "Conformance levels" below.
5. Compression method SHOULD be DEFLATE. Store (no compression) is acceptable for small packs or when speed is preferred.
6. ZIP64 extensions MUST be used for archives exceeding 4 GB (archives without ZIP64 at this size are invalid, not merely suboptimal).
7. ZIP encryption MUST NOT be used. Access control is handled at the transport and storage layers, not the container layer. If confidentiality is required, encrypt the archive file itself (e.g., age, GPG) rather than using ZIP encryption.

### Safety requirements

Archives are ZIP files and carry the same security risks as any ZIP container. Implementations MUST enforce:

8. **No path traversal.** ZIP entries containing `..` path segments, absolute paths (leading `/` or drive letters like `C:\`), or backslash separators MUST be rejected during extraction and verification.
9. **No symlinks.** ZIP entries marked as symbolic links MUST be rejected. Symlinks enable arbitrary file reads and are not portable across platforms.
10. **No duplicate entries.** ZIP entries with identical paths MUST be rejected (some ZIP implementations silently overwrite; the behavior is undefined and exploitable).
11. **No special files.** Device files, FIFOs, and other non-regular-file entries MUST be rejected.
12. **OS metadata exclusion.** The excluded set is exactly:

    ```text
    .DS_Store     Thumbs.db     desktop.ini     __MACOSX     ._*
    ```

    These SHOULD be stripped on archive creation and MUST be ignored during hash computation. **This requirement is the single normative statement of the excluded set; other sections refer to it rather than restating it.**

    **Matching is by path component, at any depth:** a path is excluded if any of its components matches an entry in the set — `.DS_Store`, `Thumbs.db`, `desktop.ini` and `__MACOSX` by equality, and `._*` by prefix, meaning a component beginning with `._` (AppleDouble sidecar files). A file at `views/.DS_Store` is excluded; so is one at `._resources/notes.md`.

    **No open-ended prefix exclusions.** Named OS-metadata patterns are enumerable, and the set above is closed and complete. `._*` is a named pattern with a bounded meaning — AppleDouble sidecars — not an open class such as "every dotfile". A file named `.provenance`, `.gitattributes` or `.anything-else` **is part of the pack and is included in the hash.**

### Conformance levels

| Level | `signatures.yaml` | Integrity chain | Use case |
|-------|-------------------|-----------------|----------|
| **Sealed archive** | REQUIRED | Participates | Client-server transfer, versioned storage, regulated contexts |
| **Export archive** | ABSENT | Does not participate | Manual sharing, convenience export, one-off backup |

An export archive is a valid ZIP containing a valid pack. It is not sealed and does not participate in the integrity chain. Tools that expect sealed archives MUST reject export archives with a clear error rather than silently skipping verification.

### Format discoverability

A receiver that encounters a `.kpack` archive cold — with no surrounding context, no documentation, no prior exposure to KP:1 — should be able to learn the format from the archive itself. Two pack-internal mechanisms support this, **in this order of priority**:

1. **Rosetta header (load-bearing).** For claim-bearing packs, the first line of `claims.md` is a self-describing HTML comment naming the format epoch and tokenization legend ([CORE.md §4](CORE.md#4-claimsmd--rosetta-header)). Definition/policy kinds instead use the manifest and their companion document rules; they need not invent a claims file or header. The Rosetta header is the offline, network-free parse signal — it does not depend on any external resource.
2. **`spec_uri` / `spec_version` (informational onboarding pointer).** Sealed-archive producers SHOULD declare a discovery URL on PACK.yaml pointing to the full KP:1 specification ([CORE.md §3 "Spec Onboarding Pointer"](CORE.md#spec-onboarding-pointer)). When present, a previously-unfamiliar consumer can fetch the spec from the URL the pack itself names — useful for first-time onboarding of agents that have never encountered KP:1 before. **`spec_uri` is informational, not a runtime parse dependency.** Consumers MUST NOT treat unreachability of `spec_uri` as a parse failure; claim-bearing headers provide the inline parse hint; supported companion kinds use their local files and known companion rules. Once a consumer has internalized the format, `spec_uri` carries no further operational weight.

Consumers SHOULD read PACK.yaml first and, on initial encounter, follow `spec_uri` (when declared) to onboard against the spec for the pack's declared `spec_version`. When `spec_uri` is absent, consumers MAY assume the published reference implementation at `https://github.com/tymofiy/kp` but MUST treat the assumption as informational, not a guarantee. Offline-first validators MUST NOT fail on absent or unreachable `spec_uri` — the field's purpose is onboarding ergonomics, not integrity.

The file extension identifies the format family; a claim-bearing pack's header supplies its inline parse hint, and the manifest declares its kind. The optional onboarding pointer helps an unfamiliar receiver learn the format. Readers that implement the relevant companion rules can parse the supported local files without network access.

---

## 3. Content Hash

The integrity of an archive is verified by its **content hash** — a deterministic hash computed from the pack's file contents. The hash is of the *knowledge*, not the *container*: re-zipping the same files produces the same content hash even if the ZIP metadata differs.

### Computation

1. Enumerate all files in the pack directory, excluding `signatures.yaml` **at the root level**. (A file at `attachments/signatures.yaml` is included normally.)
2. For each file, compute SHA-256 over its **raw bytes**. (Empty files hash as the SHA-256 of the empty string: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.)
3. Normalize each file path:
   - Use `/` as the path separator (no `\`).
   - Use bare relative paths: no leading `./`, `../`, or `/`.
   - Apply **Unicode NFC normalization** to the path string. (macOS decomposes filenames to NFD; other systems use NFC. Without normalization, the same filename produces different path bytes on different operating systems.)
4. Express each file's SHA-256 digest as **lowercase hexadecimal**.
5. Sort the file list by normalized path (UTF-8 byte order, case-sensitive).
6. Concatenate entries as `{normalized-path}\0{lowercase-hex-digest}\n` (null byte separating path from digest, newline terminating each entry).
7. Compute SHA-256 over the concatenation. This is the **pack hash**.

### Example

Given a pack with three files:

```text
claims.md     → SHA-256: a1b2c3...
PACK.yaml     → SHA-256: d4e5f6...
views/overview.md → SHA-256: 789abc...
```

Sorted by path:

```text
PACK.yaml\0d4e5f6...\n
claims.md\0a1b2c3...\n
views/overview.md\0789abc...\n
```

SHA-256 of this concatenation → pack hash.

### Canonicalization notes

- **Line endings.** Hashing operates on raw bytes, so `\r\n` and `\n` produce different hashes. Implementations that use git SHOULD set `* text=auto eol=lf` in `.gitattributes` within the pack directory to prevent `core.autocrlf` from altering line endings across platforms.
- **OS metadata files.** Operating-system metadata is not part of the Knowledge Pack. Implementations MUST exclude it from hash computation and SHOULD exclude it from archives. **The excluded set is defined once, in §2 requirement 12** — see §10 (Security Considerations) for why these files are excluded rather than which they are.

### Draft policy compatibility

The component matching and AppleDouble exclusions in this draft can produce a different content hash from earlier published rules. `seal_version` selects a signing payload, not an exclusion policy. Historical artifacts MUST NOT be silently reserialized or re-sealed to satisfy the new policy. A verification receipt must identify the exact spec revision/hash rules it applied. An explicitly selected historical compatibility mode may verify the historical rules; automatic fallback from a current-policy mismatch MUST NOT be presented as current-policy success. Keep historical bytes and receipts. See [COMPATIBILITY.md](COMPATIBILITY.md).

Fixed expected hashes in [archive-hash-vectors.json](../conformance/fixtures/archive-hash-vectors.json) cover component exclusions, retained ordinary dotfiles, root-only receipt exclusion, NFC filenames and raw line endings. The [reference helper](../conformance/archive_hash.py) accepts an already enumerated regular-file map; it does not implement archive extraction or signature/chain verification.

### Properties

- **Deterministic.** Same file contents and file paths always produce the same pack hash, regardless of filesystem ordering, ZIP implementation, creation timestamp, or operating system.
- **Content-addressed.** Changing any file's contents changes the pack hash. Adding or removing a file changes the pack hash.
- **Self-excluding.** Root-level `signatures.yaml` is excluded from the hash computation because it contains the hash. This avoids the circular dependency.

---

## 4. `signatures.yaml`

This section defines the schema for `signatures.yaml`, resolving SPEC.md §2's "Tooling only — Cryptographic hashes + signing key for integrity verification" and CORE.md AR-14. The normative JSON Schema artifact is [`conformance/grammar/kp-signatures.schema.json`](../conformance/grammar/kp-signatures.schema.json); the conformance runner validates `signatures.yaml` against it whenever the file is present.

### Schema

```yaml
# signatures.yaml — integrity metadata for a sealed Knowledge Pack

# Hash algorithm (currently only SHA-256; future-proofed for upgrades)
algorithm: SHA-256

# Stable pack identity across versions (OPTIONAL for legacy archives;
# SHOULD be present in new archives — see "Required fields" below)
pack_id: "0b3c1f9a-4d7e-4a1c-9f2b-3e4a5b6c7d8e"

# Self-describing receipts (OPTIONAL; mirrors PACK.yaml name/version)
pack_name: "solar-energy-market"
pack_version: "2026.03.18"

# Signing-payload version (§4.2) — omit for v1
seal_version: "2"

# Pack hash — computed per §3
pack_hash: "a1b2c3d4e5f6..."

# Per-file hashes — lowercase hex, must not include signatures.yaml itself
files:
  PACK.yaml: "d4e5f6..."
  claims.md: "a1b2c3..."
  evidence.md: "789abc..."
  views/overview.md: "def012..."

# Sealing metadata
sealed_at: "2026-04-12T14:30:00Z"    # ISO 8601 UTC timestamp
sealed_by: "capture-client"            # Identity of the sealing system

# Version chain (§5) — absent for v1 (first version)
parent:
  version: "2026.04.11"               # Parent pack version
  pack_hash: "fedcba987654..."         # Parent pack hash

# Optional digital signature (§4.2)
signature:
  method: "ed25519"                    # or "hmac-sha256", "rsa-pss-sha256"
  value: "base64-encoded-signature..." # Signature over the signing payload (§4.2)
  key_id: "my-signing-key-2026"        # Key identifier for verification
```

### Field types

| Field | Type | Format |
|-------|------|--------|
| `algorithm` | string | Algorithm identifier. Currently `SHA-256`. |
| `pack_id` | string | Stable identity of the pack across versions. A UUID is RECOMMENDED. Two sealed archives MUST share the same `pack_id` if and only if they represent versions of the same logical pack. |
| `pack_name` | string | Self-describing copy of `PACK.yaml.name`. Enables receipts and indexing without loading the manifest. |
| `pack_version` | string | Self-describing copy of `PACK.yaml.version`. Same rationale as `pack_name`. |
| `seal_version` | string | OPTIONAL. Signing-payload version (§4.2). Absent means v1, whose payload does not cover `pack_id`. Present values: `"2"`. Itself a signed field, so it cannot be stripped to select a weaker payload. |
| `pack_hash` | string | Lowercase hex-encoded SHA-256 digest (64 characters). |
| `files` | map\<string, string\> | Keys: NFC-normalized relative paths with `/` separator. Values: lowercase hex SHA-256 digests. MUST NOT include `signatures.yaml`. |
| `sealed_at` | string | ISO 8601 UTC timestamp (e.g., `2026-04-12T14:30:00Z`). |
| `sealed_by` | string | Identifier of the sealing system (e.g., `capture-client`, `analysis-service`). |
| `parent.version` | string | Parent pack's version string from its PACK.yaml. |
| `parent.pack_hash` | string | Parent pack's `pack_hash` (lowercase hex). |
| `parent.merge_parents` | array\<object\> | OPTIONAL. Additional parent references for branch-merge lineage. Each entry has the same shape as `parent` itself (`version` + `pack_hash`). Absent in single-parent archives. |
| `signature.method` | string | Signing method identifier: `ed25519`, `hmac-sha256`, or `rsa-pss-sha256`. |
| `signature.value` | string | Base64-encoded (standard, padded) signature over the signing payload. |
| `signature.key_id` | string | Opaque key identifier for locating the verification key. |

### Required fields

| Field | Required | When |
|-------|----------|------|
| `algorithm` | Always | |
| `pack_hash` | Always | |
| `files` | Always | |
| `sealed_at` | Always | |
| `sealed_by` | Always | |
| `pack_id` | New archives | SHOULD be present in archives sealed against v0.7.5 or later. Schema accepts absence for backwards compatibility with archives sealed before `pack_id` was documented. Readers MUST tolerate its absence. |
| `pack_name` | Never | OPTIONAL; aids self-describing receipts. |
| `pack_version` | Never | OPTIONAL; aids self-describing receipts. |
| `parent` | When version > 1 | Absent for the first version of a pack |
| `parent.version` | When `parent` is present | Both sub-fields are REQUIRED when the `parent` block exists |
| `parent.pack_hash` | When `parent` is present | |
| `parent.merge_parents` | Never | OPTIONAL; populated only when a version results from merging two or more lineages |
| `signature` | When signing is configured | Optional; depends on deployment |
| `signature.method` | When `signature` is present | All three sub-fields are REQUIRED when the `signature` block exists |
| `signature.value` | When `signature` is present | |
| `signature.key_id` | When `signature` is present | |

### 4.1 Sealing

**Sealing** is the act of computing the content hash and writing `signatures.yaml`. A sealed pack is one whose `signatures.yaml` is present and whose `pack_hash` matches the computed hash.

Sealing happens at every version transition in the pack lifecycle:

| Transition | Sealer | Example |
|------------|--------|---------|
| Capture → v1 | Capture client (on-device) | User photographs a document |
| Analysis → v2 | Analysis service | Service extracts claims and evidence |
| Research → v3 | Research service | Research loop completes |
| Edit → v(n+1) | Analysis service | User edits are merged |

### 4.2 Signing (optional)

Signing provides **tamper evidence** for the sealing metadata — proof that `pack_hash`, `sealed_at`, `sealed_by`, and the primary parent fields (`parent.version`, `parent.pack_hash`) have not been modified since sealing. It is OPTIONAL because:

- Single-user deployments gain little from signing.
- Multi-tenant deployments (auction houses, galleries) benefit from knowing *which system* sealed a version.
- Regulatory contexts (provenance disputes, legal discovery) may require it.

**Signing payload.** The signature is computed over a canonical byte string that binds the metadata, not just the pack hash. This prevents an attacker from rewriting sealing metadata while preserving a valid signature.

There are two payload versions. A seal declares which one it uses with the OPTIONAL top-level `seal_version` field in `signatures.yaml`; **its absence means v1.**

**Payload v1** (`seal_version` absent) — the original form:

```text
{algorithm}\n{pack_hash}\n{sealed_at}\n{sealed_by}\n{parent.version or empty}\n{parent.pack_hash or empty}\n
```

**Payload v2** (`seal_version: "2"`) — adds `pack_id`, and adds the version declaration itself:

```text
{seal_version}\n{algorithm}\n{pack_hash}\n{pack_id or empty}\n{sealed_at}\n{sealed_by}\n{parent.version or empty}\n{parent.pack_hash or empty}\n
```

In both, absent fields are the empty string, and all fields use their literal `signatures.yaml` values — no normalization or transformation.

**The version declaration is itself a signed field, and MUST be.** A verifier selects the payload from `seal_version`, so a marker held outside the signature would be a downgrade rather than a protection: an attacker strips it from a v2 seal, the verifier falls back to v1, the v1 payload does not cover `pack_id`, and the seal verifies — while carrying a claim of being fixed. Because the declaration is signed, stripping it yields a v1 payload that cannot match a v2 signature, and adding it to a v1 seal yields a v2 payload that cannot match a v1 signature. Neither direction forges; both fail closed. Verifiers MUST refuse a seal declaring a `seal_version` they do not implement, and MUST NOT fall back to a payload version the seal did not declare.

Producers SHOULD emit v2. Verifiers MUST accept both.

> **Scope note — what a v1 seal does and does not attest.** `signatures.yaml` is excluded from the pack content hash (§3), so any field inside it that the payload does not name is covered by **neither** the signature **nor** the hash. Under v1 that includes **`pack_id`**: an attacker can add, change, or remove a pack's identity inside a signed archive without invalidating anything, undetectably. Since identity is what groups a pack's revisions into a family, a v1 pack can be made to claim another pack's identity and enter its lineage — so **verification of a v1 seal is not verification of the identity it carries**, and consumers MUST treat a v1 `pack_id` as transport metadata rather than as a signed assertion. v2 closes this for seals minted under it; **v1 seals remain identity-rewritable by construction, permanently**, because they were signed over a payload that never covered the field. Existing packs are repaired only by being re-sealed at v2.
>
> `parent.merge_parents` entries (§4 field table) are outside **both** payload versions for the same reason and remain **unauthenticated lineage hints** under v1 and v2 alike: an attacker can add, remove, or alter them in a signed archive without invalidating anything. Verifiers MUST NOT treat merge-parent assertions as tamper-evident; only the referenced archives' own contents can be verified, never the assertion that they are parents of this pack. A future payload revision may extend coverage.

**Signing procedure:**

1. Compute the pack hash per §3.
2. Assemble the signing payload as defined above.
3. Sign the payload using the configured method.
4. Record the signature (base64-encoded), method, and key identifier in `signatures.yaml`.

**Supported methods:**

| Method | Type | Properties |
|--------|------|------------|
| `ed25519` | Asymmetric | Non-repudiation. Compact signatures. Recommended for multi-party contexts. |
| `hmac-sha256` | Symmetric (shared secret) | Tamper detection only — does **not** provide non-repudiation (both parties hold the key). Suitable for single-tenant or internal deployments. |
| `rsa-pss-sha256` | Asymmetric | Non-repudiation. Compatible with existing PKI. Uses PSS padding (PKCS#1 v2.1). |

Implementations SHOULD support at minimum Ed25519. HMAC-SHA256 MAY be supported for simpler deployments where non-repudiation is not needed.

**Key distribution** is out of scope for this spec. The `key_id` field identifies the key; how verification keys are discovered, distributed, and trusted is an implementation and deployment concern. Implementations MAY use well-known endpoints, key registries, or out-of-band exchange.

---

## 5. Version Chain

Each sealed version of a pack references its parent, forming an integrity chain. A verified chain establishes the exercised hash links among the available revisions; it does not prove that every historical revision or source artifact was retained.

### Chain structure

```text
v1 (capture)  →  v2 (analyzed)  →  v3 (researched)  →  v4 (edited)  →  v(n)
   hash: aaa        hash: bbb         hash: ccc          hash: ddd
   parent: ∅        parent: aaa       parent: bbb        parent: ccc
```

Each version's `signatures.yaml` contains the `parent` block with the previous version's `version` string and `pack_hash`. The first version has no parent.

### Verification

To verify a chain:

1. Start with the earliest available version.
2. Compute its pack hash. Confirm it matches `signatures.yaml.pack_hash`.
3. Move to the next version. Confirm its `parent.pack_hash` matches the previous version's `pack_hash`.
4. Repeat until the current version.

A broken chain (parent hash mismatch) indicates tampering, data loss, or a version created outside the integrity system. Broken chains SHOULD be flagged but MUST NOT prevent the pack from being read — the knowledge is still valid even if the chain is broken.

### Branching

Version chains may branch when multiple systems modify the same pack concurrently (e.g., two users editing simultaneously). Branch resolution is an implementation concern, not a spec concern. This spec defines the linear chain and the `parent.merge_parents` data shape (§4); branch conflict-resolution *policy* is deferred to a future version of this spec.

---

## 6. Archive Operations

### 6.1 Create (pack → archive)

```text
Input:  name.kpack/  (directory)
Output: name.kpack   (ZIP file with signatures.yaml, written to -o path or cwd)

Steps:
1. Exclude OS metadata files from the file set, per §2 requirement 12
2. Compute file hashes for all remaining files in the directory
3. Compute pack hash per §3 (NFC normalization, lowercase hex, sorted paths)
4. Write signatures.yaml (with parent reference if this is not v1)
5. ZIP the directory contents (including signatures.yaml) → archive
6. Write the archive to the output path (MUST NOT overwrite the source directory)
```

### 6.2 Verify (archive → result)

```text
Input:  name.kpack   (ZIP file)
Output: { status: "sealed" | "export" | "invalid", errors: string[] }

Steps:
1. Validate all ZIP entries against §2 safety requirements (path traversal, symlinks, duplicates)
2. Validate archive structure (§2 requirements):
   - PACK.yaml and the files required by CORE §2 for the declared kind MUST be present
   - Entries MUST be pack-rooted (no wrapper subdirectory)
   - No two entry paths may collide after NFC normalization
   - If any structural check fails: return status "invalid"
3. Check for signatures.yaml in the archive:
   - If absent: return status "export" (valid pack structure, not sealed)
   - If present: continue to step 4
4. Verify signatures.yaml.algorithm is a supported algorithm (currently: SHA-256)
5. Compute file hashes for all other files in the archive (excluding OS metadata)
6. Compute pack hash per §3
7. Compare computed pack_hash to signatures.yaml.pack_hash
8. Compare per-file hashes against signatures.yaml.files
9. Optionally verify digital signature if present (using signing payload from §4.2)
10. Optionally verify parent chain if previous version is available
```

Note: Empty directories in ZIP entries are ignored — only regular files participate in hash computation, consistent with §3.

### 6.3 Extract (archive → pack)

```text
Input:  name.kpack   (ZIP file)
Output: name.kpack/  (directory, at -o path or cwd)

Steps:
1. Validate all ZIP entries against §2 safety requirements:
   - Reject entries with path traversal (../ segments)
   - Reject entries with absolute paths or backslash separators
   - Reject symlinks, device files, and duplicate entries
   - Strip OS metadata entries, per §2 requirement 12
2. Verify the archive (§6.2) — warn but do not block on failure
3. Extract ZIP contents to directory
4. signatures.yaml is preserved in the directory (it is part of the pack)
```

### 6.4 Transfer

When a pack archive moves between systems:

1. Sender computes or reads the pack hash.
2. Sender transmits the archive file and its pack hash (the hash MAY travel in an HTTP header, a sidecar file, or as part of an API response envelope).
3. Receiver verifies the archive against the declared hash.
4. On mismatch: reject the transfer. Do not silently accept corrupted packs.

---

## 7. CLI Commands

Note: `kpack archive` is reserved for lifecycle archival (see LIFECYCLE.md). The seal/transport commands use `kpack seal` to avoid ambiguity.

```bash
# Seal a pack directory → ZIP with signatures.yaml
kpack seal solar-energy-market.kpack/ -o ./archives/
# → creates ./archives/solar-energy-market.kpack (ZIP)

# Seal without -o (writes to cwd; fails if name collides with source directory)
kpack seal ../other-location/solar-energy-market.kpack/
# → creates ./solar-energy-market.kpack (ZIP) in the current directory

# Seal with parent reference (integrity chain)
kpack seal solar-energy-market.kpack/ -o ./archives/ --parent ./archives/solar-energy-market-v2.kpack
# → creates archive with parent hash from the v2 archive

# Verify an archive's integrity
kpack verify solar-energy-market.kpack
# → checks pack hash, file hashes, optional signature, ZIP safety

# Verify a chain of archives
kpack verify --chain v1.kpack v2.kpack v3.kpack
# → checks each archive and verifies parent references

# Extract an archive to a directory
kpack extract solar-energy-market.kpack -o ./packs/
# → creates ./packs/solar-energy-market.kpack/

# Show archive metadata without extracting
kpack info solar-energy-market.kpack
# → prints: version, pack_hash, sealed_at, sealed_by, parent, file count
```

---

## 8. Interaction with Other Pack Features

### Attachments

Binary attachments (images, PDFs, scanned documents) are included in the archive as-is. Their hashes are computed over raw bytes and included in `signatures.yaml.files`. Large attachments dominate archive size — implementations MAY use Store (no compression) for already-compressed formats (JPEG, PNG, PDF) and DEFLATE for text files.

### Composition

Composite packs (see COMPOSITION.md) reference other packs by name, not by embedding them. A composite pack's archive contains only the composite's own files — it does not bundle the referenced packs. Each referenced pack has its own archive and its own integrity chain.

### Lifecycle

Archive creation is a lifecycle event, not a lifecycle state. A pack's lifecycle type (permanent, seasonal, ephemeral) is orthogonal to whether it has been archived. All lifecycle types can be archived. Ephemeral packs SHOULD be archived before their retention window expires so the integrity chain is preserved even after the pack is no longer active.

### Visibility

Sealing respects the pack's `visibility` field, following the same rules as BUNDLE.md §5:

| Visibility | `kpack seal` behavior |
|------------|----------------------|
| `private` | Warning. Requires `--force` flag. |
| `shared` | Allowed. |
| `public` | Allowed. |

---

## 9. Design Decisions

### Why ZIP and not tar, tar.gz, or a custom format?

- ZIP is universally supported. Every operating system, programming language, and mobile platform can create and extract ZIP files without additional dependencies.
- ZIP supports random access — individual files can be read without extracting the entire archive. This matters for large packs with binary attachments.
- ZIP is the container format behind .docx, .xlsx, .epub, .jar, and .ipa. The pattern is well-established and well-understood.
- tar requires a separate compression step (gzip, zstd). ZIP handles both in one format.

### Why hash the contents, not the ZIP bytes?

Two independent ZIP implementations archiving the same files may produce different byte sequences (different metadata, different ordering, different compression parameters). Hashing ZIP bytes would make verification implementation-dependent. Hashing file contents makes verification deterministic regardless of the ZIP implementation.

### Why is `signatures.yaml` excluded from the hash?

`signatures.yaml` contains the hash. Including it in its own hash computation creates a circular dependency. Excluding it is the standard approach (cf. git's tree hashing excludes commit metadata; TLS certificates exclude the signature field).

### Why is signing optional?

The integrity chain (hash verification) is valuable without signing. Signing adds tamper evidence for metadata and, with asymmetric methods, non-repudiation (proving *who* sealed the pack). This matters in multi-party contexts but adds key management complexity. Making signing optional keeps the spec useful for simple single-user deployments while supporting enterprise requirements when needed.

### Why does the signature bind metadata, not just the pack hash?

`signatures.yaml` is excluded from the content hash to avoid circular dependency. But without binding, the metadata fields (`sealed_at`, `sealed_by`, the primary `parent` fields) could be rewritten without breaking verification — defeating the purpose of the integrity chain. The signing payload (§4.2) binds these fields so that any modification invalidates the signature. Exactly which fields are bound depends on the payload version: v2 additionally binds `pack_id`, which v1 left rewritable; `parent.merge_parents` is bound by neither. See the §4.2 scope note for what a v1 seal does and does not attest.

---

## 10. Security Considerations

### ZIP extraction attacks (ZipSlip)

ZIP archives can contain entries with path traversal sequences (`../`) that, when extracted naively, write files outside the intended directory. This is a well-documented class of vulnerability (CVE-2018-1002200 and variants). The safety requirements in §2 mandate rejection of such entries.

Implementations MUST validate every ZIP entry path **before** extraction. Validation MUST reject:

- Paths containing `..` segments (e.g., `../../etc/passwd`)
- Absolute paths (e.g., `/etc/passwd`, `C:\Windows\system32\...`)
- Paths using backslash separators (may be interpreted as directory separators on Windows)
- Symbolic link entries
- Duplicate entry paths (undefined behavior in most ZIP libraries)
- Device files and other non-regular entries

### OS metadata contamination

Operating systems create hidden metadata files — for example `.DS_Store` on macOS, `Thumbs.db` on Windows, and `__MACOSX/` resource-fork directories produced by macOS ZIP tools. **These examples are illustrative; the normative set is §2 requirement 12.** Such files:

- Are not part of the Knowledge Pack.
- Vary by platform — including them in the hash makes seals non-portable.
- May leak filesystem metadata (directory structure, timestamps, thumbnail images).

**AppleDouble sidecars (`._*`) are a special case worth stating plainly.** These files carry
resource-fork and extended-attribute data, and appear both inside `__MACOSX/` directories in ZIP
archives and as bare `._`-prefixed files on disk when an archive is extracted by a tool that
flattens that directory. The two shapes are the same mechanism.

They also present a portability problem the other entries do not: **on macOS, Foundation's
directory-enumeration APIs do not report bare `._`-prefixed files to a caller.** An implementation
built on those APIs therefore cannot observe such a file in order to hash it, while an
implementation reading the directory by other means can. Requiring these files to be hashed would
make the requirement unsatisfiable for one class of conformant implementation and produce seals that
verify on one toolchain and fail on another, with the file present on disk in both cases. Excluding
them by name removes the divergence rather than leaving it to be discovered.

Implementations MUST exclude the files named in §2 requirement 12 from hash computation and SHOULD strip them when creating archives.

### Line ending normalization

The content hash operates on raw bytes. If the same text file is checked out with `\n` on one system and `\r\n` on another (common with git's `core.autocrlf` on Windows), the hashes will differ. This is by design — the hash reflects the actual bytes — but it creates a practical portability problem.

Packs that use version control SHOULD include a `.gitattributes` file with `* text=auto eol=lf` to ensure consistent line endings across platforms. This is a recommendation for pack authors, not a requirement for implementations.

### Unicode normalization in filenames

macOS HFS+/APFS normalizes filenames to NFD (decomposed). Linux and Windows preserve the original form, typically NFC (composed). The content hash algorithm (§3) mandates NFC normalization of paths to ensure cross-platform determinism. Implementations that create archives on macOS MUST normalize paths to NFC before computing hashes.
