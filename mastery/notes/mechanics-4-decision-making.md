# Mechanics 4 — Decision-Making

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-2/mechanics-4-decision-making/ — by
intercomprehensible, with contributions by illusion2, komatic5, psytrancegd (GD Creator School,
Intermediate Gameplay, Grade 2). Accessed 2026-10-09. General game design; one GD example
(detail vs optimization vs build-time trade-off).

## Key points (paraphrased)
1. Choices vary by impact and information: **uninformed** (random; no strategy), **obvious** (one option
   clearly best; fine for tutorials), **interested** (partial information; room for preference).
2. **Trade-offs:** no clearly best option; good ones depend on knowing player preferences (playtest),
   otherwise one side is obviously better.
3. **Risk vs reward:** danger scales with payoff; hard to balance; not every game needs it.
4. The level-building trade-off cited: detail, optimization and build time compete.

## Mapping to our work
- Thermal Lock is a linear classic level: in-level choices are minimal by design (fits Hard-Harder).
  Where alternative routes exist (e.g. user coins later), riskier paths need proportional rewards —
  matches notes/playtesting.md "balancing".
- The detail/optimization/time trade-off is managed explicitly in PLAN.md scope (planning-a-level's
  triangle) with an object budget per section.

## How to verify
- Any branching path: sim both routes; risk (min window, hazard density) vs reward (coin/shortcut) logged.
