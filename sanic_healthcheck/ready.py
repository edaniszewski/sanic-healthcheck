"""A checker for application readiness.

When configured with a Sanic application, this checker provides a means
for the application to specify whether or not the application is in a state
where it is fully started up and ready to receive traffic and run normally.

This checker can be used to set up readiness probes for Kubernetes deployments:
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-readiness-probes

This checker exposes the ``/ready`` endpoint by default.
"""

from sanic import response

from .checker import MSG_FAIL, MSG_OK, BaseChecker


class ReadyCheck(BaseChecker):
    """A checker allowing a Sanic application to describe when it is ready
    to serve requests.

    The results of registered check functions are not cached by this checker.
    There should not be a delay in determining application readiness due to
    a stale cache result.
    """

    default_uri = '/ready'

    async def run(self, request) -> response.HTTPResponse:
        """Run all checks and generate an HTTP response for the results."""

        results = []
        for check in self.checks:
            results.append(self.exec_check(check))

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
