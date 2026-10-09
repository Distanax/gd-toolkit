# Mechanics 1 — Intro

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/mechanics-1-intro/ — by komatic5, with
contributions by NotAModerator (GD Creator School, Intermediate Gameplay, Grade 2). Accessed 2026-10-09.
Cites "Adapting Cognitive Task Analysis to Elicit the Skill Chain of a Game" and Lost Garden's
"The Chemistry of Game Design".

## Key rules (paraphrased)
1. A **mechanic** is a rule or gimmick added to the level's existing gameplay; it changes how the player
   approaches the level.
2. Good mechanics are **extensive** (used enough to matter), **immersive** (visuals/deco/audio sell and
   hint at it; SFX trigger since 2.2), **fair and engaging** (follow the level's normal rules, support flow).
3. **Introducing:** (1) introduction — show the task and make sure it's understood (core controls must be
   taught); (2) experimentation — give time to try it (Hollow Knight's dash: flat ground -> over pits ->
   midair); (3) avoid **burnout** — a mechanic used inconsistently stops mattering (early burnout = never
   learned; late burnout = meaningful uses become rare).
4. **Combining** mechanics creates new ones; tell players up front if they should apply known skills, or
   let them discover combinations if mastery-by-discovery is the goal.
5. **Skill chains:** the ordered skills the player learns, starting from pre-existing skills (basic GD
   controls are assumed). Flowchart them: skills to start, skills to win, skills needing explicit feedback.
6. **Validate by playtesting** (record behaviour): early burnout -> fix the introduction; late burnout ->
   fix how it's reused later.

## Mapping to our tools
- Thermal Lock's PLAN.md includes a **skill chain**: which modes/objects/mechanics each section introduces,
  where each is first shown in a low-risk setting, and where it recurs (burnout check).
- Fairness linter (78) "ease new mechanics in": the first occurrence of an object type/mode in the level
  must have a larger sim window and lower hazard density than its later occurrences (thresholds from corpus).
- The "homing missile" motif in Thermal Lock is a candidate mechanic: it must be extensive (recurring), and
  readable from deco.

## How to verify
- Skill-chain table vs level-model occurrences (first-use positions per object type and mode).
- Distanax's playtest notes for confusion at first uses.
