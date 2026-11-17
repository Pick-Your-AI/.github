# Governance implementation disposition

This is partial implementation under [#13](https://github.com/Pick-Your-AI/.github/issues/13), not closure of its child issues.

| Issue | Delivered scope / remaining decision |
| --- | --- |
| [#14](https://github.com/Pick-Your-AI/.github/issues/14) | Owner selected all changes in the six research-family repositories. Enforcement is unchanged. Contributor-role effects and exact ruleset changes require separate approval; preserve checks, PR/history, branch/tag safeguards and local evidence/legal gates. |
| [#15](https://github.com/Pick-Your-AI/.github/issues/15) | Proposed refresh procedure and intervals; affected domain owners retain existing policy. Coverage, interval acceptance and activation remain decisions. |
| [#16](https://github.com/Pick-Your-AI/.github/issues/16) | Read-only access/ruleset baseline and proposed alignment analysis. No membership, permissions, bypass or protection changes. Review Leads provisioned access is distinct from pending role acceptance. |
| [#17](https://github.com/Pick-Your-AI/.github/issues/17) | Resolver, governed mapping, safe public directory, failure/freshness behavior, drift checks and entrypoint integrations. Undefined role mappings stay unresolved. Webhook/App installation, recurring activation, live default-branch template flow and deployed refresh receipts remain pending. |
| [#18](https://github.com/Pick-Your-AI/.github/issues/18) | Accepted delegation and interim Project administration retained; broader delegation remains explicitly deferred. Empty specialty teams are not vacancies this PR may fill. |
| [#19](https://github.com/Pick-Your-AI/.github/issues/19) | Existing [PR #20](https://github.com/Pick-Your-AI/.github/pull/20) owns bot filtering. It is separate from routing. No invitation/apply action or issue closure is implied by a proposed fix. |

## Routing role decision

The owner explicitly selected this contact-routing policy on 2026-10-29: **Research Maintainers for the six research-family repositories; repository-team managers elsewhere; specialty lead teams next.** It grants no access and does not imply an individual accepted a task or standing assignment.

The canonical mapping therefore uses Research Maintainers (20198473) at the maintainer stage for Research, Sustainability, Applications, Papers, Catalog Pipeline and Datasets. Other public project repositories use only the repository team's directly observed GitHub team maintainers at that stage. The separate next stage is the corresponding specialty lead team, followed by applicable parent teams and finally CompleteDotTech. This is ordered escalation, not a union that skips stages.

An empty manager/lead stage remains explicitly vacant; owner placeholders are excluded until the final stage. `.github` remains the owner-controlled exception. Education's routing policy does not authorize creating its first branch. Existing permission mismatches remain read-only findings under #16.

## Prior work

[PR #20](https://github.com/Pick-Your-AI/.github/pull/20) is reused for the bot issue. [PR #21](https://github.com/Pick-Your-AI/.github/pull/21) owns frozen organization charts and is not rewritten; its roster/invitee disclosure requires the owner's review before that separate proposal is accepted. [PR #22](https://github.com/Pick-Your-AI/.github/pull/22) owns the naming register; this change is stacked above it. Repository entrypoint changes are stacked above Research #516, Website #331, Leaderboard #526, Android #761 and Apple #455, preserving their ownership and content. Static naming/charts do not implement live routing.

The dated #13 baseline is historical. The routing collection recorded at 2026-10-30T03:21:19Z included 13 public project repositories plus `.github`; Education was empty, Market had no ruleset, and Cloud Agents had different boundary coverage. These are dated configuration observations, not a perpetual inventory or proof of push/merge behavior. The accepted private Internal Discussion exception remains outside the public audit details.

## Default community-file inheritance

The root `SUPPORT.md`, `.github/ISSUE_TEMPLATE/governance-decision.yml` and `.github/pull_request_template.md` are organization defaults. Merging this PR makes them available to repositories without the corresponding local files; this contributor-facing effect is immediate and is distinct from the inactive resolver refresh automation. The defaults preserve local evidence and security requirements and establish no new private intake route. The PR template asks for the repository's required environment/evidence, rather than imposing a new organization-wide VM requirement.

The following public default-branch file audit was read from GitHub on 2026-10-30. `Local` means the repository has an override; `Default` means the relevant local file/directory was absent and the organization default is expected to apply after this PR merges. This is a file-layout audit, not a claim that GitHub's rendered contributor flow was tested. A local issue-template directory, including a configuration file, overrides the default issue forms.

| Public repository | Support | Issue forms | PR template |
| --- | --- | --- | --- |
| Applications | Default | Default | Default |
| Apple | Local | Local | Local |
| Android | Local | Local | Local |
| Leaderboard | Default | Local | Local |
| Research | Default | Local | Local |
| Cloud Agents | Default | Default | Default |
| Market | Default | Default | Default |
| Papers | Default | Local | Local |
| Sustainability | Default | Default | Default |
| Website | Local | Local | Local |
| Education | Default | Default | Default |
| Knowledge-Base | Default | Default | Default |
| Datasets | Default | Local | Local |
| Catalog Pipeline | Default | Local | Local |
| Volunteers | Default | Default | Default |

The tracked entrypoint PRs add local overrides, so the affected defaults change as those PRs merge. Education now has a default branch; the earlier empty-repository observation is historical and grants no further bootstrap authority. Knowledge-Base and Volunteers were not in the earlier routing collection and have no selected mapping in this policy: keep their routing unresolved until separately recorded. Private repository details remain outside this public audit; default inheritance is not an override of their local security or owner exceptions. Recheck the layout after merges and before claiming rendered contributor-flow acceptance.

## Permission and review proposal boundary

Before any #14 enforcement change, approve #16's per-repository merge/branch/tag capability definition. Review removal on an entire branch affects PRs from contributors as well as maintainers; do not infer that the scope decision approves new merge rights. Existing required validation and local legal/evidence policy survive an optional peer-review rule. CODEOWNERS changes remain proposals; none is made here.

The live configuration audit is kept privately, with exact repository/ruleset IDs and timestamps. It separates direct/inherited grants, effective permissions and bypass actors. Publication must not expose private rosters or raw access responses. A later owner-approved mutation needs before/after readback and appropriate behavioral evidence; this implementation provides neither that authority nor a claim those mutations occurred.

## Acceptance still required

The routing role definition above is selected. Policy review still owns expected-access discrepancies, accepted cache/research thresholds and automation transport. Public output is limited to team destinations. Production activation needs a narrow read-only credential and real trigger/fallback receipts. The existing membership-writing Early Contributors App is not silently repurposed.

No model verdict substitutes for affected owner decisions, human review, merge, deployment or live acceptance. Keep partial issue references as `Refs`; close nothing on the strength of these artifacts alone.
