# Gameplay Objects

Source: https://www.gdcreatorschool.com/docs/guides/gameplay-1/gameplay-objects/ — by sparktwee and
xplode09 (GD Creator School, Basic Gameplay, Grade 1). Accessed 2026-10-09. Visual reference given by
the guide: level ID 114203114. (No dedicated hazards section on this page.)

## Orbs and pads (paraphrased)
- Orbs need a click while overlapping; pads fire on contact; holding afterwards keeps jumping, except
  spider orb and dash orbs (input can't be held after, like a J-block).
- Strength: **pink < yellow (= normal cube jump) < red**; red orb = yellow pad. Blue flips gravity;
  green = yellow boost + flip; black stomps down; spider orb teleports + flips (2.2; no sideways
  rotation); dash orbs move straight in the arrow direction while held (green; pink also flips).
- Single-use by default; Multi-Activate since 2.1 (default on in platformer). Reverse option exists.
- Toggle orbs activate a group (toggle/spawn behaviour); teleport orb (2.2) uses teleport-trigger setup.

## Portals
- 8 gamemode portals; Free Mode (borderless ship/ball, camera easing/padding settings); platformer
  disables wave and swing.
- Gravity: yellow flips, blue restores normal, green (2.2) swaps.
- Size: pink 0.5x (physics + hitbox change; wave zigzag sharper), green normal.
- Mirror: orange flips direction (visible in-game only), blue restores.
- Speed (5): yellow slowest, blue default, green 2x, pink 3x, red fastest.
- Dual: yellow splits (both die together), blue merges; Free Fly Mode for borderless duals (gamemode
  portals inside duals need it too unless a Camera Mode trigger set it first).
- Teleport portals: to a group spawn point; horizontal teleport since 2.2.

## Special letter blocks (invisible in-game; mark them with deco)
- **D**: wave may touch the block safely (margin). **J**: disables auto-jump on horizontal surfaces
  (not ground/slopes) — use after black orbs. **S**: stops dash orbs. **H**: cube/robot/spider may touch
  a block's underside without dying. **Force blocks** (2.2) push the player. **F** (2.2): flip gravity
  on underside contact.

## Mapping to our tools
- Object IDs in `toolkit/gdlib.py` / `server/.../objects.py`: add D/J/S/H/F block IDs and green
  gravity portal (look up IDs in gddocs/bindings; task 46/51).
- **Linter rules this enables (77):** black/blue orb followed by a landing platform without a J-block
  -> warn (auto-jump bug, also in using-gamemodes); wave segments touching blocks without D-blocks ->
  count margin; high cube launches into ceilings without H-blocks -> warn (pending task 13 for the
  exact H-block guidance).
- Sim (52): implement orb strengths relative to jump (pink < yellow < red) — already in gdphys ORB_MULT;
  add spider/dash orbs and black orb.

## How to verify in the editor
- Place each letter block via `add_objects`, playtest with frames over the case it should fix (e.g.
  black orb onto a platform with/without J-block) and compare frames.
