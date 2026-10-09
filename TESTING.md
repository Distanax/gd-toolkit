# gd-bridge — testing guide for Distanax

Things only you can do in-game. Each section says exactly what to do and what to report back.
Report results by telling Claude in chat (or add a note under "Results" at the bottom and push).

## 0. Connect GitHub to claude.ai — DONE 2026-10-09 (routine created)
Creating the "gd-bridge continue" routine failed with `github_token_missing`: cloud routines need your
GitHub account connected to claude.ai so they can clone and push `Distanax/gd-toolkit`.
1. Open https://claude.ai/code in your browser and sign in.
2. When asked (or via the GitHub/repository picker), connect your GitHub account and grant access to
   the `Distanax/gd-toolkit` repository (installing the Claude GitHub app on that repo is enough).
3. Tell Claude "GitHub is connected" in chat. Claude then creates the routine (every 3 hours,
   Sonnet 5.5, Default environment, the mission prompt) and checks off task 2.

## 1. Install the mod (about 5 minutes)
Your setup (from your Geode log): Geode v5.10.1, GD 2.2081, GD in
`C:\Program Files (x86)\Steam\steamapps\common\Geometry Dash`.

1. **Close Geometry Dash** (mods load at startup).
2. **Download the mod into GD's mods folder.** Paste this into PowerShell:
   ```powershell
   Invoke-WebRequest "https://github.com/Distanax/gd-toolkit/releases/download/latest/distanax.gd-bridge.geode" -OutFile "C:\Program Files (x86)\Steam\steamapps\common\Geometry Dash\geode\mods\distanax.gd-bridge.geode"
   ```
   (Or download that link in a browser and move the file into `...\Geometry Dash\geode\mods\`.)
   Updating later is the same command: it overwrites the old file.
3. **Start GD from Steam.**
4. **Check it loaded** (any one is enough; please do all three the first time):
   - Main menu -> Geode button -> Installed: **GD Bridge** is listed and enabled.
   - Open `http://127.0.0.1:47821/health` in a browser. Expected: `{"ok":true,"protocol":1}`.
   - This file exists: `%LOCALAPPDATA%\GeometryDash\geode\mods\distanax.gd-bridge\bridge.json`
     (paste the path into Explorer's address bar). Don't share its contents: it holds the access token.
5. **Report back** in chat: "mod loads" plus anything that didn't match. If it failed, send the newest
   file from `C:\Program Files (x86)\Steam\steamapps\common\Geometry Dash\geode\logs\` (lines
   mentioning `GD Bridge` or `distanax.gd-bridge` are what matter).

Safety: the mod listens on 127.0.0.1 only (not reachable from other computers), needs the token from
`bridge.json`, only edits levels named `CLAUDE ...` unless you confirm another by exact name, backs
up before every change, and never uploads anything. Uninstall = delete the `.geode` file.

## 2. Run the end-to-end test (about 5 minutes)
This drives GD exactly the way Claude will: MCP tools -> bridge -> mod. It only ever touches a level
called **CLAUDE test** (created if missing, emptied and rebuilt if it exists).

1. **Update the mod** to the newest build: run the PowerShell command from section 1 again (with GD
   closed), then start GD. Stay on the main menu (or any screen that isn't the editor with one of your
   own levels open — the test refuses to leave those, so your unsaved work is never discarded).
2. **Install/update the MCP server** (PowerShell):
   ```powershell
   py -m pip install --upgrade "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"
   ```
3. **Run the test** (PowerShell):
   ```powershell
   cd C:\Work\ClaudeProjects\gd-toolkit-repo
   git pull
   py tests\e2e_bridge.py
   ```
4. **What you should see in GD** (about 15 seconds): the editor opens "CLAUDE test"; a row of blocks,
   two spikes, a yellow orb, a raised block and a move trigger appear; the view jumps to them for a
   screenshot; a playtest runs for about 3 seconds and stops; the level is saved.
5. **What you should see in PowerShell**: one `[PASS]`/`[FAIL]` line per step, then `ALL PASSED` or
   `FAILED` and the path of a report folder (`out\e2e\<time>\`) holding `report.json`, the screenshot
   and the playtest frames.
6. **Report back** in chat: `ALL PASSED`, or paste the `[FAIL]` lines (and `report.json` if asked).
   If GD crashed or froze, also send the newest log from `...\Geometry Dash\geode\logs\`.

Useful extra: `py tests\e2e_bridge.py --mock` runs the same script against a fake bridge with no GD at
all — if that fails too, the problem is the Python side, not the mod.

## Results
_(none yet)_
