# Research access alignment: proposal only

This is an owner-review artifact for [#16](https://github.com/Pick-Your-AI/.github/issues/16), not authority to change GitHub settings. Live host API readback on 2026-10-30 found the following public configuration. Full individual/effective-access receipts stay private. No access, bypass actor or protection was changed.

| Repository | Independent-review ruleset | Additional team bypasses on contributor boundaries |
| --- | --- | --- |
| Research | 25362696 | Research parent, ID 20136531 |
| Sustainability | 25731107 | Research lead 20191279, Research Maintainers 20198473, Funding lead 20284775 |
| Applications | 25725543 | None beyond configured repository-role/organization-owner actors |
| Papers | 25725691 | Research lead 20191279 |
| Catalog Pipeline | 25725657 | None beyond configured repository-role/organization-owner actors |
| Datasets | 25727199 | None beyond configured repository-role/organization-owner actors |

All six review rules required one approval and latest-push approval at this readback. Research also has `Protect main` rule 25244953 with a PR requirement and zero approval count; that does not cancel the separate one-approval rule. The other existing controls and required check names must be read back, not reconstructed from this summary.

The subsequent live routing collection at 2026-10-30T03:21:19Z reported one role/access discrepancy: Research Maintainers is mapped to the Research maintainer routing stage, but its strongest observed grant there is Triage. The explicit routing decision grants no Write permission; this remains an owner decision in #16.

## Two explicit alternatives

**A — preserve current grants while roles are decided.** Keep every team grant and boundary actor unchanged. Retain the current review requirements until the owner approves the separate [review-exception proposal](../../proposals/research-review-exception.json). Continue reporting the differing maintainer capabilities as unresolved. This avoids granting authority through an ambiguous role definition.

**B — align a named maintenance role across the six repositories.** Subject to owner approval, designate Research Maintainers (20198473) as the maintenance team in each of the six, with Write and scoped contributor-boundary exemptions for branch/tag maintenance and merge updates. Keep the selected specialty lead and any expressly approved shared Research lead in the reviewed per-repository actor list. Replace Research's broad Research-parent exemption with the named maintenance/lead actors only after confirming every affected current contributor and maintainer path. Do not automatically grant shared Research lead coverage from its Project Admin role.

For B, the owner must approve the exact per-repository team list and whether shared lead coverage is needed. Existing source/evidence, fiscal/legal and release authority remain separate. The preliminary mapping deliberately leaves unaccepted role assignments unresolved; B is not encoded as accepted routing policy.

## Separate review-exception proposal

The owner selected **all changes in the six research-family repositories** for #14's scope. [The machine-readable proposal](../../proposals/research-review-exception.json) identifies the six current review rules and proposes only approval count `1 → 0` and latest-push approval `true → false`. It is a description, not an executable settings writer. Its expected-before values must match a fresh read before any future application.

Approve the merge/branch/tag capability definition first. With approval count zero, authorized mergers can merge PRs from all contributor classes, including forks; the scope decision alone does not decide who gains that merge capability. Preserve PR requirements, required checks, history, deletion/force-push safeguards, tag boundaries and every unaffected condition/actor. GitHub configuration cannot substitute for local contract, evidence, security or legal acceptance.

After separately authorized settings changes, verify included and excluded repositories, representative ordinary maintainers/leads/contributors, before/after effective permissions, exact rule IDs, and real behavior. Host configuration readback and fixture tests do not establish that behavioral result. No such change or behavioral enforcement claim is made here.
