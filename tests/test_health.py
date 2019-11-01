
import pytest

from sanic_healthcheck import HealthCheck
from sanic_healthcheck.checker import MSG_FAIL, MSG_OK


@pytest.mark.asyncio
async def test_run_no_checks():
    checker = HealthCheck()

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK

    assert len(checker.cache) == 0


@pytest.mark.asyncio
async def test_run_custom_success_data():

    def handler(results):
        return 'handler called'

    checker = HealthCheck(
        success_headers={'foo': 'bar'},
        success_status=201,
        success_handler=handler,
    )

    resp = await checker.run(None)

    assert resp.status == 201
    assert resp.headers == {'foo': 'bar'}
    assert resp.body.decode() == 'handler called'

    assert len(checker.cache) == 0


@pytest.mark.asyncio
async def test_run_checks_pass():

    def check1():
        return True, ''

    def check2():
        return True, ''

    def check3():
        return True, ''

    checker = HealthCheck(
        checks=[check1, check2, check3],
    )

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK

    assert len(checker.cache) == 3


@pytest.mark.asyncio
async def test_run_checks_pass_no_cache():
    def check1():
        return True, ''

    def check2():
        return True, ''

    def check3():
        return True, ''

    checker = HealthCheck(
        no_cache=True,
        checks=[check1, check2, check3],
    )

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK

    assert len(checker.cache) == 0


@pytest.mark.asyncio
async def test_run_checks_pass_cached():

    def check1():
        yield True, ''
        yield False, ''

    def check2():
        yield True, ''
        yield False, ''

    def check3():
        yield True, ''
        yield False, ''

    checker = HealthCheck(
        checks=[check1, check2, check3],
    )

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK

    assert len(checker.cache) == 3

    resp = await checker.run(None)

    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body.decode() == MSG_OK

    assert len(checker.cache) == 3


@pytest.mark.asyncio
async def test_run_checks_fail():

    def check1():
        return True, ''

    def check2():
        return False, ''

    checker = HealthCheck(
        checks=[check1, check2],
    )

    resp = await checker.run(None)

    assert resp.status == 500
    assert resp.headers == {}
    assert resp.body.decode() == MSG_FAIL

    assert len(checker.cache) == 2


@pytest.mark.asyncio
async def test_run_checks_fail_no_cache():

    def check1():
        return True, ''

    def check2():
        return False, ''

    checker = HealthCheck(
        checks=[check1, check2],
        no_cache=True,
    )

    resp = await checker.run(None)

    assert resp.status == 500
    assert resp.headers == {}
    assert resp.body.decode() == MSG_FAIL

    assert len(checker.cache) == 0


@pytest.mark.asyncio
async def test_run_custom_failure_data():

    def check1():
        return False, ''

    def handler(results):
        return 'handler called'

    checker = HealthCheck(
        failure_headers={'foo': 'bar'},
        failure_status=501,
        failure_handler=handler,
        checks=[check1],
    )

    resp = await checker.run(None)

    assert resp.status == 501
    assert resp.headers == {'foo': 'bar'}
    assert resp.body.decode() == 'handler called'

    assert len(checker.cache) == 1
