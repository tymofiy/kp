# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""The site's copies of the assistant instructions match the repository's."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class AssistantPageCopies(unittest.TestCase):
    def test_site_copy_of_page_matches(self):
        self.assertEqual((ROOT / "agent/CREATE-A-PACK.md").read_text(encoding="utf-8"),
                         (ROOT / "docs/create-a-pack.txt").read_text(encoding="utf-8"))

    def test_site_copy_of_llms_matches(self):
        self.assertEqual((ROOT / "llms.txt").read_text(encoding="utf-8"),
                         (ROOT / "docs/llms.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
