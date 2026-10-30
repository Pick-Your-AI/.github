# Organization activation continuation

This is an activation receipt and operator handoff for #17, not approval or a
deployed-directory claim. Original stack heads remain unchanged:

| PR | Head | Required next gate |
| --- | --- | --- |
| #22 | `ce8c876f6331b4f427d7fc8c2deff4776d003cf5` | Independent human approval, then normal merge to main |
| #23 | `6c7b99091eee056c10189cd7cf626b176658fb7d` | After #22: retarget main, recheck diff/checks and human approval |
| #24 | `9abadb5fe22115da900dd86483c7428bc8b44b0e` | After #23: retarget main, recheck diff/checks and human approval |

Prior work: #17 is canonical; #13 is its parent tracker; #21 remains a separate
historical chart proposal. Organization-wide search found the existing naming,
routing and chart work, with no separate collector/hosting activation to reuse.
The existing requested reviewer is zwright8 (verified Write on `.github`). No
human review existed on any stack head at this continuation's readback.

## Readiness fixes in this continuation

Independent review identified three defects in #24's activation path:

1. A repository secret and a job `if` do not prevent another same-repository
   branch workflow from requesting the key. The refresh now uses a protected
   environment. The key must exist **only** in that environment.
2. A no-op based only on `organization.json` could retain injected JavaScript,
   incomplete exports or unexpected files. Every run now renders the complete
   bundle with trusted source, validates it and compares all bytes before a
   no-op. Historical metadata is limited to validated timestamps, never copied
   wholesale from a pending branch. Symlinks are rejected.
3. The configured App is verified before collection. The token helper requires
   the exact read-only permission set, matching App/organization identity, an
   active all-repository installation and coverage of every policy repository.
   It requests that same permission subset when minting a short-lived token,
   masks it before output, and revokes it after the job. No permission grant is
   performed by the helper.

The normal generated-branch/PR path, independent human approval, main-only
source, serialization and website ownership remain unchanged.

Additional recovery hardening removes both collection and publication tokens
from renderer subprocesses. Failed exact-head validation reuses the same
Actions run with a maximum of three attempts, preserving failed-attempt history
and avoiding artificial data edits. Exhausted retries require maintainer
investigation rather than an unbounded retry loop.

## Dedicated collector setup: owner action still required

The organization owner (CompleteDotTech) must explicitly approve and install a
dedicated App with exactly these permissions:

[Exact registration settings](organization-collector-request.json) are prepared
for review. They contain no credentials and grant nothing by themselves.

| Scope | Permission | Used for |
| --- | --- | --- |
| Repository | Metadata: read | Repository identity and collaborator effective-permission reads |
| Repository | Administration: read | `GET /repos/{owner}/{repo}/teams` |
| Organization | Members: read | Teams, nesting, direct/inherited membership, managers, owner membership |
| Organization | Projects: read (`organization_projects`) | Projects v2 identity, state and repository associations |

Installation scope: all repositories of Pick-Your-AI, including repositories
needed by the existing private policy. No Contents, Issues, Pull requests,
Actions or membership-write permission belongs on this collector. Webhooks
remain inactive. Do not reuse or modify the Early Contributors App.

Permission references: [repository teams](https://docs.github.com/en/rest/repos/repos#list-repository-teams),
[collaborator permissions](https://docs.github.com/en/rest/collaborators/collaborators#get-repository-permissions-for-a-user),
[App authentication](https://docs.github.com/en/rest/apps/apps#get-the-authenticated-app),
[installation tokens](https://docs.github.com/en/rest/apps/apps#create-an-installation-access-token-for-an-app).
The required REST permissions do not prove GraphQL coverage; complete real
paginated collection under the installed App remains mandatory.

The existing `organization-collector` environment was configured during this
continuation: environment ID `25762244408`, custom deployment branch policy
`64875990`, branch `main` only, no tags. No previous environment was overwritten.
At readback it contained no secrets. The repository and inherited organization
secret inventories contained no `ORG_DIRECTORY_APP_KEY` fallback.

After the owner approves registration/installation, an authorized operator uses
the existing secure local credential route, never chat or an issue:

```sh
gh variable set ORG_DIRECTORY_APP_ID --repo Pick-Your-AI/.github --body APP_ID
gh secret set ORG_DIRECTORY_APP_KEY --repo Pick-Your-AI/.github \
  --env organization-collector < /secure/local/path/to/private-key.pem
```

`APP_ID` is replaced with the real registered App ID. Keep the PEM out of shell
history and Git; use the owner's secure local file route. Before activation,
read back environment `custom_branch_policies=true` with exactly `main` of type
`branch`; verify no repository/inherited secret of the same name exists. An
environment reference alone is insufficient if its branch rule is removed.

Rotation: create a replacement App key via its owner, update the environment
secret through the secure route, run a real manual collection and verify its
coverage, then revoke the old key. Revocation: disable refresh, revoke the App
key or suspend/uninstall the dedicated installation, remove its environment
secret, and reconcile pending artifact PRs. Keep the last approved publication.

## Website and public readback

The production website was read back at commit
`3a3a2f863574316f8e2ec44efa6e0c344923a4b0`, from successful deployment
[41005338789](https://github.com/Pick-Your-AI/pick-your-ai-website/actions/runs/41005338789).
At this readback `/organization/` returned the same HTML bytes as `/`, SHA-256
`45c5d03d34325ab50cce088c1ac61cce9ac7676fa9ce2dd269d9124fa85bb35a`.
That HTTP 200 was a SPA fallback, **not** an operational organization directory.

Website operations ownership is recorded in website issue #26 (CompleteDotTech
and PUSHINGSQUARES), its AGENTS.md and deployment runbook; BunsDev is also a
current CODEOWNER and authorized dispatcher. Request operations-owned changes
through that lane. Membership alone does not establish accepted task ownership.
The website integration candidate and exact operations patch must be reviewed
before use. The source pin must name a genuinely approved immutable organization
revision, and changed bundle bytes require a new website source commit.

The existing stage, validate, activate, verify, restore process is retained.
Do not upload a new bundle under the previously deployed website SHA. Collector
access is separate from publication access. Until a separate propagation
identity and workflow are approved, source-pin updates remain manual and
automatic end-to-end publication remains unaccepted.

## Existing publication authority also needs reconciliation

Live `.github` configuration reports
`can_approve_pull_request_reviews=false`. GitHub's combined setting controls
Actions PR creation as well as approval; the existing job token must not be
assumed capable of creating an artifact PR. The generated branch is also
covered by contributor-boundary ruleset `25359649`; no Integration bypass actor
is configured. No push under an actual job token has been tested, so this is a
configuration gate, not a claimed observed push failure.

Do not enable the combined setting, add bypass actors or increase the collector
permissions to work around this. An authorized maintainer can perform manual
publication using the existing human account and review process, clearly
labelled manual. Automatic publication requires the owner to select a separate
permitted writer and a branch path allowed by existing rules (for example a
single reviewed `contrib/` artifact branch). Prepare and review that exact
writer/branch change before activation; preserve any existing pending branch
and PR during reconciliation. The present automatic-publication gate remains
open until the chosen route has an actual successful receipt.

## Evidence and remaining live gates

The original candidate passed 86 Python tests and policy validation again in a
new Ubuntu 24.04.4 / Python 3.12.3 Hyper-V guest. Its source archive SHA-256 was
`ae0cde16cc1eac4e2048161e25eb3703507b2ed6b8ea726cf608ed02db1ce9d0`.
A real GitHub HTTP 401 using an intentionally invalid disposable token preserved
all fixture artifact bytes, reported failed freshness and suppressed all cached
recipients. Fixture recovery then succeeded with an unchanged-output no-op.
No production secret was changed for this test. Follow-up exact-source test and
review receipts accompany this change; original and follow-up evidence are
separate.

Hosted private model/cache files under `runner.temp` are ephemeral. Durable
last-good public data is the reviewed default branch; pending publication is the
single artifact branch/PR. Each attempt now retains a public-safe
`organization-refresh-status` artifact for 30 days plus a run summary, separating
the last merged observation, current collection result/time and publication
step outcome. Failed collection never invents a new observation timestamp.
Only explicitly selected public-safe scalar fields are serialized; raw models,
rosters, credentials and API responses are never uploaded. These are separate
records; do not call the runner's private cache durable or infer current
collection from a published timestamp. Inspect run history when recovering an
ephemeral runner. Git history remains the long-lived approved output record.

Still required: genuine human approvals and ordered merges; dedicated owner-
approved App installation and full authenticated coverage; website operations
acceptance; exact approved source-pin/build/deploy; actual manual and scheduled
workflow receipts; subsequent unchanged-run evidence; approved-source trigger
and complete public browser/download verification. The cron remains proposed
at minute 23 hourly until the workflow is merged and actually executes. Three
hours remains a proposed freshness setting. No organization webhook receiver,
new permission expansion or automatic cross-repository publishing is implied.

Rollback uses the existing website runbook and retained releases; generator
rollback is a reviewed revert followed by manual reconciliation. Disable the
organization workflow to pause attempts, preserving the pending artifact PR
and last-good public release. Do not close #17 or #13 from this continuation.
