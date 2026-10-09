# Refresh Rates

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/refresh-rates/ — main writer listed as
unknown, contributions by graylasagna (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09.
Cites KugelBlitZ "Frame Perfects & GD physics" and Stormfly "The 312 Bugs in Geometry Dash (2.113)".

## Facts (paraphrased)
1. Collision is checked every frame; higher rates = more precise input, lower response time; ship is
   affected most.
2. GD was built for mobile and mainly tested at 50-60 Hz; higher rates exposed inconsistencies (portal
   traversal, slopes: launch angle/speed/landing arc).
3. Creators should playtest at several rates (60/144/240/360 Hz).
4. **Outdated notice on the page:** update 2.208 added "Click Between Steps" / "Click On Steps", so all
   players get the same physics regardless of refresh rate; before it, physics depended on framerate.
   The page says much of its content may now be outdated.

## Mapping to our tools
- Our sim models GD 2.2's fixed-rate physics (240 steps/s per notes/advanced-hitboxes.md) with
  click-between-steps input timing, so one simulation stands for every refresh rate.
- Still ask Distanax to note his monitor Hz in playtests (the guide's advice; cheap insurance against
  rate-specific bugs the sim doesn't model).

## How to verify
- PLAYTEST.md requests include "your refresh rate / click-between-steps setting".
