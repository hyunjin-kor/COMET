"""Persistent request budgets and bounded work on a single hosted worker."""

import time
from contextlib import contextmanager
from threading import BoundedSemaphore

from fastapi import HTTPException
from sqlalchemy import delete, text

from backend.models.hosted import HostedUsageCounter
from backend.services.hosted_access import control_session

_WORK_SLOTS = BoundedSemaphore(2)


def is_work_request(request):
    path = request.url.path
    if path.startswith('/api/auth/'):
        return False
    return (request.method not in {'GET', 'HEAD', 'OPTIONS'} or path == '/api/templates/costs'
            or path.startswith('/api/decision/benchmarks/'))


def consume_budget(account, *, uncertainty=False):
    now = time.time()
    window = int(now // 60)
    budgets = [(f'account:{account.id}', 60), (f'company:{account.organization_id}', 240)]
    if uncertainty:
        budgets.append((f'uncertainty:{account.id}', 10))
    with control_session() as session:
        session.exec(text('BEGIN IMMEDIATE'))
        session.exec(delete(HostedUsageCounter).where(HostedUsageCounter.window < window - 1))
        for key, limit in budgets:
            row = session.get(HostedUsageCounter, key) or HostedUsageCounter(key=key, window=window)
            if row.window != window:
                row.window, row.attempts = window, 0
            if row.attempts >= limit:
                raise HTTPException(429, 'Request limit reached; try again after the indicated interval',
                                    headers={'Retry-After': str(max(1, 60 - int(now % 60)))})
            row.attempts += 1
            session.add(row)
        session.commit()


@contextmanager
def work_slot(request, account):
    if not is_work_request(request):
        yield
        return
    if not _WORK_SLOTS.acquire(blocking=False):
        raise HTTPException(429, 'Calculation service is busy; try again shortly', headers={'Retry-After': '2'})
    try:
        consume_budget(account, uncertainty=request.url.path == '/api/uncertainty')
        yield
    finally:
        _WORK_SLOTS.release()
