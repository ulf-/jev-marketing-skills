#!/usr/bin/env python3
"""lead-fit: sort a contact list into A/B/C/D tiers against YOUR ideal customer, in seconds.

Most CRMs hold thousands of contacts nobody has ranked. Scoring them with a chat model is slow and
costs real money at that volume; scoring them with keyword rules misses "Head of Growth" when you
wrote "VP Marketing". Jev reads each contact's title and company against a description of your
buyer and answers three closed questions. Plain code turns the answers into a tier.

Send ONLY what the decision needs: title, company and (optionally) industry. Never names, emails
or phone numbers. The decision does not need them, and they are not yours to send to a third party.

    1. Edit icp.json to describe your buyer (who signs, who scopes, who uses, who is not a fit).
    2. python3 run.py contacts.csv        needs columns: title, company (industry optional)
Writes lead-fit-results.csv next to the input, with the tier added and every other column kept.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'jev-core'))
import jev  # noqa: E402


def questions(icp):
    return {
        'role': {
            'type': 'choice',
            'instructions': 'Given this person\'s job title and company, which role would they play in buying the '
                            'service described in `offer`?',
            'criteria': {
                'decision_maker': icp['decision_maker'],
                'influencer': icp['influencer'],
                'practitioner': icp['practitioner'],
                'not_a_fit': icp['not_a_fit'],
            },
        },
        'company_fit': {
            'type': 'score',
            'instructions': 'How well does this company match the kind of company described in `ideal_company`?',
            'criteria': ['Clearly not that kind of company', 'Unclear from the name', 'Plausibly that kind of company',
                         'Clearly that kind of company'],
        },
        'seniority': {
            'type': 'score',
            'instructions': 'How senior is this job title?',
            'criteria': ['Entry level or assistant', 'Individual contributor', 'Manager', 'Director or head of',
                         'VP, C-level, founder or owner'],
        },
    }


def tier(a):
    """The rule is yours to change. Default: role decides, company fit can only pull a tier DOWN."""
    role = a['role']['choice']
    t = {'decision_maker': 'A', 'influencer': 'B', 'practitioner': 'C', 'not_a_fit': 'D'}[role]
    if a['company_fit']['score'] < 1.0 and t in 'AB':      # clearly the wrong kind of company
        t = 'C'
    return t


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    icp = json.load(open(os.path.join(HERE, 'icp.json')))
    rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
    cols = {k.lower(): k for k in (rows[0].keys() if rows else [])}
    if 'title' not in cols:
        print('contacts.csv needs a "title" column (and ideally "company").')
        return 2
    states = [{'offer': icp['offer'], 'ideal_company': icp['ideal_company'],
               'job_title': r.get(cols['title'], ''), 'company': r.get(cols.get('company', ''), ''),
               'industry': r.get(cols.get('industry', ''), '')} for r in rows]
    results = jev.decide_all(states, questions(icp))
    out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'lead-fit-results.csv')
    counts = {}
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tier', 'role', 'company_fit', 'seniority'] + list(rows[0].keys()) + ['error'])
        for r, (s, a, err) in zip(rows, results):
            if a is None:
                w.writerow(['ERROR', '', '', ''] + list(r.values()) + [err])
                continue
            t = tier(a)
            counts[t] = counts.get(t, 0) + 1
            w.writerow([t, a['role']['choice'], round(a['company_fit']['score'], 2),
                        round(a['seniority']['score'], 2)] + list(r.values()) + [''])
    print('Tiers:', dict(sorted(counts.items())), f'Results: {out}')
    errs = [e for _, a, e in results if a is None]
    if errs:
        print(f'WARNING: {len(errs)} item(s) could not be checked and are marked ERROR. First error: {errs[0]}')
    print('Spend today:', jev.status())
    return 0


if __name__ == '__main__':
    sys.exit(main())
