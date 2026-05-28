import { defineConfig } from 'astro/config';

// Static output is what Cloudflare Pages expects.
// All API calls go to the Python backend deployed separately.
export default defineConfig({
  output: 'static',
});
