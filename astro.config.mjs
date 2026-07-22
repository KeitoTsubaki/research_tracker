// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages serves project sites from https://<user>.github.io/<repo>/,
// so the site needs a `base` matching the repo name. Override via env vars
// in the deploy workflow (see .github/workflows/deploy-pages.yml) or here.
const site = process.env.SITE_URL || 'https://example.github.io';
const rawBase = process.env.SITE_BASE || '/research_tracker';
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

// https://astro.build/config
export default defineConfig({
  output: 'static',
  site,
  base,
  vite: {
    plugins: [tailwindcss()],
  },
});
