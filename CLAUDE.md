# Track Manuals Atlas — agent guide

Offline knowledge base + graph of Indian Railways track manuals (six so far). Every answer quotes a manual with manual, paragraph and page. No server: the HTML pages open from disk. The repository is still named RDSO-Drawings; it is not an official RDSO product.

## Where the truth lives

- `docs/PROJECT_MASTER.md` is the single authoritative record (about 190 KB, too long to read whole). Read only what you need:
  - §1 principles, §24 validation gates, §29 AI guardrails, §33 handoff protocol, §34 guardrails against premature complexity.
  - §37 is a dated log of delivered work, newest sub-section last (§37.46 at time of writing). §40 is the current phase plan and status table.
  - Find a section with `grep -n '^## \|^### ' docs/PROJECT_MASTER.md`, then read that line range.
- `README.md` sections 1 to 5 describe the early 3D prototype and are **unverified**. Use only its "Current status" box and command block.
- `docs/archive/` and `docs/gemini/` are history. Do not take status, file paths or commands from them.

## Commands

```
pip install -r requirements-dev.txt && npm ci
python scripts/rebuild_all.py          # ~3 min; regenerates everything under data/ from manuals/*.pdf
git diff --exit-code -- data/          # rebuild must be byte-for-byte reproducible (CI enforces)
python scripts/unify_manual_canonical.py --check-metrics
python scripts/validate_all.py         # publication gates A to AA
python -m pytest -q                    # unit + regression tests
python scripts/run_browser_tests.py    # headless Chromium suites (needs npm ci; set CHROME_PATH if needed)
node scripts/search_cli.js "question"  # offline search from the terminal
```

On a fresh clone run `rebuild_all.py` once before pytest: `test_measurements_tables.py` (and so Gate E) needs the git-ignored `data/search/passages.jsonl` that the rebuild writes.

Fast loop while editing one area: `python -m pytest -q tests/test_<area>.py`, then the full `validate_all.py` before committing.

## Layout

- `manuals/*.pdf`, `drawings/*.pdf` — source documents. Never modify or delete.
- `scripts/` — pipeline; `rebuild_all.py` lists the step order. `kg_utils.py`, `provenance_policy.py` are shared helpers. `validate_*.py` back the gates in `validate_all.py`.
- `data/knowledge-graph/{raw,intermediate,canonical,exports,reports}` — generated. `canonical/*.jsonl` is the knowledge core; `schemas/` holds the JSON schemas and `ONTOLOGY.md`.
- `data/*.js`, `data/search/*.js` — generated browser bundles (one huge line each).
- `index.html` (home: graph + chat box), `chat.html`, `browse.html`, `learn.html`, `expert.html` (full workbench, ~10k lines), shared `ui/`, vendored `lib/`.
- `eval/` — question sets, baselines, human review decisions (`eval/reviews/`). `tests/` — pytest (`test_*.py`) and Node/CDP browser suites (`verify_*.js`).

## Rules

- **Generated files are outputs.** Never hand-edit anything under `data/` (except `data/search/synonyms.json` via `scripts/apply_reviewed_synonyms.py`). Change the generator, rerun `rebuild_all.py`, commit code and regenerated data together. `.ignore` hides the huge bundles from search; open them by path only if needed.
- **Do not run `scripts/build_updated_app.py`** (deprecated; overwrites `index.html`). Other legacy prototype scripts (`analyze_rdso_drawing.py`, `build_updated_app.py`, `data/rdso_drawing_catalog.json`) are not part of the pipeline; the drawing registry is `data/knowledge-graph/canonical/drawings_registry.jsonl`.
- **Evidence before explanation.** Every answer, card or fact shown to a user must trace to a clause id and page. No hand-written engineering facts, answers or "VERIFIED" labels; status comes only from recorded human reviews (Gate M).
- **Report honestly.** When you close work, add a dated `### 37.N` sub-section to the master stating what was measured, how, and what is still open; update the §40 table if a phase changes. Say when something was not run (e.g. browser suites).
- Small validated increments. Keep the app offline: no CDNs, no network calls, no servers.
- Python 3.11, standard library + `pymupdf`/`Pillow`/`jsonschema`. Node only for the browser tests and `search_cli.js`.
