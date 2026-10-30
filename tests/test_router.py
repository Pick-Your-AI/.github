"""Synthetic routing regressions. No fixture is a live appointment or grant."""
import contextlib
import copy
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("routing_under_test", Path(__file__).parents[1] / "governance" / "router.py")
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)

REF = "https://github.com/ExampleOrg/governance/issues/1"


def role(level, state="accepted", team_ids=None):
    return {"level": level, "state": state, "team_ids": team_ids or [], "decision_refs": [REF] if state == "accepted" else []}


def policy():
    return {
        "schema_version": 1, "organization": {"id": 100, "login": "ExampleOrg"},
        "freshness": {"max_age_seconds": None, "proposed_max_age_seconds": 86400},
        "owner_fallback": {"id": 900, "login": "example-owner", "decision_refs": [REF]},
        "coordination_roles": [{"name": "Review coordination", "team_id": 40, "state": "pending_acceptance", "decision_refs": [REF]}],
        "repositories": [{"id": 101, "full_name": "ExampleOrg/example", "public": True, "anchor_team_id": 10,
                          "managed_by_team_ids": [], "management_state": "unresolved", "management_decision_refs": [],
                          "roles": [role(router.LEVELS[0], team_ids=[10]), role(router.LEVELS[1], team_ids=[20]), role(router.LEVELS[2], team_ids=[30])],
                          "parent_chain": {"mode": "live_ancestors", "expected_team_ids": [50], "decision_refs": [REF]},
                          "expected_grants": None, "exceptions": [], "path_overrides": []}]
    }


def person(identity, origin="IMMEDIATE", position="MEMBER"):
    return {"id": identity, "login": "example-owner" if identity == 900 else f"person-{identity}", "role": position, "origin": origin}


def seal(snapshot, config):
    snapshot["collection"]["policy_sha256"] = router.digest(config)
    snapshot["collection"]["content_sha256"] = router.digest({k: snapshot[k] for k in ("organization", "owner", "teams", "repositories")})
    return snapshot


def snapshot(config=None):
    config = config or policy()
    teams = []
    for identity, parent, direct, inherited in (
        (10, 50, [person(1), person(900)], [person(2, "CHILD_TEAM")]),
        (20, None, [person(1), person(3)], []),
        (30, None, [person(900)], []),
        (40, None, [person(7)], []),
        (50, None, [person(4)], [person(1, "CHILD_TEAM"), person(900, "CHILD_TEAM")]),
    ):
        teams.append({"id": identity, "status": "available", "slug": f"team-{identity}", "name": f"Team {identity}",
                      "parent_id": parent, "privacy": "closed", "direct_members": direct, "inherited_members": inherited,
                      "managers": [], "manager_source": "graphql:IMMEDIATE:edge.role"})
    result = {"schema_version": 1, "organization": config["organization"],
              "owner": {"id": 900, "login": "example-owner", "role": "admin", "state": "active"}, "teams": teams,
              "repositories": [{"id": 101, "full_name": "ExampleOrg/example", "private": False, "empty": False,
                                "team_grants": [{"team_id": 10, "permission": "push"}],
                                "effective_permissions": [{"id": 1, "login": "person-1", "permission": "write", "role_name": "write", "source": "rest:collaborator-permission"}]}],
              "collection": {"status": "complete", "started_at": "2026-01-01T12:00:00Z", "completed_at": "2026-01-01T12:00:01Z",
                             "content_verified_at": "2026-01-01T12:00:01Z", "coverage": [], "transport": "synthetic"}}
    return seal(result, config)


AT = dt.datetime(2026, 1, 1, 12, 1, tzinfo=dt.timezone.utc)


class PolicyTests(unittest.TestCase):
    def test_example_validates(self):
        self.assertEqual(router.validate_policy(policy())["schema_version"], 1)

    def test_rejects_unknown_keys_at_every_level(self):
        paths = [(), ("organization",), ("freshness",), ("owner_fallback",), ("repositories", 0),
                 ("repositories", 0, "roles", 0), ("repositories", 0, "parent_chain"), ("coordination_roles", 0)]
        for path in paths:
            with self.subTest(path=path):
                candidate = policy()
                target = candidate
                for key in path:
                    target = target[key]
                target["surprise"] = True
                with self.assertRaises(router.RoutingError):
                    router.validate_policy(candidate)

    def test_states_identity_and_provenance(self):
        changes = [lambda p: p.update(schema_version=True),
                   lambda p: p["organization"].update(id=True),
                   lambda p: p["repositories"][0].update(public="false"),
                   lambda p: p["repositories"][0]["roles"][0].update(team_ids=[10, 20]),
                   lambda p: p["repositories"][0]["roles"][1].update(state="unresolved"),
                   lambda p: p["repositories"][0]["roles"][1].update(decision_refs=[]),
                   lambda p: p["repositories"][0]["roles"][1].update(state="exception", team_ids=[]),
                   lambda p: p["repositories"][0]["parent_chain"].update(expected_team_ids=[10]),
                   lambda p: p["repositories"][0].update(anchor_team_id=None),
                   lambda p: p["repositories"].append(copy.deepcopy(p["repositories"][0])),
                   lambda p: p["owner_fallback"].update(decision_refs=["https://evil.example/x"])]
        for change in changes:
            with self.subTest(change=change):
                candidate = policy()
                change(candidate)
                with self.assertRaises(router.RoutingError):
                    router.validate_policy(candidate)

    def test_grant_contract_and_null_versus_empty(self):
        config = policy()
        config["repositories"][0]["expected_grants"] = []
        router.validate_policy(config)
        self.assertEqual(router.drift(config, snapshot(config))[0]["code"], "grant_drift")
        config["repositories"][0]["expected_grants"] = [{"team_id": 10, "permission": "push", "basis": "accepted_baseline", "decision_refs": []}]
        with self.assertRaises(router.RoutingError):
            router.validate_policy(config)
        config["repositories"][0]["expected_grants"][0]["decision_refs"] = [REF]
        router.validate_policy(config)
        self.assertNotIn("grant_drift", [f["code"] for f in router.drift(config, snapshot(config))])

    def test_override_restrictions_and_unsafe_paths(self):
        for path in ("/absolute", "../secret", "a/../b", "a\\b", "a//b", "a/./b", "C:/file", "a/*", "a\x00b"):
            with self.subTest(path=path), self.assertRaises(router.RoutingError):
                router.safe_path(path)
        config = policy()
        override = {"prefix": "docs/", "state": "accepted", "decision_refs": [REF], "roles": [role(router.LEVELS[1], team_ids=[30])]}
        config["repositories"][0]["path_overrides"] = [override]
        router.validate_policy(config)
        for alter in (lambda o: o.update(state="unresolved"), lambda o: o["roles"][0].update(level="repository_team"),
                      lambda o: o.update(decision_refs=[]), lambda o: o.update(prefix="../docs/")):
            bad = copy.deepcopy(config)
            alter(bad["repositories"][0]["path_overrides"][0])
            with self.assertRaises(router.RoutingError):
                router.validate_policy(bad)

    def test_owner_and_private_exceptions(self):
        config = policy()
        repo = config["repositories"][0]
        repo.update(anchor_team_id=None, exceptions=[{"code": "owner_controlled", "reason": "Owner-governed example", "decision_refs": [REF]}])
        repo["roles"] = [role(level, "exception") for level in router.LEVELS]
        repo["parent_chain"].update(mode="none", expected_team_ids=[])
        router.validate_policy(config)
        result = router.resolve(config, snapshot(config), repo["full_name"], max_age_seconds=3600, at=AT)
        self.assertEqual(result["levels"][3]["disposition"], "not_applicable_no_anchor")
        repo["roles"][0]["member_selector"] = "members"
        with self.assertRaises(router.RoutingError):
            router.validate_policy(config)

    def test_selector_closed_enum_and_override(self):
        for value in ("managers", "TEAM_MANAGERS", None, False):
            config = policy()
            config["repositories"][0]["roles"][1]["member_selector"] = value
            with self.assertRaises(router.RoutingError):
                router.validate_policy(config)
        config = policy()
        selected = role(router.LEVELS[1], team_ids=[20])
        selected["member_selector"] = "team_managers"
        config["repositories"][0]["path_overrides"] = [{"prefix": "docs/", "state": "accepted", "decision_refs": [REF], "roles": [selected]}]
        router.validate_policy(config)


class ResolverTests(unittest.TestCase):
    def resolve(self, config=None, data=None, **kwargs):
        config = config or policy()
        return router.resolve(config, data or snapshot(config), "ExampleOrg/example", max_age_seconds=3600, at=AT, **kwargs)

    def test_order_dedup_owner_placeholder_and_inherited_people(self):
        result = self.resolve()
        self.assertEqual([x["level"] for x in result["levels"]], [*router.LEVELS, "parent_teams", "owner"])
        self.assertEqual([[p["id"] for p in stage["recipients"]] for stage in result["levels"]], [[1, 2], [3], [], [4], [900]])
        self.assertEqual(result["levels"][2]["disposition"], "placeholder_only")
        self.assertNotIn(7, [p["id"] for stage in result["levels"] for p in stage["recipients"]])

    def test_parent_stage_excludes_inherited_siblings_and_deduplicates_direct(self):
        data = snapshot()
        parent = next(t for t in data["teams"] if t["id"] == 50)
        parent["inherited_members"].append(person(555, "CHILD_TEAM"))
        parent["direct_members"].append(person(1))
        seal(data, policy())
        stage = self.resolve(data=data)["levels"][3]
        self.assertEqual(stage["member_selector"], "direct_members")
        self.assertEqual([p["id"] for p in stage["recipients"]], [4])
        self.assertNotIn(555, [p["id"] for p in stage["recipients"]])
        self.assertIn({"id": 1, "reason": "already_included"}, stage["excluded"])

    def test_repository_state_is_observed_and_bootstrap_drift_is_explicit(self):
        config = policy()
        data = snapshot(config)
        data["repositories"][0]["empty"] = True
        seal(data, config)
        result = self.resolve(config, data)
        self.assertEqual(result["repository_state"], "unbootstrapped")
        self.assertIn("unexpected_empty_repository", [f["code"] for f in result["configuration_drift"]])
        public = router.directory(config, data, 3600, at=AT)
        self.assertEqual(public["repositories"][0]["repository_state"], "unbootstrapped")
        config["repositories"][0]["exceptions"] = [{"code": "unbootstrapped", "reason": "Owner bootstrap pending", "decision_refs": [REF]}]
        data["repositories"][0]["empty"] = False
        seal(data, config)
        result = self.resolve(config, data)
        self.assertEqual(result["repository_state"], "populated")
        self.assertIn("declared_unbootstrapped_now_populated", [f["code"] for f in result["configuration_drift"]])

    def test_manager_selector_only_direct_managers_no_fallback(self):
        config = policy()
        config["repositories"][0]["roles"][1]["member_selector"] = "team_managers"
        data = snapshot(config)
        team = next(t for t in data["teams"] if t["id"] == 20)
        team["direct_members"][1]["role"] = "MAINTAINER"
        team["managers"] = [copy.deepcopy(team["direct_members"][1])]
        team["inherited_members"] = [person(9, "CHILD_TEAM", "MAINTAINER")]
        seal(data, config)
        result = self.resolve(config, data)
        self.assertEqual([p["id"] for p in result["levels"][1]["recipients"]], [3])
        self.assertEqual(result["levels"][1]["member_selector"], "team_managers")
        team["direct_members"][1]["role"] = "MEMBER"
        team["managers"] = []
        seal(data, config)
        self.assertEqual(self.resolve(config, data)["levels"][1]["disposition"], "vacant")
        stale = router.resolve(config, data, "ExampleOrg/example", max_age_seconds=1, at=AT)
        self.assertEqual(stale["levels"][1]["recipients"], [])

    def test_unfilled_proposed_pending_and_unbootstrapped(self):
        config = policy()
        config["repositories"][0]["roles"][1] = role(router.LEVELS[1], "unresolved")
        config["repositories"][0]["roles"][2]["state"] = "proposed"
        config["repositories"][0]["exceptions"] = [{"code": "unbootstrapped", "reason": "No initial branch", "decision_refs": [REF]}]
        result = self.resolve(config)
        self.assertEqual(result["levels"][1]["disposition"], "unresolved")
        self.assertEqual(result["levels"][2]["disposition"], "proposed")
        self.assertEqual(result["exceptions"], ["unbootstrapped"])
        data = snapshot()
        data["teams"][2]["direct_members"] = []
        seal(data, policy())
        self.assertEqual(self.resolve(data=data)["levels"][2]["disposition"], "vacant")

    def test_cached_threshold_required_proposal_not_used(self):
        with self.assertRaisesRegex(router.RoutingError, "--max-age-seconds"):
            router.resolve(policy(), snapshot(), "ExampleOrg/example", at=AT)
        for invalid in (0, -1, True):
            with self.assertRaises(router.RoutingError):
                router.freshness(policy(), snapshot(), invalid, at=AT)
        fresh = router.freshness(policy(), snapshot(), live=True, at=AT)
        self.assertEqual(fresh["source"], "live")

    def test_stale_and_future_no_recipient_fallback(self):
        stale = router.resolve(policy(), snapshot(), "ExampleOrg/example", max_age_seconds=1, at=AT)
        self.assertEqual(stale["freshness"]["status"], "stale")
        self.assertTrue(all(not level["recipients"] for level in stale["levels"]))
        with self.assertRaisesRegex(router.RoutingError, "future"):
            router.freshness(policy(), snapshot(), 3600, at=AT - dt.timedelta(days=1))

    def test_identity_content_and_partial_snapshot_rejected(self):
        for change in (lambda s: s["collection"].update(status="partial"),
                       lambda s: s["collection"].update(policy_sha256="wrong"),
                       lambda s: s["teams"][0].update(slug="changed-without-hash"),
                       lambda s: s.update(repositories=[])):
            data = snapshot()
            change(data)
            with self.assertRaises(router.RoutingError):
                self.resolve(data=data)

    def test_missing_team_and_parent_move_do_not_infer_policy(self):
        data = snapshot()
        data["teams"][1] = {"id": 20, "status": "not_listed_or_inaccessible"}
        seal(data, policy())
        result = self.resolve(data=data)
        self.assertEqual(result["levels"][1]["disposition"], "team_unavailable")
        self.assertIn("team_not_listed_or_inaccessible", [x["code"] for x in result["configuration_drift"]])
        data = snapshot()
        data["teams"][0]["parent_id"] = 40
        seal(data, policy())
        parent = self.resolve(data=data)["levels"][3]
        self.assertEqual(parent["disposition"], "parent_drift")
        self.assertEqual(parent["recipients"], [])

    def test_cycle_detected_and_current_slug_used(self):
        data = snapshot()
        data["teams"][4]["parent_id"] = 10
        seal(data, policy())
        self.assertEqual(self.resolve(data=data)["levels"][3]["disposition"], "parent_cycle")
        data = snapshot()
        data["teams"][0]["slug"] = "renamed-team"
        seal(data, policy())
        self.assertTrue(self.resolve(data=data)["levels"][0]["teams"][0]["url"].endswith("/renamed-team"))

    def test_longest_override_and_no_fallthrough(self):
        config = policy()
        config["repositories"][0]["path_overrides"] = [
            {"prefix": "docs/", "state": "accepted", "decision_refs": [REF], "roles": [role(router.LEVELS[1], team_ids=[30])]},
            {"prefix": "docs/private/", "state": "unresolved", "decision_refs": [], "roles": [role(router.LEVELS[1], "unresolved")]},
        ]
        result = self.resolve(config, path="docs/private/record.md")
        self.assertEqual(result["path_override"], "docs/private/")
        self.assertEqual(result["levels"][1]["disposition"], "unresolved")
        self.assertEqual(self.resolve(config, path="docs-other/file.md")["path_override"], None)
        with self.assertRaises(router.RoutingError):
            self.resolve(path="../outside")

    def test_unknown_repo_and_owner_drift(self):
        with self.assertRaisesRegex(router.RoutingError, "no governed mapping"):
            router.resolve(policy(), snapshot(), "ExampleOrg/unknown", max_age_seconds=3600, at=AT)
        for change in ({"login": "new-owner-name"}, {"role": "member"}, {"state": "pending"}):
            data = snapshot()
            data["owner"].update(change)
            if "login" in change:
                for team in data["teams"]:
                    for person in team["direct_members"] + team["inherited_members"]:
                        if person["id"] == 900:
                            person["login"] = change["login"]
            seal(data, policy())
            self.assertEqual(self.resolve(data=data)["levels"][-1]["disposition"], "owner_drift")

    def test_public_directory_omits_private_identity_rosters_permissions(self):
        config = policy()
        private = copy.deepcopy(config["repositories"][0])
        private.update(id=102, full_name="ExampleOrg/private-secret", public=False)
        config["repositories"].append(private)
        data = snapshot(config)
        private_data = copy.deepcopy(data["repositories"][0])
        private_data.update(id=102, full_name=private["full_name"], private=True)
        data["repositories"].append(private_data)
        seal(data, config)
        result = router.directory(config, data, 3600, at=AT)
        public = router.dump(result) + router.markdown_directory(result)
        for forbidden in ("private-secret", "person-", "example-owner", "effective_permissions", "team_grants", "\"id\":"):
            self.assertNotIn(forbidden, public)
        self.assertEqual(len(result["repositories"]), 1)
        data["repositories"][0]["private"] = True
        seal(data, config)
        self.assertEqual(router.directory(config, data, 3600, at=AT)["repositories"], [])

    def test_secret_team_name_and_url_not_published(self):
        data = snapshot()
        data["teams"][0].update(privacy="secret", slug="secret-person-team", name="Secret person team")
        seal(data, policy())
        result = router.directory(policy(), data, 3600, at=AT)
        self.assertNotIn("secret-person", router.dump(result))
        self.assertNotIn("Secret person", router.dump(result))
        self.assertEqual(result["repositories"][0]["levels"][0]["disposition"], "private_team_withheld")


class TransportTests(unittest.TestCase):
    @staticmethod
    def response(value=None, code=0, stderr=""):
        return subprocess.CompletedProcess([], code, json.dumps(value), stderr)

    def test_rest_more_than_100_and_get_only(self):
        calls = []
        def run(args, **kwargs):
            calls.append(args)
            page = 1 if args[-2].endswith("page=1") else 2
            return self.response([{"id": n} for n in (range(100) if page == 1 else range(100, 105))])
        api = router.GitHub(runner=run)
        self.assertEqual(len(api.pages("orgs/ExampleOrg/teams")), 105)
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(args[2:4] == ["--method", "GET"] for args in calls))

    def test_partial_page_failure_never_returns_partial_records(self):
        responses = [self.response([{"id": n} for n in range(100)]), self.response(code=1, stderr="secret-token gh: Forbidden (HTTP 403)")]
        api = router.GitHub(runner=lambda *a, **k: responses.pop(0))
        with self.assertRaises(router.APIError) as raised:
            api.pages("orgs/ExampleOrg/teams")
        self.assertNotIn("secret-token", str(raised.exception))
        self.assertEqual(raised.exception.category, "access_denied")

    def test_retry_bounded_and_no_mutation_transport(self):
        sleeps, calls = [], []
        def run(args, **kwargs):
            calls.append(args)
            return self.response(code=1, stderr="unavailable (HTTP 503)")
        api = router.GitHub(run, sleeps.append, retries=2)
        with self.assertRaises(router.APIError):
            api.get("orgs/ExampleOrg")
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1, 2])
        with self.assertRaises(router.RoutingError):
            api.get("https://evil.example/")

    def test_throttle_classification_retry_after_and_denial(self):
        for delay, expected_calls, expected_sleeps in ((3, 3, [3, 3]), (60, 1, [])):
            calls, sleeps = [], []
            def run(*args, **kwargs):
                calls.append(args)
                return subprocess.CompletedProcess([], 1, f"HTTP/2.0 403 Forbidden\nRetry-After: {delay}\n\n{{}}", "secondary rate limit (HTTP 403)")
            api = router.GitHub(run, sleeps.append)
            with self.assertRaises(router.APIError) as raised:
                api.get("orgs/ExampleOrg")
            self.assertEqual(raised.exception.category, "rate_limited")
            self.assertEqual(len(calls), expected_calls)
            self.assertEqual(sleeps, expected_sleeps)

    def test_repository_empty_query_uses_identity_not_size(self):
        def run(args, **kwargs):
            self.assertIn("query=" + router.REPOSITORY_QUERY, args)
            return self.response({"data": {"node": {"databaseId": 101, "isEmpty": False}}})
        self.assertFalse(router.GitHub(run).is_empty({"id": 101, "node_id": "NODE", "size": 0}))

    def test_graphql_immediate_and_inherited_cursor_pagination(self):
        calls = []
        def run(args, **kwargs):
            calls.append(args)
            second = "cursor=next" in args
            members = range(100, 105) if second else range(100)
            connection = {"edges": [{"role": "MAINTAINER" if n == 0 else "MEMBER", "node": {"databaseId": n + 1, "login": f"person-{n + 1}"}} for n in members],
                          "pageInfo": {"hasNextPage": not second, "endCursor": None if second else "next"}}
            return self.response({"data": {"node": {"databaseId": 10, "members": connection}}})
        api = router.GitHub(run)
        for kind in ("IMMEDIATE", "CHILD_TEAM"):
            result = api.members({"id": 10, "node_id": "synthetic-node"}, kind)
            self.assertEqual(len(result), 105)
            self.assertEqual(result[0]["origin"], kind)
            self.assertEqual(result[0]["role"], "MAINTAINER")
        self.assertEqual(len(calls), 4)
        self.assertTrue(all("query=" + router.MEMBERS_QUERY in call for call in calls))
        self.assertTrue(all("mutation" not in " ".join(call) for call in calls))

    def test_graphql_errors_malformed_and_repeated_cursors_fail(self):
        for value in ({"errors": [{"message": "secret"}]}, {"data": {"node": None}},
                      {"data": {"node": {"databaseId": 99, "members": {}}}}):
            api = router.GitHub(lambda *a, **k: self.response(value))
            with self.assertRaises(router.APIError):
                api.members({"id": 10, "node_id": "node"}, "IMMEDIATE")
        value = {"data": {"node": {"databaseId": 10, "members": {"edges": [], "pageInfo": {"hasNextPage": True, "endCursor": "same"}}}}}
        api = router.GitHub(lambda *a, **k: self.response(value))
        with self.assertRaises(router.APIError):
            api.members({"id": 10, "node_id": "node"}, "CHILD_TEAM")


class CollectionTests(unittest.TestCase):
    class Source:
        def __init__(self, denied=False, wrong_org=False):
            self.coverage = []
            self.denied, self.wrong_org = denied, wrong_org
            self.data = snapshot()

        def get(self, endpoint):
            self.coverage.append({"resource": endpoint, "status": "complete", "pages": 1})
            if endpoint == "orgs/ExampleOrg":
                return {"id": 999 if self.wrong_org else 100, "login": "ExampleOrg"}
            if endpoint == "user/900":
                return {"id": 900, "login": "example-owner"}
            if endpoint.endswith("/memberships/example-owner"):
                return {"user": {"id": 900}, "role": "admin", "state": "active"}
            if endpoint.startswith("organizations/100/team/"):
                identity = int(endpoint.rsplit("/", 1)[1])
                team = next(t for t in self.data["teams"] if t["id"] == identity)
                return {**team, "node_id": f"NODE{identity}", "organization": {"id": 100},
                        "parent": {"id": team["parent_id"]} if team["parent_id"] else None}
            if endpoint == "repositories/101":
                return {"id": 101, "node_id": "REPO101", "full_name": "ExampleOrg/example", "owner": {"id": 100}, "private": False, "size": 0}
            if "/collaborators/" in endpoint:
                if self.denied:
                    raise router.APIError(endpoint, "access_denied", 403)
                name = endpoint.split("/")[-2]
                identity = 900 if name == "example-owner" else int(name.split("-")[-1])
                return {"user": {"id": identity}, "permission": "write", "role_name": "write"}
            raise AssertionError(endpoint)

        def pages(self, endpoint):
            self.coverage.append({"resource": endpoint, "status": "complete", "pages": 1})
            if endpoint == "orgs/ExampleOrg/teams":
                return [{"id": t["id"], "parent": {"id": t["parent_id"]} if t["parent_id"] else None} for t in self.data["teams"]]
            if endpoint == "repos/ExampleOrg/example/teams":
                return [{"id": 10, "permission": "push"}, {"id": 20, "permission": "push"}, {"id": 30, "permission": "admin"}]
            raise AssertionError(endpoint)

        def members(self, team, kind):
            self.coverage.append({"resource": f"team:{team['id']}:{kind}", "status": "complete", "pages": 1})
            source = next(t for t in self.data["teams"] if t["id"] == team["id"])
            return copy.deepcopy(source["direct_members" if kind == "IMMEDIATE" else "inherited_members"])

        def is_empty(self, repository):
            return False

    def test_full_collection_preserves_provenance_and_effective_probes(self):
        config = policy()
        data = router.collect(config, self.Source())
        router.validate_snapshot(config, data)
        self.assertEqual(data["owner"]["id"], 900)
        inherited = next(t for t in data["teams"] if t["id"] == 10)["inherited_members"]
        self.assertEqual(inherited[0]["origin"], "CHILD_TEAM")
        self.assertTrue(data["repositories"][0]["effective_permissions"])
        self.assertFalse(data["repositories"][0]["empty"])
        self.assertEqual(router.drift(config, data), [])

    def test_refresh_fails_as_a_whole_on_denied_effective_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "snapshot.json", Path(temp) / "status.json"
            original = router.dump(snapshot())
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(router.APIError):
                router.refresh(policy(), path, status, self.Source(denied=True))
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(router.read_json(status)["status"], "failed")

    def test_wrong_organization_rejected_before_collection(self):
        with self.assertRaisesRegex(router.RoutingError, "Organization identity"):
            router.collect(policy(), self.Source(wrong_org=True))

    def test_rename_refresh_keeps_id_reports_change_uses_new_link(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "snapshot.json", Path(temp) / "status.json"
            original = router.collect(policy(), self.Source())
            path.write_text(router.dump(original), encoding="utf-8")
            source = self.Source()
            source.data["teams"][0]["slug"] = "new-name"
            result = router.refresh(policy(), path, status, source)
            self.assertEqual(next(t for t in result["teams"] if t["id"] == 10)["slug"], "new-name")
            self.assertIn("observed_identity_or_structure_change", [f["code"] for f in router.drift(policy(), result)])

    def test_snapshot_rejects_forged_sources_and_unsafe_public_destinations(self):
        for change in (lambda s: s["teams"][0].update(slug="bad](https://evil.example)"),
                       lambda s: s["teams"][0]["direct_members"][0].update(origin="CHILD_TEAM"),
                       lambda s: s["teams"][0]["direct_members"][0].update(role="MAINTAINER"),
                       lambda s: s["collection"].update(coverage=[{"status": "partial"}])):
            data = snapshot()
            change(data)
            seal(data, policy())
            with self.assertRaises(router.RoutingError):
                router.validate_snapshot(policy(), data)


class PersistenceAndCLITests(unittest.TestCase):
    def test_atomic_rename_syncs_each_output_directory_after_replace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot_path, status_path = root / "data" / "snapshot.json", root / "status" / "status.json"
            events = []
            original_replace = router.os.replace
            def replace(source, target):
                original_replace(source, target)
                events.append(("replace", Path(target).parent))
            def sync(path):
                events.append(("sync", Path(path)))
            with mock.patch.object(router.os, "replace", side_effect=replace), mock.patch.object(router, "sync_directory", side_effect=sync):
                with mock.patch.object(router, "collect", return_value=snapshot()):
                    router.refresh(policy(), snapshot_path, status_path)
            for path in (snapshot_path, status_path):
                index = events.index(("replace", path.parent))
                self.assertEqual(events[index + 1], ("sync", path.parent))
            self.assertEqual(router.read_json(status_path)["status"], "complete")
            before = snapshot_path.read_bytes()
            events.clear()
            with mock.patch.object(router.os, "replace", side_effect=replace), mock.patch.object(router, "sync_directory", side_effect=sync):
                with mock.patch.object(router, "collect", side_effect=router.APIError("private-endpoint", "access_denied", 403)):
                    with self.assertRaises(router.APIError):
                        router.refresh(policy(), snapshot_path, status_path)
            index = events.index(("replace", status_path.parent))
            self.assertEqual(events[index + 1], ("sync", status_path.parent))
            self.assertEqual(snapshot_path.read_bytes(), before)
            self.assertEqual(router.read_json(status_path)["status"], "failed")

    def test_cli_api_error_omits_endpoint_and_member_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "policy.json"
            config.write_text(router.dump(policy()), encoding="utf-8")
            output = io.StringIO()
            error = router.APIError("repos/ExampleOrg/private/collaborators/sensitive-login/permission", "access_denied", 403)
            with mock.patch.object(router, "collect", side_effect=error), contextlib.redirect_stderr(output):
                self.assertEqual(router.main(["resolve", "--policy", str(config), "--repo", "ExampleOrg/example"]), 1)
            self.assertEqual(json.loads(output.getvalue()), {"error": "access_denied", "http_status": 403})
            self.assertNotIn("sensitive-login", output.getvalue())
            self.assertNotIn("collaborators", output.getvalue())

    def test_concurrent_manual_refresh_refuses_before_any_state_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "snapshot.json", Path(temp) / "status.json"
            path.write_text(router.dump(snapshot()), encoding="utf-8")
            before = path.read_bytes()
            entered, release = threading.Event(), threading.Event()
            def blocked(*args):
                entered.set()
                self.assertTrue(release.wait(5))
                return snapshot()
            with mock.patch.object(router, "collect", side_effect=blocked) as collect:
                with router.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(router.refresh, policy(), path, status)
                    self.assertTrue(entered.wait(5))
                    try:
                        with self.assertRaisesRegex(router.RoutingError, "^refresh_busy_or_reconciliation_required$"):
                            router.refresh(policy(), path, status)
                        self.assertEqual(path.read_bytes(), before)
                        self.assertFalse(status.exists())
                    finally:
                        release.set()
                    future.result()
                self.assertEqual(collect.call_count, 1)
            self.assertFalse(router.refresh_lock_path(path).exists())

    def test_preexisting_lock_never_expires_or_mutates_lastgood(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "snapshot.json", Path(temp) / "status.json"
            path.write_text(router.dump(snapshot()), encoding="utf-8")
            before = path.read_bytes()
            lock = router.refresh_lock_path(path)
            lock.mkdir()
            (lock / "owner.json").write_text('{"pid":1,"created_at":"1900-01-01T00:00:00Z","token":"old"}')
            with mock.patch.object(router, "collect") as collect:
                with self.assertRaisesRegex(router.RoutingError, "refresh_busy_or_reconciliation_required"):
                    router.refresh(policy(), path, status)
                collect.assert_not_called()
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(status.exists())
            self.assertTrue(lock.is_dir())

    def test_cli_other_process_respects_manual_snapshot_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status, config = (Path(temp) / name for name in ("snapshot.json", "status.json", "policy.json"))
            path.write_text(router.dump(snapshot()), encoding="utf-8")
            config.write_text(router.dump(policy()), encoding="utf-8")
            before = path.read_bytes()
            with router.snapshot_lock(path):
                result = subprocess.run([sys.executable, str(Path(router.__file__)), "refresh", "--policy", str(config),
                                         "--snapshot", str(path), "--status", str(status)], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stderr)["error"], "refresh_busy_or_reconciliation_required")
                self.assertTrue(router.refresh_lock_path(path).exists())
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(status.exists())

    def test_changed_lock_owner_is_not_removed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "snapshot.json"
            with self.assertRaisesRegex(router.RoutingError, "ownership_changed"):
                with router.snapshot_lock(path):
                    (router.refresh_lock_path(path) / "owner.json").write_text('{"token":"different-owner"}')
            self.assertTrue(router.refresh_lock_path(path).is_dir())

    def test_refresh_and_cli_reject_hardlink_and_ancestor_collisions(self):
        with tempfile.TemporaryDirectory() as temp:
            path, alias = Path(temp) / "snapshot.json", Path(temp) / "alias.json"
            path.write_text(router.dump(snapshot()), encoding="utf-8")
            router.os.link(path, alias)
            with self.assertRaisesRegex(router.RoutingError, "path collision"):
                router.refresh(policy(), path, alias)
            with self.assertRaisesRegex(router.RoutingError, "path collision"):
                router.refresh(policy(), path, path / "status.json")
            self.assertFalse(router.refresh_lock_path(path).exists())

    def test_failed_refresh_sidecar_suppresses_cached_recipients(self):
        with tempfile.TemporaryDirectory() as temp:
            status = Path(temp) / "status.json"
            status.write_text(router.dump({"schema_version": 1, "status": "failed", "attempted_at": "2026-01-01T12:00:30Z", "last_success_at": "2026-01-01T12:00:01Z", "errors": [{"category": "access_denied"}]}), encoding="utf-8")
            data = router.attach_refresh_status(snapshot(), status)
            result = router.resolve(policy(), data, "ExampleOrg/example", max_age_seconds=3600, at=AT)
            self.assertEqual(result["freshness"]["status"], "refresh_failed")
            self.assertEqual(result["freshness"]["last_verified_at"], "2026-01-01T12:00:01Z")
            self.assertTrue(all(not level["recipients"] for level in result["levels"]))

    def test_failed_refresh_preserves_last_good_and_records_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "private.json", Path(temp) / "status.json"
            path.write_text(router.dump(snapshot()), encoding="utf-8")
            original = path.read_bytes()
            with mock.patch.object(router, "collect", side_effect=router.APIError("secret-resource", "access_denied", 403)):
                with self.assertRaises(router.APIError):
                    router.refresh(policy(), path, status)
            self.assertEqual(path.read_bytes(), original)
            failure = router.read_json(status)
            self.assertEqual(failure["status"], "failed")
            self.assertEqual(failure["last_success_at"], "2026-01-01T12:00:01Z")
            self.assertNotIn("secret-resource", status.read_text())

    def test_same_content_keeps_directory_stable_and_refresh_timestamp_new(self):
        with tempfile.TemporaryDirectory() as temp:
            path, status = Path(temp) / "private.json", Path(temp) / "status.json"
            original = snapshot()
            path.write_text(router.dump(original), encoding="utf-8")
            updated = snapshot()
            updated["collection"].update(completed_at="2026-01-01T12:00:30Z", content_verified_at="2026-01-01T12:00:30Z")
            with mock.patch.object(router, "collect", return_value=updated):
                result = router.refresh(policy(), path, status)
            self.assertEqual(result["collection"]["completed_at"], "2026-01-01T12:00:30Z")
            self.assertEqual(result["collection"]["content_verified_at"], original["collection"]["content_verified_at"])
            self.assertEqual(router.directory(policy(), result, 3600, at=AT), router.directory(policy(), original, 3600, at=AT))
            markdown = router.markdown_directory(router.directory(policy(), result, 3600, at=AT))
            self.assertIn("Content unchanged since:", markdown)
            self.assertNotIn("Content snapshot verified:", markdown)
            output = Path(temp) / "directory.md"
            self.assertTrue(router.atomic_write(output, "same"))
            first = output.stat().st_mtime_ns
            self.assertFalse(router.atomic_write(output, "same"))
            self.assertEqual(output.stat().st_mtime_ns, first)

    def test_duplicate_keys_and_nonfinite_values_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            for value in ('{"x":1,"x":2}', '{"x": NaN}'):
                path.write_text(value)
                with self.assertRaises(router.RoutingError):
                    router.read_json(path)

    def test_entrypoint_check_missing_and_link_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "AGENTS.md").write_text("No policy link", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{"root": str(root), "policy_url": REF, "paths": ["AGENTS.md", "SUPPORT.md"]}]))
            self.assertEqual({f["code"] for f in router.check_entrypoints(manifest)}, {"entrypoint_missing", "entrypoint_policy_link_missing"})

    def test_cli_validate_and_stale_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            path, data = Path(temp) / "policy.json", Path(temp) / "snapshot.json"
            path.write_text(router.dump(policy()), encoding="utf-8")
            data.write_text(router.dump(snapshot()), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(router.main(["validate-policy", "--policy", str(path)]), 0)
                self.assertEqual(router.main(["resolve", "--policy", str(path), "--snapshot", str(data), "--repo", "ExampleOrg/example", "--max-age-seconds", "1"]), 2)
            self.assertIn('"status": "stale"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
