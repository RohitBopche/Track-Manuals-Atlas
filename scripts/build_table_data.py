#!/usr/bin/env python3
"""Browser file with the extracted tables, so the chat can show a matching row under its column headers.

data/search/tables.js:  globalThis.RDSO_TABLES = { "<table id>": { h: [header per column], r: [[cell,...],...], p: page, k: owner clause id, c: caption, x: heading line above the table naming its case, only if printed in the owning paragraph } }
Header cells of a multi-row header are already joined by extract_tables.py. Cells keep their newlines (wrapped records). Deterministic.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KG = ROOT / "data" / "knowledge-graph"
OUT = ROOT / "data" / "search" / "tables.js"
MAX_ROWS = 80


def owner_texts(ids: set) -> dict:
    """Whitespace-normalised text of the clauses that own a table, to check each table's heading line against."""
    out = {}
    with (KG / "canonical" / "nodes.jsonl").open(encoding="utf-8") as f:
        for l in f:
            n = json.loads(l)
            if n.get("id") in ids:
                out[n["id"]] = " ".join(str(n.get("text") or "").split())
    return out


def main() -> int:
    out = {}
    raw = [json.loads(l) for l in (KG / "raw" / "tables.jsonl").read_text(encoding="utf-8").splitlines()]
    texts = owner_texts({t["clause"] for t in raw if t.get("context") and t.get("clause")})
    for t in raw:
        if not t.get("clause") or not t["header_rows"]:
            continue
        hdr = [" ".join(" ".join(t["rows"][:t["header_rows"]][i][j] for i in range(t["header_rows"])).split()) for j in range(t["n_cols"])]
        body = t["rows"][t["header_rows"]:][:MAX_ROWS]
        ctx = t.get("context", "")
        if ctx and " ".join(ctx.split()) not in texts.get(t["clause"], ""):
            ctx = ""      # a heading printed for another paragraph's table is not shown with this one
        out[t["table_id"]] = {"h": hdr, "r": body, "p": t["page"], "k": t["clause"], "c": t.get("caption", ""), "x": ctx, "n": len(t["rows"]) - t["header_rows"]}
    OUT.write_text("globalThis.RDSO_TABLES=" + json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"table data: {len(out)} tables, {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
