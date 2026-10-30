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

The dated #13 baseline is historical. Current inventory includes 13 public project repositories plus `.github`; Education is empty, Market has no ruleset, and Cloud Agents has different boundary coverage. These are configuration observations, not proof of push/merge behavior. The accepted private Internal Discussion exception remains outside the public audit details.

## Permission and review proposal boundary

Before any #14 enforcement change, approve #16's per-repository merge/branch/tag capability definition. Review removal on an entire branch affects PRs from contributors as well as maintainers; do not infer that the scope decision approves new merge rights. Existing required validation and local legal/evidence policy survive an optional peer-review rule. CODEOWNERS changes remain proposals; none is made here.

The live configuration audit is kept privately, with exact repository/ruleset IDs and timestamps. It separates direct/inherited grants, effective permissions and bypass actors. Publication must not expose private rosters or raw access responses. A later owner-approved mutation needs before/after readback and appropriate behavioral evidence; this implementation provides neither that authority nor a claim those mutations occurred.

## Acceptance still required

The routing role definition above is selected. Policy review still owns expected-access discrepancies, accepted cache/research thresholds and automation transport. Public output is limited to team destinations. Production activation needs a narrow read-only credential and real trigger/fallback receipts. The existing membership-writing Early Contributors App is not silently repurposed.

No model verdict substitutes for affected owner decisions, human review, merge, deployment or live acceptance. Keep partial issue references as `Refs`; close nothing on the strength of these artifacts alone.
