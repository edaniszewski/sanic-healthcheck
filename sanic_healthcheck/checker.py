"""The base class for all implementations of a checker."""

import abc
import logging
import sys
import time
from typing import Callable, Dict, Iterator, Mapping, Optional

from sanic import Sanic, response

log = logging.getLogger(__name__)


MSG_OK = 'OK'
MSG_FAIL = 'FAILED'


class BaseChecker(metaclass=abc.ABCMeta):
    """The base class for all checkers.

    This class implements various common functionality for all checkers
    and requires that each checker define its own ``run`` method. Each
    checker implementation should also set its own ``default_uri``.

    Args:
        app: The Sanic application instance to register the checker to. If not specified on
            initialization, the user must pass it to the ``init`` method to register the checker
            route with the application. If specified on initialization, ``init`` will be called
            automatically.
        uri: The route URI to expose for the checker.
        checks: A collection of checks to register with the checker on init. A check is a
            function which takes no arguments and returns (``bool``, ``str``), where the
            boolean signifies whether the check passed or not, and the string is a message
            associated with the success/failure.
        success_handler: A handler function which takes the check results (a list[dict])
            and returns a message string. This is called when all checks pass.
        success_headers: Headers to include in the checker response on success. By default, no
            additional headers are sent. This can be useful if, for example, a success
            handler is specified which returns a JSON message. The Content-Type: application/json
            header could be included here.
        success_status: The HTTP status code to use when the checker passes its checks.
        failure_handler: A handler function which takes the check results (a list[dict])
            and returns a message string. This is called when any check fails.
        failure_headers: Headers to include in the checker response on failure. By default, no
            additional headers are sent. This can be useful if, for example, a failure
            handler is specified which returns a JSON message. The Content-Type: application/json
            header could be included here.
        failure_status: The HTTP status code to use when the checker fails its checks.
        exception_handler: A function which would get called when a registered check
            raises an exception. This handler must take two arguments: the check function
            which raised the exception, and the tuple returned by ``sys.exc_info``. It must
            return a tuple of (bool, string), where the boolean is whether or not it passed
            and the string is the message to use for the check response. By default, no
            exception handler is registered, so an exception will lead to a check failure.
        options: Any additional options to pass to the ``Sanic.add_route`` method
            on ``init``.
    """

    default_uri = None

    def __init__(
            self,
            app: Optional[Sanic] = None,
            uri: Optional[str] = None,
            checks: Optional[Iterator[Callable]] = None,
            success_handler: Optional[Callable] = None,
            success_headers: Optional[Mapping] = None,
            success_status: Optional[int] = 200,
            failure_handler: Optional[Callable] = None,
            failure_headers: Optional[Mapping] = None,
            failure_status: Optional[int] = 500,
            exception_handler: Optional[Callable] = None,
            **options,
    ) -> None:

        self.app = app
        self.uri = uri

        self.success_handler = success_handler
        self.success_headers = success_headers
        self.success_status = success_status

        self.failure_handler = failure_handler
        self.failure_headers = failure_headers
        self.failure_status = failure_status

        self.exception_handler = exception_handler

        self.checks = checks or []
        self.options = options

        if self.app:
            self.init(self.app, self.uri)

    def init(self, app: Sanic, uri: Optional[str] = None) -> None:
        """Initialize the checker with the Sanic application.

        This method will register a new endpoint for the specified
        Sanic application which exposes the results of the checker.

        Args:
            app: The Sanic application to register a new endpoint with.
            uri: The URI of the endpoint to register. If not specified, the
                checker's ``default_uri`` is used.
        """
        if not uri:
            uri = self.default_uri
        app.add_route(self.run, uri, **self.options)

    def add_check(self, fn: Callable) -> None:
        """Add a check to the checker.

        A check function is a function which takes no arguments and returns
        (``bool``, ``str``), where the boolean signifies whether the check
        passed or not, and the string is a message associated with the
        success/failure.

        Args:
            fn: The check to add.
        """
        self.checks.append(fn)

    @abc.abstractmethod
    async def run(self, request) -> response.HTTPResponse:
        """Run the checker.

        Each subclass of the BaseChecker must define its own ``run`` logic.
        """
        raise NotImplementedError

    def exec_check(self, check: Callable) -> Dict:
        """Execute a single check and generate a dictionary result from the
        result of the check.

        Args:
            check: The check function to execute.

        Returns:
            A dictionary containing the results of the check.
        """
        try:
            passed, msg = check()
        except Exception:
            log.exception(
                f'Exception while running {self.__class__.__name__} check')

            info = sys.exc_info()
            if self.exception_handler:
                passed, msg = self.exception_handler(check, info)
            else:
                passed = False
                msg = f'Exception raised: {info[0].__name__}: {info[1]}'

        if not passed:
            log.error(
                f'{self.__class__.__name__} check "{check.__name__}" failed: {msg}')

        return {
            'check': check.__name__,
            'message': msg,
            'passed': passed,
            'timestamp': time.time(),
        }
