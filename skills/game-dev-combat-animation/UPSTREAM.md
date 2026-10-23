# Upstream source

Saved from [MengTo/Skills](https://github.com/MengTo/Skills/tree/398cd41c86ba42fbb30e944ae507f463648f08b7/agent-skills/game-combat/game-dev-combat-animation).

- Revision: `398cd41c86ba42fbb30e944ae507f463648f08b7`
- Upstream directory: `agent-skills/game-combat/game-dev-combat-animation`
- `SKILL.md` adds one local-use notice after its heading. Its remaining content and every other upstream file are unchanged. This provenance file is local.
- The bundled license is retained.
- Saving this skill did not execute its scripts or install their dependencies. Review the required project, tools and permissions before running any bundled command.
- The upstream examples and helpers target the Thornvigil 3D rig/project. Its account choices, asset restrictions, paths and release workflow describe that project, not the user's environment. For 2D sprite work, use applicable staging/contact/recovery review principles rather than treating those rig scripts as a Godot implementation.

## Before executing tools

A read-only inspection found no blocker to saving this bundle. It did not execute or certify the helpers, their external imports, or the capture receiver.

- `scripts/install.sh` copies tools into an existing Thornvigil checkout's `.dream-loop/moves/` and can overwrite matching names.
- `scripts/tools/setup.js`, `play.js` and `shot.js` fetch and evaluate `/driver.js` from `127.0.0.1:6163`. The capture tools also send canvas PNG data to that local service. Verify who owns the port and how the receiver handles captures before using it; the receiver is not bundled here.
- `ab-pack.py`, `vidcompose.py` and `encode.swift` remove matching image/video outputs in operator-selected destinations. Inspect those paths before running them.
- The helpers require upstream project modules and dependencies, including `three`, Pillow and macOS-specific font/framework support. They have not been installed or tested here.
- The upstream release instructions and standing push/publish authorization describe the author's project. They do not grant permission to commit, push, publish, install dependencies, start services or send captures in the user's environment.

## Upstream file hashes

For `SKILL.md`, the hash below identifies the original content before the local-use notice.

These are Git blob SHA-1 values from the pinned tree, not raw-file SHA-1 values.

| File | Git blob SHA-1 |
|---|---|
| `SKILL.md` | `3176811d6a3d400224fd5275301491d0086802c0` |
| `references/review.md` | `ae780b2ba6a947b59f85efc87d5b39eecc0b6fd2` |
| `references/rules.md` | `31d4dbe58dd61f83135b089efd7877b3c9216357` |
| `references/techniques.md` | `c7021edf21d3ed22d55a3e9bb58309bef47b4b9b` |
| `references/thornvigil.md` | `135b5b460a66e484b539404d0a8310963a95c11c` |
| `references/traps.md` | `2034b47c5e9ae114fc9e32251756eee872e8e27a` |
| `scripts/install.sh` | `23e4969e54afb0ee54a11e121d73a2d62b4462c4` |
| `scripts/tools/ab-pack.py` | `ec49971403423a565ac6426514b88ba4804c4ed5` |
| `scripts/tools/anchor.mjs` | `d8d81bc67a68c68b3b0f4357dfa4e9b9c85342aa` |
| `scripts/tools/armcheck.mjs` | `4682f0596ecd7503f94d2aa540b559ce94728cc2` |
| `scripts/tools/at.mjs` | `bc89b2e390032253b6389f7318a3ff7e542cddb0` |
| `scripts/tools/baketime.mjs` | `8b47da7ccca0811441135df60fa4f6eaa5396cdc` |
| `scripts/tools/drawfit.mjs` | `cd092ced1006e63647d48ad8f8937929adc377dd` |
| `scripts/tools/encode.swift` | `36002a6f8f9cbf19c77e9b6787998e1e757771c4` |
| `scripts/tools/face.mjs` | `1e0b8b9435c66434732b2d0d677e9bd0a3408388` |
| `scripts/tools/host.html` | `fa3195c29c70678946bd6319fde6166060ed7503` |
| `scripts/tools/jumps.mjs` | `f032b8d2e9dc76dd6d8d06de001d7f580a33e585` |
| `scripts/tools/keydesign.mjs` | `61d003f3242b5d094d24f7710b9f9e6c2f3b3ecf` |
| `scripts/tools/knight-measure.mjs` | `4547488272baef24661f1d2cddf6ee4ea0c08cff` |
| `scripts/tools/msheet.py` | `987a66c3456a6ca1b5fffc5cd0ac22693349543b` |
| `scripts/tools/play.js` | `4977429671054a6d46712dd935c34785deab0124` |
| `scripts/tools/psheet.py` | `fa1d7b539109544edf42f89f834d715f3a0815d9` |
| `scripts/tools/setup.js` | `f4e4562601fbf4c083933f25fe0121bc70c10dc9` |
| `scripts/tools/shot.js` | `97610ea10f9c229d7f018dd4d97fdbabf524906b` |
| `scripts/tools/vidcompose.py` | `ebd6a0a88b38fac8e8552d514ee20766fe528026` |
| `templates/ab-judge-prompt.md` | `8b067eaa988db7414f3a93707058f71607486391` |
| `templates/critic-prompt.md` | `c84ae183190e2c330de47196db389604a4fc2789` |
| `LICENSE` | `b3a5f823a69b4b010f92930ac09e8a776daf65c6` |
