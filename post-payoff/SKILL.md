---
name: post-payoff
description: Checks whether a LinkedIn post (or any post) hands the reader something they can use: a list, prompt, checklist, tool or steps. Use when you say 'will this post land', 'check my drafts', 'score my hooks', or before scheduling a batch of posts.
---

# post-payoff

Most high-reach LinkedIn posts share one trait: the reader leaves with something to use. This checks the opening lines of each draft (what shows before "see more") and returns PASS or FAIL.

## Run it

```
python3 ~/.claude/skills/post-payoff/run.py drafts.txt
```
`drafts.txt` holds one post per block with a blank line between posts (or pass a `.json` list). Results go to `post-payoff-results.csv`.

## What Claude does with the result

For every FAIL, rewrite the first two lines so they promise the concrete thing the post already contains (the list, the steps, the prompt). Do not change the body. Re-run until it passes.

## How it decides

Jev answers three closed questions: what the reader gets (artifact, fact or opinion), what they do next (use it, check something, nothing) and who can use it. PASS = artifact AND use it. The rule is in `run.py`; change it if your definition of a good post differs.

## Tested

60 real opening lines (40 from a top creator's published posts, 20 from my own) against a Claude judge asked the same questions: same PASS/FAIL verdict on 52 of 60 (86%). Median 170 ms per post, about $0.00003 each.
