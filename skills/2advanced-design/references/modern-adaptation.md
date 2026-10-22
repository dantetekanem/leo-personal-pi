# Modern adaptation

How to keep the 2Advanced taste and meet current UI requirements. Each rule names the evidence that motivates
it. Labels: **[rec]** observed in the 2026 study, **[asset]** from site code or files, **[inf]** inference.

## 1. What aged badly, and what was already right

| Problem in the originals | Evidence |
| --- | --- |
| Canvas-only UI: no semantic text, no focus order | V3 reboot accessibility tree is empty; seven stacked canvases [rec] |
| Fixed stage scaled or clipped | V3 reboot scales a 1280x1046 artboard with `Fit.contain` (micro text ~5 px at 768 px wide); V4 970x655; V5 noscale 975 px column and `viewport width=1024` [rec] [asset] |
| Long ceremonies | boots 11.8-16 s; section changes 3.2-6.6 s [rec] |
| Tiny type, low contrast | 8 px pixel fonts (V4), 9-10 px Verdana (V5); on today's hub 9-11 px labels at 35-42% white measure 3.0-4.05:1 [asset] |
| State without URLs | V3 reboot and V4 have none [rec] [asset] |
| Popups | V4 store and wallpapers open sized windows that modern browsers block [asset] |
| Placeholders shipped | V3 reboot product and gallery PNGs 404 (hard-coded `/assets/...` path), "LIST ITEM 9", "LONG TITLE THAT ANIMATES IN ON PROJECT LOAD" [rec] [asset] |
| Heavy assets | mainstage.riv 5.85 MB with 281 embedded PNGs; WAV soundtrack; an 849 KB logo PNG on the hub [asset] |
| No reduced-motion path | only Kesey Signal has one [asset] |

| Already right: keep it | Evidence |
| --- | --- |
| Deep links and titles per section | V5 `#company`, "2Advanced Studios - company"; paths like `company/pressnews/pressreleases` [rec] [asset] |
| Saved preferences | V5 `SharedObject` stores language, audio and top-nav state [asset] |
| Skip and mute in the boot | V4 boot copy "+ SKIP ANIMATION >" and "+ DISENGAGE AUDIO" [asset] |
| Sound control always visible | V3 AMBIENCE.MUTE, V4 GLOBAL AMBIENCE player, V5 Soundscape slider [rec] |
| Audio starts inside a user gesture | V4/V5 archive gates resume an AudioContext on the click [asset] |
| Crawlable summary and llms.txt | V3 reboot static HTML, JSON-LD, `llms.txt` [asset] |
| Reduced motion and remembered mute | Kesey Signal: 12 CSS blocks and 4 `matchMedia` checks; muted autoplay that fades in; mute in `sessionStorage` [asset] |

## 2. Architecture: three layers

1. **Content layer**: semantic HTML. Landmarks, headings, nav, links, buttons, forms and copy. Server-rendered
   or prerendered so it works without the motion layer.
2. **Motion and chrome layer**: CSS, SVG, WAAPI, and canvas/Rive/Lottie only where vector timelines beat CSS.
   Decorative micro text, marks, frames and glyphs live here with `aria-hidden="true"` and `pointer-events: none`
   unless they are real controls.
3. **Art layer**: responsive `<picture>` or video, one "world" per section, preloaded on intent.

Rive and canvas carry no accessible text. When a Rive element is a control, put a real `<button>` over it and
forward state to the state machine inputs (the V3 reboot already maps DOM events to state machine inputs).

## 3. Boot sequence

- Draw the shell (frame, nav, sound toggle, skip control) within about one second; spend the long cinematic part
  inside the hero window, not across the whole screen.
- Full version once per session, short signature on repeat visits, nothing (or a 150 ms fade) under reduced
  motion. Escape and a visible "SKIP SEQUENCE" control finish it at once.
- Focus never lands on decoration; the first Tab reaches the skip control or the nav.

```js
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const mode = reduce ? "none" : sessionStorage.getItem("adv-booted") ? "short" : "full";
document.documentElement.dataset.boot = mode;
const anims = runBoot(mode); // returns only finite Animation objects
const done = () => {
  sessionStorage.setItem("adv-booted", "1");
  document.documentElement.dataset.boot = "done";
};
Promise.all(anims.map((a) => a.finished)).then(done, done);
const skip = () => anims.forEach((a) => a.finish());
document.querySelector("[data-skip]").addEventListener("click", skip);
addEventListener("keydown", (e) => { if (e.key === "Escape") skip(); });
```

## 4. Section changes

- Every section and selection has a URL, `history.pushState`, a `popstate` handler and a title update.
- Use the View Transitions API for the signature move (slit, slash, shutter) and fall back to an instant swap.
- Interruptible: a second navigation skips the running transition instead of queueing it.
- Stream the next world: preload its art and data on `pointerenter` or `focus` of the nav item.

```js
let running;
export function navigate(url, render, { push = true } = {}) {
  running?.skipTransition();
  if (push) history.pushState({}, "", url);
  running = document.startViewTransition ? document.startViewTransition(render) : (render(), null);
}
addEventListener("popstate", () =>
  navigate(location.href, () => renderRoute(location.pathname), { push: false }));
```
(`renderRoute` is the app's own renderer.)

## 5. Reduced motion map

| Gesture | Reduced alternative |
| --- | --- |
| Boot sequence | skip it; show the final state, optional 150 ms fade |
| Slit, slash, shutter transitions | crossfade 120-150 ms, or instant |
| Power-on flash cascade | modules appear together, no flash |
| Light bar sweeps, flicker, blinks | none |
| Decoder and type-on text | final text at once |
| Hover glows and scanlines | color or border change only |
| Idle loops, rotating features | stopped; manual next/previous controls |
| Cinematic fade-up | static frame |

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important; transition-duration: 1ms !important; }
}
```
Use the blanket rule as a safety net only; design each alternative explicitly.

## 6. Flash safety

- WCAG 2.3.1: no more than three general flashes in any one-second period. A flash is a pair of opposing
  luminance changes of 10% or more over a large area.
- V3's section change flashes the content window white three times, plus a white slab mid-wipe, in about three
  seconds; the script finds two
  abrupt flash pairs at 733 and 1,083 ms, so the worst second has two [rec]. V4's slash wipe has two pairs
  67 ms apart [rec]. Legal per second, but harsh when repeated: keep full-field flashes for the first boot at
  most.
- Prefer module-sized flashes, peak overlay opacity 0.6-0.85, and never stack two flashes within ~350 ms.
- Check with `scripts/motion.py --flashes` on a recording (approximate: full-frame mean luminance jumps).

## 7. Type, contrast and legibility

- Copy at 16 px or more in a readable face; dense UI labels at 14 px or more; micro text is decoration.
- 4.5:1 for text, 3:1 for large text and UI boundaries. Translucent panels over art need a scrim or a measured
  worst case.
- Pixel fonts at native size for short labels only. Uppercase tracked labels need extra size or weight.
- Machine-voice names are fine for systems; actions use plain verbs ("View project", "Send").

## 8. Responsive layout

| Original | Modern mapping |
| --- | --- |
| V3 shell: banner / logo band / tabs / window / utility bar / 3x2 modules | header and tabs collapse to a menu below ~720 px; window full width; modules 3 -> 2 -> 1 columns |
| V4 panels with expand/collapse | a real disclosure pattern (`button[aria-expanded]`); the content panel grows into the free column on wide screens and stacks on narrow ones |
| V5 four-column hairline grid and navigation drawer | 4 -> 2 -> 1 columns; the drawer becomes a full-screen sheet on small screens; destinations keep their columns as sections |
| Full-bleed matte | `<picture>` art direction with a portrait crop that keeps the focal point (pyramid, figure) |

- Use container queries for modules so each one adapts to its slot.
- Never scale a fixed artboard to fit. For Rive, use responsive layouts where the runtime supports them, or one
  artboard per breakpoint.
- Touch: targets 44 px or more, hover effects mirrored on press and focus, no hover-only menus.

## 9. Input and focus

- `:hover` and `:focus-visible` share the same gesture (scanline open, split shutter, glow bloom).
- The navigation drawer is a button with `aria-expanded` and `aria-controls`; it opens on click, Enter or Space
  and closes on Escape; secondary columns fill on focus as well as hover.
- Focus rings use the light language: a 2 px ring in the accent with an outer glow, never removed.

## 10. Sound

- Off by default, or muted autoplay that fades in only after the user turns sound on. Persist the choice.
- One visible toggle with `aria-pressed`, reachable by keyboard, in the header.
- UI cues short (20-60 ms ticks, sweeps under long moves) and quieter than the loop; no sound on focus moves.
- Compressed audio (Opus or AAC), not WAV.

```js
const KEY = "adv-sound";
const toggle = document.querySelector("[data-sound]");
let ctx;
function setSound(on) {
  toggle.setAttribute("aria-pressed", String(on));
  localStorage.setItem(KEY, on ? "on" : "off");
  if (on) { ctx ??= new AudioContext(); ctx.resume(); } else { ctx?.suspend(); }
}
toggle.addEventListener("click", () => setSound(toggle.getAttribute("aria-pressed") !== "true"));
if (localStorage.getItem(KEY) === "on") {
  toggle.setAttribute("aria-pressed", "true");
  addEventListener("pointerdown", () => setSound(true), { once: true }); // browsers need a gesture first
}
```

## 11. Performance

- Animate `transform` and `opacity`; keep `clip-path`, `filter`, `backdrop-filter` and glows to a few layers and
  test them on a low-end device.
- Split motion assets per section instead of one 5.85 MB file; lazy-load section art and timelines.
- AVIF or WebP art with `srcset`; font subsets with `font-display: swap`; preload only the first world.
- Pause idle loops off-screen (IntersectionObserver) and in hidden tabs (`visibilitychange`).
- `content-visibility: auto` for long off-screen sections.

## 12. Robustness

- Progress indicators reflect real loading (the originals computed `loaded / total`); never fake 100%.
- Errors stay in voice and stay honest: "SIGNAL LOST // RETRY" with a working retry.
- No placeholder copy or standby states in production; test asset paths under the deployed base path.
- External links open normally (no sized popups); downloads (wallpapers, kits) are plain links.

## 13. Acceptance checklist

- [ ] Content readable and operable with JavaScript animation disabled.
- [ ] First visit: shell usable in about 1 s; skip works (button and Escape).
- [ ] Repeat visit: short boot; section change 300-700 ms; interruptible.
- [ ] Reduced motion: every gesture in section 5 has its alternative; nothing loops.
- [ ] Flashes: three or fewer per second; none full-field in repeat navigation.
- [ ] Contrast 4.5:1 for text; copy 16 px or more.
- [ ] Layout reflows at 1440, 1024, 768 and 390 px wide.
- [ ] URLs, Back/Forward and titles work for every section.
- [ ] Sound off by default; toggle persists; keyboard reachable.
- [ ] Keyboard path reaches everything; focus visible; drawer has `aria-expanded`.
- [ ] Motion verified against the score (see `motion.md`, section 7).
