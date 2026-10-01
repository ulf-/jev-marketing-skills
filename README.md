# Jev Marketing Skills

Free [Claude Code](https://docs.claude.com/en/docs/claude-code) skills that pair Claude with
[Jev](https://typesafe.ai), TypeSafe's new decision model. **Claude writes. Jev makes the calls.**
Plain code turns the calls into the decision, so you can always see why something was flagged.

Built and tested by [Ulf Lonegren](https://www.linkedin.com/in/ulflonegren/), Executive Director of
AI at Sōvyn, on real marketing data before any of it went in here.

## Why Jev

Jev does not write a word. You give it text and a set of closed questions (pick one of these, yes or
no, or a point on a scale) and it answers each one with a probability. On my tests:

| | Jev | A Claude judge doing the same job |
|---|---|---|
| Time per decision | about 170 ms | several seconds |
| Cost per decision | about $0.00003 | about $0.08 |
| Same verdict | 52 of 60 post openings (86%) | reference |

That price changes what is worth automating. Scoring 7,000 CRM contacts costs about 20 cents.

## The skills

| Skill | Jev decides | Claude then | Tested on |
|---|---|---|---|
| [post-payoff](./post-payoff) | Does the post hand the reader something they can use? | Rewrites the hooks that fail | 60 real post openings, 86% agreement with Claude |
| [lead-fit](./lead-fit) | Which tier each contact is, from title and company | Writes first lines for tier A | 200 real CRM contacts |
| [page-grader](./page-grader) | What job each page section does, and whether it does it | Rewrites only the failing sections | 3 live landing pages, 44 sections |
| [comment-intent](./comment-intent) | Buying signal, real question, discussion, self-promo, praise or bot | Drafts replies to the ones worth it | 200 public LinkedIn comments |
| [keyword-intent](./keyword-intent) | Search intent and fit with your business | Writes briefs for the keepers | 75 real Search Console queries |
| [jev-core](./jev-core) | The shared client, with hard spend caps | | |

## What I tested and left out

- **Hook clarity** ("would a stranger understand these two lines?"). Jev caught 5 of 7 hooks I had
  rejected as unclear, but also failed about 1 in 4 good hooks. A Claude-based check does this job
  better, so it is not in the pack.
- **Picking an A/B test winner.** That is a statistics question, and TypeSafe's own docs say Jev
  cannot do arithmetic. Use a stats calculator.

## Setup

1. Get an [OpenRouter](https://openrouter.ai) API key (Jev is served there with no waitlist as of
   September 2026) and **set a credit limit on the key** in the dashboard.
2. `export OPENROUTER_API_KEY=sk-or-...`
3. Copy the folders into `~/.claude/skills/` and restart Claude Code.
4. `python3 ~/.claude/skills/jev-core/jev.py --status` to check it can see your key.

Then ask Claude for the job in plain words, for example "score my contacts in contacts.csv" or
"grade this landing page".

## Spend safety, built in

Every call goes through `jev-core/jev.py`, which refuses to send anything once you reach $0.50 or
5,000 calls in a day, or 1,000 calls in one run. It only sends Jev models, so a typo cannot send a
batch to an expensive chat model on the same key. Raise the caps with environment variables when
you mean to (see [jev-core](./jev-core)).

## Privacy

Send Jev only what the decision needs. The skills here use job titles (not names or emails), comment
text (not profiles) and page copy. If you work with regulated data, such as patient information,
get a data agreement in place with the provider first.

## License

MIT. Use them, fork them, adapt them.
