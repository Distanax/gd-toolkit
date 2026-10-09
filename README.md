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
