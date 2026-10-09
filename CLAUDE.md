# Track Manuals Atlas — agent guide

Offline knowledge base + graph of Indian Railways track manuals (six so far). Every answer quotes a manual with manual, paragraph and page. No server: the HTML pages open from disk. The repository is still named RDSO-Drawings; it is not an official RDSO product.

## Where the truth lives

- `docs/PROJECT_MASTER.md` is the authoritative spec and plan (about 60 KB). Start with "State now" at the top, then:
  - §1 principles, §24 validation gates, §29 AI guardrails, §33 handoff protocol, §34 guardrails against premature complexity, §40 phase plan and status table.
  - Find a section with `grep -n '^## \|^### ' docs/PROJECT_MASTER.md`, then read that line range.
- `docs/DELIVERY_LOG.md` is master §37: dated, measured results of every sprint (§37.1 to §37.51 at time of writing, newest last). References to "§37.N" anywhere point here. Read the last few entries, not the whole file (about 130 KB).
- `scripts/README.md` says what every script does and whether it is a rebuild step, a gate, a library, a tool or legacy.
- `docs/archive/` is history (prototype README, old plans, Gemini logs). Do not take status, file paths or commands from it.

## Commands

```
pip install -r requirements-dev.txt && npm ci   # cloud sessions: done by .claude/hooks/session-start.sh
python scripts/rebuild_all.py          # ~3 min; regenerates everything under data/ from manuals/*.pdf
git diff --exit-code -- data/          # rebuild must be byte-for-byte reproducible (CI enforces)
python scripts/unify_manual_canonical.py --check-metrics
python scripts/validate_all.py         # publication gates A to AA
python -m pytest -q                    # unit + regression tests
python scripts/run_browser_tests.py    # headless Chromium suites (needs npm ci; set CHROME_PATH if needed)
node scripts/search_cli.js "question"  # offline search from the terminal
```

Fast loop while editing one area: `python -m pytest -q tests/test_<area>.py`, then the full `validate_all.py` before committing.

## Layout

- `manuals/*.pdf`, `drawings/*.pdf` — source documents. Never modify or delete.
- `scripts/` — pipeline; `rebuild_all.py` lists the step order. `kg_utils.py`, `provenance_policy.py` are shared helpers. `validate_*.py` back the gates in `validate_all.py`.
- `data/knowledge-graph/{raw,intermediate,canonical,exports,reports}` — generated. `canonical/*.jsonl` is the knowledge core; `schemas/` holds the JSON schemas and `ONTOLOGY.md`.
- `data/*.js`, `data/search/*.js` — generated browser bundles (one huge line each).
- `index.html` (home: graph + chat box), `chat.html`, `browse.html`, `learn.html`, `expert.html` (full workbench; its logic is in `ui/expert.js`, its styles in `ui/expert.css`), shared `ui/`, vendored `lib/`.
- `eval/` — question sets, baselines, human review decisions (`eval/reviews/`). `tests/` — pytest (`test_*.py`) and Node/CDP browser suites (`verify_*.js`).

## Rules

- **Generated files are outputs.** Never hand-edit anything under `data/` (except `data/search/synonyms.json` via `scripts/apply_reviewed_synonyms.py`). Change the generator, rerun `rebuild_all.py`, commit code and regenerated data together. `.ignore` hides the huge bundles from search; open them by path only if needed.
- **Legacy scripts** (marked "legacy" in `scripts/README.md`) are not part of the pipeline; do not run them. `data/rdso_drawing_catalog.json` is superseded by `data/knowledge-graph/canonical/drawings_registry.jsonl`. Adding or removing a script means updating `scripts/README.md` (a test checks it).
- **Evidence before explanation.** Every answer, card or fact shown to a user must trace to a clause id and page. No hand-written engineering facts, answers or "VERIFIED" labels; status comes only from recorded human reviews (Gate M).
- **Report honestly.** When you close work, add a dated `### 37.N` entry at the end of `docs/DELIVERY_LOG.md` stating what was measured, how, and what is still open; update §40 and "State now" in the master if a phase or a headline number changes. Say when something was not run (e.g. browser suites).
- Commits: one plain imperative sentence as subject, one concern per commit, generated data together with its generator (master §33).
- Small validated increments. Keep the app offline: no CDNs, no network calls, no servers.
- Python 3.11, standard library + `pymupdf`/`Pillow`/`jsonschema`. Node only for the browser tests and `search_cli.js`.
