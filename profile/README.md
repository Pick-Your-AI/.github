# Pick Your AI

**Build a compatible AI stack, part by part.**

[Try the preview](https://pickyour.ai) · [Application](https://github.com/Pick-Your-AI/pickyour.ai) · [Research](https://github.com/Pick-Your-AI/pick-your-ai-research) · [Research board](https://github.com/orgs/Pick-Your-AI/projects/1)

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
| [.github](https://github.com/Pick-Your-AI/.github) | Organization profile and community defaults |

## How to take part

- **Research:** start with the [contribution guide](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/CONTRIBUTING.md), choose an existing issue on the [research board](https://github.com/orgs/Pick-Your-AI/projects/1), and follow the [submission workflow](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_WORKFLOW.md). Preserve the issue's deliverable path and coordinate with its live assignees. Keep incomplete findings in notes; never invent facts to fill a schema.
- **Application:** follow the [application contribution guide](https://github.com/Pick-Your-AI/pickyour.ai/blob/main/CONTRIBUTING.md) and link implementation work to its research counterpart. Contract changes go through [research issue #40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40).
- **Community:** follow our [Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md).

For security concerns, follow the affected repository's security policy and use a private reporting channel. The research repository's [security policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/SECURITY.md) describes its reporting process. Do not post credentials, personal data, or vulnerability details in public issues.
