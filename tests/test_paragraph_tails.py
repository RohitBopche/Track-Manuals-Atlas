"""Paragraph boundaries and form items (§37.50): a bold table header or sentence that starts with "Section" or "Chapter" is not a
chapter banner, TMM's dotted annexure headings are, and a question that quotes a form item is shown that item."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import clause_parser as C  # noqa: E402


def test_banner_needs_a_designator():
    for t in ["CHAPTER – 7", "PART – B", "SECTION – II: Re-Alignment of Curves", "Part-A Engine Operated Rail Drilling Machine (RDM)",
              "Annexure - 2/1 (Para 204)", "ANNEXURE- I"]:
        assert C.BANNER_RE.match(t), t
    for t in ["Section Category of track Lateral wear", "Section Speed", "Chapter No 3, Part D pertaining to provisions on LWR.",
              "SECTION Y - Hy for the section ‘Y’ are calculated as", "SECTION X AND Z", "Section"]:
        assert not C.BANNER_RE.match(t), t


def test_dotted_annexure_heading():
    for t in ["Annexure 7.3", "ANNEXURE 8.17", "Annexure 7.7[ACS-2]", "Annexure5.3(A)"]:
        assert C.ANNEX_DOTTED_RE.match(t), t
    for t in ["Annexure 8.6,", "Annexure 3.3 and 3.4", "Annexure 2.12 gives an example showing stepwise procedure"]:
        assert not C.ANNEX_DOTTED_RE.match(t), t


def node(nid):
    with (ROOT / "data/knowledge-graph/canonical/nodes.jsonl").open(encoding="utf-8") as f:
        for l in f:
            n = json.loads(l)
            if n.get("id") == nid:
                return n


def test_irpwm_702_keeps_its_tail_after_the_lateral_wear_table():
    n = node("CLAUSE:IRPWM:CH_07:PARA_702")
    assert n["page_end"] == 374
    assert "Lateral wear is to be measured at 13 to 15 mm below the rail top table." in " ".join(n["text"].split())
    assert "Criteria for Renewal of Sleepers" in n["text"]


def ask(*ids):
    js = ("const path=require('path'),root=process.cwd();const S=require(root+'/lib/rdso_search.js'),C=require(root+'/lib/rdso_chat.js');"
          "['search_index','clause_extras','crossrefs','tables'].forEach(f=>require(root+'/data/search/'+f+'.js'));"
          "const e=S.create(globalThis.RDSO_SEARCH_INDEX);const qs=require('fs').readFileSync(root+'/eval/real_questions_irpwm.jsonl','utf8').trim().split('\\n').map(JSON.parse);"
          "const out={};for(const id of process.argv.slice(1)){const r=C.create(e,{extras:globalThis.RDSO_CLAUSE_EXTRAS,xrefs:globalThis.RDSO_CROSSREFS,tables:globalThis.RDSO_TABLES}).ask(qs.find(q=>q.id===id).question);"
          "out[id]={points:(r.points||[]).map(p=>p.text),also:(r.alsoSee||[]).map(a=>({text:a.text,label:a.cite.label,annexure:!!a.annexure}))};}console.log(JSON.stringify(out));")
    return json.loads(subprocess.run(["node", "-e", js, *ids], cwd=ROOT, capture_output=True, text=True, check=True).stdout)


def test_r3_shows_where_lateral_wear_is_measured():
    assert any("13 to 15 mm below the rail top table" in p for p in ask("R3")["R3"]["points"])


def test_r11_shows_the_form_item_for_track_behind_crossing():
    items = [a for a in ask("R11")["R11"]["also"] if a["annexure"]]
    assert items and items[0]["label"] == "IRPWM Annexure 4/3"
    assert "Station No. 0 to be marked at the centre of last long sleeper" in items[0]["text"]
