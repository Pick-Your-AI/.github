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

## Concrete target for reviewing alternative B

The 2026-11-17 completion campaign selects B as the concrete **proposal to review**, so an unresolved engineering choice does not prevent preparation. This table is not an accepted grant, actor mutation or operational-duty assignment. Its specialty lead IDs come from the accepted routing map in `governance/escalation-policy.json`; routing acceptance alone does not confer these proposed capabilities. Current grants must still be read back before implementation.

Research Maintainers (`20198473`) is proposed to receive Write in all six repositories. The proposed named team actors for permitted branch/tag maintenance and PR merge updates are:

| Repository | Maintainer actor | Specialty lead actor | Shared Research lead actor (`20191279`) | Owner disposition |
| --- | --- | --- | --- | --- |
| Research | Research Maintainers `20198473` | AI Builder lead `20421768` | Include explicitly to replace broad Research-parent coverage | Proposed; not applied |
| Sustainability | Research Maintainers `20198473` | Funding lead `20284775` | Retain the historical named exception, subject to fresh readback | Proposed; not applied |
| Applications | Research Maintainers `20198473` | Applications lead `20421771` | No additional exception proposed | Proposed; not applied |
| Papers | Research Maintainers `20198473` | Papers lead `20421770` | Retain the historical named exception, subject to fresh readback | Proposed; not applied |
| Catalog Pipeline | Research Maintainers `20198473` | Catalog Pipeline lead `20421773` | No additional exception proposed | Proposed; not applied |
| Datasets | Research Maintainers `20198473` | Datasets lead `20421774` | No additional exception proposed | Proposed; not applied |

No additional Admin grant is proposed for a lead team. Existing lead grants are a separate readback and owner disposition; Project administration never supplies a missing repository grant. Research's broad parent actor `20136531` would be replaced only after the named actors and affected contributor paths are verified. The organization-owner and repository-role actors remain subject to their existing separately reviewed controls.

The capability contract for every row is:

- Ordinary contributors, fork authors, Early Contributors, and members of the broad Research parent gain no merge or maintenance rights solely from #14's optional-review policy. Their existing contribution paths remain available.
- Named maintenance actors may create and maintain permitted non-default branches and tags, and merge eligible PRs. This proposal grants no direct default-branch push, deletion or force-push capability, and no authority to move protected tags or bypass required validation.
- Keep the PR requirement, required status checks, protected history, deletion/force-push protection and all unrelated conditions. An actor exemption that also bypasses those safeguards is **not** an implementation of this target. Separate enforceable rules must preserve them; if GitHub cannot express the combination, record the limitation and leave enforcement unchanged.
- Apply #14's optional approval count/latest-push change only after this capability definition is accepted and preserved safeguards are verified. Local evidence, contract, security, legal and release acceptance remain independent of the optional peer-review rule.

Before any future authorized mutation, capture fresh grant/ruleset baselines and compare representative ordinary-maintainer, specialty-lead, shared-lead and contributor paths against this table. Verify both all six included repositories and excluded client/runtime repositories. Retain exact before/after rule IDs, check names, actor lists and timestamps privately where they expose access details. A synthetic matrix or configuration readback is not proof of real effective enforcement.

## Separate review-exception proposal

The owner selected **all changes in the six research-family repositories** for #14's scope. [The machine-readable proposal](../../proposals/research-review-exception.json) identifies the six current review rules and proposes only approval count `1 → 0` and latest-push approval `true → false`. It is a description, not an executable settings writer. Its expected-before values must match a fresh read before any future application.

Approve the merge/branch/tag capability definition first. With approval count zero, authorized mergers can merge PRs from all contributor classes, including forks; the scope decision alone does not decide who gains that merge capability. Preserve PR requirements, required checks, history, deletion/force-push safeguards, tag boundaries and every unaffected condition/actor. GitHub configuration cannot substitute for local contract, evidence, security or legal acceptance.

After separately authorized settings changes, verify included and excluded repositories, representative ordinary maintainers/leads/contributors, before/after effective permissions, exact rule IDs, and real behavior. Host configuration readback and fixture tests do not establish that behavioral result. No such change or behavioral enforcement claim is made here.
