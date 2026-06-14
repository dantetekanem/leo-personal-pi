# Motion library guide

Use this guide to choose the smallest animation tool that can deliver premium motion without harming performance or maintainability.

## Decision matrix

| Need | Prefer | Why |
| --- | --- | --- |
| Simple hover/focus/enter state | CSS transition/keyframes | Lowest dependency cost; browser can optimize transform/opacity well. |
| React component state, enter/exit, layout, gestures | Motion for React | Declarative API, layout/shared-element support, gestures, scroll values, good React fit. |
| Complex scroll scenes, pinning, scrubbing, timelines, SVG/canvas/WebGL | GSAP | Deep timeline and plugin ecosystem; framework-agnostic; strong production edge-case handling. |
| Lightweight creative DOM/SVG/text timeline in vanilla or framework-neutral code | Anime.js | Modular imports, timelines, stagger, SVG/text utilities, modern v4 API. |
| No dependency but JS-controlled DOM animation | Web Animations API | Native browser primitive; good for transform/opacity keyframes with JS controls. |
| Route/page transition that can be snapshot-based | View Transition API | Native page/view continuity; best for page-level context, not rapid micro-interactions. |
| Tiny rolling label/status/counter text | slot-text or custom CSS slot text | Textmotion.dev-like tactile labels; dependency-free CSS transform patterns can be enough. |
| Text reveals and typography effects | Custom CSS, Motion/GSAP text splitting, Trickle, or audited small text libraries | Text effects are often better copied/adapted than installed wholesale; keep semantics and grapheme handling correct. |
| Smooth scrolling foundation | Native CSS scroll behavior first; Lenis only when the product needs controlled smooth/inertial scroll | Smooth scroll is infrastructure, not decoration; avoid breaking anchors, scroll restoration, keyboard navigation, or native feel. |
| Ready-made animated sections/components | SmoothUI, Magic UI, Aceternity UI, Glin UI, Glass UI, or shadcn-style registries | Good for inspiration and acceleration, but audit dependency weight, source quality, accessibility, and visual fit before adopting. |
| Liquid/glass design system | Tokenized CSS surfaces first; Glin UI / Glass UI patterns when a full glass system is desired | Glass needs contrast, fallbacks, reduced transparency/motion behavior, and strict performance budgeting. |

## Current market snapshot, June 2026

Recent research shows a split ecosystem rather than a single winner:

- **React product UI default:** Motion / Framer Motion remains the safe default for React apps because it covers layout animation, enter/exit, gestures, scroll values, and state-driven micro-interactions with React-native ergonomics.
- **Advanced choreography default:** GSAP remains the strongest choice for scroll-driven storytelling, pinned/scrubbed timelines, SVG/text/plugin-heavy work, and agency/marketing motion where imperative timeline control is an advantage.
- **Physics/natural feel:** React Spring is still relevant when the exact spring feel matters more than speed of implementation, especially gesture-like interactions.
- **Designer-authored animation:** Lottie and Rive solve a different workflow. Use Lottie for play-once or looped vector illustrations; prefer Rive when designers need state machines and interactive behavior.
- **Small-polish utilities:** AutoAnimate is high-ROI for list/layout changes; Lenis is common for smooth scroll foundations; Anime.js is a good lightweight creative engine when React integration is not the main need.
- **Prebuilt motion/component layer:** SmoothUI, Magic UI, Aceternity UI, Glin UI, Glass UI, and newer text kits such as Trickle/slot-text are useful references for modern effects. Treat younger/low-adoption packages as source inspiration until their maintenance, accessibility, and dependency story is proven.

NPM last-month download counts checked 2026-06-14:

| Package | Downloads |
| --- | ---: |
| `framer-motion` | 147,946,377 |
| `motion` | 52,611,880 |
| `lottie-web` | 24,255,562 |
| `@react-spring/web` | 19,529,038 |
| `gsap` | 12,924,435 |
| `lottie-react` | 10,614,492 |
| `@gsap/react` | 3,884,159 |
| `@formkit/auto-animate` | 3,720,393 |
| `animejs` | 3,531,625 |
| `@rive-app/react-canvas` | 3,013,574 |
| `lenis` | 3,007,897 |
| `slot-text` | 1,865 |

Use these counts as adoption signal, not quality proof. The best choice still depends on stack, animation complexity, accessibility, bundle budget, and whether the team wants source-owned components or long-term package dependencies.

## Practical selection rules

1. Start with CSS for single-element or simple state transitions.
2. Use the animation library already present if it is adequate.
3. In React/Next, Motion is usually the best first new dependency for product UI motion.
4. Use GSAP for marketing-grade choreography, advanced timelines, scroll pinning/scrubbing, SVG morphing, or canvas/WebGL coordination.
5. Use Anime.js for lightweight creative DOM/SVG/text animation when React integration is not the main need.
6. Use View Transitions for route/view continuity only when non-interruptible snapshot motion is acceptable.
7. Avoid mixing libraries inside one component tree unless there is a clear ownership boundary.

## Performance reminders

- Transform and opacity are the safest properties to animate because they can often stay in the compositor.
- Avoid layout-triggering animation such as top/left/width/height/margins unless measured and necessary.
- Treat `will-change` as a temporary, targeted optimization, not a default class.
- Prefer IntersectionObserver, ScrollTimeline-supported tools, or library scroll utilities over manual scroll polling.
- Profile scroll, blur, backdrop-filter, many-element staggers, and route transitions on low-power devices.

## Accessibility reminders

- Respect `prefers-reduced-motion`.
- Preserve focus, keyboard access, and screen-reader text.
- For split text, expose the complete original phrase with ARIA and hide animated fragments from assistive tech.
- Keep important copy readable; avoid long decorative text effects on critical content.

## Source links checked while drafting

- Motion for React docs: https://motion.dev/docs/react
- Motion homepage / feature overview: https://motion.dev/
- Motion AnimateView / View Transition notes: https://motion.dev/docs/react-animate-view
- GSAP React patterns: https://gsap.com/resources/react-basics
- Anime.js module imports: https://animejs.com/documentation/getting-started/module-imports
- MDN animation performance and frame rate: https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Animation_performance_and_frame_rate
- MDN CSS and JavaScript animation performance: https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/CSS_JavaScript_animation_performance
- MDN will-change: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/will-change
- MDN prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
- MDN View Transition API: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
- textmotion.dev / slot-text: https://textmotion.dev/
- slot-text repository: https://github.com/Danilaa1/slot-text
- SmoothUI: https://smoothui.dev/
- Magic UI repository: https://github.com/magicuidesign/magicui
- Aceternity UI: https://ui.aceternity.com/
- Glin UI: https://glinui.com/
- Glass UI: https://glass-ui.crenspire.com/
- Trickle text animation kit: https://tricklekit.dev/
- NPM downloads API: https://api.npmjs.org/downloads/point/last-month/<package>
