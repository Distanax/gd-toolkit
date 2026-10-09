# Using Gamemodes

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/using-gamemodes/ — by illusion2, with
contributions by komatic5 (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09.
Examples it cites: Astral Divinity (curved ship), TROLLMACHINE (spider), BUTTON MASHER by Viprin & More
(swing).

## Core rule
Pick each mode for a reason and use what makes it unique; **don't switch modes for one or two inputs**
(e.g. robot for two clicks). One part may use several modes if each has a clear purpose.

## Per mode (paraphrased)
| Mode | Control / physics | Fits | Pitfalls |
|---|---|---|---|
| Cube | click/hold jump, fixed arc, no air control; dies on block sides/bottom | versatile, almost anywhere | fixed path gets boring; **orbs sparingly — orb chains are inconsistent**; prefer pads, gravity changes, head-hitters; holding after black/blue orbs onto a platform auto-jumps (buggy) |
| Ship | hold up / release, momentum-based; mini = more gravity; floatier at higher speed | floaty varied holds; snappy with orbs; tight curves | **idle floating with nothing to do**; keep structure readable. 2.2 made upside-down/dual ship gravity match normal (Legacy option reverts) |
| Ball | click = gravity swap, same path every click; path steeper at lower speed | between snappy and smooth; controlled repetition; slower repetitive melodies building energy | predictable/repetitive; balance clicks vs orbs; blue orb = mid-air ball click |
| UFO | mid-air jumps, consistent arc, farther at speed | snappiest air mode after wave; rapid clicking ascents, set paths; repetition (with gravity portals) | ceiling bump resets momentum; yellow orb higher, pink lower to tune heights |
| Wave | 45 deg (mini ~63.43 deg), no physics, speed-independent shape; dies on any surface except camera-border ground | very fast, sharp, precise; repetition via the trail | most limiting; jarring when mixed; **transitions in/out cause chokepoints**; only blue/green/dash/spider/purple-dash orbs work; D-blocks give margin |
| Robot | hold length = jump height, farther at speed | long holds, emphasized clicks, varying jump size without orbs | micro-clicks frustrate; poor for high-CPS; base jump size on note strength; orbs as seasoning |
| Spider | click = teleport + gravity flip, speed-independent | strong note emphasis, repetition, high CPS; snappiest | precision-heavy, instant deaths with little feedback; can glitch on some platforms |
| Swing | click = mid-air gravity flip, momentum, floatier at speed | big arcs/curves, smooth flow, low-CPS repetitive songs | **don't put swing on ship-style gameplay**; noticeable input lag (gravity trigger can tighten it); blue orb boost; only green dash flips gravity |

Mini: cube/UFO jumps smaller; ship/swing more gravity; wave ~63.43 deg.

## Mapping to our tools
- **Linter (task 77/78):** flag a mode segment with fewer than N inputs (start N=3, tune on corpus);
  flag cube segments where orbs > some share of inputs and any consecutive orb chain; flag ship
  segments with long input-free spans (idle floating, threshold from corpus); flag wave entries/exits
  without margin (chokepoints); flag swing segments whose paths are ship-like (small arcs).
- **Generators (83-86):** encode per-mode fits — ship/swing on smooth/melodic or slow sections, spider
  on high-CPS emphasis, robot hold length from note strength, wave only with speed leeway and D-blocks.
- **gdphys (48-50):** mini constants; wave 45 deg / ~63.43 deg; swing/ship momentum.

## How to verify in the editor
- Mode segments and input counts: level model from `get_level_string` + sim click logs.
- Idle ship / wave chokepoints: `capture_frames` through the segment; sim corridor clearance.
