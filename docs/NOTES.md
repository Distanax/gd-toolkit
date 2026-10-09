# GD Level Maker — running notes

## Pipeline (verified 2026-10-08)
- GDMCP is unusable: the Geode mod's GitHub repo was deleted, so there is no in-game half. (Python server `gdmcp` is still registered in the Claude config; it can be removed.)
- Workflow: Python generator (`gdlib.py`) -> `.gmd` -> `C:\Work\ClaudeProjects\gd_levels\` -> import with GDShare (Create -> My Levels -> pink page button on the right, then type the path in the file dialog) -> open in editor, **Save immediately** -> verify with screenshots.
- Never use computer `open_application` on Geometry Dash: it relaunches the game through Steam and drops unsaved work. Navigate by clicking only.
- Do not open or save Distanax's existing levels; the first row of My Levels is the newest one.

## Verified coordinate conventions
- 30 units = 1 block. Objects are placed by their centre.
- Ground row: y = 15 (next rows 45, 75, ...).
- First column right of the start line: x = 15.
- Header colours (kS38) import correctly (BG 1000, Ground 1001).
- Object IDs confirmed: block 1, spike 8, yellow orb 36, yellow pad 35, ship portal 13, 2x speed 202, text 914.
- Not yet verified: trigger property keys (move/color/pulse/alpha/spawn/rotate/zoom/shader), song offset, custom song ID field (k45).

## Speeds (units/s, GD 2.2)
0.5x 251.16 | 1x 311.58 | 2x 387.42 | 3x 468.0 | 4x 576.0

## Level brief
- Song: Creo - Heatseeker, Newgrounds ID 1502369 (3:26, uploaded Dec 2025, score 4.68)
- BPM: 127.00, measured by onset autocorrelation and stable 0-160 s. First beat at 0.055 s; beat = 0.4724 s; bar = 1.890 s.
  Downbeats on beat index 2 mod 4 (bar 2 starts 2.89 s). Phase shifts after ~160 s (pitch-shift section), so it isn't used.
- Style: modern. Difficulty: Hard-Harder (4-7 stars). Mode: classic. Target ~115 s (Long).
- Concept: "thermal lock" - thermal-camera palette (indigo, magenta, orange, white-hot); a homing missile motif chases the player.

## Song energy map (bars of 4 beats)
| Bars | Time (s) | Music |
|---|---|---|
| 2-9 | 2.9-18.0 | intro, quiet, builds |
| 10-25 | 18.0-48.2 | DROP 1 (full energy) |
| 26-32 | 48.2-61.5 | groove, mid energy |
| 33-41 | 61.5-78.5 | build, rising |
| 42-43 | 78.5-82.3 | pre-drop dip |
| 44-58 | 82.3-110.6 | DROP 2 (full energy) |
| 59-61 | 110.6-116.3 | breakdown -> level ends |

## Section map (proposed, awaiting approval)
1. Intro 0-18.0 s: cube 1x, sparse, readable
2. Drop 1a 18.0-33.1 s: cube 2x, orb/pad clicks on beats
3. Drop 1b 33.1-48.2 s: ship 2x
4. Groove 48.2-61.5 s: ball 1x
5. Build 61.5-78.5 s: UFO 1x, density rising
6. Pre-drop 78.5-82.3 s: cube, breather + camera zoom
7. Drop 2a 82.3-97.4 s: wave 2x (climax)
8. Drop 2b 97.4-110.6 s: cube/spider 2x
9. Ending 110.6-~116 s: slow-down, end

## Build status
- Builder: `heatseeker.py` (sections as functions), `sim.py` (approximate cube simulator + preview renderer). Physics constants are estimates: airtime 0.39 s, apex ~2.1 blocks, yellow pad ~0.52 s airtime.
- Section 1 (intro) built: 89 objects, 18 s, imported as "Thermal Lock S1" (saved). Simulator passes; per-click windows ~80-160 ms. AWAITING PLAYTEST.
  Beat clicks: b6,8,10,12,14,(pad b16),18,20,21,22,24,26,(orb b27),29,30,31,32,34,35,36,37; 2x portal at b37.75.
  Unverified: ground-level yellow orb at y=45 (b27) being clickable while running; pad landing distance.

## Reference study (2026-10-08): 6 recent rated Harder levels
Fatal Attraction 148620355, CrystalWrath 149977853, STARDUST 149965962, midnight valley 149538357, QUARANTINE 149946353, luminol 149779431
(exported via GDShare to C:\Work\ClaudeProjects\gd_levels\ref_*.gmd; analysis: analyze_refs.py, render_ref.py)
- Mode/speed changes: median segment 1-4 s (luminol is the outlier at 13 s). 10-38 segments per level.
- Orbs+pads: 0.9-3.4 per second; heavy use of blue/pink/green/black orbs and blue/pink pads; gravity flips everywhere.
- Cube style: hop between small floating platforms over spike carpets; ceilings used constantly.
- Speed changes (0.5x-4x) follow the music; intros may be slower single-mode (10-16 s).
- Lengths 53-107 s.

## Section 1 v2 (trajectory-first generator, trajgen.py)
- 162 objects, 24 clicks + 2 pads in ~15 s; per-click windows 120-240 ms (sim2.py estimate).
- Mechanics: floating platforms over spike carpet, yellow/pink/blue orbs, yellow/blue pads, ceiling phrase bars 6-7.
- Exported to gd_levels\thermal_lock_s1v2.gmd. NOT YET IMPORTED/TESTED.
- v1 playtest: cleared in 2 attempts, 20 jumps (= designed clicks). Too easy for Harder.

## Exact physics (gdphys.py) — replaces estimates (2026-10-08)
Sources: camila314/gdp (GD 2.2 decompiled PlayerObject::updateTimeMod/updateJump), Open-GD/OpenGD (ringJump, propellPlayer, pad handling, hitbox table).
- Per speed (playerSpeed, speedMult, jump/tick, gravity/tick^2): 0.5x (0.7, 5.98, 10.62, 0.9402) | 1x (0.9, 5.77, 11.18, 0.9582) | 2x (1.1, 5.87, 11.42, 0.9572) | 3x/4x (1.3/1.6, 6.0, 11.23, 0.9612). Ticks are 1/60 s.
- 1x cube: airtime 0.389 s, apex 65 u (2.17 blocks), jump length 4.04 blocks. Terminal fall 900 u/s.
- Orbs = jump vel x {yellow 1, pink 0.72, red 1.38, blue 0.8 (then flip), green 1 (flip)}; mini x0.8.
- Pads = 960 u/s x {yellow 1, pink 0.65, red 1.25, blue 0.8 (then flip)}.
- Blue orb/pad: velocity applied in the OLD gravity direction, then gravity flips (thrown toward new floor).
- Ball/spider gravity 0.9582*0.6; robot jump x0.5 (+hold), gravity x0.9; ship max up 8/tick, max down 6.4/tick.
- Hitboxes: spike ID 8 = 6x12 centred; player cube 30x30, solid-death inner ~9x9. Full table in OpenGD Source/LongData.cpp.
- Level-string property keys: Wyliemaster/gddocs docs/resources/client/level-components/level-string.md (move 28/29/30/51, rotate 68/69, pulse 45-48/52, alpha 35, spawn 63, scale 128 ...).

## Capability roadmap (agreed with Distanax 2026-10-08)
1. GitHub repo for the toolkit: DONE 2026-10-08 (Distanax/gd-toolkit; layout in README.md, context in CLAUDE.md).
2. Custom Geode bridge mod (load/save level in editor, list objects, playtest, screenshots). Needs VS 2022 Build Tools + CMake + Geode CLI/SDK on the PC. Geode installed: v5.10.1.
3. Blender -> GD 3D converter (EVOLUTION-style effects; reference level 150086482, copyable).
4. Playtest recordings (Win+Alt+R) dropped into gd_levels for frame analysis.

## Group IDs / colour channels in use
(none yet)

## Open issues
- 2.2-only keys (scale Y, skew/warp, shaders, area triggers) still to map from reference levels.
- Section 1 v2 re-exported with exact physics; awaiting playtest.
- gd_levels	hermal_lock_s1v2.gmd does not match the committed generator: 34 platform blocks differ by 15 units (exported file is on the 15+30k grid, committed trajgen snaps to multiples of 15). Decide which is wanted before building on Section 1.
