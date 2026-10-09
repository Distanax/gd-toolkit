# gd-toolkit

Claude + Distanax toolkit for building Geometry Dash levels from code.

Workflow: generate `.gmd` -> `C:\Work\ClaudeProjects\gd_levels\` -> import with GDShare -> playtest.

| Path | Purpose |
|---|---|
| `toolkit/gdlib.py` | Level builder: objects, colours, level string, `.gmd` export (GDShare import format) |
| `toolkit/gdphys.py` | Exact GD physics constants (from decompiled 2.2 code + OpenGD) |
| `toolkit/trajgen.py` | Trajectory-first cube generator: script inputs on beats, terrain is built around the path |
| `toolkit/sim2.py` | Cube simulator (gravity flips, orbs, pads) for checking layouts and timing windows |
| `toolkit/sim.py` | Older simulator (no flips/blue orbs) + preview renderer |
| `toolkit/gdparse.py` | `.gmd` reader (decodes level strings) |
| `levels/thermal_lock/heatseeker.py` | "Thermal Lock" level (Creo - Heatseeker, 127 BPM) built section by section |
| `analysis/analyze_refs.py`, `analysis/render_ref.py` | Analysis and strip renders of rated reference levels |
| `tests/smoke_test.py` | Calibration level (coordinates, object IDs) |
| `docs/NOTES.md` | Running notes: song map, physics, decisions, open issues |

## gd-bridge: live editor control (mod + MCP server)

`mod/` is a Geode mod that exposes the GD editor on `127.0.0.1`; `server/` is an MCP server that
lets Claude drive it (status, read/replace level strings, add/remove/modify objects, screenshots,
playtests, saving). Protocol: `docs/PROTOCOL.md`. Tool reference: `CLAUDE.md`.

1. **Mod:** install `distanax.gd-bridge.geode` from the
   [latest release](https://github.com/Distanax/gd-toolkit/releases/tag/latest) — step by step in
   `TESTING.md`, section 1.
2. **MCP server** (Python 3.10+), one command:
   ```
   py -m pip install "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"
   ```
   Upgrade later with the same command plus `--upgrade`. (`py -m pip` installs into the same Python
   that `py -m gd_bridge_mcp` below runs; plain `pip install ...` works too if that's your default.)
3. **Claude desktop config** — add to `%APPDATA%\Claude\claude_desktop_config.json`
   (Settings -> Developer -> Edit Config), then restart Claude:
   ```json
   {
     "mcpServers": {
       "gd-bridge": {
         "command": "py",
         "args": ["-m", "gd_bridge_mcp"]
       }
     }
   }
   ```
   `py -m gd_bridge_mcp` works whether or not Python's `Scripts` folder is on PATH. If `gd-bridge-mcp` is on PATH, `"command": "gd-bridge-mcp"`
   with no `args` works too. For Claude Code: `claude mcp add gd-bridge -- py -m gd_bridge_mcp`.
   No token or port goes in the config: the server reads them from the `bridge.json` file the mod
   writes each time GD starts.

Safety: only levels named `CLAUDE ...` can be modified unless a call passes `confirm_name` with the
exact level name; every write backs the level up first (`%LOCALAPPDATA%\GeometryDash\geode\mods\
distanax.gd-bridge\backups\`); nothing is ever uploaded.

## Setup and running

Run everything from the repo root (Python 3.11+):

```
pip install -r requirements.txt
python toolkit/gdphys.py                       # physics sanity table
python levels/thermal_lock/heatseeker.py       # simulate Section 1, write out/s1_preview.png + out/thermal_lock_s1.gmd
python tests/smoke_test.py                     # write out/claude_calibration.gmd
python analysis/analyze_refs.py [REFS_DIR]     # default refs/
python analysis/render_ref.py LEVEL.gmd T0 T1 OUT.png
```

Generated files go to `out/` (git-ignored); copy a `.gmd` into `gd_levels` to import it.
Reference levels belong to other creators and are not in the repo: copy
`gd_levels\ref_*.gmd` into `refs/` (git-ignored) to run the analysis scripts.
