# Using Deco Objects

Source: https://www.gdcreatorschool.com/docs/guides/deco-1/using-deco-objects/ — by komatic5 (GD Creator
School, Basic Deco, Grade 1; updated 2026-09-24). Accessed 2026-10-09.

## Key rules (paraphrased)
1. **Shape first** (then colour, then texture): the right shape makes things recognizable. Reduce to basic
   shapes (circles, rectangles, triangles) before detailing; scale/warp to reach complex shapes; objects
   are puzzle pieces (rotate, warp, recolour).
2. **Custom shapes:** polygons from triangles/rectangles or points joined by lines/glow (outlines); fill
   corners with corner pieces so it doesn't look amateurish. Curves from stacked lines/rectangles, rotating
   around a centre (check rotation centres), warping pre-made curves for big circles.
3. **Colour:** split into brightness, saturation, hue; one channel per target colour; choose by eye.
4. **Texture via stacking** (advanced, low priority): **blending** is additive (invisible over black,
   disappears on white; keep blended stacks simple; hue-shifting gradients; non-blending objects on top of
   blending ones must be much brighter or it looks foggy) and **opacity** (transparency, partial masks,
   blur from low-opacity copies). Stacks must stay subordinate to main objects.

## Mapping to our tools
- Deco library (89): build complex shapes from few scaled/warped primitives (also the optimizer's
  "scale/warp instead of many objects", task 28).
- Deco checker (80): non-blending objects layered over blending ones must have much higher value
  (brightness) than the blend underneath — compute from channel colours; flag "foggy" cases.

## How to verify
- Screenshots of each block design at normal zoom.
