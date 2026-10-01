---
name: lead-fit
description: Sorts a contact list into A/B/C/D tiers against your ideal customer using only job title and company. Use when you say 'score my contacts', 'rank my CRM', 'who should I reach out to first', or after exporting a contact list.
---

# lead-fit

Ranks a contact export against your buyer in seconds, for about three thousandths of a cent per contact ($0.0061 for 200).

## Run it

1. Edit `icp.json`: what you sell, your ideal company, and who signs, who scopes, who uses, who is not a fit. Plain sentences.
2. `python3 ~/.claude/skills/lead-fit/run.py contacts.csv` (needs a `title` column; `company` and `industry` help).

Results go to `lead-fit-results.csv` with a tier added and your other columns kept.

Over 1,000 contacts? The per-run safety cap stops at 1,000 calls. Raise it on purpose for a big list, for example `JEV_RUN_CALLS=8000 JEV_DAILY_CALLS=8000 JEV_DAILY_USD=1 python3 run.py contacts.csv` (7,000 contacts cost about 20 cents).

**Send only title, company and industry.** The decision does not need names or emails, and they are not yours to send to a third party.

## What Claude does with the result

For tier A, draft a first line or connection note grounded in the person's role and company. For tier D, suggest removing them from active lists.

## How it decides

Jev reads the role (decision maker, influencer, practitioner, not a fit), how well the company matches, and seniority. Role sets the tier; a clearly wrong company pulls A or B down to C. Edit `tier()` in `run.py` to change that.

## Tested

200 real CRM contacts (title and company only). Jev's role call matched a hand-written keyword rule on 146 of 200; most disagreements were the keyword rule being wrong (it filed "Director of Content Marketing" below the decision makers). If your list is in a different industry than `icp.json` describes, expect many tier C results: it reads your description literally, so describe your real market.
