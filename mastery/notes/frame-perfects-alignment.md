# Frame Perfects & Alignment

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/frame-perfects-alignment/ — by
MateussDev, with contributions by NotAModerator (GD Creator School, Basic Gameplay, Grade 1).
Accessed 2026-10-09.

## Facts (paraphrased)
1. **Frame-perfect** = a timing with a one-frame window. Among the hardest kinds of difficulty and easy
   to miss.
2. Types: **hard timing** ~2-5 frames at N FPS; **common frame-perfect** 1 frame (240 FPS gives more
   margin than lower rates); **frame gate** (only possible at a specific FPS); **swift click** (click and
   release within one frame); **alignment frame-perfect** (depends on position offsets; usually accidental).
3. Snapping-gravity modes (wave, spider) make tight timings easier; curved modes (ship) harder.
   Difficulty by mode, easiest to hardest: wave, spider, ball, cube/UFO, robot/ship (release timing).
4. GD has no pixel-perfects (units, not pixels); the closest thing is a "hitbox perfect".
5. A frame-perfect at N FPS is possible at 2N and above; multiples of 60 line up.
6. **Alignment** = a leftover offset (position, rotation, subframe) smaller than one step, persisting
   until something resets it. X: rotated speed portals, mirror portals, snaps. Y: wave/size portal entry,
   UFO click patterns, ship velocity — **landing on a platform resets Y**. Rotation: orb patterns, ball,
   ship velocity.
7. Making one deliberately (the "macrobuff" method) needs macros + hitbox trail — not our goal; we want
   to **avoid** them.

## Mapping to our tools
- **Fairness linter (78):** for every required input, measure the sim window in physics steps at 240/s;
  flag windows <= 1 step as frame-perfect (error), 2-5 steps as hard timing (warn; acceptable only if the
  target difficulty allows — Thermal Lock is Hard-Harder, so none expected). Report windows in ms too.
- Alignment: prefer designs where platforms reset Y before tight inputs (the guide's reset rule);
  linter warns on tight inputs that follow long airborne sequences (accumulated offset) without a reset.

## How to verify in the editor
- Sim windows are the evidence; Distanax's playtest confirms nothing feels frame-tight.
