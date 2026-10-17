<div align="center">

# Pick Your AI

**Build a compatible AI stack, part by part.**

[![Try the preview](https://img.shields.io/badge/try_the_preview-pickyour.ai-0f766e?style=for-the-badge)](https://pickyour.ai)
[![Research board](https://img.shields.io/badge/research-board-334155?style=for-the-badge)](https://github.com/orgs/Pick-Your-AI/projects/1)
[![License: MIT](https://img.shields.io/badge/license-MIT-d97706?style=for-the-badge)](https://github.com/Pick-Your-AI/pickyour.ai/blob/main/LICENSE)

[Application](https://github.com/Pick-Your-AI/pickyour.ai) · [Research](https://github.com/Pick-Your-AI/pick-your-ai-research) · [Android](https://github.com/Pick-Your-AI/pick-your-ai-android) · [Apple/iOS](https://github.com/Pick-Your-AI/pick-your-ai-apple) · [Contributor recognition](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard)

</div>

> **Preview status.** The application is available as a preview. Its components, prices, and compatibility results use synthetic demonstration data. The real component catalog is still being researched; preview results are not validated recommendations or current vendor quotes.

## What is Pick Your AI?

Pick Your AI is a web-based builder for assembling a complete AI solution the way a PC builder assembles a computer. Start with a workload and deployment mode, then choose models, infrastructure, and optional capabilities. The goal is to help people understand compatibility, costs, and tradeoffs, with evidence behind each recommendation. [PCPartPicker](https://pcpartpicker.com/list/) is a functional reference; Pick Your AI develops its own brand, interface, and code.

## The problem

Choosing an AI stack means juggling model licences, context limits, GPU memory, inference-engine support, hosting availability, retrieval components, tool permissions and pricing, and these choices constrain each other. A model may not fit a GPU, an engine may not support a format, a hosting region may not offer the hardware. We aim to make these relationships and their supporting evidence easier to inspect.

## How the configurator is intended to work

Users move through seven tiers. T3 to T5 are optional and can be left out entirely.

| Tier | Focus |
| --- | --- |
| T0 Configuration | Workload / use case and deployment mode (API, managed, self-hosted, hybrid) |
| T1 Model Selection | Provider, model, context window |
| T2 Infrastructure | Hosting, GPU / compute, inference engine |
| T3 Knowledge & Retrieval *(optional)* | Knowledge base, embeddings, vector database, RAG |
| T4 Agents & Integrations *(optional)* | Agent framework, tools and APIs, MCP servers, memory |
| T5 Training & Fine-Tuning *(optional)* | Training framework, compute, dataset, fine-tuned model |
| T6 Deployment & Operations | Guardrails, evaluation, deployment, monitoring, cost estimate |

The tiers are not a strict waterfall. Selections can constrain each other in both directions: a model affects GPU requirements, and GPU availability limits which models are options. The intended compatibility system re-checks affected selections when a component changes, and never treats unknown compatibility as compatible.

## What we are doing now

Application development and research have separate workflows. The application demonstrates the selection experience with synthetic fixtures. Research gathers sourced component facts, dated prices, and proposed compatibility rules under a versioned shared contract. Merged research does not automatically become production catalog data.

| Repository | Purpose |
| --- | --- |
| [pickyour.ai](https://github.com/Pick-Your-AI/pickyour.ai) | Application, interface, tests, and data integration |
| [pick-your-ai-research](https://github.com/Pick-Your-AI/pick-your-ai-research) | Evidence, decision records, catalog and pricing proposals, and shared contracts |
| [pick-your-ai-android](https://github.com/Pick-Your-AI/pick-your-ai-android) | Android planning client: scope, contribution guidance, and delivery planning |
| [pick-your-ai-apple](https://github.com/Pick-Your-AI/pick-your-ai-apple) | Apple/iOS planning client: scope, contribution guidance, and delivery planning |
| [pick-your-ai-leaderboard](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) | Contributor recognition, metric definitions, and leaderboard delivery planning |
| [.github](https://github.com/Pick-Your-AI/.github) | Organization profile and community defaults |

The mobile repositories hold planning and guidance only; no mobile application has been built or released, and their framework decisions remain open.

### Project boards

| Board | Tracks |
| --- | --- |
| [AI Builder Research](https://github.com/orgs/Pick-Your-AI/projects/1) | T0–T6 research workstreams and decision records |
| [Market Research & Competitive Intelligence](https://github.com/orgs/Pick-Your-AI/projects/2) | Market and competitor research |
| [Website Implementation](https://github.com/orgs/Pick-Your-AI/projects/3) | The pickyour.ai builder |
| [Android Application Delivery](https://github.com/orgs/Pick-Your-AI/projects/4) | Android client delivery plan |
| [Apple/iOS Application Delivery](https://github.com/orgs/Pick-Your-AI/projects/5) | Apple/iOS client delivery plan |
| [Contributor Leaderboard Delivery](https://github.com/orgs/Pick-Your-AI/projects/6) | Contributor recognition delivery plan |

## Contributor recognition

The [contributor leaderboard project](https://github.com/orgs/Pick-Your-AI/projects/6) and its [delivery program](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard/issues/1) plan public, source-linked recognition across pull requests, code changes, reviews, issues, triage, documentation, research, and maintenance. The initial scope defines **98 metrics, 20 epics, 112 work packages, and 474 implementation checklist tasks**. These are planned capabilities; a live leaderboard has not been deployed by publishing the plan. Metric availability, historical coverage, and limitations must be visible, and lines of code do not establish contribution quality.

The [leaderboard repository](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) owns its metric definitions, delivery workflow, and correction process. Existing repository contribution and review rules continue to determine whether work is accepted.

## How to take part

- **Research:** start with the [contribution guide](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/CONTRIBUTING.md), choose an existing issue on the [research board](https://github.com/orgs/Pick-Your-AI/projects/1), and follow the [submission workflow](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_WORKFLOW.md). Preserve the issue's deliverable path and coordinate with its live assignees. Keep incomplete findings in notes; never invent facts to fill a schema.
- **Application:** follow the [application contribution guide](https://github.com/Pick-Your-AI/pickyour.ai/blob/main/CONTRIBUTING.md) and link implementation work to its research counterpart. Contract changes go through [research issue #40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40).
- **Contributor recognition:** start with the [leaderboard delivery project](https://github.com/orgs/Pick-Your-AI/projects/6) and [repository guidance](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard). Contributions remain in their owning repositories; leaderboard work links to that evidence.
- **Community:** follow our [Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md).

For security concerns, follow the affected repository's security policy and use a private reporting channel. The research repository's [security policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/SECURITY.md) describes its reporting process. Do not post credentials, personal data, or vulnerability details in public issues.
