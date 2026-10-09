"""Trajectory-first cube generator.

You script inputs on beats; the generator simulates the cube and builds terrain around the path:
  - a platform under every grounded stretch (with an early/late timing margin at each end)
  - a spike carpet under airborne stretches where the player clears it comfortably
  - orbs placed exactly where the player is at the click; pads where the player stands
Gravity flips (blue orb / blue pad / gravity portal) mirror everything onto a ceiling.

Physics constants are estimates (see sim.py) and get calibrated from playtests.
"""
from .gdlib import *
from . import gdphys as P


def vel(kind, speed):
    """launch speed (units/s) for an input kind at a speed setting — exact GD values (gdphys)."""
    if kind == "jump":
        return P.jump_v(speed)
    if kind.endswith("_orb"):
        return P.orb_v(kind, speed)
    return P.pad_v(kind)
OBJ = {"yellow_orb": YELLOW_ORB, "pink_orb": PINK_ORB, "blue_orb": BLUE_ORB,
       "yellow_pad": YELLOW_PAD, "pink_pad": PINK_PAD, "blue_pad": BLUE_PAD}
DT = 1 / 600


def snap(x, s=7.5):
    return round(x / s) * s


class CubeRun:
    """Generates one constant-speed cube stretch.

    floor_y / ceil_y are the y of the *player centre* when standing (normal) or hanging (flipped).
    """

    def __init__(self, level, x0, t0, speed=1, y0=15.0, carpet=True, ceiling_row=None):
        self.L = level
        self.v = SPEEDS[speed]
        self.speed = speed
        self.G = P.gravity(speed)
        self.x, self.t, self.y, self.vy = x0, t0, y0, 0.0
        self.g = 1                     # +1 normal gravity, -1 flipped
        self.grounded = True
        self.ground_start = x0         # x where the current grounded stretch began
        self.stand_y = y0              # player centre y while grounded
        self.carpet = carpet
        self.ceiling_row = ceiling_row  # y (block centre) of the ceiling spike line when flipped
        self.clicks = []               # (time, kind) for simulator / logging
        self.objs = []
        self.log = []
        self.pending_land = None       # target stand height for the next landing
        self.trace = []

    # ---------------------------------------------------------------- helpers
    def _place(self, oid, x, y, **kw):
        o = self.L.add(oid, snap(x), y, **kw)
        self.objs.append(o)
        return o

    def _platform(self, xa, xb, stand_y, g):
        """Blocks so the player stands at stand_y from xa to xb (block centres on 30-grid in y)."""
        top = stand_y - 15 * g            # surface the player rests on
        row_y = top - 15 * g              # centre of the block row
        if g == 1 and row_y < 15 - 1:     # standing on real ground: nothing to build
            return
        x = snap(xa, 15)
        while x <= xb + 0.1:
            self._place(BLOCK, x, row_y)
            x += 30

    def _carpet(self, xa, xb, path, g):
        """Spikes under (normal) or over (flipped) an airborne stretch where the path clears them."""
        if not self.carpet:
            return
        if g == 1:
            spike_y, rot = 15, 0
            clear = lambda py: py - 15 >= 30 + 14      # player bottom above spike top + margin
        else:
            if self.ceiling_row is None:
                return
            spike_y, rot = self.ceiling_row, 180
            clear = lambda py: py + 15 <= spike_y - 15 - 14
        x = snap(xa + (70 if abs(path[0][1] - 15) < 8 and g == 1 else 40), 30) if path else snap(xa + 40, 30)
        while x <= xb - 40:
            # player y at this x (nearest path sample)
            py = min(path, key=lambda p: abs(p[0] - x))[1]
            if clear(py):
                self._place(SPIKE, x, spike_y, rot=rot) if rot else self._place(SPIKE, x, spike_y)
            x += 30

    # ---------------------------------------------------------------- core
    def advance_to(self, t_target):
        """Integrate physics until t_target, building terrain as stretches complete."""
        path = []
        air_start = None if self.grounded else self.x
        while self.t < t_target - 1e-9:
            if not self.grounded:
                self.vy -= self.g * self.G * DT
                self.vy = max(self.vy, -P.TERMINAL_V) if self.g == 1 else min(self.vy, P.TERMINAL_V)
                self.y += self.vy * DT
                path.append((self.x, self.y))
                # landing on the target height
                if self.pending_land is not None:
                    tgt = self.pending_land
                    if (self.g == 1 and self.vy < 0 and self.y <= tgt) or (self.g == -1 and self.vy > 0 and self.y >= tgt):
                        self.y, self.vy, self.grounded = tgt, 0.0, True
                        self._carpet(air_start if air_start is not None else self.x, self.x, path, self.g)
                        self.ground_start = self.x - 45          # early-landing margin (~1.5 blocks)
                        self.stand_y = tgt
                        self.pending_land = None
                        path = []
                        air_start = None
            self.x += self.v * DT
            self.t += DT
            self.trace.append((self.x, self.y))
        return path

    def _takeoff(self):
        """Close the grounded stretch (platform up to the click point + late margin)."""
        if self.grounded:
            self._platform(self.ground_start, self.x + 22, self.stand_y, self.g)
            self.grounded = False

    def act(self, t, kind, land=None):
        """kind: jump | yellow_orb | pink_orb | blue_orb | yellow_pad | pink_pad | blue_pad | walk
        land: stand height (player centre y) for the next landing; required for anything leaving the floor."""
        path = self.advance_to(t)
        if kind == "walk":
            return
        if kind.endswith("_orb"):
            assert not self.grounded, f"orb at t={t:.3f} but player is grounded"
            self._place(OBJ[kind], self.x, self.y)
            self.clicks.append((t, kind))
        elif kind.endswith("_pad"):
            assert self.grounded, f"pad at t={t:.3f} but player airborne"
            off = -13 if self.g == 1 else 13
            self._place(OBJ[kind], self.x, self.stand_y + off, **({"rot": 180} if self.g == -1 else {}))
        else:
            assert self.grounded, f"jump at t={t:.3f} but player airborne"
            self.clicks.append((t, kind))
        self._takeoff()
        v = vel(kind, self.speed)
        if kind in ("blue_orb", "blue_pad"):
            # GD: velocity is applied in the OLD gravity direction, then gravity flips,
            # so the player is thrown toward the new floor.
            self.vy = self.g * v
            self.g = -self.g
        else:
            self.vy = self.g * v
        self.pending_land = land
        self.log.append((round(t, 3), kind, round(self.x), round(self.y)))

    def finish(self, t_end):
        self.advance_to(t_end)
        if self.grounded:
            self._platform(self.ground_start, self.x, self.stand_y, self.g)
        return self.x


def stand(row, g=1):
    """player-centre y when standing on top of block row `row` (row 0 = ground blocks, -1 = real ground)."""
    if g == 1:
        return 15 + 30 * (row + 1)
    return 15 + 30 * (row - 1)
