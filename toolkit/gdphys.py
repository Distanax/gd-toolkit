"""Geometry Dash physics constants, from decompiled/reimplemented sources (not estimates).

Sources:
  - camila314/gdp  PlayerObject::updateTimeMod / updateJump  (GD 2.2 decompilation)
  - Open-GD/OpenGD PlayerObject::propellPlayer / ringJump, PlayLayer pad handling, LongData hitboxes
Internal units: positions in GD units (30 = 1 block); velocities per 1/60 s tick; we convert to per-second.
"""
TICK = 60.0

# speed setting -> (playerSpeed, speedMultiplier, yStart (jump vel / tick), gravity / tick^2)
_SPEED = {
    0.5: (0.7, 5.980002, 10.620032, 0.940199),
    1:   (0.9, 5.77000189, 11.1800318, 0.958199024),
    2:   (1.1, 5.870002, 11.420032, 0.957199),
    3:   (1.3, 6.000002, 11.230032, 0.961199),
    4:   (1.6, 6.000002, 11.230032, 0.961199),
}

def x_speed(speed):            # units / s
    ps, mult, _, _ = _SPEED[speed]
    return ps * mult * TICK

def jump_v(speed, mini=False):  # units / s
    return _SPEED[speed][2] * TICK * (0.8 if mini else 1.0)

def gravity(speed, mode="cube"):  # units / s^2 (cube); ball/spider use 0.9582*0.6, robot 0.9x
    g = _SPEED[speed][3]
    if mode in ("ball", "spider"):
        g = 0.9582 * 0.6
    elif mode == "robot":
        g = g * 0.9
    return g * TICK * TICK

TERMINAL_V = 15 * TICK          # max fall speed, units / s

# orbs: multiplier of the current jump velocity (cube values)
ORB_MULT = {"yellow_orb": 1.0, "pink_orb": 0.72, "red_orb": 1.38, "blue_orb": 0.8, "green_orb": 1.0}
ORB_FLIPS = {"blue_orb", "green_orb"}
# pads: 16 units/tick * force, independent of speed
PAD_FORCE = {"yellow_pad": 1.0, "pink_pad": 0.65, "red_pad": 1.25, "blue_pad": 0.8}
PAD_FLIPS = {"blue_pad"}

def orb_v(kind, speed, mini=False):
    return jump_v(speed, mini) * ORB_MULT[kind]

def pad_v(kind, mini=False):
    return 16 * TICK * PAD_FORCE[kind] * (0.8 if mini else 1.0)

# hitboxes (half-widths / half-heights around object centre), units
PLAYER_HALF = 15.0              # cube 30x30 (mini 18x18 -> 9)
SPIKE_HALF = (3.0, 6.0)         # ID 8: 6 wide x 12 tall, centred
BLOCK_HALF = (15.0, 15.0)
SOLID_INNER_HALF = 4.5          # player's inner hitbox that kills on solid contact (~9x9)

# derived reference values at 1x (sanity): airtime ~0.389 s, apex ~65 units (2.17 blocks)
if __name__ == "__main__":
    for s in _SPEED:
        v, g = jump_v(s), gravity(s)
        print(f"{s}x: x {x_speed(s):.2f} u/s  jump {v:.1f}  g {g:.0f}  airtime {2*v/g:.3f}s  apex {v*v/2/g:.1f}u  jump length {x_speed(s)*2*v/g/30:.2f} blocks")
