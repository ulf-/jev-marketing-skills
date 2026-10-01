#!/usr/bin/env python3
"""keyword-intent: sort a keyword list into the few worth a brief and the many that are not.

Every SEO tool will hand you thousands of keywords. The work is deciding which ones a buyer types,
which ones fit what you actually sell, and which are junk (competitor lookups, job searches, typos
of someone else's brand). Jev answers three closed questions per keyword against a description of
your business, and plain code decides which ones get a brief. Claude writes the briefs.

    1. Edit business.json: what you sell and to whom.
    2. python3 run.py keywords.csv     needs a "keyword" column (any other columns are kept, e.g.
                                        impressions or volume from Search Console, Semrush or Ahrefs)
Writes keyword-intent-results.csv next to the input, brief-worthy keywords first.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'jev-core'))
import jev  # noqa: E402

QUESTIONS = {
    'intent': {
        'type': 'choice',
        'instructions': 'What is the person who typed this search query most likely trying to do?',
        'criteria': {
            'hire_or_buy': 'Find a provider, agency, service or product to hire or buy.',
            'compare': 'Compare or evaluate options, e.g. "best", "top", "vs", "reviews", "alternatives".',
            'learn': 'Learn how to do something or understand a topic.',
            'navigate': 'Reach one specific company, brand or website by name.',
            'other': 'Anything else, including job searches, free tools and unrelated lookups.',
        },
    },
    'fit': {
        'type': 'score',
        'instructions': 'How well does this search match what the business in `business` sells and who it sells to?',
        'criteria': ['Unrelated', 'Loosely related', 'Related but not a core service or buyer',
                     'A core service for the right buyer'],
    },
    'about_someone_else': {
        'type': 'noul',
        'instructions': 'Is this query about a specific other company, product or person, rather than a need?',
    },
}


def brief_worthy(a):
    """Default rule: a buyer or evaluator, a close fit, and not a lookup of someone else's brand."""
    return (a['intent']['choice'] in ('hire_or_buy', 'compare') and a['fit']['score'] >= 2.0
            and a['about_someone_else']['noul'] < 0.5)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    business = json.load(open(os.path.join(HERE, 'business.json')))['business']
    rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
    key = next((k for k in (rows[0].keys() if rows else []) if k.lower() in ('keyword', 'query', 'keywords')), None)
    if not key:
        print('keywords.csv needs a "keyword" (or "query") column.')
        return 2
    results = jev.decide_all([{'business': business, 'search_query': r[key]} for r in rows], QUESTIONS)
    graded = []
    for r, (s, a, err) in zip(rows, results):
        if a is None:
            graded.append((2, 'ERROR', '', 0, r, err))
            continue
        worthy = brief_worthy(a)
        graded.append((0 if worthy else 1, 'BRIEF' if worthy else 'skip', a['intent']['choice'],
                       round(a['fit']['score'], 2), r, ''))
    graded.sort(key=lambda g: (g[0], -g[3]))
    out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'keyword-intent-results.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['decision', 'intent', 'fit_0_to_3'] + list(rows[0].keys()) + ['error'])
        for _, d, i, fit, r, err in graded:
            w.writerow([d, i, fit] + list(r.values()) + [err])
    n = sum(1 for g in graded if g[1] == 'BRIEF')
    print(f'{n} of {len(rows)} keywords are worth a brief. Results: {out}')
    errs = [e for _, a, e in results if a is None]
    if errs:
        print(f'WARNING: {len(errs)} item(s) could not be checked and are marked ERROR. First error: {errs[0]}')
    print('Spend today:', jev.status())
    return 0


if __name__ == '__main__':
    sys.exit(main())
