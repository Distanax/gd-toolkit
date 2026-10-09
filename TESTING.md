# gd-bridge — testing guide for Distanax

Things only you can do in-game. Each section says exactly what to do and what to report back.
Report results by telling Claude in chat (or add a note under "Results" at the bottom and push).

## 0. Connect GitHub to claude.ai (2 minutes) — unblocks the auto-continue routine
Creating the "gd-bridge continue" routine failed with `github_token_missing`: cloud routines need your
GitHub account connected to claude.ai so they can clone and push `Distanax/gd-toolkit`.
1. Open https://claude.ai/code in your browser and sign in.
2. When asked (or via the GitHub/repository picker), connect your GitHub account and grant access to
   the `Distanax/gd-toolkit` repository (installing the Claude GitHub app on that repo is enough).
3. Tell Claude "GitHub is connected" in chat. Claude then creates the routine (every 3 hours,
   Sonnet 5.5, Default environment, the mission prompt) and checks off task 2.

## 1. Install the mod (about 5 minutes)
_Written in task 7, once CI produces a release._

## 2. Run the end-to-end test
_Written in task 50._

## Results
_(none yet)_
