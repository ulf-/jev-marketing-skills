#!/usr/bin/env python3
"""comment-intent: find the people in your comments who might actually buy.

A post that does well collects hundreds of comments, and most of them are "Great post!", people
promoting themselves, or bots. Somewhere in there are the three people describing a problem you
solve. Jev reads each comment (and the commenter's headline, if you have it) and sorts it into one
of six intents. Claude then drafts replies for the ones worth replying to.

    python3 run.py comments.csv      needs a "comment" column; "headline" optional
Writes comment-intent-results.csv next to the input, sorted with buying signals first.
Send the comment text and headline only. The decision does not need names or profile URLs.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jev-core'))
import jev  # noqa: E402

QUESTIONS = {
    'intent': {
        'type': 'choice',
        'instructions': 'What is this LinkedIn comment doing? Judge the comment text first; use the headline only '
                        'to break a tie.',
        'criteria': {
            'buying_signal': 'Describes a problem, need or project of their own that the post relates to, asks '
                             'how to get or implement something, or asks about working together.',
            'real_question': 'Asks a genuine question about the content, without signalling a need of their own.',
            'peer_discussion': 'Adds a real opinion, experience or counterpoint to the discussion.',
            'self_promotion': 'Mainly points to their own product, service, content or offer.',
            'generic_praise': 'Short, generic agreement or praise that would fit under almost any post, or a '
                              'single keyword like "interested" or a requested code word.',
            'bot_or_spam': 'Reads as automated, off-topic, or a scam.',
        },
    },
    'reply_worth_it': {
        'type': 'noul',
        'instructions': 'Would a thoughtful reply from the post author likely start a real conversation with this '
                        'person?',
    },
}
ORDER = ['buying_signal', 'real_question', 'peer_discussion', 'self_promotion', 'generic_praise', 'bot_or_spam']


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
    cols = {k.lower(): k for k in (rows[0].keys() if rows else [])}
    if 'comment' not in cols:
        print('comments.csv needs a "comment" column.')
        return 2
    states = [{'comment': r[cols['comment']], 'commenter_headline': r.get(cols.get('headline', ''), '')}
              for r in rows]
    results = jev.decide_all(states, QUESTIONS)
    scored = []
    for r, (s, a, err) in zip(rows, results):
        if a is None:
            scored.append((99, 'ERROR', 0, r, err))
        else:
            i = a['intent']['choice']
            scored.append((ORDER.index(i), i, a['reply_worth_it']['noul'], r, ''))
    scored.sort(key=lambda x: (x[0], -x[2]))
    out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'comment-intent-results.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['intent', 'reply_worth_it'] + list(rows[0].keys()) + ['error'])
        for _, i, p, r, err in scored:
            w.writerow([i, round(p, 2)] + list(r.values()) + [err])
    counts = {}
    for _, i, *_ in scored:
        counts[i] = counts.get(i, 0) + 1
    print('Intents:', counts, f'Results: {out}')
    errs = [e for _, a, e in results if a is None]
    if errs:
        print(f'WARNING: {len(errs)} item(s) could not be checked and are marked ERROR. First error: {errs[0]}')
    print('Spend today:', jev.status())
    return 0


if __name__ == '__main__':
    sys.exit(main())
