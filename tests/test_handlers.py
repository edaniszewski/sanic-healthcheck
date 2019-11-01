
import json
import math
import time

from sanic_healthcheck import handlers


def test_json_success_handler():

    results = [
        {'test': 'foo'},
        {'test': 'bar'},
    ]

    now = time.time()
    actual = handlers.json_success_handler(results)
    assert isinstance(actual, str)

    loaded = json.loads(actual)
    assert isinstance(loaded, dict)

    assert loaded['status'] == 'success'
    assert math.isclose(loaded['timestamp'], now, rel_tol=1)
    assert loaded['results'] == results


def test_json_success_handler_no_results():

    now = time.time()
    actual = handlers.json_success_handler([])
    assert isinstance(actual, str)

    loaded = json.loads(actual)
    assert isinstance(loaded, dict)

    assert loaded['status'] == 'success'
    assert math.isclose(loaded['timestamp'], now, rel_tol=1)
    assert loaded['results'] == []


def test_json_failure_handler():

    results = [
        {'test': 'foo'},
        {'test': 'bar'},
    ]

    now = time.time()
    actual = handlers.json_failure_handler(results)
    assert isinstance(actual, str)

    loaded = json.loads(actual)
    assert isinstance(loaded, dict)

    assert loaded['status'] == 'failure'
    assert math.isclose(loaded['timestamp'], now, rel_tol=1)
    assert loaded['results'] == results


def test_json_failure_handler_no_results():

    now = time.time()
    actual = handlers.json_failure_handler([])
    assert isinstance(actual, str)

    loaded = json.loads(actual)
    assert isinstance(loaded, dict)

    assert loaded['status'] == 'failure'
    assert math.isclose(loaded['timestamp'], now, rel_tol=1)
    assert loaded['results'] == []
