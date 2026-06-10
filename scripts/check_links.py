# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Relative-link checker, anchor-aware.

Walks every tracked .md file (fixtures excluded) and verifies:
  1. relative link targets exist on disk (as before), and
  2. #fragments resolve to a real anchor in the target document —
     a GitHub heading slug or an explicit <a name=...>/<a id=...>.

Same-file links (#fragment) are checked against the containing file.
Fragments on non-markdown targets and directories are not checkable
and are skipped. External (http/https/mailto) links are out of scope.

The slug algorithm mirrors GitHub's (github-slugger): markdown
formatting is stripped from the heading text, the text is lowercased,
characters that are not word characters, hyphens, or spaces are
removed, spaces become hyphens, and repeated headings get -1, -2, ...
suffixes. Headings inside fenced code blocks do not anchor.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Optional CommonMark link titles — [text](target "title") — are consumed
# so titled links are checked rather than silently skipped.
MD_LINK_RE = re.compile(r"""\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)""")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
HTML_ANCHOR_RE = re.compile(r"""<a\s+(?:name|id)=["']([^"']+)["']""")
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
# Backticks and asterisks vanish in rendered heading text; underscores do
# NOT — github-slugger preserves them (Foo_Bar → foo_bar), so they stay.
MARKER_RE = re.compile(r"[`*]")
NON_SLUG_RE = re.compile(r"[^\w\- ]")


def slugify(heading_text: str) -> str:
    """GitHub anchor slug for a single heading occurrence (no -N suffix)."""
    text = INLINE_LINK_RE.sub(r"\1", heading_text)  # [text](url) -> text
    text = MARKER_RE.sub("", text)  # emphasis/code markers vanish in rendering
    text = text.strip().lower()
    text = NON_SLUG_RE.sub("", text)
    return text.replace(" ", "-")


def collect_anchors(path: Path) -> set[str]:
    """All anchor ids a #fragment can point at in this markdown file."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    fence_char: str | None = None  # the opener's char — ``` only closes ```, ~~~ only ~~~
    for line in path.read_text().splitlines():
        fm = FENCE_RE.match(line)
        if fm:
            mark = fm.group(1)[0]
            if fence_char is None:
                fence_char = mark
            elif fence_char == mark:
                fence_char = None
            continue
        if fence_char:
            continue
        m = HEADING_RE.match(line)
        if m:
            slug = slugify(m.group(1))
            n = counts.get(slug, 0)
            counts[slug] = n + 1
            anchors.add(slug if n == 0 else f"{slug}-{n}")
        for am in HTML_ANCHOR_RE.finditer(line):
            anchors.add(am.group(1))
    return anchors


_anchor_cache: dict[Path, set[str]] = {}


def anchors_for(path: Path) -> set[str]:
    rp = path.resolve()
    if rp not in _anchor_cache:
        _anchor_cache[rp] = collect_anchors(rp)
    return _anchor_cache[rp]


def main() -> int:
    broken = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "node_modules")]
        for file in files:
            if not file.endswith(".md") or "fixtures" in root:
                continue
            path = Path(root) / file
            content = path.read_text()
            for match in MD_LINK_RE.findall(content):
                if match.startswith(("http://", "https://", "mailto:")):
                    continue
                target, _, frag = match.partition("#")
                # Resolve the target document: same file for bare #fragment.
                # Targets are taken literally (no percent-decoding): GitHub
                # treats %2F etc. as filename characters, so decoding here
                # would mask links that 404 on the rendered site. Absolute
                # paths can never resolve as repo files on GitHub.
                if target.startswith("/"):
                    print(f"BROKEN LINK in {path}: {match} (absolute path)")
                    broken += 1
                    continue
                if target:
                    target_path = path.parent / target
                    if not target_path.exists():
                        print(f"BROKEN LINK in {path}: {match}")
                        broken += 1
                        continue
                else:
                    target_path = path
                # Verify the fragment where one exists and is checkable
                if "#" in match and target_path.is_file() and target_path.suffix == ".md":
                    fragment = unquote(frag)
                    if fragment not in anchors_for(target_path):
                        print(
                            f"BROKEN ANCHOR in {path}: {match} "
                            f"(no anchor '{fragment}' in {target_path})"
                        )
                        broken += 1
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
