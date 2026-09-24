import path from 'node:path';

const REPO = 'https://github.com/wilsonpruitt/stemma-machinarum/blob/main/';
const ROOT = path.resolve(process.cwd(), '..');

function mapLink(href, filePath) {
  if (!filePath || /^([a-z][a-z0-9+.-]*:|#|\/)/i.test(href)) return href;
  const [rawPath, hash = ''] = href.split('#');
  const frag = hash ? '#' + hash : '';
  if (!rawPath) return href;
  const rel = path.relative(ROOT, path.resolve(path.dirname(filePath), rawPath)).split(path.sep).join('/');
  let m;
  if ((m = rel.match(/^data\/models\/(.+)\.json$/))) return `/models/${m[1]}/${frag}`;
  if ((m = rel.match(/^data\/datasets\/(.+)\.json$/))) return `/datasets/${m[1]}/${frag}`;
  if (rel.startsWith('data/')) return `/${rel}${frag}`;
  if ((m = rel.match(/^narrative\/notebook\/(.+)\.md$/))) return `/notebook/${m[1]}/${frag}`;
  if ((m = rel.match(/^narrative\/exercises\/(.+)\.md$/))) return `/notebook/exercise-${m[1]}/${frag}`;
  if (rel === 'narrative/glossary.md') return `/glossary/${frag}`;
  if ((m = rel.match(/^docs\/(method|review|disputes)\.md$/))) return `/${m[1]}/${frag}`;
  if (rel === 'llms.txt') return '/llms.txt';
  return REPO + rel + frag;
}

const EMPTY = {
  'what-it-introduced': 'Not yet written.',
  'what-it-descended-from': 'Not yet written.',
  'my-notes': 'No notes yet.',
  'questions-i-still-have': 'None recorded yet.',
};

const text = (n) => (n.children || []).map((c) => (c.type === 'text' ? c.value : text(c))).join('');
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const hasContent = (nodes) => nodes.some((n) => n.type === 'element');

function walk(node, fn) {
  fn(node);
  (node.children || []).forEach((c) => walk(c, fn));
}

export default function rehypeStemma() {
  return (tree, file) => {
    walk(tree, (n) => {
      if (n.type === 'element' && n.tagName === 'a' && typeof n.properties?.href === 'string') {
        n.properties.href = mapLink(n.properties.href, file.path);
      }
    });

    const rel = file.path ? path.relative(ROOT, file.path) : '';
    if (!/^narrative\/(notebook|exercises)\//.test(rel)) return;

    const out = [];
    let cur = null;
    for (const n of tree.children) {
      if (n.type === 'element' && n.tagName === 'h1') continue;
      if (n.type === 'element' && n.tagName === 'h2') {
        cur = { id: slug(text(n)), head: n, body: [] };
        out.push(cur);
      } else if (cur) cur.body.push(n);
      else out.push(n);
    }
    tree.children = out.flatMap((s) => {
      if (!s.head) return [s];
      const filled = hasContent(s.body);
      if (s.id === 'records-added-or-verified-in-stemma' && !filled) return [];
      const kids = [s.head, ...s.body];
      if (!filled) {
        kids.push({ type: 'element', tagName: 'p', properties: { className: ['empty'] }, children: [{ type: 'text', value: EMPTY[s.id] ?? 'Nothing yet.' }] });
      }
      return [{ type: 'element', tagName: 'section', properties: { className: ['sec', `sec-${s.id}`] }, children: kids }];
    });
  };
}
