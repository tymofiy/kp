#!/usr/bin/env python3
"""Guard the published spec page against stray external domains.

`docs/index.html` is published to GitHub Pages. A client / engagement / vendor
/ product domain reaching that page is a confidentiality leak — exactly the
class of leak that put `hellobernard.ai` live before anyone caught it.

This is the *committed, no-secret* leak defense: it fails if the published page
links to any external host not in ``ALLOWED_HOSTS``. It deliberately does NOT
try to catch arbitrary client *names* (a surname or codename matches no
structural shape, and the spec's own vocabulary — "collection", "provenance",
"gallery" — would false-positive on any art-market word list). Catching the
*shape* that actually leaks — a stray external domain — is the part that can
live safely in a public repo with zero dependence on a gitignored list.

Allowlist discipline: add a host here ONLY if it belongs on a public,
vendor-neutral standards page. A new host appearing in the page that you did
not deliberately allowlist is the signal this guard exists to raise.

    python3 scripts/check_external_domains.py             # check the real page
    python3 scripts/check_external_domains.py --self-test # regression check
"""

from __future__ import annotations

import pathlib
import re
import sys

# Hosts the published page is allowed to link to. Matched case-insensitively,
# exact host or any subdomain (so `www.w3.org` matches `w3.org`).
#
# `hellobernard.ai` is the author's product domain, allowlisted here to reflect
# the page's *current* state — not an endorsement of keeping the bio link. If
# that link is ever dropped to keep the spec brand-neutral, remove the host
# here too so the guard re-tightens.
ALLOWED_HOSTS = frozenset(
    {
        "w3.org",
        "creativecommons.org",
        "doi.org",
        "github.com",
        "orcid.org",
        "tymofiy.github.io",
        "hellobernard.ai",
    }
)

PAGE = pathlib.Path(__file__).resolve().parent.parent / "docs" / "index.html"
_HOST_RE = re.compile(r"https?://([A-Za-z0-9._-]+)")


def _allowed(host: str) -> bool:
    h = host.lower().rstrip(".")
    return any(h == a or h.endswith("." + a) for a in ALLOWED_HOSTS)


def violations(text: str) -> list[str]:
    """External hosts in *text* that are not on the allowlist (sorted, unique)."""
    return sorted({h.lower() for h in _HOST_RE.findall(text) if not _allowed(h.lower())})


def _self_test() -> int:
    # A stray external domain must be flagged...
    bad = violations('<a href="https://acme-auctioneers.example/x">x</a>')
    assert bad == ["acme-auctioneers.example"], f"self-test: expected catch, got {bad}"
    # ...while every allowlisted host (incl. a www. subdomain) must pass.
    ok = violations(
        "https://www.w3.org https://doi.org/10.x https://github.com/o/r "
        "https://orcid.org/0000 https://tymofiy.github.io https://hellobernard.ai "
        "https://creativecommons.org/licenses"
    )
    assert ok == [], f"self-test: allowlist over-flagged {ok}"
    print("check_external_domains: self-test OK")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return _self_test()
    if not PAGE.exists():
        print(f"::error::{PAGE} not found")
        return 1
    bad = violations(PAGE.read_text(encoding="utf-8"))
    if bad:
        # The offending host is already in the committed page, so naming it in
        # the log leaks nothing new — it helps the author fix it fast.
        print(
            "::error::Published page links to non-allowlisted external "
            f"domain(s): {', '.join(bad)}. If the link is intentional and "
            "public-safe, add the host to ALLOWED_HOSTS in "
            "scripts/check_external_domains.py; otherwise remove it — it may be "
            "a client / vendor / engagement leak."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
