# Organization governance work

Read [CONTRIBUTING.md](CONTRIBUTING.md), the [naming register](docs/NAMING.md), and [escalation guidance](docs/governance/ESCALATION.md) before changing organization policy or shared entrypoints.

Resolve current recipients through `governance/router.py` and the governed `governance/escalation-policy.json` before escalation. Keep private snapshots outside Git. Start with the repository team, then repository maintainer, repository lead maintainer, applicable parents, and finally CompleteDotTech. Report undefined, vacant, inaccessible or stale stages; do not silently skip them or treat the owner's placeholder membership as the first destination.

Preserve issue assignees, accepted decisions, explicit deferrals, contributor ownership and local repository requirements. Team membership, team-management authority, effective access and accepted operational responsibility are different facts. Review Leads is a pending-acceptance coordination role, not a replacement owner.

Policy/role changes require the applicable owner decision. Do not change memberships, permissions, protections or recurring activation because a resolver observes drift. Keep Internal Discussion's accepted exception private; do not publish membership snapshots or invitees. Education requires owner bootstrap before any branch is pushed.

Run `python -m unittest discover -s tests -v`, `python governance/router.py validate-policy --policy governance/escalation-policy.json`, and `git diff --check`. When reviewing committed work, also run `git diff --check <base>...HEAD`; a clean checkout alone checks no patch. A passing fixture test does not prove source truth, human acceptance, active automation or live GitHub enforcement. Record fresh-VM evidence and checks not run. Do not merge under an implementation-only request.

See [current organization operation and mapping](docs/ORGANIZATION.md) for the shared directory, refresh status, unresolved responsibility and proposed mapping changes. Published artifact observations and latest refresh checks are separate timestamps.
