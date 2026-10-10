"""Geometry Dash 2.2 player simulator, all classic modes, at the engine's 240 physics steps per second.

Constants come from the decompiled PlayerObject::updateJump (camila314/gdp) and were MEASURED in the
real engine with gd-bridge autoplay traces (levels/lab/lab.py, 2026-10-09):
  - x moves xs per step, xs = playerSpeed * speedMultiplier * 0.25 (1x: 1.2983 u/step = 311.58 u/s)
  - y moves vy * 0.225 per step (wave: vy * 0.25), velocities in "tick" units
  - per-step velocity changes = decompiled per-tick values * 0.225
Units: GD units (30 = 1 block), y = level-string y (player centre; ground row y = 15).
"""
from __future__ import annotations

from dataclasses import dataclass, field

STEPS_PER_S = 240
VSTEP = 0.225          # vertical dt per physics step (measured; constant across speeds)
HSTEP = 0.25           # horizontal dt per physics step

# speed -> (playerSpeed, speedMultiplier, yStart (cube jump vy), gravity)  [PlayerObject::updateTimeMod]
SPEED = {
    0.5: (0.7, 5.980002, 10.620032, 0.940199),
    1: (0.9, 5.77000189, 11.1800318, 0.958199024),
    2: (1.1, 5.870002, 11.420032, 0.957199),
    3: (1.3, 6.000002, 11.230032, 0.961199),
    4: (1.6, 6.000002, 11.230032, 0.961199),
}
FLY_G = 0.9582          # gravity used by ship/ufo/wave/swing/ball/spider (any speed)
TERMINAL = 15.0
FALL_T = 1.95            # playerIsFallingBugged(): vy*g below this counts as falling (measured 1.944..1.969)

# corridor height (blocks) by mode, measured with the portal at y=45: floor 0
CORRIDOR = {"ship": 10, "ufo": 10, "wave": 10, "swing": 10, "ball": 8, "spider": 9}

PLAYER_HALF = 15.0      # 30x30 main hitbox
SOLID_HALF = 4.5        # inner hitbox that dies on solids (~9x9, OpenGD)
WAVE_HALF = 10.0        # wave reaches y 10..290 in a 0..300 corridor (measured)
SPIDER_HALF = 13.5      # spider rests at y 13.5 / 43.5 / 136.5 next to surfaces (measured)
SPIKE_HALF = (3.0, 6.0)  # ID 8 hazard box half-sizes (OpenGD), centred


def x_speed(speed: float) -> float:
    ps, sm, _, _ = SPEED[speed]
    return ps * sm * 60  # u/s


@dataclass
class Player:
    x: float = 0.0
    y: float = 15.0
    vy: float = 0.0
    mode: str = "cube"
    g: int = 1                 # +1 normal gravity, -1 upside down
    speed: float = 1
    grounded: bool = True
    floor: float = 0.0         # corridor floor (surface y) for flying/ball modes
    ceil: float | None = None  # corridor ceiling (surface y); None = no ceiling (cube/robot)
    held: bool = False
    clicked: bool = False      # a press edge happened this step (orb/ufo/ball/spider click)
    dead: bool = False
    death_x: float | None = None


@dataclass
class Solid:
    x: float
    y: float
    hw: float = 15.0
    hh: float = 15.0


@dataclass
class Level:
    solids: list[Solid] = field(default_factory=list)
    hazards: list[tuple[float, float, float, float]] = field(default_factory=list)  # x, y, hw, hh
    portals: list[tuple[float, float, str]] = field(default_factory=list)            # x, y, mode/speed
    end_x: float = 1e9


def _half(p: Player) -> float:
    return WAVE_HALF if p.mode == "wave" else (SPIDER_HALF if p.mode == "spider" else PLAYER_HALF)


def step(p: Player, lvl: Level, pressed: bool) -> None:
    """Advance one physics step (1/240 s)."""
    if p.dead:
        return
    edge = pressed and not p.held
    p.held = pressed
    ps, sm, ystart, grav = SPEED[p.speed]
    p.x += ps * sm * HSTEP

    # portals the player is touching (portal box ~ 1 x 3 blocks around its centre)
    for (px, py, kind) in lvl.portals:
        if abs(px - p.x) < 15 and abs(py - p.y) < 45 + _half(p):
            if kind in SPEED_KEYS:
                p.speed = SPEED_KEYS[kind]
            elif kind != p.mode:
                _enter_mode(p, kind, py)

    m, g = p.mode, p.g
    if m == "cube":
        if p.grounded and pressed:
            p.vy, p.grounded = g * ystart, False
        if not p.grounded:
            p.vy -= g * grav * VSTEP
    elif m == "ship":
        up = p.vy * g > FALL_T
        if pressed:
            p.vy += g * FLY_G * (0.4 if up else 0.5) * VSTEP
        else:
            p.vy -= g * FLY_G * 0.4 * (1.2 if up else 0.8) * VSTEP
        p.vy = _clamp_fly(p.vy, g, 8.0, 6.4)
        p.grounded = False
    elif m == "ufo":
        if edge and g * p.vy < 7.0:
            p.vy = g * 7.0
        up = p.vy * g > FALL_T
        p.vy -= g * FLY_G * 0.5 * (1.2 if up else 0.8) * VSTEP
        p.vy = _clamp_fly(p.vy, g, 8.0, 6.4)
        p.grounded = False
    elif m == "wave":
        p.vy = (1 if pressed else -1) * g * ps * sm
        p.grounded = False
    elif m == "swing":
        if edge:
            p.g = g = -g
            p.vy *= 0.8
        p.vy -= g * FLY_G * 0.4 * VSTEP
        p.vy = _clamp_fly(p.vy, g, 8.0, 8.0)
        p.grounded = False
    elif m == "ball":
        if p.grounded and edge:
            p.vy = g * ystart * 0.3  # measured: flipGravity halves on top of 0.6
            p.g = g = -g
            p.grounded = False
        if not p.grounded:
            p.vy -= g * FLY_G * 0.6 * VSTEP
    elif m == "spider":
        if p.grounded and edge:
            _spider_teleport(p, lvl)
            g = p.g
        if not p.grounded:
            p.vy -= g * FLY_G * 0.6 * VSTEP
    p.vy = max(-TERMINAL, min(TERMINAL, p.vy))
    p.y += p.vy * (HSTEP if m == "wave" else VSTEP)
    _collide(p, lvl)


SPEED_KEYS = {"speed0.5": 0.5, "speed1": 1, "speed2": 2, "speed3": 3, "speed4": 4}


def _clamp_fly(vy: float, g: int, up: float, down: float) -> float:
    lo, hi = (-down, up) if g == 1 else (-up, down)
    return max(lo, min(hi, vy))


def _enter_mode(p: Player, mode: str, portal_y: float) -> None:
    p.mode = mode
    if mode in CORRIDOR:
        p.floor = 0.0  # measured with portals near the ground; see TODO below
        p.ceil = p.floor + CORRIDOR[mode] * 30
        # TODO(lab): corridor placement for portals higher up (GD centres it on the portal; verify)
    else:
        p.ceil = None
    if mode in ("ship", "ufo", "swing", "wave"):
        p.vy *= 0.5  # GD halves momentum on entering a flying mode (approximation; verify in lab)
    # smaller hitboxes settle onto the floor on entry (measured: wave y 10, spider y 13.5)
    if p.g == 1 and abs(p.y - (p.floor + PLAYER_HALF)) < 1.0:
        p.y = p.floor + (WAVE_HALF if mode == "wave" else SPIDER_HALF if mode == "spider" else PLAYER_HALF)


def _spider_teleport(p: Player, lvl: Level) -> None:
    """Spider click: snap to the nearest surface in the gravity-up direction, then flip gravity."""
    target = None
    for s in lvl.solids:
        if abs(s.x - p.x) < s.hw + PLAYER_HALF - 1:
            surf = s.y - s.hh if p.g == 1 else s.y + s.hh
            if (surf - p.y) * p.g > 0 and (target is None or abs(surf - p.y) < abs(target - p.y)):
                target = surf
    if target is None and p.ceil is not None:
        target = p.ceil if p.g == 1 else p.floor
    if target is None:
        return
    p.y = target - p.g * SPIDER_HALF
    p.g = -p.g
    p.vy = 0.0
    p.grounded = True


def _collide(p: Player, lvl: Level) -> None:
    h = _half(p)
    # corridor floor/ceiling (ground always at 0)
    floor = p.floor if p.ceil is not None else 0.0
    if p.y - h <= floor:
        if p.mode == "wave" and p.ceil is None:
            pass
        p.y = floor + h
        if p.g == 1 or p.mode in ("ship", "ufo", "wave", "swing"):
            p.vy = max(p.vy, 0.0) if p.g == 1 else p.vy
            if p.g == 1:
                p.grounded = p.mode in ("cube", "ball", "spider", "robot")
                if p.mode != "wave":
                    p.vy = 0.0
    if p.ceil is not None and p.y + h >= p.ceil:
        p.y = p.ceil - h
        if p.g == -1:
            p.grounded = p.mode in ("cube", "ball", "spider")
            p.vy = 0.0
        elif p.mode != "wave":
            p.vy = min(p.vy, 0.0)

    # solid blocks: land on the surface in the gravity direction, die if the inner box hits a side/bottom
    for s in lvl.solids:
        if abs(s.x - p.x) >= s.hw + h or abs(s.y - p.y) >= s.hh + h:
            continue
        if p.mode == "wave":
            _die(p)
            return
        top, bot = s.y + s.hh, s.y - s.hh
        if p.g == 1 and p.vy <= 0 and p.y - h >= top - 12:
            p.y, p.vy, p.grounded = top + h, 0.0, True
        elif p.g == -1 and p.vy >= 0 and p.y + h <= bot + 12:
            p.y, p.vy, p.grounded = bot - h, 0.0, True
        elif p.mode in ("ship", "ufo", "swing") and abs(s.y - p.y) > s.hh and abs(s.x - p.x) < s.hw + h - 4:
            # flying modes may slide along a block's top/bottom face
            if p.y > s.y:
                p.y, p.vy = top + h, max(p.vy, 0.0)
            else:
                p.y, p.vy = bot - h, min(p.vy, 0.0)
        elif abs(s.x - p.x) < s.hw + SOLID_HALF and abs(s.y - p.y) < s.hh + SOLID_HALF:
            _die(p)
            return
    for (hx, hy, hw, hh) in lvl.hazards:
        if abs(hx - p.x) < hw + h and abs(hy - p.y) < hh + h:
            _die(p)
            return


def _die(p: Player) -> None:
    p.dead, p.death_x = True, p.x


def simulate(lvl: Level, inputs: list[tuple[float, bool]], x_end: float, start: Player | None = None,
             trace: bool = False):
    """Run from `start` (default cube at x=0 on the ground) with inputs [(x, press)], firing on the
    first step the player reaches x (same rule as gd-bridge autoplay). Returns (player, trace rows)."""
    p = start or Player()
    ev = sorted(inputs)
    i, pressed, rows = 0, False, []
    while p.x < x_end and not p.dead:
        while i < len(ev) and p.x >= ev[i][0]:
            pressed = ev[i][1]
            i += 1
        step(p, lvl, pressed)
        if trace:
            rows.append((p.x, p.y, p.vy, p.mode, p.g, p.grounded))
    return p, rows
