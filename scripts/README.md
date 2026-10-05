# Scripts

Every script in this folder, what it is for and who calls it. `tests/test_scripts_index.py` fails if a script is added or removed without updating this table.

Roles: **rebuild** = a step of `rebuild_all.py` (run in that order); **Gate X** = run by `validate_all.py`; **lib** = imported by other scripts; **tool** = run by hand; **legacy** = prototype or superseded code, not part of the pipeline (do not run unless you know why).

## Entry points

| Script | Role | Purpose |
|---|---|---|
| `rebuild_all.py` | entry | Deterministic rebuild of every generated file from the source PDFs (about 3 min). Lists the step order. |
| `validate_all.py` | entry | Runs publication gates A to AA. |
| `run_browser_tests.py` | entry | Runs the headless-browser (CDP) suites. Needs `npm ci` and Chrome/Chromium. |
| `search_cli.js` | tool | Offline search from the command line. |

## Rebuild pipeline (in `rebuild_all.py` order)

| Script | Role | Purpose |
|---|---|---|
| `ingest_all_manual_chapters.py` | rebuild, lib | Chapter-by-chapter extraction of the six manuals. |
| `generate_canonical_kg.py` | rebuild | Compact canonical core (entities, typed edges, facts). |
| `unify_manual_canonical.py` | rebuild, lib | Makes the canonical store the single source of clause text; writes metrics (`--check-metrics`). Runs twice. |
| `locate_evidence.py` | rebuild, lib | Finds every manual node's source text on its PDF page. |
| `export_kg_bundle.py` | rebuild | Writes the browser bundle `data/rdso_kg_data.js`. |
| `extract_tables.py` | rebuild | Ruled data tables with structure (about 2 min). |
| `extract_measurements.py` | rebuild | Structured values from clause text and table cells, plus conflict candidates. |
| `drawing_registry.py` | rebuild | Drawing identity and revision evidence from file names and committed OCR. |
| `drawing_links.py` | rebuild, lib | Clause to drawing-sheet citations. |
| `build_annexures.py` | rebuild | Annexures, appendices, front matter and loose text as searchable units. |
| `build_entities.py` | rebuild, lib | Concepts named in the text, taxonomy, co-mention links, limits per concept. |
| `build_learning.py` | rebuild | Practice cards generated only from the manuals. |
| `build_table_data.py` | rebuild | Browser file of tables with headers, for the chat. |
| `build_clause_extras.py` | rebuild | Browser file of measurements and held drawings per clause. |
| `ingest_reviews.py` | rebuild, tool | Records human review decisions; with no arguments refreshes `reports/review_accuracy.json`. |
| `evidence_coverage_report.py` | rebuild, Gate W | Page crop for every paragraph, or the reason there is none. |
| `crossref_diagnose.py` | rebuild, Gate X | Reason and page for every unresolved cross-reference. |
| `build_search_index.py` | rebuild | Offline search index: passages, then `build_search_index.js`. |
| `build_search_index.js` | rebuild | Builds `data/search/search_index.js` from `passages.jsonl` (called by `build_search_index.py`). |

## Gates (run by `validate_all.py`)

| Script | Role | Purpose |
|---|---|---|
| `validate_canonical_graph.py` | Gate A | Canonical JSONL records match the schema contract. |
| `audit_identity_references.py` | Gate B | Inventory of legacy identity references. |
| `validate_graph_integrity.py` | Gate C | Referential integrity of the canonical graph. |
| `validate_evidence_integrity.py` | Gate D | Evidence integrity across the canonical core. |
| `validate_manual_knowledge_graph.py` | Gate F | Manuals structural contract and universe isolation. |
| `validate_manual_chapter_content.py` | Gate I, lib | Chapter boundaries and content ownership. |
| `validate_manual_canonical_content.py` | Gate J | Chapter content ownership in the canonical KG. |
| `validate_manual_hierarchy.py` | Gate K | Source-heading hierarchy and ownership. |
| `validate_manual_text_integrity.py` | Gate L | Manual text integrity and single source of truth. |
| `validate_provenance_policy.py` | Gate M | Nothing is reviewed or verified without a review record. |
| `validate_evidence_locations.py` | Gate N | Evidence is locatable and re-verifiable against the PDFs. |
| `validate_ocr_coverage.py` | Gate O | Every image-only page has OCR tied to the current PDF hash. |
| `validate_retrieval.py` | Gate P | Index freshness, eval-set integrity, no retrieval regression. |
| `validate_crossrefs.py` | Gate Q | Cross-references extracted, classified, resolvable. |
| `validate_tables.py` | Gate R | Tables sound, tied to page and owner clause, indexed. |
| `validate_measurements.py` | Gate S | Measurements traceable and canonical. |
| `validate_drawings.py` | Gate T | Drawing registry complete, hash-bound, identity checks hold. |
| `validate_drawing_links.py` | Gate U | Drawing citations reproduce the clause text and point at real sheets. |
| `pilot_checklist.py` | Gate V | Pilot acceptance checklist (master §28) for all six manuals. |
| `verify_answers.py` | Gate Y | Citation verifier over every answer the chat shows. |
| `coverage_audit.py` | Gate Z | Line-by-line coverage of every manual. |
| `validate_entities.py` | Gate AA | Entity layer consistent with the text. |

Gates E, G and H run pytest (`tests/`, `test_manual_frontend_contract.py`, `test_manual_kg_query.py`).

## Shared modules

| Script | Role | Purpose |
|---|---|---|
| `kg_utils.py` | lib | Shared helpers for the validators. |
| `provenance_policy.py` | lib | The only path to `reviewed`/`verified` is a review record. |
| `clause_parser.py` | lib | Layout-aware clause parser. |
| `crossrefs.py` | lib | Cross-reference extraction and resolution. |
| `measurements.py` | lib | Measurement extraction from text and tables. |
| `render_evidence.py` | lib | Highlighted page crop for a piece of evidence. |
| `resolve_manual_hierarchy.py` | lib | Manual, section, subsection hierarchy. |
| `title_block.py` | lib | Title block and alteration table from drawing OCR. |
| `query_manual_kg.py` | lib | Manual-universe query helpers (used by tests). |

## Tools (run by hand)

| Script | Role | Purpose |
|---|---|---|
| `make_review_packet.py` | tool | Offline human-review packet: stratified random sample next to its source page. |
| `apply_reviewed_synonyms.py` | tool | Applies human-reviewed synonym groups to `data/search/synonyms.json`. |
| `ingest_real_questions.py` | tool | Validates double-labelled real engineer questions. |
| `ingest_feedback.py` | tool | Turns exported browser feedback into review work and eval candidates. |
| `build_eval_set.py` | tool | Builds `eval/questions.jsonl`. |
| `eval_retrieval.py` | tool | Evaluates retrieval against `eval/questions.jsonl`. |
| `ocr_pages.py` | tool | OCR of manual pages with no text layer (needs `requirements-ocr.txt`). |
| `ocr_drawings.py` | tool | OCR of raster drawing sheets (needs `requirements-ocr.txt`). |
| `migrate_canonical_ids.py` | tool | Plan or apply legacy-to-canonical id replacements. |
| `normalize_canonical_ids.py` | tool | Report the canonical-id migration plan. |
| `research/benchmark_docling.py` | tool | Research EXP-01: PyMuPDF against Docling. |

## Legacy (not part of the pipeline)

| Script | Role | Purpose |
|---|---|---|
| `build_canonical_pipeline.py` | legacy | DEPRECATED: rebuilds canonical from stale intermediates. Do not run. |
| `ingest_manuals.py` | legacy | DEPRECATED: superseded by `ingest_all_manual_chapters.py`. |
| `build_source_registry.py` | legacy | Early source registry (plan in `docs/archive/`). |
| `segment_manuals.py` | legacy | Early page/block segmentation. |
| `extract_candidates.py` | legacy | Early candidate entity extraction. |
| `validate_knowledge_graph.py` | legacy | Audit of the early multi-layer pipeline. |
| `validate_canonical_kg.py` | legacy | Validator for the prototype canonical core (`data/rdso_canonical_kg.json`). |
| `audit_curated_answers.py` | legacy | Audit of hand-written answers, since removed from the pages. |
| `analyze_rdso_drawing.py` | legacy | Prototype drawing analyser; writes the superseded `data/rdso_drawing_catalog.json`. |
| `extract_drawing_knowledge.py` | legacy | Prototype drawing notes and tables extractor. |
| `visual_diff_engine.py` | legacy | Prototype drawing visual diff. |
