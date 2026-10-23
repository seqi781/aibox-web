# aibox website

[简体中文](README.md) | **English**

A single-page website for aibox, with Chinese and English pages. It is fully static: no build step, dependencies, tracking scripts, or requests to third-party resources. Fonts come from the system.

The website's core message: run Claude Code in a separate Docker environment through a remote node to reduce what the tool can access or expose about your real public IP, host system, and personal configuration. The goal is to reduce related account restriction and ban risks. Codex and other terminal tools can use the same environment.

Both language versions, the social preview, and the recording page explain the scope: aibox provides network and file isolation, with no guarantee against bans or complete machine fingerprint masking. Kernel and CPU information, identity information in authorized files, tool telemetry, and account identifiers may remain accessible. Browser login, initialization, builds, subscriptions, and diagnostic traffic have separate network boundaries.

The website and aibox product code live in separate repositories. This directory contains only the website. The recording script expects the aibox repository at `~/claude/Linux-terminal` by default.

```text
Linux-terminal-web/
├── README.md         Chinese documentation
├── README.en.md      English documentation
├── index.html        Chinese homepage
├── en/index.html     English homepage
├── init/             Real ./aibox init recording (cast.js contains the data)
├── assets/site.css   Styles (colors are in :root; follows system light/dark mode)
├── assets/site.js    Header, copy buttons, and hero terminal demo
├── assets/cast-player.js  Terminal recording player (selectable text, not video)
├── favicon.svg
├── og.svg            Social preview source (export as og.png; see below)
├── robots.txt
├── nextjs/sync.sh    Sync script for an existing Next.js site
└── tools/record-init.py  Records ./aibox init and generates init/cast.js
```

## Local preview

Choose either command, then open http://localhost:8000/:

```bash
cd ~/claude/Linux-terminal-web && python3 -m http.server 8000
```

```bash
npx serve . -l 8000
```

You can also open `index.html` directly. Under `file://`, copy buttons use a compatibility fallback.

## Placeholders to replace before publishing

| Placeholder | Location | Replace with |
|---|---|---|
| `SITE_DOMAIN` | canonical, hreflang, og:url | Your website domain, including any subpath, such as `owner.github.io/aibox` |
| `LICENSE_NAME` | Footer | The license name, such as `MIT`; also add a `LICENSE` file to the repository |

Replace them in one command using GNU sed. On macOS, replace `sed -i` with `sed -i ''`:

```bash
sed -i 's#SITE_DOMAIN#aibox.example.com#g; s#LICENSE_NAME#MIT#g' index.html en/index.html init/index.html
```

## Social preview image (og.png)

Most social platforms do not support SVG preview images. Export `og.svg` to a 1200×630 `og.png` in this directory, then uncomment the `og:image` and `twitter:card` lines in the `<head>` of both homepages. For example:

```bash
rsvg-convert -w 1200 -h 630 og.svg -o og.png
```

## Deployment

This directory is the site root and works with static hosting. `README.md`, `README.en.md`, `nextjs/`, and `tools/` are maintenance files. Serving them is fine; you can exclude them in your hosting configuration if preferred.

**GitHub Pages**: in the repository, go to Settings → Pages → Source and choose “GitHub Actions”. Add `.github/workflows/pages.yml`:

```yaml
name: pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: github-pages
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - uses: actions/deploy-pages@v4
```

**Cloudflare Pages**: connect the repository. Leave the build command and output directory empty to serve the repository root.

**Vercel**: import the repository, choose “Other” as the framework, and leave Root Directory and the build command empty.

**Netlify**: leave Base directory and Publish directory empty to serve the repository root, with no build command.

## Add to an existing Next.js site

The pages are served as standalone subpages: `/aibox`, `/aibox/en`, and `/aibox/init` by default. They remain static HTML with their own CSS and JavaScript, outside the site's layout, so their styles do not affect other pages or inherit the site's global styles.

**1. Copy the pages into your Next.js project** (overwrites `public/aibox/`):

```bash
bash ~/claude/Linux-terminal-web/nextjs/sync.sh /path/to/your-next-app
```

The script copies files into `public/aibox/` and rewrites relative page paths to `/aibox/...`. Use `--base /tools/aibox` to change the path, or `--domain example.com` to fill in the domain. This source directory stays unchanged. Run the script again after making changes.

**2. Add rewrites to `next.config.ts` (or `.js` / `.mjs`):**

```ts
const nextConfig = {
  // Keep your existing configuration here.
  async rewrites() {
    return {
      beforeFiles: [
        { source: '/aibox', destination: '/aibox/index.html' },
        { source: '/aibox/en', destination: '/aibox/en/index.html' },
        { source: '/aibox/init', destination: '/aibox/init/index.html' },
      ],
    };
  },
};
```

If you already have `rewrites()`: an array return value is equivalent to `afterFiles`, so change it to `{ beforeFiles: [the entries above], afterFiles: [your existing entries] }`. If it returns an object, add these entries to its `beforeFiles` array.

**3. Run the site:**

```bash
cd /path/to/your-next-app
npm run dev
```

Open http://localhost:3000/aibox.

Previously checked in a fresh Next.js 16.4 project: both language versions, language switching, anchors, styles, and scripts worked in development mode and with `next build && next start`, with no 404s or script errors.

Notes:

- If the site has a `basePath`, such as `/blog`, run the script with `--base /blog/aibox`, but keep `/aibox` in the rewrites.
- If the site uses middleware for language redirects or authentication, exclude `/aibox` from its `matcher` to avoid redirects.
- With `output: 'export'`, rewrites do not apply. Your static host serves the exported `aibox/index.html` directly at `/aibox/`.
- To add a navigation entry, use a normal link: `<a href="/aibox">`. This is a static page rather than a Next.js route; using `next/link` only adds an unsuccessful client-side navigation attempt.

## Record ./aibox init again

The `init/` page replays a real run of `./aibox init`. Record it again when the aibox wizard or its output changes:

```bash
mkdir -p ~/code/myapp ~/code/specs && git -C ~/code/myapp init -q   # Example folders to authorize; myapp must be a Git project to appear in the wizard
printf '%s\n' "YOUR_SUBSCRIPTION_URL" > /tmp/sub.txt
cd ~/claude/Linux-terminal-web
python3 tools/record-init.py --sub-file /tmp/sub.txt          # Add --aibox <path> if aibox is not at ~/claude/Linux-terminal
rm /tmp/sub.txt
```

- The recording is real: it writes `config/` in the aibox repository, builds images, and starts containers, just like running `./aibox init` manually. To record from scratch, first run `./aibox destroy` in the aibox repository and delete `config/`.
- The script uses a 100×32 pseudo-terminal and answers the wizard prompts: option 1 → paste links → all nodes → project number 1 (`~/code/myapp`, writable) → `~/code/specs` (read-only) → skip command installation → start immediately. Unrecognized [Y/n] prompts receive Enter to accept the default.
- If the first nodes are in a region unsupported by the AI service, the wizard warns and stops. Record again with a node filter such as `--filter '日本|JP'`. Use `--mount number-or-path:y|n` to specify project folders and write access.
- Before writing `init/cast.js`, the script redacts the data: node links retain only their protocol, public IPv4 addresses become documentation addresses such as 203.0.113.x, and IPv6 addresses become 2001:db8::. Replace provider names with `--redact 'original=replacement'`. If fragments of the original links remain, the script reports an error and does not generate the file.
- The unredacted recording stays in `.aibox/init-raw.cast.json` in the aibox repository, where it is ignored by Git. It is not copied into this directory. Use `--remask` to regenerate the output with different redaction rules without recording again.
- Before publishing, review the `init/` page for anything you do not want to make public, such as provider names in node labels.

## Editing guidelines

- `README.md` is the default Chinese entry point; `README.en.md` is the English version. Keep both documents in sync and retain the language links at the top.
- The two homepages share the same structure. Update both when changing content.
- Base product claims on the aibox repository's `README.md`, `docs/`, and `AGENTS.md`. Do not label untested environments, such as a physical Mac, SELinux, or rootless Docker, as verified.
- Reducing real environment exposure and related account restriction or ban risks is a design goal, not a verified guarantee against bans. Do not claim complete machine fingerprint masking or removal of telemetry and account identifiers.
- Exit IPs in terminal demos use documentation ranges such as 203.0.113.x and 198.51.100.x. Redact real IPs and subscription URLs before using real recordings.
- The hero terminal animation reads the page's `<script type="application/json" id="demo-script">`. Keep it consistent with `<pre id="demo">`, which provides the final output when JavaScript or animations are disabled.
- Do not add Google Fonts, analytics, or other third-party resources. The footer states that the site makes no requests to third-party resources.
