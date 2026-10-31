# Escalation and current responsibility

Start with the repository team, then the repository maintainer, repository lead maintainer, applicable parent teams, and finally CompleteDotTech. Keep the disposition of every level, including an unfilled or undefined role. Do not skip directly to the owner because an earlier team includes the owner as a placeholder.

The parent stage uses each ancestor team's direct members. Members inherited from unrelated sibling teams are not automatically additional escalation recipients. The repository-team stage still includes relevant descendants of that repository team.

The [policy](../../governance/escalation-policy.json) records stable repository and team identities, accepted mappings, unresolved roles and decision sources. The [naming register](../NAMING.md) controls names. Current GitHub data supplies people, team managers, hierarchy and access. Those observations do not establish accepted individual responsibility. Issue assignees remain the authority for accepted issue ownership.

## Resolve before escalating

Use Python 3.12 and an authenticated GitHub CLI with read access to the relevant organization data. Keep snapshots outside public repositories. These commands read GitHub; they do not change members, permissions, protections or Projects.

```sh
python governance/router.py validate-policy --policy governance/escalation-policy.json
python governance/router.py refresh --policy governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json
python governance/router.py resolve --policy governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json --repo Pick-Your-AI/pick-your-ai-research --max-age-seconds 86400
```

The last value is an explicitly selected example tolerance, **not an approved organization threshold**. Refresh before a new escalation. A cached operation without an accepted policy threshold requires the caller to select a tolerance. The proposed one-day value in the policy is inert. A failed refresh preserves the last successful snapshot and its timestamp; consult the failure status as well. Do not describe stale, partial, denied or unavailable information as current.

Private resolver output can contain current people. Public directory output contains team destinations and dispositions, never a membership roster or pending invitees. Do not post raw snapshots, credentials, private repository metadata or access audit details.

```sh
python governance/router.py directory --policy governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json --max-age-seconds 86400
python governance/router.py check --policy governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json --max-age-seconds 86400
```

Use `--path` for a repository-relative path when resolving. An accepted path override can narrow maintainer/lead routing; none is configured initially. A CODEOWNERS entry does not itself authorize an escalation mapping.

## What the three kinds of authority mean

- **Operational responsibility:** an accepted role mapping or explicit issue assignment. Membership, repository Admin and a team-management role are not acceptance of work, deadlines or availability.
- **Team management:** GitHub's team-maintainer role controls membership/settings for that team. The accepted delegations and explicit deferrals remain in [#18](https://github.com/Pick-Your-AI/.github/issues/18).
- **Repository permissions:** observed effective access and configured grants. They do not prove merge eligibility, branch bypass, or acceptance of an operational role. [#16](https://github.com/Pick-Your-AI/.github/issues/16) tracks alignment separately.

The owner [selected the routing-role mapping](DECISIONS.md#routing-role-decision): Research Maintainers in the six research-family repositories, directly observed repository-team managers elsewhere, then specialty lead teams. New undefined roles remain unresolved; no assignment is invented from Admin grants. Sustainability's explicit [#143](https://github.com/Pick-Your-AI/pick-your-ai-sustainability/issues/143) remains a separate mandate. Shared Research Project administration is not repository responsibility. Empty specialty lead teams remain unfilled. Review Leads is a coordination sidecar whose role acceptance is pending; it is not an extra escalation level.

`.github` remains owner-controlled for governance even though a separately authorized Write grant exists. Internal Discussion is an accepted private exception, not an unresolved protection or delegation gap. Its private inventory is excluded from the public policy. Education is unbootstrapped: the resolver reports that state; this work does not create its first branch.

## Policy changes and refresh activation

Change mappings through a reviewed PR with the affected decision owner and links to accepted decisions. A live team rename preserves identity; a removal, changed parent or permission discrepancy requires reconciliation. Neither live lookup nor a model agreement can approve new policy, access or appointments.

The executable collector supports manual read-only refresh. [The refresh workflow example](../../automation/routing-directory.yml.example) is outside GitHub's active workflow directory and has no schedule. [The prepared event adapter and activation procedure](../../automation/ACTIVATION.md) cover authenticated delivery, duplicate suppression and recovery; no organization webhook, GitHub App, dispatch relay or recurring refresh is installed by this PR. Organization membership/team changes cannot be handled merely by naming them in a repository workflow. Activation needs an approved credential/transport, publication destination, threshold, and an actual delivery plus fallback reconciliation receipt.

The new generated directory is separate from [PR #21](https://github.com/Pick-Your-AI/.github/pull/21)'s historical charts. Neither those charts nor [PR #22](https://github.com/Pick-Your-AI/.github/pull/22)'s naming register completes dynamic routing. See [remaining decisions](DECISIONS.md) and [research refresh](RESEARCH_REFRESH.md).
