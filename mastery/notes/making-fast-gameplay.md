# Making Fast Gameplay

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-fast-gameplay/ — by illusion2 and
kbtrains, with contributions by NotAModerator (GD Creator School, Basic Gameplay, Grade 1).
Accessed 2026-10-09.

## Key rules (paraphrased)
1. **Speed is relative** to the surrounding sections (2x after 0.5x feels faster than 2x alone). Fast
   parts add intensity and contrast; without them key moments feel anticlimactic. **Balance it** —
   overuse makes a level repetitive and tiring.
2. **When:** where the song picks up tempo/energy (a drop); frequent speed changes can build toward one.
3. **Contrast without huge jumps:** a small tempo increase in the song shouldn't become half speed ->
   4x. To make a sudden boost stand out, slow the part before it (example: Glorescent). For a gradual
   rise, speed up slowly (Commatose).
4. **Predictability:** very fast or sudden changes are hard to read; simplifying gameplay helps
   (Königstein). Unreadable-on-purpose is allowed if intended (We can dream).
5. **Click rate** raises intensity and shrinks error room; click patterns matching the song help
   learning (POLYATOMIC).
6. **Mechanics:** speed portals (fast sections typically 3-4x; Alone Intelligence); timewarp (changes
   game speed incl. gravity; trial and error; best where physics matter little — OVERDOSE PARTY); move
   triggers moving the level toward the player (looks odd in editor playtest; teleport for the reverse
   risks desync and breaks start positions — dropdead).

Not on this page: numeric easing curves, an explicit "never 0.5x->4x" rule (implied by rule 3), wave
leeway (see using-gamemodes).

## Mapping to our tools
- **Speed linter (78):** flag speed jumps of 3+ steps (0.5->3x, 0.5->4x, 1->4x) unless the previous
  section was deliberately slowed and the music has a matching energy jump (energy map from the song
  analysis); flag fast (3-4x) time share above a corpus-derived ceiling; flag 3-4x sections over
  low-energy music.
- **Readability:** at 3-4x, require simpler patterns: max CPS and min reaction time per new obstacle
  from sim + corpus stats (thresholds TBD from the corpus, task 82).

## How to verify in the editor
- Speed timeline from `list_objects` (IDs 200/201/202/203/1334) against the energy map; frames at each
  speed-up for readability.
