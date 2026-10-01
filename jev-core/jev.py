#!/usr/bin/env python3
"""jev.py - a small, spend-capped client for Jev, TypeSafe's decision model.

Jev does not write. You hand it some text (the "state") and a set of closed questions, and it
returns a pick for each one with a probability, in about 200 ms, for a few hundredths of a cent.
Claude does the writing; Jev makes the calls; plain code turns the calls into a decision.

WHY THE CAPS ARE BUILT IN. An API key with no spend limit plus a loop with a bug is how people wake
up to a four-figure bill. Every call through this file is checked against a daily dollar cap, a
daily call cap and a per-run call cap BEFORE it is sent, and it only ever sends Jev models, so a
typo can never route your batch job to an expensive chat model on the same key.

    JEV_DAILY_USD     default 0.50   (at ~$0.00003 a call, that is roughly 15,000 decisions)
    JEV_DAILY_CALLS   default 5000
    JEV_RUN_CALLS     default 1000   (per process)

Every call is logged to ~/.jev/ledger.jsonl. If that file cannot be written, nothing is sent.

Access: the default route is OpenRouter's Decisions API with OPENROUTER_API_KEY (no waitlist as of
September 2026). Set JEV_ROUTE=typesafe and TYPESAFE_API_KEY to call TypeSafe directly instead.

    python3 jev.py --status      today's spend against the caps
"""
import concurrent.futures as cf
import datetime
import fcntl
import json
import os
import sys
import urllib.error
import urllib.request

ROUTE = os.environ.get('JEV_ROUTE', 'openrouter')
MODEL = os.environ.get('JEV_MODEL', 'typesafe/jev-1.13' if ROUTE == 'openrouter' else 'jev-1.13')
URL = ('https://openrouter.ai/api/alpha/decisions' if ROUTE == 'openrouter'
       else 'https://api.typesafe.ai/v1/systemone')
LEDGER = os.path.expanduser(os.environ.get('JEV_LEDGER', '~/.jev/ledger.jsonl'))
DAILY_USD = float(os.environ.get('JEV_DAILY_USD', '0.50'))
DAILY_CALLS = int(os.environ.get('JEV_DAILY_CALLS', '5000'))
RUN_CALLS = int(os.environ.get('JEV_RUN_CALLS', '1000'))
_run_calls = 0


class CapReached(RuntimeError):
    """Raised before a request is sent when it would break a cap."""


def _key():
    name = 'OPENROUTER_API_KEY' if ROUTE == 'openrouter' else 'TYPESAFE_API_KEY'
    k = os.environ.get(name, '').strip()
    if not k:
        raise RuntimeError(f'{name} is not set. See jev-core/SKILL.md for how to get one.')
    return k


def _today(fh):
    day = datetime.date.today().isoformat()
    usd = calls = 0
    fh.seek(0)
    for line in fh:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get('ts', '')[:10] == day:
            usd += float(r.get('cost') or 0)
            calls += 1
    return usd, calls


def status():
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, 'a+') as fh:
        usd, calls = _today(fh)
    return {'today_usd': round(usd, 6), 'today_calls': calls,
            'cap_usd': DAILY_USD, 'cap_calls': DAILY_CALLS, 'model': MODEL}


def decide(state, questions, timeout=30):
    """One Jev request. Returns the `answers` dict, keyed by your question ids."""
    global _run_calls
    if 'jev' not in MODEL:
        raise RuntimeError(f'this client only sends Jev models, refusing {MODEL!r}')
    if _run_calls >= RUN_CALLS:
        raise CapReached(f'per-run cap reached ({RUN_CALLS} calls). Raise JEV_RUN_CALLS on purpose if you need more.')
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, 'a+') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        usd, calls = _today(fh)
        if usd >= DAILY_USD or calls >= DAILY_CALLS:
            raise CapReached(f'daily cap reached: ${usd:.4f} of ${DAILY_USD}, {calls} of {DAILY_CALLS} calls')
        body = json.dumps({'model': MODEL, 'state': state, 'questions': questions}).encode()
        req = urllib.request.Request(URL, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + _key(), 'Content-Type': 'application/json'})
        cost = 0.0005                       # an unknown outcome is booked pessimistically
        try:
            r = json.load(urllib.request.urlopen(req, timeout=timeout))
            cost = float((r.get('usage') or {}).get('cost') or 0)
        finally:
            _run_calls += 1
            fh.seek(0, 2)
            fh.write(json.dumps({'ts': datetime.datetime.now().isoformat(timespec='seconds'),
                                 'model': MODEL, 'cost': cost}) + '\n')
            fh.flush()
    return r['answers']


def decide_all(states, questions, workers=8):
    """Run the same questions over many states in parallel. Returns [(state, answers | None, error | None)].

    Stops cleanly at the first cap: items after it come back with an error, nothing else is sent."""
    def one(s):
        try:
            return s, decide(s, questions), None
        except CapReached as e:
            return s, None, f'cap: {e}'
        except urllib.error.HTTPError as e:
            return s, None, f'HTTP {e.code}: {e.read()[:200].decode(errors="ignore")}'
        except Exception as e:
            return s, None, str(e)[:200]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, states))


if __name__ == '__main__':
    if '--status' in sys.argv:
        print(json.dumps(status(), indent=1))
    else:
        print(__doc__)
