"""Heatseeker (working title "Thermal Lock") — level builder.

Song: Creo - Heatseeker (NG 1502369), 127 BPM, first beat 0.055 s.
Build one section at a time; each section is a function that appends objects.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `toolkit` imports when run directly

from toolkit import out_path
from toolkit.gdlib import *

BPM = 127.0
BEAT = 60.0 / BPM
T0 = 0.055                     # first beat (s)
SONG_ID = 1502369


def bt(b):
    """time (s) of beat index b (fractional allowed)."""
    return T0 + b * BEAT


def snap(x, step=7.5):
    return round(x / step) * step


class Builder:
    """Tracks the player's x along a constant-speed run and places beat-relative patterns."""
    JUMP_HALF = 61     # x distance from take-off to apex at 1x (estimate, = 0.195 s * 311.58)

    def __init__(self, level):
        self.L = level
        self.clicks = []       # ideal click times for the simulator

    def X(self, b):
        # Section 1 is entirely 1x from t=0, so x = v * t.
        return SPEEDS[1] * bt(b)

    def block(self, x, row):
        self.L.add(BLOCK, snap(x), 15 + 30 * row)

    def spike(self, x, row=0):
        self.L.add(SPIKE, snap(x), 15 + 30 * row)

    # ---- patterns: each takes the beat index of the click --------------------
    def p_spike(self, b, row=0):
        self.clicks.append(bt(b))
        self.spike(self.X(b) + self.JUMP_HALF, row)

    def p_double(self, b, row=0):
        self.clicks.append(bt(b))
        x = self.X(b) + self.JUMP_HALF
        self.spike(x - 15, row); self.spike(x + 15, row)

    def platform(self, x_start, x_end, rows):
        """solid platform `rows` blocks high from x_start to x_end (block centres)."""
        x = snap(x_start, 30) + 15 if False else snap(x_start)
        while x <= x_end:
            for r in range(rows):
                self.block(x, r)
            x += 30

    def pad(self, b):
        self.L.add(YELLOW_PAD, snap(self.X(b)), 15 - 13)   # pads sit on the floor


def section1(B):
    """Intro 0 - 18.0 s (bars 1-9). Cube 1x, modern style: hops between floating platforms over a
    spike carpet, orbs on eighth notes, a gravity-flip phrase on the ceiling, quarter-note build."""
    from toolkit.trajgen import CubeRun, stand
    S0, S1, S2, S3 = stand(-1), stand(0), stand(1), stand(2)
    CEIL_ROW = 225                     # ceiling block row for the flipped phrase
    HANG = stand(7, g=-1)              # player centre while hanging under row 7 (y=225)
    R = CubeRun(B.L, x0=0.0, t0=0.0, speed=1, y0=S0, ceiling_row=CEIL_ROW)
    a = lambda b, k, land=None: R.act(bt(b), k, land)
    # bars 2-3: half-note hops, rising
    a(6, "jump", S1); a(8, "jump", S1)
    a(10, "jump", S2); a(12, "jump"); a(12.5, "yellow_orb", S2)
    # bar 4: pad launch, then hop
    a(14, "yellow_pad", S1); a(16, "jump", S1); a(17, "jump", S2)
    # bar 5: stair up on quarters, then lift into the gravity phrase
    a(18, "jump", S2); a(19, "jump", S3); a(20, "jump", S3)
    a(21.5, "jump"); a(22, "blue_orb", HANG)
    # bars 6-7: upside down on the ceiling
    a(24, "jump", HANG); a(25, "jump", HANG); a(26, "jump"); a(26.5, "pink_orb", HANG)
    a(28, "blue_pad", S1)
    # bar 8-9: quarter-note build into the drop
    a(30, "jump", S1); a(31, "jump", S2); a(32, "jump", S1); a(33, "jump", S2)
    a(34, "jump", S2); a(35, "jump", S3); a(36, "jump"); a(36.5, "yellow_orb", S0)
    x_end = R.finish(bt(38))
    B.L.add(SPEED_PORTAL[2], snap(R.x), 45)      # drop: 2x from beat 38
    B.clicks = [c[0] for c in R.clicks]
    B.run = R
    return R


def build(sections=(1,)):
    L = Level("Thermal Lock", song_id=SONG_ID,
              description="Creo - Heatseeker. Built with Claude + Distanax.")
    # gameplay-only palette: readable, no deco
    L.set_color(BG, 34, 18, 70)
    L.set_color(GROUND, 14, 8, 30)
    L.set_color(LINE, 255, 120, 60)
    B = Builder(L)
    if 1 in sections:
        section1(B)
    return L, B


if __name__ == "__main__":
    # sim2 handles gravity flips and blue/pink orbs; the older sim.py does not and fails Section 1 v2.
    from toolkit.sim import render
    from toolkit.sim2 import simulate
    L, B = build()
    ok, ev = simulate(L, B.clicks, t_end=19.0)
    for e in ev:
        print(e)
    print("SIM PASS" if ok else "SIM FAIL")
    beats = [SPEEDS[1] * bt(b) for b in range(0, 40)]
    print(render(L, B.run.trace, out_path("s1_preview.png"), x0=600, x1=6200, scale=0.32, beat_xs=beats))
    print(L.save(out_path("thermal_lock_s1.gmd")))
