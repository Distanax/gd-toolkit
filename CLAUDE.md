# gd-toolkit — Claude context

Toolkit for building Geometry Dash levels **in code**, made by Claude + Distanax. Read this first;
`docs/NOTES.md` holds the full running notes (song map, physics tables, reference study, decisions).

## Active mission: GD mastery (learn to make rated-standard levels; capstone Thermal Lock)
**Start every session with the resume protocol in `mastery/PROGRESS.md`:** `git pull`, read this file,
`mastery/PROGRESS.md` and `mastery/TASKS.md`, then do the next unchecked task you can do now ([offline]
always, [editor] only if the bridge answers). One task = one commit + push. Things Distanax must do go
in `mastery/PLAYTEST.md`. Study notes: `mastery/notes/`; lessons: `mastery/LESSONS.md`; self-review
checklist: `mastery/CHECKLIST.md`. Never claim beatable/fun/rate-worthy without evidence; cite sources.

## Finished mission: gd-bridge (v1.0.2, verified live 2026-10-09)
Records: `PROGRESS.md`, `TASKS.md`, `TESTING.md` (root). Mod code: `mod/` (built only in CI);
MCP server: `server/`. Re-run `tests/e2e_bridge.py` + `tests/e2e_extra_bridge.py` after any mod change.

## gd-bridge tool reference (MCP server `gd-bridge`)
Live control of the GD editor on Distanax's PC. Chain: MCP tool -> `server/` (Python, stdio) ->
HTTP on 127.0.0.1 with the per-launch token from `bridge.json` -> `mod/` (Geode) -> GD main thread.
Wire protocol: `docs/PROTOCOL.md`. Install: README "gd-bridge" + `TESTING.md` section 1.

**Safety (enforced in the mod, mirrored in the mock):** every write tool only works on a level whose
name starts with `"CLAUDE "` unless it passes `confirm_name="<exact level name>"`; every write backs
the level up first (`%LOCALAPPDATA%\GeometryDash\geode\mods\distanax.gd-bridge\backups\<level>\`,
newest 200 kept); `create_level`/`open_level` never leave one of Distanax's own levels open in the
editor (refused, so unsaved work is never discarded); nothing is ever uploaded or deleted. Writes are
refused during a playtest (`busy`). Errors come back as `[code] message` (codes in PROTOCOL.md).

Coordinates are GD units: 30 = 1 block, object centre, ground row y = 15 (same as `toolkit/gdlib.py`).
Every tool speaks **level-string coordinates**. (Internally GD places objects 90 units higher — string
y 15 is node y 105 — and the mod converts both ways; measured live 2026-10-09.)

| Tool | What it does | Example arguments |
|---|---|---|
| `status` | GD/mod reachable? scene, editor open, playtest state, level name/ID/song/object count, versions. **Call first.** Returns `running: false` instead of failing when GD is closed. | `{}` |
| `list_levels` | Local levels (name, song, `claude` flag). | `{"claude_only": true}` |
| `create_level` | New level, always prefixed `"CLAUDE "`; returns once it is open in the editor. | `{"name": "thermal lock s2", "song_id": 1502369}` |
| `open_level` | Open by exact name; non-CLAUDE levels need `confirm_name`. | `{"name": "CLAUDE thermal lock s2"}` |
| `save_level` | Save the open level to GD's list and to disk. | `{}` |
| `get_level_string` | Raw level string `header;obj;obj;...` + name + object count. | `{}` |
| `set_level_string` | Replace the whole level (header + objects), e.g. from `Level.level_string()` in gdlib. Reloads the editor. | `{"level_string": "kS38,...;1,1,2,15,3,15;"}` |
| `add_objects` | Add objects: GD strings or friendly dicts. Returns uids. | `{"objects": [{"id": "block", "x": 15, "y": 15}, {"id": "spike", "x": 105, "y": 15}, {"id": "yellow_orb", "x": 195, "y": 75}, {"id": "move_trigger", "x": 45, "y": 165, "target_group": 1, "move_y": 60, "duration": 0.5}, "1,8,2,135,3,15"]}` |
| `list_objects` | Objects (uid, id, x, y, rotation, scale, groups, trigger), filtered and paged (max 5000). | `{"select": {"ids": ["spike"], "region": {"x1": 0, "y1": 0, "x2": 600, "y2": 300}}, "object_strings": true}` |
| `modify_objects` | Set properties (friendly names or raw keys, `null` removes) and/or move. Objects are re-created: uids change. | `{"select": {"groups": [1]}, "set": {"rotation": 90, "color": 3}, "move": {"dx": 30}}` |
| `remove_objects` | Remove matching objects; empty selector refused unless `all`. | `{"select": {"uids": [12, 13]}}` / `{"select": {"all": true}}` |
| `get_triggers` | Every trigger with its full object string, optionally by type. | `{"type": "move"}` |
| `move_camera` | Centre the editor view on x/y at a zoom; no args = read camera. | `{"x": 900, "y": 150, "zoom": 0.6}` |
| `screenshot` | PNG of the window (image + metadata). Aim with x/y/zoom or `region`; camera restored after. | `{"region": {"x1": 0, "y1": 0, "x2": 1200, "y2": 300}}` |
| `playtest` | `start` / `stop` / `pause` / `resume` / `status`; `from_x` starts from an x (temporary start pos). | `{"action": "start", "from_x": 1500}` |
| `capture_frames` | During a playtest: N frames every interval_ms, returned as images in order. | `{"count": 6, "interval_ms": 500}` |
| `get_music` | Song ID / official track, offset, fade in/out, guidelines (time + colour). | `{}` |
| `undo` / `redo` | GD's own undo/redo of one editor action — for hand edits only (revert tool edits with `restore_backup`, see limits). | `{}` |
| `list_backups` | Backups of a level, newest first. | `{"level": "CLAUDE test"}` |
| `restore_backup` | Replace the open level with a backup (current state backed up first). | `{"file": "20261009T040557123Z_add_objects.txt"}` |

**Selectors** (`select`, criteria ANDed): `uids`, `ids` (numbers or names), `groups`, `region`
`{x1,y1,x2,y2}` (by object centre), `triggers: true`, `all: true`.
**Object names:** block, spike, half_spike, yellow/pink/red/blue/green/black/dash `_orb`,
yellow/pink/red/blue `_pad`, cube/ship/ball/ufo/wave/robot/spider/swing `_portal`,
gravity_up/down_portal, mirror_on/off_portal, mini_portal, normal_size_portal, dual_on/off_portal,
speed_0.5x..speed_4x, text, start_pos, and triggers color/move/pulse/alpha/toggle/spawn/rotate/
follow/shake/stop/zoom `_trigger` (full table: `server/src/gd_bridge_mcp/objects.py`). Anything else:
numeric ID. **Friendly properties:** x, y, flip_x, flip_y, rotation, scale, scale_x, scale_y, groups
(list), color, detail_color, z_layer, z_order, editor_layer, dont_fade, dont_enter, duration,
move_x, move_y, easing, target_group, touch_triggered, spawn_triggered, multi_trigger; anything else
as a raw key string (`"36": 1`) per gddocs.

**Typical loop:** `status` -> `create_level`/`open_level` -> `add_objects` (or `set_level_string`
from a gdlib build) -> `screenshot` to check the layout -> `playtest start` + `capture_frames` +
`playtest stop` to watch it -> `save_level`. Distanax still does the real playtest.

**Known limits (2026-10-09):**
- **Verified in-game 2026-10-09 on v1.0.2** (Geode v5.10.1, GD 2.2081), twice in a row:
  `tests/e2e_bridge.py` 13/13 and `tests/e2e_extra_bridge.py` 16/16 — every tool, including
  set_level_string/restore_backup reloads, switching levels from inside the editor, modify_objects,
  playtest from_x and frames. Re-run both after any mod change (TESTING.md section 2).
- Windows only (the mod uses Winsock; CI builds Win64 only).
- **Don't use `undo` on tool edits.** GD's history records the objects a tool removes but not the
  ones it creates, so undo after `modify_objects` leaves a duplicate (measured live). Revert tool
  edits with `list_backups` + `restore_backup`; `undo`/`redo` are for hand edits. (Removing with
  GD's noUndo flag instead frees the object while GD still uses it and kills the game — measured
  live in 1.0.1, reverted in 1.0.2. Keep removeObject(obj, false).)
- **Switching or reloading the editor is staged** (crash found live 2026-10-09: building a new
  LevelEditorLayer while the old one still ran -> access violation in GameObject::shouldBlendColor).
  `set_level_string`, `restore_backup`, `create_level`, `open_level` leave through GD's own exit
  (EditorPauseLayer::onExitEditor), wait until the old editor is gone, then open the level and wait
  until it is up (a few seconds; client timeout 60 s). The reload clears GD's undo history.
- `modify_objects` re-creates objects, so uids change.
- `playtest from_x` uses a temporary start position with default settings (cube, 1x, normal
  gravity): starting inside a ship/2x section plays it as cube 1x. It is removed when the playtest
  stops (also via GD's own stop button).
- `capture_frames`: 1-120 frames, interval >= 16 ms, each frame costs one extra render (may dip FPS);
  frames are window-sized PNGs, downscaled to `max_width` (640) for the reply. Captures live in
  `...\distanax.gd-bridge\captures\` and are deleted after 3 days (on the next GD launch).
- Friendly property names cover common keys and the move trigger only; other trigger settings need
  raw gddocs keys, which are still unverified in-game (see Rules below).
- One request at a time; commands run on GD's main thread with a 10 s deadline (`timeout` error if GD
  is frozen or loading).

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
1. Custom **Geode bridge mod** for live editor control — DONE: gd-bridge v1.0.0 (see above), verified
   in-game 2026-10-09. CI builds it, so no local C++ toolchain is needed.
2. **Blender -> GD 3D converter** for EVOLUTION-style effects (reference level 150086482, copyable).
3. **Playtest recordings** (Win+Alt+R) dropped into `gd_levels` for frame analysis.

## Working style
- Concise and professional.
- Never claim a level is beatable or fun until Distanax has playtested it.
- Commit after every meaningful change, and push to `main`.
- Keep `docs/NOTES.md` current: decisions, verified facts, open issues.
