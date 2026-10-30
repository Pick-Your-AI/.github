# Current organization: operation and maintenance

Canonical implementation: `governance/organization.py`. Inputs are deliberately separate:

- `governance/escalation-policy.json`: existing #17 role policy, stable IDs, accepted exceptions, role-selection rules and decision references. No membership lookup changes policy.
- `governance/organization-mapping.json`: versioned public-entity allowlist and display areas, with owner and decision provenance. Area membership is display grouping, not a new operational assignment. The initial 13 Project/area/repository associations come from #22; all responsibility edges come from the existing resolver policy.
- Private `model.json`: observed GitHub entities, direct and inherited membership, managers, grants, Projects and explicit Project/repository links, coverage and source identity. Never commit or upload it. `routing-snapshot.json` is the #17 resolver projection from the same collection transaction.

Private `hierarchy.mmd` contains every observed team and its exact parent edge. Public hierarchy exports contain only approved teams; keep that distinction when sharing diagrams.

The current proposed publication path is [docs/organization/current](organization/current/README.md) on the default branch. Its HTML directory is an artifact until an approved host serves it. The existing approved website host is the static Apache/GoDaddy deployment at `https://pickyour.ai`, behind Cloudflare. Its operations-owned deployment is in `pick-your-ai-website/.github/workflows/deploy-production.yml`; this task does not bypass that pipeline or copy credentials into `.github`. There is no existing GitHub Pages site; this implementation does not silently create one. GitHub's Markdown view supports the JSON/Mermaid sources and downloadable exports; GitHub does not render the HTML directory as a website. A public URL for the interactive directory remains a hosting decision.

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

The workflow generates only from default-branch code; PR workflows run fixture tests without organization secrets. Collection uses the `organization-collector` environment, restricted to branch `main`; never put the collector key in repository or organization secrets where other branch workflows could request it. Each run verifies the App and installation identity and exact read-only permission set before issuing a short-lived collection token, revoked after the job. Publication uses a separate job-scoped `GITHUB_TOKEN`. Never reuse the membership-writing Early Contributors App.

Required setup (currently absent):

| Setting | Minimum purpose |
| --- | --- |
| `ORG_DIRECTORY_APP_ID` repository variable | Dedicated collector App identity |
| `ORG_DIRECTORY_APP_KEY` protected environment secret | Key for a short-lived installation token, available only through `organization-collector` on `main` |
| Organization Members: read | Teams, hierarchy, memberships and team-management roles |
| Organization Projects: read | Project identity, status and explicit repository associations |
| Repository Metadata: read; Administration: read; access to intended repositories | Repository identity, team grants and effective-permission probes; Administration read is required for listing repository teams |
| Job `contents: write`, `pull-requests: write`, `actions: write` | Generated branch/PR and explicit credential-free validation dispatch only; never a default-branch bypass |

The current credential verifier requires an all-repository installation with exactly Members, Projects, Metadata and Administration read. That new installation remains an explicit owner decision. The model limits completeness to collector-visible inventory. Missing expected access is failure/unknown, never an empty result. Verify all read endpoints with the proposed App before activating. This change does not authorize or perform permission expansion. See [the activation receipt](ORGANIZATION_ACTIVATION.md) for configuration and owner gates.

Publication uses the single `automation/current-organization` branch and one open PR. Policy, mappings, source and publication rules require independent review; generated observations also follow the current protected PR path. Every run reconstructs the complete bundle with trusted code and a deterministic renderer; unchanged valid bytes create no new commit, PR or notification. Damaged or injected artifacts cannot be accepted merely because the model is unchanged. Observation success is logged in the run summary. Failed PR creation is retried even if data is unchanged. Unexpected branch contents or divergent history require reconciliation rather than force-pushing. No automatic merge or deployment bypass is implemented.

GitHub Actions repository workflows do not directly receive all organization team or Projects v2 events. See [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) and [organization webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads). No receiver is deployed here. A future approved receiver needs signed organization deliveries (`team`, `membership`, `repository`, `projects_v2`), delivery-ID deduplication, and a narrowly authorized dispatch to this default-branch workflow. Existing `automation/refresh_trigger.py` is an inactive membership-event adapter; it does not become a comprehensive chart-event receiver through this change. Real delivery testing needs a disposable authorized organization, not mutations of production teams. Periodic reconciliation remains independent of such infrastructure.

## Mapping and privacy review

Propose changes to the existing mapping file with decision references; do not edit generated outputs by hand. New entities are discovered in the private inventory automatically. Approved public entities without area mappings are visibly marked unmapped. Unapproved entities remain withheld; their absence is not evidence they do not exist. Expand the public allowlist only through explicit review. A private or secret entity stays excluded even when its ID is mistakenly allowlisted. Personal roster/contact disclosure is not enabled in this version.

Projects have stable node IDs and can link to multiple repositories; areas can contain multiple teams, repositories and Projects. `project_responsibilities` is a separate many-to-many reviewed mapping (Project ID, accepted/unresolved state, team IDs and decision references). It is initially empty: the naming register establishes display associations, not accepted operational Project ownership. Each public Project therefore explicitly reports its operational assignment as unresolved until a responsibility decision is accepted. Explicit API Project/repository associations are inventory facts, not proof of responsibility. Project contents, names and repository permissions never create ownership. The actual GitHub hierarchy and display groups are separate graph edges. The public graph is the induced graph of approved teams, not a claim to show hidden parents or the full private hierarchy.

The #21 snapshot is not reused as a public roster approval. Its pending invitees and membership labels are unsuitable for automatic republication. Its blue/teal visual palette and editable Mermaid approach are retained, with strict escaping and HTML labels disabled. Existing dated evidence is untouched. Routine refresh replaces the current directory only; historical snapshots are deliberate reviewed releases, not hourly copies. Keep existing history; retain at most 12 future deliberately published monthly snapshots unless an owner documents an exception.

## Failure and rollback

Inspect the latest workflow summary, its source revision, pending artifact PR, private `status.json`, and the public observation time separately. Auth/permission failure, partial or repeated pages, malformed JSON, cycles, invalid mappings, inconsistent double observations, rendering failure and publication failure fail closed. Cached state has an integrity checksum; archive corrupt state privately and reconcile before retrying. Do not replace inaccessible data with `[]`.

Disable the workflow through GitHub Actions to stop publication. Revert a faulty generator through the normal reviewed PR path, retain private failure evidence, then manually refresh and verify. Revert a faulty published artifact commit if necessary. Never rewrite the historical snapshot branch or delete audit evidence. The last merged directory stays available when a new observation or artifact PR fails.

## Verification boundary

Tests and the [acceptance ledger](ORGANIZATION_ACCEPTANCE.md) distinguish fixtures, live authenticated reads, fresh-VM tests, independent code review, hosted checks, merge, actual scheduled execution and visible publication. Do not close #17 based on this chart extension: cross-repository flows, real event delivery, activation and its other acceptance criteria remain separately tracked.

## Prepared handoff to the existing website host

The website's current `AGENTS.md` reserves deployment workflows, `.htaccess` and `scripts/deploy/**` to its operations workstream and requires requesting those changes. The repository is a static Vite SPA, not a Node server. The minimal hosting integration is:

1. Website/operations owner accepts `/organization/` as the public path on the existing host.
2. In the website build, copy only the reviewed `.github` revision's `docs/organization/current/*` into `public/organization/`. Pin the full approved commit SHA, not a moving branch. Keep the generated directory, script, JSON and all paired exports together. The Vite build already copies `public/` into `dist/`.
3. Run the website's existing quality, unit, contract, build, accessibility, browser and `ci-required` gates. Deployment must consume that run's exact `site-dist`, validate the release, activate and read back through Cloudflare, retaining the existing restore behavior.
4. Agree how subsequent reviewed artifact commits update that source pin through the website's own PR gate. `.github`'s token cannot write another repository; use an already authorized narrowly scoped publication identity or let the responsible website team perform the pin update. Do not broaden the collector credential.
5. Verify `/organization/index.html`, `/organization/directory.js`, JSON, SVG and PNG MIME types, cache revalidation and CSP under Apache, then record the deployed website SHA and publication time. Until then the interactive directory URL is pending, not live.

This precise integration request belongs on canonical #17 and the existing website owner/review lane, not a duplicate organization automation issue. Existing hosting is identified; operations acceptance and cross-repository publication authority remain the dependency.
