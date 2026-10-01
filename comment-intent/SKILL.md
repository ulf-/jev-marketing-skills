---
name: comment-intent
description: Sorts the comments on your posts into buying signals, real questions, discussion, self-promotion, generic praise and bots, so you reply to the few that matter. Use when you say 'who should I reply to', 'sort my comments', or after a post takes off.
---

# comment-intent

A post that does well collects hundreds of comments. This finds the handful worth your time.

## Run it

```
python3 ~/.claude/skills/comment-intent/run.py comments.csv
```
Needs a `comment` column; a `headline` column (the commenter's job headline) helps break ties. Results go to `comment-intent-results.csv`, with buying signals and real questions at the top. Send comment text and headline only.

## What Claude does with the result

Draft replies for buying signals and real questions, in your voice. Skip generic praise, self-promotion and bots.

## Tested

200 public comments from creator posts: 140 discussion, 33 generic praise, 10 self-promotion, 9 real questions, 4 buying signals, 4 bots. The praise and self-promotion calls were reliable on review; the buying-signal bucket is small and occasionally includes a casual one ("grab coffee?"), so read it rather than auto-messaging it.
