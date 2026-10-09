# Making Structures

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-structures/ — by komatic5, with
contributions by etherail (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09.

## Key rules (paraphrased)
1. Structures shape how the level plays and how intuitive it feels, guide the player, make skips
   harder, and — being the most common element — strongly affect decoration. Messy structures make a
   level unreadable even with good deco.
2. **Essential points** = what the player interacts with (platform tops) and hazards to avoid. Other
   structure should **point toward** essential points. Misleading essential points (a platform top that
   suggests "don't jump") are fixed by adding a hazard that makes the required action obvious.
3. **Prevent skips:** block sides kill, so use them to stop cheesing; find skips by playtesting; fix by
   reshaping or adding hazards; last resort: a spike wall at floor and ceiling (a similar setup blocks
   Noclip).
4. **Grid:** no Free Move when structuring; snap to the grid (or half/quarter grid); simple shapes
   (blocks, slopes); leave complex details to the decorator.

## Mapping to our tools
- Generators already snap to the grid; Thermal Lock S1's open question (trajgen snapping blocks to
  multiples of 15 so some land off the 15+30k grid) violates rule 4 — fix in task 114.
- **Structure checker (part of 77/80):** off-grid solid objects (x or y not on 30, 15 or 7.5 multiples)
  -> warn; free-moved rotations -> warn.
- **Skip test (78):** sim alternative inputs (jump earlier/later, hold, no click) and check whether any
  reaches a later safe point while skipping required inputs — if so, a block side or hazard is missing.

## How to verify in the editor
- `list_objects` positions -> grid check; skip tests by sim, then Distanax tries to break it (playtesting
  "reliability").
