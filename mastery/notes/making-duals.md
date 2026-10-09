# Making Duals

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-duals/ — by e.clypse and
naem.less, with contributions by ChuckOlate (GD Creator School, Basic Gameplay, Grade 1).
Accessed 2026-10-09.

## Key rules (paraphrased)
1. Both icons react to clicks; default opposite gravity, one's change flips the other. Different modes
   have independent gravity — except cube + wave, which still share gravity.
2. **Types:** symmetrical (same mode, mirrored; easiest), asymmetrical (own paths; usually different
   modes), 2-player mode (independent control; always independent gravity).
3. **Focus:** don't give both icons equal focus (hard to read, play, build). Build one main path; let the
   other "float along" with enough design to feel purposeful. Switch focus by moving one icon to the
   screen top/bottom while the other is in the middle.
4. **Borders/camera:** default dual height 9 blocks; ship/wave/UFO/swing make it 10; camera zoom
   expands; Free Mode removes borders but must be set on every mode change inside the dual. Camera
   follows player 1 (Advanced Follow + static camera to follow P2).
5. **Offset duals** via teleport trigger/portal/orb; keep focus on one icon; smooth focus switches
   (short auto part or eased gameplay).
6. **Gimmicks:** Unlink Dual Gravity; Disable Controls P1/P2 (sync-only icon, precise hand-overs);
   per-player gravity trigger; reverse only player 2 (camera follows P1); arrow-trigger duals (wave
   popular for consistency; teleports keep both visible).
7. Examples: Verdant Landscape (Nisha), Diligence (Davphla), Floating Outskirts (YoReid), Codependence
   (TCTeam), Resonance (Human/Angel GD), Out Of This World (Perox08), Magic Touch (DawuU).

## Mapping to our tools
- Sim (52) needs dual support: two players sharing input, gravity linking rules (incl. cube+wave), and
  border heights 9/10 blocks.
- Linter: dual sections where both icons require inputs at different times with comparable hazard
  density -> warn "equal focus"; reverse on P1 -> warn.
- Thermal Lock currently plans no duals; if one is added (Should/Could), use asymmetrical with one
  focus icon.

## How to verify in the editor
- Frames through the dual (both icons visible, borders as expected); Distanax playtest for readability.
