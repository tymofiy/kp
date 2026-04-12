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

**Filesystem coexistence.** A file and a directory cannot share the same path. When sealing a pack, the archive MUST be written to a different location than the source directory — either a specified output path (`-o`) or the current working directory. The naming convention describes how the artifact is *identified*, not that both forms coexist at the same path. See §7 for CLI examples.

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
12. **OS metadata exclusion.** Entries matching `.DS_Store`, `Thumbs.db`, `__MACOSX/*`, and `desktop.ini` SHOULD be stripped on archive creation and MUST be ignored during hash computation.

### Conformance levels

| Level | `signatures.yaml` | Integrity chain | Use case |
|-------|-------------------|-----------------|----------|
| **Sealed archive** | REQUIRED | Participates | Client-server transfer, versioned storage, regulated contexts |
| **Export archive** | ABSENT | Does not participate | Manual sharing, convenience export, one-off backup |

An export archive is a valid ZIP containing a valid pack. It is not sealed and does not participate in the integrity chain. Tools that expect sealed archives MUST reject export archives with a clear error rather than silently skipping verification.

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
- **OS metadata files.** Files such as `.DS_Store` (macOS), `Thumbs.db` (Windows), and `__MACOSX/` entries are not part of the Knowledge Pack. Implementations MUST exclude them from hash computation and SHOULD exclude them from archives. See §10 (Security Considerations).

### Properties

- **Deterministic.** Same file contents and file paths always produce the same pack hash, regardless of filesystem ordering, ZIP implementation, creation timestamp, or operating system.
- **Content-addressed.** Changing any file's contents changes the pack hash. Adding or removing a file changes the pack hash.
- **Self-excluding.** Root-level `signatures.yaml` is excluded from the hash computation because it contains the hash. This avoids the circular dependency.

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
| `pack_hash` | string | Lowercase hex-encoded SHA-256 digest (64 characters). |
| `files` | map\<string, string\> | Keys: NFC-normalized relative paths with `/` separator. Values: lowercase hex SHA-256 digests. MUST NOT include `signatures.yaml`. |
| `sealed_at` | string | ISO 8601 UTC timestamp (e.g., `2026-04-12T14:30:00Z`). |
| `sealed_by` | string | Identifier of the sealing system (e.g., `capture-client`, `analysis-service`). |
| `parent.version` | string | Parent pack's version string from its PACK.yaml. |
| `parent.pack_hash` | string | Parent pack's `pack_hash` (lowercase hex). |
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
| `parent` | When version > 1 | Absent for the first version of a pack |
| `signature` | When signing is configured | Optional; depends on deployment |

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

Signing provides **tamper evidence** for the sealing metadata — proof that `pack_hash`, `sealed_at`, `sealed_by`, and `parent` have not been modified since sealing. It is OPTIONAL because:

- Single-user deployments gain little from signing.
- Multi-tenant deployments (auction houses, galleries) benefit from knowing *which system* sealed a version.
- Regulatory contexts (provenance disputes, legal discovery) may require it.

**Signing payload.** The signature is computed over a canonical byte string that binds the metadata, not just the pack hash. This prevents an attacker from rewriting sealing metadata while preserving a valid signature.

The signing payload is the UTF-8 encoding of the following concatenation:

```text
{algorithm}\n{pack_hash}\n{sealed_at}\n{sealed_by}\n{parent.pack_hash or empty}\n
```

Where `parent.pack_hash` is the parent's pack hash if present, or the empty string for a v1 pack. All fields use their exact string values from `signatures.yaml`.

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

Version chains may branch when multiple systems modify the same pack concurrently (e.g., two users editing simultaneously). Branch resolution is an implementation concern, not a spec concern. This spec defines the linear chain; conflict resolution policies and merge-parent semantics are deferred to a future version of this spec.

---

## 6. Archive Operations

### 6.1 Create (pack → archive)

```text
Input:  name.kpack/  (directory)
Output: name.kpack   (ZIP file with signatures.yaml, written to -o path or cwd)

Steps:
1. Exclude OS metadata files (.DS_Store, Thumbs.db, __MACOSX/) from the file set
2. Compute file hashes for all remaining files in the directory
3. Compute pack hash per §3 (NFC normalization, lowercase hex, sorted paths)
4. Write signatures.yaml (with parent reference if this is not v1)
5. ZIP the directory contents (including signatures.yaml) → archive
6. Write the archive to the output path (MUST NOT overwrite the source directory)
```

### 6.2 Verify (archive → boolean)

```text
Input:  name.kpack   (ZIP file)
Output: { valid: boolean, errors: string[] }

Steps:
1. Validate all ZIP entries against §2 safety requirements (path traversal, symlinks, duplicates)
2. Extract signatures.yaml from the archive
3. Compute file hashes for all other files in the archive (excluding OS metadata)
4. Compute pack hash per §3
5. Compare computed pack_hash to signatures.yaml.pack_hash
6. Compare per-file hashes against signatures.yaml.files
7. Optionally verify digital signature if present (using signing payload from §4.2)
8. Optionally verify parent chain if previous version is available
```

### 6.3 Extract (archive → pack)

```text
Input:  name.kpack   (ZIP file)
Output: name.kpack/  (directory, at -o path or cwd)

Steps:
1. Validate all ZIP entries against §2 safety requirements:
   - Reject entries with path traversal (../ segments)
   - Reject entries with absolute paths or backslash separators
   - Reject symlinks, device files, and duplicate entries
   - Strip OS metadata entries (.DS_Store, Thumbs.db, __MACOSX/)
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

# Seal to current working directory (default when -o is omitted and no collision)
kpack seal solar-energy-market.kpack/
# → creates ./solar-energy-market.kpack (ZIP) — fails if file already exists

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

`signatures.yaml` is excluded from the content hash to avoid circular dependency. But without binding, the metadata fields (`sealed_at`, `sealed_by`, `parent`) could be rewritten without breaking verification — defeating the purpose of the integrity chain. The signing payload (§4.2) binds these fields so that any modification invalidates the signature.

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

Operating systems create hidden metadata files (`.DS_Store` on macOS, `Thumbs.db` on Windows, `__MACOSX/` resource fork directories in macOS ZIP tools). These files:

- Are not part of the Knowledge Pack.
- Vary by platform — including them in the hash makes seals non-portable.
- May leak filesystem metadata (directory structure, timestamps, thumbnail images).

Implementations MUST exclude these files from hash computation and SHOULD strip them when creating archives.

### Line ending normalization

The content hash operates on raw bytes. If the same text file is checked out with `\n` on one system and `\r\n` on another (common with git's `core.autocrlf` on Windows), the hashes will differ. This is by design — the hash reflects the actual bytes — but it creates a practical portability problem.

Packs that use version control SHOULD include a `.gitattributes` file with `* text=auto eol=lf` to ensure consistent line endings across platforms. This is a recommendation for pack authors, not a requirement for implementations.

### Unicode normalization in filenames

macOS HFS+/APFS normalizes filenames to NFD (decomposed). Linux and Windows preserve the original form, typically NFC (composed). The content hash algorithm (§3) mandates NFC normalization of paths to ensure cross-platform determinism. Implementations that create archives on macOS MUST normalize paths to NFC before computing hashes.
