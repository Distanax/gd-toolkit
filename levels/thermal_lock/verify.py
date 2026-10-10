"""Run the built level's input script in real GD (gd-bridge autoplay) and compare GD's trajectory with
gdsim's. With Mega Hack noclip on, GD never kills the player, so the real trace is also checked against
the level's hazards/solids offline ("would have died here").  py levels/thermal_lock/verify.py [from_beat]"""
import bisect, json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "server" / "src")); sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build as B
from toolkit import gdsim
from gd_bridge_mcp.client import BridgeClient

w, tl = B.build()
x_end = tl.xb(B.SECTIONS[-1].b1)
b = BridgeClient()
st = b.call("status")
assert st.get("in_editor") and st["level"]["name"] == "CLAUDE Thermal Lock", st
b.call("autoplay", inputs=[[x, p] for x, p in sorted(w.inputs)], trace_every=2, stop_on_death=True)
b.call("playtest", action="start")
secs = B.bt(B.SECTIONS[-1].b1) + 3
time.sleep(secs)
res = b.call("autoplay_status", trace=True)
b.call("playtest", action="stop"); b.call("autoplay_clear")
real = res["trace"]
(ROOT / "out" / "thermal_lock_real.json").write_text(json.dumps(res), encoding="utf-8")
lvl = gdsim.Level(solids=w.solids, hazards=w.hazards, portals=w.portals)
_, sim = gdsim.simulate(lvl, sorted(w.inputs), x_end, trace=True)
sx = [r[0] for r in sim]
worst = []
for r in real:
    j = bisect.bisect_left(sx, r[0])
    if 0 < j < len(sim):
        worst.append((abs(sim[j][1] - r[1]), r[0], r[1], sim[j][1]))
worst.sort(reverse=True)
errs = sorted(e[0] for e in worst)
print(f"real run: deaths {res['deaths']} max_x {res['max_x']:.0f} of {x_end:.0f}; events {res['next_event']}/{res['events']}")
print(f"y error vs sim: median {errs[len(errs)//2]:.2f} p95 {errs[int(len(errs)*.95)]:.2f} max {errs[-1]:.2f}")
for e in worst[:5]:
    sec = next((s.name for s in B.SECTIONS if tl.xb(s.b0) <= e[1] < tl.xb(s.b1)), "?")
    print(f"   largest gap at x={e[1]:.0f} ({sec}): real y {e[2]:.1f} sim y {e[3]:.1f}")
# would-have-died check on the REAL path (noclip hides deaths)
hits = []
for r in real:
    x, y, mode = r[0], r[1], r[3]
    h = gdsim.WAVE_HALF if mode == 4 else gdsim.PLAYER_HALF
    for hx, hy, hw, hh in w.hazards:
        if abs(hx - x) < hw + h and abs(hy - y) < hh + h:
            hits.append((x, y, "hazard")); break
print("real path touches hazards at:", hits[:5] if hits else "none")
