# Organization charts

This directory publishes a **dated organizational snapshot**, not a live directory or an access-control policy.

The [2026-10-29 snapshot](snapshots/2026-10-29/) contains **91 teams**, captured at **2026-10-30T02:33:56.069534+00:00**. The directory date follows the original Eastern-time capture date; `team-snapshot.json` records the precise UTC timestamp.

- [Complete leadership chart — PNG](snapshots/2026-10-29/organization-complete.png) · [SVG](snapshots/2026-10-29/organization-complete.svg) · [Mermaid](snapshots/2026-10-29/organization-complete.mmd)
- [Actual GitHub team hierarchy — PNG](snapshots/2026-10-29/github-team-hierarchy.png) · [SVG](snapshots/2026-10-29/github-team-hierarchy.svg) · [Mermaid](snapshots/2026-10-29/github-team-hierarchy.mmd)
- [Download all charts and sources](snapshots/2026-10-29/organization-charts.zip)

The complete charts are 16,000 pixels wide. Use a vector export or an area chart to inspect team structure.

## Area charts

| Area | PNG | SVG | Mermaid |
| --- | --- | --- | --- |
| AI Builder | [PNG](snapshots/2026-10-29/area-ai-builder.png) | [SVG](snapshots/2026-10-29/area-ai-builder.svg) | [Source](snapshots/2026-10-29/area-ai-builder.mmd) |
| AI Papers & Index | [PNG](snapshots/2026-10-29/area-ai-papers-index.png) | [SVG](snapshots/2026-10-29/area-ai-papers-index.svg) | [Source](snapshots/2026-10-29/area-ai-papers-index.mmd) |
| AI Tools & Platforms | [PNG](snapshots/2026-10-29/area-ai-tools-platforms.png) | [SVG](snapshots/2026-10-29/area-ai-tools-platforms.svg) | [Source](snapshots/2026-10-29/area-ai-tools-platforms.mmd) |
| Catalog Pipeline | [PNG](snapshots/2026-10-29/area-catalog-pipeline.png) | [SVG](snapshots/2026-10-29/area-catalog-pipeline.svg) | [Source](snapshots/2026-10-29/area-catalog-pipeline.mmd) |
| Cloud Agents | [PNG](snapshots/2026-10-29/area-cloud-agents.png) | [SVG](snapshots/2026-10-29/area-cloud-agents.svg) | [Source](snapshots/2026-10-29/area-cloud-agents.mmd) |
| Datasets & Benchmarks | [PNG](snapshots/2026-10-29/area-datasets-benchmarks.png) | [SVG](snapshots/2026-10-29/area-datasets-benchmarks.svg) | [Source](snapshots/2026-10-29/area-datasets-benchmarks.mmd) |
| Funding, Grants & Sustainability | [PNG](snapshots/2026-10-29/area-funding-grants-sustainability.png) | [SVG](snapshots/2026-10-29/area-funding-grants-sustainability.svg) | [Source](snapshots/2026-10-29/area-funding-grants-sustainability.mmd) |
| Market & Competitive Intelligence | [PNG](snapshots/2026-10-29/area-market-competitive-intelligence.png) | [SVG](snapshots/2026-10-29/area-market-competitive-intelligence.svg) | [Source](snapshots/2026-10-29/area-market-competitive-intelligence.mmd) |
| Hardware & Infrastructure | [PNG](snapshots/2026-10-29/area-hardware-infrastructure.png) | [SVG](snapshots/2026-10-29/area-hardware-infrastructure.svg) | [Source](snapshots/2026-10-29/area-hardware-infrastructure.mmd) |
| Websites | [PNG](snapshots/2026-10-29/area-websites.png) | [SVG](snapshots/2026-10-29/area-websites.svg) | [Source](snapshots/2026-10-29/area-websites.mmd) |
| Mobile Apps | [PNG](snapshots/2026-10-29/area-mobile-apps.png) | [SVG](snapshots/2026-10-29/area-mobile-apps.svg) | [Source](snapshots/2026-10-29/area-mobile-apps.mmd) |
| Education | [PNG](snapshots/2026-10-29/area-education.png) | [SVG](snapshots/2026-10-29/area-education.svg) | [Source](snapshots/2026-10-29/area-education.mmd) |

## Reading the charts

- Only team names and hierarchy are displayed. Member identities, owners, membership counts and pending invitations are excluded.
- Leadership views place lead-maintainer teams above their areas for readability. They do not redefine GitHub parent-team settings; the actual hierarchy has a separate chart.
- Team membership, repository permissions, Project access, and accepted task ownership are different facts. These charts describe team hierarchy only.

## Reproducing and checking the snapshot

From `docs/organization/snapshots/2026-10-29`, run:

```sh
python -X utf8 build_sources.py
python -X utf8 render_charts.py
python -X utf8 validate.py
```

Rendering requires Python 3.10+, Node.js/npm and Chrome or Chromium. Set `CHROME_PATH` if browser discovery does not find your installation. The renderer uses Mermaid CLI **12.0.0**, writes a temporary browser configuration, and does not change GitHub. The frozen JSON input contains only team IDs, names, slugs, links, parent relationships and the capture timestamp. It excludes personal and invitation data. Set `MERMAID_CLI_PATH` to an existing Mermaid CLI 12.0.0 `src/cli.js` when npm executable resolution is unavailable. Rendering also rebuilds the ZIP from an explicit list of public artifacts; previews and temporary files are excluded. Rendering may vary with installed fonts.

The validator checks complete team coverage, stable IDs, actual hierarchy edges, the public field allowlist, team labels, team links, and PNG dimensions. Local validation does not establish any person's acceptance of an operational assignment. Fresh-VM validation was not run; the published artifacts were rendered and inspected locally on Windows.

## Refresh and prior work

This is a static publication. A future refresh must read all GitHub pages, reconcile current public team IDs/names and hierarchy, and retain the new capture timestamp. Do not publish member identities, owners, invitation details or membership counts in the public snapshot or its exports.

Prior work: [current public model PR #24](https://github.com/Pick-Your-AI/.github/pull/24) excludes rosters and pending invitations; this historical export follows the same privacy boundary. [Team/access documentation PR #9](https://github.com/Pick-Your-AI/.github/pull/9) and [dynamic routing/directory issue #17](https://github.com/Pick-Your-AI/.github/issues/17). This snapshot supplies chart artifacts; it does **not** implement the live resolver, scheduled refresh or cross-repository guidance required by #17. That issue remains open.
