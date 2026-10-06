#!/usr/bin/env python3
"""Typed relations between concepts, read from single sentences by explicit cue patterns.

Reads canonical/entities.jsonl, entity_mentions.jsonl and the paragraph text; writes canonical/entity_typed_relations.jsonl,
one row per sentence in which a relation is stated, with the character spans of both concepts and of the cue words:
  DETECTED_BY     defect -> test method          "flaws are detected by USFD", "USFD detects flaws", "detection of flaws using probes"
  CAUSES          cause -> effect                "X causes / leads to / results in Y", "Y due to / because of X"
  RESPONSIBLE_FOR role -> activity               "SSE/P.Way shall inspect ...", "tamping shall be supervised by SSE/P.Way"
  PERFORMED_WITH  activity -> machine            "tamping with a tamping machine", "the rail cutter is used for rail cutting"
A cue must sit between (or next to) the two concept mentions, in the same sentence, with no other mention of the same class in between.
Precision was measured by hand (eval/typed_relation_audit.json); recall was estimated the same way and is lower. Nothing is inferred beyond the sentence."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data" / "knowledge-graph" / "canonical"
sys.path.insert(0, str(ROOT / "scripts"))
from build_entities import sentence_bounds  # noqa: E402

W = r"(?:[^\W\d_]+[\s,/-]+){0,%d}"            # up to n words of filler


def rx(p):
    return re.compile(p, re.I)


DETECT_V = r"(?:detected|found|identified|revealed|located|noticed|observed|diagnosed|detectable|traced|picked\s+up|checked|examined|ascertained)"
DETECT_ACT = r"(?:detects?|finds?|reveals?|locates?|identif(?:y|ies)|picks?\s+up|shows?)"
PASSIVE_BY = r"\b(?:is|are|can\s+be|may\s+be|shall\s+be|should\s+be|will\s+be|be|get|gets|being|were|was|is\s+to\s+be|are\s+to\s+be)?\s*" + DETECT_V + r"\s+(?:by|with|through|using|on|during|in)\b"
NOUN_DET = r"\b(?:detection|detecting|identification|examination)\s+of\b"
CAUSE_V = r"\b(?:causes?|caused|causing|leads?\s+to|leading\s+to|led\s+to|results?\s+in|resulting\s+in|resulted\s+in|can\s+cause|may\s+cause|contributes?\s+to|gives?\s+rise\s+to)\b"
CAUSE_REV = r"\b(?:due\s+to|because\s+of|resulting\s+from|caused\s+by|arising\s+from)\b"
MODAL = r"\b(?:shall|should|will|must|is\s+responsible\s+for|are\s+responsible\s+for|has\s+to|have\s+to|is\s+to|are\s+to|will\s+ensure|shall\s+ensure|responsible\s+for)\b"
PASS_DONE = r"\b(?:shall|should|will|must|can|may)\s+be\s+(?:done|carried\s+out|performed|supervised|ensured|checked|arranged|monitored|conducted|undertaken|planned|attended|controlled|approved)\s+by\b"
USE_PREP = r"\b(?:with|using|by\s+means\s+of|by\s+use\s+of|through|by)\b"
WITH_MACHINE = r"\b(?:with|using|by\s+means\s+of|by\s+use\s+of|(?:done|carried\s+out|performed|undertaken|executed|completed|made|worked|cleaned|tamped|ground|cut|drilled|welded)\s+by)\b"
USED_FOR = r"\b(?:is|are|shall\s+be|should\s+be|can\s+be|may\s+be|be)\s+used\s+(?:for|to|in)\b"
ACT_CLASSES = {"Maintenance activity", "Welding"}
CAUSES_FROM = {"Defect", "Safety", "Geometry", "Parameter", "Maintenance activity", "Component", "Material", "Track structure"}
CAUSES_TO = {"Defect", "Safety", "Geometry"}
GENERIC = {"ENT:rail", "ENT:track", "ENT:safety", "ENT:manual", "ENT:speed", "ENT:signal", "ENT:station", "ENT:inspection"}      # too general to be a cause or an effect on their own
# between the modal and the activity: nothing but an adverb or one more word (the activity word is the verb), or a verb of doing and a short object
DOES = r"^\s*(?:(?:also|personally|jointly|himself|themselves|regularly|periodically|then|generally)\s+)*(?:be\s+)?(?:(?:ensure|arrange|carry\s+out|undertake|supervise|monitor|conduct|organi[sz]e|plan|do|perform|take\s+up|attend\s+to|responsible\s+for)\b\s*(?:the\s+|an?\s+|all\s+)?.{0,10})?\|?$"


def main() -> int:
    ents = {}
    for l in (CANON / "entities.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(l); ents[e["id"]] = e
    cls = lambda i: ents[i]["class"]
    text = {}
    for l in (CANON / "nodes.jsonl").read_text(encoding="utf-8").splitlines():
        n = json.loads(l)
        if n["type"] == "CLAUSE" and n.get("text"):
            text[n["id"]] = n["text"]
    ments = defaultdict(list)
    for l in (CANON / "entity_mentions.jsonl").read_text(encoding="utf-8").splitlines():
        m = json.loads(l)
        if m["source"] in text:
            ments[m["source"]].append((m["start"], m["end"], m["entity"]))

    rows = []
    seen = set()

    def emit(kind, a, b, cue, sid, sent):
        key = (kind, a[2], b[2], sid, sent[0])
        if key in seen or a[2] == b[2]:
            return
        seen.add(key)
        rows.append({"type": kind, "from": a[2], "to": b[2], "source": sid, "manual": sid.split(":")[1], "from_span": [a[0], a[1]], "to_span": [b[0], b[1]],
                     "cue": list(cue), "sentence": list(sent), "basis": "cue pattern in one sentence"})

    def clean_between(t, x, y, others, limit):
        """text between two spans, short, with no clause break and no other mention of the given classes in it"""
        s, e = x[1], y[0]
        if e - s > limit or e < s:
            return None
        gap = t[s:e]
        if re.search(r"[;:]|\.\s+[A-Z(]", gap):
            return None
        for m in others:
            if s <= m[0] and m[1] <= e:
                return None
        return gap

    for sid in sorted(ments):
        t = text[sid]
        ms = sorted(ments[sid])
        for (sa, sb) in sentence_bounds(t):
            inn = [m for m in ms if sa <= m[0] < sb]
            if len(inn) < 2:
                continue
            sent = (sa, sb)
            defects = [m for m in inn if cls(m[2]) == "Defect"]
            methods = [m for m in inn if cls(m[2]) == "Test method"]
            for d in defects:
                for m in methods:
                    if d[0] < m[0]:           # defect first: "flaws are detected by USFD"
                        gap = clean_between(t, d, m, [x for x in inn if cls(x[2]) in ("Defect", "Test method")], 110)
                        c = gap is not None and re.search(PASSIVE_BY, gap, re.I)
                        if c and not re.search(r"\b(?:not|no|never|without|nor)\b", gap[:c.end()], re.I):
                            emit("DETECTED_BY", d, m, (d[1] + c.start(), d[1] + c.end()), sid, sent)
                    else:                     # method first: "USFD detects flaws", "USFD for detection of flaws", "detection of flaws using USFD" (defect after)
                        gap = clean_between(t, m, d, [x for x in inn if cls(x[2]) in ("Defect", "Test method")], 90)
                        if gap is None:
                            continue
                        c = re.search(DETECT_ACT + r"\b|\b(?:for|to)\s+(?:detect(?:ing)?|find(?:ing)?|identify(?:ing)?)\b|" + NOUN_DET, gap, re.I)
                        if c and not re.search(r"\b(?:not|no|never|restrict\w*|prevent\w*|without|cannot|unable)\b", gap[:c.end()], re.I):
                            emit("DETECTED_BY", d, m, (m[1] + c.start(), m[1] + c.end()), sid, sent)
                # "detection of flaws by/using/with USFD": the noun cue sits just before the defect, the method follows it
                for m in methods:
                    if m[0] > d[1]:
                        lo = max(sa, d[0] - 30)
                        pre = t[lo:d[0]]
                        gap = clean_between(t, d, m, [x for x in inn if cls(x[2]) in ("Defect", "Test method")], 60)
                        c = re.search(NOUN_DET + r"\s*(?:the\s+|all\s+|any\s+)?$", pre, re.I)
                        if gap is not None and c and re.search(USE_PREP, gap, re.I):
                            emit("DETECTED_BY", d, m, (lo + c.start(), d[0]), sid, sent)
            # CAUSES
            for i, a in enumerate(inn):
                for b in inn:
                    if a is b or a[2] == b[2]:
                        continue
                    if a[1] <= b[0]:
                        gap = clean_between(t, a, b, inn, 45)
                        if gap is None:
                            continue
                        if a[2] in GENERIC or b[2] in GENERIC:
                            continue
                        c = re.search(CAUSE_V, gap, re.I)
                        if c and not re.search(CAUSE_REV, gap, re.I):               # "A causes B"
                            if cls(a[2]) in CAUSES_FROM and cls(b[2]) in CAUSES_TO:
                                emit("CAUSES", a, b, (a[1] + c.start(), a[1] + c.end()), sid, sent)
                        else:
                            c = re.search(CAUSE_REV, gap, re.I)                     # "A due to B": b is the cause, a the effect
                            if c and cls(b[2]) in CAUSES_FROM and cls(a[2]) in CAUSES_TO:
                                emit("CAUSES", b, a, (a[1] + c.start(), a[1] + c.end()), sid, sent)
            # RESPONSIBLE_FOR and PERFORMED_WITH
            roles = [m for m in inn if cls(m[2]) == "Role"]
            acts = [m for m in inn if cls(m[2]) in ACT_CLASSES or cls(m[2]) == "Test method"]
            machines = [m for m in inn if cls(m[2]) == "Machine" and not ents[m[2]].get("part_of")]
            for r in roles:
                for a in acts:
                    if r[1] <= a[0]:
                        gap = clean_between(t, r, a, [x for x in inn if cls(x[2]) == "Role"], 90)
                        if gap is None:
                            continue
                        c = re.search(MODAL, gap, re.I)
                        if c and c.start() <= 30 and not re.search(r"\b(?:not|never|no|to|with|by|from|for|that|which|if|when|where|than)\b", gap[:c.start()], re.I) and re.match(DOES, gap[c.end():] + "|"):
                            emit("RESPONSIBLE_FOR", r, a, (r[1] + c.start(), r[1] + c.end()), sid, sent)
                    elif a[1] <= r[0]:
                        gap = clean_between(t, a, r, [x for x in inn if cls(x[2]) == "Role"], 90)
                        c = gap is not None and re.search(PASS_DONE, gap, re.I)
                        if c and re.match(r"^\s*(?:the\s+|a\s+|an\s+)?$", gap[c.end():]):
                            emit("RESPONSIBLE_FOR", r, a, (a[1] + c.start(), a[1] + c.end()), sid, sent)
            for a in [x for x in inn if cls(x[2]) in ACT_CLASSES]:
                for mc in machines:
                    if a[1] <= mc[0]:
                        gap = clean_between(t, a, mc, [x for x in inn if cls(x[2]) in ACT_CLASSES or cls(x[2]) == "Machine"], 70)
                        c = gap is not None and re.search(WITH_MACHINE, gap, re.I)
                        if c:
                            emit("PERFORMED_WITH", a, mc, (a[1] + c.start(), a[1] + c.end()), sid, sent)
                    elif mc[1] <= a[0]:
                        gap = clean_between(t, mc, a, [x for x in inn if cls(x[2]) in ACT_CLASSES or cls(x[2]) == "Machine"], 60)
                        c = gap is not None and re.search(USED_FOR, gap, re.I)
                        if c:
                            emit("PERFORMED_WITH", a, mc, (mc[1] + c.start(), mc[1] + c.end()), sid, sent)
    rows.sort(key=lambda r: (r["type"], r["from"], r["to"], r["source"], r["sentence"][0]))
    with (CANON / "entity_typed_relations.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    by = defaultdict(int)
    for r in rows:
        by[r["type"]] += 1
    print(f"typed relations {len(rows)}: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
