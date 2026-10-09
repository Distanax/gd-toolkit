# How To Decorate

Source: https://www.gdcreatorschool.com/docs/guides/deco-1/how-to-decorate/ — by komatic5, with
contributions by galofuf, NotAModerator, poryii (GD Creator School, Basic Deco, Grade 1; updated
2026-05-31). Accessed 2026-10-09. Examples cited: Royal Roost Ruins (Glubfuberz), And Ever (Galofuf),
Azimuth (Knots).

## Key rules (paraphrased)
1. **Deco elements:** block designs (make the path clear), gameplay-object deco (e.g. glow), background
   (must feel distinct from blocks so scenery isn't mistaken for gameplay), foreground (less common, often
   darkened), air deco (same layer as blocks: arrows, connectors, particles), animations, visual effects.
   Not every level needs all of them.
2. **Styles:** classic design (game objects as they are, combined cleverly) vs custom art (new assets from
   objects; more variety, harder). Modern/glow/effect are subgenres — aesthetic choices.
3. **Organize:**
   - **Editor layers:** one per major shape/detail type; add layers when selecting something takes more
     than ~20 s; document them.
   - **Z layers:** one per deco element (e.g. blocks T1, background B1); complex deco spans ranges (e.g.
     background B5-B3, blocks B2-T1); **background must never render above blocks** — ranges must not
     collide; tilesets, blending, animated objects, particles complicate layering.
   - **Z order** gaps of ~3-5 (example 5, 10, 15) leave room for later changes.
   - **Colour channels:** reserve some (author: 1 white, 2 black, 3 invisible blending black; many use 1
     or 2 for black); use plenty of channels.
   - **Triggers:** same editor layer as the deco they affect, sorted by group ID ascending, in separate
     editor space from the deco.
4. **Workflow:** idea -> inspiration + references -> **basic shapes and colours first** -> details (don't
   overload small spaces) -> feedback -> repeat. Don't copy a reference; add your own elements.

## Mapping to our tools
- Deco library (89) constants: editor layer per element type; Z layers (background B5-B3, blocks B2-T1 as
  the default scheme); Z orders in steps of 5; reserved channels 1 white, 2 black, 3 blending black (fits
  the planning guide's reserved-resources advice).
- **Deco checker (80):** background objects (by planned layer/role) with Z above any block object -> error;
  consecutive Z orders without gaps -> info; reserved channels used for anything else -> warn; triggers
  mixed into deco editor space -> info.
- Workflow for Thermal Lock deco tasks 134-138: base shapes + colours per section first (134-137), details
  after (138).

## How to verify in the editor
- `list_objects` with object strings: Z layer key 24, Z order 25, editor layer 20, channels 21/22; check
  ranges per role; screenshots in preview.
