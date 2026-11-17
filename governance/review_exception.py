"""Compare local ruleset JSON against the bundled proposal; never apply settings.

Inputs are supplied by the caller. A match authenticates neither the baseline nor
GitHub enforcement, authorization, permissions, or real merge behavior.
"""
import argparse
import copy
import json
import math
import os
from pathlib import Path
import stat
import sys


PROPOSAL = Path(__file__).resolve().parents[1] / "proposals" / "research-review-exception.json"
MAX_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_NODES = 50000
FIELDS = ("required_approving_review_count", "require_last_push_approval")


class Rejected(Exception):
    """Only fixed, public-safe reason codes may leave the verifier."""


def verdict(matches, reason):
    return {"matches_proposal": matches, "evidence": "offline_diff_only", "reason": reason}


def _reject_constant(_value):
    raise Rejected("invalid_json")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate_json_key")
        result[key] = value
    return result


def _bounded_json(value):
    """Bound traversal and reject non-JSON values, including nonfinite floats."""
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise Rejected("input_limit")
        if type(item) is dict:
            if any(type(key) is not str for key in item):
                raise Rejected("invalid_json")
            pending.extend((child, depth + 1) for child in item.values())
        elif type(item) is list:
            pending.extend((child, depth + 1) for child in item)
        elif type(item) is float:
            if not math.isfinite(item):
                raise Rejected("invalid_json")
        elif item is not None and type(item) not in (str, int, bool):
            raise Rejected("invalid_json")


def read_json(path):
    """Read at most one MiB without disclosing filenames or parser exceptions."""
    try:
        # Nonblocking open plus fstat avoids waiting on pipes/devices supplied as files.
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise Rejected("input_error")
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise Rejected("input_limit")
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=_object,
                            parse_constant=_reject_constant)
        _bounded_json(result)
        return result
    except Rejected:
        raise
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise Rejected("input_error") from None


def _same(left, right):
    """JSON structural equality with exact scalar types (True is not 1)."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    if type(left) is list:
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def _operation(repository):
    proposal = read_json(PROPOSAL)
    if type(proposal) is not dict or type(proposal.get("operations")) is not list:
        raise Rejected("invalid_proposal")
    operations = proposal["operations"]
    if len(operations) != 6 or any(type(op) is not dict for op in operations):
        raise Rejected("invalid_proposal")
    names = [op.get("repository") for op in operations]
    if any(type(name) is not str for name in names) or len(set(names)) != 6:
        raise Rejected("invalid_proposal")
    matches = [op for op in operations if repository == "Pick-Your-AI/" + op["repository"]]
    if len(matches) != 1:
        raise Rejected("repository_excluded")
    op = matches[0]
    if (type(op.get("ruleset_id")) is not int or op["ruleset_id"] <= 0
            or op.get("ruleset_name") != "Review required: default branch"
            or not _same(op.get("expected_before"), dict(zip(FIELDS, (1, True))))
            or not _same(op.get("proposed_after"), dict(zip(FIELDS, (0, False))))):
        raise Rejected("invalid_proposal")
    return op


def _pull_request(document, repository, operation):
    if type(document) is not dict:
        raise Rejected("invalid_ruleset")
    if (type(document.get("id")) is not int or document["id"] != operation["ruleset_id"]
            or document.get("name") != operation["ruleset_name"]):
        raise Rejected("ruleset_identity")
    # GitHub repository-ruleset responses may include these public source fields.
    if (("source" in document and document["source"] != repository)
            or ("source_type" in document and document["source_type"] != "Repository")):
        raise Rejected("ruleset_identity")
    if (document.get("target") != "branch" or document.get("enforcement") not in ("active", "evaluate", "disabled")
            or type(document.get("conditions")) is not dict
            or type(document.get("bypass_actors")) is not list
            or type(document.get("rules")) is not list):
        raise Rejected("invalid_ruleset")
    seen = set()
    pr = None
    for rule in document["rules"]:
        if type(rule) is not dict or type(rule.get("type")) is not str or not rule["type"]:
            raise Rejected("invalid_rules")
        if rule["type"] in seen:
            raise Rejected("duplicate_rule")
        seen.add(rule["type"])
        if rule["type"] == "pull_request":
            pr = rule
    if pr is None or type(pr.get("parameters")) is not dict:
        raise Rejected("missing_pull_request")
    return pr["parameters"]


def verify(repository, before, candidate):
    """Return a public-safe verdict without mutating either caller-owned input."""
    try:
        _bounded_json(before)
        _bounded_json(candidate)
        operation = _operation(repository)
        before_pr = _pull_request(before, repository, operation)
        candidate_pr = _pull_request(candidate, repository, operation)
        if not all(key in before_pr and _same(before_pr[key], value)
                   for key, value in operation["expected_before"].items()):
            raise Rejected("baseline_mismatch")
        if not all(key in candidate_pr and _same(candidate_pr[key], value)
                   for key, value in operation["proposed_after"].items()):
            raise Rejected("candidate_mismatch")
        expected = copy.deepcopy(before)
        expected_pr = _pull_request(expected, repository, operation)
        expected_pr.update(operation["proposed_after"])
        if not _same(expected, candidate):
            raise Rejected("unrelated_change")
        return verdict(True, "matches_proposal")
    except Rejected as error:
        return verdict(False, error.args[0])


class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise Rejected("invalid_arguments")


def main(argv=None):
    parser = _Parser(description=__doc__, add_help=False)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--candidate", required=True)
    try:
        args = parser.parse_args(argv)
        result = verify(args.repository, read_json(args.before), read_json(args.candidate))
    except Rejected as error:
        result = verdict(False, error.args[0])
    print(json.dumps(result, sort_keys=True))
    return 0 if result["matches_proposal"] else 2


if __name__ == "__main__":
    sys.exit(main())
