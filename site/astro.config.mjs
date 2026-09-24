import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import rehypeStemma from './src/lib/rehype-stemma.mjs';

export default defineConfig({
  site: 'https://stemma.network',
  output: 'static',
  trailingSlash: 'always',
  integrations: [sitemap()],
  markdown: { rehypePlugins: [rehypeStemma] },
});
