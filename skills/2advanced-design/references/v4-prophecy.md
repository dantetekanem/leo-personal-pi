# V4 Prophecy (Flash, 2003-2004)

URL: https://v4prophecy.2advanced.com/ (2026 Ruffle archive of `flashindex.swf` inside the original HTML table
shell). Labels as in `motion.md`; **[src]** = public source listed in `sources.md`.

## Identity
- Date: the movie's footer reads "COPYRIGHT (C) 2003 2ADVANCED STUDIOS, LLC." and its news items are dated
  02.10.04 and 03.10.04 [rec]; the archive wrapper says 2004; Summit International Gold Award 2004 [src]. Treat it
  as launched in 2003 and updated into 2004.
- Fiction: "PROPHECY", a datacore "SENT BACK IN TIME TO HELP FORGE A NEW PATH" [asset]; the site celebrated a
  cinematic reel, "Prophecy", for which the studio built a 3D model of Tokyo [rec]. Copy voice: "Fight for the
  Future.", "And so it begins..." [rec].
- Soundtracks by Elijah Shepard: "a handful of soundtracks for the site users could switch between and loop,
  meant to set a mood which matched the visuals" [src].

## Information architecture [rec] [asset]
- An operating system of trademarked panels: INITSEQ.2A, GLOBAL AMBIENCE (music player), GLOBAL NAVIGATOR,
  MAINFRAME (content), FEATURE SYSTEM (news), AUXILIARY PANEL, PRESS UPDATES, SUB SYSTEM (partners, DESKTOPS,
  APP.SKINS), ARCHIVED VERSIONS.
- Nav: COMPANY, SERVICES, PORTFOLIO, ACCOLADES, EXPERIMENTAL, EQUIPMENT, CONTACT; a "////" marker over the active
  item.
- Panels collapse and expand; MAINFRAME grows over AUXILIARY PANEL on PORTFOLIO and COMPANY.
- Section template: header pod ("COMPANY / STUDIO.DATABANK"), pill sub-buttons with LEDs (VISION, APPROACH,
  PARTNERS, EXECUTIVE TEAM, MEDIA KIT), a curved content plate, a full-bleed 3D render.
- Portfolio: project list, "SORT PROJECT MENU BY", a detail plate with a live preview, Client and Technology
  fields (Flash MX, After Effects, 3DSM), VIEW.
- Personalization: four soundtrack loops (01. DESERT TRANCE, 02. NEVERRAIN, 03. SYNERGY, 04. EXILE) with
  transport controls and a plasma visualizer; wallpapers (PHIBERGLASS, EXPEDITION_01 ...); app skins (PROPHECY
  PRIME, CHROME OXIDIZED, AQUA OXIDIZED); Winamp skins; archive links to V3 "EXPANSIONS" and V2 "REBIRTH".

## Visual signature
- Oxblood with teal and one hot cyan (palette in `visual-system.md`); diagonal hatch bands; beveled pods; glossy
  red orbs; LED dots; curved plates; glossy 3D renders; katakana status text.
- Type [asset]: pixel fonts hooge 05_55, uni 05_53 and standard 07_53 for UI; Interstate, Akzidenz Grotesk
  Condensed, Eurose Wide and Hoefler ("IV") for display.
- Panel header: `>>` icon, MAIN|FRAME split weight, micro text, `- - -` controls.
- Key frames: `assets/taste-board.jpg` row 2.

## Motion signature
- Boot ~16 s: readouts and circuit traces on an empty frame -> a drawn bracket with an "IV" tag -> a glass orb
  with the logo -> line tracer carrying boxes -> shell assembly with "LOADING DATA" placeholders -> in MAINFRAME
  ring lock, glyph shatter, diagonal slashes to white, a katakana readout (RETRIEVING_MAINLEVEL.CORE.JP, a bar to
  100, COMPLETE), slash-out reveal, then a ~4 s cinematic fade-up of the hero. Table in `motion.md` section 3.
- Section change ~6.6 s: the same shatter and slash grammar, then MAINFRAME's layout morph and a module cascade.
- Hover: instant rose block; rollout splits into two lines that part and fade (~200 ms).
- Detail views: image opens from a single line into a box; previews cycle with horizontal motion-blur streaks.
- Asset facts [asset]: 41 fps; median move 220 ms ease-out (k 3.0); panel enter 244-268 ms ease-out (k
  3.4-3.7), exit 244 ms ease-in; white "develop" tint 317-488 ms linear; 1-frame alpha blinks; no filters (SWF6),
  so light is faked with tint, masks and gradients; 18 short MP3 cues and a 5.64 s intro ambience loop; boot copy
  "+ SKIP ANIMATION >" and "+ DISENGAGE AUDIO".
- Sheets: `assets/motion/v4-*.jpg`.

## How it works [asset]
- SWF6, AS1, 970x655 stage. The core movie loads section SWFs (`subdata/subsection_company.swf` and others, 712x400
  at 40 fps) into a section deck, showing `ceil(loaded / total x 100)` progress.
- A playlist player reads `swfInfo.xml` and loads each soundtrack as a SWF; fades run through dedicated fader clips.
- Store, wallpapers, legal and archives open in sized popup windows via `javascript:` URLs; no deep linking.
- A `backend.php` endpoint handles the mailing list ("SUBSCRIPTION RECEIVED / INVALID EMAIL ADDRESS").

## Borrow
- The interface as a window manager: named systems, collapsible panels, a content panel that claims space.
- The glyph shatter and slash wipe as a once-per-session hero moment.
- User-chosen ambience (soundtracks), skins and wallpapers, persisted.
- Split-weight panel titles and LED-indicated sub-navigation.
- Skip and mute controls inside the boot.

## Fix
- 8 px pixel fonts for copy; teal-on-oxblood body text; tiny hit areas.
- 16 s boot and 6.6 s section changes; full-field white during navigation.
- Fixed 970x655 table layout; popups; no URLs per section.
