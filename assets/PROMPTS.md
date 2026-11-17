# Image generation record

Generated 2026-10-16 with Codex built-in `image_gen.imagegen`. The tool does not expose a model identifier; model: not reported (do not infer an API model). All illustrations are conceptual, not product evidence. Text and the canonical logo are composed separately.

Hero B was selected over A: clearer silhouettes, calmer negative space, exactly one amber indicator. Light hero is an edit of B. Android variant 2 replaces a gold-contact draft. All other outputs use variant 1. Inspected all outputs for text, trademarks, palette, composition and artifacts; final dimensions and alpha checked after optimization.

### Output mapping and reproduction

| Output | Exact prompt below | Selection |
| --- | --- | --- |
| `hero-dark.png` | heroB | B (A rejected: extra gold accents) |
| `hero-light.png` | heroLight | 1, edit target is heroB |
| `tiers/t0.png`–`tiers/t6.png` | t0–t6 respectively | 1 each |
| `repo-cards/pickyour.ai.png` | cardApplication | 1 |
| `repo-cards/pick-your-ai-research.png` | cardResearch | 1 |
| `repo-cards/pick-your-ai-leaderboard.png` | cardLeaderboard | 1 |
| `repo-cards/github.png` | cardGithub | 1 |
| `repo-cards/pick-your-ai-android.png` | cardAndroid | 2 (1 rejected: gold contacts) |
| `repo-cards/pick-your-ai-apple.png` | cardApple | 1 |

The seven icon calls used `transparent_background: true`; other calls used `false`. heroLight used heroB as its referenced image. Generation is nondeterministic and the built-in tool exposes neither a model identifier nor a seed. Do not claim bit-for-bit regeneration from the prompts.

`build_assets.py` records each selected source filename. To reproduce postprocessing from the original generations, run `python assets/build_assets.py SOURCE_DIRECTORY PNGQUANT_PATH` (Python, Pillow 12.2.0 and Segoe UI fonts). For newly generated replacements, update the source IDs first. Originals remain in the generation store; they are not duplicated into this lightweight repository.

Postprocessing: Lanczos resize to 1600×500 heroes, 128×128 transparent icons, 1280×640 cards. Cards receive real Segoe UI text through Pillow. PNGs use pngquant 2.17.0 with `--quality=65-85 --speed=1 --strip`; icons retain RGBA with Pillow optimization. The portable Windows binary was obtained from [pngquant's official site](https://pngquant.org/) because no pngquant, oxipng or cwebp was preinstalled. No optimizer binary is committed.

`banner-dark.svg` and `banner-light.svg` are hand-composed wrappers, not additional image generations: each embeds a WebP encoding (Pillow quality 90, method 6) of the matching optimized hero, then adds canonical favicon geometry and real system-font SVG text. `favicon.svg` is copied unchanged from [pickyour.ai at dc66a9e2](https://github.com/Pick-Your-AI/pickyour.ai/blob/dc66a9e269917ab7241c7d08fd0e7f2a2f039872/public/favicon.svg). `divider.svg` is hand-built. `review/*.webp` are browser screenshots, not generated illustrations.

## heroA

```text
Use case: stylized-concept. Create a text-free wide editorial hero illustration for Pick Your AI, variant A. Output landscape 1600x500 if possible, 3.2:1 composition. Precise engineered friendly isometric modular AI stack parts: one model microchip, one GPU expansion card, one database cylinder, one plug-in tool block, one guardrail shield. All five recognizable abstract unbranded parts slot into a layered low-profile tray on the RIGHT two thirds. Left third calm empty space for later typeset wordmark. Subtle blueprint grid. Teal surfaces strictly #0f766e #115e59 #14b8a6 #5eead4, pale highlights #f0fdfa, one small amber #fbbf24 highlight echoing a signature dot. Deep background gradient #042f2e to #0b1f1e. Soft upper-left light, clean bevels, restrained orthographic geometry, crisp high quality illustration. No text, lettering, numbers, logos, trademarks, UI, screenshots, robots, brains, faces, purple, or neural-net webs.
```

## heroB

```text
Use case: stylized-concept. Wide 1600x500 text-free hero variant B. Precise engineered friendly isometric modular AI stack: five abstract unbranded parts (model microchip, GPU expansion card, database cylinder, plug-in/tool block, guardrail shield) slot into one layered tray. All objects on RIGHT two thirds, quiet empty LEFT third for later wordmark. Clean simplified matte machined geometry, orthographic camera, soft upper-left light. Subtle low-contrast blueprint grid. Teal surfaces #0f766e #115e59 #14b8a6 #5eead4 with #f0fdfa highlights. Exactly ONE small amber #fbbf24 circular indicator; all contacts and edges teal, no other gold accents. Deep background #042f2e to #0b1f1e. Crisp elegant restrained illustration with generous breathing room. No text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, faces, purple, neon glow or neural webs.
```

## heroLight

```text
Edit the referenced hero illustration to create its LIGHT THEME companion. Keep identical five objects, tray, camera, layout, single amber indicator, left-third negative space, no text and no logos. Replace dark background with exact pale mint #f0fdfa and very subtle #5eead4 blueprint lines. Give tray and parts lighter teal matte surfaces #0f766e #14b8a6 #5eead4 with deep #115e59 edges. Soft upper-left studio lighting and gentle shadows. Keep the illustration clear and friendly, no neon, no new objects, no UI. Wide aspect 1600x500.
```

## t0

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: compact configuration control block with three physical sliders at different positions and one rotary dial. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t1

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: one model microchip, square raised blank central die on a compact substrate with chunky teal contacts along four edges. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t2

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: one compact GPU expansion card with a single large cooling fan and plain teal connector, no branding. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t3

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: one database cylinder beside one blank document sheet with a folded corner. This tier is optional: use an outlined teal construction with hollow/open faces and a clearly visible dashed teal perimeter around its isometric base. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t4

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: two connected plug-in blocks with a short physical cable and simple plug pins. This tier is optional: use an outlined teal construction with hollow/open faces and a clearly visible dashed teal perimeter around its isometric base. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t5

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: one large simple gear resting on a three-layer dataset tile stack, all tiles blank. This tier is optional: use an outlined teal construction with hollow/open faces and a clearly visible dashed teal perimeter around its isometric base. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## t6

```text
Use case: stylized-concept. Single isolated isometric icon for a technical AI stack tier, centered, square 128x128 target with generous transparent margin, actual transparent background. Subject: one upright solid guardrail shield with a single simple raised pale mint pulse line across its face. Clean matte machined teal geometry #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa. Orthographic 30-degree view, soft upper-left light, crisp large simple silhouette readable at 48px. No floor, no background, no text, letters, numbers, logos, trademarks, UI screenshots, glow, purple or amber. Friendly engineered style matching modular hardware illustration.
```

## cardApplication

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of a modular AI stack tray with model chip, GPU, database and tool block, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon.
```

## cardResearch

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of a research evidence tray with a database cylinder, three blank document plates and a magnifying lens, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon.
```

## cardLeaderboard

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of three equal-height contribution tiles linked to blank evidence documents, an abstract recognition medallion with blank center, no rankings, bars, scores or charts, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon.
```

## cardGithub

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of a community documentation tray with three interlocking blank rounded tiles and an upright open book with totally blank pages, abstract shared foundations, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon.
```

## cardAndroid

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of a generic unbranded small handheld slab with a completely blank dark glass face beside two modular model chips in a layered planning tray. No device logo or distinctive manufacturer details, no robot mascots, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon. Strict revision: all chip contacts, edges, and device buttons must be teal or pale mint, NEVER gold. Exactly one small circular amber dot on the tray. Use simplified illustrative block geometry, no photorealistic consumer device.
```

## cardApple

```text
Use case: stylized-concept. Text-free repository social card background, wide 1280x640. Precise engineered friendly isometric illustration of two generic unbranded rounded handheld slabs of different sizes, completely blank dark glass faces, beside a single model chip in a layered planning tray. No device logo or distinctive manufacturer details, no fruit emblems, no robot mascots, all on the right half, leaving left half and top-left calm empty for real text composed later. Matte teal #0f766e #115e59 #14b8a6 #5eead4, highlights #f0fdfa, one tiny amber #fbbf24 indicator. Background deep #042f2e to #0b1f1e with subtle blueprint grid. Soft upper-left light, clean bevels, no text, letters, numbers, logos, trademarks, UI, screenshots, robots, brains, purple or neon. Strict revision: all chip contacts, edges, and device buttons must be teal or pale mint, NEVER gold. Exactly one small circular amber dot on the tray. Use simplified illustrative block geometry, no photorealistic consumer device.
```

## assets/icon.png

- Date: 2026-10-30
- Tool and model: Codex built-in `image_gen` via codex-cli 0.164.0 / model: not reported (do not infer an API model)
- Seed: not supported
- Reference images: none
- Prompt: (verbatim, fenced)

```text
Use your image generation capability to create ONE image. Do not modify any other files.

NEON NIGHT REPO ICON · Pick-Your-AI/.github

Create one square 1024 × 1024 px image of a single repository glyph.
Use a simple geometric silhouette with a luminous outline and one accent spark.
Keep the background empty and the glyph inside the central 688 × 688 px square.
Size class WIDE: the glyph spans close to the full 688 px width and is about 430 to 560 px tall.

GLYPH: Organization profile card with stacked build slots. A rounded-rectangle profile card in outline. On the left of the card a plain circular avatar ring; on the right three short horizontal rounded bars stacked vertically with even gaps, like component slots in a build list. The bars and ring are empty outlines with no marks inside.
SPARK PLACEMENT: A small four-point spark at the top-right corner of the card, overlapping the outline slightly.
PALETTE: outline #0F766E, glow #14B8A6; one spark in #FBBF24.
The spark is the only filled shape and the only element in #FBBF24; keep the
glyph outline in #0F766E so the spark remains distinct at small sizes.

No text, letters, numbers, words, logos, brand marks, human figures or third-party IP.

Produce exactly one image.
The lock pass renders assets/icon.png as a flat glyph in the family's light-surface
inks, without a tile or glow. Do not render the repository name in the image.
NEGATIVE LIST: no tile, card background, frame or border around the glyph; no gradient background; no text of any kind (including inside the card, bars or avatar ring); no letters, numbers or symbols; no logos; no people or faces; no extra objects; no shadows beyond a soft glow; background must be a flat empty white (#FFFFFF) with nothing touching the edges.
ASPECT RATIO: square 1:1, 1024x1024.
STYLE: flat vector look. Perfectly flat solid fills and crisp anti-aliased edges only; no texture, grain, noise, paper effect, gradients, glow haze, shadows or JPEG artifacts anywhere, including the white background (one single flat #FFFFFF). Few colors: only #0F766E, #14B8A6 (used sparingly) and #FBBF24, on white.
```

- Candidates: 2 attempts; selected: attempt 2 (attempt 1 normalized to 540 KB, over the 300 KB budget, with `--ground auto` keeping the white ground opaque; attempt 2 used a flat-fill prompt and `--ground transparent`)
- Post-processing: github-showcase-skill `content icon normalize --ground transparent` (keyed from #FEFEFE, trimmed, fitted to the 688 px live area); output sha256 a99019b527de2b753f220fa6e65ee4413d09acd278a2fe29fb833e07dc0a8083; size 143 KB
