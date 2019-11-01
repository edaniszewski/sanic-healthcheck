
import math
import time

import pytest
from sanic import Sanic

from sanic_healthcheck import HealthCheck


def test_init_with_app():
    app = Sanic()
    assert len(app.router.routes_names) == 0

    HealthCheck(app=app)
    assert len(app.router.routes_names) == 1
    assert 'run' in app.router.routes_names
    assert HealthCheck.default_uri in app.router.routes_names['run'][0]


def test_init_with_app_custom_uri():
    app = Sanic()
    assert len(app.router.routes_names) == 0

    HealthCheck(app=app, uri='/v2/health')
    assert len(app.router.routes_names) == 1
    assert 'run' in app.router.routes_names
    assert '/v2/health' in app.router.routes_names['run'][0]


def test_add_check():
    checker = HealthCheck()
    assert len(checker.checks) == 0

    def check():
        return True, ''

    checker.add_check(check)
    assert len(checker.checks) == 1
    checker.add_check(check)
    assert len(checker.checks) == 2


@pytest.mark.asyncio
async def test_exec_check_passes():
    checker = HealthCheck()

    def test_check():
        return True, 'test message'

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'test message'
    assert resp['passed'] is True
    assert math.isclose(resp['timestamp'], now, rel_tol=1)


@pytest.mark.asyncio
async def test_exec_check_passes_coro():
    checker = HealthCheck()

    async def test_check():
        return True, 'test message'

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'test message'
    assert resp['passed'] is True
    assert math.isclose(resp['timestamp'], now, rel_tol=1)


@pytest.mark.asyncio
async def test_exec_check_fails():
    checker = HealthCheck()

    def test_check():
        return False, 'test message'

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'test message'
    assert resp['passed'] is False
    assert math.isclose(resp['timestamp'], now, rel_tol=1)


@pytest.mark.asyncio
async def test_exec_check_fails_coro():
    checker = HealthCheck()

    async def test_check():
        return False, 'test message'

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'test message'
    assert resp['passed'] is False
    assert math.isclose(resp['timestamp'], now, rel_tol=1)


@pytest.mark.asyncio
async def test_exec_check_exception():
    checker = HealthCheck()

    def test_check():
        raise ValueError('test error')

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'Exception raised: ValueError: test error'
    assert resp['passed'] is False
    assert math.isclose(resp['timestamp'], now, rel_tol=1)


@pytest.mark.asyncio
async def test_exec_check_exception_coro():
    checker = HealthCheck()

    async def test_check():
        raise ValueError('test error')

    now = time.time()
    resp = await checker.exec_check(test_check)

    assert isinstance(resp, dict)
    assert len(resp) == 4
    assert resp['check'] == 'test_check'
    assert resp['message'] == 'Exception raised: ValueError: test error'
    assert resp['passed'] is False
    assert math.isclose(resp['timestamp'], now, rel_tol=1)
