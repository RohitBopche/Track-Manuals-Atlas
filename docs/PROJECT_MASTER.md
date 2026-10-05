# Track Manuals Atlas — Master Project Specification

> Renamed on 2026-10-01 from "RDSO-Drawings" (the repository and some file paths, ids and older sections still use the old name). The old name described the first prototype, a viewer for RDSO drawings; the project is now an offline knowledge base and graph of Indian Railways manuals (six track manuals so far, more to be added), and the issuing body's name is not part of the product name, so the name does not suggest an official RDSO product.

**Status:** Canonical project document  
**Purpose:** Single source of project direction, architecture, implementation roadmap, data contracts, UX requirements, validation gates, and agent handoff rules.  
**Supersedes:** Multiple overlapping documents previously maintained under `docs/`.  
**Archive policy:** Historical/source documents are retained under `docs/archive/` for traceability; new project decisions belong here.

---

## State now (2026-10-05)

Keep this block short and current; details live in §40 (phase table) and [`DELIVERY_LOG.md`](DELIVERY_LOG.md).

- **Product:** offline pages `index.html` (graph + chat box), `chat.html` (cited answers), `browse.html`, `learn.html`, `expert.html`. No server, no network.
- **Content:** six track manuals (IRPWM 2024, TMM 2020, STMM 2024, USFD 2026, AT Weld 2022, FBW 2022), 1,172 numbered paragraphs plus 219 annexure units; 130 curated concepts with about 35,700 mentions; 59 drawing sheets in the registry. Live counts: `data/knowledge-graph/reports/metrics.json`.
- **Quality bar:** `scripts/rebuild_all.py` is byte-for-byte reproducible; `scripts/validate_all.py` runs gates A to AA; citation verifier (Gate Y) checks every shown answer against its paragraph.
- **Phases:** P1 and P2 closed; P5 about 90%, P6 about 85%, P7 about 75%, P3 and P4 about 45%, P8 not started (see §40).
- **Biggest gaps:** human review (12 of 1,171 paragraphs reviewed); real engineer questions exist only for IRPWM (20); 99 of 103 drawing numbers cited by the manuals have no sheet; no typed domain relations beyond co-mention.

---

## 1. Executive Direction

Track Manuals Atlas (formerly RDSO-Drawings) is evolving from a drawing/PDF visualization prototype into an **offline-first Railway Engineering Knowledge System**.

The product combines:

1. RDSO drawings and drawing revisions.
2. Railway manuals, codes, specifications, letters and circulars.
3. Engineering components, assemblies, materials, measurements and requirements.
4. Evidence and provenance down to document/page/section/clause/drawing region.
5. Search, graph exploration, revision analysis and engineering workflows.
6. Evidence-grounded question answering and future AI assistance.
7. Learning, analytics and knowledge-gap detection.

The graph is **not the product by itself**. It is the relationship and navigation layer over an authoritative knowledge core.

### Core product loop

```text
User question / drawing / identifier
        ↓
Search / retrieval
        ↓
Canonical entity or provision
        ↓
Structured facts + relationships
        ↓
Evidence / source
        ↓
Related knowledge / revisions
        ↓
Engineering workflow / answer
        ↓
Verification / feedback
```

### Non-negotiable principles

- Evidence before explanation.
- Canonical data before visualization.
- Source facts before AI inference.
- Revision awareness everywhere.
- Explicit uncertainty and conflicts.
- Offline-first operation.
- Human review for safety-relevant facts.
- Deterministic, reproducible ingestion.
- Small validated increments instead of broad rewrites.
- One canonical knowledge core, many interfaces.
- UI must never become the authoritative data store.

---

## 2. Current Baseline

The existing application must be improved incrementally rather than replaced.

### Existing product surfaces (2026-10-05)

- `index.html`: simple home page, Three.js knowledge graph with a chat box.
- `chat.html`: offline chat with cited answers, follow-up questions, table rows and concept questions.
- `browse.html`: manuals by chapter, paragraph and annexure.
- `learn.html`: practice cards generated from cited paragraphs.
- `expert.html`: the full original workbench (drawings, revisions, semantic graph modes, intelligence drawer).
- Pipeline: `scripts/rebuild_all.py` (deterministic, about 3 minutes) and `scripts/validate_all.py` (gates A to AA); pytest and headless browser suites; CI runs all of them.

### Historical manual-ingestion baseline

The September 2026 session record reported:

- 6 official railway manuals ingested.
- 1,485 manual pages used for deep chapter extraction.
- 83 chapters catalogued.
- 2,731 statutory clauses extracted.
- 2,157 canonical nodes.
- 3,256 typed edges.
- 121,229 search-index tokens.
- 100% referential integrity in the recorded validation run.
- 8/8 browser/CDP verification tests passed in that recorded run.

> **Correction (§37):** the "2,731 clauses", "2,157 nodes / 3,256 edges" and later "7,321 nodes / 9,305 edges / 8,370 facts" figures are not reproducible from the repository. Quote only `data/knowledge-graph/reports/metrics.json` (generated). At HEAD after P0-R.1/R.2: 6,830 canonical nodes, 9,037 edges, 1,838 manual clauses, 361 tolerance nodes.

These numbers are **baseline/session metrics, not permanent acceptance targets**. Always regenerate current metrics before making claims about the present repository state.

The six recorded manuals were:

1. IRPWM 2024 (ACS 1–14) — 530 pages.
2. USFD Manual 2026 — 157 pages.
3. AT Weld Manual 2022 — 49 pages.
4. FBW Manual 2022 CS 1–5 — 69 pages.
5. Indian Railways Track Machine Manual 2020 — 458 pages.
6. Small Track Machines Manual 2024 — 222 pages.

---

## 3. Product Domains

Maintain two primary knowledge universes.

### 3.1 Manual / Codes universe

Contains:

- manuals;
- editions/revisions;
- chapters;
- sections/subsections;
- clauses/provisions;
- tables;
- figures;
- evidence;
- topics/concepts;
- requirements;
- procedures;
- authorities;
- inspection/acceptance criteria;
- limits/tolerances;
- failures and safety information;
- cross-references;
- letters/circulars where introduced.

### 3.2 Drawing universe

Contains:

- drawings;
- drawing revisions;
- sheets;
- notes;
- components;
- assemblies;
- subassemblies;
- dimensions;
- tolerances;
- materials;
- BOM items;
- geometry;
- drawing-specific requirements and evidence.

### 3.3 Cross-domain rule

For the current release, **do not create direct Manual ↔ Drawing graph edges in the base KG**.

If future integration is required, use a dedicated relationship/evidence layer with:

- source;
- page/sheet/region;
- extraction method;
- confidence;
- verification status.

Candidate future predicates include:

- REFERENCES
- APPLIES_TO
- ILLUSTRATED_BY
- DEFINED_IN
- SPECIFIED_BY
- RELATED_TO

This prevents manual chapters from being polluted by random drawing-derived concepts—the central problem the manual KG v2 work was designed to solve.

---

## 4. Target Architecture

```text
SOURCE LAYER
  PDFs / drawings / manuals / images / field data
        ↓
INGESTION
  parsing / OCR / layout / tables / title blocks
        ↓
EVIDENCE
  pages / clauses / regions / quotes / crops / provenance
        ↓
CANONICAL KNOWLEDGE
  entities / facts / requirements / revisions / relationships
        ↓
RETRIEVAL + GRAPH
  full text / vector / hierarchy / graph / cross-reference
        ↓
APPLICATION
  search / document detail / graph / revisions / workflows / learning
        ↓
OPTIONAL INTELLIGENCE
  grounded QA / semantic retrieval / AI copilot
```

### Authoritative ownership rule

No frontend feature owns engineering truth.

The canonical data/evidence layer owns truth; every interface consumes it.

---

## 5. Canonical Identity and Document Model

Separate logical identity from physical source identity.

```text
DOCUMENT_FAMILY
  ↓
DOCUMENT / MANUAL / CODE / DRAWING
  ↓
EDITION / REVISION
  ↓
SOURCE_FILE
  ↓
PAGE / SHEET
  ↓
CHAPTER / SECTION / CLAUSE / REGION
```

Every canonical entity should have:

- stable machine-safe ID;
- entity type;
- human-readable name;
- aliases;
- status;
- provenance;
- verification state where applicable.

Never use filenames or display names as canonical identity.

Source files should retain content hashes, especially SHA-256.

### Version relationships

Support:

- HAS_EDITION
- HAS_REVISION
- SUPERSEDES
- AMENDS
- MODIFIES
- CORRECTS
- VALID_DURING
- WITHDRAWN_BY

Never infer supersession merely because one document is newer. The source must establish the relationship or applicability logic must explicitly support it.

---

## 6. Manual Structural Contract

Manual structure is authoritative and document-first.

```text
MANUAL
  └── CHAPTER
       └── SECTION
            └── SUBSECTION
                 └── CLAUSE / PROVISION
```

When a manual is selected, the first expansion must show **only its registered chapters**.

A manual must have:

1. Stable document ID.
2. Deterministic ordered chapter registry.
3. One CHAPTER node per registered chapter.
4. One manual-to-chapter ownership edge per chapter.
5. Stable chapter IDs.
6. Page ranges.
7. Structure status.
8. Source-derived semantic content below the structural layer.
9. Provenance on source-derived structural children.

### Derived section/subsection layer

Sections/subsections may be derived conservatively from clause numbering when authoritative headings are unavailable.

Such nodes must be explicitly marked as:

`DERIVED_FROM_CLAUSE_NUMBERING`

They must retain source document, page, source reference/text, extraction method, confidence, and chapter ownership.

A later heading-aware extractor may enrich or replace this derived layer without changing chapter ownership.

### Orphan headings

If a source heading implies a numeric parent that was not extracted:

- preserve the observed heading;
- do not invent the missing parent;
- attach it to the authoritative chapter as a fallback;
- record that the parent was unavailable.

Missing structure is a data-quality signal, not permission to fabricate hierarchy.

---

## 7. Manual Structural Artifacts

The following may be first-class structural artifacts:

- TABLE
- FIGURE
- EVIDENCE

Each must carry:

- deterministic ID;
- source document;
- source page;
- source section/reference;
- source text;
- extraction method;
- confidence;
- parent chapter.

Only label-driven, evidence-backed artifacts should become structural nodes. Random semantic mentions must not create direct manual children.

### Heading coverage diagnostics

The ingestion pipeline should track:

- pages with detected source headings;
- pages containing useful clauses/tables/figures/evidence but no source heading;
- heading coverage ratio;
- empty-content pages.

These diagnostics should drive future extraction improvements without weakening the deterministic hierarchy.

---

## 8. Engineering Knowledge Model

### Entity families

Documents:

- DOCUMENT
- DOCUMENT_FAMILY
- MANUAL
- EDITION
- SOURCE_FILE
- PAGE
- SECTION
- CLAUSE
- TABLE
- FIGURE
- EVIDENCE

Engineering:

- DRAWING
- DRAWING_REVISION
- ASSEMBLY
- SUBASSEMBLY
- COMPONENT
- SUBCOMPONENT
- MATERIAL
- GEOMETRY
- EQUIPMENT
- TOOL
- PART
- BOM_ITEM
- SPARE_PART

Requirements/operations:

- REQUIREMENT
- SPECIFICATION
- STANDARD
- CODE
- TOLERANCE
- MEASUREMENT
- CONSTRAINT
- ACCEPTANCE_CRITERION
- INSPECTION_CRITERION
- PROCEDURE
- SOP
- INSPECTION
- MAINTENANCE_ACTION
- FAILURE_MODE
- DEFECT
- HAZARD
- CAUSE
- EFFECT
- MITIGATION
- AUTHORITY
- ORGANIZATION
- LOCATION
- TOPIC

### Controlled relationships

Use directional, typed relationships such as:

```text
CONTAINS
HAS_EDITION
HAS_REVISION
HAS_PAGE
HAS_SECTION
HAS_CLAUSE
HAS_TABLE
HAS_FIGURE
HAS_EVIDENCE

REFERENCES
CITES
SUPPORTS
APPLIES_TO
GOVERNS
REQUIRES
PROHIBITS
ALLOWS
EXCEPTION_TO

PART_OF
ASSEMBLES
ASSEMBLED_FROM
MATES_WITH
INTERFACES_WITH
CONNECTED_TO
INSTALLED_ON
FASTENED_BY
SPECIFIED_BY
CONSTRAINED_BY
MEASURED_BY
INSPECTED_BY
TESTED_BY
ACCEPTED_BY

PERFORMED_BY
APPROVED_BY
DOCUMENTED_BY
PRECEDES
FOLLOWED_BY
DEPENDS_ON

SUPERSEDES
AMENDS
MODIFIES
CORRECTS
CONFLICTS_WITH
DERIVED_FROM
USED_IN
PROCURED_AS
REPLACED_BY
HAS_BOM_ITEM
HAS_SPARE
```

New relationships must be defined in the controlled vocabulary, validated, documented, and covered by fixtures/tests before broad use.

---

## 9. Engineering Facts

Relationships alone are insufficient. Important values must be first-class facts.

Examples:

- measurements;
- tolerances;
- limits;
- time periods;
- thresholds;
- quantities;
- materials;
- authority;
- responsibility;
- required documents;
- inspection intervals;
- acceptance criteria.

For numeric values store:

- value;
- unit;
- nominal/min/max/bounds where applicable;
- measurement/fact type;
- applicability;
- evidence;
- verification status.

Distinguish:

- specified;
- measured;
- observed;
- derived;
- inferred.

An inferred value must never be presented as an official requirement.

---

## 10. Evidence and Provenance Contract

Every safety-relevant or decision-relevant claim must be traceable.

Evidence should support:

- source document;
- edition/revision;
- page/sheet;
- chapter/section/clause;
- source text;
- image/region/crop where applicable;
- extraction method;
- extraction timestamp;
- confidence;
- verification status;
- reviewer/review date where applicable.

Controlled evidence states:

- EXTRACTED
- VERIFIED
- DERIVED
- INFERRED
- CONFLICTING
- REJECTED
- UNKNOWN

Required navigation:

```text
Answer
  → Provision / Fact
    → Evidence
      → Source page / sheet / crop
```

The user must not need to manually locate the cited source.

---

## 11. Ingestion Pipeline

The deterministic pipeline is:

```text
Source files
  ↓
Validate + hash
  ↓
Classify document
  ↓
Extract native PDF text/layout
  ↓
OCR only where required
  ↓
Detect metadata
  ↓
Detect hierarchy
  ↓
Extract clauses/provisions
  ↓
Extract tables/figures/notes
  ↓
Extract references
  ↓
Extract entities/facts/requirements
  ↓
Normalize
  ↓
Resolve identities
  ↓
Score confidence
  ↓
Human review for uncertain/critical content
  ↓
Canonical publication
  ↓
Validate
  ↓
Build full-text/vector/graph exports
```

### Raw/intermediate/canonical separation

```text
data/
  manuals/
    raw/
    intermediate/
    canonical/
    evidence/
    indexes/
  drawings/
  shared/
```

Never overwrite raw source extraction with normalized output.

---

## 12. Drawing Extraction

Drawings are engineering artifacts, not ordinary PDFs.

Extract when available:

- drawing number;
- title;
- revision;
- issue/effective date;
- sheet number;
- scale;
- units;
- title-block fields;
- dimensions;
- tolerances;
- materials/grades;
- notes/callouts;
- BOM;
- part/assembly references;
- referenced drawings;
- approvals;
- supersession information.

Use deterministic extraction first for identifiers, dates, revisions and dimensions; layout/OCR/computer vision for difficult structures; human review for critical dimensions and requirements.

Machine-extracted dimensions remain unverified until validated.

---

## 13. Manuals and Codes Extraction

The manual pipeline must capture:

- manual identity;
- edition/revision;
- chapter/section hierarchy;
- clauses;
- definitions;
- requirements;
- procedures;
- responsibilities;
- authorities;
- inspection/acceptance criteria;
- exceptions;
- tables;
- figures;
- notes/warnings;
- cross-references;
- limits/tolerances;
- terminology and aliases;
- source evidence.

A procedure should preserve source-defined ordering.

A rule may be decomposed as:

```text
CONDITION
 → REQUIREMENT
 → ACTION / PROCEDURE
 → AUTHORITY
 → DOCUMENTATION
 → INSPECTION / ACCEPTANCE
 → EXCEPTION
```

This structured interpretation never replaces the original provision text.

---

## 14. Cross-References

References are first-class relationships.

Store:

- source provision;
- target manual/document;
- target edition;
- target chapter/section/paragraph;
- reference text;
- evidence;
- resolution state.

Resolution states:

- RESOLVED
- AMBIGUOUS
- BROKEN
- EXTERNAL
- NOT_FOUND

Cross-reference resolution is required for reliable multi-hop question answering.

---

## 15. Hybrid Retrieval

Do not build `PDF → embeddings → chatbot`.

Use:

```text
Question
  ├── exact identifier search
  ├── full-text search
  ├── metadata filtering
  ├── semantic/vector search
  └── graph/cross-reference traversal
            ↓
      candidate evidence
            ↓
        re-ranking
            ↓
      applicability check
            ↓
      conflict check
            ↓
      evidence set
```

Ranking should generally prioritize:

1. exact identifier/provision;
2. exact title/name;
3. lexical relevance;
4. metadata relevance;
5. semantic similarity;
6. graph/context relevance.

Vector search must not replace structural/lexical retrieval.

---

## 16. Question Understanding and Grounded QA

Classify questions such as:

- RULE_LOOKUP
- PROCEDURE_LOOKUP
- AUTHORITY_LOOKUP
- SOURCE_LOOKUP
- EXCEPTION_LOOKUP
- COMPARISON
- DEPENDENCY_LOOKUP

Extract:

- activity/work;
- department;
- component/equipment;
- context/location;
- rule type;
- authority;
- time/version;
- named manual;
- known identifier.

### QA pipeline

```text
User question
  ↓
Intent + entity extraction
  ↓
Hierarchy filtering
  ↓
Hybrid retrieval
  ↓
Cross-reference expansion
  ↓
Graph traversal
  ↓
Evidence re-ranking
  ↓
Version/applicability check
  ↓
Conflict check
  ↓
Bounded evidence context
  ↓
LLM synthesis
  ↓
Citation verification
  ↓
Answer
```

The LLM must never receive unrestricted corpus context when a bounded evidence set can be supplied.

---

## 17. Answer Contract

A standard engineering answer should expose:

1. Direct answer.
2. Applicable requirement/rule.
3. Procedure/ordered steps.
4. Authority/responsibility.
5. Exceptions.
6. Related provisions.
7. Manual/document.
8. Edition/revision.
9. Chapter/section/paragraph.
10. Page/sheet.
11. Evidence excerpt.
12. Applicability/status.
13. Confidence/verification.
14. Conflict warning where applicable.

Every substantive claim should be traceable.

---

## 18. Conflict and Applicability Handling

Never silently resolve conflicting requirements.

When conflicts exist, show:

- both provisions;
- source versions;
- scope;
- dates;
- explicit precedence if documented;
- evidence.

If precedence cannot be established:

**Conflict/ambiguity detected — manual verification required.**

Do not select a provision merely because retrieval ranked it higher.

---

## 19. Search and UX

The primary workflow is:

```text
Search
  ↓
Results
  ↓
Entity / Provision detail
  ↓
Evidence / Source
  ↓
Related knowledge
  ↓
Graph exploration
```

Search must support:

- drawing number;
- drawing title;
- component;
- material;
- standard/specification;
- manual/document;
- clause/requirement;
- revision;
- defect/failure;
- procedure/inspection;
- measurement/tolerance;
- general engineering keywords.

### Result cards

Show:

- entity type;
- display name;
- canonical ID where useful;
- revision/edition;
- short description;
- evidence/source indicator.

For drawings show number + title together.

### Context preservation

Navigation must preserve:

- search query;
- selected entity;
- graph mode;
- filters;
- revision context.

### Accessibility

- keyboard navigation;
- visible focus;
- accessible labels;
- no colour-only meaning;
- readable at increased zoom;
- explicit empty/loading/error states;
- bounded large result sets.

---

## 20. Knowledge Graph UX

The graph is a supporting surface.

Required interactions:

- focus entity;
- expand one hop;
- filter entity types;
- filter relationship types;
- highlight path;
- explain why connected;
- open evidence from edge/fact;
- preserve context;
- return to previous state.

For manuals:

```text
Manual
  → Chapter
    → Section
      → Provision
        → Related knowledge
```

Semantic neighborhoods should expand on demand rather than flooding the universe.

---

## 21. Recommended Data/Technology Architecture

Initial low-cost architecture:

| Concern | Direction |
|---|---|
| Processing | Python |
| PDF | PyMuPDF |
| OCR | OCRmyPDF/Tesseract; PaddleOCR where justified |
| Database | PostgreSQL |
| Full text | PostgreSQL FTS |
| Vector | pgvector |
| Graph | Relational graph initially |
| API | FastAPI |
| Frontend | Existing application, modularized incrementally |
| Local AI | Configurable local inference |
| Cloud AI | Provider abstraction |
| Validation | JSON Schema + pytest |
| Browser testing | E2E/CDP |

Neo4j/Apache AGE/OpenSearch should be introduced only when workload evidence justifies the operational cost.

PostgreSQL remains the authoritative metadata/evidence registry.

---

## 22. Repository Direction

Keep the existing root application stable during migration.

Target direction:

```text
RDSO-Drawings/
├── index.html
├── manuals/
├── drawings/
├── data/
│   ├── manuals/
│   │   ├── raw/
│   │   ├── intermediate/
│   │   ├── canonical/
│   │   ├── evidence/
│   │   └── indexes/
│   ├── drawings/
│   └── shared/
├── scripts/
│   ├── manuals/
│   ├── drawings/
│   ├── ingestion/
│   ├── validation/
│   └── search/
├── src/
│   ├── knowledge/
│   ├── manuals/
│   ├── drawings/
│   ├── evidence/
│   ├── search/
│   ├── graph/
│   └── qa/
├── tests/
│   ├── manuals/
│   ├── drawings/
│   ├── knowledge/
│   ├── search/
│   └── qa/
└── docs/
    ├── PROJECT_MASTER.md
    └── archive/
```

Do not create all target directories at once. Migrate incrementally.

---

## 23. Historical/Existing Pipeline Components

The previous implementation record identified these important components:

- `scripts/build_source_registry.py`
- `scripts/segment_manuals.py`
- `scripts/extract_candidates.py`
- `scripts/ingest_all_manual_chapters.py`
- `scripts/build_canonical_pipeline.py`
- `scripts/validate_knowledge_graph.py`
- `scripts/build_updated_app.py` (deleted 2026-10-05: deprecated, overwrote `index.html`; see git history)
- `tests/verify_kg_manuals.js`

The exact current state must be inspected before modifying or replacing any of them.

Existing generated artifacts previously included:

- source registry;
- extracted pages;
- candidate entities/relationships;
- normalized measurements;
- review queue;
- canonical nodes/edges;
- requirements;
- graph export;
- search index;
- manual knowledge export.

Generated metrics must always be regenerated rather than trusted from historical documentation.

---

## 24. Validation Gates

### Gate A — Source

- file exists;
- hash recorded;
- source identity valid;
- duplicates detected.

### Gate B — Structure

- valid manual root;
- deterministic chapter order;
- chapter ownership;
- valid section/subsection ownership;
- page bounds valid.

### Gate C — Identity

- stable IDs;
- no accidental duplicates;
- aliases explicit;
- source file and logical document identities separated.

### Gate D — Graph

- valid endpoints;
- controlled relationship vocabulary;
- correct direction;
- no duplicate logical edges;
- no impossible revision cycles;
- Manual/Drawing isolation enforced.

### Gate E — Evidence

- every evidence reference resolves;
- page/sheet exists;
- provenance complete;
- verification state valid.

### Gate F — Engineering semantics

- units normalized;
- bounds coherent;
- applicability explicit;
- conflicts represented;
- inferred values distinguished.

### Gate G — Publication

Only validated canonical data feeds production search/graph exports.

---

## 25. Continuous Engineering Loop

Every implementation iteration should follow:

```text
Inspect current repository
  ↓
Check recent work / overlap
  ↓
Select one coherent task
  ↓
Implement smallest safe change
  ↓
Run focused tests
  ↓
Run relevant validation
  ↓
Run regression suite
  ↓
Inspect actual UI/data output
  ↓
Commit only validated work
  ↓
Record next priority
  ↓
Repeat
```

If a continuous GitHub workflow is used, it should:

1. rebuild authoritative manual structure;
2. rebuild canonical KG;
3. validate structure/isolation/provenance;
4. run publication validation;
5. detect generated-data drift;
6. report failures;
7. refresh deterministic artifacts only when appropriate.

---

## 26. Implementation Roadmap

### P0 — Foundation and reliability

1. Inspect current repository state.
2. Confirm current manual inventory.
3. Confirm current chapter/section/provision coverage.
4. Validate source registry and hashes.
5. Validate evidence integrity.
6. Establish one unified validation command.
7. Establish reproducible regression baseline.
8. Add CI validation.

**Exit:** deterministic canonical data can be validated reproducibly.

### P1 — Manual structure and browsing

1. Complete manual hierarchy.
2. Chapter tree.
3. Section/subsection navigation.
4. Provision detail.
5. Source page opening.
6. Search result cards.
7. Context preservation.

**Exit:** a user can browse manuals structurally and reach source evidence.

### P2 — Evidence and cross-reference intelligence

1. Evidence registry.
2. Source highlighting/crops.
3. Cross-reference extraction.
4. Reference resolution.
5. Broken/ambiguous reference dashboard.
6. Evidence-backed graph edges.

**Exit:** multi-hop source navigation works reliably.

### P3 — Drawing intelligence

1. Drawing identity.
2. Revision lineage.
3. Title-block extraction.
4. Notes/tables/BOM.
5. Dimensions/tolerances.
6. Drawing evidence.
7. Revision comparison.

**Exit:** drawings become structured engineering artifacts.

### P4 — Engineering graph intelligence

1. Typed relationship filters.
2. Dependency trace.
3. Failure analysis.
4. Procurement/BOM.
5. Inspection mode.
6. Path finding.
7. Why-connected explanation.

**Exit:** graph answers concrete engineering relationship questions.

### P5 — Hybrid retrieval

1. Exact search.
2. Full-text search.
3. Metadata filters.
4. Vector retrieval.
5. Graph traversal.
6. Re-ranking.

**Exit:** natural-language queries retrieve relevant evidence.

### P6 — Evidence-grounded QA

1. Intent detection.
2. Retrieval.
3. Evidence ranking.
4. Version/applicability checks.
5. Conflict detection.
6. Answer synthesis.
7. Citation verification.

**Exit:** questions produce source-backed answers.

### P7 — Reliability, learning and analytics

1. Regression question suite.
2. Answer evaluation.
3. Learning paths.
4. Flashcards/practice questions.
5. Knowledge-gap detection.
6. Search analytics.
7. Review queues.

### P8 — Optional AI copilot / digital twin

Only after evidence integrity and retrieval are mature:

- Ask the Graph;
- explain this node;
- compare revisions;
- explain conflicts;
- generate learning material;
- drawing-to-geometry mapping;
- inspection overlays;
- grounded AI copilot.

---

## 27. First Manual Pilot Strategy

Do not semantically ingest all manuals simultaneously.

Select one complete approximately 500-page manual and prove:

```text
PDF
 → source registry
 → page segmentation
 → hierarchy
 → provisions
 → evidence
 → cross-references
 → search
 → question
 → grounded answer
 → citation
```

Then scale the same deterministic pipeline to the remaining manuals.

This reduces extraction risk and prevents the UI from becoming the debugging environment.

---

## 28. Pilot Acceptance Criteria

For one complete manual:

- all pages registered;
- hierarchy represented;
- chapter order deterministic;
- provisions preserved where detectable;
- source pages resolvable;
- full-text search works;
- representative natural-language queries retrieve evidence;
- citations resolve;
- source page opens;
- cross-references resolve or are explicitly classified;
- uncertain extraction is flagged;
- no answer is generated without retrieved evidence;
- regression tests exist;
- rerunning ingestion produces deterministic structural output.

---

## 29. AI Guardrails

The AI layer must:

1. Never invent a rule.
2. Never invent a paragraph number.
3. Never invent a page/sheet.
4. Never invent dimensions or standards.
5. Never silently change source meaning.
6. Never present inference as official text.
7. Never ignore version/applicability conflicts.
8. Prefer primary source evidence.
9. Preserve citations.
10. Surface uncertainty.
11. Require human verification for unresolved or safety-critical conflicts.

---

## 30. Offline-First and Security

Offline-capable functions should include:

- manual browsing;
- drawing browsing;
- full-text search;
- source viewing;
- evidence inspection;
- graph exploration;
- revision comparison;
- local calculations;
- local QA where a local model is configured;
- exports/reports.

Security/reliability requirements:

- immutable raw sources;
- content hashes;
- audit logs;
- no secrets in datasets;
- controlled model/provider configuration;
- access control for central deployments;
- safe uploaded-document handling;
- no silent source replacement.

---

## 31. Metrics

Measure outcomes, not implementation volume.

### Search

- exact identifier success;
- zero-result rate;
- relevant-result rate;
- time to useful provision/entity.

### Evidence

- important facts with evidence;
- evidence resolution rate;
- verification coverage.

### Revision

- structured revision lineage coverage;
- comparison success;
- downstream impact coverage.

### Graph

- successful path queries;
- useful relationship exploration;
- unnecessary expansion reduction.

### QA

- citation coverage;
- unsupported-claim rate;
- conflict detection;
- human validation rate.

### Data quality

- dangling references;
- broken cross-references;
- duplicate entities;
- stale editions;
- unresolved conflicts;
- low-confidence candidates;
- review queue age.

Do not optimize for node count, edge count, animation complexity, or embedding count.

---

## 32. Testing Strategy

Maintain multiple layers:

### Data tests

- schema validation;
- ID uniqueness;
- relationship integrity;
- manual/drawing isolation;
- provenance completeness;
- page bounds;
- version consistency.

### Extraction tests

- representative manual chapter fixtures;
- heading detection;
- clause parsing;
- table/figure extraction;
- reference resolution.

### Search tests

- exact identifier;
- chapter/provision;
- natural-language query;
- no-result behavior;
- revision filtering.

### Browser/E2E

At minimum validate:

- application startup;
- manual universe;
- manual chapter expansion;
- search;
- result selection;
- provision detail;
- source/evidence navigation;
- drawing workflow;
- graph focus;
- context restoration.

The historical 8-test manual CDP suite should be treated as a regression asset, not as proof of current health.

---

## 33. Agent Handoff Protocol

Before every change:

1. Inspect current HEAD.
2. Inspect recent commits.
3. Inspect active PRs/work.
4. Inspect exact files to change.
5. Identify overlapping changes.
6. Do not overwrite active work.

Choose one small coherent task.

Every iteration should report:

```text
Inspected:
- current HEAD
- relevant files
- active work

Changed:
- files
- behavior

Validation:
- tests
- data validation
- build/manual checks

Commit:
- SHA
- message

Next priority:
- one task
```

Commit messages (changed 2026-10-05 to match the history; conventional-commit prefixes were never used in practice):

- Subject: one plain sentence in the imperative saying what changed and, if it closes a phase, which (for example "Close phase P2: explain every unresolved reference ...").
- One concern per commit; generated data is committed together with the code that generates it.
- Body: what was measured and what is still open, when that is not obvious from the subject.

Never commit generated junk or secrets.

---

## 34. Guardrails Against Premature Complexity

Do not prematurely:

- rewrite the entire frontend;
- replace Three.js;
- migrate all IDs;
- introduce Neo4j/PostgreSQL/OpenSearch merely for architectural fashion;
- build an LLM answer layer before evidence integrity;
- rebuild the entire graph without demonstrated need;
- delete legacy data without reference audits;
- remove source PDFs;
- optimize graph appearance instead of engineering workflows.

Prefer:

- deterministic extraction;
- evidence visibility;
- revision context;
- structured facts;
- controlled relationships;
- focused regression tests;
- incremental migration;
- offline operation.

---

## 35. Final Target State

```text
                 RAILWAY ENGINEERING KNOWLEDGE SYSTEM

Sources
  ↓
Document Structure
  ↓
Evidence + Provenance
  ↓
Canonical Knowledge Core
  ├── Manuals / Codes
  ├── Drawings
  ├── Requirements
  ├── Procedures
  ├── Components
  ├── Revisions
  ├── Failures
  └── BOM / Procurement
          ↓
  Search + Graph + Versions
          ↓
  Hybrid Retrieval
          ↓
  Evidence Ranking
          ↓
  Grounded Answer / Workflow
          ↓
  Source Page / Drawing Sheet
```

The end state is not a larger graph.

It is a system where an engineer can move from a question, drawing number, component, rule, or requirement to the relevant canonical knowledge, applicable revision, supporting evidence, related engineering context, and actionable workflow—with uncertainty and conflicts visible.

---

## 36. Canonical Project Decision

From this point forward:

**This file is the project-level source of truth for architecture, roadmap, quality gates, and implementation direction.**

Historical plans and session records remain available only as archived evidence.

New project decisions should update this document rather than create another parallel blueprint.

---

## 37. Delivery Log (moved)

The dated audit and sprint results (§37.1 to §37.46 and later entries) now live in [`docs/DELIVERY_LOG.md`](DELIVERY_LOG.md), with the same section numbers. Add new results there; record phase changes in §40 here.

---

## 38. Plan for Remaining Work (post P0-R.1/R.2)

**Ordering principle:** data truth first, then retrieval, then answers, then learning. Each work package (WP) is one small validated increment: it ends with a gate or test that fails before the change and passes after, a conventional commit, and an updated metrics file. Do not start a WP whose dependency is open.

### 38.1 Work packages

| WP | Title | Depends | Deliverable | Acceptance test (must fail today) |
|---|---|---|---|---|
| **P0-R.3 (DONE, §37.8)** | Provenance re-baseline | R.2 | Every non-drawing node/edge/evidence/requirement is `machine_extracted` unless a review record exists; remove false `raster_blueprint_crop_and_transcription`/confidence 1.0 stamps on text-derived facts; add `reviews.jsonl` (reviewer, date, decision) as the only path to `reviewed`/`verified`. | Gate M: no `verified` without a review record; no fact whose `extraction_method` contradicts its source type. |
| **P0-R.4 (DONE, §37.9)** | Evidence on every edge and clause | R.3 | Evidence record carries `page_number`, `bbox` (PyMuPDF word boxes), `page_sha256`, `source_pdf_sha256`; every edge lists `evidence_ids`. | Gate D extended: 0 edges without evidence (structural HAS_SECTION edges cite the heading evidence); every evidence page hash matches the PDF on disk. |
| **P0-R.5 (DONE, §37.9)** | Metrics as single truth | R.2 | `metrics.json` extended (short clauses, non-extractable pages, per-manual coverage); docs/UI read only it; a CI step diffs regenerated vs committed. | CI fails if committed metrics differ from regenerated. |
| **P0-R.6 (DONE, §37.10)** | Clause-boundary repair | R.2 | Extractor rewrite for paragraph bodies: numbering monotonic per chapter, reject values outside manual range (`PARA_5300`), drop header/annexure pseudo-clauses, join body until next valid paragraph; per-manual detected-vs-kept reconciliation report. Target: short clauses under 5%, IRPWM kept/detected above 90%. Benchmark against Docling result in `research/` before choosing the parser. | Gate L ratchet tightened stepwise; new gate for para-number monotonicity and range. |
| **P0-R.7 (DONE, §37.10)** | OCR for image-only pages | none | OCR (offline Tesseract or Docling) for the 64 pages without text; `extraction_method: ocr`, per-page confidence, low-confidence pages enter the review queue. | 0 pages with `is_extractable=false` and no OCR record. |
| **P0-R.8 (DONE, §37.9)** | Portable browser tests + CI | none | Env-driven Chrome path, headless flags, repo-relative artifacts; a `run_browser_tests.py`; CI job on all branches and PRs including browser tests; stop committing regenerated PNGs (upload as CI artifacts). | Fresh Linux CI runs the CDP suites green. |
| **P0-R.9 (DONE, §37.9)** | Repo hygiene | none | Untrack `__pycache__`, `index.html.bak`, `scratch/`; enforce conventional commits and one concern per commit; retire `docs/gemini/*` status claims (link to §37). | `git ls-files` contains none of those paths. |
| **P0-R.10 (DONE, §37.9)** | Bootstrap | none | `validate_all.py` checks/installs dependencies (or prints exact fix); dependency versions pinned. | Fresh clone: one command yields a green run. |
| **P1-R.1 (DONE, §37.10)** | Frontend reads canonical only | R.2 | Remove `RDSO_MANUALS_KNOWLEDGE` reads from `index.html`; provision cards use canonical `text`/`page`/`evidence_ids`; drop the derived legacy view once unused. | Test: card text equals canonical node text; grep gate for `RDSO_MANUALS_KNOWLEDGE` = 0. |
| **P1-R.2 (PARTIAL, §37.10)** | Honest P1 sign-off | R.6 | Tick the pilot checklist (§28) for IRPWM with evidence links; only then scale to other manuals. | Every checklist line has a reproducible command or test. |
| **P2.1 (DONE, §37.11)** | Cross-reference extraction and resolution | R.6 | Extract "Para N", "Annexure", "Chapter", "Rule", external IS/IRS/RDSO refs (~640 in IRPWM); classify `RESOLVED / AMBIGUOUS / EXTERNAL / NOT_FOUND`; edges `REFERENCES` with evidence; broken-reference report. | Every reference in the raw text is classified; 0 unclassified; resolved targets exist. |
| **P2.2 (PARTIAL, §37.11)** | Source highlighting | R.4 | Render page image with evidence `bbox` highlight (PyMuPDF, offline); UI opens the highlighted region, not just the page. | Test opens a clause and finds the highlighted rect over the quoted words. |
| **P2.3** | Measurement and requirement facts | R.6 | Structured `Measurement {subject, quantity, comparator, value, unit, applies_to, clause_id, evidence}` replacing bare tolerance nodes; requirement priority from modal verbs ("shall/should/may") with reviewed overrides. | Every tolerance has a subject and comparator; sample of 100 reviewed with at least 95% precision. |
| **P5.1 (DONE as BM25, §37.11)** | Offline retrieval core | R.6 | SQLite FTS5 (BM25) over clause text and headings in a single `.db` served with the app; identifier and para-number exact match; abbreviation/synonym dictionary (SSE/P.Way, CMS, USFD, ...); filters by manual/chapter/type/edition. | Retrieval eval set (below): Recall@5 at least 0.85 on keyword and identifier queries. |
| **P5.2** | Semantic layer | P5.1 | Small local embedding model (quantised, CPU) with an ANN index built offline; hybrid score = BM25 + vector + graph proximity; cross-encoder re-rank optional. Model file versioned and hashed. | Recall@5 at least 0.90 on natural-language set; no network calls (test blocks sockets). |
| **P6.1 (PARTIAL, §37.12)** | Grounded answers | P5.1 | Extractive answer builder: top evidence spans, quoted with citation (manual, para, page, evidence id); confidence from retrieval scores and agreement; explicit "insufficient evidence" refusal below threshold; conflict/applicability flags. Replace the 13 hand-written answers and their hard-coded confidences; keep them as regression questions. | 0 answers without a citation; refusal correct on the out-of-corpus set; every quoted span verifiable in the source text. |
| **P6.2** | Optional local LLM | P6.1 | Optional offline small LLM (llama.cpp class) only to rephrase extractive answers; output checked by a citation verifier that rejects any sentence not supported by retrieved spans. | Verifier rejects seeded hallucinations in tests. |
| **P7.1 (STARTED, §37.11)** | Evaluation harness | P5.1 | `eval/questions.jsonl` (start 150: 60 keyword, 40 natural-language, 20 identifier, 15 conflict/revision, 15 out-of-scope), each with gold clause ids and page; `scripts/eval_retrieval.py` prints Recall@k, MRR, refusal precision; results tracked per commit; regression gate. | Metrics file changes are diffed in CI; drops beyond tolerance fail the build. |
| **P7.2 (DONE, §37.12)** | Local feedback capture | P6.1 | Opt-in local log (IndexedDB/JSONL): query, results shown, clicked evidence, thumbs up/down, "wrong page" flag; never leaves the machine; exportable. | Log records round-trip; schema validated. |
| **P7.3 (PARTIAL, §37.12)** | Self-improvement loop | P7.1, P7.2 | Nightly/on-demand job: (a) zero-result and low-confidence queries into `review_queue`; (b) suggested synonyms/aliases from co-clicked queries, applied only after reviewer approval; (c) accepted corrections become new eval questions; (d) re-index and re-run eval, refusing to publish if metrics regress. Dashboard of knowledge gaps per manual/chapter. | An accepted correction changes the answer to that query, and the eval gate stays green. |
| **P7.4** | Learning content from evidence | P6.1 | Flashcards/quizzes generated only from cited clauses, stored with their clause ids; remove hand-authored quiz facts not traceable to a clause. | Every card links to a clause id and page. |
| **P3 / P4** | Drawings and engineering graph | P2.3 | As specified in §26; do not begin until manuals are proven. | Per §26 exit criteria. |
| **Scale** | Roll out to remaining manuals | P1-R.2, P2.1 | Apply pipeline to USFD, AT Weld, FBW, TMM, STMM one at a time using the IRPWM acceptance checklist. | Same checklist per manual. |

### 38.2 Recommended sequence and effort (relative)

1. **Sprint A, data truth:** R.3, R.4, R.5, R.10, R.9, R.8 (small each; R.4 is the largest).
2. **Sprint B, extraction quality:** R.6 (largest risk; benchmark Docling vs current parser first), R.7, P1-R.1, P1-R.2.
3. **Sprint C, retrieval:** P7.1 eval set first (so improvements are measurable), then P5.1, then P2.1 and P2.2 in parallel.
4. **Sprint D, answers:** P6.1, P2.3, then P5.2.
5. **Sprint E, self-improvement:** P7.2, P7.3, P7.4, then optional P6.2.
6. **Then** scale to the other five manuals, and only after that P3/P4.

### 38.3 Evaluation set design (needed before retrieval work)

- Source questions from real usage: senior engineers' typical queries (limits, intervals, who is responsible, procedure for X, difference between revisions), plus queries mined from the manuals' own headings.
- Each item: question, gold clause ids, acceptable pages, category, expected behaviour (`answer` or `refuse`).
- Keep the 13 existing hand-written Q&A items and the browser test questions as the first entries.
- Two-person review of gold labels; inter-reviewer disagreement is itself logged as a gap.

### 38.4 Risks and mitigations

| Risk | Mitigation |
|---|---|
| Extractor rewrite (R.6) changes clause ids, breaking links | Keep an id-alias map (`identity_aliases.json`); Gate B already audits references; migrate in one commit with the map. |
| Machine-extracted text is wrong on safety limits | Priority review queue for any clause containing numbers with units and "shall/mandatory"; answers show the extraction/review state. |
| OCR errors in scanned pages | Store confidence; show "OCR" badge; exclude low-confidence spans from extractive answers. |
| Offline embedding model size on low-end PCs | Ship BM25 only as the default; embeddings optional; measure on a low-spec machine. |
| Scope creep into an LLM before retrieval quality is proven | §34 guardrail: P6.2 is blocked until the P7.1 metrics meet target. |
| Agents overwrite each other's status docs | Status lives only in §37/§38 and `metrics.json`; other logs are non-authoritative. |

### 38.5 Definition of done for the product goal

An engineer can type a natural-language question offline and receive, in under 2 seconds on a modest laptop, an answer composed of quoted source spans with manual/paragraph/page citations that open on a highlighted region; weak or conflicting evidence is stated, not hidden; every wrong or missing answer reported by users becomes a reviewed correction and a permanent regression question; and all published metrics come from one generated file that CI recomputes.


### 38.6 Notes from P0-R.3

- The 13 hand-written QA answers and the UI still show hard-coded `VERIFIED`/0.99 badges (`CANONICAL_QA_DATABASE`). They are not canonical data, so Gate M cannot see them; they are replaced by computed confidence and review state in P6.1 and must not be presented as reviewed before then.
- Drawing-derived nodes (transcribed from crops) were downgraded too: no drawing fact has a human review record either. The review queue should start with safety-relevant numeric limits and the pilot drawings.
- `scripts/build_canonical_pipeline.py` is deprecated (it would re-stamp everything `verified`); `unify_manual_canonical.py` is the generator until the P0-R.6 extractor rewrite replaces its input.

### 38.7 Revised order after Sprint C

1. **Independent evaluation first (P7.1 completion).** Collect 100+ real questions from engineers (not derived from clause text), have a second reviewer label gold clauses, and report them as a separate `real` category. Decide on the semantic layer (P5.2) only after this set shows where BM25 fails; the informal probe suggests misses come from paraphrase, tables and poor titles.
2. **Retrieval quality fixes that need no model:** repair clause titles for decimal manuals (done, Sprint F1), ~~index table rows as structured records~~ (done, Sprint E1; row-aware answers Sprint F3, proforma tables still indexed), add reviewed synonyms from the misses. Re-measure on the independent set.
3. **Grounded answers (P6.1):** promote the extractive card to the only answer path, retire the 13 curated answers into regression questions (they still show hard-coded `VERIFIED`), add sentence-level extraction of the answering span with per-claim citation, conflict and revision flags, and a refusal rule tuned on the independent set.
4. **Feedback loop (P7.2, P7.3):** local log of queries, clicks and thumbs; zero-result and low-coverage queries into the review queue; accepted corrections become eval questions.
5. **Then** P5.2 (embeddings, only if step 1 justifies it), ~~table extraction, P2.3 measurements~~ (done, Sprint E), and rolling the remaining checks to drawings.

---

## 39. Interface and experience upgrade plan (2026-10-01)

### 39.1 Why the interface felt confusing

The main page (`index.html`) was built as a research console: a 3D graph that opens first, several drawers and tabs, and vocabulary from the data model ("universes", "nodes", "evidence"). There is no single obvious first action, the answer area is one panel among many, and the first screen takes seconds to appear. The chat page added later was simpler but had little structure: no way to choose a manual, no history, no visual choice, and every answer had the same weight whether it was strong or doubtful. Nothing here was measured with users; this diagnosis is a design judgement.

Principles for the rework: one obvious task on the first screen (ask a question); the evidence always one click away and never hidden; advanced material behind "Details" or an Expert mode; plain words; everything works offline; readable for everyone by default (tested contrast, size and spacing controls, keyboard use).

### 39.2 Done in this sprint (Phase 1): a simple front door, `chat.html`

- **Nine themes** from one shared stylesheet (`ui/themes.css`, preferences in `ui/theme.js`): Match my device, Light, Dark, Solarized light, Solarized dark, Paper, Nord, Signal (night, amber) and High contrast. Every theme is checked by `tests/test_ui_themes.py` against WCAG contrast for the colour pairs the pages use (4.5:1 for text and links, 7:1 for High contrast). The two Solarized themes are Solarized-inspired and adjusted for contrast, because the original palette fails the 4.5:1 rule for body text.
- **Appearance panel (Aa):** theme swatches, four text sizes, comfortable or compact spacing, four reading fonts (standard, easy to read, serif, mono), reset. Choices are kept on this computer.
- **Simple answer card:** the answer first (the question's own words highlighted), one source button and a plain-word confidence ("Strong match", "Likely match", "Not sure"; shown with a dot and a word, never colour alone), then Copy (with the source), Save, thumbs; everything else (values, sub-paragraphs, drawings, other relevant text, full paragraph, whole table) under "Details"; the next questions under "Ask next".
- **Page viewer** beside the answer: the source button opens the manual at the cited page (and the highlighted crop when it has been rendered) without leaving the page; a full-screen sheet on phones.
- **Search in one manual** (strict, from a drop-down or the command palette), history and saved answers in a side panel (kept locally, clearable), a **command palette** (Ctrl+K: switch theme or manual, jump to a paragraph by typing "IRPWM 429", new chat, print), keyboard shortcuts ("/" to type, Esc to close panels, Up arrow to recall the last question), a clean **print** layout, an empty state with six topic cards, and a link from the old main page ("Ask the manuals").
- Tested by the 15th browser suite (themes, size, palette, strict scope, history and saved answers, keyboard, table answers, local feedback, escaping) and the contrast tests.

Not measured: whether it is actually less confusing for an engineer. That needs 3 to 5 people using it for twenty minutes (see 39.5).

### 39.3 Phased plan

| Phase | Content | Value | Effort |
|---|---|---|---|
| 1 (done) | Simple chat front door, themes, settings, scope, history, saved answers, viewer, palette | high | done |
| 2 (partly done: shared top bar Ask · Browse manuals · Explore graph on `chat.html`/`browse.html`, link from `index.html`; `index.html` still on its own styling) | One application shell with a top bar **Ask · Browse manuals · Drawings · Explore graph · Review**; move `index.html` onto `ui/themes.css`; hide its advanced panels behind an "Expert" switch; first paint under 1.5 s (lazy 3D, see section 37.24) | high | medium |
| 3 (done 2026-10-01, §37.32) | **Browse manuals:** chapter and paragraph tree, reading view with sub-paragraph navigation, cross-reference links, find in manual, "continues in" links | high | medium |
| 4 | **Drawings gallery:** thumbnails, search by drawing number, alteration timeline from the registry, "paragraphs that cite this drawing" | medium | medium |
| 5 | **Field mode:** installable app (manifest and service worker, offline cache of the index and PDFs), large touch targets, sunlight theme, read-aloud | high for site staff | medium |
| 6 | **Workspace:** collections of saved answers with notes, export to PDF or Word with citations, printable job cards | medium | medium |
| 7 | **Review and learning in the app:** answer review packets, accept or reject suggested synonyms, feedback inbox (replacing the file round trip) | medium | medium |

### 39.4 Out-of-the-box options (not requested explicitly; each needs a decision)

1. **Show it on the page:** hovering a citation shows a thumbnail of the page with the exact sentence highlighted; the viewer highlights the sentence itself (the line regions already exist; needs a vendored PDF renderer for pages without a pre-rendered crop).
2. **Compare across manuals:** the same question answered side by side for each manual (strict scope already exists); useful where TMM, STMM and IRPWM overlap.
3. **Checklist mode:** a procedural paragraph ((a), (b), (i) steps) turned into tick-off steps with a printable job card; every step is the manual's own sentence.
4. **Calculators from the manuals' own formulas** (versine and radius, cant and speed, rail temperature limits, breathing length), unit-checked and each citing its paragraph. Deterministic, so safe; limited to formulas the manuals state.
5. **Glossary cards:** hover an abbreviation (SEJ, LWR, USFD) for its expansion, from the synonym file the engine already uses.
6. **What changed:** per paragraph, the correction slips and the version history ("ACS 14 changed this on ...").
7. **Why this answer:** which words matched, which other paragraphs were close, why it is "Likely" and not "Strong".
8. **Hands-free:** dictation and read-aloud for gloved use (read-aloud works offline with installed voices; dictation often needs a network and would be offered only where it works offline).
9. **More comfort themes:** automatic night mode by time, a sunlight (maximum contrast) mode for outdoor screens, a colour-blind-safe palette option, a custom accent colour.
10. **Guided start for new users:** "Not sure how to ask?" topic wizard (manual, topic, ready-made questions).
11. **Hindi and Marathi interface labels and transliterated terms** (for example "rail", "patri") added to the synonyms; honest limit: the manuals are English, so questions can be understood only as far as the vocabulary mapping goes, and answers stay in English.
12. **Pinned paragraphs and daily lists** for a gang or an inspection round; QR-free (file-path based) because the tool is offline.
13. **Polish:** loading skeletons, subtle motion respecting the reduced-motion setting, answer reveal, haptic feedback on phones.

### 39.5 How we will know it is better

Before and after for any phase: (a) five people from the target group each ask five real questions without instructions; record time to first useful answer, rephrasings per question and what they could not find; (b) a short usability questionnaire (SUS) at the end; (c) thumbs ratio and the share of questions with no answer from the exported feedback log; (d) automated checks stay green: contrast for every theme, keyboard operation, first-paint time. Accessibility checks to add: automated landmarks and label checks in the browser suite, and one session with a screen reader.

### 39.6 Needed from you

Pick three ideas from 39.4; name three to five people who can try the assistant for twenty minutes and what devices they use (phone, tablet, office PC), which decides whether Phase 5 comes before Phase 2; say whether Hindi support matters now.

## 40. Phase-by-phase completion plan (2026-10-01)

Rule: a phase is closed only when its exit criterion in §26 has a reproducible command or test and the master records it. One phase at a time; "Next sprint" continues the open phase. Status figures are estimates from §26, §37 and §38, not measurements.

| Order | Phase | Now | Work to close it | Done when (test) | Needs from the owner |
|---|---|---|---|---|---|
| 1 | **P1** browsing | CLOSED 2026-10-01 (§37.39) | Tick every IRPWM pilot line in §28 with a command or test; run the same checklist for the other five manuals; fix gaps the checklist finds. | `scripts/pilot_checklist.py` (new) prints PASS for all six manuals; Gate in `validate_all`. | None. |
| 2 | **P2** evidence and references | CLOSED 2026-10-01 (§37.40) | Broken and ambiguous reference report in the UI (145 not found, 19 ambiguous); fix extractable ones; keep the rest as listed, honest gaps; page crops for every clause. | Gate: every unresolved reference listed with a reason; crop exists or is explained for 1,172 clauses. | Optional: decide the 19 ambiguous references. |
| 3 | **P7** reliability, learning | ~75% (§37.41; not closed: real questions, learning paths) | Flashcards and quiz generated only from cited paragraphs, replacing the hand-authored quiz and its made-up certificate id; review queue in the app; zero-result queries feed the queue; weekly metrics file. | Every card links to a clause id and page (test); training view has no hand-written facts. | Review answers: 50 to 100 real questions from engineers across all six manuals, two people labelling. |
| 4 | **P6** grounded answers | ~85% (§37.42; open: conflict flags need reviewed candidates, new questions from other manuals) | Answer each part of a multi-part question; revision and applicability notes per answer; conflict flags; citation verifier test over all shown text; optional offline rephrase (P6.2) only if the verifier rejects seeded hallucinations. | Real-question set: at least 75% fully answered, none refused wrongly; verifier test passes. | The real questions above; approval of synonym additions (PWI to JE/SSE/P.Way and similar). |
| 5 | **P5** hybrid retrieval | ~90% (§37.43; open: real questions from the other five manuals) | Metadata filters in the UI; graph proximity as a ranking signal; semantic layer only if the real-question set shows ranking misses that words cannot fix (decision rule recorded). | Recall at 5 of at least 0.90 on the real set. | None beyond the real questions. |
| 6 | **P3** drawings | ~45% | Notes, BOM and dimension extraction from drawing sheets; revision comparison; replace the six hand-made drawing nodes; gallery page only if wanted. Cited drawings without a sheet stay listed as missing. | Every drawing node has evidence on a sheet or is marked missing; revision diff test. | The missing drawing sheets (99 of 103 cited numbers have none); decision on the gallery. |
| 7 | **P4** engineering graph | ~45% (§37.44; reference-based questions done; entity-based ones need new extraction) | Typed relationship filters, dependency trace, failure analysis, path finding and why-connected on the canonical graph, in the simple home page's graph. | Questions such as "what depends on X" answered with a path and evidence (tests). | Which relationship questions engineers actually ask. |
| 8 | **P8** optional | 0% | Only after phases 1 to 7 and only the parts that the verifier can check. | n/a | Go or no-go. |

Cross-cutting, runs alongside every phase: human review of paragraphs through packets (only 12 of 1,171 reviewed), reported in `reports/review_accuracy.json`; the interface plan in §39 (Phases 2, 4 to 7) follows the data phases, and the three out-of-the-box ideas stay undecided until the owner picks.
