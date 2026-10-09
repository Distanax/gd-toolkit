# Mechanics 2 — Gameplay Loops

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/mechanics-2-gameplay-loops/ — by
komatic5, with contributions by etherail (GD Creator School, Intermediate Gameplay, Grade 2).
Accessed 2026-10-09. Cites GameAnalytics "How to Perfect your Game's Core Loop" and Daniel Cook
"Loops and Arcs".

## Key rules (paraphrased)
1. A **gameplay loop** = the core actions repeated through a level; loops nest (jumping between platforms
   serves a bigger goal). GD's own core loop is play -> die -> retry.
2. Bad loops: poor controls on custom mechanics, unintuitive use of existing mechanics, no reason to keep
   going.
3. Good loops are **easy to understand** (don't open complex), **expandable** (add mechanics over time so
   repetition keeps paying off), **rewarding** (reward desired actions promptly).
4. Case studies: VEIL (neigefeu) — positive, mechanic visible in the first seconds; DAYA (WerewolfGD) —
   negative, introduced halfway with too little time to adapt and bugs.
5. Build loops from skill chains; each loop should teach something and fit the level's theme (gameplay- or
   story-driven).
6. Process: define the main idea precisely -> quantify skills -> define core mechanics -> prototype an
   expandable loop -> playtest and refine.

## Mapping to our tools
- Thermal Lock (classic, non-mechanic level) still has a loop: per section, the motif set
  (jump/orb/pad patterns tied to the song's phrases). PLAN.md states the loop and how it expands
  section by section (new object, mode or speed per section, never two new things at once — working rule
  to validate against corpus first-use spacing in task 82).
- "Rewarding": the sync checker's strong-beat payoffs (big movements on strong notes) are the reward
  moments; pending task 21 for the exact rule.

## How to verify
- Section spec lists the loop + the one new element per section; level-model first-use table matches it.
