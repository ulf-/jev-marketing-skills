#!/usr/bin/env python3
"""page-grader: grade every section of a landing page, then let Claude rewrite only the weak ones.

Page feedback from a chat model is a wall of opinions. This splits the page into its sections and
asks Jev the same five yes/no questions about each one, so you get a grid you can act on: which
section never says who it is for, which one has no proof, which one never tells the reader what to
do next. Claude rewrites the sections that fail, and only those.

    python3 run.py page.html                 a saved page
    python3 run.py https://example.com/lp     fetches the page (plain HTTP, no JavaScript)
Writes page-grader-results.csv next to the input (or in the current folder for a URL).
"""
import csv
import html.parser
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jev-core'))
import jev  # noqa: E402

QUESTIONS = {
    'job': {'type': 'choice', 'instructions': 'What job is this section of a landing page mainly doing?',
            'criteria': {'hero': 'The opening headline area that introduces the offer.',
                         'audience': 'Says who the offer is for.',
                         'outcome': 'Describes what the reader gets or what changes for them.',
                         'proof': 'Shows evidence: results, clients, awards, quotes, numbers.',
                         'process': 'Explains how it works or what happens step by step.',
                         'objections': 'Answers questions or doubts, such as an FAQ or pricing.',
                         'call_to_action': 'Asks the reader to book, sign up, download or contact.',
                         'other': 'Anything else.'}},
    'says_who_for': {'type': 'noul', 'instructions': 'Does this section make clear, in plain words, who it is for?'},
    'specific_outcome': {'type': 'noul', 'instructions': 'Does this section name a specific result the reader gets, '
                                                         'rather than a general benefit like "grow faster"?'},
    'has_proof': {'type': 'noul', 'instructions': 'Does this section include evidence: a number, a named client, a '
                                                  'quote, an award, or a described result?'},
    'clear_next_step': {'type': 'noul', 'instructions': 'Does this section tell the reader what to do next?'},
    'plain_language': {'type': 'score', 'instructions': 'How easy is this section to read for a busy buyer '
                                                        'who is not an expert in the field?',
                       'criteria': ['Hard: full of jargon or needs rereading', 'Some effort: a few terms '
                                    'need decoding', 'Easy: clear on one read', 'Very easy: instantly clear']},
}
CHECKS = [q for q in QUESTIONS if q != 'job']


def strength(ans):
    """0-1 for every check. Yes/no answers are already a probability; the readability score runs
    0 to 3, and a section passes when it lands at 'Some effort' or better (1.5 and up)."""
    if 'noul' in ans:
        return ans['noul']
    return 1.0 if ans['score'] >= 1.5 else ans['score'] / 3
# Which checks count for which job. A proof block does not need a call to action; an FAQ does not
# need to name its audience. Edit this table to match how you build pages.
# Readability is reported as a ranking (the hardest sections first), never as a rewrite trigger: it was
# not calibrated against labelled pages, and on real pages it flagged about half of all sections.
REQUIRED = {'hero': ['says_who_for', 'specific_outcome'],
            'audience': ['says_who_for'],
            'outcome': ['specific_outcome'],
            'proof': ['has_proof'],
            'process': [],
            'objections': [],
            'call_to_action': ['clear_next_step'],
            'other': []}


class Sections(html.parser.HTMLParser):
    """Splits a page into sections at <section> tags and at h1/h2 headings."""
    SKIP = {'script', 'style', 'noscript', 'svg', 'nav', 'footer', 'head'}

    def __init__(self):
        super().__init__()
        self.out, self.cur, self.skip = [], [], 0

    def _cut(self):
        text = re.sub(r'\s+', ' ', ' '.join(self.cur)).strip()
        if len(text.split()) >= 8:
            self.out.append(text)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in ('section', 'h1', 'h2'):
            self._cut()

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.cur.append(data.strip())

    def sections(self):
        self.close()
        self._cut()
        return self.out


def load(src):
    if src.startswith('http'):
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0 page-grader'})
        return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    return open(src, encoding='utf-8', errors='ignore').read()


def grade(src):
    p = Sections()
    p.feed(load(src))
    sections = p.sections()
    results = jev.decide_all([{'page_section': s[:6000]} for s in sections], QUESTIONS)
    graded = []
    for i, (s, a, err) in enumerate(results, 1):
        if a is None:
            graded.append({'n': i, 'error': err, 'text': s['page_section']})
            continue
        job = a['job']['choice']
        need = REQUIRED.get(job, [])
        missing = [c for c in need if strength(a[c]) < 0.5]
        graded.append({'n': i, 'job': job, 'ok': not missing, 'missing': missing,
                       'present': [c for c in CHECKS if strength(a[c]) >= 0.5],
                       'probs': {c: round(a[c].get('noul', a[c].get('score', 0)), 2) for c in CHECKS}, 'text': s['page_section']})
    return graded


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    graded = grade(src)
    base = os.getcwd() if src.startswith('http') else os.path.dirname(os.path.abspath(src))
    out = os.path.join(base, 'page-grader-results.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['section', 'job', 'verdict', 'missing_for_its_job', 'first_words'] + CHECKS)
        for g in graded:
            if 'error' in g:
                w.writerow([g['n'], 'ERROR', g['error'], g['text'][:80]])
                continue
            w.writerow([g['n'], g['job'], 'OK' if g['ok'] else 'REWRITE', ', '.join(g['missing']), g['text'][:80]]
                       + [g['probs'][c] for c in CHECKS])
    ok = [g for g in graded if 'job' in g]
    page = {c: any(c in g['present'] for g in ok) for c in CHECKS}
    print(f'{len(ok)} sections graded. To rewrite: '
          f'{[(g["n"], g["job"], g["missing"]) for g in ok if not g["ok"]]}')
    hard = sorted(ok, key=lambda g: g['probs']['plain_language'])[:3]
    print('Hardest to read (rewrite these for clarity first):',
          [(g['n'], g['probs']['plain_language'], g['text'][:40]) for g in hard])
    print('Anywhere on the page:', {c: ('yes' if v else 'NO') for c, v in page.items()})
    print(f'Results: {out}')
    errs = [g['error'] for g in graded if 'error' in g]
    if errs:
        print(f'WARNING: {len(errs)} section(s) could not be checked and are marked ERROR. First error: {errs[0]}')
    print('Spend today:', jev.status())
    return 0


if __name__ == '__main__':
    sys.exit(main())
