# 2026-10-29 organization snapshot

This frozen snapshot contains 91 teams and their hierarchy. See [the chart index](../../README.md) for the area links, legend, limitations and prior work.

From this directory:

```sh
python -X utf8 build_sources.py
python -X utf8 render_charts.py
python -X utf8 validate.py
```

The renderer uses Mermaid CLI 12.0.0 and an installed Chrome/Chromium browser. Set `CHROME_PATH` when browser discovery is insufficient. Public team structure is frozen in `team-snapshot.json`; no command here refreshes or mutates GitHub.

The exported PNGs use the same basename as their Mermaid sources. The complete and actual-nesting PNGs are 16,000 pixels wide; the twelve area PNGs are 5,000 pixels wide. Font availability can affect layout on another machine.

Member identities, owners, membership counts and pending invitations are excluded from the public source, diagrams and archive.
