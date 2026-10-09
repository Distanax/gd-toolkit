# gd-bridge — progress log

## Resume protocol (every session)
1. `git pull`
2. Read CLAUDE.md, this file, TASKS.md.
3. Continue with the first unchecked task that is not `[blocked: Distanax]`. Never redo checked tasks.
4. One task = one commit + push. Update this file (Status, Next, Decisions, Open questions) in the
   same commit. Never hold more than ~30 min of unpushed work.
5. If a task needs Distanax: write exact steps in TESTING.md, mark it `[blocked: Distanax]`, move on.
6. If every remaining task is done or blocked on Distanax, update this file and stop.

## Mission
Build **gd-bridge**: a Geode mod (`mod/`) + Python MCP server (`server/`) that gives Claude live
control of the Geometry Dash editor on Distanax's Windows PC. Distanax playtests; Claude does the rest.

Acceptance criteria (mission done when all are true):
1. CI builds the Windows .geode on every push to main, and a release exists.
2. TESTING.md has a 5-minute install guide, and Distanax has confirmed the mod loads in GD.
3. The MCP server installs with one pip command; its Claude desktop config snippet is in README.md.
4. `tests/e2e_*.py` creates "CLAUDE test", adds blocks, spikes, an orb and a move trigger, reads
   them back, screenshots the editor, playtests 3 s with frame capture, and saves. Distanax runs it.
5. CLAUDE.md documents every tool with examples, plus known limits.

Safety (non-negotiable): only modify levels whose name starts with `"CLAUDE "` unless the call passes
`confirm_name=<exact level name>`; never delete or overwrite Distanax's levels; every write backs
up the level string first; never upload levels online.

## Status
- 2026-10-08: Mission started. TASKS.md written (53 tasks, M0-M10).

- 2026-10-08: Task 2 blocked: routine creation returned `github_token_missing` (GitHub not connected
  to claude.ai). Steps in TESTING.md section 0. Prepared config: name "gd-bridge continue", cron
  `0 */3 * * *` (UTC), model claude-sonnet-5-5, environment Default (env_016RcFPPpmcyg8QVpaAzEvtc),
  repo Distanax/gd-toolkit, tools Bash/Read/Write/Edit/Glob/Grep/WebFetch/WebSearch, prompt = the
  mission's continue prompt plus a note that cloud runs have no PC access and must verify CI via the API.

- 2026-10-08: Task 3 done (Geode v5 layout research, notes under Environment facts).

- 2026-10-08: Task 4 done: mod/ skeleton (mod.json pins geode 5.10.1 / gd win 2.2081, CMake from
  example-mod, main.cpp logs on load). Not built yet; CI comes in task 5.

- 2026-10-09: Task 5 done: `.github/workflows/build-mod.yml` (windows-latest, build-geode-mod@main,
  path mod, Win64) green on first run (run 37879730513, 2.5 min, artifact `gd-bridge-win` 13 KB).
  Triggers: push to main touching `mod/**` or the workflow, plus manual dispatch.

- 2026-10-09: Task 6 done: release job (ubuntu, `gh release`, contents: write). Main builds recreate a
  rolling prerelease tagged `latest` on the new commit; `v*` tags get versioned releases. Verified:
  release `latest` @ d9d6881 with `distanax.gd-bridge.geode` (13 KB); stable URL
  https://github.com/Distanax/gd-toolkit/releases/download/latest/distanax.gd-bridge.geode -> 200.
  **Acceptance 1 met.**

- 2026-10-09: Task 7 done: TESTING.md section 1 (PowerShell download into `<GD>\geode\mods`, three
  load checks: Geode mod list, `/health` in a browser, bridge.json). The `/health` check needs task 11's
  build. Task 8 is blocked on Distanax.

- 2026-10-09: Task 9 done: threading, matjson, file, settings, bindings and MCP v2 notes recorded below.
- 2026-10-09: Task 10 done: docs/PROTOCOL.md: bridge.json discovery, HTTP POST /rpc + X-GD-Bridge-Token, /health, Origin rejected, error codes, main-thread execution, jobs for long work, PNGs returned as file paths, safety rules.
- 2026-10-09: Task 11 done: Winsock listener on 127.0.0.1 (port setting 47821, ephemeral fallback), /health, Origin -> 403. CI green at 1f2b6eb after one fix: Geode PCH already includes Windows.h -> winsock.h, so winsock2.h redefined sockaddr; now uses winsock.h. Added a problem matcher so compiler errors show up as public check-run annotations (raw logs need auth).
- 2026-10-09: Task 12 done: Auth.cpp: 32 random bytes (MSVC random_device = OS CSPRNG) as hex, bridge.json {protocol, port, token, pid, mod_version} written atomically to the mod save dir, constant-time token compare. Wired into main.cpp with task 13. Workflow: matcher file in path filter + concurrency group (no racing release jobs).
- 2026-10-09: Task 13 done: Rpc.cpp: command registry (BRIDGE_COMMAND macros), main-thread dispatch via queueInMainThread + promise with 10 s timeout, RpcError -> protocol error codes, param helpers. main.cpp: POST /rpc with token auth, JSON body {id, method, params} -> {id, ok, result|error}. ping runs off-thread.
- 2026-10-09: Task 14 done: status command (in commands/Core.cpp, same commit as 13): scene (first child of running scene), in_editor, in_level, playtest (not/playing/paused), level {name, id, song_id, audio_track, object_count}, versions {mod, geode, gd, protocol}.
- 2026-10-09: Task 15 done: server/ package gd-bridge-mcp 0.1.0 (hatchling, Python >= 3.10, mcp>=2.3,<3, console script gd-bridge-mcp -> MCPServer("gd-bridge").run(transport="stdio")). Committed together with 16 and 18.
- 2026-10-09: Task 16 done: client.py BridgeClient: reads bridge.json (GD_BRIDGE_FILE override, else %LOCALAPPDATA%/GeometryDash/geode/mods/distanax.gd-bridge/), POSTs /rpc with the token, re-reads bridge.json once on unauthorized/connection failure (GD restarted), maps errors to BridgeError(code). Deliberately no pid liveness check: os.kill(pid, 0) can terminate a process on Windows.
- 2026-10-09: Task 18 done: MCP tool status (returns running:false with instructions instead of an error when GD/mod is not reachable). bridge_errors decorator turns BridgeError into ToolError for every other tool.

## Next
- Task 17: mock bridge + pytest + Python CI.

## Environment facts (verified 2026-10-08)
- Distanax: Steam GD on Windows, Geode **v5.10.1** (released 2026-08-29).
- Geode v5.10.1 targets **GD 2.2081** (`GEODE_GD_VERSION` in geode-sdk/geode CMakeLists.txt at tag v5.10.1).
- CI action: `geode-sdk/build-geode-mod@main` (inputs `sdk`, `cli`, `target`, `combine`, ...);
  `sdk` accepts a version, so pin `v5.10.1`.
- Template (geode-sdk/example-mod): mod.json `"geode": "<ver>"`, `"gd": {"win": "2.2081"}`;
  CMake 3.21, C++23, `add_subdirectory($ENV{GEODE_SDK})` + `setup_geode_mod(target)`.
- **Distanax's install, read from the Geode log 2026-10-08:** "Running Geode v5.10.1 in Geometry Dash
  v2.2081 on Windows". GD lives in `C:\Program Files (x86)\Steam\steamapps\common\Geometry Dash`;
  installed mods go in `<GD>\geode\mods\`, logs in `<GD>\geode\logs\`.
- **Per-mod save dir** = `dirs::getModsSaveDir() / <mod id>` = `%LOCALAPPDATA%\GeometryDash\geode\mods\distanax.gd-bridge\`
  (Mod.cpp `m_saveDirPath`, Dirs.cpp, windows/util.cpp `dirs::getSaveDir` uses
  LOCAL_APPDATA + exe name). Verified the folder layout exists on the PC.
- **mod.json (docs.geode-sdk.org/mods/configuring):** required `geode`, `gd`, `id`, `name`, `version`,
  `developer`/`developers`. id: lowercase a-z, `.`, `_`, `-`. v5 reworked dependencies (`importance`
  removed -> `required` / `breaking`); superseding is server-side now.
- **v5 API (headers at tag v5.10.1):** `$on_mod(Loaded)` (loader/ModEvent.hpp), `geode::queueInMainThread`
  (loader/Loader.hpp), `Mod::get()->getSaveDir()` / `getSettingValue<T>(key)` (loader/Mod.hpp),
  `geode::async` (utils/async.hpp, in the prelude, `async::waitForMainThread`). C++23 required.
  `Mod::isEnabled` was renamed `isLoaded`; `geode::cast::as`, `CCARRAY_FOREACH` removed (use `CCArrayExt`).
- **Threading (task 9):** `queueInMainThread(ScheduledFunction&&)` with
  `ScheduledFunction = geode::Function<void()>` (Loader.hpp/Types.hpp). The dispatcher passes a lambda
  owning a `shared_ptr<std::promise>` and waits on the future with a timeout.
- **JSON:** Geode v5.10.1 pulls `geode-sdk/json@3.3.1` (matjson): `matjson::parse(sv)` ->
  `Result<Value, ParseError>`, `.dump(indent)`, `makeObject({{k,v}})`, `Value::array()`/`object()`,
  `push`, `contains`, `operator[]`, `isNull/isBool/isNumber/isString/isArray/isObject`,
  `asBool/asInt/asDouble/asString/asArray` -> `Result`.
- **Files:** `utils/file.hpp` `writeStringSafe` (atomic via temp file), `readString`,
  `createDirectoryAll`. `utils::string::pathToString` for UTF-8-safe paths. Logging `log::info/warn/error`.
- **Windows headers:** Geode's platform/windows.hpp includes `<Windows.h>` without
  `WIN32_LEAN_AND_MEAN`, so socket code includes `<winsock2.h>` first. Geode's CMake already links
  `ws2_32` into every mod (`target_link_libraries(... INTERFACE delayimp ws2_32)`).
- **Settings:** int setting `{type, name, description, default, min, max, requires-restart, control}`;
  read with `getSettingValue<int64_t>`.
- **Bindings 2.2081 (geode-sdk/bindings main, GeometryDash.bro)** — Windows-available (address or
  inline): `LevelEditorLayer::get()`, `getLevelString()`, `createObjectsFromString(str, noUndo, noLimit)`,
  `createObject(id, pos, noUndo)`, `removeObject(obj, noUndo)`, `removeAllObjects()`,
  `objectsInRect(rect, ignoreGroups)`, `onPlaytest()`, `onStopPlaytest()`, `undoLastAction()`,
  `redoLastAction()`, `m_editorUI`; `EditorUI::get()`, `updateZoom(float)`,
  `constrainGameLayerPosition(x,y)`, `selectObjects`, `getSelectedObjects`, `moveObject`,
  `onPlaytest/onStopPlaytest(sender)`; `GameManager::sharedState()->m_playLayer /
  m_levelEditorLayer`; `GJGameLevel::m_levelName/m_levelID (SeedValueRSV, .value())/m_songID/
  m_audioTrack/m_levelString/m_levelType (GJLevelType::Editor = 2)`; `GJBaseGameLayer::m_level,
  m_playbackMode (PlaybackMode::Not/Playing/Paused), m_objects`; `LevelEditorLayer::m_objectCount`.
- **MCP Python SDK is v2 (2.3.0, Python >= 3.10)** — v1's `FastMCP` is gone:
  `from mcp.server.mcpserver import MCPServer, Context, Image`, `mcp.run(transport="stdio")`,
  tool failures raise `ToolError` (`mcp.server.mcpserver.exceptions`), sync tools run on a worker
  thread, `Client` in `mcp` for tests. `MCP_*` env vars are no longer read. (py.sdk.modelcontextprotocol.io/migration)
- Other editor mods installed on the PC: hjfod.betteredit, hjfod.gdshare, hjfod.gmd-api,
  alphalaneous.editortab_api (possible conflicts to keep in mind; none expected).
- No local C++ toolchain on the PC; all mod builds happen in CI. Python 3.14 is installed locally.

## Decisions
- **Mod id `distanax.gd-bridge`.** Local tool, not for the Geode index.
- **Transport: minimal HTTP/1.1 on 127.0.0.1 over raw Winsock**, POST `/rpc` with a JSON body,
  token in a header. Why: no third-party C++ dependency to break in CI, debuggable with curl, trivial
  from Python's stdlib. Windows-only is fine (only target).
- **Token + port in `<mod save dir>/bridge.json`**, regenerated each GD launch; the MCP server reads it.
- **All game-state work runs on the main thread** via a queue; the socket thread waits with a timeout.
- **Safety is enforced in the mod**, so no client (MCP or otherwise) can bypass it; the MCP server
  checks too for friendlier errors.
- **Backups are written by the mod** before every write, so they happen whatever the caller is.
- **Python MCP server uses the official `mcp` SDK v2 (`MCPServer`, stdio)**, installed via
  `pip install "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"`.
- **SDK pin lives in mod.json** (`"geode": "5.10.1"`): build-geode-mod's `sdk` input defaults to
  `given`, i.e. the version in mod.json, so CI and the mod can't disagree.
- **A mock bridge** lets the Python side be built and tested without GD running.

## Open questions
- (resolved) GD version is 2.2081, matching Geode v5.10.1.
