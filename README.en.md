# aibox website

[简体中文](README.md) | **English**

A single-page website for aibox, with Chinese and English pages. It is fully static: no build step, dependencies, tracking scripts, or requests to third-party resources. Fonts come from the system.

The website's core message: run Claude Code in a separate Docker environment through a remote node to reduce what the tool can access or expose about your real public IP, host system, and personal configuration. The goal is to reduce related account restriction and ban risks. Codex and other terminal tools can use the same environment.

Both language versions, the social preview, and the recording page explain the scope: aibox provides network and file isolation, with no guarantee against bans or complete machine fingerprint masking. Kernel and CPU information, identity information in authorized files, tool telemetry, and account identifiers may remain accessible. Browser login, initialization, builds, subscriptions, and diagnostic traffic have separate network boundaries.

The website and aibox product code live in separate repositories. This directory contains only the website. The recording script expects the aibox repository at `~/claude/Linux-terminal` by default.

```text
aibox-web/
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
├── docs/DEPLOYMENT.md  Independent deployment design (Chinese)
├── nextjs/sync.sh    Legacy sync tool; not for production
└── tools/record-init.py  Records ./aibox init and generates init/cast.js
```

## Local preview

Choose either command, then open http://localhost:8000/:

```bash
cd /Users/ahao/Documents/ChatGPT/充值/aibox-web && python3 -m http.server 8000
```

```bash
npx serve . -l 8000
```

You can also open `index.html` directly. Under `file://`, copy buttons use a compatibility fallback.

## UseHooo integration decision (2026-10-27)

The public entry point will be `https://usehooo.com/aibox/`, with `/aibox/en/` and `/aibox/init/`. Nginx will serve static files from a separate directory, outside the main site's Next.js routing and build process.

- Keep source in the separate `aibox-web/` Git repository.
- Maintain independent artifacts, server directories, release records, deployment permissions, and rollback.
- Do not copy files into the main site's `public/aibox/`, create `app/aibox/page.tsx`, or embed the site in an iframe.
- Initial setup requires a coordinated Nginx configuration change and, optionally, a main-site navigation link. Routine content releases then switch only the aibox release.
- Sharing an origin and server still shares browser-origin privileges and infrastructure. Independent deployment is not complete security isolation.

See the [deployment design](docs/DEPLOYMENT.md) (Chinese) for boundaries, proposed directories, release steps, and acceptance checks. Server paths are proposals; production integration has not been implemented.

## Delivery status

| Item | Status |
|---|---|
| Chinese, English, and recording pages | Static source exists; Chinese commercial content is not yet synchronized with English |
| Local static checks | JS syntax, local resource references, and page anchors passed on 2026-10-27; browser acceptance remains pending |
| Legacy Next.js sync script | Failed in a temporary-directory run; excluded from the production design and not repaired |
| Independent packaging, release, and rollback scripts | Not implemented |
| Server directory, Nginx routing, main-site navigation | Verification and implementation pending; not deployed |
| Commercial products and fulfillment | Planning only; displayed prices and buttons do not prove products are available |

## Content checks before publishing

- Normalize canonical, hreflang, and og:url to the full `/aibox/` URLs and corresponding subpages with trailing slashes. Remove `SITE_DOMAIN` without duplicating the prefix.
- Replace `LICENSE_NAME` only after checking the actual repository license. A footer saying MIT is not license evidence.
- If a social preview is needed, export `og.svg` as a 1200×630 PNG and reference the existing output in page metadata.
- Synchronize language versions, prices, boundaries, and links. Do not enable purchases before commercial terms and fulfillment are ready.
- The main site does not currently support `?category=Aibox` selection. Paid buttons on the Chinese page now show an unavailable preparation state; its footer links to the general store. Commerce integration requires separate main-site acceptance.
- Publish public static assets only. Exclude documentation, tools, Git data, environment configuration, and raw recordings.

## Legacy Next.js integration

`nextjs/sync.sh` is disabled and exits without writing to a main-site checkout. The previous sync approach deleted and recreated a `public<base>` directory and is incompatible with independent updates. Use the whitelist package and static release selection tools described in `docs/DEPLOYMENT.md`.

## Record ./aibox init again

The `init/` page replays a real run of `./aibox init`. Record it again when the aibox wizard or its output changes:

```bash
mkdir -p ~/code/myapp ~/code/specs && git -C ~/code/myapp init -q   # Example folders to authorize; myapp must be a Git project to appear in the wizard
printf '%s\n' "YOUR_SUBSCRIPTION_URL" > /tmp/sub.txt
cd /Users/ahao/Documents/ChatGPT/充值/aibox-web
python3 tools/record-init.py --sub-file /tmp/sub.txt          # Add --aibox <path> if aibox is not at ~/claude/Linux-terminal
rm /tmp/sub.txt
```

- The recording is real: it writes `config/` in the aibox repository, builds images, and starts containers, just like running `./aibox init` manually. Use a dedicated demonstration environment; do not destroy or clear an active working environment to make a recording.
- The script uses a 100×32 pseudo-terminal and answers the wizard prompts: option 1 → paste links → all nodes → project number 1 (`~/code/myapp`, writable) → `~/code/specs` (read-only) → skip command installation → start immediately. Unrecognized [Y/n] prompts receive Enter to accept the default.
- If the first nodes are in a region unsupported by the AI service, the wizard warns and stops. Record again with a node filter such as `--filter '日本|JP'`. Use `--mount number-or-path:y|n` to specify project folders and write access.
- Before writing `init/cast.js`, the script redacts the data: node links retain only their protocol, public IPv4 addresses become documentation addresses such as 203.0.113.x, and IPv6 addresses become 2001:db8::. Replace provider names with `--redact 'original=replacement'`. If fragments of the original links remain, the script reports an error and does not generate the file.
- The unredacted recording stays in `.aibox/init-raw.cast.json` in the aibox repository, where it is ignored by Git. It is not copied into this directory. Use `--remask` to regenerate the output with different redaction rules without recording again.
- Before publishing, review the `init/` page for anything you do not want to make public, such as provider names in node labels.

## Editing guidelines

- `README.md` is the default Chinese entry point; `README.en.md` is the English version. Keep both documents in sync and retain the language links at the top.
- Keep both homepages synchronized. Chinese commercial content currently differs from the English version.
- Base product claims on the aibox repository's `README.md`, `docs/`, and `AGENTS.md`. Do not label untested environments, such as a physical Mac, SELinux, or rootless Docker, as verified.
- Reducing real environment exposure and related account restriction or ban risks is a design goal, not a verified guarantee against bans. Do not claim complete machine fingerprint masking or removal of telemetry and account identifiers.
- Exit IPs in terminal demos use documentation ranges such as 203.0.113.x and 198.51.100.x. Redact real IPs and subscription URLs before using real recordings.
- The hero terminal animation reads the page's `<script type="application/json" id="demo-script">`. Keep it consistent with `<pre id="demo">`, which provides the final output when JavaScript or animations are disabled.
- Do not add Google Fonts, analytics, or other third-party resources. The footer states that the site makes no requests to third-party resources.


## Store-managed plans

Prices, descriptions, feature lists, terms and button labels come from the same-origin `/api/aibox` endpoint. Chinese is the fallback for product fields without English copy. Paid services require email sign-in; after payment the customer sends their email and order number to support, which verifies the paid order before arranging delivery. If the API or support is unavailable, paid links close. Free GitHub self-service remains accessible. See `docs/DEPLOYMENT.md` for independent packaging and rollback.
