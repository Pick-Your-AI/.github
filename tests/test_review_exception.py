"""Offline synthetic diff evidence only; no GitHub settings or behavior tests."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "governance" / "review_exception.py"
SPEC = importlib.util.spec_from_file_location("review_exception_under_test", SCRIPT)
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)
OPERATIONS = json.loads((ROOT / "proposals" / "research-review-exception.json").read_text())["operations"]


def fixture(operation=None):
    operation = operation or OPERATIONS[0]
    repository = "Pick-Your-AI/" + operation["repository"]
    before = {
        "id": operation["ruleset_id"], "name": operation["ruleset_name"],
        "source_type": "Repository", "source": repository,
        "target": "branch", "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "bypass_actors": [{"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
        "rules": [
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 1, "require_last_push_approval": True,
                "dismiss_stale_reviews_on_push": True, "required_review_thread_resolution": True,
                "require_code_owner_review": False}},
            {"type": "required_status_checks", "parameters": {
                "required_status_checks": [{"context": "synthetic-required", "integration_id": None}],
                "strict_required_status_checks_policy": True}},
            {"type": "non_fast_forward"}, {"type": "deletion"},
            {"type": "required_linear_history"}],
        "future_metadata": {"enabled": True, "version": 1, "items": [None, 1.0]},
    }
    candidate = copy.deepcopy(before)
    candidate["rules"][0]["parameters"].update(operation["proposed_after"])
    return repository, before, candidate


class ReviewDiffTests(unittest.TestCase):
    def reject_change(self, change, baseline=False):
        repository, before, candidate = fixture()
        change(before if baseline else candidate)
        result = verifier.verify(repository, before, candidate)
        self.assertFalse(result["matches_proposal"])
        self.assertEqual(result["evidence"], "offline_diff_only")
        return result

    def test_all_six_exact_pairs_accept_and_inputs_remain_immutable(self):
        self.assertEqual(len(OPERATIONS), 6)
        for operation in OPERATIONS:
            with self.subTest(repository=operation["repository"]):
                repository, before, candidate = fixture(operation)
                saved = copy.deepcopy((before, candidate))
                self.assertEqual(verifier.verify(repository, before, candidate), {
                    "matches_proposal": True, "evidence": "offline_diff_only", "reason": "matches_proposal"})
                self.assertEqual((before, candidate), saved)

    def test_excluded_repository_and_wrong_identities(self):
        repository, before, candidate = fixture()
        for excluded in ("Pick-Your-AI/pick-your-ai-website", "Pick-Your-AI/.github",
                         "Other/" + OPERATIONS[0]["repository"], OPERATIONS[0]["repository"]):
            with self.subTest(excluded=excluded):
                self.assertFalse(verifier.verify(excluded, before, candidate)["matches_proposal"])
        for field, value in (("id", OPERATIONS[1]["ruleset_id"]), ("name", "Protect main"),
                             ("source", "PrivateOrg/secret"), ("source_type", "Organization")):
            for baseline in (True, False):
                with self.subTest(field=field, baseline=baseline):
                    self.reject_change(lambda doc: doc.update({field: value}), baseline)

    def test_optional_source_fields_and_object_key_order(self):
        repository, before, candidate = fixture()
        for document in (before, candidate):
            del document["source"]
            del document["source_type"]
        candidate = dict(reversed(list(candidate.items())))
        self.assertTrue(verifier.verify(repository, before, candidate)["matches_proposal"])

    def test_enforcement_state_is_preserved_without_claiming_activation(self):
        repository, before, candidate = fixture()
        for state in ("evaluate", "disabled"):
            with self.subTest(state=state):
                before["enforcement"] = candidate["enforcement"] = state
                self.assertTrue(verifier.verify(repository, before, candidate)["matches_proposal"])

    def test_missing_duplicate_and_malformed_rules(self):
        changes = [lambda d: d["rules"].pop(0),
                   lambda d: d["rules"].append(copy.deepcopy(d["rules"][0])),
                   lambda d: d["rules"].append(copy.deepcopy(d["rules"][1])),
                   lambda d: d.update(rules={}), lambda d: d["rules"].append(None),
                   lambda d: d["rules"][0].update(parameters=[]),
                   lambda d: d["rules"][0]["parameters"].pop("require_last_push_approval")]
        for change in changes:
            for baseline in (True, False):
                with self.subTest(change=changes.index(change), baseline=baseline):
                    self.reject_change(change, baseline)

    def test_baseline_must_match_both_expected_values(self):
        for field, value in (("required_approving_review_count", 0),
                             ("require_last_push_approval", False)):
            self.reject_change(lambda d: d["rules"][0]["parameters"].update({field: value}), True)

    def test_validation_history_actors_conditions_and_unknown_fields_preserved(self):
        changes = [lambda d: d["rules"].pop(1),
                   lambda d: d["bypass_actors"][0].update(actor_id=2),
                   lambda d: d["conditions"]["ref_name"]["include"].append("refs/heads/*"),
                   lambda d: d["rules"][0]["parameters"].update(required_review_thread_resolution=False),
                   lambda d: d["rules"].pop(), lambda d: d["rules"].pop(2),
                   lambda d: d["rules"].pop(3),
                   lambda d: d["future_metadata"].update(enabled=False),
                   lambda d: d["rules"][0].update(future="added"),
                   lambda d: d.update(enforcement="disabled"),
                   lambda d: d.update(target="tag"), lambda d: d.pop("future_metadata")]
        for index, change in enumerate(changes):
            with self.subTest(change=index):
                self.reject_change(change)

    def test_unchanged_unknown_rule_and_fields_are_accepted(self):
        repository, before, candidate = fixture()
        for document in (before, candidate):
            document["rules"].append({"type": "future_protection", "parameters": {"private": [1, True]}})
        self.assertTrue(verifier.verify(repository, before, candidate)["matches_proposal"])

    def test_exact_scalar_types_everywhere(self):
        for baseline, field, values in (
                (True, "required_approving_review_count", [True, 1.0, "1", None]),
                (True, "require_last_push_approval", [1, 1.0, "true", None]),
                (False, "required_approving_review_count", [False, 0.0, "0", None]),
                (False, "require_last_push_approval", [0, 0.0, "false", None])):
            for value in values:
                with self.subTest(baseline=baseline, field=field, value=value):
                    self.reject_change(lambda d: d["rules"][0]["parameters"].update({field: value}), baseline)
        for field, value in (("id", float(OPERATIONS[0]["ruleset_id"])),
                             ("bypass_actors", {}), ("conditions", [])):
            self.reject_change(lambda d: d.update({field: value}))
        self.reject_change(lambda d: d["future_metadata"].update(enabled=1))
        self.reject_change(lambda d: d["future_metadata"].update(version=True))
        self.reject_change(lambda d: d["future_metadata"]["items"].__setitem__(1, 1))

    def test_rejected_inputs_are_immutable_and_verdict_is_public_safe(self):
        repository, before, candidate = fixture()
        candidate["bypass_actors"].append({"secret": "DO-NOT-PRINT-private-actor"})
        saved = copy.deepcopy((before, candidate))
        result = verifier.verify(repository, before, candidate)
        self.assertEqual((before, candidate), saved)
        self.assertEqual(result, {"matches_proposal": False, "evidence": "offline_diff_only",
                                  "reason": "unrelated_change"})
        self.assertNotIn("DO-NOT-PRINT", json.dumps(result))


class CommandTests(unittest.TestCase):
    def run_cli(self, before, candidate, repository=None, raw=False, extra=()):
        with tempfile.TemporaryDirectory(prefix="private-fixture-") as directory:
            before_path = Path(directory) / "secret-baseline.json"
            candidate_path = Path(directory) / "secret-candidate.json"
            before_path.write_text(before if raw else json.dumps(before), encoding="utf-8")
            candidate_path.write_text(candidate if raw else json.dumps(candidate), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), "--repository",
                                   repository or fixture()[0], "--before", str(before_path),
                                   "--candidate", str(candidate_path), *extra],
                                  capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})

    def assert_rejection(self, result):
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        data = json.loads(result.stdout)
        self.assertEqual(set(data), {"matches_proposal", "evidence", "reason"})
        self.assertFalse(data["matches_proposal"])
        self.assertEqual(data["evidence"], "offline_diff_only")
        self.assertNotIn("secret", result.stdout)
        self.assertNotIn("private-fixture", result.stdout)
        self.assertNotIn("DO-NOT-PRINT", result.stdout)

    def test_cli_success(self):
        repository, before, candidate = fixture()
        result = self.run_cli(before, candidate, repository)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["matches_proposal"])
        self.assertEqual(result.stderr, "")

    def decimal_pair(self, before_number, candidate_number):
        repository, before, candidate = fixture()
        marker = '"items": [null, 1.0]'
        raw_before, raw_candidate = json.dumps(before), json.dumps(candidate)
        self.assertEqual(raw_before.count(marker), 1)
        self.assertEqual(raw_candidate.count(marker), 1)
        return (raw_before.replace(marker, '"items": [null, ' + before_number + ']'),
                raw_candidate.replace(marker, '"items": [null, ' + candidate_number + ']'),
                repository)

    def test_raw_changed_decimals_cannot_collapse_to_a_match(self):
        for before_number, candidate_number in (
                ("1.0", "1.0000000000000001"), ("1e-999", "0.0"),
                ("1e-400", "0.0"), ("9007199254740992.0", "9007199254740993.0"),
                ("0.123456789012345678901234567890", "0.123456789012345678901234567891")):
            with self.subTest(before=before_number, candidate=candidate_number):
                result = self.run_cli(*self.decimal_pair(before_number, candidate_number), raw=True)
                self.assert_rejection(result)
                self.assertEqual(json.loads(result.stdout)["reason"], "unrelated_change")

    def test_raw_unchanged_precise_decimals_accept(self):
        for number in ("1.0000000000000001", "1e-999", "1e-400", "9007199254740993.0",
                       "0.123456789012345678901234567890"):
            with self.subTest(number=number):
                result = self.run_cli(*self.decimal_pair(number, number), raw=True)
                self.assertEqual(result.returncode, 0)
                self.assertTrue(json.loads(result.stdout)["matches_proposal"])
                self.assertEqual(result.stderr, "")

    def test_raw_fractional_integer_boolean_distinctions_remain_strict(self):
        for before_number, candidate_number in (("1.0", "1"), ("1.0", "true"),
                                                ("0.0", "0"), ("0.0", "false")):
            with self.subTest(before=before_number, candidate=candidate_number):
                self.assert_rejection(self.run_cli(
                    *self.decimal_pair(before_number, candidate_number), raw=True))
        _, before, candidate = fixture()
        for document, field, replacement in (
                ("before", "required_approving_review_count", "1.0"),
                ("candidate", "required_approving_review_count", "0.0"),
                ("before", "require_last_push_approval", "1.0"),
                ("candidate", "require_last_push_approval", "0.0")):
            raw_before, raw_candidate = json.dumps(before), json.dumps(candidate)
            source = before if document == "before" else candidate
            value = source["rules"][0]["parameters"][field]
            old = json.dumps(field) + ": " + json.dumps(value)
            new = json.dumps(field) + ": " + replacement
            if document == "before":
                raw_before = raw_before.replace(old, new)
            else:
                raw_candidate = raw_candidate.replace(old, new)
            with self.subTest(document=document, field=field):
                self.assert_rejection(self.run_cli(raw_before, raw_candidate, raw=True))

    def test_raw_unchanged_overflow_remains_invalid(self):
        result = self.run_cli(*self.decimal_pair("1e999", "1e999"), raw=True)
        self.assert_rejection(result)

    def test_invalid_json_duplicate_keys_nonfinite_and_wrong_top_level(self):
        for raw in ('{"secret": "DO-NOT-PRINT"', '{"id": 1, "id": 2}',
                    '{"nested": {"secret": 1, "secret": 2}}',
                    '{"secret": NaN}', '{"secret": Infinity}', '{"secret": -Infinity}',
                    '{"secret": 1e999}', '{"secret": 1e9999999999999999999999}',
                    '{"secret": 1e-9999999999999999999999}', '[]', 'null', '"DO-NOT-PRINT"'):
            with self.subTest(raw=raw):
                self.assert_rejection(self.run_cli(raw, "{}", raw=True))
                self.assert_rejection(self.run_cli("{}", raw, raw=True))

    def test_bounded_inputs(self):
        for raw in ('"' + 'x' * verifier.MAX_BYTES + '"', '[' * 100 + '0' + ']' * 100,
                    '[' + ','.join('0' for _ in range(verifier.MAX_NODES)) + ']'):
            self.assert_rejection(self.run_cli(raw, "{}", raw=True))

    def test_nonregular_file_does_not_block(self):
        with tempfile.TemporaryDirectory() as directory:
            pipe = Path(directory) / "secret-pipe"
            os.mkfifo(pipe)
            result = subprocess.run([sys.executable, str(SCRIPT), "--repository", fixture()[0],
                                     "--before", str(pipe), "--candidate", str(pipe)],
                                    capture_output=True, text=True, timeout=5,
                                    env={"PATH": "/usr/bin:/bin"})
            self.assert_rejection(result)

    def test_both_changes_required_and_noop_rejected(self):
        repository, before, candidate = fixture()
        self.assert_rejection(self.run_cli(before, before, repository))
        for field in verifier.FIELDS:
            partial = copy.deepcopy(candidate)
            partial["rules"][0]["parameters"][field] = before["rules"][0]["parameters"][field]
            self.assert_rejection(self.run_cli(before, partial, repository))

    def test_invalid_files_and_arguments_are_redacted(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--repository", fixture()[0],
                                 "--before", "/DO-NOT-PRINT/secret", "--candidate", "/secret"],
                                capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        self.assert_rejection(result)
        _, before, candidate = fixture()
        self.assert_rejection(self.run_cli(before, candidate, extra=("--policy", "DO-NOT-PRINT")))
        result = subprocess.run([sys.executable, str(SCRIPT), "--DO-NOT-PRINT"],
                                capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        self.assert_rejection(result)


if __name__ == "__main__":
    unittest.main()
