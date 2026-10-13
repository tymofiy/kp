# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Reference evidence segmentation and CORE §10 body encoding.

Logical bodies are text projections. Keep the source file for byte custody.
"""

from dataclasses import dataclass, field
import re


ENCODING = "markdown-backslash-v1"
MARKER = f"> **kp-content-encoding:** {ENCODING}"
HEADING = re.compile(r"^## (E[0-9]+)(?:(?: ?— ?| ?-- ?)([^\r\n]+))?[ \t]*$")
H2 = re.compile(r"^##(?:[ \t]|$)")
QUOTE_FIELD = re.compile(r"^\*\*([^:*]+):\*\*\s*(.*)$")
LIST_FIELD = re.compile(r"^- ([A-Za-z][A-Za-z0-9-]*):\s*(.*)$")
# CORE §10 / EvidenceFieldName in the normative PEG, normalized per AR-07.
EVIDENCE_FIELDS = frozenset({
    "type", "source", "captured", "prepared", "sha-256", "notes",
    "reliability", "credibility", "kp-content-encoding",
})


def needs_escape(line: str) -> bool:
    """Accept a logical line after its spaces/tabs, without its line ending."""
    return (
        line.startswith("\\")
        or line == MARKER
        or re.match(r"^##(?:\s|$)", line) is not None
        or re.match(r"^-\s+\[E[0-9]+\](?:\s|$)", line) is not None
    )


def transform_body(text: str, *, decode: bool = False) -> str:
    result = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        ending = line[len(content):]
        indent = re.match(r"[ \t]*", content).group()
        rest = content[len(indent):]
        if decode:
            if rest.startswith("\\") and needs_escape(rest[1:]):
                rest = rest[1:]
        elif needs_escape(rest):
            rest = "\\" + rest
        result.append(indent + rest + ending)
    return "".join(result)


@dataclass
class EvidenceRecord:
    id: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)
    encoded_body: str = ""
    logical_body: str = ""
    warnings: list[str] = field(default_factory=list)


def parse_evidence(text: str) -> list[EvidenceRecord]:
    """Segment before decoding; only the initial metadata block is metadata.

    One blank separator after metadata is structural. Additional blank lines
    belong to the body. Unknown encoding values preserve the encoded body.
    """
    records = []
    current = None
    body = []
    metadata = False

    def finish():
        if current is None:
            return
        current.encoded_body = "".join(body)
        encoding = current.fields.get("kp-content-encoding")
        if encoding == ENCODING:
            current.logical_body = transform_body(current.encoded_body, decode=True)
        else:
            current.logical_body = current.encoded_body
            if encoding is not None:
                current.warnings.append(f"unknown content encoding {encoding!r}; body preserved")
        records.append(current)

    for number, raw in enumerate(text.splitlines(keepends=True), 1):
        line = raw.rstrip("\r\n")
        if H2.match(line):
            finish()
            heading = HEADING.fullmatch(line)
            current = (EvidenceRecord(heading[1], (heading[2] or heading[1]).strip(), number)
                       if heading else None)
            body = []
            metadata = current is not None
            continue
        if current is None:
            continue
        if metadata and line == "" and not current.fields:
            # Blank lines between a record heading and its fields are common
            # in both permitted Markdown layouts.
            continue
        fields = []
        if metadata:
            if line.startswith(">"):
                quoted = line[1:].removeprefix(" ")
                matches = [QUOTE_FIELD.fullmatch(part.strip()) for part in quoted.split("|")]
                if matches and all(matches):
                    fields = [(m[1], m[2]) for m in matches]
            else:
                match = LIST_FIELD.fullmatch(line)
                if match:
                    fields = [(match[1], match[2])]
        if fields:
            for key, value in fields:
                key = key.lower()
                if key in current.fields:
                    current.duplicates.append(key)
                current.fields[key] = value.strip()
            continue
        if metadata:
            metadata = False
            if line == "" and current.fields:
                continue
        body.append(raw)
    finish()
    return records
