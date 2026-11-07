"""Validate the frozen organization snapshot and all rendered chart exports."""
from pathlib import Path
import json
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent

def validate_snapshot(snapshot):
    """Reject anything beyond the public team hierarchy allowlist."""
    if set(snapshot) != {"captured_at_utc", "teams"}:
        raise ValueError("Snapshot must contain only capture time and public teams")
    for team in snapshot["teams"]:
        if set(team) != {"id", "name", "slug", "html_url", "parent"}:
            raise ValueError("Team contains fields outside the public hierarchy allowlist")
        if type(team["id"]) is not int or not all(isinstance(team[k], str) for k in ("name", "slug", "html_url")):
            raise ValueError("Invalid public team identity")
        if team["parent"] is not None and not isinstance(team["parent"], str):
            raise ValueError("Invalid parent identity")
        if team["html_url"] != "https://github.com/orgs/Pick-Your-AI/teams/" + team["slug"]:
            raise ValueError("Invalid public team URL")


def main():
    snapshot = json.loads((ROOT / "team-snapshot.json").read_text(encoding="utf-8"))
    validate_snapshot(snapshot)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    teams = {team["slug"]: team for team in snapshot["teams"]}
    assert len(teams) == len(snapshot["teams"]), "Duplicate team slugs"
    assert len({team["id"] for team in teams.values()}) == len(teams), "Duplicate team IDs"
    charts = manifest["charts"]
    assert set(charts[0]["teams"]) == set(teams), "Incomplete organization overview"
    assert set(map(tuple, charts[1]["edges"])) == {
        (team["parent"], team["slug"]) for team in teams.values() if team["parent"]
    }, "Actual GitHub hierarchy does not match snapshot"
    results = []
    for chart in charts:
        name = chart["name"]
        svg = ET.parse(ROOT / f"{name}.svg").getroot()
        links = [element for element in svg.iter() if element.tag.endswith("}a")]
        assert len(links) == len(chart["teams"]), f"{name}: missing rendered team links"
        source = (ROOT / f"{name}.mmd").read_text(encoding="utf-8")
        for slug in chart["teams"]:
            team = teams[slug]
            key = f"team_{team['id']}"
            nodes = [element for element in svg.iter()
                     if element.tag.endswith("}g") and key in element.get("id", "")
                     and "node" in element.get("class", "").split()]
            assert len(nodes) == 1, f"{name}: invalid node for {slug}"
            text = " ".join(nodes[0].itertext())
            assert team["html_url"] in source, f"{name}: missing link for {slug}"
            assert team["name"] in text or team["name"].split(" - ")[-1] in text, f"{name}: missing team name"
        png = (ROOT / f"{name}.png").read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n", f"{name}: invalid PNG"
        width, height = struct.unpack(">II", png[16:24])
        expected_width = 16000 if name in ("organization-complete", "github-team-hierarchy") else 5000
        assert width == expected_width and height > 0, f"{name}: incorrect resolution"
        results.append({"chart": name, "teams": len(links), "width": width, "height": height})
    print(json.dumps({"teams": len(teams), "charts": results}, indent=2))

if __name__ == "__main__":
    main()
