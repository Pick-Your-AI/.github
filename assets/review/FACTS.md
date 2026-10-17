# Profile facts audit

Baseline: `.github` main `6f95de942984ad108b2a127413f7ec11c2a5c660`. Reviewed 2026-10-16. Each item below covers a claim or instruction in the old profile. No substantive claim or destination was removed.

- [x] **Kept verbatim:** application available as a preview; components, prices and compatibility results use synthetic demonstration data; real catalog still being researched; results are not validated recommendations or current vendor quotes. Now a visible NOTE immediately under navigation.
- [x] **Faithfully tightened:** web-based builder for a complete AI solution, analogous to a PC build; start with workload and deployment mode, then models, infrastructure and optional capabilities.
- [x] **Kept:** compatibility, costs and tradeoffs with evidence behind recommendations are the goal, not a claim that the preview supplies validated recommendations.
- [x] **Kept verbatim:** PCPartPicker is a functional reference; own brand, interface and code. Original PCPartPicker destination retained.
- [x] **Faithfully tightened:** model licences, context limits, GPU memory, inference-engine support, hosting availability, retrieval components, tool permissions and pricing constrain each other.
- [x] **Kept:** a model may not fit GPU memory; an engine may not support a format; a hosting region may not offer hardware; aim is to make relationships and evidence inspectable.
- [x] **Kept:** configurator describes intended behavior, seven tiers, T3–T5 optional and can be omitted entirely.
- [x] **Kept verbatim:** T0 workload/use case and API, managed, self-hosted or hybrid deployment.
- [x] **Kept verbatim:** T1 provider, model and context window.
- [x] **Kept verbatim:** T2 hosting, GPU/compute and inference engine.
- [x] **Kept verbatim:** optional T3 knowledge base, embeddings, vector database and RAG.
- [x] **Kept verbatim:** optional T4 agent framework, tools/APIs, MCP servers and memory.
- [x] **Kept verbatim:** optional T5 training framework, compute, dataset and fine-tuned model.
- [x] **Kept verbatim:** T6 guardrails, evaluation, deployment, monitoring and cost estimate.
- [x] **Faithfully tightened:** tiers are not a one-way waterfall; model and GPU selections constrain each other in both directions.
- [x] **Kept verbatim:** intended compatibility system re-checks affected selections when a component changes and never treats unknown compatibility as compatible.
- [x] **Kept:** separate application/research workflows; application selection experience uses synthetic fixtures. Added explicit separation from leaderboard work.
- [x] **Kept:** research gathers sourced component facts, dated prices and proposed compatibility rules under a versioned shared contract; merged research does not automatically become production catalog data.
- [x] **Kept verbatim:** application repository owns application/interface/tests/data integration; research repository owns evidence/decision records/catalog and pricing proposals/shared contracts; leaderboard repository owns recognition/metric definitions/delivery planning; `.github` owns profile/community defaults.
- [x] **Verified and retained:** 98 metric definitions, 20 epics, 112 work packages, 474 implementation checklist tasks. Source: [leaderboard README at 37398771](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard/blob/37398771e8f1064da130e84e8f3cb40c024aaa98/README.md). These are planning-baseline counts; not independently counted production functionality.
- [x] **Kept:** Project 6 and issue #1 plan public, source-linked recognition across PRs, code changes, reviews, issues, triage, documentation, research and maintenance.
- [x] **Kept and made prominent:** capabilities are planned, not a deployed leaderboard; publishing the plan does not establish a live service. The upstream README explicitly confirms the application, collector and public service remain planned.
- [x] **Kept verbatim:** metric availability, historical coverage and limitations must be visible; lines of code do not establish contribution quality.
- [x] **Kept verbatim:** leaderboard repository owns metric definitions, delivery workflow and correction process; existing repository contribution/review rules determine acceptance.
- [x] **Kept verbatim:** research contributors use CONTRIBUTING, an existing Project 1 issue and RESEARCH_WORKFLOW; preserve deliverable path; coordinate with live assignees; keep incomplete findings in notes; never invent facts to fill a schema.
- [x] **Kept verbatim:** application contributors use its contribution guide and link work to the research counterpart; contract changes go through research issue #40.
- [x] **Kept verbatim:** recognition work starts from the delivery project and repo guidance; contributions remain in owning repos; leaderboard links to the evidence.
- [x] **Kept verbatim:** follow Code of Conduct; for security use affected repo policy and a private channel; research SECURITY describes its process; do not put credentials, personal data or vulnerability details in public issues.
- [x] **Verified additions:** Android and Apple repositories are public in the organization REST inventory. Their current READMEs say planning clients with contribution/scope guidance only and no implementation, build toolchain, backend or release. The new rows and social cards say planning.
- [x] **Integrated from PR #4 (head `1babf20`):** fuller Android and Apple/iOS planning descriptions; statement that no mobile application has been built or released and framework decisions remain open; six-Project board table (titles and purposes as written in #4); MIT licence navigation (as a text link rather than a badge). Added a `Contribute` navigation link to the existing research contribution guide (an in-page anchor was not used because heading anchors on the organization page are unverified). Project URLs and the licence URL were re-checked on 2026-10-17.
- [x] **Presentation pass (2026-10-17, after #4 and #5 merged):** header navigation split into three primary buttons (preview, research board, contribute) and one text-link row; Get involved moved directly below the preview note and laid out as Research, Application and Recognition cards with the same links and rules; the Code of Conduct and security guidance kept verbatim in substance below it; repositories shown as a three-column grid of their existing social-preview cards with the same purpose text; Project boards shown as grouped badges whose alt text keeps each board's full title and purpose. No destination, status qualification or count was removed.
- [x] **Unchanged policy:** `CODE_OF_CONDUCT.md` byte-for-byte identical to baseline.

Presentation-only omissions: the optional Mermaid diagram was not introduced because the three constraint examples fit in one paragraph; redundant section labels were shortened. All original destination URLs remain.
