"""Ensure historical public charts cannot reintroduce private roster data."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import zipfile

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

    def test_archive_is_complete_and_matches_public_files(self):
        manifest = json.loads((SNAPSHOT / "manifest.json").read_text(encoding="utf-8"))
        expected = {"README.md", ".gitignore", "team-snapshot.json", "chart-catalog.json",
                    "manifest.json", "mermaid-config.json", "render-metadata.json",
                    "build_sources.py", "render_charts.py", "export_png.cjs", "validate.py"}
        expected.update(chart["name"] + suffix for chart in manifest["charts"]
                        for suffix in (".mmd", ".svg", ".png"))
        with zipfile.ZipFile(SNAPSHOT / "organization-charts.zip") as archive:
            self.assertEqual(set(archive.namelist()), expected)
            self.assertEqual(len(archive.namelist()), len(expected))
            for name in expected:
                with self.subTest(file=name):
                    self.assertEqual(archive.read(name), (SNAPSHOT / name).read_bytes())
            validator.validate_snapshot(json.loads(archive.read("team-snapshot.json")))

if __name__ == "__main__":
    unittest.main()
