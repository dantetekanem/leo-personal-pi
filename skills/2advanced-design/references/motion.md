# Motion: the core of the taste

Labels: **[rec]** measured from browser recordings (MediaRecorder at 60 fps, analyzed at 30-60 fps).
**[asset]** read from the SWF/Rive files (frame counts / fps, tween curves, ActionScript). **[inf]** inference.
Times are ms from the trigger unless stated.

## 1. House constants

| Constant | Value | Evidence |
| --- | --- | --- |
| One tween beat | 150-250 ms. V4 median position tween 220 ms, scale 195 ms; V5 position 171 ms, alpha 220 ms, tint 244 ms; V3 ramps 160-240 ms | [asset] |
| Long beat (big panels, mattes, pops) | 400-610 ms; V5 matte slit 1,073 ms in-out | [asset] |
| Cascade step | 25-40 ms for list items (V5 nav build 35 ms primary, 25 ms secondary; V3 most common gap 40 ms) | [asset] |
| Module stagger | ~130 ms (V3), 130-250 ms (V5), in reading order | [rec] |
| Sequence beats | intro beats land every ~250-300 ms, often with a blank frame between them | [rec] |
| Entrance easing | ease-out, exponent k 3-4 (cubic to quart); fly-ins up to k 5 | [asset] V4 51% of moves ease-out, median k 3.0 |
| Exit easing | ease-in, k 2-3 | [asset] |
| Big slides | S-curve ease-in-out (V5 sections 488 ms; V5 matte 1,073 ms) | [asset] |
| Light (fade, tint, flash) | linear; V4 white "develop" tint 317-488 ms; V5 tint 244 ms | [asset] |
| Springs / bounce | none. Overshoot only on V5 bracket marks (Back easing) | [asset] |
| Flicker | 1-frame steps: V4 alpha 39% <-> 100% at 24 ms; V3 opacity 0.6 <-> 1.0 every 40 ms for ~5 frames; V3 preloader decay 1.0 -> 0.6 -> 0.3 -> 0.6 -> 1.0 | [asset] |
| Frame rates | V4/V5 41 fps (24.4 ms/frame); V3 Rive 25 fps (40 ms/frame) | [asset] |

CSS tokens that reproduce these curves:

```css
:root {
  --adv-ease-out: cubic-bezier(0.33, 1, 0.68, 1);      /* cubic, k=3: default entrance */
  --adv-ease-out-hard: cubic-bezier(0.25, 1, 0.5, 1);  /* quart, k=4: panels, pops, wipes */
  --adv-ease-out-max: cubic-bezier(0.22, 1, 0.36, 1);  /* quint, k=5: long fly-ins */
  --adv-ease-in: cubic-bezier(0.32, 0, 0.67, 0);       /* cubic: exits */
  --adv-ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);   /* big slides, the slit */
  --adv-light: linear;                                 /* fades, tints, flashes */
  --adv-beat: 200ms;
  --adv-beat-short: 120ms;
  --adv-beat-long: 450ms;
  --adv-step: 35ms;          /* list cascade */
  --adv-stagger: 130ms;      /* module cascade */
  --adv-frame: 40ms;         /* one flicker frame */
}
```

## 2. Gesture catalog

Each gesture: what it looks like, when 2Advanced used it, measured timing, and a modern build.

### Registration marks and micro readout
Tiny corner ticks, `=` marks, crosshairs and 5-8 px status text appear on an empty stage before anything else
(V4 "PROPHECY.DATACORE-04028_AWAKE +", "NODE ENGAGED"; V5 "STANDBY: INITIALIZING:"). They blink in and out in
1-3 frame steps. [rec] V5 marks at 0.9 s; V4 readouts at 1.5-3.9 s.
Build: absolutely positioned decorative spans, `aria-hidden`, toggled with stepped opacity keyframes
(`steps(1)`), each 80-200 ms, 40-120 ms apart.

### Line tracer and hairline draw
A line draws itself (scaleX from one end), often turning corners like a circuit trace or carrying a small node
or boxes along it. Frames and panel outlines are drawn this way before they fill. [rec] V4 traces 1.5-5.4 s;
V3 frame lines draw down and across in ~200-300 ms each.
Build: `transform: scaleX(0) -> scaleX(1)` with `transform-origin` at the start edge, `--adv-ease-out`,
150-300 ms; corners as separate segments chained by delay; SVG `stroke-dashoffset` for diagonal traces.

### Converging hairlines and flare (V5)
Two hairlines grow from the left and right edges toward the center, meet, and flare into a short bright streak.
[rec] 470 ms to meet, flare ~120 ms. [asset] edge travel 659 ms ease-out k 2.
Build: two 1 px bars, `transform-origin: left` / `right`, scaleX 0 -> 1 over 470 ms `--adv-ease-out`; then a
center element with a horizontal radial gradient scaling scaleX 0.2 -> 1 and fading out over 120-200 ms linear.

### Slit open and close (V5 signature)
The world image opens from a 1-2 px horizontal slit to full height; leaving a world, it closes back into a slit
and a dot. [rec] close ~400 ms; open ~450-600 ms visible, fast start and soft settle. [asset] matte layers move
y +/-325 px over 1,073 ms ease-in-out on show, 756 ms on hide [inf: the two halves of the slit mask; the slow
start of the ease is invisible while the slit is thin].
Build: `clip-path: inset(50% 0 50% 0)` -> `inset(0)`; 450-600 ms `--adv-ease-in-out` (first load) or 300 ms
`--adv-ease-out` (repeat). Close with `--adv-ease-in` 200-300 ms.

### Shutter slab with tint flash (V3 signature)
The old content hard-cuts to the empty panel color. An angular slab with a chamfered corner rises from the bottom
edge, tilts slightly as if in perspective, flashes toward white mid-move, then fills the window; a full white
frame follows. [rec] cut 1 frame; slab ~450 ms; white frame 1-2 frames, decay ~100 ms.
Build: a `clip-path: polygon(...)` slab animated with `translateY` and a small `skewY`/`rotate` change,
`--adv-ease-out-hard`; a sibling white layer animated `opacity 0 -> 0.9 -> 0` linear inside the move.

### Glyph shatter and diagonal slash wipe (V4 signature)
The logo glyph locks on (corner brackets), flips, scales up past the frame and breaks into white shards; thick
diagonal white bars sweep across to a white field; a status readout types in the corner; dark diagonal bars then
cut the white away to reveal the next scene; shards decay. [rec] lock-on ~400 ms, shatter and slash-in ~600 ms,
white hold with readout ~650 ms, slash-out reveal ~600 ms, debris ~400 ms.
Build: SVG or canvas for the shards; the slashes as 3-5 skewed bars (`skewX(-35deg)`) translated across with
40-80 ms offsets, `--adv-ease-out-hard`; reveal by animating a `clip-path: polygon()` with diagonal edges.

### Power-on "develop" flash
A module appears as a white or light-gray block that fades into its real colors. This is the most reused
gesture across V3, V4 and V5. [rec] V3 and V5 modules flash ~100-130 ms then show content, staggered ~130 ms
(V3) and 130-250 ms (V5). [asset] V4 tint-add white 255 -> 0 over 317-488 ms linear.
Build: a white overlay inside each module, opacity 0.85 -> 0 linear over 120-320 ms, started with the module;
cascade with a constant delay in reading order (code in section 6).

### Full white flash
A 1-2 frame white field marks a hard state boundary (a V3 section change has three full-window white frames,
plus the white slab mid-wipe, in ~3 s). [rec]
Modern rule: keep at most three flashes per second, prefer a partial area, and drop it from repeat navigation
and reduced motion (see `modern-adaptation.md`).

### Light bar sweep
A bright bar crosses a band and leaves it filled (V3 logo band at boot; vertical light bars sweeping a section
window on entry). [rec] ~150-300 ms.
Build: a gradient pseudo-element translated across with `--adv-ease-out`, then the band's fill fades in.

### Ring zoom and logo lock-on
A ring scales from large to small around the logo and locks, or zooms out from it; arcs rotate off; a reticle
crosses it. [rec] V3 ring scale-down ~120 ms; V3 lock-on beats every ~250-300 ms. [asset] V5 pops 2000% -> 100%
in 415 ms ease-out k 4; ring 32% -> 277% in 610 ms.
Build: scale with `--adv-ease-out-hard`; arcs as SVG paths with `stroke-dasharray` and rotation.

### Text reveals
- **Type-on and retype status**: a status line types, then retypes to the next state
  ("INITIALIZING.2ADVANCED" -> "CONSTRUCT.EXPANSION" -> "[ PLS.STANDBY ]"). [rec] ~30-50 ms per character.
- **Tint-in headline**: the old copy hard-cuts out; the headline tints from the panel color to full contrast
  (~200 ms), the tagline follows ~150 ms later. [rec] V3 sub-tabs.
- **Mask-wipe body**: body copy reveals left to right behind a moving mask (~350 ms), then darkens. [rec]
- **Decoder**: characters scramble and settle left to right (V5 "digitize", 439 ms; class `base.Decoder`). [asset]
Build: keep the real text in the DOM for assistive tech and animate an `aria-hidden` copy (section 6).

### Hover and focus states
- **V3 scanline open**: a thin line appears mid-tab and opens vertically into a light block (~130 ms); on
  rollout it collapses to a bottom underline that lingers 150-300 ms while the next tab lights. [rec]
  [asset] Section Nav "Over" 440 ms, "Not Over" 200 ms, "Click" 80 ms.
- **V4 block and split shutter**: a rose block appears within 1-2 frames; on rollout it splits into a top and a
  bottom line that part and fade (~200 ms). [rec] [asset] nav on 171 ms ease-in, off 146 ms linear, masked.
- **V5 glow bloom**: a blue-white glow blooms in ~100 ms ease-out and decays in ~120 ms; the row gets an arrow and
  the next menu column fills. [asset] glow blur 9 -> 15 px, strength to 5, colors #a8d4fe or #ffffff.
- **Sound**: a 20-60 ms tick on hover. [asset]
Build: run the same keyframes on `:hover` and `:focus-visible`; glow with `filter: drop-shadow()` or a
pre-blurred pseudo-element (cheaper).

### Panel slides, masks and layout morphs (V4)
Section panels enter from the right with hard deceleration and leave to the left with a slow start, behind
masks. The MAINFRAME grows over the AUXILIARY PANEL on content-heavy sections, which collapses to its header
with an EXPAND toggle. [asset] enter 244-268 ms ease-out k 3.4-3.7; exit 244 ms ease-in k 3.1; grow 220 ms
ease-out k 2.6. [rec] the morph reads as the window manager rearranging itself.
Build: FLIP technique or the View Transitions API for the morph; panel slides with `--adv-ease-out-hard` in and
`--adv-ease-in` out.

### Ambient idle loops
Every module has its own loop with a long hold and a short show-off, desynchronized from its neighbors: a chrome
coin spins in 3D for ~1.5 s after ~3 s of rest; a logo lockup cycles; a thumbnail morphs into a glyph. Features
rotate every 6-15 s. [rec] V3 module loops ~5-6 s. [asset] V3 loops 2-12 s; V5 thumbnails every 6,000 ms with the
second offset 3,000 ms, news every 15,000 ms.
Build: CSS animations with long `animation-duration` and keyframes that hold for 70-80% of the cycle; different
durations or negative delays per module; pause when off-screen; none under reduced motion.

### Cinematic fade-up
After the V4 slash reveal, the hero scene fades up from near-black over ~4 s while the subject rises. [rec]
Use only on first load of a hero, never on navigation.

## 3. Measured choreographies

### V3 Expansions boot (ENTER -> hero, ~14.5 s) [rec] [asset]
Recording time; ENTER at 0.3 s while the splash was still settling. From a settled splash, ENTER -> hero
measured 14.7 s.

| t (s) | Beat |
| --- | --- |
| 0 | splash hard-cuts out |
| 1.7-2.2 | "2A.LOADING.EXP / + MODULE.STANDBY" and a micro paragraph tint in |
| 2.5 | chrome 2A mark inside bracket arcs |
| 2.7-3.5 | arcs rotate off; a ring zooms out to full size, then contracts and locks around the white logo |
| 3.7 | blank frame |
| 4.0-4.2 | open ring with "TRANSMISSION.STNDBY" rotating through it |
| 4.7-5.2 | the text drops lower and blinks with `+ +` markers |
| 5.7-6.0 | "SEQUENCE.COMPLETE", then a small open ring |
| 6.8-7.3 | frame lines draw down and across; panel outlines; halftone header bands |
| 7.5-8.0 | a white light bar flashes through the logo band and leaves it filled; logo mark appears |
| 8.2-8.7 | "LOAD NAV" placeholder expands outward; wordmark appears |
| 9.4-9.9 | the nav fill grows from the center out; "[ PLS.STANDBY ]" |
| 11.9-12.8 | modules flash on in reading order, ~130 ms apart |
| 13.5-16 | the content window runs the section transition to the hero |

Asset timing: Splash 1,840 ms; Preloader 5,120 ms; Main UI Build 6,640 ms (839 linear keyframes, most common
gap 40 ms); Home build 2,800 ms.

### V3 section change (~3.2 s) [rec]
| t (ms) | Beat |
| --- | --- |
| 0-17 | old content hard-cuts to the empty navy window |
| 50-500 | chamfered slab rises from the bottom, tilting, flashing toward white mid-move |
| 550-600 | full white frame, then decay |
| 650-800 | loader ring scales down from large to small; 2A icon with orbiting arcs |
| 900-1,900 | hairline draws; status types ".MODULE / INITIALIZING.MECHANISM" -> "LOADING.MODULE" -> "MODULE.ENGAGED" |
| 2,000 | white flash; inset frame; faint "2" watermark |
| 2,500 | white flash |
| 2,700-3,200 | photo appears desaturated; grid overlay; angular light panels slide in from the top right |

### V4 Prophecy boot (~16 s from player start) [rec] [asset]
| t (s) | Beat |
| --- | --- |
| 0-1.5 | empty red frame with faint outlines; soft preloader glow |
| 1.5-3.0 | micro readouts; diagonal circuit traces; registration ticks blink; a chamfered bracket draws with an "IV" tag |
| 3.3-4.5 | a glass bubble inflates into a glossy red orb; the 2A logo lands inside; the fill drops to an outline |
| 4.8-5.4 | the logo shrinks to a node; a line tracer drops and runs right carrying small boxes |
| 5.4-7.2 | shell assembles: nav stripes and labels, logo pod, teal FEATURE panel, "LOADING DATA" placeholders, then content; the audio panel flashes white blocks |
| 7.4-8.0 | in MAINFRAME a ring contracts onto the red orb; the glyph flips |
| 8.4-9.1 | the glyph scales up and shatters; white diagonal slashes sweep to a white field |
| 9.3-9.9 | corner readout: katakana "loading sequence", RETRIEVING_MAINLEVEL.CORE.JP, progress bar to 100, COMPLETE |
| 9.9-10.7 | dark diagonal bars cut the white away; shards decay; a white 2A ring spins |
| 11.4-17 | cinematic fade-up to the night city; the pod rises from the water |

Asset timing: main timeline label animationdone at 7,756 ms; rotation 179.5 -> 0.3 degrees in 561 ms ease-out;
most common start gap 73 ms (3 frames). Copy includes "+ SKIP ANIMATION >" and "+ DISENGAGE AUDIO".

### V4 section change (home -> PORTFOLIO, ~6.6 s) [rec]
| t (ms) | Beat |
| --- | --- |
| 0 | "////" marker over the active nav item |
| 250-1,000 | MAINFRAME cuts to a black-red gradient with the outline 2A ring; corner brackets lock on |
| 1,350-2,100 | glyph shatter and slashes to white |
| 2,500-3,600 | MAINFRAME grows over the AUXILIARY PANEL; a white band shows RETRIEVING_SUBLEVEL.ELMNT, a progress line, COMPLETE |
| 4,350-4,750 | the enlarged panel turns dark red with vertical guide lines; floating UI fragments slide into place |
| 5,100-6,600 | modules light up from the top left: pod header, pill buttons, featured thumbnail, copy |

### V5 Attractor boot (ENTER -> interactive, ~11.8 s) [rec] [asset]
| t (s) | Beat |
| --- | --- |
| 0.9 | registration ticks at the corners; micro readout at center |
| 1.7 | thin beam at top center |
| 2.1 | pyramid emblem fades in with a point light on its apex |
| 2.5-7.0 | hold while a loading readout runs (soundtrack starts) |
| 7.2-7.55 | emblem fades out, apex light last |
| 7.7-8.15 | hairlines converge from both edges |
| 8.27 | flare |
| 8.4-9.0 | slit opens into the matte painting |
| 9.0-9.5 | hold on the bare world |
| 9.7-10.6 | grid draws: double rules, column caps, footer fades in low, the ATTRACTOR band, chevrons, "INITIALIZING" blinks twice in all columns, column headers |
| 10.9-11.8 | modules power on left to right, ~130-250 ms apart |

Asset timing: preloader labels loadconfig 2,488 ms, loadtouts 2,780, loadfontlibs 3,049, siteready 3,317 ms.

### V5 section change (home -> Company, ~6.3 s) [rec]
| t (ms) | Beat |
| --- | --- |
| 0 | the UI disappears (1 frame) |
| 0-400 | the painting closes into a slit, then a dot |
| 600-1,700 | tiny readout on black |
| 2,200-2,700 | hairlines converge; flare |
| 2,900-3,350 | the slit opens on the new world (green valley) |
| 4,000-4,500 | header and navigation array redraw in the section hue; grid; "INITIALIZING" blink |
| 5,150-6,300 | modules flash on left to right, ~230 ms apart |

The URL becomes `#company` and the title "2Advanced Studios - company".

## 4. Sound sync

- V4 intro cues [asset], ms from start: 171 (0.58 s blip), 512 (5.64 s ambience loop), 1,024, 1,537 (three layers),
  1,659, 1,854, 3,317, 4,683. A 0.02 s tick is started 21 times by nav sprites. Four selectable soundtrack loops.
- V5 [asset]: four 0.05 s ticks at 195, 317, 439 and 561 ms (122 ms apart) during the preloader pops; a 4.06 s
  sweep at 927 ms; a 9.14 s stereo soundtrack loop; 0.04 s hover ticks; volume ramps every 10 ms.
- V3 reboot [asset]: 14.1 s soundtrack loop plus 17 Rive audio events (transition 0.93 s, sectionshapes2 1.05 s,
  scanner 0.55, zoom 0.30, quikzoom 0.22, jitter 0.63, buttonhit 0.56, highblip 0.19, interference 0.08 ...).
- Pattern [inf]: one tick per visual pop, a sweep under each long move, the loop under everything; cue lengths
  match the beat they decorate.

## 5. Compression for modern use

| Moment | 2Advanced original | First visit (this session) | Repeat | Reduced motion |
| --- | --- | --- | --- | --- |
| Boot | 11.8-16 s | 2.5-4 s, skippable, content interactive by ~1 s | 300-700 ms signature (slit or flash) | none, or a 150 ms fade |
| Section change | 3.2-6.6 s | 600-900 ms | 300-500 ms | crossfade <= 150 ms |
| Module power-on cascade | 1-2 s | 400-700 ms total | 200-400 ms | instant |
| Hover | 100-440 ms | same | same | color change only |
| Idle loops | always on | on, paused off-screen | on | off |

Keep the beat structure when compressing: shorten holds and blank frames first, then shorten the stagger, and
keep the hard ease-out shape.

## 6. Implementation sketches

Module power-on cascade (WAAPI):

```js
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
export function powerOn(modules, { stagger = 130, flash = 240 } = {}) {
  modules.forEach((el, i) => {
    const delay = reduce ? 0 : i * stagger;
    el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1, delay, fill: "both" });
    if (reduce) return;
    const veil = el.querySelector(".veil"); // absolutely positioned white layer, aria-hidden
    veil.animate([{ opacity: 0.85 }, { opacity: 0 }], { duration: flash, delay, easing: "linear", fill: "both" });
  });
}
```

Slit transition for a world image with the View Transitions API (fallback: instant swap):

```css
.world { view-transition-name: world; }
@keyframes adv-slit-close { to { clip-path: inset(50% 0 50% 0); } }
@keyframes adv-slit-open { from { clip-path: inset(50% 0 50% 0); } to { clip-path: inset(0); } }
@media (prefers-reduced-motion: no-preference) {
  ::view-transition-old(world) { animation: adv-slit-close 220ms var(--adv-ease-in) both; }
  ::view-transition-new(world) { animation: adv-slit-open 380ms var(--adv-ease-out) 80ms both; }
}
/* Reduced motion keeps the browser's default short crossfade. */
```

```js
function go(render) {
  if (!document.startViewTransition) return render();
  document.startViewTransition(render);
}
```

Decoder headline with accessible text:

```html
<h2 class="decode"><span class="visually-hidden">About us</span><span aria-hidden="true" data-decode>About us</span></h2>
```

```js
export function decode(node, duration = 440) {
  const final = node.textContent;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/+#";
  const start = performance.now();
  const frame = (now) => {
    const p = Math.min(1, (now - start) / duration);
    const settled = Math.floor(p * final.length);
    node.textContent = final.slice(0, settled) +
      [...final.slice(settled)].map((c) => (c === " " ? " " : glyphs[(Math.random() * glyphs.length) | 0])).join("");
    if (p < 1) requestAnimationFrame(frame); else node.textContent = final;
  };
  requestAnimationFrame(frame);
}
```

Skippable boot: run the boot as WAAPI animations started from one function, store `sessionStorage` flag after
it ends, and on Skip or Escape call `finish()` on every animation whose end time is finite
(`a.effect.getComputedTiming().endTime !== Infinity`; `finish()` throws on infinite animations).

## 7. Verifying motion

Score first, then measure. Compare the measured onset, duration, stagger and easing shape with the score.

**Canvas, WebGL, Rive or Ruffle content.** Record the canvas in the page:

```js
const stream = canvas.captureStream(60);
const rec = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9", videoBitsPerSecond: 6e6 });
const chunks = []; rec.ondataavailable = (e) => e.data.size && chunks.push(e.data); rec.start(200);
// trigger the interaction, wait, then: rec.stop(); new Blob(chunks, { type: "video/webm" })
```

Return the blob as base64 from a page script, save it as `.webm`, and run:

```bash
python3 scripts/motion.py rec.webm name --crop W:H:X:Y --fps 30 --from 0 --to 6 --sheet 20 --tile 4x5 --width 420
```

It prints the motion window, active segments, an energy curve, the share of the window at which the frame
reaches 10/25/50/75/90% of its final state (an easing fingerprint), and writes a labeled contact sheet to
`sheets/name.jpg` next to the video. Needs ffmpeg and ImageMagick. Small periodic full-frame energy spikes
(~every 2.5 s) are encoder keyframes, not design. `drawImage()` of a WebGL canvas can come back blank, so record
with `captureStream()` instead. Some players ignore synthetic pointer events for clicks; use a real click on a
transparent `pointer-events: none` overlay positioned over the target when that happens.

**DOM, CSS and WAAPI.** Start all animations from one script, then pause and seek them
(`document.getAnimations()`, `a.pause()`, `a.currentTime = t`) and screenshot at fixed steps, or set
`a.playbackRate = 0.1` and screenshot while it plays.

**Also check:** the reduced-motion path, the keyboard path (focus triggers the same gestures), the repeat-visit
path, flash count per second, and that content is reachable before the ornament finishes.

## 8. Contact sheet index (`assets/motion/`)

| File | Shows |
| --- | --- |
| `v3-m04a-preamble.jpg` | V3 boot preamble: status text, logo lock-on, rotating ring text, SEQUENCE.COMPLETE |
| `v3-m04b-framebuild.jpg` | V3 wireframe build, typed status, light-bar fill, center-out nav fill |
| `v3-m04c-modules-online.jpg` | V3 modules power on in reading order, then the first section transition |
| `v3-m01-to-accolades.jpg` | V3 section change: hard cut, slab, white flashes, loader, status, reveal |
| `v3-m02-nav-hover.jpg` | V3 nav hover: scanline open, collapsing underline afterglow |
| `v3-m06-subtab.jpg` | V3 sub-tab change: tint-in headline, staggered tagline, mask-wipe body |
| `v4-m02a-build.jpg` | V4 boot: traces, bracket outline, orb, line tracer, shell assembly |
| `v4-m02b-slash.jpg` | V4 MAINFRAME: ring lock, glyph shatter, slashes, readout, slash-out reveal |
| `v4-m03-nav-hover.jpg` | V4 nav hover: instant block, split-shutter rollout |
| `v4-m04-to-portfolio.jpg` | V4 section change with the MAINFRAME layout morph |
| `v5-m01b-slit.jpg` | V5 converging hairlines, flare, slit opening on the world (60 fps) |
| `v5-m01c-grid.jpg` | V5 grid draw, INITIALIZING blink, module flashes left to right |
| `v5-m05-to-company.jpg` | V5 section change: slit close, readout, slit open on a new hue world |
