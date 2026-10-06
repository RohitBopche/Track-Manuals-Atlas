#!/usr/bin/env python3
"""Gate AA: the entity layer is consistent with the manual text.

Checks: lexicon valid; every mention span reads as an alias of its concept; counts add up; every relation endpoint exists;
every co-mention example sentence holds both concepts; every limit sits in a sentence that names its concept; every typed relation has both concepts and its cue words inside one sentence and equals the set read by hand in eval/typed_relation_audit.json; coverage floors per manual."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data" / "knowledge-graph" / "canonical"
sys.path.insert(0, str(ROOT / "scripts"))
from build_entities import SENT_END, case_sensitive, sentence_bounds  # noqa: E402

MIN_CONCEPTS_PER_MANUAL = 35


def load(n):
    return [json.loads(l) for l in (CANON / n).read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    errs = []
    lex = json.loads((ROOT / "data" / "ontology" / "concepts.json").read_text(encoding="utf-8"))["concepts"]
    ids = {f"ENT:{c['id']}" for c in lex}
    ents, mentions, rels, limits = load("entities.jsonl"), load("entity_mentions.jsonl"), load("entity_relations.jsonl"), load("entity_limits.jsonl")
    if {e["id"] for e in ents} != ids:
        errs.append("entities.jsonl does not match concepts.json")
    text = {}
    for n in load("nodes.jsonl"):
        if n["type"] == "CLAUSE" and n.get("text"):
            text[n["id"]] = n["text"]
    for a in load("annexures.jsonl"):
        text[a["id"]] = a["text"]
    alias_of = {e["id"]: e["aliases"] for e in ents}
    seen = set()
    per = defaultdict(Counter)
    ment_in = defaultdict(list)                                       # source -> [(start, end, entity)]
    for m in mentions:
        key = (m["source"], m["start"], m["end"])
        if key in seen:
            errs.append(f"overlapping duplicate mention {key}")
        seen.add(key)
        t = text.get(m["source"])
        if t is None or m["entity"] not in ids:
            errs.append(f"mention of unknown source or concept: {m['source']} {m['entity']}"); continue
        span = re.sub(r"\s+", " ", t[m["start"]:m["end"]])
        ok = False
        for a in alias_of[m["entity"]]:
            for suf in ("", "s", "es"):                                    # the matcher allows a plural ending
                if (span == a + suf) if case_sensitive(a) else (span.lower() == (a + suf).lower()):
                    ok = True
        if not ok:
            errs.append(f"span {span!r} is not an alias of {m['entity']} ({m['source']})")
        ment_in[m["source"]].append((m["start"], m["end"], m["entity"]))
        per[m["manual"]][m["entity"]] += 1
    counts = Counter(m["entity"] for m in mentions)
    for e in ents:
        if e["mentions"] != counts[e["id"]]:
            errs.append(f"{e['id']}: mentions field {e['mentions']} != {counts[e['id']]}")
        if not counts[e["id"]]:
            errs.append(f"{e['id']}: concept never found in the text")
    for r in rels:
        if r["from"] not in ids or r["to"] not in ids:
            errs.append(f"relation with unknown endpoint: {r['from']} {r['to']}")
        if r["type"] == "DISCUSSED_WITH":
            if r["support"] < 3:
                errs.append(f"{r['from']} {r['to']}: support below 3")
            for ex in r["examples"]:
                a, b = ex["sentence"]; got = {x[2] for x in ment_in[ex["source"]] if a <= x[0] < b}
                if r["from"] not in got or r["to"] not in got:
                    errs.append(f"example sentence of {r['from']}~{r['to']} in {ex['source']} does not name both")
    for l in limits:
        t = text.get(l["source"]); at = l["at"]
        if t is None or t[at[0]:at[1]] != l["raw"]:
            errs.append(f"limit {l['measurement']}: raw value not at its span"); continue
        a, b = l["sentence"]
        if not (a <= at[0] < b) or l["entity"] not in {x[2] for x in ment_in[l["source"]] if a <= x[0] < b}:
            errs.append(f"limit {l['measurement']}: concept {l['entity']} not in the value's sentence")
    typed = load("entity_typed_relations.jsonl")
    allowed = {"DETECTED_BY", "RESPONSIBLE_FOR", "PERFORMED_WITH", "CAUSES"}
    for r in typed:
        t = text.get(r["source"])
        if t is None or r["type"] not in allowed or r["from"] not in ids or r["to"] not in ids:
            errs.append(f"typed relation with unknown type, source or concept: {r['type']} {r['source']}"); continue
        a, b = r["sentence"]
        for who, span in (("from", r["from_span"]), ("to", r["to_span"])):
            if not (a <= span[0] < span[1] <= b) or (span[0], span[1], r[who]) not in set(ment_in[r["source"]]):
                errs.append(f"typed {r['type']} {r['source']}: {who} concept is not a mention inside the sentence")
        if not (a <= r["cue"][0] < r["cue"][1] <= b) or not t[r["cue"][0]:r["cue"][1]].strip():
            errs.append(f"typed {r['type']} {r['source']}: cue words are not inside the sentence")
    audit = json.loads((ROOT / "eval" / "typed_relation_audit.json").read_text(encoding="utf-8"))
    audited = {(x["type"], x["from"], x["to"], x["source"], x["sentence"][0], x["from_span"][0], x["to_span"][0]) for x in audit["extracted_rows"]}
    current = {(x["type"], x["from"], x["to"], x["source"], x["sentence"][0], x["from_span"][0], x["to_span"][0]) for x in typed}
    if audited != current:
        errs.append(f"typed relations changed since the hand audit: {len(current - audited)} new, {len(audited - current)} gone; read the new ones, update eval/typed_relation_audit.json")
    for man in ("IRPWM", "TMM", "STMM", "USFD", "AT_WELD", "FBW"):
        if len(per[man]) < MIN_CONCEPTS_PER_MANUAL:
            errs.append(f"{man}: only {len(per[man])} concepts found (floor {MIN_CONCEPTS_PER_MANUAL})")
    if errs:
        print("\n".join(errs[:25])); print(f"[FAIL] {len(errs)} problem(s)"); return 1
    print(f"[PASS] {len(ents)} concepts, {len(mentions)} mentions, {len(rels)} relations, {len(limits)} limits, {len(typed)} typed relations; concepts per manual: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(per.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
