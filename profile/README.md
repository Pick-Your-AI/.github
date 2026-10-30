<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../assets/banner-light.svg">
    <img src="../assets/banner-light.svg" alt="Pick Your AI — Build a compatible AI stack, part by part. Illustrated model chip, GPU, database, tool block and guardrail shield in a modular tray." width="1600">
  </picture>
</p>

<p align="center">
  <a href="https://pickyour.ai"><img src="https://img.shields.io/badge/Try_the_preview-0f766e?style=for-the-badge" alt="Try the preview"></a>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/1"><img src="https://img.shields.io/badge/Research_board-334155?style=for-the-badge" alt="Research board"></a>
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contribute-334155?style=for-the-badge" alt="Contribute"></a>
</p>

<p align="center">
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-website">Application</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-research">Research</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-android">Android</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-apple">Apple/iOS</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-leaderboard">Leaderboard plan</a> ·
  <a href="https://github.com/Pick-Your-AI/pick-your-ai-website/blob/main/LICENSE">MIT licence</a>
</p>

> [!NOTE]
> **Preview status.** The application is available as a preview. Its components, prices, and compatibility results use synthetic demonstration data. The real component catalog is still being researched; preview results are not validated recommendations or current vendor quotes.

## Get involved

Explore the [volunteer hub](https://github.com/Pick-Your-AI/pick-your-ai-volunteers) for public-safe applications, opportunities, staffing readiness and onboarding. Pick Your AI intends to pursue US 501(c)(3) status; this volunteer program does not establish incorporation, tax exemption or tax-deductible donation eligibility.


<table>
<tr>
<td width="33%" valign="top">
<h3>Research</h3>
<ol>
<li>Read the <a href="https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/CONTRIBUTING.md">contribution guide</a></li>
<li>Choose an existing issue on the <a href="https://github.com/orgs/Pick-Your-AI/projects/1">research board</a></li>
<li>Follow the <a href="https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_WORKFLOW.md">submission workflow</a></li>
</ol>
<sub>Preserve the issue's deliverable path and coordinate with its live assignees. Keep incomplete findings in notes; never invent facts to fill a schema.</sub>
</td>
<td width="33%" valign="top">
<h3>Application</h3>
<ol>
<li>Read the <a href="https://github.com/Pick-Your-AI/pick-your-ai-website/blob/main/CONTRIBUTING.md">application contribution guide</a></li>
<li>Link implementation work to its research counterpart</li>
<li>Propose contract changes in <a href="https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40">research issue #40</a></li>
</ol>
</td>
<td width="33%" valign="top">
<h3>Recognition</h3>
<ol>
<li>Start with the <a href="https://github.com/orgs/Pick-Your-AI/projects/6">leaderboard delivery project</a></li>
<li>Read the <a href="https://github.com/Pick-Your-AI/pick-your-ai-leaderboard">repository guidance</a></li>
</ol>
<sub>Contributions remain in their owning repositories; leaderboard work links to that evidence.</sub>
</td>
</tr>
</table>

Everyone follows our [Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md). Report security concerns privately through the affected repository's security policy; the research repository's [security policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/SECURITY.md) describes its process. Do not post credentials, personal data, or vulnerability details in public issues.

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

<table>
<tr>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/pick-your-ai-website"><img src="../assets/repo-cards/thumbs/pickyour.ai.webp" width="260" alt="pickyour.ai repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/pick-your-ai-website">pick-your-ai-website</a></b><br>
<sub>Application, interface, tests, and data integration</sub>
</td>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/pick-your-ai-research"><img src="../assets/repo-cards/thumbs/pick-your-ai-research.webp" width="260" alt="pick-your-ai-research repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/pick-your-ai-research">pick-your-ai-research</a></b><br>
<sub>Evidence, decision records, catalog and pricing proposals, and shared contracts</sub>
</td>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/pick-your-ai-leaderboard"><img src="../assets/repo-cards/thumbs/pick-your-ai-leaderboard.webp" width="260" alt="pick-your-ai-leaderboard repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/pick-your-ai-leaderboard">pick-your-ai-leaderboard</a></b><br>
<sub>Contributor recognition, metric definitions, and leaderboard delivery planning</sub>
</td>
</tr>
<tr>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/pick-your-ai-android"><img src="../assets/repo-cards/thumbs/pick-your-ai-android.webp" width="260" alt="pick-your-ai-android repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/pick-your-ai-android">pick-your-ai-android</a></b><br>
<sub>Android planning client: scope, contribution guidance, and delivery planning</sub>
</td>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/pick-your-ai-apple"><img src="../assets/repo-cards/thumbs/pick-your-ai-apple.webp" width="260" alt="pick-your-ai-apple repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/pick-your-ai-apple">pick-your-ai-apple</a></b><br>
<sub>Apple/iOS planning client: scope, contribution guidance, and delivery planning</sub>
</td>
<td width="33%" valign="top">
<a href="https://github.com/Pick-Your-AI/.github"><img src="../assets/repo-cards/thumbs/github.webp" width="260" alt=".github repository card"></a><br>
<b><a href="https://github.com/Pick-Your-AI/.github">.github</a></b><br>
<sub>Organization profile and community defaults</sub>
</td>
</tr>
</table>

Application, research and leaderboard work have separate workflows. Funding, grants and sustainability work is coordinated in [pick-your-ai-sustainability](https://github.com/Pick-Your-AI/pick-your-ai-sustainability), tracked in [Project 7](https://github.com/orgs/Pick-Your-AI/projects/7). The application demonstrates selection with synthetic fixtures. Research gathers sourced facts, dated prices and proposed compatibility rules under a versioned shared contract. **Merged research does not automatically become production catalog data.**

The mobile repositories are early-stage and unreleased. Android has a Kotlin/JVM core and an unsigned debug diagnostic; Apple/iOS has an unsigned SwiftUI app with local drafts. Neither has a signed installable product, production backend or release yet.

### Project boards

<p>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/1"><img src="https://img.shields.io/badge/Research-T0%E2%80%93T6_workstreams-0f766e?style=for-the-badge&labelColor=334155" alt="AI Builder Research: T0–T6 research workstreams and decision records"></a>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/2"><img src="https://img.shields.io/badge/Research-Market_intelligence-0f766e?style=for-the-badge&labelColor=334155" alt="Market Research and Competitive Intelligence: market and competitor research"></a>
</p>
<p>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/3"><img src="https://img.shields.io/badge/Delivery-Website-115e59?style=for-the-badge&labelColor=334155" alt="Website Implementation: the pickyour.ai builder"></a>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/4"><img src="https://img.shields.io/badge/Plan-Android-115e59?style=for-the-badge&labelColor=334155" alt="Android Application Delivery: Android client delivery plan"></a>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/5"><img src="https://img.shields.io/badge/Plan-Apple%2FiOS-115e59?style=for-the-badge&labelColor=334155" alt="Apple/iOS Application Delivery: Apple/iOS client delivery plan"></a>
  <a href="https://github.com/orgs/Pick-Your-AI/projects/6"><img src="https://img.shields.io/badge/Plan-Contributor_leaderboard-115e59?style=for-the-badge&labelColor=334155" alt="Contributor Leaderboard Delivery: contributor recognition delivery plan"></a>
<a href="https://github.com/orgs/Pick-Your-AI/projects/7"><img src="https://img.shields.io/badge/Plan-Sustainability-115e59?style=for-the-badge&labelColor=334155" alt="Funding, Grants and Sustainability: funding and support research and pipeline"></a>
</p>

## Contributor recognition · Planned

The [contributor leaderboard project](https://github.com/orgs/Pick-Your-AI/projects/6) and its [delivery program](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard/issues/1) plan public, source-linked recognition across pull requests, code changes, reviews, issues, triage, documentation, research, and maintenance. The plan defines **98 metrics, 20 epics, 112 work packages and 474 implementation checklist tasks**. These are planned capabilities, not a deployed leaderboard. Metric availability, historical coverage, and limitations must be visible, and lines of code do not establish contribution quality.

The [leaderboard repository](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) owns its metric definitions, delivery workflow, and correction process. Existing repository contribution and review rules continue to determine whether work is accepted.

<img src="../assets/divider.svg" width="1200" alt="Teal closing divider with an amber node">
