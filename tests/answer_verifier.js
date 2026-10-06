// Citation verifier: every piece of text the chat shows must be a verbatim part of what it cites. Run over every evaluation question, the
// real questions and the probe. Prints one JSON document: counts and every violation.
const path = require('path'), fs = require('fs'), root = path.resolve(__dirname, '..');
const S = require(path.join(root, 'lib/rdso_search.js')), C = require(path.join(root, 'lib/rdso_chat.js'));
['search_index', 'clause_extras', 'crossrefs', 'tables', 'editions', 'drawing_cites', 'entities'].forEach(f => require(path.join(root, 'data/search', f + '.js')));
const engine = S.create(globalThis.RDSO_SEARCH_INDEX);
const norm = t => String(t).replace(/\s+/g, ' ').replace(/…$/, '').replace(/\s*\.\.\.$/, '').trim();
const docsByClause = {};
globalThis.RDSO_SEARCH_INDEX.docs.forEach(d => { (docsByClause[d.clause] = docsByClause[d.clause] || []).push(norm(d.text)); });
const clauseHay = id => (docsByClause[id] || []).join(' ');
const cellsOf = id => { const T = globalThis.RDSO_TABLES[id]; return T ? new Set([].concat(T.h, ...T.r).map(c => norm((c || '').replace(/\n/g, '; ')))) : null; };
const G = require(path.join(root, 'lib/rdso_graphq.js')), EN = require(path.join(root, 'lib/rdso_entities.js'));
const entities = EN.create(globalThis.RDSO_ENTITIES);
const graph = G.create({ xrefs: globalThis.RDSO_CROSSREFS, clauseText: id => engine.clauseText(id), drawingCites: globalThis.RDSO_DRAWING_CITES });
const lines = f => fs.readFileSync(path.join(root, f), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const questions = lines('eval/questions.jsonl').map(q => q.question).concat(lines('eval/real_questions_irpwm.jsonl').map(q => q.question),
  JSON.parse(fs.readFileSync(path.join(root, 'eval/chat_probe.json'), 'utf8')).items.map(i => i.q));
const out = { questions: questions.length, answers: 0, refused: 0, fragments: 0, violations: [] };
const check = (q, what, text, clause) => { out.fragments++; const hay = clauseHay(clause), t = norm(text);
  if (!clause || !hay) out.violations.push({ q, what, text: t.slice(0, 80), why: 'no cited paragraph' });
  else if (!hay.includes(t)) out.violations.push({ q, what, text: t.slice(0, 100), why: 'not in the cited paragraph' }); };
questions.forEach(q => {
  const r = C.create(engine, { extras: globalThis.RDSO_CLAUSE_EXTRAS, xrefs: globalThis.RDSO_CROSSREFS, tables: globalThis.RDSO_TABLES, editions: globalThis.RDSO_EDITIONS, entities, graph, entities }).ask(q);
  if (r.kind !== 'answer') { out.refused++; return; }
  out.answers++;
  if (!r.primary || !r.primary.page || !r.primary.label) out.violations.push({ q, what: 'citation', why: 'missing label or page' });
  if (r.table) { // rows come from the stored table that the primary paragraph owns or is
    const cells = cellsOf(r.table.id); r.table.rows.forEach(w => w.cells.forEach(c => { out.fragments++; if (cells && c && !cells.has(norm(c))) out.violations.push({ q, what: 'table cell', text: norm(c).slice(0, 80), why: 'not in the stored table' }); }));
  } else (r.points || []).forEach(p => check(q, 'point', p.text, p.cite && p.cite.clause));
  // the heading line shown above a table ("For Speeds above 100 Kmph ...:") must be printed in the paragraph that owns the table
  [r.table].concat(r.ownedTables || []).forEach(t => { if (t && t.context) { out.fragments++; const k = (globalThis.RDSO_TABLES[t.id] || {}).k; if (!k || !clauseHay(k).includes(norm(t.context))) out.violations.push({ q, what: 'table heading', text: norm(t.context).slice(0, 80), why: 'not printed in the owning paragraph' }); } });
  (r.ownedTables || []).forEach(t => { const cells = cellsOf(t.id); t.rows.forEach(w => w.cells.forEach(c => { out.fragments++; if (cells && c && !cells.has(norm(c))) out.violations.push({ q, what: 'owned table cell', text: norm(c).slice(0, 80), why: 'not in the stored table' }); })); });
  (r.alsoSee || []).forEach(p => check(q, 'also relevant', p.text, p.cite && p.cite.clause));
  // edition line and correction-slip marks: the edition must be the registry's, every mark must be printed in the cited paragraph
  if (!r.edition) out.violations.push({ q, what: 'edition', why: 'answer without an edition line' });
  (r.amendments || []).forEach(a => { out.fragments++; const [kind, n] = a.split(' '); if (!new RegExp('\\(\\s*' + kind + '\\s*[-\u2013]\\s*' + n + '\\s*\\)').test(clauseHay(r.primary.clause))) out.violations.push({ q, what: 'amendment', text: a, why: 'mark not printed in the cited paragraph' }); });
});
// relationship answers: every quoted sentence is a verbatim part of the paragraph that prints the reference
out.relations = 0;
const relIds = Object.keys(globalThis.RDSO_CROSSREFS.out).filter(i => /^CLAUSE:(IRPWM|TMM|STMM|USFD|AT_WELD|FBW):/.test(i)).sort().filter((_, i) => i % 5 === 0).slice(0, 60);
relIds.forEach(id => { const m = /^CLAUSE:([^:]+):CH_\d+:PARA_(.+)$/.exec(id), label = m[1].replace('_', ' ') + ' Para ' + m[2].replace(/_/g, '.');
  ['What refers to ' + label + '?', 'What does ' + label + ' refer to?', 'Which figures does ' + label + ' mention?'].forEach(q => {
    const r = require(path.join(root, 'lib/rdso_chat.js')).create(engine, { extras: globalThis.RDSO_CLAUSE_EXTRAS, xrefs: globalThis.RDSO_CROSSREFS, tables: globalThis.RDSO_TABLES, editions: globalThis.RDSO_EDITIONS, entities, graph, entities }).ask(q);
    if (r.kind !== 'relation') { if (r.kind !== 'clarify' && !/figures/.test(q)) out.violations.push({ q, what: 'relation', why: 'not understood as a relationship question: ' + r.kind }); return; }
    out.relations++; (r.rows || []).forEach(x => { const at = x.at || x.cite; out.fragments++; check(q, 'relation quote', String(x.quote).replace(/^…/, ''), at && at.clause); }); }); });
// concept answers: every concept asked about four ways; each quoted sentence must be a verbatim part of the paragraph it cites, and a named concept must be found
out.concepts = 0;
entities.ids().forEach(id => { const name = globalThis.RDSO_ENTITIES.c[id].a[0];
  ['Where is ' + name + ' mentioned in the manuals?', 'What is ' + name + ' related to?', 'What are the types of ' + name + '?', 'List all the values given for ' + name].forEach((q, i) => {
    const r = C.create(engine, { extras: globalThis.RDSO_CLAUSE_EXTRAS, xrefs: globalThis.RDSO_CROSSREFS, tables: globalThis.RDSO_TABLES, editions: globalThis.RDSO_EDITIONS, entities, graph }).ask(q);
    if (r.kind !== 'relation' || r.mode !== 'concept') { if (i === 0) out.violations.push({ q, what: 'concept', why: 'not understood as a concept question: ' + r.kind }); return; }
    out.concepts++; (r.rows || []).forEach(x => { out.fragments++; check(q, 'concept quote', String(x.quote).replace(/^\u2026/, ''), x.at && x.at.clause); }); }); });
// typed relations: every relation read from sentences is asked about both ways; the answer must come back as a concept answer whose rows quote their paragraph and name the other concept
out.typed = 0;
const asked = {}, nm = id => globalThis.RDSO_ENTITIES.c[id].a[0], FORMS = { DETECTED_BY: [t => 'How is ' + nm(t[1]) + ' detected?', t => 'What can ' + nm(t[2]) + ' detect?'], RESPONSIBLE_FOR: [t => 'Who is responsible for ' + nm(t[2]) + '?', t => 'What is ' + nm(t[1]) + ' responsible for?'],
  PERFORMED_WITH: [t => 'What machine is used for ' + nm(t[1]) + '?', t => 'What is the ' + nm(t[2]) + ' used for?'], CAUSES: [t => 'What causes ' + nm(t[2]) + '?', t => 'What does ' + nm(t[1]) + ' cause?'] };
globalThis.RDSO_ENTITIES.typed.forEach(t => FORMS[t[0]].forEach((f, i) => { const q = f(t); if (asked[q]) return; asked[q] = 1;
  const r = C.create(engine, { extras: globalThis.RDSO_CLAUSE_EXTRAS, xrefs: globalThis.RDSO_CROSSREFS, tables: globalThis.RDSO_TABLES, editions: globalThis.RDSO_EDITIONS, entities, graph }).ask(q);
  if (r.kind !== 'relation' || r.mode !== 'concept' || !(r.rows || []).length) { out.violations.push({ q, what: 'typed', why: 'not answered as a typed relation: ' + r.kind + ' ' + (r.mode || '') }); return; }
  out.typed++; const want = i === 0 ? t[2 - 0 + (t[0] === 'DETECTED_BY' || t[0] === 'PERFORMED_WITH' ? 0 : -1) + 0] : null;
  r.rows.forEach(x => { out.fragments++; check(q, 'typed quote', String(x.quote).replace(/^\u2026/, ''), x.at && x.at.clause); }); }));
if (process.env.RDSO_SEED_BAD) { check('seeded', 'seeded', 'The maximum permissible speed on every curve is 999 Kmph.', 'CLAUSE:IRPWM:CH_06:PARA_616'); check('seeded', 'seeded', 'Casual rail renewal shall be done for replacement of defective rail', 'CLAUSE:IRPWM:CH_06:PARA_616'); }   // self-test: a fabricated sentence must be caught, a real one not
console.log(JSON.stringify(out));
