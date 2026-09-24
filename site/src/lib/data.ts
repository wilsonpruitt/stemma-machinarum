import { getCollection, type CollectionEntry } from 'astro:content';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export type Edge = {
  child: string;
  parent: string;
  relation: string;
  evidence: string;
  source: string;
  note?: string;
};

export const RELATION_GROUPS: { key: string; title: string; relations: string[] }[] = [
  { key: 'weights', title: 'Weights descend', relations: ['fine_tuned_from', 'merged_from', 'quantized_from', 'adapter_on'] },
  { key: 'data', title: 'Training data', relations: ['trained_on'] },
  { key: 'influence', title: 'Influence without weights', relations: ['distilled_from_outputs', 'feedback_from'] },
  { key: 'design', title: 'Design', relations: ['successor_in_series', 'same_architecture_retrained', 'design_follows'] },
];

export const EVIDENCE_TAGS = ['declared', 'declared_by_uploader', 'inferred_weights', 'inferred_behavior', 'alleged'] as const;

export function loadEdges(): Edge[] {
  const p = resolve(process.cwd(), '..', 'data', 'edges', 'edges.jsonl');
  return readFileSync(p, 'utf8')
    .split('\n')
    .filter((l) => l.trim())
    .map((l) => JSON.parse(l));
}

export type Rec = { kind: 'model' | 'dataset'; id: string; name: string; data: Record<string, any> };

export async function loadRecords() {
  const [models, datasets] = await Promise.all([getCollection('models'), getCollection('datasets')]);
  const byId = new Map<string, Rec>();
  for (const m of models) byId.set(m.data.id, { kind: 'model', id: m.data.id, name: m.data.name, data: m.data });
  for (const d of datasets) byId.set(d.data.id, { kind: 'dataset', id: d.data.id, name: d.data.name, data: d.data });
  return { models, datasets, byId };
}

export const recordUrl = (r: Rec) => `/${r.kind === 'model' ? 'models' : 'datasets'}/${r.id}/`;

export async function loadStations() {
  const { byId } = await loadRecords();
  const entries = await getCollection('notebook');
  const rank = (e: CollectionEntry<'notebook'>) => {
    const k = { source: 0, alongside: 1, exercise: 2 }[e.data.kind];
    return [k, e.id] as const;
  };
  entries.sort((a, b) => {
    const [ka, ia] = rank(a);
    const [kb, ib] = rank(b);
    return ka - kb || ia.localeCompare(ib);
  });
  const backlinks = new Map<string, CollectionEntry<'notebook'>[]>();
  for (const e of entries) {
    for (const id of e.data.records) {
      if (!byId.has(id)) {
        throw new Error(`Dangling record id "${id}" in notebook/${e.id}: no such model or dataset in data/.`);
      }
      backlinks.set(id, [...(backlinks.get(id) ?? []), e]);
    }
  }
  return { entries, backlinks };
}

export function notesCount(body: string | undefined) {
  const m = (body ?? '').match(/^## My notes\s*$([\s\S]*?)(?=^## |(?![\s\S]))/m);
  if (!m) return 0;
  return (m[1].match(/^### \d{4}-\d{2}-\d{2}/gm) ?? []).length;
}

export const isRead = (e: CollectionEntry<'notebook'>) => Boolean(e.data.read_on);
export const fmtDate = (d: Date) => d.toISOString().slice(0, 10);
export const stationUrl = (e: CollectionEntry<'notebook'>) => `/notebook/${e.id}/`;
export const stationLabel = (e: CollectionEntry<'notebook'>) =>
  e.data.kind === 'source' ? `Station ${e.data.station}` : e.data.kind === 'alongside' ? 'Read alongside' : 'Exercise';
