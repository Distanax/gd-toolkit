# Making a Draft

Source: https://www.gdcreatorschool.com/docs/guides/main-skills/making-a-draft/ — by komatic5, with
contributions by sparktwee (GD Creator School, Main Skills, Grade 0). Accessed 2026-10-09.

## Key rules (paraphrased)
1. **A draft is a minimum viable product (MVP):** a bare-bones, pre-alpha version with only the
   most basic concepts in place. Purpose: get feedback early, fail fast, save effort later.
2. **Make it as quickly and simply as possible.** Use placeholders (e.g. for decoration). Don't invest
   so much that changing the idea wastes a lot of work.
3. **Execution test:** a well-executed level lets someone immediately tell what you were going for.
   Pitfalls: ideas the editor can't really express; getting lost in execution and losing the intent.
4. **Prioritize** the MVP with MoSCoW (the least ambitious set of goals first).
5. **Save time:** Occam's razor (simplest solution likely best), drop tasks where possible, don't
   fixate on small details, reuse content as placeholders (with permission, replaced later), do
   unavoidable tasks fast.
6. **Unknown tasks -> scientific method:** hypothesis (which objects might work), experiment,
   evaluate (if it works, look for a more efficient way; if not, find where it broke and adjust).
7. **Failing well:** find where low-level logic diverges from the high-level plan; try to fix it
   yourself first; if stuck, ask for help stating the high-level goal first, then the specific
   low-level problem, ideally with a video.
8. **Priority is "make something playable"**; visuals are secondary in the draft.

Gap noted: the page doesn't spell out layout-before-deco or structuring steps beyond "visuals are
secondary" — that ordering comes from other guides and the mission brief.

## Mapping to our work
- Thermal Lock order stays: plan -> playable layout (MVP, placeholder blocks) -> Distanax playtest ->
  structuring -> deco. Layout tasks 117-125 build gameplay only, with no deco.
- Drills follow hypothesis -> experiment -> evaluate, and each drill log records which hypothesis
  failed and why (mastery/LESSONS.md).
- When stuck on an engine question, the note format is: goal, then the precise low-level problem, then
  bridge frames/screenshots as the "video".

## How to verify in the editor
- MVP check: the level can be playtested end to end (`playtest` + `capture_frames`) before any deco
  objects exist (count of non-gameplay objects ~0 in the level model).
