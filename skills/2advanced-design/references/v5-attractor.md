# V5 Attractor (Flash, 2006; content updated into 2009)

URL: https://v5attractor.2advanced.com/ (2026 Ruffle archive of `2A_v5_core.swf` behind an enter gate; the
wrapper says subsection content is still incomplete). Labels as in `motion.md`; **[src]** = public source listed
in `sources.md`.

## Identity
- "Release Five - 2006" [rec]; Webby honoree 2007 [src]. The FWA called it "2Advanced's most complex blend of user
  aesthetics and backend technology to date" [src]. Eric Jordan: it "pushed Flash's usability by making it
  possible to bookmark and link to specific sections of the site" [src].
- Fiction: an "Attractor", a stepped pyramid that emits a beam, in a series of worlds. Each section is a world
  with its own hue and matte painting; the six paintings were offered as wallpapers (Edge of the Ocean, River of
  Eschaton, Distant Progressions, Fires of Hyperspace, Return of the Sakura, The Ice Concrescence) [asset].
- Boot copy: "STANDBY: INITIALIZING:", "INTERNAL ASSETS", "FONT HANDLER", "AUTOKERN INIT", "DIGITAL ATMOSPHERE"
  [asset].

## Information architecture [rec] [asset]
- Header on a four-column hairline grid: Home / Contact / Language, centered logo "2ADVANCED STUDIOS, LLC.
  PROGRESSIVE DESIGN TECHNOLOGY", Soundscape volume slider.
- "Expand Navigation Array": a translucent four-column drawer. Primary sections with color bullets (Company
  green, Portfolio yellow, Services orange-red, Case Studies magenta, Recognition white); Secondary Destinations
  fill on hover (Company: About Us, Executive Team, Press & News, Partners, Careers; Portfolio: Date, Projects by
  Alpha, Clients by Alpha, Industry, Service); Tertiary Destinations; Auxiliary Destinations (Home, Set
  Language, Contact, blog, hosting).
- Utility row: View Demo Reel, Download Digital Matte Wallpaper, 2A Website Archives, Preferences (Languages,
  Audio, Top Nav, Save). A hatched band with the ATTRACTOR mark. Four modules: Featured Project (rotating),
  Recent News, Contact (world map with numbered offices), Clients & Partners.
- Deep links: `#company`, titles like "2Advanced Studios - company"; paths such as
  `company/pressnews/pressreleases` and `portfolio/bydate/showall&id=` [rec] [asset]. EN/JP language switch.

## Visual signature
- The art is the hero; the UI is hairlines, small sentence-case labels, bar bullets and chevrons. Near-black base,
  electric blue at home, one hue per world (table in `visual-system.md`). Restraint where V3 and V4 were dense.
- Type [asset]: Verdana 9/10 px pixel-snapped for body, DIN Medium 14 px for tree nav, DIN Regular 25 px for
  "decoder" headers, a custom Attractor face, pixel fonts for status.
- Light [asset]: 943 Flash 8 glow filters (blur 6-15 px, #A8D4FE or #FFFFFF), rich on hover, none at rest.
- Key frames: `assets/taste-board.jpg` row 3.

## Motion signature
- Boot ~11.8 s: registration ticks -> beam -> pyramid emblem with an apex light -> long loading hold with the
  soundtrack -> emblem fades -> hairlines converge -> flare -> slit opens into the world -> grid draws ->
  "INITIALIZING" blinks -> modules power on left to right. Table in `motion.md` section 3.
- Section change ~6.3 s: UI vanishes -> the world closes into a slit -> readout on black -> hairlines converge ->
  slit opens on the new world -> UI redraws in the new hue -> module cascade. One metaphor for everything.
- Hover: glow bloom ~100 ms, decay ~120 ms; the row gets an arrow; the next column fills.
- Asset facts [asset]: 41 fps; position tweens median 171 ms; section panel slides 488 ms ease-in-out; matte slit
  1,073 ms in-out on show, 756 ms on hide; preloader pops 2000% -> 100% in 415 ms ease-out (k 4) with four ticks
  122 ms apart; nav build stagger 35 ms primary, 25 ms secondary; decoder headers 439 ms; thumbnails swap every
  6 s (offset 3 s), news every 15 s; inertial scroll `y = target - (target - y) / 1.2` per tick (about 17% of the remaining distance); Back easing only on bracket
  marks.
- Sheets: `assets/motion/v5-*.jpg`.

## How it works [asset]
- SWF8, AS2, 1600x1200 stage centered without scaling. Boot chain: config -> touts -> shared font libraries
  (`verdana.swf`, `dinmedium.swf` ...) -> `siteready` at 3.3 s.
- Content from `getData.php?lang=...` XML per section; mattes as separate `matte0..5.swf`; FLV demo reel;
  contact form via `LoadVars.sendAndLoad`.
- Preferences in a `SharedObject` (language, audio, top nav). Deep links through `ExternalInterface` to
  `dhtmlHistory.js`; `v5util.js` recolors the browser scrollbar per section hue.
- Sound: a 9.14 s soundtrack loop, hover ticks of 0.04 s, volume ramps every 10 ms, an ON/OFF preference.

## Borrow
- One transition metaphor (the slit) for boot and every section change.
- Color-coded worlds as wayfinding: the hue and the art change; the layout stays.
- A progressive-disclosure site map in a drawer (primary, secondary, tertiary, auxiliary).
- Restraint: let the art carry the detail and keep the UI quiet.
- Deep links, titles, saved preferences, language switch, downloadable art, an archive of past versions.

## Fix
- 6.3 s section changes that blank the UI: compress to 300-700 ms and stream content.
- Small low-contrast pixel text for real content.
- Hover-only secondary menus; make them work on click and focus.
- Fixed 975 px column and a forced 1024 px viewport; reflow the four columns.
