# V3 Expansions (2001; rebuilt in Rive and React, 2024)

URL: https://v3.2advanced.com/ (redirects to `/v3expansionsreboot/`). Labels as in `motion.md`; **[src]** = public
source listed in `sources.md`.

## Identity
- The 2001 Flash site that the FWA named "Most Influential Flash Site of the Decade" [src]. Creative direction and
  design by Eric Jordan [src].
- The 2024 reboot re-implements it in Rive (animation by Eric Jordan) and React (development by Tony Novak) in
  two months, aiming to map "all of the animations of the iconic 2001 V3 Website down to the keyframe" [src]. The
  motion measured here is therefore close to the original; the content, partners and some sections are new.
- Theme: architecture and travel, "NEW.METHODS.OF.TRANSPORTATION"; tagline "solace in technology. belief in the
  future." [rec]

## Information architecture [rec]
- HTML-era splash: "2ADVANCED STUDIOS . PRESENTS", a dotted rule, "V3.EXPANSIONS [CIRCA 2001]", "ENTER 2ADVANCED
  STUDIOS" with a lead-in line and a mini progress-bar glyph.
- Persistent shell: banner strip, logo band, tab nav (PROFILE, EQUIPMENT, SUBCULTURE, ACCOLADES, EXPLORATORY,
  CONTACT) with a version tab "-> 2A.V3_2024 // EXPANSIONS", one content window, a utility bar
  (SCROLL.EXTENDED.CONTENT / AMBIENCE.MUTE), two rows of three modules (F FEATURED.PARTNER, S SUB.DATA,
  U UPDATES; MAILING LIST, SUPPORT 2A, FOLLOW 2A), footer.
- Section template: a photo on one side, a spaced label bar ("P R O F I L E") with angled caps, sub-tabs on a
  slanted strip, "+ HEADLINE." then "lowercase tagline.", dense caps body, `[ RETURN TO MAIN ]`.
- Lists: framed rows with scroll triangles and a `...` more indicator; dates as `2024.10.06 // TITLE`.

## Visual signature
- Monochrome steel blue everywhere (palette in `visual-system.md`); duotone architecture from below; grid
  overlays; HUD glyph clusters; beveled metal tab strips; chamfered corners; halftone header bands.
- Type: Berthold Akzidenz Grotesk in seven weights embedded in the Rive file [asset]: extended for the wordmark,
  condensed bold for tabs and module headers, small bold caps for body.
- Light without filters: Rive had no blurs, glows or gradient clipping masks when the reboot was built [src], and
  the file animates only opacity, color and transforms [asset]. The flashes and glows are white fills and opacity
  ramps. The look survives without real blur, which makes it cheap to rebuild in CSS.
- Key frames: `assets/taste-board.jpg` row 1.

## Motion signature
- Boot ~14.5 s: status text -> logo lock-on in rings -> rotating "TRANSMISSION.STNDBY" -> SEQUENCE.COMPLETE ->
  wireframe build with typed status -> light-bar fills -> center-out nav fill -> modules flash on in reading
  order (~130 ms apart). Tables in `motion.md` section 3.
- Section change ~3.2 s: hard cut -> chamfered slab rises with a white flash -> white frame -> loader ring ->
  typed status (LOADING.MODULE -> MODULE.ENGAGED) -> white flashes -> photo, grid overlay, sliding angular panels.
- Hover: scanline opens into a block; rollout leaves a lingering underline.
- Sub-tabs: hard cut out, headline tint-in, tagline +150 ms, body mask-wipe left to right.
- Idle: each module has its own loop (chrome coin spin, lockup cycle, glyph morph) with long holds.
- Asset facts [asset]: Rive at 25 fps; 5,197 linear keyframes vs 124 cubic; state machine transitions all 0 ms
  (blending baked into the timelines); Preloader 5,120 ms; Main UI Build 6,640 ms; section builds 2.8-5.5 s;
  nav hover 440 ms in, 200 ms out, click 80 ms; flicker 0.6 <-> 1.0 at 40 ms steps.
- Sheets: `assets/motion/v3-*.jpg`.

## How the reboot works [asset]
- Vite + React SPA; `@rive-app/canvas-advanced@2.21.2` (canvas 2D renderer) with one runtime instance per
  canvas; seven stacked full-viewport canvases (home stage, mail overlay, three web-view modals, photo, video).
- `mainstage.riv` 5.85 MB: 73 artboards, 281 embedded PNGs, 17 WAV sound events, 7 Akzidenz weights; the Main
  Stage state machine has 13 inputs (section triggers, `Enter`, sub-section numbers) and 64 Rive events that call
  back into React (`gotoDiscord`, `eqClothingBtnNext`, ...).
- Each canvas runs a rAF loop, advances artboard and state machine, and draws with `Fit.contain` centered on
  `innerWidth x innerHeight`; DOM pointer events are mapped into artboard space.
- Product and gallery images are injected at runtime into empty Rive image assets; the paths are hard-coded to
  `/assets/...` and 404 in production, so carousels show empty frames [asset] [rec].
- Soundtrack: a 14.1 s WAV loop in an `<audio>` element started by a Rive event; mute via AMBIENCE.MUTE.
- A crawlable static summary, JSON-LD and `llms.txt` ship with the app.

## Borrow
- The boot narrative: standby -> handshake -> wireframe -> modules online.
- The status vocabulary and dot-joined machine naming.
- The power-on flash cascade in reading order.
- The persistent shell with one swapping content window and a utility bar that holds sound control.
- Idle loops with long holds, desynchronized per module.

## Fix
- Canvas-only UI: render nav, copy and forms in the DOM; keep Rive for the motion layer.
- Scale-to-fit artboard: reflow instead; micro text becomes unreadable when scaled.
- 14.5 s boot and 3.2 s section changes: compress per `motion.md` section 5.
- No URLs per section; full white frames on every section change; WAV audio; one 5.85 MB motion file.
