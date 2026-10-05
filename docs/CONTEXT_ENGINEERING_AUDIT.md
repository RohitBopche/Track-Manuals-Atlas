# Context Engineering Audit — 2026-10-05

**Question:** when an AI coding agent (Claude Code, Gemini, Copilot, or similar) opens this repository cold, does it get the right context, quickly and cheaply, and is anything misleading it?
**Scope:** agent instruction files, docs reachable from the root, commands, size and shape of searchable files, git hygiene, CI labels. Pipeline correctness, data quality and UI were out of scope.
**Method:** read the root files, `docs/`, `.github/`, `.gitignore`, `scripts/rebuild_all.py`, `scripts/validate_all.py`; measured file sizes and line lengths; checked that the paths and commands in the docs exist; ran `pytest` and `validate_all.py` on a fresh clone without running the rebuild first.

## Verdict

The project's *knowledge* is well recorded: `PROJECT_MASTER.md` §37 is a careful, honest, dated record with measured results. Agents struggled to *get at it*. Nothing told an agent where to start except a README whose first 200 lines describe a prototype that no longer exists. The authoritative document is 187 KB (about 47k tokens, 2,399 lines), so it is cut off in one read. Two broken code fences made everything after §11 render as code. A single grep over `data/` could return 20 MB from one line. And one documented command would overwrite `index.html`.

Round 1 fixed findings 1 to 6. Round 2 (same day) fixed findings 7 to 15. All 15 are now closed.

## Findings

| # | Sev | Finding | Evidence | Status |
|---|---|---|---|---|
| 1 | P0 | **No agent entry file.** No `CLAUDE.md`, `AGENTS.md` or `.github/copilot-instructions.md`. Agents fell back to the README. | `find` for these names: none | **Fixed:** `CLAUDE.md` (about 60 lines): where the truth lives, exact commands, layout, rules |
| 2 | P0 | **A documented command destroys work.** README §5 "Compiling the Standalone Web App" said to run `scripts/build_updated_app.py`. The script's own docstring says it is deprecated and overwrites `index.html` with an old template. | `README.md` §5; `scripts/build_updated_app.py:1-3` | **Fixed:** README now says do not run it; `CLAUDE.md` repeats it |
| 3 | P0 | **Broken Markdown fences in the master.** Two blocks open with a backtick fence and close with `~~~` (lines 606 and 1486). After §11, code and prose are swapped in every renderer. Agents that read rendered output (or other agents' summaries of it) see §33 (handoff protocol) as code. | the backtick fence opened at line 596 has no matching close | **Fixed:** both fences closed with backticks; pairing check clean |
| 4 | P0 | **Huge single-line generated files pollute search.** `data/rdso_kg_data.js` is 22 MB with a 21.8 MB line; `data/search/search_index.js` is 7.9 MB on one line; there are 7 more one-line bundles. One `grep` hit fills an agent's context. | `awk` max line length per file | **Fixed:** `.ignore` (honoured by ripgrep, so by Claude Code's Grep) lists generated bundles and `data/knowledge-graph/{raw,intermediate,exports,canonical/*.jsonl}`. They are still in git and readable by path. |
| 5 | P0 | **`node_modules/` committed although `.gitignore` excludes it**, while `package-lock.json` (needed by `npm ci` in CI) was in `.gitignore` but committed anyway. Agents get contradictory signals about what is tracked. | `git ls-files node_modules` gave 20 files | **Fixed:** `node_modules/` untracked; `package-lock.json` removed from `.gitignore` |
| 6 | P1 | **Stale gate labels.** README and CI said "gates A to U"; `validate_all.py` runs A to AA (27 gates). | `grep "Gate [A-Z]*" scripts/validate_all.py` | **Fixed:** README says "A to AA"; the CI step label no longer names a range |
| 7 | P1 | **README is mostly wrong for agents.** §1 to §5 (about 200 lines) describe the 3D digital-twin prototype: unverified statistics, a `F:\git\...` tree, `analyze_rdso_drawing.py` at the root (it is in `scripts/`), `docs/RDSO_Knowledge_Graph_Improvement_Blueprint.md` (moved to `docs/archive/`). The "read this first" banner helps, but the bulk still costs about 5k tokens and invites wrong edits. | `README.md` | **Fixed (round 2):** README rewritten (pages, build commands, layout, doc pointers; about 50 lines); prototype text in `docs/archive/PROTOTYPE_README.md` with a banner. |
| 8 | P1 | **Master is too large to load and mixes spec with journal.** §1 to §36 (spec, about 1,575 lines) and §37 (46 sprint logs, about 670 lines) are in one file. §2 "Current Baseline" still describes the pre-audit state. Default read limits truncate around line 2000, which falls inside §37, so §38 to §40 (the current plan) are exactly what gets dropped. | `wc -c`: 187,292 bytes | **Fixed (round 2):** §37 moved to `docs/DELIVERY_LOG.md` with section numbers unchanged (stub left at §37); "State now" block at the top; §2 refreshed. Master 187 KB to 58 KB. |
| 9 | P1 | **`docs/gemini/` is stale and links nowhere.** All links are `file:///f:/my git project/...` (Windows-local); the status files still show P0 as "In Progress"; it calls the master "Read-Only" while the master is updated every sprint. §37 already records that its P0/P1 "complete" claims were overturned. | `grep -l file:/// docs` gives 6 files | **Fixed (round 2):** moved to `docs/archive/gemini/`, banner added, `file:///f:/` links made relative. |
| 10 | P1 | **Tests depend on an untracked rebuild output.** On a fresh clone `pytest` and Gate E fail (`test_form_like_tables_are_flagged_and_demoted` needs git-ignored `data/search/passages.jsonl`). CI is green only because it runs the rebuild first. Agents that run tests before the rebuild see a red baseline and may "fix" the wrong thing. | ran on fresh clone: 275 passed, 1 failed | **Fixed (round 2):** the test reads the committed `data/search/search_index.js` instead; pytest is green on a fresh clone without a rebuild. |
| 11 | P2 | **Handoff protocol (§33) doesn't match practice.** It requires conventional commits (`feat(kg): ...`); none of the last 40 subjects use them. Rules nobody follows teach agents to ignore the rest. | `git log --format=%s` | **Fixed (round 2):** §33 now states the style the history actually uses (plain imperative subject, one concern per commit). |
| 12 | P2 | **`docs/archive/` is about 180 KB of superseded plans** (the largest is 2,220 lines) with conflicting architectures. It is reachable from the root and from search. | `wc -l docs/archive/*.md` | **Fixed (round 2):** `docs/archive/README.md` index and banner; `docs/archive/` added to `.ignore`. |
| 13 | P2 | **`scripts/README.md` is a 12-line placeholder.** It lists 78 scripts with no index. Agents must open files to learn which are pipeline steps, which are gates and which are legacy. | `scripts/README.md` | **Fixed (round 2):** `scripts/README.md` lists all 76 scripts by role (entry, rebuild, gate, lib, tool, legacy); `tests/test_scripts_index.py` fails if it goes stale. |
| 14 | P2 | **Very large hand-edited files.** `expert.html` (10.4k lines, 446 KB) and the deprecated `scripts/build_updated_app.py` (9.9k lines) are expensive to edit by agents. | `wc -l` | **Fixed (round 2):** `build_updated_app.py` deleted. `expert.html` 10,376 to 668 lines: logic moved to `ui/expert.js`, styles to `ui/expert.css` (byte-identical blocks, loaded in the same place); static tests read all three. |
| 15 | P2 | **No cloud-session bootstrap.** No `.claude/settings.json` SessionStart hook, so remote agents start without `pip install`/`npm ci` and without the rebuild that tests need. | no `.claude/` | **Fixed (round 2):** `.claude/settings.json` + `.claude/hooks/session-start.sh` (cloud sessions only): installs Python and Node deps, sets `CHROME_PATH` to the preinstalled Chromium. |

## Validation of this change

- Fence pairing check over `docs/PROJECT_MASTER.md`: no unclosed fence.
- `python scripts/validate_all.py` on a fresh clone without the rebuild: 26 of 27 gates pass. Gate E fails with the same single test before and after this change (finding 10). No data or code paths changed.
- Paths named in `CLAUDE.md` checked to exist (`drawings_registry.jsonl`, `apply_reviewed_synonyms.py`, `kg_utils.py`, `provenance_policy.py`, gate list).
- Browser suites not run (no UI change).

## Validation of round 2

- `python scripts/rebuild_all.py` then `git diff --exit-code -- data/`: clean (rebuild still reproducible).
- `python -m pytest -q` on a tree without `data/search/passages.jsonl`: 277 passed (was 1 failing).
- `python scripts/validate_all.py`: all 27 gates (A to AA) pass.
- `python scripts/run_browser_tests.py` with the preinstalled Chromium: 18/18 before the `expert.html` split and 18/18 after.
- SessionStart hook run by hand with `CLAUDE_CODE_REMOTE=true`: exit 0, `CHROME_PATH` written to the env file.

## Remaining suggestions

- Prototype-era scripts marked legacy in `scripts/README.md` could be deleted after a reference check.
- `ui/expert.js` (6.9k lines) could be split further by feature when it is next changed.
