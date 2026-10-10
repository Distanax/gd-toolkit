"""Thermal Lock — full-level builder (layout pass).

Trajectory-first: each section scripts its inputs on the beat grid, simulates the exact path with
toolkit/gdsim.py (calibrated against the real engine), and places structure around that path with
safety margins. The whole level is then re-simulated with full collision, and every input's timing
window is measured by moving that input alone earlier/later until the run fails.

    py levels/thermal_lock/build.py          # build + check, write out/thermal_lock.json
    py levels/thermal_lock/build.py --push   # also load it into "CLAUDE Thermal Lock" via gd-bridge

Song: Creo - Heatseeker (NG 1502369), 127 BPM, first beat 0.055 s, downbeats on beat index 2 mod 4.
"""
from __future__ import annotations

import copy
import json
import math
import pathlib
import sys
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from toolkit import gdsim  # noqa: E402
from toolkit.gdlib import BLOCK, SPIKE, Level as GdLevel  # noqa: E402

BPM = 127.0
BEAT = 60.0 / BPM
T0 = 0.055
SONG_ID = 1502369


def bt(b: float) -> float:
    return T0 + b * BEAT


PORTAL_ID = {"cube": 12, "ship": 13, "ball": 47, "ufo": 111, "wave": 660, "spider": 1331, "swing": 1933}
SPEED_ID = {0.5: 200, 1: 201, 2: 202, 3: 203, 4: 1334}
SPEED_KIND = {0.5: "speed0.5", 1: "speed1", 2: "speed2", 3: "speed3", 4: "speed4"}


@dataclass
class World:
    objs: list[str] = field(default_factory=list)
    solids: list[gdsim.Solid] = field(default_factory=list)
    hazards: list[tuple[float, float, float, float]] = field(default_factory=list)
    portals: list[tuple[float, float, str]] = field(default_factory=list)
    inputs: list[tuple[float, bool]] = field(default_factory=list)
    clicks: list[float] = field(default_factory=list)  # x of each deliberate press (for windows)
    notes: list[str] = field(default_factory=list)

    def block(self, x: float, y: float, **keys) -> None:
        self.objs.append(_obj(BLOCK, x, y, keys))
        self.solids.append(gdsim.Solid(x, y))

    def spike(self, x: float, y: float, flip: bool = False) -> None:
        self.objs.append(_obj(SPIKE, x, y, {"6": 180} if flip else {}))
        hw, hh = gdsim.SPIKE_HALF
        # spike hitbox sits in the lower part of the tile (pointing up) / upper part when flipped
        self.hazards.append((x, y + (2 if flip else -2), hw, hh))

    def portal(self, x: float, y: float, kind: str) -> None:
        oid = PORTAL_ID.get(kind) or SPEED_ID[{v: k for k, v in SPEED_KIND.items()}[kind]]
        self.objs.append(_obj(oid, x, y, {}))
        self.portals.append((x, y, kind))

    def press(self, x: float) -> None:
        self.inputs.append((x, True))
        self.clicks.append(x)

    def release(self, x: float) -> None:
        self.inputs.append((x, False))

    def tap(self, x: float, length: float = 6.0) -> None:
        self.press(x)
        self.release(x + length)


def _obj(oid: int, x: float, y: float, keys: dict) -> str:
    s = f"1,{oid},2,{_f(x)},3,{_f(y)}"
    for k, v in keys.items():
        s += f",{k},{_f(v)}"
    return s


def _f(v: float) -> str:
    v = round(float(v), 2)
    return str(int(v)) if v == int(v) else str(v)


def snap(v: float, step: float = 15.0) -> float:
    return round(v / step) * step


# ---------------------------------------------------------------- timeline
@dataclass
class Section:
    name: str
    b0: float           # start beat (bar downbeat)
    b1: float           # end beat
    mode: str
    speed: float
    gen: str            # generator name
    params: dict = field(default_factory=dict)


SECTIONS = [
    Section("intro", 0, 38, "cube", 1, "cube", dict(pattern="intro")),
    Section("drop1a", 38, 70, "cube", 2, "cube", dict(pattern="drop")),
    Section("drop1b", 70, 102, "ship", 2, "ship", dict(pattern="melodic")),
    Section("groove", 102, 130, "ball", 1, "ball", dict(pattern="groove")),
    Section("build", 130, 166, "ufo", 1, "ufo", dict(pattern="build")),
    Section("predrop", 166, 174, "cube", 1, "cube", dict(pattern="breather")),
    Section("drop2a", 174, 206, "wave", 2, "wave", dict(pattern="climax")),
    Section("drop2b", 206, 234, "spider", 2, "spider", dict(pattern="drop2")),
    Section("ending", 234, 246, "cube", 1, "cube", dict(pattern="ending")),
]


class Timeline:
    """x(t) from the section speeds (speed portals at each section's start)."""

    def __init__(self, sections: list[Section]):
        self.points = []  # (t, x, speed)
        x = 0.0
        for s in sections:
            t = bt(s.b0) if s.b0 > 0 else 0.0
            if self.points:
                pt, px, ps = self.points[-1]
                x = px + gdsim.x_speed(ps) * (t - pt)
            self.points.append((t, x, s.speed))

    def x(self, t: float) -> float:
        pt, px, ps = self.points[0]
        for p in self.points:
            if p[0] <= t:
                pt, px, ps = p
        return px + gdsim.x_speed(ps) * (t - pt)

    def xb(self, b: float) -> float:
        return self.x(bt(b))


# ---------------------------------------------------------------- generators
GROUND = 15.0  # player centre on the ground


def arc(speed: float, x0: float, y0: float, g: int, vy0: float, target_y: float, mode: str = "cube"):
    """Free flight from (x0, y0) with vy0 until the player centre comes back down through target_y.
    Returns the list of (x, y) points (one per physics step) and the landing x (or None)."""
    ps, sm, _, grav = gdsim.SPEED[speed]
    gg = grav if mode == "cube" else gdsim.FLY_G * 0.6
    x, y, vy, pts = x0, y0, vy0, []
    for _ in range(2400):
        x += ps * sm * gdsim.HSTEP
        vy -= g * gg * gdsim.VSTEP
        vy = max(-gdsim.TERMINAL, min(gdsim.TERMINAL, vy))
        y += vy * gdsim.VSTEP
        pts.append((x, y))
        if (vy * g < 0) and (y - target_y) * g <= 0:
            return pts, x
    return pts, None


def platform(w: World, x_a: float, x_b: float, top: float, g: int = 1) -> None:
    """One-block-thick platform whose surface is `top` (surface y), covering [x_a, x_b]."""
    yc = top - 15 if g == 1 else top + 15
    c = snap(x_a - 15, 30) + 15
    if c - 15 > x_a:
        c -= 30
    while c - 15 < x_b:
        w.block(c, yc)
        c += 30


def spike_carpet(w: World, x_a: float, x_b: float, path, clear: float = 40.0) -> None:
    """Ground spikes under an airborne stretch wherever the player's bottom clears them by `clear`."""
    c = snap(x_a, 30) + 15
    while c < x_b:
        ys = [y for x, y in path if abs(x - c) <= 22]
        if ys and min(ys) - 15 >= 30 + clear:
            w.spike(c, 15)
        c += 30


def gen_cube(w: World, s: Section, tl: Timeline) -> None:
    """Hops between floating platforms; jumps on chosen beats with chosen landing heights."""
    speed = s.speed
    pat = s.params["pattern"]
    # (beat offset from section start, landing surface height in blocks above ground)
    # Rule: jumps on consecutive beats always climb one block (a higher landing comes sooner); a
    # two-beat jump may drop. Strong beats (bar starts, db % 4 == 0) carry the big drops.
    if pat == "intro":
        jumps = [(6, 1), (8, 1), (10, 2), (12, 2), (14, 1), (16, 1), (18, 2), (20, 3), (22, 2), (24, 1),
                 (25, 2), (26, 3), (28, 2), (30, 1), (31, 2), (32, 3), (34, 2), (36, 0)]
    elif pat == "drop":
        jumps = [(0, 1), (2, 1), (3, 2), (4, 3), (6, 2), (8, 1), (9, 2), (10, 3), (12, 2), (14, 1), (15, 2),
                 (16, 3), (18, 2), (20, 1), (21, 2), (22, 3), (24, 2), (26, 1), (27, 2), (28, 3), (30, 0)]
    elif pat == "breather":
        jumps = [(2, 1), (4, 1), (6, 0)]
    else:  # ending
        jumps = [(2, 1), (4, 1), (6, 2), (8, 1), (10, 0)]
    _cube_hops(w, s, tl, jumps)


def _cube_hops(w: World, s: Section, tl: Timeline, jumps) -> None:
    speed = s.speed
    ps, sm, ystart, grav = gdsim.SPEED[speed]
    xs = gdsim.x_speed(speed)
    early = 0.12 * xs   # platform starts this far before the planned landing (early-jump margin)
    late = 0.10 * xs    # and ends this far after the takeoff point (late-jump margin)
    x_start = tl.xb(s.b0)
    surf = 0.0           # current surface height (0 = the ground)
    stand_from = x_start
    for k, (db, land_blocks) in enumerate(jumps):
        xj = tl.xb(s.b0 + db)
        # platform under the current stretch (the ground needs none)
        if surf > 0:
            platform(w, stand_from, xj + late, surf)
        w.tap(xj)
        # the landing must happen well before the next click (else the click is wasted mid-air):
        # if it doesn't, land one block higher (shorter fall), up to +2 blocks
        x_next = tl.xb(s.b0 + jumps[k + 1][0]) if k + 1 < len(jumps) else None
        buffer = 0.03 * xs
        for extra in (0, 1, 2, -1):
            target = max(0, land_blocks + extra) * 30.0
            if target - surf > 60:  # can't rise more than 2 blocks
                continue
            pts, xl = arc(speed, xj, surf + 15, 1, ystart, target + 15)
            if xl is not None and (x_next is None or xl + buffer <= x_next):
                break
        else:
            raise RuntimeError(f"{s.name}: jump at beat {s.b0 + db} can't land before the next click")
        if extra:
            w.notes.append(f"{s.name}: beat {s.b0 + db} landing moved {land_blocks}->{int(target // 30)} blocks")
        # platform must start where the arc is already above its surface (no side hit)
        above = [x for x, y in pts if y - 15 >= target + 4]
        x_up = above[0] if above else xj
        stand_from = max(x_up + 8, xl - early) if target > 0 else xl
        spike_carpet(w, xj + late + 15, xl - early - 15, pts)
        surf = target
    # last stretch to the section end on whatever surface we're on
    if surf > 0:
        platform(w, stand_from, tl.xb(s.b1) + 30, surf)


def gen_tunnel(w: World, s: Section, tl: Timeline, holds, margin: float, thin: bool = True) -> None:
    """Flying modes: script holds/taps, simulate the free path in the corridor, build a tunnel around
    it (walls `margin` units from the path's extent in each 30-unit column)."""
    x0, x1 = tl.xb(s.b0), tl.xb(s.b1)
    for item in holds:
        if item[0] == "hold":
            _, b_on, b_off = item
            w.press(tl.xb(s.b0 + b_on))
            w.release(tl.xb(s.b0 + b_off))
        else:
            w.tap(tl.xb(s.b0 + item[1]))
    # simulate this section alone: player enters at the floor in this mode
    lvl = gdsim.Level(portals=[(x0, 45.0, s.mode)])
    start = gdsim.Player(x=x0 - 40, y=GROUND, mode="cube", speed=s.speed)
    ev = [(x, p) for x, p in w.inputs if x0 - 1 <= x <= x1 + 1]
    p, rows = gdsim.simulate(lvl, ev, x1, start=start, trace=True)
    half = gdsim.WAVE_HALF if s.mode == "wave" else gdsim.PLAYER_HALF
    ceil = gdsim.CORRIDOR.get(s.mode, 10) * 30
    c = snap(x0 + 90, 30) + 15  # leave the portal entry open
    while c < x1 - 60:
        ys = [y for x, y, *_ in rows if abs(x - c) <= 15 + half]
        if ys:
            lo = min(ys) - half - margin   # wall top below the path
            hi = max(ys) + half + margin   # wall bottom above the path
            if lo >= 30:
                w.block(c, snap(lo - 15, 15))
            if hi <= ceil - 30:
                w.block(c, snap(hi + 15, 15))
        c += 30


def gen_ship(w: World, s: Section, tl: Timeline) -> None:
    # melodic: long smooth holds on half-bars, quick corrections on beats
    # last bar has no input: the ship settles on the floor before the next portal
    holds = []
    for bar in range(0, 28, 4):
        holds += [("hold", bar + 0.0, bar + 1.5), ("hold", bar + 2.0, bar + 2.6), ("hold", bar + 3.0, bar + 3.5)]
    gen_tunnel(w, s, tl, holds, margin=50)


def gen_ufo(w: World, s: Section, tl: Timeline) -> None:
    # build: clicks get denser bar by bar (quarters -> eighths), climbing then dropping on bar ends
    taps = []
    for bar in range(0, 32, 4):  # last bar: no clicks, the UFO falls to the floor
        dens = 1.0 if bar < 12 else 0.5
        b = bar
        while b < bar + 3:
            taps.append(("tap", b))
            b += dens
    gen_tunnel(w, s, tl, taps, margin=45)


def gen_wave(w: World, s: Section, tl: Timeline) -> None:
    # climax zigzag: switch direction on every beat, eighths in the last bar of each phrase
    holds = []
    up = True
    b = 0.0
    while b < 27:  # last bar released: the wave slides down to the floor
        step = 0.5 if (b % 8) >= 6 else 1.0
        if up:
            holds.append(("hold", b, b + step))
        up = not up
        b += step
    gen_tunnel(w, s, tl, holds, margin=55)


def flip_time(speed: float, mode: str, gap: float) -> float:
    """Seconds for a ball/spider click to carry the player across `gap` units of free space."""
    if mode == "spider":
        return 0.0
    ystart = gdsim.SPEED[speed][2]
    v, d, n = ystart * 0.3, 0.0, 0
    while d < gap and n < 2000:
        v += gdsim.FLY_G * 0.6 * gdsim.VSTEP
        d += v * gdsim.VSTEP
        n += 1
    return n / gdsim.STEPS_PER_S


def flip_hops(w: World, s: Section, tl: Timeline, plan) -> None:
    """Ball/spider: plan = [(beat offset, floor_blocks, ceil_blocks)] — at each click the player flips to
    the other side; floor/ceiling surfaces (in blocks above the ground) are platforms placed under/over
    the landing stretch. The gap is checked so every flip lands before the next click."""
    speed, mode = s.speed, s.mode
    xs = gdsim.x_speed(speed)
    x0, x1 = tl.xb(s.b0), tl.xb(s.b1)
    side = 1                  # 1 = on a floor surface, -1 = on a ceiling surface
    cur_floor, cur_ceil = 0, None
    seg_start = x0
    for k, (db, fl, cl) in enumerate(plan):
        xc = tl.xb(s.b0 + db)
        x_next = tl.xb(s.b0 + plan[k + 1][0]) if k + 1 < len(plan) else x1
        # surface we stand on until this click
        if side == 1 and cur_floor > 0:
            platform(w, seg_start, xc + 0.10 * xs, cur_floor * 30)
        if side == -1:
            platform(w, seg_start, xc + 0.10 * xs, cur_ceil * 30, g=-1)
        w.tap(xc)
        gap = (cl - fl) * 30 - 30
        t = flip_time(speed, mode, gap)
        if t + 0.03 > (x_next - xc) / xs:
            raise RuntimeError(f"{s.name}: flip at beat {s.b0 + db} needs {t:.2f}s, next click too soon")
        x_land = xc + t * xs
        seg_start = x_land - 0.10 * xs
        side = -side
        cur_floor, cur_ceil = fl, cl
        # spikes on the surface the player just left, between landings (the "don't stay" hazard)
        if side == -1:  # now on the ceiling: floor spikes under the flight + stay
            c = snap(xc + 0.25 * xs, 30) + 15
            while c < x_next - 0.25 * xs:
                if fl == 0:
                    w.spike(c, 15)
                c += 30
    end_surface = cur_floor * 30 if side == 1 else cur_ceil * 30
    if side == 1 and cur_floor > 0:
        platform(w, seg_start, x1 + 30, end_surface)
    if side == -1:
        raise RuntimeError(f"{s.name}: ends on the ceiling (odd click count)")


def gen_ball(w: World, s: Section, tl: Timeline) -> None:
    # groove: flips on beats; lanes 4-5 blocks apart so a flip (~0.3 s) fits between beats;
    # on the "and" of beat 2 in odd bars a quick double flip on a 3-block lane
    plan = []
    for bar in range(0, 24, 4):
        if bar % 8 == 0:
            plan += [(bar + 1, 0, 5), (bar + 2, 0, 5), (bar + 3, 1, 5), (bar + 4, 1, 5)]
        else:  # quick double flip on a tight 3-block lane (half-beat flips need <= 3 blocks)
            plan += [(bar + 1, 0, 5), (bar + 2, 1, 4), (bar + 2.5, 1, 4), (bar + 3, 0, 5)]
    if len(plan) % 2:
        plan.append((plan[-1][0] + 1, 0, 4))
    flip_hops(w, s, tl, plan)


def gen_spider(w: World, s: Section, tl: Timeline) -> None:
    # drop 2b: teleports on every beat; lane heights step with the music, wider on bar starts
    plan = []
    for b in range(1, 25):
        strong = (s.b0 + b) % 4 == 2
        plan.append((b, 0 if strong else 1, 6 if strong else 4 + (b % 2)))
    if len(plan) % 2:
        plan.append((25, 0, 5))
    flip_hops(w, s, tl, plan)


GENERATORS = {"cube": gen_cube, "ship": gen_ship, "ufo": gen_ufo, "wave": gen_wave, "ball": gen_ball,
              "spider": gen_spider}


# ---------------------------------------------------------------- assembly + checks
def build() -> tuple[World, Timeline]:
    tl = Timeline(SECTIONS)
    w = World()
    for i, s in enumerate(SECTIONS):
        x0 = tl.xb(s.b0) if s.b0 > 0 else 0.0
        if i > 0:
            prev = SECTIONS[i - 1]
            if s.speed != prev.speed:
                w.portal(x0, 45.0, SPEED_KIND[s.speed])
            if s.mode != prev.mode:
                w.portal(x0, 45.0, s.mode)
        GENERATORS[s.gen](w, s, tl)
        w.notes.append(f"{s.name}: beats {s.b0}-{s.b1}, x {x0:.0f}-{tl.xb(s.b1):.0f}, {s.mode} {s.speed}x")
    return w, tl


def simulate_world(w: World, x_end: float, inputs=None, start=None):
    lvl = gdsim.Level(solids=w.solids, hazards=w.hazards, portals=w.portals)
    return gdsim.simulate(lvl, sorted(inputs or w.inputs), x_end, start=start)


def windows(w: World, x_end: float, step_ms: float = 8.0, max_ms: float = 160.0):
    """For each deliberate press: how far (ms) it can move earlier/later alone before the run dies
    within the next ~1.5 s. Uses state snapshots so each trial only simulates a short stretch."""
    base = sorted(w.inputs)
    lvl = gdsim.Level(solids=w.solids, hazards=w.hazards, portals=w.portals)
    # snapshots: player state just before each input event
    snaps = {}
    p = gdsim.Player()
    i, pressed = 0, False
    while p.x < x_end and not p.dead:
        while i < len(base) and p.x >= base[i][0]:
            snaps.setdefault(i, copy.deepcopy(p))
            pressed = base[i][1]
            i += 1
        gdsim.step(p, lvl, pressed)
    if p.dead:
        return None, p.death_x
    out = []
    for k, (xk, pk) in enumerate(base):
        if not pk:
            continue
        st = snaps.get(k - 1) if k > 0 else gdsim.Player()
        if st is None:
            continue
        xs = gdsim.x_speed(st.speed)
        horizon = xk + 1.5 * xs
        res = []
        for sign in (-1, 1):
            ok_ms = 0.0
            d = step_ms
            while d <= max_ms:
                shifted = list(base)
                # move the press and its release together
                rel = next((j for j in range(k + 1, len(base)) if not base[j][1]), None)
                shifted[k] = (xk + sign * d / 1000 * xs, True)
                if rel is not None and base[rel][0] - xk < 30:
                    shifted[rel] = (base[rel][0] + sign * d / 1000 * xs, False)
                q = copy.deepcopy(st)
                ev = sorted(e for e in shifted if e[0] >= q.x - 1e-6)
                q2, _ = gdsim.simulate(lvl, ev, min(horizon, x_end), start=q)
                if q2.dead:
                    break
                ok_ms = d
                d += step_ms
            res.append(ok_ms)
        out.append((xk, res[0], res[1]))
    return out, None


def level_string(w: World) -> str:
    L = GdLevel("CLAUDE Thermal Lock", song_id=SONG_ID,
                description="Creo - Heatseeker. Made by Distanax with Claude (AI-assisted).")
    L.set_color(1000, 18, 10, 40)   # BG: deep indigo (thermal cold)
    L.set_color(1001, 10, 6, 24)    # ground
    L.set_color(1002, 255, 120, 40)  # line: heat orange
    header = L.level_string().split(";")[0]
    return header + ";" + "".join(o + ";" for o in w.objs)


def main() -> None:
    w, tl = build()
    x_end = tl.xb(SECTIONS[-1].b1) + 200
    p, _ = simulate_world(w, x_end)
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    report = {"objects": len(w.objs), "inputs": len(w.inputs), "length_s": bt(SECTIONS[-1].b1),
              "sections": w.notes, "sim_dead": p.dead, "death_x": p.death_x}
    print(f"objects {len(w.objs)}  clicks {len(w.clicks)}  length {bt(SECTIONS[-1].b1):.1f}s")
    for n in w.notes:
        print("  ", n)
    if p.dead:
        sec = next((s.name for s in SECTIONS if tl.xb(s.b0) <= p.death_x < tl.xb(s.b1)), "?")
        print(f"SIM: DIES at x={p.death_x:.0f} ({sec})")
    else:
        print("SIM: full run survives with the scripted inputs")
        win, _ = windows(w, x_end)
        tight = [(x, a, b) for x, a, b in win if min(a, b) < 40]
        report["windows"] = win
        print(f"windows: {len(win)} presses, min early/late (ms): "
              f"{min(a for _, a, _ in win):.0f}/{min(b for _, _, b in win):.0f}; tight (<40 ms either side): {len(tight)}")
        for x, a, b in tight[:12]:
            sec = next((s.name for s in SECTIONS if tl.xb(s.b0) <= x < tl.xb(s.b1)), "?")
            print(f"   tight press at x={x:.0f} ({sec}): early {a:.0f} ms, late {b:.0f} ms")
    (out / "thermal_lock.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (out / "thermal_lock_level.txt").write_text(level_string(w), encoding="utf-8")
    if "--push" in sys.argv:
        sys.path.insert(0, str(ROOT / "server" / "src"))
        from gd_bridge_mcp.client import BridgeClient
        b = BridgeClient()
        names = [lv["name"] for lv in b.call("list_levels", claude_only=True)["levels"]]
        st = b.call("status")
        if not (st.get("in_editor") and (st.get("level") or {}).get("name") == "CLAUDE Thermal Lock"):
            if "CLAUDE Thermal Lock" in names:
                b.call("open_level", name="CLAUDE Thermal Lock")
            else:
                b.call("create_level", name="Thermal Lock", song_id=SONG_ID)
        b.call("set_level_string", level_string=level_string(w))
        b.call("save_level")
        print("pushed to GD:", b.call("status")["level"])


if __name__ == "__main__":
    main()
