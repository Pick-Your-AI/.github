# Current organization: operation and maintenance

Canonical implementation: `governance/organization.py`. Inputs are deliberately separate:

- `governance/escalation-policy.json`: existing #17 role policy, stable IDs, accepted exceptions, role-selection rules and decision references. No membership lookup changes policy.
- `governance/organization-mapping.json`: versioned public-entity allowlist and display areas, with owner and decision provenance. Area membership is display grouping, not a new operational assignment. The initial 13 Project/area/repository associations come from #22; all responsibility edges come from the existing resolver policy.
- Private `model.json`: observed GitHub entities, direct and inherited membership, managers, grants, Projects and explicit Project/repository links, coverage and source identity. Never commit or upload it. `routing-snapshot.json` is the #17 resolver projection from the same collection transaction.

The current proposed publication path is [docs/organization/current](organization/current/README.md) on the default branch. Its HTML directory is an artifact until an approved host serves it. There is no existing GitHub Pages site; this implementation does not silently create one. GitHub's Markdown view supports the JSON/Mermaid sources and downloadable exports; GitHub does not render the HTML directory as a website. A public URL for the interactive directory remains a hosting decision.

## Manual refresh

Use Python 3.12, Node 22 and Mermaid CLI 12.0.0 with Chromium available:

```sh
npm install --global @mermaid-js/mermaid-cli@12.0.0
python -m unittest discover -s tests -v
python governance/router.py validate-policy --policy governance/escalation-policy.json
python governance/organization.py --state /PRIVATE/organization-state \
  --source-revision "$(git rev-parse HEAD:governance)"
```

`gh` supplies the current authenticated identity. Set `PUPPETEER_EXECUTABLE_PATH` for an existing Chromium installation if needed. Keep private state outside the repository and outside the public directory. The CLI never pushes or contacts role holders. A failed collection or export retains the last complete public directory and records a private failure sidecar. The lock rejects concurrent refreshes; reconcile a crashed process and its state before removing a surviving lock.

For routing from the exact same observation:

```sh
python governance/router.py resolve --policy governance/escalation-policy.json \
  --snapshot /PRIVATE/organization-state/routing-snapshot.json \
  --status /PRIVATE/organization-state/routing-status.json \
  --repo Pick-Your-AI/pick-your-ai-research --max-age-seconds 10800
```

10800 seconds is a proposed three-hour freshness setting, not a previously accepted policy. A snapshot may be stale while an unchanged hourly check is successful: the published timestamp describes that artifact's observation, and the workflow run describes the later check. Always compare both. An open publication PR can also contain newer observations than the merged directory. No route sends messages, mentions people, assigns issues or changes permissions.

## Scheduled and change-triggered reconciliation

`.github/workflows/organization-refresh.yml` proposes minute 23 of every hour, manual dispatch, and pushes to `main` affecting the model/generator. The schedule becomes eligible only after review and merge; a cron declaration is not evidence of a scheduled execution. Delays are possible. Three missed hourly intervals should be treated as stale. GitHub run failure status is kept separate from last-good artifacts.

The workflow generates only from default-branch code; PR workflows run fixture tests without organization secrets. Each run has a short-lived dedicated GitHub App token for collection and a separate job-scoped `GITHUB_TOKEN` for publication. Never reuse the membership-writing Early Contributors App.

Required setup (currently absent):

| Setting | Minimum purpose |
| --- | --- |
| `ORG_DIRECTORY_APP_ID` repository variable | Dedicated collector App identity |
| `ORG_DIRECTORY_APP_KEY` repository secret | Key for a short-lived installation token |
| Organization Members: read | Teams, hierarchy, memberships and team-management roles |
| Organization Projects: read | Project identity, status and explicit repository associations |
| Repository Metadata: read; access to intended repositories | Repository identity and grants; effective permission probes used by the #17 resolver must be verified under this installation |
| Job `contents: write`, `pull-requests: write`, `actions: write` | Generated branch/PR and explicit credential-free validation dispatch only; never a default-branch bypass |

An installation restricted to selected repositories cannot claim a complete organization-wide inventory. The model explicitly limits completeness to the collector-visible inventory. Missing expected access is failure/unknown, never an empty result. Verify all read endpoints with the proposed App before activating. This change does not authorize or perform permission expansion.

Publication uses the single `automation/current-organization` branch and one open PR. Policy, mappings, source and publication rules require independent review; generated observations also follow the current protected PR path. Unchanged semantic data creates no new commit, PR or notification. Observation success is logged in the run summary. Failed PR creation is retried even if data is unchanged. Unexpected branch contents or divergent history require reconciliation rather than force-pushing. No automatic merge or deployment bypass is implemented.

GitHub Actions repository workflows do not directly receive all organization team or Projects v2 events. See [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) and [organization webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads). No receiver is deployed here. A future approved receiver needs signed organization deliveries (`team`, `membership`, `repository`, `projects_v2`), delivery-ID deduplication, and a narrowly authorized dispatch to this default-branch workflow. Existing `automation/refresh_trigger.py` is an inactive membership-event adapter; it does not become a comprehensive chart-event receiver through this change. Real delivery testing needs a disposable authorized organization, not mutations of production teams. Periodic reconciliation remains independent of such infrastructure.

## Mapping and privacy review

Propose changes to the existing mapping file with decision references; do not edit generated outputs by hand. New entities are discovered in the private inventory automatically. Approved public entities without area mappings are visibly marked unmapped. Unapproved entities remain withheld; their absence is not evidence they do not exist. Expand the public allowlist only through explicit review. A private or secret entity stays excluded even when its ID is mistakenly allowlisted. Personal roster/contact disclosure is not enabled in this version.

Projects have stable node IDs and can link to multiple repositories; areas can contain multiple teams, repositories and Projects. Explicit API Project/repository associations are inventory facts, not proof of responsibility. Project contents, names and repository permissions never create ownership. The actual GitHub hierarchy and display groups are separate graph edges. The public graph is the induced graph of approved teams, not a claim to show hidden parents or the full private hierarchy.

The #21 snapshot is not reused as a public roster approval. Its pending invitees and membership labels are unsuitable for automatic republication. Its blue/teal visual palette and editable Mermaid approach are retained, with strict escaping and HTML labels disabled. Existing dated evidence is untouched. Routine refresh replaces the current directory only; historical snapshots are deliberate reviewed releases, not hourly copies. Keep existing history; retain at most 12 future deliberately published monthly snapshots unless an owner documents an exception.

## Failure and rollback

Inspect the latest workflow summary, its source revision, pending artifact PR, private `status.json`, and the public observation time separately. Auth/permission failure, partial or repeated pages, malformed JSON, cycles, invalid mappings, inconsistent double observations, rendering failure and publication failure fail closed. Cached state has an integrity checksum; archive corrupt state privately and reconcile before retrying. Do not replace inaccessible data with `[]`.

Disable the workflow through GitHub Actions to stop publication. Revert a faulty generator through the normal reviewed PR path, retain private failure evidence, then manually refresh and verify. Revert a faulty published artifact commit if necessary. Never rewrite the historical snapshot branch or delete audit evidence. The last merged directory stays available when a new observation or artifact PR fails.

## Verification boundary

Tests and the [acceptance ledger](ORGANIZATION_ACCEPTANCE.md) distinguish fixtures, live authenticated reads, fresh-VM tests, independent code review, hosted checks, merge, actual scheduled execution and visible publication. Do not close #17 based on this chart extension: cross-repository flows, real event delivery, activation and its other acceptance criteria remain separately tracked.
