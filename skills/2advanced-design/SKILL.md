---
name: 2advanced-design
description: Design, animate, and critique interfaces in the taste of 2Advanced Studios' classic sites (V3 Expansions 2001, V4 Prophecy 2003-04, V5 Attractor 2006) - cinematic boot sequences, choreographed transitions, HUD/FUI chrome, machine-voice labels, world-building art, and sound-aware interaction - rebuilt for modern UI requirements (semantic DOM, accessibility, responsive layout, performance, reduced motion, deep links). Use when the user asks for a 2Advanced-style, futuristic, sci-fi, FUI/HUD, cinematic, or Flash-era-inspired interface, landing page, loader, transition, motion system, or design review, or mentions 2Advanced, Eric Jordan, Expansions, Prophecy, or Attractor.
---

# 2Advanced design

2Advanced built websites that behave like machines from a film. The interface boots, names its own systems,
loads modules with visible effort, and moves with short, hard-eased beats that add up to long, rhythmic
sequences. Motion is the core of the taste: nothing simply appears. It is drawn, scanned, flashed, decoded or
revealed through a slit, always in the same grammar for one site.

This skill carries that taste into modern UI work. The motion and the world-building stay. The things that aged
badly go: fixed stages, canvas-only text, unskippable intros, tiny low-contrast type, sound that ambushes users,
and state that has no URL.

## Reference map

Load only what the task needs. All paths are relative to this skill directory.

| Need | Read |
| --- | --- |
| Any motion work: loaders, intros, transitions, hovers, idle loops, sound sync | `references/motion.md` (start here; it is the core) |
| Color, type, layout, panel anatomy, texture, imagery, copy voice, tokens | `references/visual-system.md` |
| Making it accessible, responsive, fast, addressable; code patterns | `references/modern-adaptation.md` |
| One version in depth (what it is, how it works, what to borrow, what to fix) | `references/v3-expansions.md`, `references/v4-prophecy.md`, `references/v5-attractor.md` |
| History, quotes, sources, evidence labels | `references/sources.md` |
| Visual anchor: nine key frames of the three sites | `assets/taste-board.jpg` |
| Frame-by-frame contact sheets of the measured animations | `assets/motion/*.jpg` (index in `references/motion.md`) |
| Measuring a recording (energy curve, timing, contact sheet) | `scripts/motion.py` (usage in `references/motion.md`) |

## The taste, as rules

1. **The interface is a machine with a story.** Name every region as a system (MAINFRAME, FEATURE SYSTEM,
   SUB.DATA, Navigation Array, Auxiliary Destinations). Give the product a fiction: a transmission, a datacore, a
   world. Each release is an installment, so the version name and number are part of the brand.
2. **Boot, don't load.** First contact is a power-on sequence: registration marks, a status readout, a logo
   lock-on, the frame drawn as wireframe, then fills, then labels, then content. Loading states narrate in
   machine voice (LOADING.MODULE -> MODULE.ENGAGED) and show real progress.
3. **One transition grammar per product.** Pick one metaphor and reuse it for the intro and every state change:
   a shutter slab plus white flash (V3), a glyph shatter plus diagonal slash wipe (V4), or a slit that closes and
   opens on a new world (V5). Consistency makes the motion feel engineered, not decorative.
4. **Short beats, long sequences.** Single tweens run about 150-250 ms. Cascades step 25-130 ms apart. Rhythm
   comes from stacking beats, with blank or flickered frames as punctuation. See the house constants in
   `references/motion.md`.
5. **Hard ease-out in, ease-in out, linear light.** Entrances decelerate hard (cubic to quart, sometimes quint).
   Exits accelerate. Fades, tints and flashes are linear. No springs and no bounce; overshoot is rare and small.
6. **Light marks state changes.** White flashes, light bars sweeping across panels, a flare where two hairlines
   meet, glows that bloom on hover, a point light on the logo apex. A module comes online with a white "develop"
   flash that fades into its real colors.
7. **Build in reading order.** Frame, then hierarchy, then modules left to right and top to bottom, each with the
   same power-on gesture and a constant stagger.
8. **Detail is texture around a clear hierarchy.** Micro text, crosshairs, registration ticks, halftone dots,
   hatch stripes, `+` markers, `[ BRACKET LINKS ]`, `//` separators, tiny progress glyphs, trademark marks on panel
   names. The primary hierarchy (one hero, one nav, one content window) stays obvious. In V5 the detail moved into
   the art and the UI became hairlines: that restraint is also part of the taste.
9. **A restricted palette per release, one hot accent.** V3: monochrome steel blue. V4: oxblood with teal and one
   hot cyan. V5: near-black with electric blue, and one hue per section world. Imagery is tinted to the palette.
10. **Type in three registers.** A wide extended face for the brand, condensed bold caps for navigation and
    panel titles, a pixel or small sans for micro UI. Spaced caps for section labels ("P R O F I L E"), lowercase
    taglines for contrast ("solace in technology. belief in the future.").
11. **Sound is authored with the motion.** A soundtrack loop the user controls, short ticks on hover (20-60 ms),
    sweeps on transitions, a visible mute or volume control at all times.
12. **Give users artifacts and control.** Soundtrack choice, skins or themes, wallpapers, an archive of past
    versions, saved preferences, deep links. The site is a product with a history.

## Workflow

1. **Choose the lens.** Pick V3, V4 or V5 as the dominant reference, or name an explicit blend (for example "V5
   layout and slit grammar, V4 module power-on"). Read that version's reference.
2. **Write the fiction before the layout.** Name the product's systems, its status vocabulary, its transmission
   or world, and one tagline. Draft the labels with the patterns in `references/visual-system.md`.
3. **Lay out the shell.** A persistent frame (header, nav, utility bar, content window, module grid) on a real
   responsive grid. Decide which regions are art, which are chrome, which are content.
4. **Score the motion before coding it.** Write a timeline table: beat, element, property, duration, easing,
   delay, sound cue. Cover first load, repeat load, section change, hover/focus, module power-on, text reveal,
   idle loops, loading and error states. Use the measured values in `references/motion.md` as defaults.
5. **Apply the modern contract below** while implementing, not after.
6. **Verify the motion.** Record or step through the animation and compare timing with the score. Use the
   recording and stepping methods in `references/motion.md`. Check the reduced-motion path and the keyboard
   path separately.

## Modern contract

These rules win over fidelity to the originals.

- Real content is semantic DOM. Canvas, WebGL, Rive or video carry the decorative and motion layers only.
  Decorative micro text is `aria-hidden`.
- The shell is usable within about one second. The full boot sequence plays once per session, can be skipped
  with one visible control and with Escape, and never blocks navigation. Returning visitors get a short version
  (300-700 ms).
- Repeat section changes take 300-700 ms. Keep the signature (slit, slash, shutter) but compress it; stream
  content instead of blanking the whole UI.
- `prefers-reduced-motion: reduce` replaces sweeps, slits, flicker and flashes with short crossfades or instant
  changes. Nothing loops.
- No more than three flashes per second (WCAG 2.3.1), and keep large full-field white flashes out of repeat
  navigation.
- Body copy at 16 px or more, dense UI at 14 px or more, contrast 4.5:1 or better. Pixel and micro fonts are
  decoration or short labels only.
- The layout reflows (for example 4 -> 2 -> 1 columns). Do not scale a fixed artboard to fit the viewport.
- Every section and selection has a URL; Back and Forward work; titles update.
- Sound is off until the user opts in, or muted autoplay with a visible toggle. The choice persists.
- Hover effects also run on `:focus-visible`. Menus open on click or focus, not on hover alone. Touch targets
  are at least 44 px.
- Loading states report real progress, and failures say so in the product's voice ("SIGNAL LOST // RETRY").
  Placeholder states never ship as content.
- Animate transform and opacity first. Treat clip-path, filter and glow as budgeted effects on few layers.

`references/modern-adaptation.md` has the patterns and code for each rule.

## Critique rubric

When reviewing a design or build against this taste, score each line pass, partial or fail, with the evidence.

| Area | The 2Advanced bar | Modern bar |
| --- | --- | --- |
| Fiction | Systems are named; status copy narrates; one tagline | Labels still tell users what things do |
| Motion grammar | One metaphor reused for intro and transitions | Fast repeat path; interruptible |
| Timing | Beats ~150-250 ms, staggers 25-130 ms, hard ease-out entrances, linear light | Reduced-motion path exists and is tested |
| Light | Flashes, light bars, glows mark state changes | Flash rate and area within WCAG 2.3.1 |
| Build order | Frame -> hierarchy -> modules in reading order | Content reachable before ornament finishes |
| Palette | Restricted, tinted imagery, one hot accent | Text contrast 4.5:1 |
| Type | Three registers; spaced caps; lowercase taglines | Readable sizes; real text in DOM |
| Detail | Dense micro texture around a clear hierarchy | Decorative layer hidden from assistive tech |
| Sound | Authored cues and a loop the user controls | Opt-in, persistent mute |
| Structure | Persistent shell, module grid, utility bar | Responsive reflow, URLs per state, focus order |

## Anti-patterns

- Neon-cyan "cyberpunk" with random glitches and no grammar. 2Advanced is disciplined, not noisy.
- Easing everything with the same `ease-in-out`, or springs and bounces.
- Motion that only fades. The signature gestures are wipes, slits, light bars, decoding text and power-on flashes.
- Micro text as the only carrier of meaning.
- A long intro on every visit, or a section change that blanks the screen for seconds.
- Copying 2Advanced's logo, marks, matte paintings or copy. Borrow the principles and the grammar; create the
  fiction, marks and art for the product at hand.

## Evidence

The specs in this skill come from a first-hand study on 2026-10-21: browser navigation of the three sites,
MediaRecorder recordings of the animations measured frame by frame, a static teardown of the SWF, Rive and
wrapper assets, and a sourced research brief. `references/sources.md` lists the sources, labels claims by
provenance, and points to the local study folder if it still exists.
