# Creating Gameplay

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/creating-gameplay/ — by mesoionosphere,
with contributions by ChuckOlate (GD Creator School, Basic Gameplay, Grade 1; updated 2026-06-04).
Accessed 2026-10-09. The author frames it as pointers, not a rulebook.

## Key rules (paraphrased)
1. **Vision first:** standalone layout or to be decorated; aim (mechanically impressive, fun, unique,
   all-rounder). Pick a song you won't tire of and can "see" gameplay in.
2. **Section the song:** predrop, drop, optional post-drop. Length bands used by the author: Mini
   < 50 s, Standard 50 s - 1:59, XL > 2:00.
3. **Building methods:** base-first (common, tedious), structure-first (author: produces strange
   gameplay, not recommended), **hybrid** (author's preference): base gameplay for a section, then
   structure it, then move on.
4. **Setup triggers** the author uses: group 1 invisible, group 2 half opacity, group 3 follows player
   Y (or the Hide Invisible option instead of the invisible trigger). A teleport portal can lift the
   player off the ground for floating-structure layouts.
5. **Gamemode fits the song's character** (e.g. short retro sounds -> small spontaneous jumps;
   mini-cube/mini-UFO for grounded gameplay).
6. **Motifs:** elements repeat with the song's repetition, varied slightly — no lazy copy-paste.
7. **Movement flow:** every movement sets up the next (e.g. prepare vertical room before a staircase);
   set up movement before a gamemode portal so entry is clean and consistent.
8. **Speed changes, four kinds:** short incremental (one step, briefly), long incremental (one step,
   stays), short burst (2+ steps briefly; impact on kicks/snares — steep vertical movement gives a
   similar effect), long burst (2+ steps, extended; typical big-drop start). **Speed easing:** several
   increments with spacing widening as speed rises; skip it when a sudden burst is the point.
9. Structuring/effects are secondary to base gameplay; don't overdo; moving structures add life.
10. **Review:** fun-focused -> replay for annoying parts; mechanical -> check missed/poorly represented
    notes; take a break and return fresh; peer review from players who give accurate mechanical
    feedback; feedback conflicting with the vision can be set aside.

(No explicit difficulty/fairness guidance on this page — see pacing-3, task 20.)

## Mapping to our tools
- **Hybrid method** = Thermal Lock order: layout a section -> structure it -> next (tasks 117-130 are
  per section; structuring tasks can interleave per the guide).
- **Motif check (sync checker, 79):** detect repeated input patterns aligned to repeated song phrases;
  flag exact copies (identical object strings shifted) as "copy-paste" for review.
- **Mode-entry rule (77):** the cube/ship state entering a portal must be the same on every attempt —
  sim: portal entry y/velocity variance across the click window must stay small.
- **Speed-change classifier (78):** label each speed change as short/long incremental or burst
  (steps = speed index difference, duration = time until next change); flag bursts not on a strong
  musical event (needs energy map) and ramps without widening spacing.
- Setup groups 1-3 go into the reserved-resource plan (task 115).

## How to verify in the editor
- Speed plan: `list_objects` with speed portal IDs 200/201/202/203/1334 -> timeline.
- Portal entry consistency: sim with clicks jittered across the window; frames at the portal.
