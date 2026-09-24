// Draws one family of the Stemma as a manuscript-style stemma (inline SVG, themed by the site's CSS).
// Pilot for Phase 3: columns are hand-set for this family; heights come from release dates; every line is a recorded edge.
import type { Edge, Rec } from './data';

export const LANES: Record<string, number> = {
  'text-davinci-003': 110, chatgpt: 250,
  'alpaca-52k': 350, 'sharegpt-vicuna': 450,
  'alpaca-7b': 560, 'vicuna-7b-v1-3': 620, 'vicuna-7b-v1-5': 600,
  'llama-7b': 780, 'llama-2-7b': 780, 'code-llama-7b': 780,
  'codellama-7b-instruct': 700, 'codellama-7b-python': 860,
  'llama-2-7b-chat': 880, 'nous-hermes-llama-2-7b': 1010,
  'open-llama-7b': 960,
  'llama-2-13b': 1180, 'wizardlm-13b-v1-2': 1140, 'vicuna-13b-v1-5': 1290,
  'llama-2-70b': 1400,
};
const SHORT: Record<string, string> = {
  'text-davinci-003': 'text-davinci-003', chatgpt: 'ChatGPT',
  'alpaca-52k': 'Alpaca 52K', 'sharegpt-vicuna': 'ShareGPT',
  'alpaca-7b': 'Alpaca 7B', 'vicuna-7b-v1-3': 'Vicuna 7B v1.3',
  'vicuna-7b-v1-5': 'Vicuna 7B v1.5', 'vicuna-13b-v1-5': 'Vicuna 13B v1.5',
  'llama-7b': 'LLaMA 7B', 'llama-2-7b': 'Llama 2 7B', 'llama-2-13b': 'Llama 2 13B',
  'llama-2-70b': 'Llama 2 70B', 'llama-2-7b-chat': 'Llama 2-Chat 7B',
  'code-llama-7b': 'Code Llama 7B', 'codellama-7b-instruct': '… Instruct',
  'codellama-7b-python': '… Python', 'nous-hermes-llama-2-7b': 'Nous-Hermes 7B',
  'wizardlm-13b-v1-2': 'WizardLM 13B', 'open-llama-7b': 'OpenLLaMA 7B',
};
const FORM: Record<string, string> = {
  fine_tuned_from: 'weights', merged_from: 'weights', quantized_from: 'weights', adapter_on: 'weights',
  trained_on: 'data',
  distilled_from_outputs: 'contamination', feedback_from: 'contamination',
  successor_in_series: 'design', same_architecture_retrained: 'design', design_follows: 'design',
};

const TOP = 110, MONTH_PX = 100, MIN_GAP = 44, W = 1520;
const START = [2022, 11];

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function monthY(date: string) {
  const y = +date.slice(0, 4), m = +date.slice(5, 7);
  const d = date.length >= 10 ? +date.slice(8, 10) : 15;
  return TOP + ((y - START[0]) * 12 + (m - START[1]) + (d - 1) / 30) * MONTH_PX;
}

export function drawFamily(byId: Map<string, Rec>, allEdges: Edge[], crop?: { top: number }) {
  const missing = Object.keys(LANES).filter((id) => !byId.has(id));
  if (missing.length) throw new Error(`Stemma drawing: no record for ${missing.join(', ')}`);
  const edges = allEdges.filter((e) => e.child in LANES && e.parent in LANES);

  const pos = new Map<string, [number, number]>();
  const undated: string[] = [];
  for (const id of Object.keys(LANES)) {
    const date = byId.get(id)!.data.release_date?.value;
    if (date) pos.set(id, [LANES[id], monthY(date)]);
    else undated.push(id);
  }
  for (const id of undated) {
    const kids = edges.filter((e) => e.parent === id && pos.has(e.child)).map((e) => pos.get(e.child)![1]);
    pos.set(id, [LANES[id], Math.min(...kids) - MIN_GAP]);
  }
  for (let i = 0; i < pos.size; i++) {
    for (const e of edges) {
      const c = pos.get(e.child)!, p = pos.get(e.parent)!;
      if (c[1] < p[1] + MIN_GAP) c[1] = p[1] + MIN_GAP;
    }
  }

  const H = Math.round(Math.max(...[...pos.values()].map(([, y]) => y)) + 60);
  const o: string[] = [];
  o.push(`<svg class="stemma" xmlns="http://www.w3.org/2000/svg" viewBox="0 ${crop?.top ?? 30} ${W} ${H - (crop?.top ?? 30)}" role="img" aria-label="The LLaMA family, drawn as a stemma">`);

  for (let k = 0; k <= 10; k++) {
    const mm = START[1] - 1 + k;
    const y = START[0] + Math.floor(mm / 12), m = (mm % 12) + 1;
    const yy = TOP + k * MONTH_PX;
    o.push(`<line class="axis" x1="20" x2="${W - 20}" y1="${yy}" y2="${yy}"/>`);
    o.push(`<text class="month" x="20" y="${yy - 4}">${y}-${String(m).padStart(2, '0')}</text>`);
  }
  for (const [x, label] of [[190, 'Closed · known by outputs'], [400, 'Datasets'], [1000, 'Open weights']] as const) {
    o.push(`<text class="band" x="${x}" y="60" text-anchor="middle">${label}</text>`);
  }

  for (const e of edges) {
    const [cx, cy] = pos.get(e.child)!, [px, py] = pos.get(e.parent)!;
    const form = FORM[e.relation];
    let d = `M${px},${py} L${cx},${cy}`;
    if (form === 'weights' && cx !== px) {
      const mid = Math.round(py + (cy - py) * 0.7);
      d = `M${px},${py} L${px},${mid} L${cx},${mid} L${cx},${cy}`;
    }
    const title = esc(`${e.child} ← ${e.relation} ← ${e.parent} (${e.evidence})`);
    o.push(`<a href="${esc(e.source)}"><path class="e ${form} ev-${e.evidence}" d="${d}"><title>${title}</title></path></a>`);
  }

  for (const [id, [x, y]] of pos) {
    const r = byId.get(id)!;
    const closed = ['closed', 'api_only'].includes(r.data.weights_status);
    const shape =
      r.kind === 'dataset'
        ? `<rect class="ds" x="${x - 7}" y="${y - 7}" width="14" height="14"/>`
        : closed
          ? `<circle class="closed" cx="${x}" cy="${y}" r="8"/>`
          : `<circle class="open" cx="${x}" cy="${y}" r="5.5"/>`;
    const sub = closed ? 'closed' : undated.includes(id) ? 'undated' : r.data.release_date?.value ?? '';
    const href = `/${r.kind === 'model' ? 'models' : 'datasets'}/${id}/`;
    o.push(
      `<a href="${href}"><g>${shape}<text class="lbl" x="${x + 12}" y="${y + 4}">${esc(SHORT[id])}</text>` +
        `<text class="sub" x="${x + 12}" y="${y + 18}">${esc(sub)}</text><title>${esc(r.name)}</title></g></a>`,
    );
  }
  o.push('</svg>');
  return o.join('\n');
}

// Phone layout: one indented column (the weights/design tree, siblings in date order), with the
// closed models and datasets in a left gutter whose rails feed the rows that trained on them.
const N = { W: 380, RAIL0: 14, RAIL_GAP: 22, COL: 70, INDENT: 26, HEAD_ROW: 34, ROW: 46, PAD: 22 };

export function drawFamilyNarrow(byId: Map<string, Rec>, allEdges: Edge[], opts: { links?: boolean } = {}) {
  const links = opts.links ?? true;
  const ids = Object.keys(LANES);
  const edges = allEdges.filter((e) => e.child in LANES && e.parent in LANES);
  const rec = (id: string) => byId.get(id)!;
  const isClosed = (id: string) => ['closed', 'api_only'].includes(rec(id).data.weights_status);
  const date = (id: string) => rec(id).data.release_date?.value ?? '';
  const treeEdge = (e: Edge) => ['weights', 'design'].includes(FORM[e.relation]) && !isClosed(e.parent);

  // Tree: each open model hangs under its first weights/design parent.
  const treeParent = new Map<string, Edge>();
  for (const e of edges) if (treeEdge(e) && !treeParent.has(e.child)) treeParent.set(e.child, e);
  const kids = (id: string) =>
    ids.filter((c) => treeParent.get(c)?.parent === id).sort((a, b) => date(a).localeCompare(date(b)) || LANES[a] - LANES[b]);
  const roots = ids.filter((id) => rec(id).kind === 'model' && !isClosed(id) && !treeParent.has(id));
  const order: { id: string; depth: number }[] = [];
  const visit = (id: string, depth: number) => {
    order.push({ id, depth });
    kids(id).forEach((c) => visit(c, depth + 1));
  };
  roots.sort((a, b) => date(a).localeCompare(date(b))).forEach((r) => visit(r, 0));

  // Gutter: datasets in order of first use, each preceded by the closed models that wrote or graded it.
  const rowOf = new Map(order.map((o, i) => [o.id, i]));
  const datasets = ids
    .filter((id) => rec(id).kind === 'dataset')
    .map((id) => ({ id, first: Math.min(...edges.filter((e) => e.parent === id && rowOf.has(e.child)).map((e) => rowOf.get(e.child)!)) }))
    .sort((a, b) => a.first - b.first)
    .map((d) => d.id);
  const rail = new Map(datasets.map((d, i) => [d, N.RAIL0 + i * N.RAIL_GAP]));
  const head: { id: string; x: number; y: number }[] = [];
  let y = N.PAD;
  for (const d of datasets) {
    for (const e of edges.filter((e) => e.child === d && FORM[e.relation] === 'contamination')) {
      head.push({ id: e.parent, x: rail.get(d)!, y });
      y += N.HEAD_ROW;
    }
    head.push({ id: d, x: rail.get(d)!, y });
    y += N.HEAD_ROW;
  }
  const top = y + 10;
  const pos = new Map<string, [number, number]>(head.map((h) => [h.id, [h.x, h.y]]));
  order.forEach((o, i) => pos.set(o.id, [N.COL + o.depth * N.INDENT, top + i * N.ROW]));
  const H = top + order.length * N.ROW;

  const wrap = (href: string, inner: string) => (links ? `<a href="${esc(href)}">${inner}</a>` : inner);
  const o: string[] = [];
  o.push(`<svg class="stemma" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${N.W} ${H}" role="img" aria-label="The LLaMA family, drawn as a stemma (narrow layout)">`);

  const ev = (e: Edge) => `ev-${e.evidence}`;
  const title = (e: Edge) => `<title>${esc(`${e.child} ← ${e.relation} ← ${e.parent} (${e.evidence})`)}</title>`;
  // Contamination: closed model down to its dataset, in the dataset's rail.
  for (const e of edges.filter((e) => FORM[e.relation] === 'contamination')) {
    const [x, y1] = pos.get(e.parent)!, [, y2] = pos.get(e.child)!;
    o.push(wrap(e.source, `<path class="e contamination ${ev(e)}" d="M${x},${y1} L${x},${y2}">${title(e)}</path>`));
  }
  // Training data: the rail runs down from the dataset; a tick runs into each row that trained on it.
  for (const d of datasets) {
    const x = rail.get(d)!, y1 = pos.get(d)![1];
    const users = edges.filter((e) => e.parent === d && e.relation === 'trained_on');
    const last = Math.max(...users.map((e) => pos.get(e.child)![1]));
    o.push(`<path class="e data" d="M${x},${y1} L${x},${last}"/>`);
    for (const e of users) {
      const [cx, cy] = pos.get(e.child)!;
      o.push(wrap(e.source, `<path class="e data ${ev(e)}" d="M${x},${cy} L${cx - 9},${cy}">${title(e)}</path>`));
    }
  }
  // Tree: design first, then weights on top, so a shared trunk shows the stronger relation.
  const tree = [...treeParent.values()].sort((a, b) => Number(FORM[a.relation] === 'weights') - Number(FORM[b.relation] === 'weights'));
  for (const e of tree) {
    const [px, py] = pos.get(e.parent)!, [cx, cy] = pos.get(e.child)!;
    o.push(wrap(e.source, `<path class="e ${FORM[e.relation]} ${ev(e)}" d="M${px},${py} L${px},${cy} L${cx},${cy}">${title(e)}</path>`));
  }
  for (const [id, [x, yy]] of pos) {
    const r = rec(id);
    const closed = isClosed(id);
    const shape =
      r.kind === 'dataset'
        ? `<rect class="ds" x="${x - 7}" y="${yy - 7}" width="14" height="14"/>`
        : closed
          ? `<circle class="closed" cx="${x}" cy="${yy}" r="7"/>`
          : `<circle class="open" cx="${x}" cy="${yy}" r="5.5"/>`;
    const lx = rowOf.has(id) ? x + 11 : Math.max(...rail.values()) + 16;
    const sub = closed ? 'closed' : date(id) || 'undated';
    const inline = !rowOf.has(id);
    const href = `/${r.kind === 'model' ? 'models' : 'datasets'}/${id}/`;
    const text = inline
      ? `<text class="lbl" x="${lx}" y="${yy + 4}">${esc(SHORT[id])} <tspan class="sub">${esc(sub)}</tspan></text>`
      : `<text class="lbl" x="${lx}" y="${yy + 4}">${esc(SHORT[id])}</text><text class="sub" x="${lx}" y="${yy + 18}">${esc(sub)}</text>`;
    const leader = inline ? `<line class="axis" x1="${x + 9}" x2="${lx - 4}" y1="${yy}" y2="${yy}"/>` : '';
    o.push(wrap(href, `<g>${leader}${shape}${text}<title>${esc(r.name)}</title></g>`));
  }
  o.push('</svg>');
  return o.join('\n');
}
