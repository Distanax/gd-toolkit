# Making Consistent Gameplay

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-consistent-gameplay/ — by
e.clypse, with contributions by psytrancegd (GD Creator School, Basic Gameplay, Grade 1).
Accessed 2026-10-09.

## Definition
Consistent = the level plays about the same every attempt: small input differences (click timing,
hold length) must not cause large path changes, and every death should be understandable.

## Error types (paraphrased)
1. **Unjustified deaths:** a slightly early jump / early-late orb click / missed gravity-portal landing
   puts the player on a lethal path before they can react.
2. **Unfair transitions:** mode changes depend on momentum and position at the portal (clicking right
   before a ball portal; holding vs releasing wave before a ship portal).
3. **Slopes:** landing/jumping at different points gives different heights; higher speed amplifies it.
4. **Orb chains** (consecutive orb inputs): among the least consistent patterns.

## Fixes
**Objects:** leave a grid-block gap at slope transitions to reset Y (the page doesn't give a number
beyond "a gridblock"; the brief's "1-block gap" is our working value); pads stabilize mode transitions
(not for wave); teleport portal/trigger to a fixed position; **H-blocks** on top of blocks as a roof
that realigns over-high orb launches; **J-blocks** stop auto-jumps after black/blue orbs near landings.
Drawbacks: they reset momentum, can create new bugs, may look/feel unnatural.

**Physics-based design (best, hardest):** force the intended route; rely on **platforms/structures**
(they reset momentum); orbs/pads are consistent when hit at about the same spot, and most reliable when
used to jump/fall off a platform; avoid orb chains. Flying modes are the most inconsistent in
transitions (orbs with ship/swing, wave spam, UFO with gravity changes/slopes, clicks right before any
portal). **Place portals before orbs**; nudging a portal slightly ahead of an orb fixes inconsistent
orb-to-portal clicks. A black orb next to a yellow one can force the intended landing block.

**Options trigger:** briefly disable/limit input in transitions (fast gameplay, duals — disable the
player who shouldn't act; unlinked dual gravity must then be handled manually), after blue/black orbs
where J-blocks are imperfect. Drawbacks: players feel loss of control; practice-mode respawns can skip
the triggers; must stay fair.

Process: playtest every click; study consistent and inconsistent levels; get outside testers.
(D-blocks are not covered on this page; see gameplay-objects.)

## Mapping to our tools — consistency linter (task 77)
| Rule | Check |
|---|---|
| orb chains | 2+ orb inputs with no ground/platform contact between them -> error (count chain length) |
| portals before orbs | an orb within ~1-2 blocks before a portal in the path -> warn (suggest moving the portal ahead) |
| slope transitions | slope end followed by a jump/portal without a 1-grid flat gap -> warn |
| H-blocks | sim: launch apex range across the click window exceeds a threshold and a ceiling exists -> suggest H-block |
| J-blocks | black/blue orb with a landing surface reachable while holding -> require J-block or Options trigger |
| mode entry | sim the click window jitter: spread of (y, vy) at each portal; large spread -> warn |
| flying transitions | flag orbs inside ship/swing, wave spam (CPS above a threshold), clicks needed within N ms before a portal |
- The sim is the evidence: jitter every click across its window and measure path divergence; GD's own
  playtest frames confirm the risky spots.

## How to verify in the editor
- Build the bad and fixed version side by side in a "CLAUDE drill consistency" level; playtest each
  with `capture_frames` at early/late timing (Distanax's manual runs, or start positions).
