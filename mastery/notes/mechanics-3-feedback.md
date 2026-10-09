# Mechanics 3 — Feedback

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/mechanics-3-feedback/ — by illusion2, with
contributions by sparktwee (GD Creator School, Intermediate Gameplay, Grade 2). Accessed 2026-10-09.
A general game-design page; GD appears once (rhythm-game responsiveness). No telegraphing or
death-feedback section.

## Key points (paraphrased)
1. Feedback = everything that conveys information to the player (seen, heard or interacted with); it
   shapes how a mechanic feels.
2. Visual feedback: more effect layers make a mechanic feel more important (aim arrow, trail, icon hinting
   strength); strength and function are separate things to communicate.
3. Audio: distinct sounds give mechanics identity (see sound-design guides).
4. Responsiveness: input-to-response delay is itself feedback; rhythm games like GD set near-instant
   expectations.
5. Teach rules through feedback: the player should know when they used a mechanic; don't contradict
   previously learned rules.
6. Consequences (reward/punishment) teach; early clear right/wrong outcomes set the approach.
7. Feedback loops = small information -> response cycles nested in bigger loops.

## Mapping to our work
- Thermal Lock: effects on strong beats double as feedback that the player is "on the music"; orb/pad
  activations get visible responses (pulse/particles) — planned in the effects pass (task 139), within the
  performance budget.
- Rule 5 -> consistency: an object type must behave the same everywhere in the level (no fake orb that
  looks identical to a real one unless the level has taught fakes in a slow part — making-slow-gameplay).

## How to verify
- Effects report: every interactive object type has a consistent look across the level (level model:
  same object ID + colour channel per role).
