# Profile verification — 2026-10-16

## Screenshots and scope

- `before-light.webp` / `before-dark.webp`: the actual public organization profile at `https://github.com/Pick-Your-AI`, baseline main `6f95de942984ad108b2a127413f7ec11c2a5c660`.
- `after-light.webp` / `after-dark.webp`: browser-only previews in that same live organization page's profile container, using GitHub's rendered HTML from `design/profile-overhaul`. The HTML was replaced only in the local browser DOM; nothing was published to the org profile. Asset URLs were pinned to `9c6695ca3bec8bc42268638c6db8962061d83d18` to avoid stale branch-image caches. That commit contains the final image bytes.
- `camo.webp`: the dark SVG banner rendered through GitHub's camo proxy. A commit-pinned jsDelivr URL was passed through the GitHub Markdown API to obtain a real camo URL (GitHub's own raw image URLs bypass camo). Both the embedded WebP and SVG text visibly render. No fallback is needed.

Screenshots use headless Chromium via Docker Playwright MCP, 1440×1000 viewport, with the profile element captured at its full height. Theme checks set both the browser color preference and GitHub's document theme. Capture waits for the expected banner `currentSrc` and decoded images. WebP screenshot encoding: quality 85 before, 80 after. These are genuine browser captures, not generated images.

## Checks

- Both final Markdown files rendered successfully through `gh api markdown` with `mode=gfm` and `context=Pick-Your-AI/.github`. For file input, use `-F text=@profile/README.md`, not lowercase `-f`, which sends the path literally.
- Both READMEs were opened on github.com; the profile was additionally previewed in the actual org layout in both themes. All seven icons, the NOTE, divider and theme-specific banners render. `render-checks.json` records each loaded image's dimensions and selected source.
- At a 390 px viewport, the profile container's client/scroll widths were both 292 px, and body/viewport widths were both 390 px: no horizontal page overflow.
- The optional Mermaid diagram was omitted; the constraint examples remain prose. There is no Mermaid rendering claim to verify.
- `links.json`: all 19 distinct external destinations in the old/new profile and repository README returned HTTP 200 with unauthenticated curl GETs following redirects.
- `image-checks.json`: all 19 published SVG/PNG illustration and logo paths returned HTTP 200 at the final asset commit. Local relative paths also resolve from `profile/README.md`.
- Heroes: 1600×500; icons: 128×128 with actual alpha; repository cards: 1280×640. Every banner is below 400 KB and every icon below 60 KB. Total assets, including these screenshots and audit records, remain below 3 MB.
- Canonical favicon bytes match the application source at `dc66a9e269917ab7241c7d08fd0e7f2a2f039872`. Code of Conduct bytes match baseline exactly. All original destination URLs remain. [Facts audit](FACTS.md) lists every preserved claim and the two new public planning repos.

## Remaining manual checks

The default-branch organization profile cannot display this PR before merge. A maintainer should verify the newly published org profile in both themes after merge, including main-branch relative image resolution. No org settings, avatar, social previews or repository metadata were changed.

The built-in image tool did not expose its underlying model identifier or seed. That limitation is recorded in `../PROMPTS.md`; no model name has been guessed. Generation and asset review used the local calendar date above (America/New_York; later verification calls fall on October 17 UTC).
