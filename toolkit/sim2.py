"""Cube simulator with gravity flips, yellow/pink/blue orbs and pads. Same estimated constants as trajgen."""
from .gdlib import *
from . import gdphys as P
from .trajgen import vel

DT = 1 / 600
ORB_V = {YELLOW_ORB: "yellow_orb", PINK_ORB: "pink_orb", BLUE_ORB: "blue_orb"}
PAD_V = {YELLOW_PAD: "yellow_pad", PINK_PAD: "pink_pad", BLUE_PAD: "blue_pad"}


def simulate(level, clicks, t_end, speed=1, x0=0.0, y0=15.0, t0=0.0):
    solids = [o for o in level.objects if o[1] == BLOCK]
    spikes = [o for o in level.objects if o[1] == SPIKE]
    orbs = [o for o in level.objects if o[1] in ORB_V]
    pads = [o for o in level.objects if o[1] in PAD_V]
    v = SPEEDS[speed]
    G = P.gravity(speed)
    x, y, vy, g, t = x0, y0, 0.0, 1, t0
    clicks = sorted(clicks); ci = 0; used = set(); ev = []
    grounded = True
    while t < t_end:
        press = False
        while ci < len(clicks) and clicks[ci] <= t:
            press = True; ci += 1
        if press:
            hit = next((o for o in orbs if id(o) not in used and abs(o[2] - x) <= 30 and abs(o[3] - y) <= 30), None)
            if hit is not None:
                k = ORB_V[hit[1]]; used.add(id(hit)); grounded = False
                if k == "blue_orb":
                    vy = g * vel(k, speed); g = -g
                else:
                    vy = g * vel(k, speed)
                ev.append((round(t, 3), k))
            elif grounded:
                vy = g * vel("jump", speed); grounded = False; ev.append((round(t, 3), "jump"))
            else:
                ev.append((round(t, 3), "air-click"))
        for o in pads:
            if id(o) in used or abs(o[2] - x) > 16:
                continue
            if abs(o[3] - (y - 13 * g)) < 10:
                k = PAD_V[o[1]]; used.add(id(o)); grounded = False
                if k == "blue_pad":
                    vy = g * vel(k, speed); g = -g
                else:
                    vy = g * vel(k, speed)
                ev.append((round(t, 3), k))
        x += v * DT
        vy -= g * G * DT
        vy = max(vy, -P.TERMINAL_V) if g == 1 else min(vy, P.TERMINAL_V)
        y += vy * DT
        # support: block surfaces in the gravity direction
        support = 15.0 if g == 1 else None
        for o in solids:
            if abs(o[2] - x) < 29:
                if g == 1:
                    top = o[3] + 15
                    if y - 15 >= top - 10 and (support is None or top + 15 > support):
                        support = top + 15
                else:
                    bot = o[3] - 15
                    if y + 15 <= bot + 10 and (support is None or bot - 15 < support):
                        support = bot - 15
        if support is not None and ((g == 1 and y <= support) or (g == -1 and y >= support)):
            y, vy, grounded = support, 0.0, True
        else:
            grounded = False
        for o in solids:
            if abs(o[2] - x) < 20 and abs(o[3] - y) < 20:
                return False, ev + [(round(t, 3), "DIED block", round(x), round(y))]
        for o in spikes:
            # approx GD spike hitbox: ~9 wide, ~14 tall, sitting toward the spike's base
            lo, hi = o[3] - P.SPIKE_HALF[1], o[3] + P.SPIKE_HALF[1]
            if abs(o[2] - x) < P.PLAYER_HALF + P.SPIKE_HALF[0] and y - 15 < hi and y + 15 > lo:
                return False, ev + [(round(t, 3), "DIED spike", round(x), round(y))]
        if y > 2000 or y < -100:
            return False, ev + [(round(t, 3), "DIED out of bounds")]
        t += DT
    return True, ev


def windows(level, clicks, t_end, step=10, span=150):
    base = sorted(clicks); out = []
    for i, c in enumerate(base):
        lo = hi = None
        for d in range(-span, span + 1, step):
            cl = base.copy(); cl[i] = c + d / 1000
            ok, _ = simulate(level, cl, min(c + 1.4, t_end))
            if ok:
                lo = d if lo is None else lo; hi = d
        out.append((round(c, 3), lo, hi))
    return out
