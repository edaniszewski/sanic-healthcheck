"""Success and failure handler definitions for checkers."""

import json
import time
from typing import Iterator, Mapping


def json_success_handler(results: Iterator[Mapping]) -> str:
    """A success handler which returns results in a JSON-formatted response.

    Args:
        results: The results of all checks which were executed for a checker.
            Each result dictionary is guaranteed to have the keys: 'check',
            'message', 'passed', 'timestamp'.

    Returns:
        The checker response, formatted as JSON.
    """
    return json.dumps({
        'status': 'success',
        'timestamp': time.time(),
        'results': results,
    })


def json_failure_handler(results: Iterator[Mapping]) -> str:
    """A failure handler which returns results in a JSON-formatted response.

   Args:
        results: The results of all checks which were executed for a checker.
            Each result dictionary is guaranteed to have the keys: 'check',
            'message', 'passed', 'timestamp'.

    Returns:
        The checker response, formatted as JSON.
    """
    return json.dumps({
        'status': 'failure',
        'timestamp': time.time(),
        'results': results,
    })
