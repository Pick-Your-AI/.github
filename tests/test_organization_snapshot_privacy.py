"""Ensure historical public charts cannot reintroduce private roster data."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "docs/organization/snapshots/2026-10-29"
spec = importlib.util.spec_from_file_location("snapshot_validator", SNAPSHOT / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class PublicSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((SNAPSHOT / "team-snapshot.json").read_text(encoding="utf-8"))

    def test_public_hierarchy_is_accepted(self):
        validator.validate_snapshot(self.snapshot)

    def test_rejects_top_level_private_data(self):
        for key in ("owners", "members", "pending_invitations", "member_count"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.snapshot)
                candidate[key] = []
                with self.assertRaises(ValueError):
                    validator.validate_snapshot(candidate)

    def test_rejects_team_rosters_and_invitation_data(self):
        for key in ("members", "pending", "login", "invitation_id", "member_count"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.snapshot)
                candidate["teams"][0][key] = []
                with self.assertRaises(ValueError):
                    validator.validate_snapshot(candidate)

    def test_rejects_nested_data_in_public_fields(self):
        candidate = copy.deepcopy(self.snapshot)
        candidate["teams"][0]["parent"] = {"login": "synthetic-private-user"}
        with self.assertRaises(ValueError):
            validator.validate_snapshot(candidate)

    def test_generated_public_sources_are_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("build_sources.py", "validate.py", "team-snapshot.json"):
                shutil.copyfile(SNAPSHOT / name, target / name)
            subprocess.run([sys.executable, "-X", "utf8", str(target / "build_sources.py")],
                           check=True, capture_output=True)
            expected = {"manifest.json", "chart-catalog.json", "mermaid-config.json"}
            expected.update(path.name for path in SNAPSHOT.glob("*.mmd"))
            for name in expected:
                with self.subTest(file=name):
                    self.assertEqual((target / name).read_bytes(), (SNAPSHOT / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
