# gd-toolkit — Claude context

Toolkit for building Geometry Dash levels **in code**, made by Claude + Distanax. Read this first;
`docs/NOTES.md` holds the full running notes (song map, physics tables, reference study, decisions).

## Workflow
1. Generate a `.gmd` with Python (`toolkit/gdlib.py`, level scripts under `levels/`).
2. Save it to `C:\Work\ClaudeProjects\gd_levels\` (scripts write to `out/` first; copy across).
3. Distanax imports it into Geometry Dash with the **GDShare** mod
   (Create -> My Levels -> pink page button on the right, type the path), saves it, and playtests.
4. Their playtest result is the only verdict on whether a level works.

## Layout
- `toolkit/` — `gdlib` (builder + `.gmd` export), `gdphys` (exact physics), `trajgen`
  (trajectory-first cube generator), `sim2` (current simulator), `sim` (old simulator; its
  `render()` is still the preview renderer), `gdparse` (`.gmd` reader).
- `levels/thermal_lock/heatseeker.py` — current level. `analysis/` — reference-level stats and renders.
- `tests/smoke_test.py` — calibration level. `docs/NOTES.md` — running notes.
- Run everything from the repo root, e.g. `python levels/thermal_lock/heatseeker.py`. Entry scripts
  carry a `sys.path` shim; `toolkit` modules use relative imports. `out/` and `refs/` are git-ignored
  (refs are other creators' levels: copy `gd_levels\ref_*.gmd` into `refs/` to analyse them).

## Rules (verified — do not re-derive)
- **Coordinates:** 30 units = 1 block; objects are placed by their centre; ground row y = 15
  (then 45, 75, ...); first column right of the start line x = 15.
- **Physics:** use the exact values in `toolkit/gdphys.py` (sources: camila314/gdp — GD 2.2
  decompiled `PlayerObject` — and Open-GD/OpenGD). Never fall back to estimates. A simulator pass
  is evidence, not proof.
- **Level-string keys:** from Wyliemaster/gddocs
  (`docs/resources/client/level-components/level-string.md`). Trigger property keys are still
  unverified in-game; check them against a reference level before relying on them.
- **Never use computer-use `open_application` on Geometry Dash** — it relaunches the game through
  Steam and drops unsaved work. Navigate by clicking only. Don't open or save Distanax's own levels.

## Current level: "Thermal Lock"
- Song: Creo - Heatseeker, Newgrounds ID 1502369, 127 BPM, first beat 0.055 s
  (beat 0.4724 s, bar 1.890 s). Target Hard-Harder, ~115 s, modern style, thermal-camera palette.
- **Section 1 v2** (intro, 0-18 s, trajectory-first): built, 162 objects, sim2 passes —
  **awaiting playtest**.
- Known mismatch (2026-10-08): `gd_levels\thermal_lock_s1v2.gmd` was exported from a slightly
  different `trajgen` than the committed one — 34 platform blocks sit 15 units (half a block) apart
  between the two. Confirm which is wanted before building on Section 1.

## Roadmap
1. Custom **Geode bridge mod** for live editor control (load/save level, list objects, playtest,
   screenshots). Geode v5.10.1 installed; needs VS 2022 Build Tools + CMake + Geode SDK.
2. **Blender -> GD 3D converter** for EVOLUTION-style effects (reference level 150086482, copyable).
3. **Playtest recordings** (Win+Alt+R) dropped into `gd_levels` for frame analysis.

## Working style
- Concise and professional.
- Never claim a level is beatable or fun until Distanax has playtested it.
- Commit after every meaningful change, and push to `main`.
- Keep `docs/NOTES.md` current: decisions, verified facts, open issues.
