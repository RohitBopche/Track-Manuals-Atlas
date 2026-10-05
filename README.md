# Track Manuals Atlas

An offline knowledge base and knowledge graph of Indian Railways manuals, starting with six track manuals and built to take more, with a chat that answers only by quoting the manuals (manual, paragraph and page for every statement). Formerly "RDSO-Drawings"; the repository keeps that name until it is renamed in GitHub settings. This is an independent tool, not an official RDSO product.

**Developed for:** Track Analytical Cell, Bhusawal Division, Central Railway, Indian Railways

## Use it

No server or internet needed. Open a page from disk (double-click works):

| Page | What it is |
|---|---|
| `index.html` | Home: knowledge graph with a chat box |
| `chat.html` | Chat assistant: cited answers, follow-up questions |
| `browse.html` | Browse the manuals by chapter and paragraph |
| `learn.html` | Practice cards generated from the manuals |
| `expert.html` | Full workbench: drawings, revisions, 3D graph |

From the terminal: `node scripts/search_cli.js "your question"`.

## Build and check

```
pip install -r requirements-dev.txt && npm ci
python scripts/rebuild_all.py        # rebuild every generated file from the source PDFs (about 3 minutes); must leave `git diff data/` empty
python scripts/validate_all.py       # all publication gates (A to AA)
python -m pytest -q                  # unit and regression tests
python scripts/run_browser_tests.py  # headless browser suites
python scripts/make_review_packet.py --per-kind 10 --seed 1   # offline human-review packet (master §37.22)
```

## Layout

| Path | Contents |
|---|---|
| `manuals/`, `drawings/` | Source PDFs (six manuals, 59 RDSO drawing sheets). Never edited. |
| `scripts/` | Extraction pipeline, validators and tools; index in [`scripts/README.md`](scripts/README.md) |
| `data/knowledge-graph/` | Generated knowledge core: `raw/`, `intermediate/`, `canonical/`, `exports/`, `reports/`, `schemas/` |
| `data/*.js`, `data/search/` | Generated browser bundles |
| `eval/` | Question sets, baselines, human review decisions |
| `tests/` | pytest suites and headless browser suites |
| `ui/`, `lib/` | Shared page styles and scripts; vendored offline libraries |
| `docs/` | [`PROJECT_MASTER.md`](docs/PROJECT_MASTER.md) (spec and plan), [`DELIVERY_LOG.md`](docs/DELIVERY_LOG.md) (what was delivered and measured), `archive/` (history) |
| `research/` | Research notes and benchmarks |

## Documentation

- [`docs/PROJECT_MASTER.md`](docs/PROJECT_MASTER.md): the authoritative record. Start with "State now" at the top and §40 (phase plan).
- [`docs/DELIVERY_LOG.md`](docs/DELIVERY_LOG.md): dated results of every sprint and audit (master §37).
- [`CLAUDE.md`](CLAUDE.md): rules and commands for coding agents.
- [`docs/archive/PROTOTYPE_README.md`](docs/archive/PROTOTYPE_README.md): the original 3D digital-twin prototype README (unverified, history only).
