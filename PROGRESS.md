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

## Next
- Task 5: GitHub Actions build, get it green.

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
- **Python MCP server uses the official `mcp` SDK (FastMCP, stdio)**, installed via
  `pip install "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"`.
- **SDK pin lives in mod.json** (`"geode": "5.10.1"`): build-geode-mod's `sdk` input defaults to
  `given`, i.e. the version in mod.json, so CI and the mod can't disagree.
- **A mock bridge** lets the Python side be built and tested without GD running.

## Open questions
- (resolved) GD version is 2.2081, matching Geode v5.10.1.
