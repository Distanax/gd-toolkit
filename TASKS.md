# gd-bridge — task list

One task = one commit + push. Check a box only when its commit is pushed (and, for mod code, CI is
green). `[blocked: Distanax]` = needs Distanax in-game; instructions live in TESTING.md.
Mission and acceptance criteria: PROGRESS.md.

## M0 — Mission setup
- [x] 1. TASKS.md, PROGRESS.md, TESTING.md skeleton, resume protocol in CLAUDE.md
- [ ] 2. [blocked: Distanax] Create the "gd-bridge continue" routine (every 3 h) and record its id in PROGRESS.md — needs GitHub connected to claude.ai (TESTING.md section 0)

## M1 — Mod skeleton + CI (acceptance 1)
- [x] 3. Research: Geode v5 mod layout (mod.json schema, CMake, `$on_mod(Loaded)`), pin SDK v5.10.1 / GD 2.2081; notes in PROGRESS.md
- [x] 4. mod/ skeleton (mod.json id `distanax.gd-bridge`, CMakeLists, main.cpp that logs on load)
- [x] 5. GitHub Actions: build Win64 .geode on every push to main (build-geode-mod, sdk v5.10.1); get it green
- [x] 6. CI: publish the .geode as a release asset (rolling `latest` release on main, versioned on `v*` tags)
- [x] 7. TESTING.md: 5-minute install guide (download .geode, drop in mods folder, check log)
- [ ] 8. [blocked: Distanax] (TESTING.md section 1) Confirm the mod loads in GD (acceptance 2)

## M2 — Mod transport
- [x] 9. Research: Geode v5 threading (`queueInMainThread`), matjson API, save-dir path, logging; notes in PROGRESS.md
- [x] 10. Protocol spec in docs/PROTOCOL.md (HTTP/1.1 POST /rpc on 127.0.0.1, JSON-RPC-ish body, token header, error codes)
- [x] 11. Mod: Winsock listener thread on 127.0.0.1 (port from settings, fallback to ephemeral), minimal HTTP parser
- [x] 12. Mod: random token + port written to `<mod save dir>/bridge.json`; reject requests without it
- [x] 13. Mod: main-thread dispatcher (queue -> promise, timeout) + command registry; `ping` command
- [x] 14. Mod: `status` command (scene, editor open, level name/ID, object count, GD/Geode/mod versions)

## M3 — Python MCP server
- [x] 15. server/ package skeleton (pyproject, `gd-bridge-mcp` entry point, FastMCP stdio, Python >= 3.10)
- [x] 16. Bridge client: discover bridge.json, token auth, timeouts, clear "GD not running / mod not loaded" errors
- [x] 17. Mock bridge (in-process fake mod) + pytest suite running against it; add a Python CI job
- [x] 18. Tool: `status`
- [x] 19. README: one-command pip install + Claude desktop config snippet (acceptance 3)

## M4 — Level string read/write + safety
- [x] 20. Research: LevelEditorLayer / GJGameLevel bindings for 2.2081 (getLevelString, createObjectsFromString, removeAllObjects)
- [x] 21. Mod: `get_level_string`
- [x] 22. Mod: backup store (`<save dir>/backups/<level>/<timestamp>.txt`, rotation) used by every write command
- [x] 23. Mod: safety guard — writes only if level name starts with "CLAUDE " or `confirm_name` matches exactly
- [x] 24. Mod: `set_level_string` (backup -> clear -> load)
- [x] 25. MCP tools: `get_level_string`, `set_level_string` (+ tests on mock)

## M5 — Objects
- [x] 26. Shared object model: dict of GD keys <-> object; reuse toolkit/gdlib key names in the server
- [x] 27. Mod: `add_objects` (batch, from object-string fragments)
- [x] 28. Mod: object selectors (by uid, object id, group, region) shared by remove/modify/list
- [x] 29. Mod: `remove_objects`
- [x] 30. Mod: `modify_objects` (position, rotation, scale, groups, colour, raw keys)
- [x] 31. Mod: `list_objects` (filters, paging) and `get_triggers(type)`
- [x] 32. MCP tools for M5 with friendly arguments (names like "spike", "move_trigger") + tests

## M6 — Camera + screenshots
- [x] 33. Research: editor camera (EditorUI / m_objectLayer position + scale), CCRenderTexture -> PNG in v5
- [x] 34. Mod: `move_camera(x, y, zoom)` and `get_camera`
- [x] 35. Mod: `screenshot` (current view or region; hide editor UI optionally) -> PNG file + base64
- [x] 36. MCP tools `move_camera`, `screenshot` (returns an MCP image)

## M7 — Playtest + frame capture
- [x] 37. Research: editor playtest API (onPlaytest/onStopPlaytest, start from x / start pos)
- [x] 38. Mod: `playtest(start|stop, from_x?)`
- [x] 39. Mod: `capture_frames(n, interval)` during playtest (async job, poll for results)
- [x] 40. MCP tools `playtest`, `capture_frames` (returns images)

## M8 — Level management + music
- [x] 41. Research: saving from the editor, LocalLevelManager, creating/opening levels by name in 2.2081
- [x] 42. Mod: `save_level`
- [x] 43. Mod: `create_level(name, song_id)` (forces "CLAUDE " prefix) and `open_level(name)`
- [x] 44. Mod: `get_music` (song ID, offset, guidelines/BPM if set)
- [x] 45. MCP tools for M8

## M9 — Undo/redo + backups
- [x] 46. Mod: `undo`, `redo`
- [x] 47. Mod: `list_backups`, `restore_backup` (restore itself backs up first)
- [x] 48. MCP tools for M9

## M10 — End-to-end + docs
- [ ] 49. tests/e2e_bridge.py: create "CLAUDE test", add blocks/spikes/orb/move trigger, read back, screenshot, playtest 3 s with frames, save (acceptance 4)
- [ ] 50. TESTING.md: how to run the e2e test and what to report
- [ ] 51. [blocked: Distanax] Run the e2e test and report
- [ ] 52. CLAUDE.md: every tool with examples + known limits (acceptance 5)
- [ ] 53. Tag v1.0.0 release; delete the "gd-bridge continue" routine once acceptance 2 and 4 are confirmed
