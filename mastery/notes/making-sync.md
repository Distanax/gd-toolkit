# Making Sync

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-sync/ — by e.clypse, with
contributions by NotAModerator (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09.

## Key rules (paraphrased)
1. Sync keeps a level engaging and gives clicks a foundation; energy comes from matching clicks or
   movement to the rhythm.
2. **Be selective about the layer** you sync to: melody, bass or percussion. Consistent patterns are
   what players enjoy. Syncing extra clicks to extra notes mostly suits slower songs.
3. **Tools:** Music Line (tracks cube X; arrow triggers, speed portals and X teleports may conflict with
   it as of 2.208; weak for click-sync); editor playtest (air-time/idle sync; editor physics can
   differ from in-game — test in-game too); music guidelines (record lines in level settings; clutter,
   no colours, shifted by input/audio delay); BPM trigger (strict BPM grid, beats-per-bar; not for
   vertical gameplay; use sparingly); speed hack ~0.5-0.75x for precision.
4. **Speed portal position:** the player's collision point decides when the change happens in play; a
   Follow-Player-Y secondary portal can stop players jumping over the original.
5. Avoid Bluetooth audio while building (~2+ blocks of delay); mobile click delay exists.
6. **Playtest sync** with start positions per section, TimeWarp 0.5 + Edit Song -12 (= 50% speed), or
   a speedhack; get a friend to test; take special care with speed portals, arrow triggers, teleports.

## What this guide does NOT say (gap vs the mission brief)
Beat-strength order in 4/4 (1, 3, 2, 4), holds for sustained notes, gamemode/speed changes on strong
beats, consistent syncopation and motif repetition are **not on this page**. Motifs-with-variation is
in creating-gameplay. The rest stays "(pending)" in CHECKLIST.md until a guide states it — expected in
pacing-4-note-representation / pacing-5-intensity (task 21).

## Mapping to our tools
- Our sync is computed, not by ear: beat grid from BPM 127 + first beat 0.055 s (Thermal Lock), x(t)
  from the speed timeline. The sync checker (79) reports each input's offset from the nearest grid
  subdivision and which layer it follows (from the song analysis, task 113).
- Speed portal tall-enough check (77): a speed portal the player could pass above/below without
  touching -> warn (or add the guide's Follow-Player-Y secondary portal).
- Distanax's in-game playtest remains the only check of perceived sync (audio latency differs per
  setup — he should note his audio device).

## How to verify in the editor
- Grid: compute beat x positions and place temporary guide markers in a "CLAUDE ..." copy, then
  `screenshot` regions; or read the level's own guidelines via `get_music`.
- In-game: Distanax playtests; our frames can't judge audio sync.
