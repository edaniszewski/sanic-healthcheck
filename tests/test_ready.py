
import pytest

from sanic_healthcheck import ReadyCheck
from sanic_healthcheck.checker import MSG_FAIL, MSG_OK


@pytest.mark.asyncio
async def test_run_no_checks():
    checker = ReadyCheck()

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK


@pytest.mark.asyncio
async def test_run_custom_success_data():

    def handler(results):
        return 'handler called'

    checker = ReadyCheck(
        success_headers={'foo': 'bar'},
        success_status=201,
        success_handler=handler,
    )

    resp = await checker.run(None)

    assert resp.status == 201
    assert resp.headers == {'foo': 'bar'}
    assert resp.body.decode() == 'handler called'


@pytest.mark.asyncio
async def test_run_checks_pass():

    def check1():
        return True, ''

    checker = ReadyCheck(
        checks=[check1, check1, check1],
    )

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK


@pytest.mark.asyncio
async def test_run_checks_fail():

    def check1():
        return True, ''

    def check2():
        return False, ''

    checker = ReadyCheck(
        checks=[check1, check2, check1],
    )

    resp = await checker.run(None)

    assert resp.status == 500
    assert resp.headers == {}
    assert resp.body.decode() == MSG_FAIL


@pytest.mark.asyncio
async def test_run_custom_failure_data():

    def check2():
        return False, ''

    def handler(results):
        return 'handler called'

    checker = ReadyCheck(
        failure_headers={'foo': 'bar'},
        failure_status=501,
        failure_handler=handler,
        checks=[check2],
    )

    resp = await checker.run(None)

    assert resp.status == 501
    assert resp.headers == {'foo': 'bar'}
    assert resp.body.decode() == 'handler called'
