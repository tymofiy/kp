<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Archive Format — Knowledge Pack Companion Spec

> **Parent:** SPEC.md v0.7
> **Date:** 2026-04-12
> **Status:** Draft
> **Resolves:** AR-14 (signatures.yaml schema deferred to Phase C2)

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

### Archive contents

The ZIP file contains the pack directory's contents at the root level — not nested inside a subdirectory:

```text
marquet-le-passeur.kpack (ZIP)
├── PACK.yaml
├── claims.md
├── evidence.md
├── signatures.yaml        # REQUIRED in archives — integrity metadata
├── entities.md             # if present in pack
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
2. Files MUST be stored at the root of the archive, not inside a subdirectory.
3. `PACK.yaml` and `claims.md` MUST be present (per SPEC.md §2).
4. `signatures.yaml` MUST be present in any archive that participates in an integrity chain (§4). It MAY be absent in archives created for convenience (e.g., manual export).
5. Compression method SHOULD be DEFLATE. Store (no compression) is acceptable for small packs or when speed is preferred.
6. ZIP64 extensions SHOULD be used for archives exceeding 4 GB.
7. ZIP encryption MUST NOT be used. Access control is handled at the transport and storage layers, not the container layer. If confidentiality is required, encrypt the archive file itself (e.g., age, GPG) rather than using ZIP encryption.

---

## 3. Content Hash

The integrity of an archive is verified by its **content hash** — a deterministic hash computed from the pack's file contents. The hash is of the *knowledge*, not the *container*: re-zipping the same files produces the same content hash even if the ZIP metadata differs.

### Computation

1. Enumerate all files in the pack directory, excluding `signatures.yaml` itself.
2. For each file, compute SHA-256 over its raw bytes.
3. Sort the file list by path (UTF-8 byte order, `/` as separator, case-sensitive).
4. Concatenate entries as `{path}\0{hex-digest}\n` (null byte separating path from digest, newline separating entries).
5. Compute SHA-256 over the concatenation. This is the **pack hash**.

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

### Properties

- **Deterministic.** Same file contents always produce the same pack hash, regardless of filesystem ordering, ZIP implementation, or creation timestamp.
- **Content-addressed.** Changing any file's contents changes the pack hash. Adding or removing a file changes the pack hash.
- **Self-excluding.** `signatures.yaml` is excluded from the hash computation because it contains the hash. This avoids the circular dependency.

---

## 4. `signatures.yaml`

This section defines the schema for `signatures.yaml`, resolving SPEC.md §2's "Tooling only — Cryptographic hashes + signing key for integrity verification" and CORE.md AR-14.

### Schema

```yaml
# signatures.yaml — integrity metadata for a sealed Knowledge Pack

# Hash algorithm (currently only SHA-256; future-proofed for upgrades)
algorithm: SHA-256

# Pack hash — computed per §3
pack_hash: "a1b2c3d4e5f6..."

# Per-file hashes (for selective verification and debugging)
files:
  PACK.yaml: "d4e5f6..."
  claims.md: "a1b2c3..."
  evidence.md: "789abc..."
  views/overview.md: "def012..."

# Sealing metadata
sealed_at: "2026-04-12T14:30:00Z"    # ISO 8601 timestamp
sealed_by: "bernard-cloud"             # Identity of the sealing system

# Version chain (§5) — absent for v1 (first version)
parent:
  version: "2026.04.11"               # Parent pack version
  pack_hash: "fedcba987654..."         # Parent pack hash

# Optional digital signature (§4.2)
signature:
  method: "hmac-sha256"               # or "ed25519", "rsa-sha256"
  value: "..."                         # Signature over pack_hash
  key_id: "bernard-cloud-2026"        # Key identifier for verification
```

### Required fields

| Field | Required | When |
|-------|----------|------|
| `algorithm` | Always | |
| `pack_hash` | Always | |
| `files` | Always | |
| `sealed_at` | Always | |
| `sealed_by` | Always | |
| `parent` | When version > 1 | Absent for the first version of a pack |
| `signature` | When signing is configured | Optional; depends on deployment |

### 4.1 Sealing

**Sealing** is the act of computing the content hash and writing `signatures.yaml`. A sealed pack is one whose `signatures.yaml` is present and whose `pack_hash` matches the computed hash.

Sealing happens at every version transition in the pack lifecycle:

| Transition | Sealer | Example |
|------------|--------|---------|
| Capture → v1 | Bernard App (on-device) | User photographs a document |
| Analysis → v2 | Bernard Cloud | Cloud extracts claims and evidence |
| Research → v3 | Bernard Cloud | Research loop completes |
| Edit → v(n+1) | Bernard Cloud | User edits are merged |

### 4.2 Signing (optional)

Signing provides non-repudiation — proof that a specific system sealed the pack. It is OPTIONAL because:

- Single-user deployments (a collector using Bernard alone) gain little from signing.
- Multi-tenant deployments (auction houses, galleries) benefit from knowing *which system* sealed a version.
- Regulatory contexts (provenance disputes, legal discovery) may require it.

When signing is used:

1. Compute the pack hash per §3.
2. Sign the pack hash (not the ZIP file, not individual files) using the configured method.
3. Record the signature, method, and key identifier in `signatures.yaml`.

Supported methods are not prescribed by this spec. Implementations SHOULD support at minimum HMAC-SHA256 (symmetric, simple) and Ed25519 (asymmetric, compact). RSA-SHA256 MAY be supported for compatibility with existing PKI infrastructure.

---

## 5. Version Chain

Each sealed version of a pack references its parent, forming an integrity chain. The chain is the proof that a pack's history is unbroken.

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

Version chains may branch when multiple systems modify the same pack concurrently (e.g., two users editing simultaneously). Branch resolution is an implementation concern, not a spec concern. This spec defines the chain; conflict resolution policies belong to the systems that manage chains.

When a branch is resolved (merged), the resulting version SHOULD reference both parents:

```yaml
parent:
  version: "2026.04.12"
  pack_hash: "aaa..."
  merge_parents:
    - version: "2026.04.12-rev1"
      pack_hash: "bbb..."
```

---

## 6. Archive Operations

### 6.1 Create (pack → archive)

```text
Input:  name.kpack/  (directory)
Output: name.kpack   (ZIP file with signatures.yaml)

Steps:
1. Compute file hashes for all files in the directory
2. Compute pack hash per §3
3. Write signatures.yaml (with parent reference if this is not v1)
4. ZIP the directory contents (including signatures.yaml) → archive
```

### 6.2 Verify (archive → boolean)

```text
Input:  name.kpack   (ZIP file)
Output: { valid: boolean, errors: string[] }

Steps:
1. Extract signatures.yaml from the archive
2. Compute file hashes for all other files in the archive
3. Compute pack hash per §3
4. Compare computed pack_hash to signatures.yaml.pack_hash
5. Optionally verify digital signature if present
6. Optionally verify parent chain if previous version is available
```

### 6.3 Extract (archive → pack)

```text
Input:  name.kpack   (ZIP file)
Output: name.kpack/  (directory)

Steps:
1. Verify the archive (§6.2) — warn but do not block on failure
2. Extract ZIP contents to directory
3. signatures.yaml is preserved in the directory (it is part of the pack)
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
kpack seal solar-energy-market.kpack/
# → creates solar-energy-market.kpack (ZIP)

# Seal with parent reference (integrity chain)
kpack seal solar-energy-market.kpack/ --parent solar-energy-market-v2.kpack
# → creates archive with parent hash from the v2 archive

# Verify an archive's integrity
kpack verify solar-energy-market.kpack
# → checks pack hash, file hashes, optional signature

# Verify a chain of archives
kpack verify --chain v1.kpack v2.kpack v3.kpack
# → checks each archive and verifies parent references

# Extract an archive to a directory
kpack extract solar-energy-market.kpack -o ./packs/
# → creates ./packs/solar-energy-market.kpack/

# Show archive metadata without extracting
kpack seal --info solar-energy-market.kpack
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

Archive creation respects the pack's `visibility` field, following the same rules as BUNDLE.md §5:

| Visibility | `kpack archive` behavior |
|------------|--------------------------|
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

The integrity chain (hash verification) is valuable without signing. Signing adds non-repudiation (proving *who* sealed the pack), which matters in multi-party contexts but adds key management complexity. Making signing optional keeps the spec useful for simple single-user deployments while supporting enterprise requirements when needed.
