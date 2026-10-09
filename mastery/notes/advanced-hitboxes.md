# Advanced Hitboxes

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/advanced-hitboxes/ — by MateussDev, with
contributions by NotAModerator (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09.

## Facts (paraphrased)
1. **Main hitbox (AABB) 30x30 units:** collides with non-rotated hazards, floors, ceilings, slopes; not
   with rotated objects; anchors the player on solids; has subframes; its right edge drives the X snap.
   Y snap happens ~24 units from a block when vertical velocity is zero or toward the block.
2. **Solid (inner/"blue") hitbox:** checks solid blocks/slopes only and decides whether a solid hit
   kills; smaller = more reaction time (no size given here — gdphys uses ~9x9 from OpenGD).
3. **Rotated hitbox (OBB):** collides only with rotated objects; controls **coyote time** (short grace to
   jump after leaving a ledge; mentioned for ball); no subframes; its rotation depended on FPS at
   1000+ FPS (mostly ship) — the guide says 2.2's **240 FPS physics** may make that obsolete.
4. **Slope hitbox:** circle inscribed in the main hitbox; matters mostly in wave (deaths other hitboxes
   don't explain); exists to make some gaps impossible; no subframes.
5. **Subframes:** 4 extra checks between physics frames, linear between centres; prevent phasing at
   low FPS; negligible above ~240 FPS; can create frame-perfects (often two).
6. **Collision blocks:** OBB-like with subframes; static blocks only collide at 90-degree orientations.
7. **Moving platforms** apply movement to their group's hitboxes each frame. Trick: a large-distance,
   0-duration move trigger relocates a hazard/platform within one frame without killing/flinging.

Not on this page: per-mode/mini sizes, spike/saw sizes, orb/pad/portal hitboxes, scale enlargement,
No Touch, how to view hitboxes. Those come from OpenGD (task 51).

## Mapping to our tools
- Sim (52): player AABB 30x30 (mini from OpenGD), inner solid box (~9x9, OpenGD), slope circle for wave,
  OBB for rotated hazards, coyote time on ledges (value from gdp/OpenGD), physics at 240 steps/s.
- Fairness linter (78): rotated hazards checked with the OBB; wave near slopes checked with the circle.

## How to verify in the editor
- GD's "Show Hitboxes" (editor playtest setting) + `capture_frames` to compare sim deaths with real ones.
