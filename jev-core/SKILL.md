---
name: jev-core
description: The shared, spend-capped client every other skill in this pack uses to call Jev, TypeSafe's decision model. Use when setting up the pack, checking today's Jev spend, or writing a new Jev question set.
---

# jev-core

Jev is a model that makes decisions and never writes. You give it some text and a set of closed questions (pick one of these options, yes or no, or a position on a scale), and it answers each one with a probability in roughly 200 ms. Claude does the writing. Jev makes the calls. A few lines of plain code turn the calls into the final decision, so you can read exactly why anything was flagged.

## Setup (5 minutes)

1. Get an OpenRouter API key at openrouter.ai (Jev is served there with no waitlist as of September 2026). Put a credit limit on the key while you are in the dashboard.
2. `export OPENROUTER_API_KEY=sk-or-...`
3. Copy this whole pack's folders into `~/.claude/skills/` and restart Claude Code.
4. Check it: `python3 ~/.claude/skills/jev-core/jev.py --status`

## The spend caps (read this)

`jev.py` refuses to send a request once today's spend reaches `JEV_DAILY_USD` (default $0.50), today's calls reach `JEV_DAILY_CALLS` (default 5,000), or one run reaches `JEV_RUN_CALLS` (default 1,000). It only ever sends Jev models, so a typo cannot route a batch to an expensive chat model on the same key. Every call is logged to `~/.jev/ledger.jsonl`, and if that file cannot be written, nothing is sent. Raise a cap on purpose with an environment variable; never by editing it out.

## Writing your own Jev question set

- Ask small, closed questions. One decision per question.
- Define every option in plain words. Jev reads definitions literally: "go look" will be applied to anything that sends the reader somewhere, so say what you mean.
- Let code make the final call from the answers, never a question that asks "is this good?".
- Send only what the decision needs. No names, emails or phone numbers when a job title will do.
- Jev cannot count, do arithmetic or compare dates. Do those in code.
- Use low `confidence` as the trigger to hand an item to Claude for a second look.
