"""Approximate cube simulator + preview renderer for layout sanity checks.

Physics constants are ESTIMATES (cube jump ~0.39 s airtime, ~2.1 block apex) and are
calibrated against Distanax's playtests. A pass here is NOT proof a layout is beatable.
"""
from PIL import Image, ImageDraw
from .gdlib import *

G = 3314.0          # gravity, units/s^2 (estimate)
V_JUMP = 646.0      # cube jump velocity (estimate)
V_PAD = {YELLOW_PAD: 862.0}
V_ORB = {YELLOW_ORB: 640.0}
DT = 1 / 480

SOLID = {BLOCK}
HAZARD = {SPIKE: (12, 18, 2)}   # id: (hitbox w, h, y offset from object bottom)


def speed_at(level, x):
    """Speed portals change speed when the player's x passes them."""
    portals = sorted((o[2], k) for o in level.objects for k, pid in SPEED_PORTAL.items() if o[1] == pid)
    s = level.start_speed
    for px, k in portals:
        if x >= px:
            s = k
    return s


def simulate(level, clicks, t_end, verbose=False):
    """clicks: list of times (s) the player presses (tap = jump when grounded / orb when overlapping).
    Returns (ok, events, path)."""
    solids = [o for o in level.objects if o[1] in SOLID]
    hazards = [o for o in level.objects if o[1] in HAZARD]
    pads = [o for o in level.objects if o[1] in V_PAD]
    orbs = [o for o in level.objects if o[1] in V_ORB]
    x, y, vy, t = 0.0, 15.0, 0.0, 0.0
    clicks = sorted(clicks)
    ci = 0
    used = set()
    path, events = [], []
    grounded = True
    while t < t_end:
        sp = SPEEDS[speed_at(level, x)]
        # input
        press = False
        while ci < len(clicks) and clicks[ci] <= t:
            press = True
            ci += 1
        if press:
            hit_orb = None
            for o in orbs:
                if id(o) not in used and abs(o[2] - x) < 30 and abs(o[3] - y) <= 30:
                    hit_orb = o
                    break
            if hit_orb is not None:
                vy = V_ORB[hit_orb[1]]; used.add(id(hit_orb)); grounded = False
                events.append((round(t, 3), "orb", round(x)))
            elif grounded:
                vy = V_JUMP; grounded = False
                events.append((round(t, 3), "jump", round(x)))
            else:
                events.append((round(t, 3), "click-in-air(ignored)", round(x)))
        # pads
        for o in pads:
            if id(o) not in used and abs(o[2] - x) < 18 and y - 15 <= o[3] + 2:
                vy = V_PAD[o[1]]; used.add(id(o)); grounded = False
                events.append((round(t, 3), "pad", round(x)))
        # integrate
        x += sp * DT
        vy -= G * DT
        y += vy * DT
        # floor = ground (y=15 centre) or block tops beneath
        floor = 15.0
        for o in solids:
            if abs(o[2] - x) < 15 + 14:          # horizontal overlap (player 30 wide)
                top = o[3] + 15
                if y - 15 >= top - 12 and top + 15 > floor:
                    floor = top + 15
        if y <= floor:
            y, vy, grounded = floor, 0.0, True
        else:
            grounded = False
        # deaths
        for o in solids:   # inner hitbox (approx 10x10) into a block
            if abs(o[2] - x) < 15 + 5 and abs(o[3] - y) < 15 + 5 and not (y - 15 >= o[3] + 15 - 12):
                return False, events + [(round(t, 3), "DIED: block", round(x), round(y))], path
        for o in hazards:
            w, h, off = HAZARD[o[1]]
            bottom = o[3] - 15 + off
            if abs(o[2] - x) < 15 + w / 2 and (y - 15) < bottom + h and (y + 15) > bottom:
                return False, events + [(round(t, 3), "DIED: spike", round(x), round(y))], path
        path.append((x, y))
        t += DT
    return True, events, path


def render(level, path, out, x0=0, x1=None, scale=0.5, beat_xs=(), height=330):
    xs = [o[2] for o in level.objects]
    x1 = x1 or (max(xs) + 300)
    W = int((x1 - x0) * scale)
    H = int(height * scale) + 20
    img = Image.new("RGB", (W, H), (34, 18, 70))
    d = ImageDraw.Draw(img)
    gy = lambda y: H - 10 - y * scale
    gx = lambda x: (x - x0) * scale
    d.rectangle([0, gy(0), W, H], fill=(14, 8, 30))
    for bx in beat_xs:
        if x0 <= bx <= x1:
            d.line([gx(bx), gy(0), gx(bx), gy(height)], fill=(70, 50, 110))
    for o in level.objects:
        oid, x, y = o[1], o[2], o[3]
        if not (x0 - 30 <= x <= x1):
            continue
        r = 15 * scale
        if oid == BLOCK:
            d.rectangle([gx(x) - r, gy(y) - r, gx(x) + r, gy(y) + r], fill=(10, 10, 10), outline=(255, 255, 255))
        elif oid == SPIKE:
            if o.get(6) == 180:
                d.polygon([(gx(x) - r, gy(y) - r), (gx(x) + r, gy(y) - r), (gx(x), gy(y) + r)], fill=(10, 10, 10), outline=(255, 120, 120))
            else:
                d.polygon([(gx(x) - r, gy(y) + r), (gx(x) + r, gy(y) + r), (gx(x), gy(y) - r)], fill=(10, 10, 10), outline=(255, 255, 255))
        elif oid in (PINK_ORB, BLUE_ORB):
            c = (255, 110, 220) if oid == PINK_ORB else (70, 170, 255)
            d.ellipse([gx(x) - r * .7, gy(y) - r * .7, gx(x) + r * .7, gy(y) + r * .7], fill=c)
        elif oid in (PINK_PAD, BLUE_PAD):
            c = (255, 110, 220) if oid == PINK_PAD else (70, 170, 255)
            yy = y - 12 if o.get(6) != 180 else y + 12
            d.rectangle([gx(x) - r, gy(yy) - 2, gx(x) + r, gy(yy) + 2], fill=c)
        elif oid == YELLOW_PAD:
            d.rectangle([gx(x) - r, gy(y - 12), gx(x) + r, gy(y - 15)], fill=(255, 230, 40))
        elif oid == YELLOW_ORB:
            d.ellipse([gx(x) - r * .7, gy(y) - r * .7, gx(x) + r * .7, gy(y) + r * .7], fill=(255, 230, 40))
        elif oid in SPEED_PORTAL.values() or oid in PORTAL.values():
            d.rectangle([gx(x) - r * .5, gy(y) - r * 2, gx(x) + r * .5, gy(y) + r * 2], outline=(80, 255, 120), width=2)
    if path:
        d.line([(gx(x), gy(y)) for x, y in path[::4]], fill=(255, 120, 40), width=2)
    img.save(out)
    return out
