"""Tables in chat answers keep every column a reader needs, every row a question "across" cases asks for, and the
heading that names each case (§37.49). Guarded on three real questions that were partial for exactly these reasons."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def shown(*ids):
    out = subprocess.run(["node", "tests/table_probe.js", *ids], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def test_table_of_seven_columns_is_shown_whole():
    # R5: ERC clips; the weight column used to be dropped, hiding the ERC-J weight (1 kg)
    t = shown("R5")["R5"][0]
    assert "Approximate Weight (kg)" in t["columns"]
    assert ["1", "ERC-J", "RT-8258", "650", "8.5", "20.64", "1"] in t["rows"]


def test_question_across_cases_shows_every_row():
    # R20: versine variation limits "across different speed bands": all three bands, not only the first
    rows = [r for t in shown("R20")["R20"] for r in t["rows"]]
    for mm in ("10 mm", "20 mm", "40 mm"):
        assert any(r[-1].startswith(mm) for r in rows), mm


def test_one_table_per_case_with_its_heading():
    # R18: UML acceleration limits per speed band: one table per band, each with the band printed above it
    tables = shown("R18")["R18"]
    pairs = {(t["context"], r[-1]) for t in tables for r in t["rows"] if "acceleration" in r[-1]}
    assert ("For Speeds above 110 Kmph and up to 130 Kmph:", "Vertical and lateral acceleration peak of 0.25 g") in pairs
    assert ("For Speeds above 130 Kmph and up to 160 Kmph:", "Vertical and lateral acceleration peak of 0.20 g") in pairs
    assert len({t["context"] for t in tables}) == len(tables) == 4
