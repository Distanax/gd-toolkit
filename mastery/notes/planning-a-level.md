# Planning a Level

Source: https://www.gdcreatorschool.com/docs/guides/main-skills/planning-a-level/ — by komatic5
(GD Creator School, Main Skills, Grade 0). Accessed 2026-10-09.

## Key rules (paraphrased)
1. **Main idea -> secondary ideas.** A level has one main idea (the destination) and supporting
   secondary ideas with smaller scope, which must relate to the main idea. Secondary ideas are either
   specific to one part, or general across the whole level but less important. They can nest further
   (tertiary... easter eggs). A mind map helps connect them.
2. **Write a plan:** state the main idea, describe each part, and list an asset list plus a section
   for small details/ideas kept for later. Example given: a four-part arc (wasteland -> city rooftops
   and underground -> sewer -> storm-destroyed city).
3. **Resources = IDs, layers, objects.** Reserving groups and colour channels for universal purposes
   is worthwhile for complex plans (e.g. one group for invisible objects, a channel for pure black).
   Document resource use; it slows building but makes pausing/resuming easy.
4. **Scope:** lengths range ~10 s to 3+ min; fit scope to space, resources, time and skill. Trade-off
   triangle (quality / optimization / speed: pick two); balancing all three tends to a middling level.
5. **Prioritize with MoSCoW** (Must, Should, Could, Won't). Build Musts first. If a non-essential
   feature fights you, take a break or replace it; if a Must fails, re-check how necessary it is
   (Occam's razor, see making-a-draft).
6. **Detours:** road closure (too hard), crash (beyond skill/resources), traffic (idea too common ->
   find a more unique path), emergency (real life). Plans stay flexible.

## Mapping to our work
- Thermal Lock PLAN.md (task 115) uses exactly these fields: main idea, secondary ideas per part,
  part descriptions, asset list, details backlog, reserved groups/colour channels/editor layers,
  scope (length, object budget, time), MoSCoW list, known detours.
- Reserved resources become code constants in the trigger/deco libraries (tasks 88-89) so generated
  objects never collide with hand-reserved IDs.
- The deco checker (task 80) can verify reserved channels are used only for their purpose.

## How to verify in the editor
- Reserved groups/channels: `list_objects` / `get_level_string` and count which objects use each
  reserved group (key 57) and channel (keys 21/22) — every use must match the plan's purpose.
- Scope: object count from `status`, length from the level model.
