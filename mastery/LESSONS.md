# Lessons

One entry per lesson: what was learned, the evidence (source, corpus numbers, frames, playtest), and
what changed because of it (tool, checklist, plan). Newest at the bottom.

- 2026-10-09 — **Tier standards are not published.** RobTop's rating doc says there are no specific
  guidelines for what makes a level rate-worthy, and tiers reflect "how much RobTop likes your level"
  (https://robtopgames.com/files/GDRating.pdf, p. 7 and 9). So every "this is Featured-quality" claim
  in this project must point at corpus data or moderator feedback. -> Encoded in PROGRESS.md
  non-negotiables and CHECKLIST.md (task 10).
- 2026-10-09 — **Measured GD 2.2 physics in the real engine (gd-bridge 1.1.0 autoplay traces).**
  Horizontal: 0.25 tick per 1/240 s step (1x = 311.58 u/s). **Vertical: 0.225 tick per step at every
  speed** (wave uses 0.25 -> exact 45 deg). Real units: v = 54*vy u/s, a = 2916*g u/s². So the old
  gdphys airtimes/jump lengths were ~10% short (1x cube: 0.432 s / 4.37 blocks measured, not 0.389 s /
  4.04); apex heights were right. Ball click = 0.3 * yStart (not 0.6); ship/UFO switch gravity factors at
  vy*g < 1.95 ("falling"), not at 0. Corridors with the portal near the ground: ship/UFO/wave/swing 10
  blocks, ball 8, spider 9. A portal centred at y=105 misses a player running at y=15. -> toolkit/gdsim.py
  replays every lab run to within ~3 units p95 (levels/lab/lab.py). Evidence: out/lab/*.json traces.
- 2026-10-09 — **Mega Hack noclip is on in Distanax's install**, so autoplay never sees deaths (the
  player passes through hazards). Traces are still exact; hazard checks come from gdsim's collision model
  until noclip is off for test runs.
