# Pacing 3 — Fairness

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-3-fairness/ — by TDP9, with
contributions by NotAModerator (GD Creator School, Intermediate Gameplay, Grade 2). Accessed 2026-10-09.

## Key rules (paraphrased)
1. A level is fair when it can clearly teach its rules and mechanics; the player should feel in control.
   The creator's own skill and bias distort their judgment of fairness.
2. Unfairness comes from sudden or buggy progression, the "unknown", punishing what isn't the player's
   fault, and demanding perfection.
3. **Techniques:**
   - **Coyote time:** slightly enlarge platforms so a jump still works a few frames after leaving the
     edge (platformer mode has it built in since 2.206).
   - **Lenient hitboxes:** scale up orbs/portals; for hazards, turn on **No Touch** and place smaller
     hitboxes inside the visible shape.
   - **Predictability:** structure keeps the path straightforward; random events within a reasonable
     timeframe; never contradict intuition (a yellow orb acting like a blue one).
   - **Helping:** visual hints; careful nerfs/invisible helpers; remove unintended choke points and
     slow spots.
   - **Mechanic easing:** introduce a gimmick gradually before complex uses.
4. **Micro pacing:** once the player is in flow, give extra leniency (found by playtesting).
5. **Don't overdo it:** too much help removes meaningful input ("hand-holding"; SLAM by Rafer, 7 stars,
   mostly beaten first try). Aim: enjoyable, finishable by most of its audience, identity intact.

No numeric thresholds are given (platform margin, hitbox scale, windows) — ours come from the sim and
corpus (task 82). Frame-perfects: notes/frame-perfects-alignment.md.

## Mapping to our tools — fairness linter (task 78)
| Rule | Check |
|---|---|
| coyote time | sim: jumps required within N px of a platform edge with no margin block -> warn; generators extend platforms by a margin (trajgen already adds ~1.5 blocks early / late margin) |
| lenient hitboxes | orbs/portals at scale 1.0 on tight paths -> suggest scale (e.g. 1.2) — value TBD from corpus |
| No Touch + inner hitbox | hazard deco without No Touch whose visible shape exceeds its real hitbox -> info |
| predictability | same object ID must have the same behaviour everywhere (no recoloured/reskinned look-alikes of other orb types) |
| mechanic easing | first use of each object/mode: wider window + lower density than later uses |
| hand-holding | count helper objects (invisible blocks, nerfs) per section; a high share -> review (balance) |

## How to verify in the editor
- Frames at platform edges and orb/portal contacts; Distanax's playtest for "felt in control".
