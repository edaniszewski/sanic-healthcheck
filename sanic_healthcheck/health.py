"""A checker for application health.

When configured with a Sanic application, this checker provides a means
for the application to specify whether or not it is operating in a healthy state.
By identifying broken/unhealthy states, a management system could restart the
application, potentially allowing it to recover.

This checker can be used to set up liveness probes for Kubernetes deployments:
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-a-liveness-command

It may also be used to define container health checks in docker-compose:
https://docs.docker.com/compose/compose-file/#healthcheck

This checker exposes the ``/health`` endpoint by default.
"""

import logging
import time
from typing import Callable, Mapping, Optional

from sanic import Sanic, response

from .checker import MSG_FAIL, MSG_OK, BaseChecker

log = logging.getLogger(__name__)


class HealthCheck(BaseChecker):
    """A checker allowing a Sanic application to describe the health of the
    application at runtime.

    The results of registered check functions are cached by this checker by
    default. To disable result caching, initialize the checker with ``no_cache=True``.
    Since the health endpoint may be polled frequently (and potentially by multiple
    systems), the cache allows the check function results to be valid for a window of
    time, reducing the execution cost. This may be particularly helpful if a given
    health check is more expensive.

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
        no_cache: Disable the checker from caching check results. If this is set to ``True``, the
            ``success_ttl`` and ``failure_ttl`` do nothing.
        success_handler: A handler function which takes the check results (a list[dict])
            and returns a message string. This is called when all checks pass.
        success_headers: Headers to include in the checker response on success. By default, no
            additional headers are sent. This can be useful if, for example, a success
            handler is specified which returns a JSON message. The Content-Type: application/json
            header could be included here.
        success_status: The HTTP status code to use when the checker passes its checks.
        success_ttl: The TTL for a successful check result to live in the cache before it is updated.
        failure_handler: A handler function which takes the check results (a list[dict])
            and returns a message string. This is called when any check fails.
        failure_headers: Headers to include in the checker response on failure. By default, no
            additional headers are sent. This can be useful if, for example, a failure
            handler is specified which returns a JSON message. The Content-Type: application/json
            header could be included here.
        failure_status: The HTTP status code to use when the checker fails its checks.
        failure_ttl: The TTL for a failed check result to live in the cache before it is updated.
        exception_handler: A function which would get called when a registered check
            raises an exception. This handler must take two arguments: the check function
            which raised the exception, and the tuple returned by ``sys.exc_info``. It must
            return a tuple of (bool, string), where the boolean is whether or not it passed
            and the string is the message to use for the check response. By default, no
            exception handler is registered, so an exception will lead to a check failure.
        options: Any additional options to pass to the ``Sanic.add_route`` method
            on ``init``.
    """

    default_uri = '/health'

    def __init__(
            self,
            app: Optional[Sanic] = None,
            uri: Optional[str] = None,
            checks=None,
            no_cache: bool = False,
            success_handler: Optional[Callable] = None,
            success_headers: Optional[Mapping] = None,
            success_status: Optional[int] = 200,
            success_ttl: Optional[int] = 25,
            failure_handler: Optional[Callable] = None,
            failure_headers: Optional[Mapping] = None,
            failure_status: Optional[int] = 500,
            failure_ttl: Optional[int] = 5,
            exception_handler: Optional[Callable] = None,
            **options,
    ) -> None:

        self.cache = {}
        self.no_cache = no_cache

        self.success_ttl = success_ttl
        self.failure_ttl = failure_ttl

        super(HealthCheck, self).__init__(
            app=app,
            uri=uri,
            checks=checks,
            success_handler=success_handler,
            success_headers=success_headers,
            success_status=success_status,
            failure_handler=failure_handler,
            failure_headers=failure_headers,
            failure_status=failure_status,
            exception_handler=exception_handler,
            **options,
        )

    async def run(self, request) -> response.HTTPResponse:
        """Run all checks and generate an HTTP response for the results."""

        results = []
        for check in self.checks:
            # See if the check already has a cached health state. If so, use it;
            # otherwise, re-run the check.
            if not self.no_cache and check in self.cache and self.cache[check].get('expires') >= time.time():
                results.append(self.cache[check])
            else:
                result = await self.exec_check(check)
                if not self.no_cache:
                    if result.get('passed'):
                        ttl = self.success_ttl
                    else:
                        ttl = self.failure_ttl

                    result['expires'] = result['timestamp'] + ttl
                    self.cache[check] = result

                results.append(result)

        passed = all((r['passed'] for r in results))
        if passed:
            msg = MSG_OK
            if self.success_handler:
                msg = self.success_handler(results)

            return response.text(
                body=msg,
                status=self.success_status,
                headers=self.success_headers,
            )

        else:
            msg = MSG_FAIL
            if self.failure_handler:
                msg = self.failure_handler(results)

            return response.text(
                body=msg,
                status=self.failure_status,
                headers=self.failure_headers,
            )
