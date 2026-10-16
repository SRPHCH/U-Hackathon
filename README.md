# Solora — Landing page + AI Workspace (prototype)

Solora is a platform concept for **solo e-commerce entrepreneurs**: a team of AI agents (Finance, Marketing, Legal,
Market & Industry Update, Daily Update, Operations, …) coordinated by a **Secretary** agent. This repo holds the
front-end prototype built for the U-Hackathon:

1. **Landing page** (`solora-landing.html`) — white / pastel-pink marketing page with a 3D ant mascot.
2. **AI Workspace** (`solora-app.html`, also embedded in the landing page) — a Grok-bot-style chat UI where every
   AI "employee" has a live 3D ant profile.
3. **Ant engine** (`ant-mascot.html`) — the Three.js ant renderer reused for the hero mascot, avatar snapshots,
   live avatars with role props, and the 3D profile view.

> Everything is static HTML/JS. There is **no backend**: agent replies in the Workspace are canned demo text.
> The UI language is **Thai** (brand terms stay English: Agent, AI, Token, Secretary, Plan Demo).

Read `docs/CONVERSATION_SUMMARY.md` for the full history of what the product owner asked for and why
(also zipped in `docs/solora-handoff.zip`).

---

## 1. Quick start

```bash
# 1) put your API keys on the server side (never in the page)
cp keys.example.env keys.env        # then fill GEMINI_API_KEY / ELEVENLABS_API_KEY
# 2) run the site + API proxy (Python 3.9+, standard library only)
python server.py
# 3) open http://127.0.0.1:8765/   (press "เริ่มใช้งาน" to enter the Workspace)
```

**API keys are locked on the server.** `server.py` serves the pages and proxies `/api/gemini/...` and `/api/eleven/...`,
adding the keys from `keys.env`. The browser never receives a key, `keys.env` is git-ignored and refused if requested over
HTTP, and the proxy only accepts calls from this site's own pages (`X-Antistant` header + same Origin), validates model/voice ids,
caps request size and rate (120 calls / 10 min per client), and can require `ACCESS_PASSWORD`. By default it listens on
127.0.0.1 only. Anyone who receives the *files* (including `keys.env`) can still read the keys, so use restricted keys with
spending limits and rotate them after the event. Without the server (or without keys) the app falls back to local rules
and browser voices.

- Open the files through `http://` (or directly from disk in a normal browser). Viewers that render local files as
  static snapshots (e.g. some IDE previews) cannot load the sibling `ant-mascot.html` iframes — the 3D parts will not appear.
- `solora-landing.html` is the deliverable and already contains the Workspace. `solora-app.html` is the same
  Workspace as a standalone page (its logo/“หน้าแรก” link points to `solora-landing.html`).
- `ant-mascot.html` **must sit next to** `solora-landing.html` / `solora-app.html`.

## 2. Repository map

| Path | What it is |
|---|---|
| `solora-landing.html` | **Built output.** Bundled single file (runtime + fonts + template + boot loader + embedded Workspace). Do not hand-edit. |
| `solora-app.html` | Workspace source (hand-edited, plain HTML/CSS/JS). Also embedded into the landing build. |
| `ant-mascot.html` | **Built output** of `tools/make_ant.py` (patched copy of the user's ant studio). Do not hand-edit. |
| `source/ant-studio.html` | The original 3D ant character studio supplied by the product owner (input of `make_ant.py`). |
| `source/solora-landing.orig.html` | Original bundled landing page (outer shell + assets + runtime). Input of `build.py`. |
| `tools/markup.html` | Landing page markup (custom `x-dc` template syntax — see §4). |
| `tools/style.css` | Landing page + scoped styles. |
| `tools/template.original.html` | Original unpacked template; only its `@font-face` block and component script are reused. |
| `tools/build.py` | Builds `solora-landing.html` (markup+css+script → template, embeds Workspace, boot loader). |
| `tools/make_ant.py` | Builds `ant-mascot.html` from `source/ant-studio.html` (all mascot behaviour lives here). |
| `tools/boot.gif` | 18-frame GIF of the Secretary ant hopping, used by the boot loader. |
| `tools/mkgif.py`, `tools/gifsrv.py` | Helpers used to regenerate the GIF (see §7). |
| `docs/CONVERSATION_SUMMARY.md` | Full requirements/decision history. |
| `docs/solora-handoff.zip` | Zip with the summary + this README. |

## 3. Rebuilding

```bash
python tools/make_ant.py   # source/ant-studio.html  -> ant-mascot.html
python tools/build.py      # tools/* + solora-app.html + ant-mascot.html -> solora-landing.html
```

Run both after editing anything in `tools/` or `solora-app.html`. Both scripts are idempotent and path-relative
(verified: they reproduce the committed outputs byte-for-byte). Python 3.10+, standard library only
(`Pillow` is only needed for `tools/mkgif.py`; note `python -I` hides user-site packages such as Pillow).

**Rule of thumb**
- Landing copy/layout/style → edit `tools/markup.html`, `tools/style.css`, then `python tools/build.py`.
- Component data (agent cards, FAQ, plans) → patched in `tools/build.py` (search for `faqData`, `plans`, `_norm`).
- Workspace → edit `solora-app.html`, rebuild landing.
- Mascot behaviour/props/poses → edit `tools/make_ant.py` (patch strings against `source/ant-studio.html`), rebuild both.

## 4. Landing page internals

- The original page is a **bundler single file**: a shell that base64-decodes assets, then replaces
  `document.documentElement` with the template. `build.py` re-serialises the template JSON into the shell.
- The template uses a small custom runtime ("DC"): `<x-dc>`, `sc-for`, `sc-if`, `{{ expr }}`, `sc-camel-on-click`,
  `style-hover`, and a component class with `renderVals()`. Keep dynamic data in the script block patched by `build.py`.
- `build.py` runs `_norm()` over markup and script: **Thai terms are normalised** (`เอเจนท์→Agent`, `เอไอ→AI`,
  `โทเคน→Token`, `AI Advisor→Secretary`, `Oracle Agent→Market & Industry Update`) and spaces are inserted between
  Thai and Latin words. Write new copy in either form; it will be normalised.
- Sections (in order): nav → hero (headline, lede, single CTA "เริ่มใช้งาน", mascot iframe) → agents bento (6 cards,
  no status/code badges) → Secretary section (headline "มี Secretary เลือก Agent ให้ ไม่ต้องนั่งเลือกเอง") → market
  forecast section → pricing (one card: **Plan Demo ฿0**, monthly/yearly toggle shows "ถูกกว่า 0%") → FAQ (4 items,
  centred) → CTA → footer.
- The Workspace is injected **outside** `<x-dc>` (`#ws`) so the runtime never re-renders it; its CSS is
  auto-prefixed with `#ws`. Navigation is hash based: `#app` shows the Workspace, anything else shows the landing page.
  Workspace classes that collided with landing classes were renamed `ws-brand`, `ws-btn`, `ws-plan`, `ws-note`.
- `ant-mascot.html?v=5` is referenced by `<iframe>` in the hero. Bump the query string to bust caches.
- Embedding the mascot via `srcdoc` was tried and fails (script SyntaxError in the srcdoc context) — don't.

## 5. Ant engine (`ant-mascot.html`)

A patched copy of the studio. Always a **transparent, chrome-free viewer** of the `ant` shape in `plush` material.
Configuration comes from the URL:

| Param | Meaning |
|---|---|
| `style` | Accessory set from the studio (`gentleman`, `royal`, `artist`, `scholar`, `detective`, `cool`, `athlete`, `playful`, `futuristic`, …) |
| `color` | Body colour `#RRGGBB` (URL-encode `#`) |
| `role` | Role key for props/poses (`secretary`, `finance`, `marketing`, `legal`, `market`, `daily`, `ops`, `support`, `analyst`) |
| `snap=1` | **Snapshot service**: no visible model; renders PNG avatars on request via `postMessage` |
| `av=1` + `look=down\|diag` | **Small live avatar** mode (tight framing, low-res, role props, not clickable) |
| `chat=1` | Legacy "dock" mode (hops/cheers; no intro) — not used by the current Workspace |
| `debug=1` | Exposes `window.__DIR` (`freeze=['fall',0.5]` etc.) for stepping animations in tests |

Default (no `av`/`snap`) is the **hero mascot**: intro (faces right → two hops to face the viewer → leans and waves a
👋 emoji) → endless idle (rocking + turning, an occasional hop/twirl) → **tease** when clicked: kicked backwards onto
its back → lies dazed → jumps up → rages (steam, anger mark, red glow, stomping) → a user's hand offers a banknote
from the bottom edge → the ant hops over to inspect it → takes it → hops back.

### postMessage protocol

Parent → mascot
- `{type:'ant:state', state:'idle'|'typing'|'think', role}` — look at the composer / cheer with the role prop
- `{type:'ant:config', style, color, role, key}` — rebuild the model without reloading the iframe
- `{type:'ant:render', id, style, color, pose?, res?, margin?}` (snap mode) — render one PNG

Mascot → parent
- `ant:shown` (hero's first frame on screen), `ant:built` (model built), `ant:configured {key}`,
  `ant:ready` (snap service ready), `ant:rendered {id, url}` (PNG data URL with alpha)

### Role → look (all variants are the same ant model; only accessory + colour + prop differ)

| Role | Style | Default colour | Working prop (when "thinking") |
|---|---|---|---|
| Secretary (mandatory per team; the landing ant) | `gentleman` | `#E2513F` | black landline handset at the ear + coiled cord |
| Finance | `royal` | `#FFCC38` | fanning banknotes (counting) |
| Marketing | `artist` | `#FA70AB` | megaphone |
| Legal | `scholar` | `#4778FF` | gavel (taps with a nod) |
| Market & Industry Update | `detective` | `#04BB9F` | magnifying glass scanning |
| Daily Update | `cool` | `#00B1FF` | coffee mug (sips) |
| Operations | `athlete` | `#FF8066` | cardboard box |
| Customer Support | `playful` | `#A25BFF` | headset with mic |
| Data Analyst | `futuristic` | `#B6D80B` | animated bar chart |

## 6. Workspace (`solora-app.html`)

- Layout copied from the Grok-bot reference: left list (search, "+", teams with collapsible groups), right chat,
  centred name pill on top, pill composer at the bottom. Dark theme. Mobile: list ⇄ chat views.
- **Teams**: one default team "ทีม 1" (renamable via the pencil on the group header; more teams can be created, each
  gets a **Secretary automatically**). The Secretary cannot be deleted.
- **Adding an employee**: the role is a *select* only (no free text, no "what should the bot do" field). Each role has
  its own **conversation pattern** (opening message + how it asks questions), shown in the dialog. Optional name,
  colour (10 presets + custom colour input), team.
- **Secretary routing**: replies to a message by keyword and shows a button that opens the right team member
  (`ROUTE` table in the script). Other roles answer with canned, honest "demo mode" text.
- **Profiles**: every avatar is a 3D ant snapshot ringed in the employee colour. Header and sidebar avatars of the
  *active* employee are **live** (`av=1`): they look at the composer while you type (header: straight down; sidebar:
  diagonal), and perform the role pose + prop while a reply is pending. Click the header pill for the full live 3D
  profile (colour changes apply to the model and every avatar).
- **State**: `localStorage` keys `solora.workspace.v2` (teams, bots, messages) and `solora.avatars.v1`
  (PNG snapshot cache, max 40). Changing the schema → bump the key suffix.
- `window.SoloraWS = { start(), progress() }` is the hook for the boot loader.

## 7. Boot loader & preloading

- `build.py` replaces the shell's thumbnail with a **loader**: the Secretary GIF (`tools/boot.gif`, inlined), a
  progress bar and text. The shell is patched so this element survives the document swap; `window.__boot`
  exposes `set(pct, text)`, `show(text)`, `hide()`.
- Sequence: shell (8 %) → template swap (40 %) → **hero ant on screen** (`ant:shown`, 70 %) → loader hides →
  background preload via `SoloraWS.start()` (avatar snapshots, 2 live avatar frames, the profile frame) → 100 %.
- If the user enters `#app` before preload is complete the loader is shown again with
  **"Preparing for your team..."** until everything is ready.
- Fail-safes: landing loader gives up after 25 s; Workspace entry after 70 s (falls back to flat faces).
- Regenerating the GIF: serve the repo, open `ant-mascot.html?snap=1`, run `tools/gifsrv.py` (POST sink), render
  18 frames with `postMessage({type:'ant:render', ..., pose:{y,rz,yaw,sq}, margin:1.8})`, then `python tools/mkgif.py`.

## 8. Known issues / decisions to revisit

- **No AI backend.** All replies are canned; wire a real LLM/agent API into `composeReply()` in `solora-app.html`.
- **Placeholder contact email** `XXX@gmail.com` (FAQ + footer) — replace with the real address.
- **"Oracle" naming**: the Secretary section's mix table and per-industry notes (`NAMES`, `IND` in the component
  script) still show "Oracle" next to "Market Update"; the owner treats Oracle ≡ Market & Industry Update.
  The industry picker/panel was removed from the hero, but `IND.it` is still the default data for that table.
- Landing theme (white/pastel pink) and Workspace theme (dark) intentionally differ — owner may want them unified.
- Pricing is a single free **Plan Demo**; the yearly toggle is cosmetic ("ถูกกว่า 0%").
- Per-role gestures/props were verified visually for Secretary and Finance; the others were checked only by
  code/pose stepping. Prop sizes are tuned for 32–48 px avatars and the 360 px profile view.
- Mobile layouts were checked at a narrow pane only; real-device testing is still needed.
- Reduced-motion: idle/intro animations deliberately ignore `prefers-reduced-motion` (owner wanted constant life);
  CSS transitions respect it.
- Requires internet for three.js (`cdn.jsdelivr.net`) and Google Fonts (Anuphan; falls back to IBM Plex Sans Thai /
  system fonts).

## 9. Suggested next steps

1. Connect the Workspace to a real agent backend (per-role system prompts = the `pattern`/`hello` fields in `ROLES`).
2. Real sign-up / auth in front of `#app`; persist teams server-side.
3. Unify naming (Oracle → Market & Industry Update) and replace the placeholder email.
4. Ship `three.js` locally to remove the CDN dependency and speed up first load.
5. Review accessibility (focus order in the Workspace dialogs, contrast of dark theme chips).
