# Making Slow Gameplay

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-slow-gameplay/ — by komatic5,
with contributions by Half-Cooked Ramen (GD Creator School, Basic Gameplay, Grade 1).
Accessed 2026-10-09.

## Key rules (paraphrased)
1. Slow = usually 0.5x or 1x; 2x can be slow in context. Speed is relative.
2. Slow sections give a break from drops, create contrast that makes fast parts satisfying, can build
   up into a drop, and fit calmer song parts. Treating them as filler is a mistake.
3. Players see upcoming obstacles, so **traps that would be unfair at speed can be fair here**.
4. Design: make players think rather than rely on muscle memory; vary click timing and gamemodes more;
   less readable/complex layouts add value; **fake orbs/pads/portals**; slope decisions (ride or jump).
5. Method from the worked example: build the correct path first, then add obstacles/fakes.
6. Examples: Polargeist (all 1x, jump-and-fall gimmicks, fake orbs/pads), ISO (~89 s, fading moving
   objects), Soft Melody (toggle orb gimmick), Gloom (fake portals, placed black glow).

## Mapping to our tools
- Thermal Lock's intro (0-18 s) and groove/pre-drop sections are slow parts: per this guide they
  should carry thinking-based interest (fakes, mode switches, slope choices), not filler.
- Generator rule: in slow sections, allow more varied click timing and mode switches; fakes are only
  placed after the true path exists (correct-path-first, as in the guide).
- Fairness linter (78): a fake object is allowed only where the sim shows a reaction window above the
  slow-speed threshold (the guide's premise is that slow speed makes fakes fair) — threshold from corpus.

## How to verify in the editor
- Frames through the slow section show whether the true path is visible early enough (camera range at
  0.5x/1x).
