---
name: page-grader
description: Grades every section of a landing page and flags only the ones that fail their job, so Claude rewrites those and nothing else. Use when you say 'review this landing page', 'why isn't this page converting', or 'grade this page'.
---

# page-grader

Splits a landing page into sections, works out what job each section is doing (hero, audience, outcome, proof, process, FAQ, call to action), and checks only what that job needs. A proof block is checked for proof; a call-to-action block for a next step; a hero for who it is for and what they get.

## Run it

```
python3 ~/.claude/skills/page-grader/run.py page.html
python3 ~/.claude/skills/page-grader/run.py https://example.com/landing-page
```
Results go to `page-grader-results.csv`, plus a printed list of sections to rewrite and the three hardest-to-read sections.

## What Claude does with the result

Rewrite only the sections flagged REWRITE, fixing exactly what is missing (name the buyer, state the outcome, add the proof), and simplify the three hardest-to-read sections. Leave the rest alone.

## Limits

Readability is reported as a ranking, not a pass/fail, because it was not calibrated against labelled pages. The URL mode fetches plain HTML only; save pages built with JavaScript from the browser first.

## Tested

Three live landing pages (44 sections): each page came back with two to four sections to rewrite, such as a second hero block that never names its buyer and a "proof" block with no evidence in it, and flagged a framework-heavy jargon section as hardest to read.
