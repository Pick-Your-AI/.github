# Organization chart acceptance ledger

This ledger tracks the chart extension to #17. Pending means pending, not accepted. The implementation builds on PR #23 at `6c7b99091eee056c10189cd7cf626b176658fb7d`; it does not replace its owner, branch, policy or repository-entrypoint PRs.

## Prior work and ownership

Live sources read on 2026-10-30: #13, #14, #15, #16, #17, #18, chart PR #21, naming PR #22, and implementation PR #23, including comments. #17 is assigned to CompleteDotTech; #23 is awaiting independent GitHub approval by zwright8. Search across the organization found no other organization-chart refresh implementation. Dataset/application directories and contributor leaderboard directories serve different products. Existing naming and cross-repository entrypoint PRs remain their own lanes.

The research checkout `pickyour.ai` tracks `Pick-Your-AI/pick-your-ai-research` and has unrelated local changes. They are untouched. This work is isolated in `pya-org-current`, tracking `Pick-Your-AI/.github`. No assignee, label, Project field, native relationship, member, grant, ruleset or Project configuration has been modified.

| Requirement | Implementation / verification | Current disposition |
| --- | --- | --- |
| Versioned observed model and reviewed policy separation | `governance/organization.py`, existing escalation policy, organization mapping | Implemented; deployment pending |
| Stable identity and refreshable metadata | Numeric team/repository IDs, Project node IDs, ID-based mapping; rename tests | Implemented |
| Full visible inventory, pages and unavailable distinction | REST paginator, fixed paginated Project queries; abort on incomplete response | Implemented; real collection evidence recorded below |
| Membership, management, access, hierarchy, responsibility distinct | Private inventory; public typed edges; existing resolver | Implemented |
| Many-to-many Projects/teams/repositories | Area arrays, Project repository associations, role edges | Implemented; synthetic tests |
| New/unmapped entities | Private auto-discovery, explicit public allowlist, unmapped and unavailable indicators | Implemented; unapproved identities deliberately withheld |
| Escalation, placeholders, vacancies, private exception | Reused #23 policy/resolver; public role dispositions | Implemented; no role acceptance invented |
| Current overview, hierarchy, area diagrams, directory, JSON | One projected model; Mermaid, SVG/PNG exports, accessible table/filter UI | Implemented; local browser and export checks passed; hosted publication pending |
| Historical evidence and bounded retention | #21 untouched; current directory replacement; deliberate monthly retention policy proposed | Implemented in design; historical PR not merged here |
| Safe labels and links | Escaped HTML/Mermaid, fixed GitHub link construction, strict renderer, CSP | Synthetic regression tests; independent review pending |
| Hourly, manual and approved source-change refresh | `organization-refresh.yml` | Prepared; not merged or executed |
| Org event availability | Official docs checked; no direct team/Projects workflow trigger assumed | No receiver/credential; no real event delivery claimed |
| Least privilege and untrusted PR isolation | Dedicated read-only App requirement; default-branch guard; fixture-only PR tests | Existing App has only Members write; unsuitable; dedicated credential missing |
| Concurrency, retries, no-op, failure recovery | Shared lock, existing retry transport, staged exports, one artifact PR | Tests; real scheduled/publication failure tests pending |
| Controlled publication and stable hosting | Protected artifact PR path; no self-approval or force push | Required GitHub approval missing; existing website hosting integration pending operations acceptance |
| Shared #17 routing and entrypoints | Routing snapshot produced in same transaction; canonical repo links | Other entrypoint PRs preserved; merged flow verification pending |
| Freshness and provenance | Artifact observation, policy/model/source revisions, separate run status | Three-hour threshold is proposed, not historical policy |
| Independent review and applicable checks | Exact revision and results added with delivery evidence | Source e2b4235 independently approved; final artifact revision review pending |
| Real authenticated manual refresh | Private evidence outside Git; only sanitized summary public | Authenticated host collection and unchanged reconciliations succeeded; latest 2026-10-30T04:36:46Z; publication remains null |
| Actual scheduled run, no-op, deployed readback | Must read back merged default branch and workflow run | Blocked by review/credential/hosting, not substituted with fixtures |
| Public privacy verification | No raw data/rosters/invitees in projection; deny secret/private entities | Tests and independent review; final artifacts to inspect |
| Canonical issue update and closure | Scoped evidence on #17, retain full issue scope | Do not close #17 |

## Evidence

Source revision `e2b4235bffa541b9cb85a431633c2679236a06c2` passed 86 tests on Windows and a fresh Ubuntu 24.04.4 / Python 3.12.3 VM. Actionlint 1.7.12 passed both workflow files in that VM. The source archive SHA-256 is `4bc7f2a4e0e68a9f20e35c418c81e91cb2f7b92d6aa27a240b96b977d3ee0ce6`. An independent reviewer re-ran 86 tests and approved that exact source revision. A genuine invalid-credential GitHub request in the fresh VM preserved every public artifact byte and caused cached routing to report `refresh_failed` with zero recipients. Local Chromium checks verified 59 public entries, 14 repository-filter results, one Research search result, a stale-age warning, and no page errors. Fifteen SVG/PNG pairs passed structural checks; desktop/mobile layout and a representative area export were visually inspected locally. The same filter, stale-warning and JavaScript-error checks passed in Chromium in the fresh VM. All 15 diagram pairs were rendered there using installed Google Chrome with its sandbox; final exported SVGs use native text, contain no HTML foreignObject labels or scripts, and retain proper Unicode. The public artifact archive SHA-256 is `ad1114cc0616326f6db226f7519f12e70835f622c42c389f2278c9c6b41e8543`. Hosted deployment remains unverified. Raw authenticated inventory and VM logs stay outside this public repository. No private records, counts of secret entities, tokens, invitations or personal membership lists belong in this ledger.

## External dependencies

1. Independent approval of the existing #22/#23 stack and this chart extension under current branch rules. No admin bypass is authorized.
2. A dedicated read-only GitHub App installation with the access listed in `ORGANIZATION.md`, supplied as `ORG_DIRECTORY_APP_ID` and `ORG_DIRECTORY_APP_KEY`. The current Members-write App cannot satisfy Project collection and will not be repurposed.
3. Operations acceptance of `/organization/` on the existing `pickyour.ai` Apache/GoDaddy host and its exact-revision build integration, as prepared in `ORGANIZATION.md`. Website `AGENTS.md` reserves deployment changes to that owner; `.github` has no Pages site. Source/artifact URLs are not a deployed searchable directory.
4. After those dependencies: actual manual run, actual hourly scheduled run, unchanged-run evidence, controlled failure/recovery and visible publication readback. A new organization webhook receiver is a separate optional dependency; no real event support is claimed before deployment and testing.

The final real authenticated reconciliation completed at `2026-10-30T04:36:46Z` with `changed: false`, retaining every published-candidate artifact byte. Its semantic public content SHA-256 was `b4e17d497ceee977ab60a7b831b83b0f69641ee6040f37058996acb33a0bf334`. This is local manual execution, not hosted Actions or a scheduled run. Source/label changes were then verified through the fresh-VM renderer; no deployed-source claim is made.
