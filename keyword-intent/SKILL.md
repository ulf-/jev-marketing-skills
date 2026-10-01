---
name: keyword-intent
description: Sorts a keyword list by search intent and fit with your business, and picks the ones worth a content brief. Use when you say 'which keywords should we target', 'triage this keyword export', or with a Search Console, Semrush or Ahrefs export.
---

# keyword-intent

Takes any keyword export and splits it into the few worth a brief and the many that are not: someone else's brand, a free tool lookup, a service you do not sell.

## Run it

1. Edit `business.json`: what you sell and to whom, in one or two sentences.
2. `python3 ~/.claude/skills/keyword-intent/run.py keywords.csv` (needs a `keyword` or `query` column; other columns such as impressions are kept).

Results go to `keyword-intent-results.csv`, brief-worthy keywords first.

## What Claude does with the result

Write a content brief for each BRIEF keyword, highest fit first, grouping near-duplicates into one brief.

## How it decides

BRIEF = the searcher wants to hire, buy or compare, the fit with your business is at least "related", and the query is not about another company. Edit `brief_worthy()` in `run.py` to change the rule.

## Tested

75 real Search Console queries from an agency site: 33 marked BRIEF (healthcare SEO, PPC management, medical device marketing), with Shopify builds the agency does not sell, a plagiarism checker, competitor names and the agency's own brand name all skipped. Cost for the whole list: about a tenth of a cent.
