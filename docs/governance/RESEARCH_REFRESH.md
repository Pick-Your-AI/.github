# Research refresh proposal

Status: proposed procedure and intervals for review under [#15](https://github.com/Pick-Your-AI/.github/issues/15). No recurring job is activated and no numerical threshold is accepted by this document. Existing research evidence and contract requirements remain authoritative.

The initial proposed coverage is the six research-family repositories: Research, Sustainability, Applications, Papers, Catalog Pipeline, and Datasets. Market and research-relevant Cloud Agents artifacts are proposed extensions requiring the affected owners' decision. Use live issue assignees and accepted domain roles; do not assign work automatically to everyone with repository access.

Research [#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41), the repository's evidence/freshness decisions, and tier-owner ADRs remain the sources for artifact-specific policy. These organization-level intervals do not override accepted domain policy or impose a universal expiry on version-pinned evidence.

| Artifact | Proposed recheck interval | Event that prompts earlier review |
| --- | --- | --- |
| Current prices, availability and service limits | 30 days | Vendor change, unavailable offer, billing discrepancy |
| Capabilities and version-dependent measurements | 90 days | New evaluated version, changed methodology, contradictory result |
| Papers metadata | 180 days; proposed retraction recheck every 30 days | Retraction, correction, withdrawal |
| Dataset rights, access and availability | 90 days | Licence change, removal, rights dispute |
| Funding opportunities | 14 days and within 7 days before a deadline | Deadline, eligibility or sponsor change |
| Market observations (if coverage is accepted) | 60 days | Launch, acquisition or material correction |

## Perform a refresh

1. Start from the existing issue, decision record and exact artifact version. Preserve assignees, triage and original evidence. Identify the claim being rechecked and its affected consumers.
2. Revisit the primary source using an allowed access route. Record actual source access date, source/version locator, method, conditions, units and uncertainty in the existing research format. Do not replace an original measurement date with a later web access date.
3. Compare claim-level facts. Record unchanged, changed, superseded, withdrawn or unverifiable findings. Keep the prior revision and explain the difference. A failed link is not proof a finding was false; a vendor statement is not an independent reproduction.
4. Validate using the owning repository's prescribed commands. Preserve the imported v1 contract; use existing fields according to [the contract mapping](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/CONTRACT_MAPPING.md). New fields or units require the [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40) versioning/owner process. Incomplete findings remain notes, not invented schema values.
5. Request affected owner/consumer review for changed interpretation, compatibility, rights or downstream use. Publish a scoped PR with source links and a clear description of remaining uncertainty. Notify consumers through their existing issue handoffs; this does not authorize deployment or a production catalog update.

## Failures and stale evidence

Record the last successful verification and the failed attempt separately. Preserve historical artifacts and rights restrictions. Flag current-state claims for review when their accepted domain threshold or a material event warrants it. Do not automatically delete old research, fabricate replacement measurements, convert unknown compatibility to pass, or relabel a vendor claim as independently reproduced.

For a retraction, rights concern, conflicting measurement or unavailable critical source, record the affected claim and consumers promptly, retain the historical citation, and follow [escalation](ESCALATION.md). Preserve uncertainty at every level. Do not silently route straight to the organization owner or publish restricted evidence.

Schema checks establish shape and references, not source truth, freshness, rights, scientific validity or runtime acceptance. Repeating research does not prove its correctness. The [#14](https://github.com/Pick-Your-AI/.github/issues/14) scope decision covers all changes in the six research-family repositories, but the enforcement change is **not applied** by this proposal. Current required reviews and checks still apply.

Approval of coverage/intervals and recurring activation are separate decisions. A future activation PR must specify credential scope, responsible role acceptance, output destination, triggers/fallback, failure handling and rollback, and include real verification receipts before calling it operational.
