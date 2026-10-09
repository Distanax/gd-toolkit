# Pacing 2 — Progression

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-2-progression/ — by komatic5, with
contributions by Half-Cooked Ramen (GD Creator School, Intermediate Gameplay, Grade 2). Accessed 2026-10-09.

## Key rules (paraphrased)
1. **Macro flow:** larger changes building toward the central idea; once players have muscle memory an
   unchanging level becomes forgettable, so add new (fair) obstacles. Main long-term variables:
   **difficulty and intensity**, which should change over time.
2. Stay between **boredom** and **anxiety/frustration**; more difficulty or intensity is not automatically
   better (intensity clashing with the song is a named failure).
3. **Plan it:** set target difficulty and audience first; **chart difficulty and intensity per section**;
   compare the chart against playtests; limit how much changes between sections (disorienting otherwise).
4. **Ordering:** lower skill -> higher; teach simple mechanics first (Stereo Madness introduces ship in a
   wide space).
5. **Typical whole-level shape:** start slower -> raise intensity toward the drop (climax) -> hold steady or
   change gradually after -> decline or rise again.
6. **Match the song:** calm songs -> calm levels, intense -> intense; level changes follow how the song
   develops.

## Mapping to our tools
- Thermal Lock PLAN.md gets a per-section **difficulty + intensity chart** (planned values), next to the
  song energy map; after layout, the tools compute measured proxies per section — difficulty: min sim
  window, required CPS, hazard density; intensity: speed, CPS, effect density — and plot plan vs measured.
- Linter: section-to-section jumps in either proxy above a threshold -> warn ("limit change between
  sections"); intensity that contradicts the song energy map -> warn.
- The existing Thermal Lock section map (docs/NOTES.md: intro 1x -> drop 2x -> ... -> drop 2 wave climax
  -> ending) already follows rule 5; task 116 makes it explicit.

## How to verify
- Plan-vs-measured chart per section (generated), plus Distanax's playtest notes per section.
