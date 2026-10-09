# Self-review checklist (v0)

Used for the capstone self-review (task 144) and every drill. Each category is scored 0-10 and the
capstone needs **7+ in every category with evidence**, or the category is listed as a known weakness.
A score without evidence is 0. Tools never score enjoyability; only Distanax's playtests do.

Citations: [R] RobTop GDRating.pdf, [F] RobTop FAQ (notes/robtop-rating.md); GDCS guides by note file.
"(pending: task N)" = rule taken from the mission brief; its guide is read and the citation confirmed
in task N. Until then it is a working rule, not a verified one.

**Scoring anchor (all categories):** 3 = known problems remain; 5 = no known problems, thin evidence;
7 = every criterion below checked with the listed evidence and no open issue; 9-10 = 7 plus favourable
comparison against corpus levels of the target tier (numbers cited) and positive tester feedback.

## 1. Length and scope
- [ ] >= 60 s ("Long") [R p.9]; Thermal Lock target ~115 s. Evidence: level-model length.
- [ ] Scope matches the plan's MoSCoW Musts (notes/planning-a-level.md). Evidence: PLAN.md checklist.

## 2. Gameplay clarity
- [ ] Clear gameplay [R p.9]: every input is readable before it's needed (pending: task 20 pacing-3).
  Evidence: fairness linter + frames at each new mechanic.
- [ ] No unexplained deaths, esp. at transitions (notes/playtesting.md "playability").
  Evidence: linter clean + Distanax playtest log.

## 3. Sync
- [ ] Inputs map to chosen song layers; strong notes -> big movements, weak -> small; holds on
  sustains (layer choice: notes/making-sync.md; strong/weak notes + holds pending: task 21 pacing-4 —
  making-sync does not state them). Evidence: sync checker report.
- [ ] Mode/speed changes on strong beats (4/4 strength 1,3,2,4) (pending: task 21 — not in making-sync).
  Evidence: sync checker portal report.
- [ ] Motifs repeat with the music, slight variation (notes/creating-gameplay.md). Evidence: section spec vs layout.

## 4. Consistency
- [ ] No orb chains; portals before orbs; slope transitions with 1-block gaps; H-blocks after high
  launches; J-blocks near blue/black orbs; consistent mode entries; Options-trigger input locks only
  where justified (notes/making-consistent-gameplay.md; slope gap size: the guide says "a gridblock" —
  1 block is our working value). Evidence: consistency linter clean + jitter sim.

## 5. Fairness
- [ ] No frame-perfect inputs (window <= 1 physics step at 240/s) and no hard timings (2-5 steps) for a
  Hard-Harder level (notes/frame-perfects-alignment.md, advanced-hitboxes.md, refresh-rates.md).
  Evidence: sim windows table (min window per click).
- [ ] Coyote-time margins on platform edges; enlarged orb/portal hitboxes or No Touch where needed;
  new mechanics eased in (pending: tasks 16, 20). Evidence: linter + frames.

## 6. Pacing and speed
- [ ] Speed changes follow the music's energy; no 0.5x->4x jumps; successive speed-ups eased;
  3-4x only with musical energy, not overused (notes/making-fast-gameplay.md, making-slow-gameplay.md;
  speed-change kinds/easing: notes/creating-gameplay.md). Slow parts are designed, not filler.
  Evidence: timeline + energy map.
- [ ] Mode fit per notes/using-gamemodes.md: cube versatile, ship smooth/melodic, ball mid-speed
  repetition, UFO floaty, wave sharp/fast with leeway, robot slow holds, spider high-CPS emphasis,
  swing big arcs. Evidence: section spec vs layout.

## 7. Structure
- [ ] Hybrid structuring: simple grid-aligned shapes, structures point at essential points, block
  sides stop skips; no Free Move (notes/making-structures.md; hybrid method: notes/creating-gameplay.md).
  Evidence: grid check, screenshots, sim skip tests + Distanax trying to break it.

## 8. Decoration
- [ ] Decent visuals [R p.9]: block designs clearly differ from the background (value contrast);
  contrast + variety without overcrowding; one cohesive style (pending: tasks 22-23, 29-33).
  Evidence: deco checker (contrast, crowding) + screenshots per part.
- [ ] Organized: editor layer per element type, Z orders spaced (5/10/15), reserved channels for
  white/black/black-blend, triggers grouped (pending: task 22-28). Evidence: level-model resource report.

## 9. Effects
- [ ] Effects support the music (pulses/camera on strong beats), within the performance budget
  (pending: tasks 24-25, 37-44). Evidence: trigger report + perf_stats.

## 10. Polish
- [ ] Layering/blending order, copied-group trigger conflicts, screen edges and camera culling, other
  aspect ratios, pixel misalignment at normal zoom, overscaled dithering (pending: task 27).
  Evidence: polish pass log with screenshots (incl. a non-16:9 window if possible).

## 11. Performance and LDM
- [ ] Performs well; follows the editor's object limits/warnings [R p.9-10]; Featured placement weighs
  optimization [F]. Evidence: perf_stats frame time in playtest, object counts vs corpus median of tier.
- [ ] Covered objects deleted; scale/warp instead of many objects; LDM hides only non-functional
  detail; alpha/hide don't reduce active objects; shaders/blending/animated/Link Visible/dense detail
  budgeted (pending: task 28). Evidence: optimizer report before/after.

## 12. Presentation
- [ ] The level conveys its main idea (thermal lock / homing missile) consistently across parts
  (notes/playtesting.md "presentation"; notes/planning-a-level.md). Evidence: plan vs screenshots review
  + tester answer to "what was this level about?".
- [ ] Description states AI involvement (mission rule). Evidence: feedback package text.
