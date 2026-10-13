# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""ARCHIVE §3 content hashing of an already enumerated regular-file map.

This helper does not extract ZIPs or verify signatures/ancestry. Its rules
are those of this checkout; historical-policy selection belongs to callers.
"""
import hashlib
import unicodedata


def excluded_path(path: str) -> bool:
    return path == 'signatures.yaml' or any(
        part in {'.DS_Store', 'Thumbs.db', 'desktop.ini', '__MACOSX'} or part.startswith('._')
        for part in path.split('/')
    )


def content_hash(files: dict[str, bytes]) -> tuple[str, dict[str, str]]:
    """Input paths are bare slash-separated relative paths; values are bytes."""
    digests = {}
    for path, data in files.items():
        if excluded_path(path):
            continue
        normalized = unicodedata.normalize('NFC', path)
        if normalized in digests:
            raise ValueError(f'duplicate normalized path {normalized!r}')
        digests[normalized] = hashlib.sha256(data).hexdigest()
    paths = sorted(digests, key=lambda path: path.encode('utf-8'))
    payload = b''.join(path.encode('utf-8') + b'\0' + digests[path].encode('ascii') + b'\n'
                       for path in paths)
    return hashlib.sha256(payload).hexdigest(), {path: digests[path] for path in paths}
