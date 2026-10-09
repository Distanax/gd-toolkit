"""Live checks for the gd-bridge tools that tests/e2e_bridge.py doesn't cover.

Run AFTER tests/e2e_bridge.py (it expects the "CLAUDE test" layout that script builds), with GD open
and "CLAUDE test" in the editor:
    py tests/e2e_extra_bridge.py
Covers get_music, modify_objects (move + raw key), undo/redo (runs only; see CLAUDE.md limits),
list_backups + restore_backup, playtest from_x (temporary start pos appears and is removed) + frames,
set_level_string reload, switching levels from inside the editor ("CLAUDE switch test" is created
once and reused), and the not_found refusal. Touches only CLAUDE levels.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "server" / "src"))
import time
from gd_bridge_mcp.client import BridgeClient, BridgeError

b = BridgeClient()
results = []


def check(name, ok, detail=None):
    results.append((name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok else f" - {detail}"))


def orb():
    objs = b.call("list_objects", select={"ids": [36]})["objects"]
    return (objs[0]["x"], objs[0]["y"]) if objs else None


st = b.call("status")
assert st["in_editor"] and st["level"]["name"] == "CLAUDE test", st
n0 = st["level"]["object_count"]

m = b.call("get_music")
check("get_music", "song_id" in m and "guidelines" in m, m)

start = orb()
check("orb at its e2e position", start == (720, 105), start)

r = b.call("modify_objects", select={"ids": [36]}, move={"dx": 30, "dy": 30}, set={"6": "45"})
after = orb()
check("modify_objects move (level coords)", after == (750, 135), after)
s = b.call("list_objects", select={"ids": [36]}, object_strings=True)["objects"][0]["object_string"].split(",")
check("modify_objects set rotation key 6", dict(zip(s[::2], s[1::2])).get("6") == "45", s)

# undo/redo: only check they run and GD survives (undo on tool edits is documented as inconsistent;
# restore_backup below puts the level back exactly).
u = b.call("undo"); r = b.call("redo")
check("undo/redo run, GD alive", b.call("status")["in_editor"], (u, r))

bk = b.call("list_backups", limit=10)["backups"]
mod_backup = next((x["file"] for x in bk if x["file"].endswith("_modify_objects.txt")), None)
check("list_backups has the modify_objects backup", mod_backup is not None, [x["file"] for x in bk])
if mod_backup:
    b.call("restore_backup", file=mod_backup)
    time.sleep(2.5)  # editor reloads
    st = b.call("status")
    check("restore_backup reloads the pre-modify level", orb() == start and st["level"]["object_count"] == n0,
          (orb(), st["level"]["object_count"]))

# playtest from x: temporary start position must appear during and vanish after.
p = b.call("playtest", action="start", from_x=600)
time.sleep(1.0)
sp_during = b.call("list_objects", select={"ids": [31]})["total"]
check("playtest from_x places a temporary start pos", p["temp_start_pos"] and sp_during == 1, (p, sp_during))
job = b.call("capture_frames", count=2, interval_ms=300)["job"]
for _ in range(40):
    js = b.call("job_status", job=job)
    if js["state"] != "running":
        break
    time.sleep(0.25)
check("frames from x=600", js["state"] == "done" and len(js["frames"]) == 2, js)
b.call("playtest", action="stop")
time.sleep(0.5)
sp_after = b.call("list_objects", select={"ids": [31]})["total"]
check("temporary start pos removed after stop", sp_after == 0, sp_after)
check("playtest stopped", b.call("status")["playtest"] == "not")

# set_level_string: whole-level replace + editor reload (the path that crashed before 1.0.1)
ls = b.call("get_level_string")["level_string"]
header = ls.split(";")[0]
b.call("set_level_string", level_string=header + ";1,1,2,15,3,15;1,8,2,75,3,15;")
st = b.call("status")
check("set_level_string reloads with 2 objects", st["in_editor"] and st["level"]["object_count"] == 2, st)
b.call("set_level_string", level_string=ls)  # put the e2e layout back
check("set_level_string restores the full layout", b.call("status")["level"]["object_count"] == n0)

# switching levels from inside the editor (the other crash path): CLAUDE test -> scratch level -> back
names = [lv["name"] for lv in b.call("list_levels", claude_only=True)["levels"]]
if "CLAUDE switch test" not in names:
    b.call("create_level", name="switch test")
else:
    b.call("open_level", name="CLAUDE switch test")
st = b.call("status")
check("switch from editor to another CLAUDE level", st["in_editor"] and st["level"]["name"] == "CLAUDE switch test", st)
b.call("open_level", name="CLAUDE test")
st = b.call("status")
check("switch back to CLAUDE test", st["in_editor"] and st["level"]["name"] == "CLAUDE test"
      and st["level"]["object_count"] == n0, st)

# safety: a non-CLAUDE name must be refused (no real level involved: confirm_name mismatch only)
try:
    b.call("open_level", name="Definitely Not A Level 12345")
    check("open_level unknown name refused", False)
except BridgeError as e:
    check("open_level unknown name refused", e.code == "not_found", e)

b.call("save_level")
passed = sum(ok for _, ok in results)
print(f"\n{passed}/{len(results)} passed")
sys.exit(0 if passed == len(results) else 1)
