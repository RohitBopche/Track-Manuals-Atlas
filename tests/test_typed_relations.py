"""Typed relations read from single sentences: the data, the hand audit, and the chat's answers."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data" / "knowledge-graph" / "canonical"


def rows():
    return [json.loads(l) for l in (CANON / "entity_typed_relations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def test_all_four_types_present_and_spans_read_as_concepts():
    r = rows()
    assert {x["type"] for x in r} == {"DETECTED_BY", "RESPONSIBLE_FOR", "PERFORMED_WITH", "CAUSES"}
    assert len(r) >= 50
    text = {}
    for l in (CANON / "nodes.jsonl").read_text(encoding="utf-8").splitlines():
        n = json.loads(l)
        if n["type"] == "CLAUSE" and n.get("text"):
            text[n["id"]] = n["text"]
    for x in r:
        t = text[x["source"]]
        assert x["cue"][0] >= x["sentence"][0] and x["cue"][1] <= x["sentence"][1]
        assert re.search(r"[A-Za-z]", t[x["from_span"][0]:x["from_span"][1]]) and re.search(r"[A-Za-z]", t[x["to_span"][0]:x["to_span"][1]])


def test_hand_audit_matches_current_extraction_and_reports_precision_and_recall():
    a = json.loads((ROOT / "eval" / "typed_relation_audit.json").read_text(encoding="utf-8"))
    key = lambda x: (x["type"], x["from"], x["to"], x["source"], x["sentence"][0], x["from_span"][0], x["to_span"][0])
    assert {key(x) for x in a["extracted_rows"]} == {key(x) for x in rows()}
    p = a["precision_after_tightening"]
    assert p["extracted"] == len(a["extracted_rows"]) and p["correct"] == sum(x["correct"] for x in a["extracted_rows"])
    assert p["correct"] / p["extracted"] >= 0.85
    rs = a["recall_sample"]
    assert rs["stated_and_extracted"] == sum(1 for x in a["recall_rows"] if x["stated"] and x["extracted"])
    assert rs["relation_stated"] == sum(1 for x in a["recall_rows"] if x["stated"])
    assert a["first_version"] == {"extracted": 88, "correct": 71}


def test_chat_answers_typed_questions_and_leaves_others_alone():
    qs = ["How is a flaw detected?", "What can USFD detect?", "Who inspects the track?", "What machine is used for tamping?", "What causes buckling?",
          "What is the tamping machine used for?", "How is an ultrasonic rail flaw detector calibrated before testing?", "What are the duties of a patrolman?"]
    r = subprocess.run(["node", str(ROOT / "tests" / "entity_probe.js"), *qs], capture_output=True, text=True, check=True)
    o = json.loads(r.stdout)
    assert o[qs[0]]["mode"] == "concept" and any("USFD" in x["label"] for x in o[qs[0]]["rows"]) and "detect" in o[qs[0]]["text"]
    assert o[qs[1]]["mode"] == "concept" and "detect" in o[qs[1]]["text"]
    assert o[qs[2]]["mode"] == "concept" and any("SSE/P.Way" in x["label"] for x in o[qs[2]]["rows"])
    assert o[qs[3]]["mode"] == "concept" and any("Tamping machine" in x["label"] for x in o[qs[3]]["rows"])
    assert o[qs[4]]["mode"] == "concept" and "cause" in o[qs[4]]["text"]
    assert o[qs[5]]["mode"] == "concept"
    for x in o[qs[0]]["rows"] + o[qs[3]]["rows"]:
        assert x["quote"] and x["clause"]
    assert o[qs[6]]["kind"] == "answer" and o[qs[7]]["kind"] == "answer"      # calibration and duties go to the normal answer
