<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../assets/banner-light.svg">
    <img src="../assets/banner-light.svg" alt="Pick Your AI — Build a compatible AI stack, part by part. Illustrated model chip, GPU, database, tool block and guardrail shield in a modular tray." width="1600">
  </picture>
</p>

<p align="center">
  <a href="https://pickyour.ai"><img src="https://img.shields.io/badge/Try_the_preview-0f766e?style=for-the-badge" alt="Try the preview"></a>
  <a href="https://github.com/Pick-Your-AI/pickyour.ai">Application</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-research">Research</a> ·
  <a href="https://github.com/orgs/Pick-Your-AI/projects/1">Research board</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-leaderboard">Leaderboard plan</a>
</p>

> [!NOTE]
> **Preview status.** The application is available as a preview. Its components, prices, and compatibility results use synthetic demonstration data. The real component catalog is still being researched; preview results are not validated recommendations or current vendor quotes.

## What is Pick Your AI?

Pick Your AI is a web-based builder for assembling a complete AI solution, like a PC build. Start with a workload and deployment mode, then choose models, infrastructure, and optional capabilities. The goal is to help people understand compatibility, costs, and tradeoffs, with evidence behind each recommendation.

[PCPartPicker](https://pcpartpicker.com/list/) is a functional reference; Pick Your AI develops its own brand, interface, and code.

## The problem

Model licences, context limits, GPU memory, inference-engine support, hosting availability, retrieval, tool permissions and pricing constrain each other. A model may not fit a GPU; an engine may not support a format; a hosting region may not offer the hardware. We aim to make these relationships and their evidence easier to inspect.

## Seven tiers

The configurator is intended to guide users through seven tiers. T3 to T5 are optional and can be left out entirely.

| | Tier | Focus |
| --- | --- | --- |
| <img src="../assets/tiers/t0.png" width="48" height="48" alt="Configuration sliders and dial"> | **T0** Configuration | Workload / use case and deployment mode (API, managed, self-hosted, hybrid) |
| <img src="../assets/tiers/t1.png" width="48" height="48" alt="Model chip"> | **T1** Model Selection | Provider, model, context window |
| <img src="../assets/tiers/t2.png" width="48" height="48" alt="GPU card"> | **T2** Infrastructure | Hosting, GPU / compute, inference engine |
| <img src="../assets/tiers/t3.png" width="48" height="48" alt="Outlined database and document"> | **T3** Knowledge & Retrieval *(optional)* | Knowledge base, embeddings, vector database, RAG |
| <img src="../assets/tiers/t4.png" width="48" height="48" alt="Outlined connected plug-in blocks"> | **T4** Agents & Integrations *(optional)* | Agent framework, tools and APIs, MCP servers, memory |
| <img src="../assets/tiers/t5.png" width="48" height="48" alt="Outlined gear and dataset stack"> | **T5** Training & Fine-Tuning *(optional)* | Training framework, compute, dataset, fine-tuned model |
| <img src="../assets/tiers/t6.png" width="48" height="48" alt="Guardrail shield with a pulse line"> | **T6** Deployment & Operations | Guardrails, evaluation, deployment, monitoring, cost estimate |

Tiers constrain each other in both directions: models affect GPU requirements, and GPU availability limits model choices. The intended compatibility system re-checks affected selections when a component changes, and never treats unknown compatibility as compatible.

## Where the work happens

| Repository | Purpose |
| --- | --- |
| [pickyour.ai](https://github.com/Pick-Your-AI/pickyour.ai) | Application, interface, tests, and data integration |
| [pick-your-ai-research](https://github.com/Pick-Your-AI/pick-your-ai-research) | Evidence, decision records, catalog and pricing proposals, and shared contracts |
| [pick-your-ai-leaderboard](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) | Contributor recognition, metric definitions, and leaderboard delivery planning |
| [pick-your-ai-android](https://github.com/Pick-Your-AI/pick-your-ai-android) | Android planning client |
| [pick-your-ai-apple](https://github.com/Pick-Your-AI/pick-your-ai-apple) | Apple / iOS planning client |
| [.github](https://github.com/Pick-Your-AI/.github) | Organization profile and community defaults |

Application, research and leaderboard work have separate workflows. The application demonstrates selection with synthetic fixtures. Research gathers sourced facts, dated prices and proposed compatibility rules under a versioned shared contract. **Merged research does not automatically become production catalog data.**

## Contributor recognition · Planned

The [contributor leaderboard project](https://github.com/orgs/Pick-Your-AI/projects/6) and its [delivery program](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard/issues/1) plan public, source-linked recognition across pull requests, code changes, reviews, issues, triage, documentation, research, and maintenance. The plan defines **98 metrics, 20 epics, 112 work packages and 474 implementation checklist tasks**. These are planned capabilities, not a deployed leaderboard. Metric availability, historical coverage, and limitations must be visible, and lines of code do not establish contribution quality.

The [leaderboard repository](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) owns its metric definitions, delivery workflow, and correction process. Existing repository contribution and review rules continue to determine whether work is accepted.

## Get involved

- **Research:** start with the [contribution guide](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/CONTRIBUTING.md), choose an existing issue on the [research board](https://github.com/orgs/Pick-Your-AI/projects/1), and follow the [submission workflow](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_WORKFLOW.md). Preserve the issue's deliverable path and coordinate with its live assignees. Keep incomplete findings in notes; never invent facts to fill a schema.
- **Application:** follow the [application contribution guide](https://github.com/Pick-Your-AI/pickyour.ai/blob/main/CONTRIBUTING.md) and link implementation work to its research counterpart. Contract changes go through [research issue #40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40).
- **Recognition:** start with the [leaderboard delivery project](https://github.com/orgs/Pick-Your-AI/projects/6) and [repository guidance](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard). Contributions remain in their owning repositories; leaderboard work links to that evidence.
- **Community:** follow our [Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md).

For security concerns, follow the affected repository's security policy and use a private reporting channel. The research repository's [security policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/SECURITY.md) describes its reporting process. Do not post credentials, personal data, or vulnerability details in public issues.

<img src="../assets/divider.svg" width="1200" alt="Teal closing divider with an amber node">
