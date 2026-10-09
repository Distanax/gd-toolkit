"""Calibration level: verifies ground-row y, x origin, colours, text and objects import correctly."""
import os
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # repo root, so `toolkit` imports when run directly

from toolkit import out_path
from toolkit.gdlib import *

L = Level("Claude Calibration")
L.set_color(BG, 40, 20, 70)
L.set_color(GROUND, 20, 10, 40)

# column of labelled blocks: whichever label sits on the ground line is the ground-row y
for y in (15, 45, 75, 105, 135):
    L.add(BLOCK, 165, y)
    L.text(225, y, f"y{y}", scale=0.5)

# x markers along the y=255 line, every 150 units
for x in range(15, 1000, 150):
    L.add(BLOCK, x, 255)
    L.text(x, 285, f"x{x}", scale=0.5)

# spikes at both candidate ground heights + an orb, to check object IDs
L.add(SPIKE, 405, 15)
L.add(SPIKE, 465, 105)
L.add(YELLOW_ORB, 555, 75)
L.add(YELLOW_PAD, 645, 15)
L.add(PORTAL["ship"], 765, 75)
L.add(SPEED_PORTAL[2], 855, 75)

p = L.save(out_path("claude_calibration.gmd"))
print(p, os.path.getsize(p))
print(L.level_string()[:400])
