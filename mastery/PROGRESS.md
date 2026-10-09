# GD mastery — progress log

## Resume protocol (every session)
1. `git pull`
2. Read `CLAUDE.md`, this file, `mastery/TASKS.md`.
3. Do the first unchecked task you can do now: [offline] always; [editor] only if the bridge answers
   (`status` tool, or `py -c "from gd_bridge_mcp.client import BridgeClient; print(BridgeClient().call('status'))"`).
   Skip `[blocked: Distanax]` tasks. Never redo checked tasks.
4. One task = one commit + push. Update this file (Status, Next) in the same commit.
5. Anything needing Distanax: exact steps in `mastery/PLAYTEST.md`, mark the task `[blocked: Distanax]`.
6. If nothing is doable, update this file and stop. No empty commits.

## Mission
Learn to plan, lay out, decorate, optimize and polish GD levels at the standard of recent
Featured/Epic 2.2 levels, using gd-bridge in the real editor; capstone = finish **Thermal Lock**
(Creo - Heatseeker, NG 1502369, 127 BPM, first beat 0.055 s; docs/NOTES.md).

## Non-negotiables
- **Ground truth on rating:** only RobTop rates; there are NO published criteria for any tier
  (GDRating.pdf: "There are no specific guidelines for what makes a level rate-worthy"). Stated
  factors only: 30 s minimum / Long 60 s+ standard, clear gameplay, decent visuals, performance
  (lag can block or lower a rate), Upload Guidelines, improving from feedback. Tier standards are
  LEARNED from rated levels and moderator feedback; every claim cites a source or corpus data.
- **Honesty:** never call anything beatable, fun or rate-worthy without evidence (sim results,
  bridge frames, Distanax's playtests). Never fake editor results.
- **Safety:** only touch levels named "CLAUDE ..."; never upload; always state AI involvement in
  level descriptions; recreations of others' levels are study material only, never published;
  downloaded levels/strings never go into git.
- Cite sources: GDCS guide URL + author + accessed date in every note.

## Status
- 2026-10-09: Mission started. Read the five priority-1 guides (planning-a-level, making-a-draft,
  playtesting, asking-for-feedback, the-rating-system), RobTop's GDRating.pdf (text extracted from the
  PDF, 13 pages) and the level FAQ. Wrote TASKS.md (146 tasks, M0-M12).
- 2026-10-09: Task 2 done: Routine "gd-mastery continue" created: id trig_01F3vG1LgUpVQyQoGauYaWWP (https://claude.ai/code/routines/trig_01F3vG1LgUpVQyQoGauYaWWP), cron `43 */3 * * *` UTC, Sonnet 5.5, Default environment, tools Bash/Read/Write/Edit/Glob/Grep/WebFetch/WebSearch. Cloud runs do [offline] tasks only (no bridge access). Delete it in task 146 (claude.ai/code/routines; the API cannot delete).
- 2026-10-09: Task 3 done: mastery/SOURCES.md: all 163 GD Creator School guides from the site navigation with status (read/planned/optional), RobTop rating doc + FAQ, gddocs, gdp, OpenGD, SPWN, Geode bindings.
- 2026-10-09: Task 4 done: notes/robtop-rating.md: stated factors (30 s min / Long 60 s+, clear gameplay, decent visuals, performance can block or lower a rate, Upload Guidelines, feedback), sending, Featured-tab placement (recency, playability, optimization per FAQ), explicit list of what is NOT stated, mapping to our tools. Also fixed the guide count in task 3 (163).
- 2026-10-09: Task 5 done: notes/planning-a-level.md (komatic5): main/secondary ideas, plan fields, reserved resources, scope triangle, MoSCoW, detours; mapped to PLAN.md (task 115) and resource constants in the trigger/deco libraries.
- 2026-10-09: Task 6 done: notes/making-a-draft.md (komatic5, sparktwee): MVP draft, placeholders, execution test, Occam, scientific method for unknown tasks, failing well; mapped to layout-before-deco ordering and drill logs.
- 2026-10-09: Task 7 done: notes/playtesting.md (TDP9, sparktwee): five elements (enjoyability, reliability, playability, balancing, presentation), solo limits + mirror portal, order of familiarity, creators then players; mapped each element to the evidence we can produce (only Distanax judges enjoyability).
- 2026-10-09: Task 8 done: notes/asking-for-feedback.md (komatic5): be specific, describe intent/inspiration/stage, polite receiving, list -> evaluate -> revise -> re-ask; mapped to PLAYTEST.md request format and the decision table for received feedback.
- 2026-10-09: Task 9 done: notes/the-rating-system.md (sparktwee, NotAModerator): roles, lifecycle, tiers, request servers/streams/DMs, known vs unknown (criteria subjective, no checklist), how to improve chances; mapped to the feedback package (venues verified with dates).
- 2026-10-09: Task 10 done: mastery/CHECKLIST.md v0: 12 categories (length/scope, clarity, sync, consistency, fairness, pacing/speed, structure, deco, effects, polish, performance/LDM, presentation), scoring anchors (no evidence = 0, 7 = all criteria evidenced, 9-10 needs corpus comparison + tester feedback). Rules from the mission brief are marked "(pending: task N)" until their guide is read and cited.
- 2026-10-09: Task 11 done: notes/using-gamemodes.md (illusion2, komatic5) + notes/gameplay-objects.md (sparktwee, xplode09): per-mode fit/pitfalls table (no mode switch for 1-2 inputs, orb chains inconsistent, idle ship, wave chokepoints, swing not on ship gameplay, robot hold = note strength), orb strengths, portals, letter blocks D/J/S/H/F; derived linter checks and sim/object-ID follow-ups.
- 2026-10-09: Task 12 done: notes/creating-gameplay.md (mesoionosphere, ChuckOlate): vision, sectioning, hybrid build method, setup groups, motifs with variation, movement flow + clean portal entry, four speed-change kinds + easing. notes/making-sync.md (e.clypse, NotAModerator): pick one layer, tools, speed-portal placement, sync playtesting. GAP: beat-strength order, holds, mode changes on strong beats are NOT in making-sync; CHECKLIST updated (motifs now cited; the rest pending task 21).
- 2026-10-09: Task 13 done: notes/making-consistent-gameplay.md (e.clypse, psytrancegd): error types, object fixes (slope grid gap, pads, teleports, H/J-blocks), physics-based design (platforms reset momentum, portals before orbs, no orb chains, flying-mode transition risks), Options trigger; linter rule table with sim-jitter evidence. CHECKLIST consistency row now cited.
- 2026-10-09: Task 14 done: notes/making-fast-gameplay.md (illusion2, kbtrains, NotAModerator): relative speed, use with musical energy, contrast without huge jumps, readability, click rate, 3-4x portals/timewarp/move-trigger speed. notes/making-slow-gameplay.md (komatic5, Half-Cooked Ramen): slow parts are designed (fakes, slopes, mode switches, correct path first). CHECKLIST pacing/mode-fit rows now cited.
- 2026-10-09: Task 15 done: notes/making-structures.md (komatic5, etherail): essential points, structures point at them, block sides/hazards stop skips, grid snap and simple shapes; grid + skip checks. notes/making-duals.md (e.clypse, naem.less, ChuckOlate): gravity linking (cube+wave share), symmetrical/asymmetrical/2-player, one focus icon, borders 9/10 blocks, offset duals, gimmicks. CHECKLIST structure row cited.
- 2026-10-09: Task 16 done: notes/advanced-hitboxes.md, frame-perfects-alignment.md (MateussDev, NotAModerator), refresh-rates.md (graylasagna): main 30x30 AABB / inner solid / OBB (coyote time) / slope circle, subframes, 240 FPS physics in 2.2, 2.208 click-between-steps makes physics rate-independent, frame-perfect types and mode difficulty order, alignment resets on landing. Linter thresholds: <=1 step = frame-perfect error, 2-5 steps = hard timing. **M2 complete.**
- 2026-10-09: Task 17 done: notes/mechanics-1-intro.md (komatic5, NotAModerator): extensive/immersive/fair mechanics, introduce -> experiment -> avoid burnout, skill chains. notes/mechanics-2-gameplay-loops.md (komatic5, etherail): loops easy/expandable/rewarding, VEIL vs DAYA cases. Mapped to a skill-chain table in PLAN.md and a first-use easing check in the fairness linter.
- 2026-10-09: Task 18 done: notes mechanics-3-feedback (illusion2, sparktwee), mechanics-4-decision-making (intercomprehensible et al.), mechanics-5-limitations-strategy (illusion2 et al.): general game design; applicable parts recorded (consistent object behaviour, effects as feedback, risk/reward on branches, motif reuse in new contexts, readability over strategy for a classic level).

## Next
- Task 19: notes pacing-1 + pacing-2.

## Decisions
- **Corpus through the game, not scraping:** new bridge commands search/download rated levels via GD's
  own GameLevelManager (task 53-55), so "via the bridge" holds and nothing bypasses GD.
- **Copy protection respected:** uncopyable levels are studied from their level data offline (stats,
  renders) and by playing them; only copyable levels are opened in the editor (POLICY.md, task 59).
- **The cloud routine can only do [offline] tasks** (it runs in Anthropic's cloud and can't reach the
  bridge on Distanax's PC). Editor tasks happen in sessions on the PC.
