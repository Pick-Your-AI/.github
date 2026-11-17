"""Read-only, policy-governed organization routing. Private snapshots contain people.

REST transport is GET only. The fixed GraphQL documents below are read queries;
callers cannot supply a query. GitHub access never writes or sends messages.
Policy input v1 is documented in governance/POLICY_FORMAT.md. Output is not policy.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.parse import quote, urlsplit

LEVELS = ("repository_team", "repository_maintainer", "repository_lead_maintainer")
PERMISSIONS = {"pull", "triage", "push", "maintain", "admin"}
STATES = {"accepted", "proposed", "unresolved", "exception"}
MEMBERS_QUERY = """query RoutingMembers($id: ID!, $membership: TeamMembershipType!, $cursor: String) {
  node(id: $id) { ... on Team { databaseId members(first: 100, after: $cursor, membership: $membership) {
    edges { role node { databaseId login } }
    pageInfo { hasNextPage endCursor }
  } } }
}"""
REPOSITORY_QUERY = """query RoutingRepository($id: ID!) {
  node(id: $id) { ... on Repository { databaseId isEmpty } }
}"""


class RoutingError(ValueError):
    """Safe-to-display validation or transport error (never raw API stderr)."""


class APIError(RoutingError):
    def __init__(self, resource, category, status=None):
        self.resource, self.category, self.status = resource, category, status
        super().__init__(f"{category}: {resource}" + (f" (HTTP {status})" if status else ""))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp(value):
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError()
        return result.astimezone(dt.timezone.utc)
    except (ValueError, AttributeError, TypeError):
        raise RoutingError("Invalid timezone-aware timestamp") from None


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def object_keys(value, required, location):
    if not isinstance(value, dict) or set(value) != set(required):
        raise RoutingError(f"{location}: expected exactly {', '.join(sorted(required))}")


def positive(value, location):
    if type(value) is not int or value <= 0:
        raise RoutingError(f"{location}: expected positive integer")


def string(value, location):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RoutingError(f"{location}: expected nonempty unpadded string")


def login(value, location):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", value):
        raise RoutingError(f"{location}: invalid GitHub login")


def enum(value, choices, location):
    if not isinstance(value, str) or value not in choices:
        raise RoutingError(f"{location}: invalid enum value")


def array(value, location):
    if not isinstance(value, list):
        raise RoutingError(f"{location}: expected array")


def ids(value, location):
    array(value, location)
    for item in value:
        positive(item, location)
    if len(set(value)) != len(value):
        raise RoutingError(f"{location}: duplicate IDs")


def refs(value, location, required=False):
    array(value, location)
    if required and not value:
        raise RoutingError(f"{location}: decision provenance required")
    if len(set(map(str, value))) != len(value):
        raise RoutingError(f"{location}: duplicate references")
    for item in value:
        string(item, location)
        parsed = urlsplit(item)
        parts = parsed.path.split("/")
        decision_path = bool(re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(issues|pull|discussions)/[1-9][0-9]*", parsed.path))
        document_path = (len(parts) >= 6 and parts[3] == "blob" and
                         all(re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in {".", ".."} for part in parts[1:]))
        if (parsed.scheme != "https" or parsed.netloc != "github.com" or
                parsed.username or parsed.password or parsed.query or
                not (decision_path or document_path)):
            raise RoutingError(f"{location}: expected HTTPS GitHub decision reference")


def safe_path(value, prefix=False):
    if not isinstance(value, str) or not value or value != value.strip():
        raise RoutingError("Path must be a nonempty relative POSIX path")
    if (value.startswith("/") or "\\" in value or re.search(r"[\x00-\x1f\x7f:*?\[\]{}]", value)
            or any(part in ("", ".", "..") for part in value.rstrip("/").split("/"))):
        raise RoutingError("Unsafe or non-normalized relative path")
    if prefix and not value.endswith("/"):
        raise RoutingError("Override prefix must end in /")
    if not prefix and value.endswith("/"):
        return value
    return value


def validate_role(role, where, exception_allowed):
    required = ("level", "state", "team_ids", "decision_refs")
    optional = ("member_selector",) if isinstance(role, dict) and "member_selector" in role else ()
    object_keys(role, required + optional, where)
    enum(role["level"], LEVELS, where)
    enum(role["state"], STATES, where)
    ids(role["team_ids"], where)
    refs(role["decision_refs"], where, role["state"] == "accepted")
    if role["state"] in {"accepted", "proposed"} and not role["team_ids"]:
        raise RoutingError(f"{where}: concrete team IDs required")
    if role["state"] in {"unresolved", "exception"} and role["team_ids"]:
        raise RoutingError(f"{where}: unresolved/exception roles cannot name teams")
    if role["state"] == "exception" and not exception_allowed:
        raise RoutingError(f"{where}: exception role requires owner/private exception")
    if "member_selector" in role:
        enum(role["member_selector"], {"members", "team_managers"}, where + ".member_selector")
        if role["state"] == "exception":
            raise RoutingError(f"{where}: exception role cannot select team members")


def validate_policy(policy):
    object_keys(policy, ("schema_version", "organization", "freshness", "owner_fallback", "repositories", "coordination_roles"), "policy")
    if type(policy["schema_version"]) is not int or policy["schema_version"] != 1:
        raise RoutingError("Unsupported policy schema version")
    object_keys(policy["organization"], ("login", "id"), "organization")
    positive(policy["organization"]["id"], "organization.id")
    login(policy["organization"]["login"], "organization.login")
    object_keys(policy["freshness"], ("max_age_seconds", "proposed_max_age_seconds"), "freshness")
    for key, value in policy["freshness"].items():
        if value is not None:
            positive(value, key)
    owner = policy["owner_fallback"]
    object_keys(owner, ("id", "login", "decision_refs"), "owner_fallback")
    positive(owner["id"], "owner.id")
    login(owner["login"], "owner.login")
    refs(owner["decision_refs"], "owner.decision_refs", True)
    array(policy["repositories"], "repositories")
    if not policy["repositories"]:
        raise RoutingError("No repository mappings")
    seen_ids, seen_names = set(), set()
    for repo in policy["repositories"]:
        object_keys(repo, ("id", "full_name", "public", "anchor_team_id", "managed_by_team_ids", "management_state", "management_decision_refs", "roles", "parent_chain", "expected_grants", "exceptions", "path_overrides"), "repository")
        positive(repo["id"], "repository.id")
        name = repo["full_name"]
        if not isinstance(name, str) or not re.fullmatch(re.escape(policy["organization"]["login"]) + r"/[A-Za-z0-9_.-]+", name):
            raise RoutingError("Repository outside declared organization or unsafe name")
        if repo["id"] in seen_ids or name.casefold() in seen_names:
            raise RoutingError("Duplicate repository identity")
        seen_ids.add(repo["id"])
        seen_names.add(name.casefold())
        if type(repo["public"]) is not bool:
            raise RoutingError("Repository public must be boolean")
        array(repo["exceptions"], "exceptions")
        exception_codes = set()
        for exception in repo["exceptions"]:
            object_keys(exception, ("code", "reason", "decision_refs"), "exception")
            enum(exception["code"], {"owner_controlled", "private_accepted", "unbootstrapped"}, "exception")
            string(exception["reason"], "exception.reason")
            refs(exception["decision_refs"], "exception.refs", True)
            if exception["code"] in exception_codes:
                raise RoutingError("Duplicate exception")
            exception_codes.add(exception["code"])
        exception_allowed = bool(exception_codes & {"owner_controlled", "private_accepted"})
        if "private_accepted" in exception_codes and repo["public"]:
            raise RoutingError("Private exception cannot be public")
        anchor = repo["anchor_team_id"]
        if anchor is None:
            if not exception_allowed:
                raise RoutingError("Null anchor requires owner/private exception")
        else:
            positive(anchor, "anchor")
        enum(repo["management_state"], {"accepted", "unresolved"}, "management_state")
        ids(repo["managed_by_team_ids"], "managed_by_team_ids")
        refs(repo["management_decision_refs"], "management_decision_refs", repo["management_state"] == "accepted")
        if bool(repo["managed_by_team_ids"]) != (repo["management_state"] == "accepted"):
            raise RoutingError("Management state and IDs disagree")
        array(repo["roles"], "roles")
        if [r.get("level") if isinstance(r, dict) else None for r in repo["roles"]] != list(LEVELS):
            raise RoutingError("Exactly three ordered role levels required")
        for role in repo["roles"]:
            validate_role(role, "role", exception_allowed)
        if repo["roles"][0]["state"] == "accepted" and repo["roles"][0]["team_ids"] != [anchor]:
            raise RoutingError("Accepted repository team must equal the single anchor")
        parent = repo["parent_chain"]
        object_keys(parent, ("mode", "expected_team_ids", "decision_refs"), "parent_chain")
        enum(parent["mode"], {"live_ancestors", "none"}, "parent_chain.mode")
        ids(parent["expected_team_ids"], "parent_chain.expected_team_ids")
        refs(parent["decision_refs"], "parent_chain.refs", True)
        if anchor in parent["expected_team_ids"]:
            raise RoutingError("Ancestors cannot include anchor")
        if parent["mode"] == "none":
            if anchor is not None or parent["expected_team_ids"] or not exception_allowed:
                raise RoutingError("No-parent mode requires documented null anchor")
        elif anchor is None:
            raise RoutingError("Live ancestors require anchor")
        if repo["expected_grants"] is not None:
            array(repo["expected_grants"], "expected_grants")
            grant_ids = set()
            for grant in repo["expected_grants"]:
                object_keys(grant, ("team_id", "permission", "basis", "decision_refs"), "expected_grant")
                positive(grant["team_id"], "grant.team_id")
                enum(grant["permission"], PERMISSIONS, "grant.permission")
                enum(grant["basis"], {"accepted_baseline", "observed_baseline"}, "grant.basis")
                refs(grant["decision_refs"], "grant.refs", grant["basis"] == "accepted_baseline")
                if grant["team_id"] in grant_ids:
                    raise RoutingError("Duplicate expected grant")
                grant_ids.add(grant["team_id"])
        array(repo["path_overrides"], "path_overrides")
        prefixes = set()
        for override in repo["path_overrides"]:
            object_keys(override, ("prefix", "state", "decision_refs", "roles"), "override")
            safe_path(override["prefix"], True)
            if override["prefix"] in prefixes:
                raise RoutingError("Duplicate path prefix")
            prefixes.add(override["prefix"])
            enum(override["state"], {"accepted", "proposed", "unresolved"}, "override.state")
            refs(override["decision_refs"], "override.refs", override["state"] == "accepted")
            array(override["roles"], "override.roles")
            if not override["roles"]:
                raise RoutingError("Override must include roles")
            role_levels = set()
            for role in override["roles"]:
                validate_role(role, "override.role", False)
                if role["level"] == LEVELS[0] or role["level"] in role_levels or role["state"] != override["state"]:
                    raise RoutingError("Override cannot change anchor, repeat role, or disagree with state")
                role_levels.add(role["level"])
    array(policy["coordination_roles"], "coordination_roles")
    seen_teams = set()
    for role in policy["coordination_roles"]:
        object_keys(role, ("name", "team_id", "state", "decision_refs"), "coordination_role")
        string(role["name"], "coordination.name")
        positive(role["team_id"], "coordination.team_id")
        enum(role["state"], {"accepted", "pending_acceptance"}, "coordination.state")
        refs(role["decision_refs"], "coordination.refs", True)
        if role["team_id"] in seen_teams:
            raise RoutingError("Duplicate coordination team")
        seen_teams.add(role["team_id"])
    return policy


class GitHub:
    """gh owns authentication; never reads/prints tokens or accepts arbitrary queries."""
    def __init__(self, runner=subprocess.run, sleeper=time.sleep, retries=2):
        self.runner, self.sleeper, self.retries = runner, sleeper, retries
        self.coverage = []

    def _call(self, args, resource):
        for attempt in range(self.retries + 1):
            delay = min(2 ** attempt, 4)
            try:
                result = self.runner(["gh", "api", *args, "--include"], capture_output=True, text=True, encoding="utf-8", timeout=60, check=False)
            except (OSError, subprocess.TimeoutExpired):
                error = APIError(resource, "transport_unavailable")
            else:
                body = result.stdout or ""
                # --include makes retry metadata available without exposing raw headers.
                while body.startswith("HTTP/"):
                    sections = re.split(r"\r?\n\r?\n", body, maxsplit=1)
                    if len(sections) != 2:
                        raise APIError(resource, "invalid_http_response")
                    body = sections[1]
                if result.returncode == 0:
                    try:
                        value = json.loads(body)
                    except (ValueError, TypeError):
                        raise APIError(resource, "invalid_json") from None
                    if isinstance(value, dict) and value.get("errors"):
                        raise APIError(resource, "graphql_error")
                    return value
                match = re.search(r"HTTP (\d{3})", result.stderr or "")
                status = int(match.group(1)) if match else None
                response_text = (result.stderr or "") + "\n" + (result.stdout or "")
                throttled = status == 429 or status == 403 and any(marker in response_text.lower() for marker in ("rate limit", "retry-after:", "secondary rate"))
                category = "rate_limited" if throttled else "access_denied" if status in {401, 403} else "not_found_or_inaccessible" if status == 404 else "api_failure"
                error = APIError(resource, category, status)
                if status not in {429, 500, 502, 503, 504} and not throttled:
                    raise error
                retry_after = re.search(r"(?im)^retry-after:\s*(\d+)\s*$", response_text)
                if retry_after:
                    delay = int(retry_after.group(1))
                    # Do not retry before the server's requested interval. Longer waits
                    # fail closed for a later reconciliation rather than block the agent.
                    if delay > 5:
                        raise error
                else:
                    delay = min(2 ** attempt, 4)
            if attempt == self.retries:
                raise error
            self.sleeper(delay)
        raise RoutingError("Unreachable retry state")

    def get(self, endpoint):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./?=&%-]*", endpoint) or ".." in endpoint:
            raise RoutingError("Unsafe REST endpoint")
        result = self._call(["--method", "GET", endpoint], endpoint)
        self.coverage.append({"resource": endpoint, "status": "complete", "pages": 1})
        return result

    def pages(self, endpoint):
        if "?" in endpoint:
            raise RoutingError("Pagination endpoint must omit query")
        records, identities = [], set()
        page = 1
        while True:
            batch = self.get(f"{endpoint}?per_page=100&page={page}")
            if not isinstance(batch, list):
                raise APIError(endpoint, "invalid_list")
            for record in batch:
                identity = record.get("id") if isinstance(record, dict) else None
                if identity is None or identity in identities:
                    raise APIError(endpoint, "duplicate_or_missing_identity")
                identities.add(identity)
            records.extend(batch)
            if len(batch) < 100:
                break
            page += 1
            if page > 10000:
                raise APIError(endpoint, "pagination_limit")
        self.coverage.append({"resource": endpoint, "status": "complete", "pages": page})
        return records

    def members(self, team, membership):
        enum(membership, {"IMMEDIATE", "CHILD_TEAM"}, "membership")
        cursor, seen_cursors, people = None, set(), {}
        page = 0
        while True:
            args = ["graphql", "--method", "POST", "-f", f"query={MEMBERS_QUERY}", "-f", f"id={team['node_id']}", "-f", f"membership={membership}"]
            if cursor is not None:
                args.extend(["-f", f"cursor={cursor}"])
            value = self._call(args, f"team:{team['id']}:members:{membership}")
            try:
                node = value["data"]["node"]
                if node["databaseId"] != team["id"]:
                    raise KeyError()
                connection = node["members"]
                edges, info = connection["edges"], connection["pageInfo"]
                if type(info["hasNextPage"]) is not bool or not isinstance(edges, list):
                    raise KeyError()
                for edge in edges:
                    person = edge["node"]
                    positive(person["databaseId"], "member ID")
                    string(person["login"], "member login")
                    enum(edge["role"], {"MEMBER", "MAINTAINER"}, "member role")
                    if person["databaseId"] in people:
                        raise KeyError()
                    people[person["databaseId"]] = {"id": person["databaseId"], "login": person["login"], "role": edge["role"], "origin": membership}
                page += 1
                if not info["hasNextPage"]:
                    break
                cursor = info["endCursor"]
                if not cursor or cursor in seen_cursors or page >= 10000:
                    raise KeyError()
                seen_cursors.add(cursor)
            except (KeyError, TypeError, RoutingError):
                raise APIError(f"team:{team['id']}:members:{membership}", "invalid_or_partial_graphql_page") from None
        self.coverage.append({"resource": f"team:{team['id']}:members:{membership}", "status": "complete", "pages": page, "source": "graphql"})
        return sorted(people.values(), key=lambda p: p["id"])

    def is_empty(self, repository):
        resource = f"repository:{repository['id']}:isEmpty"
        value = self._call(["graphql", "--method", "POST", "-f", f"query={REPOSITORY_QUERY}", "-f", f"id={repository['node_id']}"], resource)
        try:
            node = value["data"]["node"]
            if node["databaseId"] != repository["id"] or type(node["isEmpty"]) is not bool:
                raise KeyError()
        except (KeyError, TypeError):
            raise APIError(resource, "invalid_repository_identity_or_state") from None
        self.coverage.append({"resource": resource, "status": "complete", "pages": 1, "source": "graphql"})
        return node["isEmpty"]


def relevant_team_ids(policy):
    result = {role["team_id"] for role in policy["coordination_roles"]}
    for repo in policy["repositories"]:
        if repo["anchor_team_id"] is not None:
            result.add(repo["anchor_team_id"])
        result.update(repo["managed_by_team_ids"])
        result.update(repo["parent_chain"]["expected_team_ids"])
        result.update(g["team_id"] for g in (repo["expected_grants"] or []))
        for role in repo["roles"]:
            result.update(role["team_ids"])
        for override in repo["path_overrides"]:
            for role in override["roles"]:
                result.update(role["team_ids"])
    return result


def collect(policy, api=None):
    validate_policy(policy)
    try:
        return _collect(policy, api)
    except (AttributeError, KeyError, TypeError, IndexError):
        # A successful HTTP status is not proof of the expected protocol shape.
        # Normalize before the refresh transaction records failure, and before
        # live CLI reads can expose a traceback or response-derived identity.
        raise APIError("collection", "invalid_response") from None


def _collect(policy, api=None):
    api = api or GitHub()
    started = now()
    org = api.get(f"orgs/{policy['organization']['login']}")
    if org.get("id") != policy["organization"]["id"]:
        raise RoutingError("Organization identity mismatch")
    owner = api.get(f"user/{policy['owner_fallback']['id']}")
    if owner.get("id") != policy["owner_fallback"]["id"]:
        raise RoutingError("Owner identity mismatch")
    owner_membership = api.get(f"orgs/{org['login']}/memberships/{quote(owner['login'], safe='')}")
    if owner_membership.get("user", {}).get("id") != owner["id"]:
        raise RoutingError("Owner membership identity mismatch")
    raw_teams = api.pages(f"orgs/{org['login']}/teams")
    indexed = {team["id"]: team for team in raw_teams}
    wanted = relevant_team_ids(policy)
    # Include actual ancestors, even after drift; never silently route to them.
    queue = list(wanted)
    while queue:
        raw = indexed.get(queue.pop())
        if raw and raw.get("parent"):
            parent_id = raw["parent"]["id"]
            if parent_id not in wanted:
                wanted.add(parent_id)
                queue.append(parent_id)
    teams = []
    for team_id in sorted(wanted):
        raw = indexed.get(team_id)
        if raw is None:
            teams.append({"id": team_id, "status": "not_listed_or_inaccessible"})
            continue
        # Stable-ID read validates source identity separately from mutable slug.
        exact = api.get(f"organizations/{org['id']}/team/{team_id}")
        if exact.get("id") != team_id or exact.get("organization", {}).get("id") != org["id"]:
            raise RoutingError("Team identity/organization mismatch")
        for field in ("slug", "name", "node_id"):
            string(exact.get(field), f"team.{field}")
        immediate = api.members(exact, "IMMEDIATE")
        inherited = api.members(exact, "CHILD_TEAM")
        teams.append({"id": team_id, "status": "available", "slug": exact["slug"], "name": exact["name"],
                      "parent_id": (exact.get("parent") or {}).get("id"), "privacy": exact.get("privacy"),
                      "direct_members": immediate, "inherited_members": inherited,
                      "managers": [p for p in immediate if p["role"] == "MAINTAINER"],
                      "manager_source": "graphql:IMMEDIATE:edge.role"})
    team_index = {t["id"]: t for t in teams}
    repositories = []
    for configured in sorted(policy["repositories"], key=lambda r: r["id"]):
        raw = api.get(f"repositories/{configured['id']}")
        if raw.get("id") != configured["id"] or raw.get("owner", {}).get("id") != org["id"]:
            raise RoutingError("Repository identity/organization mismatch")
        name = raw["full_name"]
        grants = api.pages(f"repos/{name}/teams")
        observed_grants = []
        for grant in grants:
            permission = grant.get("permission")
            if permission not in PERMISSIONS:
                raise RoutingError("Unknown repository team permission")
            observed_grants.append({"team_id": grant["id"], "permission": permission})
        people = {}
        probe_teams = set(configured["parent_chain"]["expected_team_ids"])
        for role in configured["roles"]:
            probe_teams.update(role["team_ids"])
        for override in configured["path_overrides"]:
            for role in override["roles"]:
                probe_teams.update(role["team_ids"])
        for team_id in probe_teams:
            team = team_index.get(team_id, {})
            for person in team.get("direct_members", []) + team.get("inherited_members", []):
                people[person["id"]] = person
        people[owner["id"]] = owner
        def probe(person):
            permission = api.get(f"repos/{name}/collaborators/{quote(person['login'], safe='')}/permission")
            if permission.get("user", {}).get("id") != person["id"]:
                raise RoutingError("Effective permission identity mismatch")
            return {"id": person["id"], "login": person["login"], "permission": permission.get("permission"), "role_name": permission.get("role_name"), "source": "rest:collaborator-permission"}
        # Independent read probes are bounded; executor.map preserves stable result order.
        # Any failure aborts the transaction after outstanding reads settle.
        with ThreadPoolExecutor(max_workers=4) as executor:
            effective = list(executor.map(probe, sorted(people.values(), key=lambda p: p["id"])))
        repositories.append({"id": raw["id"], "full_name": name, "private": raw["private"], "empty": api.is_empty(raw),
                             "team_grants": sorted(observed_grants, key=lambda g: g["team_id"]), "effective_permissions": effective})
    completed = now()
    payload = {"organization": {"id": org["id"], "login": org["login"]},
               "owner": {"id": owner["id"], "login": owner["login"], "state": owner_membership.get("state"), "role": owner_membership.get("role")},
               "teams": teams, "repositories": repositories}
    return {"schema_version": 1, **payload, "collection": {"status": "complete", "started_at": started, "completed_at": completed,
            "content_verified_at": completed, "policy_sha256": digest(policy), "content_sha256": digest(payload),
            "transport": "gh-rest-get-and-fixed-graphql-read", "coverage": sorted(api.coverage, key=canonical)}}


def read_json(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise RoutingError("Duplicate JSON object key")
            obj[key] = value
        return obj
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(RoutingError("Nonfinite JSON number")))
    except (OSError, ValueError) as error:
        if isinstance(error, RoutingError):
            raise
        raise RoutingError("Cannot read valid JSON file") from None


def atomic_write(path, text, private=False):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == text:
        return False
    fd, temp = tempfile.mkstemp(prefix=".routing-", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if private:
            os.chmod(temp, 0o600)
        os.replace(temp, target)
        sync_directory(target.parent)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return True


def dump(value):
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def distinct_paths(paths):
    resolved = [Path(path).resolve() for path in paths]
    for index, path in enumerate(resolved):
        for other in resolved[:index]:
            if path == other or path in other.parents or other in path.parents:
                raise RoutingError("Input/output path collision")
            if path.exists() and other.exists() and os.path.samefile(path, other):
                raise RoutingError("Input/output path collision")


def refresh_lock_path(snapshot_path):
    return Path(str(Path(snapshot_path).resolve()) + ".refresh.lock")


def sync_directory(path):
    if os.name == "posix":
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


@contextmanager
def snapshot_lock(snapshot_path):
    """Exclusive across processes. Existing locks require operator reconciliation.

    No PID/age heuristics or automatic stale-lock removal are safe here. A lock
    refusal never writes snapshot or status. Only this invocation's receipt and
    unchanged directory identity permit cleanup after the body has finished.
    """
    lock = refresh_lock_path(snapshot_path)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError:
        raise RoutingError("refresh_busy_or_reconciliation_required") from None
    identity = lock.stat()
    token = uuid.uuid4().hex
    receipt = lock / "owner.json"
    # Failure to durably initialize leaves the lock for explicit reconciliation.
    with receipt.open("x", encoding="utf-8") as stream:
        stream.write(dump({"token": token, "pid": os.getpid(), "created_at": now()}))
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(lock)
    sync_directory(lock.parent)
    try:
        yield
    finally:
        try:
            current = lock.stat()
            owner = read_json(receipt)
            if (identity.st_dev, identity.st_ino) != (current.st_dev, current.st_ino) or owner.get("token") != token:
                raise RoutingError("refresh_lock_ownership_changed_reconciliation_required")
            receipt.unlink()
            lock.rmdir()
            sync_directory(lock.parent)
        except (OSError, AttributeError):
            raise RoutingError("refresh_lock_cleanup_reconciliation_required") from None


def refresh(policy, snapshot_path, status_path, api=None):
    """The sole public refresh transaction; always owns the shared snapshot lock."""
    distinct_paths((snapshot_path, status_path, refresh_lock_path(snapshot_path)))
    with snapshot_lock(snapshot_path):
        return _refresh_under_lock(policy, snapshot_path, status_path, api)


def _refresh_under_lock(policy, snapshot_path, status_path, api):
    previous = None
    try:
        if Path(snapshot_path).exists():
            previous = read_json(snapshot_path)
        snapshot = collect(policy, api)
        changes = []
        if previous:
            for kind, fields in (("teams", ("slug", "name", "parent_id", "status")), ("repositories", ("full_name", "private"))):
                old = {r["id"]: r for r in previous.get(kind, [])}
                for record in snapshot[kind]:
                    before = old.get(record["id"])
                    if before:
                        for field in fields:
                            if before.get(field) != record.get(field):
                                changes.append({"kind": kind, "id": record["id"], "field": field, "before": before.get(field), "after": record.get(field)})
        snapshot["collection"]["observed_changes"] = changes
        if previous and previous.get("collection", {}).get("content_sha256") == snapshot["collection"]["content_sha256"] and previous["collection"].get("policy_sha256") == digest(policy):
            snapshot["collection"]["content_verified_at"] = previous["collection"].get("content_verified_at", previous["collection"]["completed_at"])
        validate_snapshot(policy, snapshot)
        atomic_write(snapshot_path, dump(snapshot), private=True)
        atomic_write(status_path, dump({"schema_version": 1, "status": "complete", "attempted_at": snapshot["collection"]["completed_at"], "last_success_at": snapshot["collection"]["completed_at"], "content_sha256": snapshot["collection"]["content_sha256"]}), private=True)
        return snapshot
    except (RoutingError, OSError) as error:
        failure = {"schema_version": 1, "status": "failed", "attempted_at": now(), "last_success_at": (previous or {}).get("collection", {}).get("completed_at"),
                   "errors": [{"category": error.category if isinstance(error, APIError) else "refresh_failed", "http_status": error.status if isinstance(error, APIError) else None}]}
        atomic_write(status_path, dump(failure), private=True)
        raise


def validate_snapshot(policy, snapshot):
    try:
        collection = snapshot["collection"]
        if snapshot["schema_version"] != 1 or collection["status"] != "complete":
            raise KeyError()
        if collection["policy_sha256"] != digest(policy) or snapshot["organization"]["id"] != policy["organization"]["id"]:
            raise RoutingError("Snapshot does not match policy/organization; refresh required")
        timestamp(collection["completed_at"])
        timestamp(collection["content_verified_at"])
        if timestamp(collection["content_verified_at"]) > timestamp(collection["completed_at"]):
            raise RoutingError("Content timestamp cannot follow collection timestamp")
        if not isinstance(collection["coverage"], list) or any(c.get("status") != "complete" for c in collection["coverage"]):
            raise RoutingError("Snapshot contains incomplete source coverage")
        payload = {k: snapshot[k] for k in ("organization", "owner", "teams", "repositories")}
        if collection["content_sha256"] != digest(payload):
            raise RoutingError("Snapshot content digest mismatch")
        for key in ("teams", "repositories"):
            values = snapshot[key]
            if not isinstance(values, list) or len({r["id"] for r in values}) != len(values):
                raise KeyError()
        if {r["id"] for r in snapshot["repositories"]} != {r["id"] for r in policy["repositories"]}:
            raise RoutingError("Snapshot repository coverage mismatch")
        if not relevant_team_ids(policy).issubset({t["id"] for t in snapshot["teams"]}):
            raise RoutingError("Snapshot team coverage mismatch")
        if snapshot["owner"]["id"] != policy["owner_fallback"]["id"]:
            raise RoutingError("Snapshot owner identity mismatch")
        login(snapshot["owner"]["login"], "snapshot.owner.login")
        identities = {snapshot["owner"]["id"]: snapshot["owner"]["login"]}
        for team in snapshot["teams"]:
            positive(team["id"], "team.id")
            if team["status"] == "available":
                if not isinstance(team["slug"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", team["slug"]):
                    raise RoutingError("Invalid team slug")
                string(team["name"], "team.name")
                enum(team["privacy"], {"closed", "secret"}, "team.privacy")
                if team["manager_source"] != "graphql:IMMEDIATE:edge.role":
                    raise RoutingError("Unknown team-management provenance")
                if team["parent_id"] is not None:
                    positive(team["parent_id"], "team.parent_id")
                for group in ("direct_members", "inherited_members", "managers"):
                    if not isinstance(team[group], list):
                        raise KeyError()
                    group_ids = set()
                    for member in team[group]:
                        positive(member["id"], "member.id")
                        login(member["login"], "member.login")
                        enum(member["role"], {"MEMBER", "MAINTAINER"}, "member.role")
                        enum(member["origin"], {"IMMEDIATE", "CHILD_TEAM"}, "member.origin")
                        if member["id"] in group_ids:
                            raise RoutingError("Duplicate membership identity")
                        group_ids.add(member["id"])
                        if member["id"] in identities and identities[member["id"]] != member["login"]:
                            raise RoutingError("Conflicting observed user identities; refresh required")
                        identities[member["id"]] = member["login"]
                        if group in {"direct_members", "managers"} and member["origin"] != "IMMEDIATE":
                            raise RoutingError("Direct management/membership cannot come from child team")
                        if group == "inherited_members" and member["origin"] != "CHILD_TEAM":
                            raise RoutingError("Inherited membership source mismatch")
                        if group == "managers" and member["role"] != "MAINTAINER":
                            raise RoutingError("Team manager source role mismatch")
                expected_managers = {p["id"] for p in team["direct_members"] if p["role"] == "MAINTAINER"}
                if {p["id"] for p in team["managers"]} != expected_managers:
                    raise RoutingError("Team managers do not match direct source roles")
            elif team["status"] != "not_listed_or_inaccessible":
                raise KeyError()
        for repo in snapshot["repositories"]:
            if type(repo["private"]) is not bool or type(repo["empty"]) is not bool:
                raise RoutingError("Invalid observed repository flags")
            if not isinstance(repo["full_name"], str) or not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repo["full_name"]):
                raise RoutingError("Invalid observed repository name")
            grant_ids = set()
            for grant in repo["team_grants"]:
                positive(grant["team_id"], "observed grant.team_id")
                enum(grant["permission"], PERMISSIONS, "observed grant.permission")
                if grant["team_id"] in grant_ids:
                    raise RoutingError("Duplicate observed team grant")
                grant_ids.add(grant["team_id"])
            if not isinstance(repo["effective_permissions"], list):
                raise KeyError()
    except (KeyError, TypeError):
        raise RoutingError("Incomplete or invalid snapshot") from None
    return snapshot


def freshness(policy, snapshot, max_age_seconds=None, live=False, at=None):
    validate_snapshot(policy, snapshot)
    threshold = max_age_seconds if max_age_seconds is not None else policy["freshness"]["max_age_seconds"]
    if threshold is None and not live:
        raise RoutingError("Cached operation requires --max-age-seconds; proposed threshold is not policy")
    if threshold is not None:
        positive(threshold, "max_age_seconds")
    age = ((at or dt.datetime.now(dt.timezone.utc)) - timestamp(snapshot["collection"]["completed_at"])).total_seconds()
    if age < -60:
        raise RoutingError("Snapshot timestamp is in the future")
    state = "current" if live or age <= threshold else "stale"
    if not live and snapshot.get("_refresh_failed_at"):
        state = "refresh_failed"
    result = {"status": state, "source": "live" if live else "cached",
              "last_verified_at": snapshot["collection"]["completed_at"], "max_age_seconds": threshold}
    if snapshot.get("_refresh_failed_at"):
        result["failed_refresh_at"] = snapshot["_refresh_failed_at"]
    return result


def attach_refresh_status(snapshot, status_path):
    """Optional local failure sidecar changes freshness, not the preserved data."""
    if not Path(status_path).exists():
        return snapshot
    status = read_json(status_path)
    if not isinstance(status, dict) or status.get("schema_version") != 1 or status.get("status") not in {"complete", "failed"}:
        raise RoutingError("Invalid refresh status sidecar")
    attempted = timestamp(status.get("attempted_at"))
    if status["status"] == "failed" and attempted >= timestamp(snapshot["collection"]["completed_at"]):
        snapshot["_refresh_failed_at"] = status["attempted_at"]
    return snapshot


def ancestors(repo, teams):
    chain, seen = [], set()
    current = repo["anchor_team_id"]
    while current is not None:
        if current in seen:
            return chain, "parent_cycle"
        seen.add(current)
        team = teams.get(current)
        if not team or team.get("status") != "available":
            return chain, "parent_unavailable"
        current = team.get("parent_id")
        if current is not None:
            chain.append(current)
    if chain != repo["parent_chain"]["expected_team_ids"]:
        return chain, "parent_drift"
    return chain, None


def drift(policy, snapshot):
    validate_snapshot(policy, snapshot)
    teams = {t["id"]: t for t in snapshot["teams"]}
    observed = {r["id"]: r for r in snapshot["repositories"]}
    findings = []
    for change in snapshot["collection"].get("observed_changes", []):
        findings.append({"code": "observed_identity_or_structure_change", **change})
    if snapshot["owner"]["login"] != policy["owner_fallback"]["login"]:
        findings.append({"code": "owner_renamed"})
    if snapshot["owner"].get("role") != "admin" or snapshot["owner"].get("state") != "active":
        findings.append({"code": "owner_not_active_admin"})
    for repo in policy["repositories"]:
        actual = observed[repo["id"]]
        def add(code, **details):
            findings.append({"code": code, "repository_id": repo["id"], **details})
        if actual["full_name"] != repo["full_name"]:
            add("repository_renamed")
        if actual["private"] == repo["public"]:
            add("repository_visibility_drift")
        declared_empty = any(e["code"] == "unbootstrapped" for e in repo["exceptions"])
        if declared_empty and not actual["empty"]:
            add("declared_unbootstrapped_now_populated")
        elif actual["empty"] and not declared_empty:
            add("unexpected_empty_repository")
        if repo["parent_chain"]["mode"] == "live_ancestors":
            chain, issue = ancestors(repo, teams)
            if issue:
                add(issue, observed_team_ids=chain)
        if repo["expected_grants"] is not None:
            expected = {(g["team_id"], g["permission"]) for g in repo["expected_grants"]}
            actual_grants = {(g["team_id"], g["permission"]) for g in actual["team_grants"]}
            if expected != actual_grants:
                add("grant_drift", missing=sorted(expected - actual_grants), unexpected=sorted(actual_grants - expected))
        for role in repo["roles"]:
            for team_id in role["team_ids"]:
                if teams.get(team_id, {}).get("status") != "available":
                    add("team_not_listed_or_inaccessible", team_id=team_id, level=role["level"])
                elif role["state"] == "accepted":
                    # Configuration health, never authorization to change a role or grant.
                    # Include the accepted team's live ancestors when computing inherited access.
                    grants = {g["team_id"]: g["permission"] for g in actual["team_grants"]}
                    chain, cursor = set(), team_id
                    permissions = []
                    while cursor is not None and cursor not in chain:
                        chain.add(cursor)
                        if cursor in grants:
                            permissions.append(grants[cursor])
                        cursor = teams.get(cursor, {}).get("parent_id")
                    rank = {"pull": 1, "triage": 2, "push": 3, "maintain": 4, "admin": 5}
                    strongest = max(permissions, key=rank.get) if permissions else None
                    if strongest is None:
                        add("accepted_role_without_observed_team_access", team_id=team_id, level=role["level"], severity="needs_review")
                    elif role["level"] == "repository_maintainer" and rank[strongest] < rank["push"]:
                        add("accepted_maintainer_below_write", team_id=team_id, permission=strongest, severity="needs_review")
                    elif role["level"] == "repository_lead_maintainer" and rank[strongest] < rank["admin"]:
                        add("accepted_lead_below_admin", team_id=team_id, permission=strongest, severity="informational")
    return findings


def resolve(policy, snapshot, repository, path=None, max_age_seconds=None, live=False, at=None):
    validate_policy(policy)
    state = freshness(policy, snapshot, max_age_seconds, live, at)
    matches = [r for r in policy["repositories"] if r["full_name"].casefold() == repository.casefold()]
    if not matches:
        raise RoutingError("Repository has no governed mapping")
    repo = matches[0]
    if path is not None:
        safe_path(path)
    roles = copy.deepcopy(repo["roles"])
    overrides = [o for o in repo["path_overrides"] if path and path.startswith(o["prefix"])]
    matched = max(overrides, key=lambda o: len(o["prefix"])) if overrides else None
    if matched:
        for role in matched["roles"]:
            roles[LEVELS.index(role["level"])] = copy.deepcopy(role)
    teams = {t["id"]: t for t in snapshot["teams"]}
    actual_repo = next(r for r in snapshot["repositories"] if r["id"] == repo["id"])
    owner_id = policy["owner_fallback"]["id"]
    seen, levels = set(), []
    def level_output(level, role_state, team_ids, forced=None, member_selector="members"):
        result = {"level": level, "policy_state": role_state, "member_selector": member_selector,
                  "disposition": forced or role_state, "teams": [], "recipients": [], "excluded": []}
        unavailable = False
        for team_id in team_ids:
            team = teams.get(team_id, {})
            if team.get("status") != "available":
                result["teams"].append({"id": team_id, "disposition": "not_listed_or_inaccessible"})
                unavailable = True
                continue
            result["teams"].append({"id": team_id, "name": team["name"], "slug": team["slug"], "url": f"https://github.com/orgs/{policy['organization']['login']}/teams/{team['slug']}",
                                    "direct_managers": [{"id": p["id"], "login": p["login"]} for p in team["managers"]],
                                    "manager_source": team["manager_source"],
                                    "observed_repository_grants": [g for g in actual_repo["team_grants"] if g["team_id"] == team_id]})
            if role_state != "accepted" or forced or state["status"] != "current":
                continue
            people = {}
            if member_selector == "team_managers":
                candidates = team["managers"]
            elif member_selector == "direct_members":
                # Parent escalation must not include inherited sibling teams.
                candidates = team["direct_members"]
            else:
                candidates = team["direct_members"] + team["inherited_members"]
            for person in candidates:
                people.setdefault(person["id"], person)
            for person in sorted(people.values(), key=lambda p: p["id"]):
                reason = "owner_placeholder" if person["id"] == owner_id else "already_included" if person["id"] in seen else None
                if reason:
                    result["excluded"].append({"id": person["id"], "reason": reason})
                else:
                    seen.add(person["id"])
                    result["recipients"].append({"id": person["id"], "login": person["login"], "membership_origin": person["origin"], "observed_team_role": person["role"], "operational_assignment": "not_inferred"})
        if state["status"] != "current":
            result["disposition"] = state["status"]
        elif forced:
            pass
        elif role_state == "accepted":
            result["disposition"] = "team_unavailable" if unavailable else "resolved" if result["recipients"] else "already_included" if any(x["reason"] == "already_included" for x in result["excluded"]) else "placeholder_only" if result["excluded"] else "vacant"
        return result
    for role in roles:
        item = level_output(role["level"], role["state"], role["team_ids"], member_selector=role.get("member_selector", "members"))
        item["decision_refs"] = role["decision_refs"]
        levels.append(item)
    if repo["parent_chain"]["mode"] == "none":
        levels.append(level_output("parent_teams", "exception", [], "not_applicable_no_anchor"))
    else:
        chain, issue = ancestors(repo, teams)
        levels.append(level_output("parent_teams", "accepted", chain, issue, member_selector="direct_members"))
    owner = snapshot["owner"]
    owner_ok = owner.get("role") == "admin" and owner.get("state") == "active" and owner["login"] == policy["owner_fallback"]["login"]
    levels.append({"level": "owner", "disposition": state["status"] if state["status"] != "current" else "resolved" if owner_ok else "owner_drift", "teams": [],
                   "recipients": [{"id": owner["id"], "login": owner["login"], "operational_assignment": "final_escalation_only"}] if owner_ok and state["status"] == "current" else []})
    return {"schema_version": 1, "repository": repo["full_name"], "repository_id": repo["id"], "path": path,
            "repository_state": "unbootstrapped" if actual_repo["empty"] else "populated",
            "freshness": state, "levels": levels, "exceptions": [e["code"] for e in repo["exceptions"]],
            "path_override": matched["prefix"] if matched else None,
            "configuration_drift": [f for f in drift(policy, snapshot) if f.get("repository_id") in (None, repo["id"])],
            "effective_permissions": actual_repo["effective_permissions"],
            "coordination_roles": [{"name": r["name"], "state": r["state"], "team_id": r["team_id"], "chain_level": False, "decision_refs": r["decision_refs"]} for r in policy["coordination_roles"]],
            "instruction": "Begin with the repository-team stage. Record each unresolved stage before escalating; recipients are candidates, not accepted issue assignees. No messages have been sent."}


def directory(policy, snapshot, max_age_seconds=None, live=False, at=None):
    state = freshness(policy, snapshot, max_age_seconds, live, at)
    records = []
    observed = {r["id"]: r for r in snapshot["repositories"]}
    teams = {t["id"]: t for t in snapshot["teams"]}
    for repo in sorted(policy["repositories"], key=lambda r: r["full_name"].casefold()):
        # Both policy and live visibility must permit publication.
        if not repo["public"] or observed[repo["id"]]["private"]:
            continue
        route = resolve(policy, snapshot, repo["full_name"], max_age_seconds=max_age_seconds, live=live, at=at)
        records.append({"repository": repo["full_name"], "repository_state": route["repository_state"], "url": f"https://github.com/{repo['full_name']}", "exceptions": route["exceptions"],
                        "levels": [{"level": item["level"], "policy_state": item.get("policy_state", "accepted"), "member_selector": item.get("member_selector"),
                                    "disposition": "private_team_withheld" if any(teams.get(t.get("id"), {}).get("privacy") == "secret" for t in item["teams"]) else item["disposition"],
                                    "teams": [{"name": t["name"], "url": t["url"]} for t in item["teams"] if "url" in t and teams.get(t.get("id"), {}).get("privacy") != "secret"]} for item in route["levels"]]})
    # No roster/permissions/login or private-repo details cross this boundary.
    coordination = []
    for role in policy["coordination_roles"]:
        team = teams.get(role["team_id"], {})
        if team.get("privacy") == "secret":
            continue
        coordination.append({"name": role["name"], "state": role["state"], "chain_level": False,
                             "team_url": f"https://github.com/orgs/{policy['organization']['login']}/teams/{team['slug']}" if team.get("status") == "available" else None})
    return {"schema_version": 1, "status": state["status"], "status_scope": "at_generation_only", "export_kind": "static_snapshot", "coordination_roles": coordination,
            "snapshot_content_verified_at": snapshot["collection"]["content_verified_at"],
            "freshness_threshold_seconds": state["max_age_seconds"], "repositories": records,
            "notice": "Static export: status was evaluated at generation under the displayed threshold and is not a continuing freshness claim. Automatic refresh is not activated by this tool. Rerun the resolver before relying on this directory. Team destinations only; membership does not establish accepted issue ownership. See the private collection status for the latest successful refresh time."}


def markdown_directory(value):
    def escape(text):
        return str(text).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ").replace("\r", " ")
    lines = ["# Organization routing directory", "", f"Status at generation: **{value['status']}**. Content unchanged since: {value['snapshot_content_verified_at']}.",
             f"", f"Selected freshness threshold: {value['freshness_threshold_seconds']} seconds.", "", value["notice"], ""]
    if value["coordination_roles"]:
        lines.extend(["## Coordination roles", "", "These roles do not replace any escalation stage.", "", "| Role | Acceptance | Team destination |", "| --- | --- | --- |"])
        for role in value["coordination_roles"]:
            destination = f"[Team]({role['team_url']})" if role["team_url"] else "Unavailable"
            lines.append(f"| {escape(role['name'])} | {role['state']} | {destination} |")
        lines.append("")
    for repo in value["repositories"]:
        lines.extend([f"## [{escape(repo['repository'])}]({repo['url']})", "", f"Repository state: **{repo['repository_state']}**.", "", "| Stage | Policy state | Disposition | Team destinations |", "| --- | --- | --- | --- |"])
        for level in repo["levels"]:
            links = ", ".join(f"[{escape(t['name'])}]({t['url']})" for t in level["teams"])
            lines.append(f"| {level['level']} | {level['policy_state']} | {level['disposition']} | {links or '—'} |")
        if repo["exceptions"]:
            lines.extend(["", "Exceptions: " + ", ".join(repo["exceptions"])])
        lines.append("")
    return "\n".join(lines)


def check_entrypoints(manifest_path):
    """Manifest is local-only: {root, policy_url, paths:[relative-file,...]} records."""
    records = read_json(manifest_path)
    array(records, "entrypoint manifest")
    findings = []
    for item in records:
        object_keys(item, ("root", "policy_url", "paths"), "entrypoint")
        root = Path(item["root"]).resolve()
        array(item["paths"], "entrypoint.paths")
        for name in item["paths"]:
            safe_path(name)
            path = (root / name).resolve()
            if not path.is_relative_to(root):
                raise RoutingError("Entrypoint escapes root")
            if not path.is_file():
                findings.append({"code": "entrypoint_missing", "path": name})
            elif item["policy_url"] not in path.read_text(encoding="utf-8"):
                findings.append({"code": "entrypoint_policy_link_missing", "path": name})
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-policy", "refresh", "resolve", "directory", "check"):
        command = sub.add_parser(name)
        command.add_argument("--policy", default=str(Path(__file__).with_name("escalation-policy.json")))
        if name != "validate-policy":
            command.add_argument("--snapshot", required=name == "refresh", help="Private last-good snapshot; omit for a new live read")
            command.add_argument("--max-age-seconds", type=int)
            command.add_argument("--status", help="Private failure/success sidecar; defaults to SNAPSHOT.status.json")
        if name == "resolve":
            command.add_argument("--repo", required=True)
            command.add_argument("--path")
        if name == "directory":
            command.add_argument("--format", choices=("json", "markdown"), default="markdown")
            command.add_argument("--output")
        if name == "check":
            command.add_argument("--entrypoints")
    args = parser.parse_args(argv)
    try:
        policy = validate_policy(read_json(args.policy))
        if args.command == "validate-policy":
            print(dump({"valid": True, "repositories": len(policy["repositories"]), "policy_sha256": digest(policy)}), end="")
            return 0
        if args.command == "refresh":
            status_path = args.status or args.snapshot + ".status.json"
            distinct_paths((args.policy, args.snapshot, status_path, refresh_lock_path(args.snapshot)))
            snapshot = refresh(policy, args.snapshot, status_path)
            print(dump({"status": "complete", "completed_at": snapshot["collection"]["completed_at"], "content_sha256": snapshot["collection"]["content_sha256"]}), end="")
            return 0
        live = not args.snapshot
        snapshot = collect(policy) if live else attach_refresh_status(read_json(args.snapshot), args.status or args.snapshot + ".status.json")
        if args.command == "resolve":
            result = resolve(policy, snapshot, args.repo, args.path, args.max_age_seconds, live)
        elif args.command == "directory":
            result = directory(policy, snapshot, args.max_age_seconds, live)
            text = dump(result) if args.format == "json" else markdown_directory(result)
            if args.output:
                inputs = [args.policy, args.output]
                if args.snapshot:
                    inputs.extend((args.snapshot, args.status or args.snapshot + ".status.json", refresh_lock_path(args.snapshot)))
                distinct_paths(inputs)
                atomic_write(args.output, text)
            else:
                print(text, end="")
            return 0 if result["status"] == "current" else 2
        else:
            state = freshness(policy, snapshot, args.max_age_seconds, live)
            findings = drift(policy, snapshot)
            if state["status"] != "current":
                findings.append({"code": state["status"] + "_snapshot"})
            if args.entrypoints:
                findings.extend(check_entrypoints(args.entrypoints))
            result = {"freshness": state, "findings": findings}
            print(dump(result), end="")
            return 2 if findings else 0
        print(dump(result), end="")
        return 0 if result["freshness"]["status"] == "current" else 2
    except (RoutingError, OSError) as error:
        # Do not echo arbitrary source strings, filenames, or authentication output.
        if isinstance(error, APIError):
            report = {"error": error.category, "http_status": error.status}
        else:
            report = {"error": str(error) if isinstance(error, RoutingError) else "local_io_failure"}
        print(dump(report), file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
