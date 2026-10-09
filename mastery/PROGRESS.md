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

## Next
- Task 2: create the "gd-mastery continue" routine. Then tasks 3-10 (sources index, priority-1 notes,
  checklist v0).

## Decisions
- **Corpus through the game, not scraping:** new bridge commands search/download rated levels via GD's
  own GameLevelManager (task 53-55), so "via the bridge" holds and nothing bypasses GD.
- **Copy protection respected:** uncopyable levels are studied from their level data offline (stats,
  renders) and by playing them; only copyable levels are opened in the editor (POLICY.md, task 59).
- **The cloud routine can only do [offline] tasks** (it runs in Anthropic's cloud and can't reach the
  bridge on Distanax's PC). Editor tasks happen in sessions on the PC.
