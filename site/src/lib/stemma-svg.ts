// Draws one family of the Stemma as a manuscript-style stemma (inline SVG, themed by the site's CSS).
// Pilot for Phase 3: columns are hand-set for this family; heights come from release dates; every line is a recorded edge.
import type { Edge, Rec } from './data';

export type Family = {
  id: string;
  aria: string;
  lanes: Record<string, number>;
  short: Record<string, string>;
  // Records whose parents Stemma has not recorded. Drawn with a stub, not a line.
  noParents: string[];
  // A recorded edge whose parent is drawn in another family: a labelled stub instead of a duplicated tree.
  offFamily?: { child: string; parent: string; label: string; href: string }[];
  start: [number, number];
  months: number;
  W: number;
  bands: [number, string][];
  monthPx?: number;
};

const LLAMA_LANES: Record<string, number> = {
  // closed models
  'text-davinci-003': 110, chatgpt: 250, 'gpt-4': 170,
  // datasets
  'flan-v2': 400, 'alpaca-52k': 300, 'alpaca-cleaned': 400, baize: 300, 'baize-sdf': 500, starcoderdata: 600,
  oasst1: 400, 'sharegpt-vicuna': 500, 'orca-1-data': 300, openorca: 400, 'open-platypus': 300,
  ultrafeedback: 300, 'tulu-v2-sft-mixture': 400, 'orca-2-data': 500, slimpajama: 600,
  // open weights
  'alpaca-7b': 720, 'alpaca-lora-7b': 840, 'guanaco-7b': 840, 'baize-v2-7b': 720,
  'vicuna-7b-v1-3': 720, 'vicuna-7b-v1-5': 720, 'open-llama-7b': 1100,
  'llama-7b': 960, 'llama-2-7b': 960, 'code-llama-7b': 960,
  'codellama-7b-instruct': 840, 'codellama-7b-python': 1100,
  'llama-2-7b-chat': 840, 'nous-hermes-llama-2-7b': 960,
  'llama-2-13b': 1220, 'wizardlm-13b-v1-2': 1100, 'vicuna-13b-v1-5': 1220,
  'openorcaxopenchat-preview2-13b': 1345, 'platypus2-13b': 1100, 'openorca-platypus2-13b': 1220,
  'llama-2-70b': 1345,
  'mythologic-l2-13b': 1500, 'mythomax-l2-13b': 1620,
  'tulu-2-7b': 720, 'tulu-2-dpo-7b': 720, 'orca-2-7b': 840, 'tinyllama-1-1b-intermediate-step-1431k-3t': 1220,
};
const LLAMA_SHORT: Record<string, string> = {
  'text-davinci-003': 'text-davinci-003', chatgpt: 'ChatGPT', 'gpt-4': 'GPT-4',
  'flan-v2': 'FLAN v2', 'alpaca-52k': 'Alpaca 52K', 'alpaca-cleaned': 'Alpaca-cleaned', baize: 'Baize data',
  'baize-sdf': 'Baize SDF', starcoderdata: 'StarCoderData', oasst1: 'OASST1', 'sharegpt-vicuna': 'ShareGPT',
  'orca-1-data': 'Orca 1 data', openorca: 'OpenOrca', 'open-platypus': 'Open-Platypus', ultrafeedback: 'UltraFeedback',
  'tulu-v2-sft-mixture': 'Tulu v2 mix', 'orca-2-data': 'Orca 2 data', slimpajama: 'SlimPajama',
  'alpaca-7b': 'Alpaca 7B', 'alpaca-lora-7b': 'Alpaca-LoRA 7B', 'guanaco-7b': 'Guanaco 7B', 'baize-v2-7b': 'Baize v2 7B',
  'vicuna-7b-v1-3': 'Vicuna 7B v1.3', 'vicuna-7b-v1-5': 'Vicuna 7B v1.5', 'vicuna-13b-v1-5': 'Vicuna 13B v1.5',
  'llama-7b': 'LLaMA 7B', 'llama-2-7b': 'Llama 2 7B', 'llama-2-13b': 'Llama 2 13B',
  'llama-2-70b': 'Llama 2 70B', 'llama-2-7b-chat': 'Llama 2-Chat 7B',
  'code-llama-7b': 'Code Llama 7B', 'codellama-7b-instruct': '… Instruct',
  'codellama-7b-python': '… Python', 'nous-hermes-llama-2-7b': 'Nous-Hermes 7B',
  'wizardlm-13b-v1-2': 'WizardLM 13B', 'open-llama-7b': 'OpenLLaMA 7B',
  'openorcaxopenchat-preview2-13b': 'OpenOrca-Preview2', 'platypus2-13b': 'Platypus2 13B',
  'openorca-platypus2-13b': 'OpenOrca-Platypus2', 'mythologic-l2-13b': 'MythoLogic 13B', 'mythomax-l2-13b': 'MythoMax 13B',
  'tulu-2-7b': 'Tulu 2 7B', 'tulu-2-dpo-7b': 'Tulu 2-DPO 7B', 'orca-2-7b': 'Orca 2 7B',
  'tinyllama-1-1b-intermediate-step-1431k-3t': 'TinyLlama 1.1B',
};
const MISTRAL_LANES: Record<string, number> = {
  // closed models
  'gpt-4': 90,
  // datasets / off-family
  ultrachat: 320, ultrafeedback: 240, openorca: 320, nectar: 420, 'llama-2-7b-chat': 780,
  // open weights
  'mistral-7b-v0-1': 560, 'mistral-7b-instruct-v0-1': 700, 'mistral-7b-instruct-v0-1-gptq': 840,
  'mistral-7b-openorca': 460, 'openhermes-2-5-mistral-7b': 840, 'solar-10-7b-v1-0': 980,
  'zephyr-7b-alpha': 420, 'mistral-7b-sft-beta': 560, 'zephyr-7b-beta': 700,
  'openchat-3-5': 420, 'starling-rm-7b-alpha': 780, 'starling-lm-7b-alpha': 560,
  'mixtral-8x7b-v0-1': 980, 'mixtral-8x7b-instruct-v0-1': 1120,
};
const MISTRAL_SHORT: Record<string, string> = {
  'gpt-4': 'GPT-4', ultrachat: 'UltraChat', ultrafeedback: 'UltraFeedback', openorca: 'OpenOrca', nectar: 'Nectar',
  'llama-2-7b-chat': 'Llama 2-Chat 7B',
  'mistral-7b-v0-1': 'Mistral 7B', 'mistral-7b-instruct-v0-1': 'Mistral 7B Instruct',
  'mistral-7b-instruct-v0-1-gptq': '… GPTQ', 'mistral-7b-openorca': 'Mistral-OpenOrca',
  'openhermes-2-5-mistral-7b': 'OpenHermes-2.5', 'solar-10-7b-v1-0': 'SOLAR 10.7B',
  'zephyr-7b-alpha': 'Zephyr-α', 'mistral-7b-sft-beta': 'Zephyr SFT (β)', 'zephyr-7b-beta': 'Zephyr-β',
  'openchat-3-5': 'OpenChat 3.5', 'starling-rm-7b-alpha': 'Starling-RM',
  'starling-lm-7b-alpha': 'Starling-LM', 'mixtral-8x7b-v0-1': 'Mixtral 8x7B', 'mixtral-8x7b-instruct-v0-1': '… Instruct',
};
export const MISTRAL: Family = {
  id: 'mistral',
  aria: 'The Mistral family, drawn as a stemma',
  lanes: MISTRAL_LANES,
  short: MISTRAL_SHORT,
  noParents: [],
  offFamily: [
    { child: 'starling-rm-7b-alpha', parent: 'llama-2-7b-chat', label: 'see the LLaMA family →', href: '/graph/#llama' },
  ],
  start: [2023, 8],
  months: 6,
  W: 1300,
  bands: [[90, 'Closed'], [350, 'Datasets'], [830, 'Open weights']],
  monthPx: 220,
};
export const LLAMA: Family = {
  id: 'llama',
  aria: 'The LLaMA family, drawn as a stemma',
  lanes: LLAMA_LANES,
  short: LLAMA_SHORT,
  noParents: ['mythologic-l2-13b', 'mythomax-l2-13b'],
  start: [2022, 11],
  months: 14,
  W: 1760,
  bands: [[180, 'Closed · known by outputs'], [450, 'Datasets'], [1230, 'Open weights']],
};
const FORM: Record<string, string> = {
  fine_tuned_from: 'weights', merged_from: 'weights', quantized_from: 'weights', adapter_on: 'weights',
  trained_on: 'data',
  distilled_from_outputs: 'contamination', feedback_from: 'contamination',
  successor_in_series: 'design', same_architecture_retrained: 'design', design_follows: 'design',
};

const TOP = 110, MONTH_PX = 100, MIN_GAP = 44;

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function monthY(date: string, START: [number, number], monthPx = MONTH_PX) {
  const y = +date.slice(0, 4), m = +date.slice(5, 7);
  const d = date.length >= 10 ? +date.slice(8, 10) : 15;
  return TOP + ((y - START[0]) * 12 + (m - START[1]) + (d - 1) / 30) * monthPx;
}

export function drawFamily(byId: Map<string, Rec>, allEdges: Edge[], crop?: { top: number }, fam: Family = LLAMA) {
  const { lanes: LANES, short: SHORT, noParents: NO_PARENTS, start: START, W, monthPx = MONTH_PX } = fam;
  const missing = Object.keys(LANES).filter((id) => !byId.has(id));
  if (missing.length) throw new Error(`Stemma drawing: no record for ${missing.join(', ')}`);
  const edges = allEdges.filter((e) => e.child in LANES && e.parent in LANES);

  const pos = new Map<string, [number, number]>();
  const undated: string[] = [];
  for (const id of Object.keys(LANES)) {
    const date = byId.get(id)!.data.release_date?.value;
    if (date) pos.set(id, [LANES[id], monthY(date, START, monthPx)]);
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
  o.push(`<svg class="stemma" xmlns="http://www.w3.org/2000/svg" viewBox="0 ${crop?.top ?? 30} ${W} ${H - (crop?.top ?? 30)}" role="img" aria-label="${fam.aria}">`);

  for (let k = 0; k <= fam.months; k++) {
    const mm = START[1] - 1 + k;
    const y = START[0] + Math.floor(mm / 12), m = (mm % 12) + 1;
    const yy = TOP + k * monthPx;
    o.push(`<line class="axis" x1="20" x2="${W - 20}" y1="${yy}" y2="${yy}"/>`);
    o.push(`<text class="month" x="20" y="${yy - 4}">${y}-${String(m).padStart(2, '0')}</text>`);
  }
  for (const [x, label] of fam.bands) {
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

  const offFamily = new Map((fam.offFamily ?? []).map((o) => [o.parent, o]));
  for (const [id, [x, y]] of pos) {
    const r = byId.get(id)!;
    const off = offFamily.get(id);
    const closed = ['closed', 'api_only'].includes(r.data.weights_status);
    const shape = off
      ? `<circle class="offfam" cx="${x}" cy="${y}" r="6"/>`
      : r.kind === 'dataset'
        ? `<rect class="ds" x="${x - 7}" y="${y - 7}" width="14" height="14"/>`
        : closed
          ? `<circle class="closed" cx="${x}" cy="${y}" r="8"/>`
          : `<circle class="open" cx="${x}" cy="${y}" r="5.5"/>`;
    const sub = off ? off.label : closed ? 'closed' : undated.includes(id) ? 'undated' : r.data.release_date?.value ?? '';
    const href = off ? off.href : `/${r.kind === 'model' ? 'models' : 'datasets'}/${id}/`;
    if (NO_PARENTS.includes(id)) {
      o.push(
        `<g class="noparents"><path class="e stub" d="M${x},${y - 7} L${x},${y - 30}"/><circle class="q" cx="${x}" cy="${y - 36}" r="6"/>` +
          `<text class="qm" x="${x}" y="${y - 33}" text-anchor="middle">?</text>` +
          `<text class="sub" x="${x + 12}" y="${y - 32}">parents not recorded</text><title>${esc(`${r.name}: no parents recorded in Stemma`)}</title></g>`,
      );
    }
    o.push(
      `<a href="${href}"><g>${shape}<text class="lbl" x="${x + 12}" y="${y + 4}">${esc(SHORT[id])}</text>` +
        `<text class="sub" x="${x + 12}" y="${y + 18}">${esc(sub)}</text><title>${esc(r.name)}</title></g></a>`,
    );
  }
  o.push('</svg>');
  return o.join('\n');
}

// Phone layout: one indented column (the weights/design tree, siblings in date order). Closed models and
// datasets sit in a left gutter, each entered just before the first row that uses it; its rail runs down to the
// last row that uses it, and rails that have ended are reused so the gutter stays narrow.
const N = { W: 380, RAIL0: 12, RAIL_GAP: 18, INDENT: 22, HEAD_ROW: 28, ROW: 46, PAD: 22 };

export function drawFamilyNarrow(byId: Map<string, Rec>, allEdges: Edge[], opts: { links?: boolean } = {}, fam: Family = LLAMA) {
  const { lanes: LANES, short: SHORT, noParents: NO_PARENTS } = fam;
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
  const isModelRow = (id: string) => rec(id).kind === 'model' && !isClosed(id);
  const roots = ids.filter((id) => isModelRow(id) && !treeParent.has(id));
  const order: { id: string; depth: number }[] = [];
  const visit = (id: string, depth: number) => {
    order.push({ id, depth });
    kids(id).forEach((c) => visit(c, depth + 1));
  };
  roots.sort((a, b) => date(a).localeCompare(date(b))).forEach((r) => visit(r, 0));
  const rowIdx = new Map(order.map((o, i) => [o.id, i]));

  // Gutter sequence: each dataset just before its first model row, preceded by any closed model that wrote or graded it.
  const usesOf = (g: string) => edges.filter((e) => e.parent === g && ['data', 'contamination'].includes(FORM[e.relation]));
  const dsFirst = new Map<string, number>();
  for (const id of ids.filter((i) => rec(i).kind === 'dataset')) {
    const rows = usesOf(id).map((e) => rowIdx.get(e.child)).filter((v): v is number => v !== undefined);
    if (rows.length) dsFirst.set(id, Math.min(...rows));
  }
  const seq: { id: string; gutter: boolean }[] = [];
  const placed = new Set<string>();
  for (let i = 0; i <= order.length; i++) {
    const here = [...dsFirst].filter(([, f]) => f === i).map(([d]) => d).sort((a, b) => date(a).localeCompare(date(b)) || a.localeCompare(b));
    for (const d of here) {
      for (const e of edges.filter((e) => e.child === d && FORM[e.relation] === 'contamination' && !placed.has(e.parent))) {
        placed.add(e.parent);
        seq.push({ id: e.parent, gutter: true });
      }
      seq.push({ id: d, gutter: true });
    }
    if (i < order.length) seq.push({ id: order[i].id, gutter: false });
  }

  const yOf = new Map<string, number>();
  let y = N.PAD;
  for (const it of seq) {
    yOf.set(it.id, y);
    y += it.gutter ? N.HEAD_ROW : N.ROW;
  }
  const H = y;

  // Rails: interval-coloured lanes, reused once a rail's last row has passed.
  const gut = seq.filter((s) => s.gutter).map((s) => s.id);
  const lastUse = new Map(gut.map((g) => [g, Math.max(yOf.get(g)!, ...usesOf(g).map((e) => yOf.get(e.child) ?? 0))]));
  const laneEnd: number[] = [];
  const lane = new Map<string, number>();
  for (const g of gut) {
    let k = laneEnd.findIndex((end) => end <= yOf.get(g)! - 14);
    if (k < 0) k = laneEnd.length;
    laneEnd[k] = lastUse.get(g)!;
    lane.set(g, k);
  }
  const railX = (g: string) => N.RAIL0 + lane.get(g)! * N.RAIL_GAP;
  const maxRail = N.RAIL0 + (laneEnd.length - 1) * N.RAIL_GAP;
  const COL = maxRail + 28;
  const maxDepth = Math.max(...order.map((o) => o.depth));
  const pos = new Map<string, [number, number]>();
  for (const g of gut) pos.set(g, [railX(g), yOf.get(g)!]);
  for (const o of order) pos.set(o.id, [COL + o.depth * N.INDENT, yOf.get(o.id)!]);

  const wrap = (href: string, inner: string) => (links ? `<a href="${esc(href)}">${inner}</a>` : inner);
  const out: string[] = [];
  out.push(`<svg class="stemma" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${N.W} ${H}" role="img" aria-label="${fam.aria} (narrow layout)">`);

  const ev = (e: Edge) => `ev-${e.evidence}`;
  const title = (e: Edge) => `<title>${esc(`${e.child} ← ${e.relation} ← ${e.parent} (${e.evidence})`)}</title>`;
  // Rails, then the ticks that run from a rail into each row that used it.
  for (const g of gut) {
    const x = railX(g), y1 = yOf.get(g)!, y2 = lastUse.get(g)!;
    const form = rec(g).kind === 'dataset' ? 'data' : 'contamination';
    if (y2 > y1) out.push(`<path class="e ${form}" d="M${x},${y1} L${x},${y2}"/>`);
    for (const e of usesOf(g)) {
      if (!pos.has(e.child)) continue;
      const [cx, cy] = pos.get(e.child)!;
      const end = gut.includes(e.child) ? cx + (cx > x ? -9 : 9) : cx - 9;
      out.push(wrap(e.source, `<path class="e ${FORM[e.relation]} ${ev(e)}" d="M${x},${cy} L${end},${cy}">${title(e)}</path>`));
    }
  }
  // Tree: design first, then weights on top, so a shared trunk shows the stronger relation.
  const tree = [...treeParent.values()].sort((a, b) => Number(FORM[a.relation] === 'weights') - Number(FORM[b.relation] === 'weights'));
  for (const e of tree) {
    const [px, py] = pos.get(e.parent)!, [cx, cy] = pos.get(e.child)!;
    out.push(wrap(e.source, `<path class="e ${FORM[e.relation]} ${ev(e)}" d="M${px},${py} L${px},${cy} L${cx},${cy}">${title(e)}</path>`));
  }
  // A second weights parent (a merge) runs down beside the parent's trunk into the child.
  for (const e of edges.filter((e) => FORM[e.relation] === 'weights' && isModelRow(e.parent) && treeParent.get(e.child) !== e)) {
    const [px, py] = pos.get(e.parent)!, [cx, cy] = pos.get(e.child)!;
    out.push(wrap(e.source, `<path class="e weights ${ev(e)}" d="M${px},${py} L${px - 10},${py} L${px - 10},${cy} L${cx - 9},${cy}">${title(e)}</path>`));
  }
  for (const [id, [x, yy]] of pos) {
    const r = rec(id);
    const closed = isClosed(id);
    const off = (fam.offFamily ?? []).find((o) => o.parent === id);
    const shape = off
      ? `<circle class="offfam" cx="${x}" cy="${yy}" r="6"/>`
      : r.kind === 'dataset'
        ? `<rect class="ds" x="${x - 7}" y="${yy - 7}" width="14" height="14"/>`
        : closed
          ? `<circle class="closed" cx="${x}" cy="${yy}" r="7"/>`
          : `<circle class="open" cx="${x}" cy="${yy}" r="5.5"/>`;
    const inline = gut.includes(id);
    const lx = inline ? COL + maxDepth * N.INDENT + 16 : x + 11;
    const orphan = NO_PARENTS.includes(id);
    const sub = off ? off.label : closed ? 'closed' : (date(id) || 'undated') + (orphan ? ' · parents not recorded' : '');
    const href = off ? off.href : `/${r.kind === 'model' ? 'models' : 'datasets'}/${id}/`;
    const text = inline
      ? `<text class="lbl" x="${lx}" y="${yy + 4}">${esc(SHORT[id])} <tspan class="sub">${esc(sub)}</tspan></text>`
      : `<text class="lbl" x="${lx}" y="${yy + 4}">${esc(SHORT[id])}</text><text class="sub" x="${lx}" y="${yy + 18}">${esc(sub)}</text>`;
    const leader = inline ? `<line class="axis" x1="${x + 9}" x2="${lx - 4}" y1="${yy}" y2="${yy}"/>` : '';
    if (orphan) {
      out.push(
        `<g class="noparents"><path class="e stub" d="M${x},${yy - 6} L${x},${yy - 16}"/><circle class="q" cx="${x}" cy="${yy - 21}" r="4.5"/>` +
          `<text class="qm" x="${x}" y="${yy - 18.5}" text-anchor="middle">?</text></g>`,
      );
    }
    out.push(wrap(href, `<g>${leader}${shape}${text}<title>${esc(r.name)}</title></g>`));
  }
  out.push('</svg>');
  return out.join('\n');
}
