# Visual system

Labels: **[rec]** sampled from recorded frames (ImageMagick quantize), **[asset]** authored values in the SWF/Rive
files or site code, **[inf]** inference. Section 2 translates each palette into modern tokens.

## 1. Palettes

### V3 Expansions: monochrome steel blue
| Role | Hex | Source |
| --- | --- | --- |
| Deep navy (page, dark frames) | #16243D, #17253E, #20273F | [rec] [asset] |
| Navy panel | #25334E, #2A3753, #2B3853 | [rec] [asset] |
| Slate | #364661, #4B5971 | [rec] |
| Steel | #657289, #696F86 | [rec] [asset] |
| Shell blue-gray (logo band, tabs) | #7989A4, #798AA7 | [rec] [asset] |
| Light steel | #98A1AF, #9BA4B2 | [rec] [asset] |
| Pale panel | #B9C4D5, #C0C9D9, #C2C7CD | [rec] [asset] |
| Paper | #D8DBE2, #E7F2FE, #F1F2F2 | [rec] [asset] |
| Flash and active text | #FFFFFF | [rec] |
| Rare accent | #468AAE (UI), #7C96CF | [asset] [rec] |

Imagery is blue duotone; saturated color appears only in partner logos.

### V4 Prophecy: oxblood with teal and one hot cyan
| Role | Hex | Source |
| --- | --- | --- |
| HTML shell and stage | #4A100F, #5E171F | [asset] |
| Oxblood panels | #561A24, #6E1C24, #802833, gradient #984151 -> #69232D, #701D25 -> #4A100F | [rec] [asset] |
| Near-black | #1A1E1E, #28171A, #3A1014 | [rec] [asset] |
| Mauve and rose | #6B3A43, #8F575D, #BA5F6F, #C13D4A (stroke) | [rec] [asset] |
| Pale rose (wrapper accent, links, focus) | #D8A0A0 | [asset] |
| Deep teal | #013D3E, #12433C | [asset] [rec] |
| Teal | #267171, #1D5D57, #519C98 | [asset] [rec] |
| Sea and pale teal | #579A90, #649D95, #A0C5C9, #C5DDDE | [asset] [rec] |
| Hot cyan accent (glows, visualizer, hero light) | #14BCAD, #6ACAC6 | [rec] [asset] |
| Text | #FFFFFF, #F3ECE8, #CBB4B5, #B1E3E0 | [asset] |

### V5 Attractor: near-black, electric blue, one hue per world
| Role | Hex | Source |
| --- | --- | --- |
| Base | #030305, #04070E, #05080D | [asset] [rec] |
| Navy and panel | #0D1932, #1A3256, #1D324A | [asset] [rec] |
| Steel navy | #294B6E, #34466C | [rec] [asset] |
| Blue | #1D9AD3, #0D95D2, #256193 | [asset] [rec] |
| Glow and highlights | #A8D4FE, #65B2FF, #80CCEA, #4DB3CE | [asset] [rec] |
| Text | #FFFFFF, #666666 (muted) | [asset] |

Section hues from the scrollbar themes in `v5util.js` (face / arrow / highlight) [asset]:

| Index | Hue | Face | Arrow | Highlight |
| --- | --- | --- | --- | --- |
| 0 | blue (home) | #0D1932 | #BFD8F1 | #34466C |
| 1 | green (company) | #0D3311 | #BFF2C4 | #336B39 |
| 2 | amber (portfolio) | #33280D | #F2E3BF | #6B5A33 |
| 3 | red | #330D0D | #F2BFBF | #6B3333 |
| 4 | magenta | #330D24 | #F2BFDF | #6B3356 |
| 5 | slate | #212B31 | #FFFFFF | #4A5D68 |

The navigation bullets use the same coding: Company green, Portfolio yellow, Services orange-red, Case Studies
magenta, Recognition white [rec]. In the green world the UI text reads about #3DAE51 on #020A02 panels [rec].

### 2Advanced today (2advanced.com and microsites, for reference)
Base #0A0A0B, text white at 92%, accent cyan family rgba(0, 200, 235, x) with CTA fill 12% and border 50%, dot
grid 1 px every 28 px, aurora gradient bands, square corners. Kesey Signal: #010F53 / #000437 gradient, signal
#6B4FE8 and #4A7BFF, bone #F2F4F8, alert #FF3B6B [asset]. Their low-alpha 9-11 px labels fail contrast; do not
copy that part.

## 2. Token presets

Starting points for a modern build. Rename to the product's fiction.

```css
/* V3: steel shell */
.theme-expansions {
  --bg: #16243d; --surface: #25334e; --surface-2: #364661; --line: #7989a4;
  --panel: #c0c9d9; --paper: #e7f2fe; --ink: #17253e; --text: #e7f2fe;
  --muted: #98a1af; --accent: #7c96cf; --flash: #ffffff;
}
/* V4: oxblood operating system */
.theme-prophecy {
  --bg: #4a100f; --surface: #561a24; --surface-2: #802833; --line: #ba5f6f;
  --teal: #267171; --teal-pale: #a0c5c9; --accent: #14bcad; --text: #f3ece8;
  --muted: #cbb4b5; --focus: #d8a0a0; --flash: #ffffff;
}
/* V5: night world; swap the hue per section */
.theme-attractor {
  --bg: #05080d; --surface: #0d1932; --surface-2: #1d324a; --line: #34466c;
  --accent: #1d9ad3; --glow: #a8d4fe; --text: #ffffff; --muted: #8fa9c2; --flash: #ffffff;
}
.theme-attractor[data-world="green"] { --surface: #0d3311; --line: #336b39; --accent: #3dae51; --glow: #bff2c4; }
.theme-attractor[data-world="amber"] { --surface: #33280d; --line: #6b5a33; --accent: #e0b040; --glow: #f2e3bf; }
```
`--muted` in the V5 preset and the amber `--accent` are new values chosen for contrast, not sampled. Computed
WCAG ratios for the preset text pairs on their surfaces run from 4.9:1 (green accent on #0d3311) to 14:1; check
every new pair at 4.5:1 against the real background, including art behind translucent panels.

## 3. Typography

| Register | V3 | V4 | V5 | Free substitutes |
| --- | --- | --- | --- | --- |
| Brand / display (wide extended) | Berthold Akzidenz Grotesk Bold Extended, wordmark letter-spaced | Eurose Wide Heavy, Interstate Black | custom "Attractor" techno face, DIN | Michroma (used on 2advanced.com/about), Eurostile (licensed) |
| Nav and panel titles (condensed bold caps) | Akzidenz Grotesk Extra Bold Condensed | Akzidenz Grotesk BE Cn / XBdCn, Interstate Bold Condensed | DIN Medium 14 px (tree nav) | Barlow Condensed, Archivo Narrow, Roboto Condensed |
| Micro UI | small bold caps; micro text 5-8 px | pixel fonts hooge 05_55, uni 05_53, standard 07_53 at 8 px | Verdana 9-10 px pixel-snapped, FFF Simplicity, 04b_08 | Silkscreen (pixel), JetBrains Mono (status), Inter |
| Headline voice | caps headline + lowercase tagline | mixed weight "Fight" / "for the Future." | DIN Regular 25 px with the decoder effect | |

Sources: [asset] font tags in the SWFs and Rive files.

Rules:
- Spaced caps for section labels: wide tracking (0.5-1em) or literal spaces ("P R O F I L E").
- Nav and labels in caps with 0.1-0.3em tracking; taglines lowercase, regular weight.
- Pixel fonts only at their native size or integer multiples, and only for short labels.
- Real copy: 16 px or more in a readable face. The originals used 8-10 px pixel type for copy; do not.

## 4. Layout and anatomy

**Stages** [asset]: V3 artboard 1280x1046 (content window 1277x384); V4 970x655 (section area 712x400); V5
1600x1200 stage with a 975 px UI column and 1600x659 mattes. All fixed. Translate to a fluid grid.

**V3 shell** [rec]: top banner strip (photo + micro text) / logo band / tab nav with a version tab
("-> 2A.V3_2024 // EXPANSIONS") / one content window that swaps modules / utility bar (SCROLL.EXTENDED.CONTENT
left, AMBIENCE.MUTE right) / two rows of three modules with letter badges (F, S, U) / footer with `//`
separators. Sections mirror a big photo on one side and a spaced label bar with angled end caps on the other.

**V4 operating system** [rec]: every region is a trademarked panel. Panel header: `>>` icon button, bold first
word plus lighter second word (MAIN|FRAME, FEATURE|SYSTEM), one line of micro text, `- - -` window controls at the
right. Panels collapse and expand; the content panel grows over its neighbor on heavy sections. Section header
pod: thumbnail + name + `.DATABANK` subtitle + glyph tile. Sub-navigation: pill buttons with a red LED.

**V5 hairline grid** [rec]: four equal columns, each with a thin top cap; a header with text links left, logo
center, sound control right; a translucent navigation drawer that spans the columns (primary / secondary /
tertiary / auxiliary destinations); a utility row; a hatched band with the release mark; four modules; a credit
footer. The art fills the viewport behind the column.

**Buttons and controls**:
- V3: beveled metal tabs (1 px light top edge, dark bottom edge), slanted strips, chamfered corners, bracket
  links `[ RETURN TO MAIN ]`, a mini progress-bar glyph before CTAs.
- V4: glossy red orb buttons, pill buttons with LED indicators, dropdowns with a cyan arrow, scrollbars styled
  into the panel.
- V5: bar bullets (a 3x9 px tick) before labels, `^` and `>` chevrons, flat dark buttons.
- Modern 2Advanced CTA [asset]: square corners, 1 px cyan border at 50%, cyan fill at 12%, uppercase label with
  0.12em tracking, CSS chevron.

## 5. Texture and light

```css
.dot-grid { background-image: radial-gradient(circle at center, rgb(255 255 255 / .32) 1px, transparent 1px); background-size: 28px 28px; }
.hatch { background-image: repeating-linear-gradient(-45deg, rgb(255 255 255 / .06) 0 2px, transparent 2px 6px); }
.halftone { background-image: radial-gradient(rgb(255 255 255 / .35) 1px, transparent 1.2px); background-size: 4px 4px; }
.scanlines { background-image: repeating-linear-gradient(to bottom, rgb(0 0 0 / .18) 0 1px, transparent 1px 3px); }
.grid-overlay { background-image: linear-gradient(rgb(255 255 255 / .06) 1px, transparent 1px), linear-gradient(90deg, rgb(255 255 255 / .06) 1px, transparent 1px); background-size: 16px 16px; }
.glow { filter: drop-shadow(0 0 6px rgb(168 212 254 / .8)); }
```
- Glows: V5 Flash 8 glow, blur 6-15 px, strength 1.5-5, colors #A8D4FE or #FFFFFF, rich on hover, none at rest
  [asset]. V4 and V3 fake light with tint, white flashes and gradients (no filters) [asset].
- Bevels and gloss belong to V3/V4 chrome; V5 is flat hairlines. Mix carefully.
- Overlays on photography: fine grid, HUD glyph clusters, concentric rings, small arrow groups.

## 6. Imagery direction

- V3: architecture shot from below (overpasses, towers, tunnels with motion blur), duotone steel blue, a grid
  overlay, HUD clusters; a human figure with a white visor touching a glowing wall. Theme: "new methods of
  transportation".
- V4: glossy 3D renders (white and red pods, spherical drones), a teal night city over water, a 3D Tokyo built
  for the "Prophecy" reel; katakana as decorative status text.
- V5: digital matte paintings, one world per section (night lake with a stepped pyramid emitting a beam; green
  valley with a white pyramid and a waterfall), a lone figure for scale, light beams, moons. The art carries the
  detail; the UI stays quiet.
- Make original art for the product. Tint it to the palette and leave calm areas where the UI sits.

## 7. Glyph kit and copy voice

Glyphs: `+` markers, `//` separators, `[ ]` brackets, `>>` and `->` arrows, `^` chevrons, `- - -` window
controls, letter badges, LED dots, numbered map markers, `(TM)` on system names, `. . .` animated ellipses.

Naming patterns [rec] [asset]:
- Dot-joined machine words: SUB.CONTENT, MODULE.STANDBY, SEQUENCE.COMPLETE, SCROLL.EXTENDED.CONTENT,
  AMBIENCE.MUTE, NEW.METHODS.OF.TRANSPORTATION.
- Underscore codes and numbers: PROPHECY.DATACORE-04028_AWAKE, SPECIAL.DESIGN.FORCES-00632_ACTIVE, 04___
  2ADVANCED SYSTEM BIOS V.IV, RETRIEVING_SUBLEVEL.ELMNT.
- Status sequences: TRANSMISSION.STNDBY -> LOADING.MODULE -> MODULE.ENGAGED; STANDBY: INITIALIZING -> LOADING ->
  COMPLETE; [ PLS.STANDBY ].
- Places and systems: MAINFRAME, FEATURE SYSTEM, AUXILIARY PANEL, SUB SYSTEM, Navigation Array, Secondary /
  Tertiary / Auxiliary Destinations, Soundscape, STUDIO.DATABANK, WORK.SHOWCASE.
- Dates: 2024.10.06 // TITLE (V3), 03.10.04 (V4), 09.01.2009 (V5).
- Taglines, lowercase or sentence case and sincere: "solace in technology. belief in the future.", "Fight for
  the Future.", "And so it begins...", "Progressive Design Technology".
- Today's voice keeps the transmission metaphor: "The channel went dark a long time ago. Years of static. Then a
  carrier wave. Same source, different frequency." / "RECEIVE THE SIGNAL".
Keep functional labels plain enough to understand ("Contact", "Portfolio"); put the machine voice in system
names, status lines and decoration.
