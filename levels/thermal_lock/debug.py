"""Print the simulated path and nearby objects around a death (or any x): py levels/thermal_lock/debug.py [x]"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build as B
from toolkit import gdsim

w, tl = B.build()
x_end = tl.xb(B.SECTIONS[-1].b1) + 200
lvl = gdsim.Level(solids=w.solids, hazards=w.hazards, portals=w.portals)
p, rows = gdsim.simulate(lvl, sorted(w.inputs), x_end, trace=True)
xd = float(sys.argv[1]) if len(sys.argv) > 1 else (p.death_x or 0)
print("dead" if p.dead else "alive", "death_x", p.death_x, "mode", p.mode, "y", round(p.y, 1), "vy", round(p.vy, 2), "g", p.g)
for r in rows:
    if xd - 120 <= r[0] <= xd + 5 and int(r[0]) % 6 < 2:
        print(f"  x {r[0]:8.1f} y {r[1]:7.1f} vy {r[2]:7.2f} {r[3]} g{r[4]} gnd {r[5]}")
print("inputs near:", [e for e in sorted(w.inputs) if xd - 400 <= e[0] <= xd + 50])
print("solids near:", sorted((round(s.x), round(s.y)) for s in w.solids if abs(s.x - xd) < 120))
print("hazards near:", sorted((round(h[0]), round(h[1])) for h in w.hazards if abs(h[0] - xd) < 120))
