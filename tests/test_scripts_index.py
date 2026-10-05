"""scripts/README.md lists every script exactly once, so agents and people can find the right one."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_every_script_is_indexed_once():
    on_disk = {p.relative_to(SCRIPTS).as_posix() for p in SCRIPTS.rglob("*") if p.suffix in (".py", ".js")}
    rows = re.findall(r"^\| `([^`]+\.(?:py|js))` \|", (SCRIPTS / "README.md").read_text(encoding="utf-8"), re.M)
    assert len(rows) == len(set(rows)), "a script is listed twice"
    assert set(rows) == on_disk, f"missing: {sorted(on_disk - set(rows))}; stale: {sorted(set(rows) - on_disk)}"
