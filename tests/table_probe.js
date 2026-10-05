// Prints the tables the chat shows (answer table and the paragraph's own tables) for the real questions named on the command line.
const path = require('path'), root = path.resolve(__dirname, '..');
const S = require(path.join(root, 'lib/rdso_search.js')), C = require(path.join(root, 'lib/rdso_chat.js'));
['search_index', 'clause_extras', 'crossrefs', 'tables'].forEach(f => require(path.join(root, 'data/search', f + '.js')));
const e = S.create(globalThis.RDSO_SEARCH_INDEX);
const qs = require('fs').readFileSync(path.join(root, 'eval/real_questions_irpwm.jsonl'), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const view = t => ({ id: t.id, context: t.context, columns: t.columns, rows: t.rows.map(w => w.cells) });
console.log(JSON.stringify(Object.fromEntries(process.argv.slice(2).map(id => {
  const r = C.create(e, { extras: globalThis.RDSO_CLAUSE_EXTRAS, xrefs: globalThis.RDSO_CROSSREFS, tables: globalThis.RDSO_TABLES }).ask(qs.find(q => q.id === id).question);
  return [id, (r.table ? [view(r.table)] : []).concat((r.ownedTables || []).map(view))];
}))));
