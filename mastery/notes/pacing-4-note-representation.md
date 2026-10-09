# Pacing 4 — Note Representation

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-4-note-representation/ — by
illusion2, with contributions by sparktwee (GD Creator School, Intermediate Gameplay, Grade 2).
Accessed 2026-10-09.

## Key rules (paraphrased unless quoted)
1. Sync = timing a sound with a visual or an input. Notes differ in pitch, volume, texture.
2. **Strength -> movement size:** "Small player movements = Weak impact", "Big player movements = Strong
   impact". **Holds add emphasis** (longer attention than a click). Structures, deco pulses and effects
   are secondary tools. Not absolute (VINDICATION by Chunlv1: one hold input, pads/slopes carry sync,
   stronger beats get bigger pad movements).
3. **Sound division:** give each song layer its own kind of representation (clicks for main beats, pads
   for secondary drums, long sweeping structures for strings; Fallen Land: oboe = ship, violin = cube;
   Wir Fliegen: spider orbs for electric guitar, robot holds for the fast guitar layer).
4. **Direction:** sharp reversals/angles = strong notes, shallow = weak; turns must match clicks (don't let
   three clicks make four sharp turns). Direction can hint pitch (subtle).
5. **Path (macro):** smooth curves feel welcoming, sharp angles alarming; less movement = calm, more =
   intense; large position shifts signal change; a basic comprehensible path beats a complex
   incomprehensible one.
6. **Click patterns** should be engaging, representative of the song, and fit the learning curve.
7. **Repetition** aids memory, emphasis and learning; emphasis needs contrast; overuse dulls it.
   **Breaking** a repeated pattern on a repeated musical part breaks the level's own rules — only with a
   good reason (e.g. syncopation), well hidden; easier to get away with in slower/easier levels.
8. **Form:** A-B-A-C, A-B-A-B; path shifts mark new sections; antecedent/consequent phrasing.
9. **Beat strength:** 4/4 order "1 3 2 4"; 3/4 "1 3 2"; the first beat of every other bar is stronger at
   half tempo. Clicking on strong beats is a good default when not syncing every note; clicks landing on
   weak beats instead of strong ones feel misleading.
10. **Syncopation:** a note just before/after a strong beat, with the strong beat still emphasized by
    background elements; keep it consistent (overuse feels weird, esp. fast/hard parts); a weak click right
    before a strong one sets it up ("baby notes").
11. **Gamemode changes land on significant (strong) beats, not offbeats.** (No explicit rule for speed
    changes on this page.)
12. Odd meters: split into even groups (5/4 = 3+2; 7/4 as 4+4+2+2+2 rather than 4+4+4+2).

## Mapping to our tools — sync checker (task 79)
- Beat grid from BPM + first beat; per input: beat position within the bar -> strength rank (1,3,2,4),
  offset from grid in ms.
- **Errors/warnings:** gamemode portal not within a tolerance of a strong beat (1 or 3) -> warn (rule 11);
  largest movements (apex height change, orb/pad launches) not on the strongest notes of their phrase ->
  info (rule 2); repeated musical phrase with a different click pattern -> warn unless marked intentional
  syncopation (rule 7); turns without clicks / clicks without turns in wave -> warn (rule 4).
- **Speed changes on strong beats** = our extension of rule 11 (same reasoning: a very significant change)
  — labelled "working rule", not a guide citation.
- Sound division: section spec assigns a layer to each input type (task 116).

## How to verify
- Sync report per section; Distanax's in-game playtest for perceived sync (audio latency differs).
