"""Checks for valid organization security-policy navigation; no network access."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SecurityPolicyLinksTests(unittest.TestCase):
    def test_readme_security_link_targets_existing_local_file(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        match = re.search(
            r"\[Security\]\(https://github\.com/Pick-Your-AI/\.github/blob/main/([^)]*)\)",
            readme,
        )
        self.assertIsNotNone(match, "Expected organization security navigation link")
        self.assertEqual(match.group(1), "SECURITY.md")
        self.assertTrue((ROOT / match.group(1)).is_file())

    def test_security_policy_local_links_resolve(self):
        policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("**Do not post vulnerabilities", policy)
        self.assertIn("only if that private feature is available", policy)
        for link in ("SUPPORT.md", "CODE_OF_CONDUCT.md"):
            self.assertIn(f"]({link})", policy)
            self.assertTrue((ROOT / link).is_file())


if __name__ == "__main__":
    unittest.main()
