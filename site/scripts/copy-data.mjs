// Generated, never committed: mirror ../data (minus staging) and llms.txt into public/.
import { cpSync, rmSync, mkdirSync, copyFileSync } from 'node:fs';
import { resolve, basename } from 'node:path';

const root = resolve(import.meta.dirname, '..', '..');
const pub = resolve(import.meta.dirname, '..', 'public');
rmSync(resolve(pub, 'data'), { recursive: true, force: true });
mkdirSync(pub, { recursive: true });
cpSync(resolve(root, 'data'), resolve(pub, 'data'), {
  recursive: true,
  filter: (src) => basename(src) !== 'staging' && basename(src) !== '.DS_Store',
});
copyFileSync(resolve(root, 'llms.txt'), resolve(pub, 'llms.txt'));
console.log('copy-data: data/ (minus staging) and llms.txt mirrored into public/');
