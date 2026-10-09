# Ground truth: how levels get rated (RobTop's own sources)

Sources (both read 2026-10-09):
- [R] RobTop, *Geometry Dash Rating System* — https://robtopgames.com/files/GDRating.pdf (13 pages;
  text extracted from the PDF). Page numbers below are the document's own.
- [F] RobTop FAQ, Level section — http://www.robtopgames.com/faq/en/answers/level/

## What is stated
- **Only RobTop rates.** "there is no way for your level to be rated unless RobTop sees it" [R p.9].
- **No criteria are published.** "There are no specific guidelines for what makes a level rate-worthy"; it
  is "decided on a case-by-case basis depending on various factors" [R p.9]. The FAQ says the same: RobTop
  decides what is "good enough" and there are no specific guidelines [F].
- **Tiers = how much RobTop likes it.** Rated, Featured, Epic, Legendary, Mythic are "in increasing order
  of how much RobTop likes your level" [R p.7]. Creator Points 1-5 by tier [R p.8].
- **The general tips (the only stated factors):**
  - Length: at least 30 s; Long (60 s+) is "the length standard for rated levels" [R p.9].
  - Content: "levels with clear gameplay and decent visuals are more likely to get a rating"; RobTop has
    rated "a wide variety of styles"; "no specific answer to how your level should look or play" [R p.9].
  - Performance: high object density can cause lag; bad performance "may stop it from getting rated" or
    lead "to a lower rating tier". Follow the editor's object limits/warnings, don't waste objects, use
    triggers smartly [R p.9-10].
  - Upload Guidelines must be followed [R p.10].
  - Feedback: improving from community feedback makes a rating more likely [R p.11].
- **Sending:** Moderators and Elder Moderators can suggest ("send") levels; RobTop "will often rate"
  sent levels, but a send isn't required, it only raises the chance [R p.11-12]. No number of sends is
  required [F]. Many moderators run level-request servers with queues [R p.12].
- **Featured tab placement** is set manually by RobTop, "based on factors such as recency, playability,
  and optimization" [F].
- **After rating:** big changes, especially in difficulty, can be reverted and locked [R p.8]; the FAQ
  says rated levels lock from updates after 7 days without a moderator's permission [F]. (The two
  differ in wording; treat any post-rating change as needing care.)
- **Difficulty:** request 1-10 stars at upload; Hard 4-5, Harder 6-7, Insane 8-9, Demon 10 [R p.2, 5].
  Thermal Lock's target (Hard-Harder) = 4-7 stars.

## What is NOT stated (do not invent)
- No thresholds for object count, effects, deco style, gameplay difficulty or anything else per tier.
- Nothing distinguishes Featured from Epic from Legendary beyond RobTop's preference.
- Therefore: tier standards in this project come only from **corpus data** (rated levels we analyse)
  and **moderator/creator feedback**, always cited.

## How this maps to our tools
| Stated factor | Tool / evidence |
|---|---|
| Length >= 30 s, aim 60 s+ | level model timeline (task 76): computed length; Thermal Lock target ~115 s |
| Clear gameplay | consistency/fairness linters (77-78), sync checker (79), Distanax playtests |
| Decent visuals | deco checker (80), screenshots, corpus comparison (75) |
| Performance | optimizer/LDM pass (81), bridge perf_stats in playtest (56) |
| Upload Guidelines | read in-game at upload time (Distanax's job; we never upload) |
| Feedback | feedback package (145), PLAYTEST.md loop |

## How to verify in the editor
- Length: GD shows the length tag at upload; our level model computes seconds from speed portals.
- Performance: run perf_stats during a playtest (frame time) and check the editor's object warnings.
- Everything else here is policy, not something the editor can verify.
