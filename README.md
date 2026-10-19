# Pick Your AI organization files

This repository maintains the public [Pick Your AI organization profile](https://github.com/Pick-Your-AI) and shared community guidance.

| File | Purpose |
| --- | --- |
| [profile/README.md](profile/README.md) | Public organization profile |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards, reporting, and enforcement |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Organization-wide access, branch, review and merge rules |

Web application work belongs in [pick-your-ai-website](https://github.com/Pick-Your-AI/pick-your-ai-website). Research, evidence, and shared contracts belong in [pick-your-ai-research](https://github.com/Pick-Your-AI/pick-your-ai-research). The Android and Apple/iOS planning clients live in [pick-your-ai-android](https://github.com/Pick-Your-AI/pick-your-ai-android) and [pick-your-ai-apple](https://github.com/Pick-Your-AI/pick-your-ai-apple), and funding and sustainability work lives in [pick-your-ai-sustainability](https://github.com/Pick-Your-AI/pick-your-ai-sustainability). Follow each repository's contribution guide for its workflow and required checks.

Contributor recognition and leaderboard delivery planning belong in [pick-your-ai-leaderboard](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard), with the [delivery project](https://github.com/orgs/Pick-Your-AI/projects/6) and [program](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard/issues/1) tracking the work. The repository and project describe planned capabilities; their creation does not establish a deployed leaderboard. Link to the leaderboard repository for current metric definitions and workflow.

## Updating these files

Submit changes through a branch and pull request against main. Check Markdown rendering and link destinations, and verify product-status claims against the current application and research documentation. Keep the preview's synthetic-data disclosure visible. Link to repository guidance instead of duplicating changing ownership, Project fields, or validation commands here.

The Code of Conduct can serve as a default for organization repositories without their own copy. Changes to it affect shared community guidance and should be reviewed with that scope in mind.

## Assets

[`assets/`](assets/) contains the light and dark hero illustrations, editable SVG banners, seven transparent tier icons, six repository social-preview cards with half-size WebP thumbnails for the profile grid (`repo-cards/thumbs/`), a 500×500 organization avatar rendered from the favicon (`avatar-500.png`, full-bleed teal so it crops cleanly), the canonical favicon and a hand-built divider. These are illustrations, not screenshots or evidence of product capabilities. [`assets/PROMPTS.md`](assets/PROMPTS.md) records the exact generation prompts, tool/model disclosure, date and selected variants. [`assets/build_assets.py`](assets/build_assets.py) resizes the generated sources and composes real text with Pillow; it uses Windows Segoe UI fonts for the social cards and pngquant for PNG optimization. The banners embed compact WebP versions of the matching heroes. [`assets/review/`](assets/review/) holds verification evidence and clearly labelled before/after profile screenshots.

Brand tokens match the application's `src/styles/index.css`: teal 50 `#f0fdfa`, 300 `#5eead4`, 500 `#14b8a6`, 600 `#0d9488`, 700 `#0f766e` (primary), 800 `#115e59`, 950 `#042f2e`; amber 400 `#fbbf24` (signature dot), 500 `#f59e0b`, 600 `#d97706`. Use system sans for UI and monospace for technical labels. The mark is copied unchanged from the application's `public/favicon.svg`; never regenerate it with an image model.

Maintainer-only follow-ups, outside the files in this repository:

- Upload `assets/avatar-500.png` as the organization avatar in organization settings (GitHub has no API for this).
- Upload each matching `assets/repo-cards/*.png` under that repository's **Settings → Social preview** (`github.png` belongs to `.github`).
- Review the organization website (`https://pickyour.ai`) and description in organization settings. Keep the preview and synthetic-data qualifications in any description.

No avatar, social preview, repository metadata or organization setting is changed by committing these files.
