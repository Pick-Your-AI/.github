# Pick Your AI

**Building the PCPartPicker for AI: discover, compare, configure and validate compatible AI stacks.**

> **Status: research and planning.** AI Builder does not exist yet as a product. Everything below describes what we are researching and intend to build.

## What is AI Builder?

AI Builder is a planned web-based tool for assembling a complete AI solution the way a PC builder assembles a computer. Instead of picking a CPU, motherboard and GPU, you choose a workload, a deployment mode, a model, infrastructure, retrieval, agents, training and operations components. The tool would check that the choices work together, estimate costs, and let you save, share and compare configurations. [PCPartPicker](https://pcpartpicker.com/list/) is a functional reference only; AI Builder will have its own brand, interface and code.

## The problem

Choosing an AI stack means juggling model licences, context limits, GPU memory, inference-engine support, hosting availability, retrieval components, tool permissions and pricing, and these choices constrain each other. A model may not fit a GPU, an engine may not support a format, a hosting region may not offer the hardware. There is no single place that checks these relationships with evidence.

## How the configurator is intended to work

Users move through seven tiers. T3 to T5 are optional and can be left out entirely.

| Tier | Focus |
|---|---|
| T0 Configuration | Workload / use case and deployment mode (API, managed, self-hosted, hybrid) |
| T1 Model Selection | Provider, model, context window |
| T2 Infrastructure | Hosting, GPU / compute, inference engine |
| T3 Knowledge & Retrieval *(optional)* | Knowledge base, embeddings, vector database, RAG |
| T4 Agents & Integrations *(optional)* | Agent framework, tools and APIs, MCP servers, memory |
| T5 Training & Fine-Tuning *(optional)* | Training framework, compute, dataset, fine-tuned model |
| T6 Deployment & Operations | Guardrails, evaluation, deployment, monitoring, cost estimate |

The tiers are not a strict waterfall. Selections can constrain each other in both directions: a model affects GPU requirements, and GPU availability limits which models are options. The planned compatibility system is dependency-aware: when you add, remove or change a component, everything it touches is re-checked, and unknown compatibility is never treated as compatible.

## What we are doing now

We are gathering evidence and defining the shared data contract the future application will use: component catalogs, compatibility rules, pricing and sources, with every claim marked as fact, estimate, assumption or unverified.

- **Research repository:** [Pick-Your-AI/pick-your-ai-research](https://github.com/Pick-Your-AI/pick-your-ai-research)
- **Project board:** [AI Builder Research](https://github.com/orgs/Pick-Your-AI/projects/1)

## How to take part

1. Read the research repository's `README.md` and `CONTRIBUTING.md`.
2. Pick an open research issue on the project board, or propose a new one using the issue template.
3. Submit findings by pull request with sources and dates, following the repository's research workflow.

Security concerns can be reported privately as described in the research repository's `SECURITY.md`.
