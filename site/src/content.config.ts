import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { basename } from 'node:path';

const notebook = defineCollection({
  loader: glob({
    base: '../narrative',
    pattern: ['notebook/[!_]*.md', 'exercises/[!_]*.md'],
    generateId: ({ entry }) =>
      (entry.startsWith('exercises/') ? 'exercise-' : '') + basename(entry, '.md'),
  }),
  schema: z.object({
    station: z.union([z.number(), z.literal('alongside')]),
    kind: z.enum(['source', 'alongside', 'exercise']),
    title: z.string(),
    short: z.string(),
    sources: z.array(z.object({ label: z.string(), url: z.string().url() })),
    records: z.array(z.string()).default([]),
    read_on: z.coerce.date().optional(),
  }),
});

const record = z.object({ id: z.string(), name: z.string() }).passthrough();

const models = defineCollection({
  loader: glob({ base: '../data/models', pattern: '*.json' }),
  schema: record,
});
const datasets = defineCollection({
  loader: glob({ base: '../data/datasets', pattern: '*.json' }),
  schema: record,
});

const docs = defineCollection({
  loader: glob({
    base: '..',
    pattern: ['docs/{method,review,disputes}.md', 'narrative/glossary.md'],
    generateId: ({ entry }) => basename(entry, '.md'),
  }),
});

export const collections = { notebook, models, datasets, docs };
