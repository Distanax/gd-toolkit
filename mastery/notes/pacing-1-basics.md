# Pacing 1 — Basics

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-1-basics/ — by komatic5, with
contributions by azgamez and creeperiv (GD Creator School, Intermediate Gameplay, Grade 2).
Accessed 2026-10-09. Cites gamedeveloper.com "The Flow Applied to Game Design", "Rational Design,
Part 1", and medicalnewstoday.com on flow.

## Key points (paraphrased)
1. **Pacing** = how the player's attention is held (usually changes in speed or intensity);
   **progression** = anything that evolves across the level.
2. Goal: **flow** ("the zone"). Three conditions: **clear goals and rewards** (players understand how to
   survive and why they died; unclear deaths feel random/unfair; reward progress), **rapid feedback**
   (wrong inputs cause fast deaths so the mistake is obvious), **adequate challenge** (difficulty
   reasonably consistent within a level).
3. **Micro flow** (second to second) is the main consideration while building: rhythm (click patterns
   that repeat; links to sync/note representation), encouragement (a bit more room for error; see
   fairness), positive feedback (e.g. deco that reacts to the player).
4. Pace style is the creator's choice (on-edge vs time to think), each with trade-offs.

## Mapping to our tools
- "Rapid feedback": linter flags delayed-death setups — a mistaken input whose death happens long after
  the input (sim: alternative input -> time until death; > threshold = warn).
- "Clear goals": every death in the sim's alternative-input runs must be against a visible hazard
  (no death off-screen / off-camera).
- Rhythm: repeated click patterns per phrase = the motif data the sync checker already produces.

## How to verify
- Sim alternative inputs per click: report time-to-death; frames for any long-delay case.
