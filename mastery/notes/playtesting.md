# Playtesting

Source: https://www.gdcreatorschool.com/docs/guides/main-skills/playtesting/ — by TDP9, with
contributions by sparktwee (GD Creator School, Main Skills, Grade 0). Accessed 2026-10-09.
(The guide cites Canvas "Level 11.0-11.2" on solo testing and playing with designers/non-designers.)

## Key rules (paraphrased)
1. Playtesting fixes errors in gameplay, decoration and trigger usage. There's no single method
   (a minigame and a regular layout break differently). It's iterative and continues through
   creation; no shortcuts.
2. **Five elements, one at a time** (any order):
   - **Enjoyability** — is it fun and interesting? Note frustrating, boring and engaging moments;
     preferences conflict (memory vs sight-readable), so judge for the target audience.
   - **Reliability** — does it run as intended? Learn the level's rules, then try to break them:
     bugs, secret ways, poor optimization. Physics can differ between refresh rates.
   - **Playability** — fair, clear, predictable. Unexplained deaths frustrate; transitions are a common
     source. Good sign: people replay it when they don't have to.
   - **Balancing** — consistent quality of gameplay difficulty AND decoration; some progression is fine;
     riskier paths need proportional rewards.
   - **Presentation** — does it convey its vision: message, theme, style, atmosphere (nothing "off").
3. **Solo testing is limited**: the creator knows the level too well and misjudges difficulty.
   Mirror portal to flip the level and fight muscle memory (only a partial fix).
4. **Order of familiarity**: yourself -> close friends -> useful acquaintances -> strangers. Familiar
   testers gloss over errors, so keep adding fresh eyes.
5. **Creators first, then players.** Creators find major issues and propose fixes; players judge the
   general experience, aesthetics and dynamics (filtered by their skill, taste and hardware).
6. Take in all feedback, drop the ego, ask specific questions (parts, gameplay, deco, "try to break
   it", did the message land), and thank/credit testers.

## Mapping to our work
| Element | Our evidence |
|---|---|
| Enjoyability | Distanax's playtests only (PLAYTEST.md) — never claimed by tools |
| Reliability | simulator windows at 240 tps (task 52), bridge playtests + frames, "break it" tests (skips via block sides) |
| Playability | fairness linter (78): unexplained deaths, transitions, readability; frames at transitions |
| Balancing | difficulty curve from sim windows per section; deco density per screen (80) |
| Presentation | plan vs result review (screenshots per part against PLAN.md) |

- PLAYTEST.md requests name the element(s) being tested and ask specific questions, per rule 6.
- Mirror-portal test: the bridge can add a mirror portal (ID 45) at the start of a copy of the level
  for Distanax's muscle-memory check.
- Refresh rates: the sim runs at GD 2.2's fixed physics rate; Distanax's playtests note his monitor Hz.

## How to verify in the editor
- `playtest` + `capture_frames` across each transition; death positions are visible in frames.
- Mirror check: `add_objects` a mirror portal (45) at the start of a "CLAUDE ... mirror" copy.
