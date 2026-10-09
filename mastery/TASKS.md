# GD mastery — task list

Mission, rules and resume protocol: `mastery/PROGRESS.md`. One task = one commit, pushed at once.
Tags: **[offline]** = code/docs/research, any session (incl. the cloud routine).
**[editor]** = needs Distanax's PC on with GD + the bridge; if the bridge is unreachable, skip to the
next [offline] task — never fake editor results. **[blocked: Distanax]** = steps in `mastery/PLAYTEST.md`.
Notes go to `mastery/notes/<guide>.md` (one file per guide, cited). Lessons go to `mastery/LESSONS.md`.

## M0 — Setup
- [x] 1. [offline] mastery/ scaffolding (TASKS, PROGRESS, PLAYTEST, LESSONS, notes/, corpus/), resume protocol, CLAUDE.md pointer
- [x] 2. [offline] Create the "gd-mastery continue" routine (every 3 h), record its id
- [ ] 3. [offline] mastery/SOURCES.md: every guide URL from the GDCS index with status, RobTop docs, gddocs, gdp, OpenGD, SPWN

## M1 — Ground truth + main skills (priority 1)
- [ ] 4. [offline] notes/robtop-rating.md — GDRating.pdf + FAQ: what is stated, what is NOT (no tier criteria)
- [ ] 5. [offline] notes/planning-a-level.md
- [ ] 6. [offline] notes/making-a-draft.md
- [ ] 7. [offline] notes/playtesting.md
- [ ] 8. [offline] notes/asking-for-feedback.md
- [ ] 9. [offline] notes/the-rating-system.md
- [ ] 10. [offline] mastery/CHECKLIST.md v0: self-review categories (gameplay, sync, consistency, fairness, pacing, deco, effects, performance, LDM, presentation), each criterion cited, with the evidence that proves it

## M2 — Basic gameplay notes (priority 2)
- [ ] 11. [offline] notes: using-gamemodes, gameplay-objects
- [ ] 12. [offline] notes: creating-gameplay, making-sync
- [ ] 13. [offline] notes: making-consistent-gameplay
- [ ] 14. [offline] notes: making-fast-gameplay, making-slow-gameplay
- [ ] 15. [offline] notes: making-structures, making-duals
- [ ] 16. [offline] notes: advanced-hitboxes, frame-perfects-alignment, refresh-rates

## M3 — Intermediate gameplay notes (priority 3)
- [ ] 17. [offline] notes: mechanics-1-intro, mechanics-2-gameplay-loops
- [ ] 18. [offline] notes: mechanics-3-feedback, mechanics-4-decision-making, mechanics-5-limitations-strategy
- [ ] 19. [offline] notes: pacing-1-basics, pacing-2-progression
- [ ] 20. [offline] notes: pacing-3-fairness
- [ ] 21. [offline] notes: pacing-4-note-representation, pacing-5-intensity

## M4 — Basic deco notes (priority 4)
- [ ] 22. [offline] notes: how-to-decorate, creating-details, using-deco-objects
- [ ] 23. [offline] notes: making-blocks, making-backgrounds
- [ ] 24. [offline] notes: making-air-deco, making-animations, making-effects
- [ ] 25. [offline] notes: using-shaders, parallax
- [ ] 26. [offline] notes: layering-masks, blending-masks, other-masks
- [ ] 27. [offline] notes: polishing
- [ ] 28. [offline] notes: optimizing, low-detail-mode
- [ ] 29. [offline] notes: deco-styles (+ animated-objects, detail-objects)

## M5 — Intermediate/advanced deco notes (priority 5)
- [ ] 30. [offline] notes: color-1-basics, color-2-using-colors, color-3-color-schemes
- [ ] 31. [offline] notes: color-4-color-grading, color-5-human-perception
- [ ] 32. [offline] notes: light-1-basics, light-2-making-shadows, light-3-value
- [ ] 33. [offline] notes: light-4-reflections, light-5-texture
- [ ] 34. [offline] notes: animation-1-timing-easing, animation-3-follow-through, animation-5-transitions
- [ ] 35. [offline] notes: perspective-1..4
- [ ] 36. [offline] notes: deco-3 elements-of-decoration, evenness

## M6 — Trigger notes (priority 6) + programmatic triggers
- [ ] 37. [offline] notes: triggers-1 trigger-intro, color, pulse, groups, alpha, toggle
- [ ] 38. [offline] notes: triggers-1 move-rotate, follow, scale, keyframes, advanced-follow
- [ ] 39. [offline] notes: triggers-1 area-triggers, animate, gradient, spawn-particle, screen-filters, enter-triggers
- [ ] 40. [offline] notes: triggers-1 start-pos-end, reverse-arrow, camera-triggers, gravity-teleport-timewarp, show/hide, gp-options
- [ ] 41. [offline] notes: triggers-1 song/sfx/bpm, spawn, on-death, touch, collision, event-link, sequence, random
- [ ] 42. [offline] notes: triggers-1 stop, pickup, count, item-edit/comp/pers, time, bg/mg-change, ui/link-visible, reset, fixing-bugs, stacking
- [ ] 43. [offline] notes: triggers-2 the-trigger-process, spawn-order, priority-order
- [ ] 44. [offline] notes: triggers-2 using-remap-properties, making-loops, making-optimized-setups, making-functions
- [ ] 45. [offline] notes/spwn.md: SPWN (Spu7Nix) — model, how HOW/WHAT-style trigger systems were built, what to copy into our Python trigger library
- [ ] 46. [offline] docs/TRIGGER_KEYS.md: property keys for color/move/rotate/alpha/toggle/spawn/pulse/scale/keyframe/camera/shader/area triggers from gddocs, cross-checked against corpus trigger strings
- [ ] 47. [editor] Verify TRIGGER_KEYS in-game: build one trigger of each kind via the bridge, playtest + frames, confirm the effect

## M7 — Physics + hitboxes (engine facts the tools rely on)
- [ ] 48. [offline] gdphys: ship physics (gdp/OpenGD), units/s and per-tick
- [ ] 49. [offline] gdphys: ball, spider, robot (incl. robot hold boost)
- [ ] 50. [offline] gdphys: UFO, wave (normal + mini ~63.4 deg), swing
- [ ] 51. [offline] gdphys: hitbox table (player per mode/mini, spikes, saws, orbs, pads, portals, slopes) from OpenGD
- [ ] 52. [offline] Simulator core at 240 ticks/s (2.2), all modes, input windows in ms and ticks; regression vs sim2 cube results

## M8 — Bridge extensions for study
- [ ] 53. [offline] Research 2.2081 bindings: GameLevelManager search (GJSearchObject, getOnlineLevels) and downloadLevel + delegates
- [ ] 54. [offline] Mod: search_levels(list featured/epic/legendary/mythic/awarded/recent, difficulty, page) -> ids, names, creators, tiers
- [ ] 55. [offline] Mod: download_level(id) -> level string + metadata (tier, difficulty, length, song, copyable, objects); read-only, nothing uploaded
- [ ] 56. [offline] Mod: perf_stats(seconds) during playtest (fps/frame-time, active objects) and set_ldm(on/off) for previews
- [ ] 57. [offline] MCP tools + mock + tests for 54-56; docs in CLAUDE.md
- [ ] 58. [editor] Live test of the new commands (search, download 1 level, perf_stats)
- [ ] 59. [offline] mastery/corpus/POLICY.md: .gmd/level strings never in git; editor viewing only for copyable levels; recreations never published

## M9 — Corpus (40+ rated 2.2 levels)
- [ ] 60. [editor] Select 40+ levels across tiers (featured/epic/legendary/mythic), difficulties and styles -> corpus/INDEX.md
- [ ] 61. [editor] Download batch 1 (20) to the git-ignored corpus folder
- [ ] 62. [editor] Download batch 2 (20+)
- [ ] 63. [offline] analysis/levelstats.py: objects, triggers by type, groups, colour channels, editor/z layers, LDM (high-detail) count, mode/speed/gravity timeline, orb/pad density, length
- [ ] 64. [offline] corpus/stats/*.json + corpus/SUMMARY.md: distributions by tier/difficulty (correlation only, never "criteria")
- [ ] 65. [offline] analysis/render_ref.py v2: colour-accurate strip renders (header colour channels) for teardowns
- [ ] 66. [offline] Song-structure helper: beat grid + section energy from cached song mp3s (GD caches played songs) for teardowns
- [ ] 67. [editor] Teardowns 1-4 (template: song vs gameplay, mode/speed plan, consistency, deco style, palette, layering, effects, budget, LDM) + screenshots
- [ ] 68. [editor] Teardowns 5-8
- [ ] 69. [editor] Teardowns 9-12
- [ ] 70. [editor] Teardowns 13-16
- [ ] 71. [editor] Teardowns 17-20
- [ ] 72. [offline] Teardowns 21-28 (stats + renders only)
- [ ] 73. [offline] Teardowns 29-36 (stats + renders only)
- [ ] 74. [offline] Teardowns 37-40+ (stats + renders only)
- [ ] 75. [offline] Cross-corpus lessons: what recurs per tier/style, with numbers -> LESSONS.md

## M10 — Tools that encode the rules (each check cites its guide)
- [ ] 76. [offline] analysis/levelmodel.py: shared level model (objects, x->time, mode/speed/gravity/mini/dual timeline)
- [ ] 77. [offline] Linter: consistency checks (orb chains, portal-before-orb, slope transition gaps, H-blocks after launches, J-blocks near blue/black orbs, mode entry)
- [ ] 78. [offline] Linter: fairness checks (sim windows at 240 tps, frame-tight inputs, coyote margins on edges, hitbox enlargement/No Touch, speed jumps 0.5x->4x, readability before speed)
- [ ] 79. [offline] Sync checker: inputs/portals/speed changes vs beat strength (4/4: 1,3,2,4), holds on sustains
- [ ] 80. [offline] Deco checker: block vs background contrast (value), crowding per screen, z/layer conflicts, reserved channel misuse
- [ ] 81. [offline] Optimizer/LDM pass: fully covered objects, duplicate-and-reduce hints, LDM candidates (never functional), lag risks (shaders, blending, animated, Link Visible, dense details)
- [ ] 82. [offline] Validate all checkers on the corpus: flag rates per tier, false positives reviewed, thresholds tuned, report
- [ ] 83. [offline] Generator: ship (corridors with margins, smooth melodic lines)
- [ ] 84. [offline] Generator: ball and spider
- [ ] 85. [offline] Generator: UFO and robot (holds, no two-click robot switches)
- [ ] 86. [offline] Generator: wave (normal + mini, speed leeway) and swing (big arcs)
- [ ] 87. [offline] Generator glue: mode/speed changes on strong beats, portal placement, transition rules, cube upgrades from trajgen
- [ ] 88. [offline] Trigger library (SPWN-style, Python): group/channel allocator, move/rotate/alpha/pulse/spawn helpers, keyframe sequences, functions/loops
- [ ] 89. [offline] Deco library: block outlines/fills per style, background layers, air deco, LDM flags, editor-layer/Z conventions (5/10/15)

## M11 — Drills (built in "CLAUDE drill ..." levels, screenshotted, logged)
- [ ] 90. [editor] Recreation 1: 5-10 s of a teardown level, gameplay then deco; diff vs original; lessons
- [ ] 91. [editor] Recreation 2
- [ ] 92. [editor] Recreation 3
- [ ] 93. [editor] Recreation 4
- [ ] 94. [editor] Recreation 5
- [ ] 95. [editor] Mode drills: cube + ship (generators + linters + frames)
- [ ] 96. [editor] Mode drills: ball + UFO
- [ ] 97. [editor] Mode drills: wave + robot
- [ ] 98. [editor] Mode drills: spider + swing
- [ ] 99. [editor] Sync drill A: 8 bars synced to the melody layer
- [ ] 100. [editor] Sync drill B: same 8 bars to the bass layer
- [ ] 101. [editor] Sync drill C: same 8 bars to percussion; compare A/B/C with the sync checker
- [ ] 102. [editor] Deco drill: one layout in classic style
- [ ] 103. [editor] Deco drill: same layout in glow style
- [ ] 104. [editor] Deco drill: same layout in modern style
- [ ] 105. [editor] Deco drill: same layout in custom-art style; compare all four with the deco checker
- [ ] 106. [editor] Effect drill: camera (zoom/offset/rotate/edge)
- [ ] 107. [editor] Effect drill: shaders (with perf_stats)
- [ ] 108. [editor] Effect drill: keyframes
- [ ] 109. [editor] Effect drill: area triggers
- [ ] 110. [editor] Effect drill: programmatic trigger system generated from code (trigger library)
- [ ] 111. [blocked: Distanax] Playtest a drill set (PLAYTEST.md): feel of mode drills + sync drills
- [ ] 112. [offline] Drill retrospective -> LESSONS.md + CLAUDE.md

## M12 — Capstone: Thermal Lock
- [ ] 113. [offline] Song analysis: sections, layers (melody/bass/percussion), intensity curve, strong beats; supersedes NOTES energy map if different
- [ ] 114. [offline] Resolve the Section 1 grid mismatch (trajgen snapping) with a test; regenerate S1
- [ ] 115. [offline] PLAN.md (planning-a-level template): main idea, parts, asset list, reserved groups/channels/layers, scope, MoSCoW
- [ ] 116. [offline] Gameplay spec per section (modes, speeds, input layer, motifs, intensity) — lint-able
- [ ] 117. [editor] Layout: section 1 (intro)
- [ ] 118. [editor] Layout: section 2 (drop 1a)
- [ ] 119. [editor] Layout: section 3 (drop 1b)
- [ ] 120. [editor] Layout: section 4 (groove)
- [ ] 121. [editor] Layout: section 5 (build)
- [ ] 122. [editor] Layout: section 6 (pre-drop)
- [ ] 123. [editor] Layout: section 7 (drop 2a)
- [ ] 124. [editor] Layout: section 8 (drop 2b)
- [ ] 125. [editor] Layout: section 9 (ending); full lint + sim + frames report
- [ ] 126. [blocked: Distanax] Layout playtest (PLAYTEST.md)
- [ ] 127. [editor] Apply layout feedback
- [ ] 128. [editor] Structuring: sections 1-3
- [ ] 129. [editor] Structuring: sections 4-6
- [ ] 130. [editor] Structuring: sections 7-9
- [ ] 131. [blocked: Distanax] Structure playtest
- [ ] 132. [editor] Apply structure feedback
- [ ] 133. [offline] Deco plan: style, palette (value structure), reserved channels, editor layers/Z plan, LDM plan
- [ ] 134. [editor] Deco: sections 1-2 (base shapes + colours)
- [ ] 135. [editor] Deco: sections 3-4
- [ ] 136. [editor] Deco: sections 5-6
- [ ] 137. [editor] Deco: sections 7-9
- [ ] 138. [editor] Deco details pass
- [ ] 139. [editor] Effects pass (camera, pulses on strong beats, shaders within budget)
- [ ] 140. [editor] Polish checklist pass (layering, copied-group conflicts, screen edges/culling, aspect ratios, pixel alignment, dithering)
- [ ] 141. [editor] Optimization + LDM pass with perf_stats before/after
- [ ] 142. [blocked: Distanax] Final playtest
- [ ] 143. [editor] Apply final fixes
- [ ] 144. [offline] Self-review vs CHECKLIST.md: every category 7+ with evidence, or listed as a weakness
- [ ] 145. [offline] Feedback package: description (states AI involvement), screenshots, known weaknesses, verified-current request servers/streams
- [ ] 146. [offline] Close-out: LESSONS.md + CLAUDE.md, delete the routine
