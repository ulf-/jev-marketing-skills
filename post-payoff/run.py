#!/usr/bin/env python3
"""post-payoff: does this post hand the reader something they can use?

The pattern behind most high-reach LinkedIn posts is not a better opinion, it is a better payoff:
the reader leaves with a prompt, a list, a checklist, a tool or a set of steps. This checks the
opening lines of each draft (what shows before "see more") and returns PASS or FAIL.

Jev answers three closed questions. The PASS rule is plain code, so you can change it:
    PASS = payoff is "artifact" AND the reader's next move is "use_it"

    python3 run.py drafts.txt            one post per block, blank line between posts
    python3 run.py drafts.json           a JSON list of strings
Writes post-payoff-results.csv next to the input.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jev-core'))
import jev  # noqa: E402

QUESTIONS = {
    'payoff': {
        'type': 'choice',
        'instructions': 'Judging only these opening lines of a LinkedIn post, what does the reader GET from the post?',
        'criteria': {
            'artifact': 'The post promises something concrete the reader can take and apply: a prompt, a template, '
                        'a checklist, a named list of tools, skills or resources, a ranked list, or step-by-step '
                        'instructions. It still counts if the reader has to click a link or open a tool to use it.',
            'fact': 'The post explains how something works or reports what is true. Nothing to take or apply.',
            'opinion': 'The post offers a take, a prediction, a stance or a story, with nothing to take or apply.',
        },
    },
    'next_move': {
        'type': 'choice',
        'instructions': 'After reading the full post these lines promise, what is the reader most likely to do?',
        'criteria': {
            'use_it': 'Save it, copy it, install it or apply it to their own work, including following a list '
                      'of links or resources the post hands over.',
            'check_something': 'Go and look at a setting, a number or a page in their own account to see if a '
                               'claim applies to them, with nothing handed over to use.',
            'nothing': 'Nothing. They are informed or entertained and scroll on.',
        },
    },
    'reach': {
        'type': 'choice',
        'instructions': 'Who could use what this post gives?',
        'criteria': {
            'broad': 'Anyone who uses the tool or topic named, or any working professional.',
            'narrow': 'Only a specialist already deep in the settings, internals or edge cases.',
        },
    },
}


def verdict(a):
    ok = a['payoff']['choice'] == 'artifact' and a['next_move']['choice'] == 'use_it'
    return 'PASS' if ok else 'FAIL'


def opening(text, lines=2):
    rows = [l.strip() for l in text.strip().split('\n') if l.strip()]
    return '\n'.join(rows[:lines])


def load(path):
    raw = open(path, encoding='utf-8').read()
    if path.endswith('.json'):
        return [str(x) for x in json.loads(raw)]
    return [b for b in raw.split('\n\n\n') if b.strip()] if '\n\n\n' in raw else [b for b in raw.split('\n\n') if b.strip()]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    posts = load(sys.argv[1])
    results = jev.decide_all([{'post_opening_lines': opening(p)} for p in posts], QUESTIONS)
    out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'post-payoff-results.csv')
    passed = 0
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['verdict', 'payoff', 'next_move', 'reach', 'payoff_confidence', 'opening_lines', 'error'])
        for (state, a, err) in results:
            if a is None:
                w.writerow(['ERROR', '', '', '', '', state['post_opening_lines'], err])
                continue
            v = verdict(a)
            passed += v == 'PASS'
            w.writerow([v, a['payoff']['choice'], a['next_move']['choice'], a['reach']['choice'],
                        round(a['payoff'].get('confidence', 0), 2), state['post_opening_lines'], ''])
    print(f'{passed} of {len(posts)} posts hand the reader something to use. Results: {out}')
    errs = [e for _, a, e in results if a is None]
    if errs:
        print(f'WARNING: {len(errs)} item(s) could not be checked and are marked ERROR. First error: {errs[0]}')
    print('Spend today:', jev.status())
    return 0


if __name__ == '__main__':
    sys.exit(main())
