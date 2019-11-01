
Usage
=====

``sanic-healthcheck`` provides two types of checkers: a health check and a readiness check.

Check Functions
---------------

Check functions take no arguments and return a tuple of ``(bool, str)``, where the boolean describes
whether or not the check passed, and the string is the message that is output for the check.

.. code-block:: python

  def check_db_connection():
      ok = db.ping()
      if ok:
          return True, "successfully pinged DB"
      else:
          return False, "failed to ping DB"

Exceptions raised in the check are caught and result in the check returning a failure state.


Health Check
------------

The ``HealthCheck`` class lets you register health check functions which get evaluated
whenever the health route (``/health`` by default) is called. Since the health route may be called
frequently by potentially numerous services, the class supports caching health check results for
a short period of time.

.. code-block:: python

  import random

  from sanic import Sanic, response
  from sanic_healthcheck import HealthCheck

  app = Sanic()
  health_check = HealthCheck(app)


  @app.route('/')
  async def test(request):
      return response.json({'hello', 'world'})


  # Define checks for the health check.
  def check_health_random():
      if random.random() > 0.9:
          return False, 'the random number is > 0.9'
      return True, 'the random number is <= 0.9'


  if __name__ == '__main__':
      health_check.add_check(check_health_random)

      app.run(host='0.0.0.0', port=8000)


Where a passing health check would look like:

.. code-block:: console

  $ curl -i localhost:8000/health
  HTTP/1.1 200 OK
  Connection: keep-alive
  Keep-Alive: 5
  Content-Length: 2
  Content-Type: text/plain; charset=utf-8

  OK


and a failing health check would look like:

.. code-block:: console

  $ curl -i localhost:8000/health
  HTTP/1.1 500 Internal Server Error
  Connection: keep-alive
  Keep-Alive: 5
  Content-Length: 6
  Content-Type: text/plain; charset=utf-8

  FAILED


Readiness Check
---------------


The ``HealthCheck`` class lets you register health check functions which get evaluated
whenever the health route (``/health`` by default) is called. Since the health route may be called
frequently by potentially numerous services, the class supports caching health check results for
a short period of time.

.. code-block:: python

  import time

  from sanic import Sanic, response
  from sanic_healthcheck import ReadyCheck

  app = Sanic()
  ready_check = ReadyCheck(app)

  start = time.time()


  @app.route('/')
  async def test(request):
      return response.json({'hello', 'world'})


  # Define checks for the ready check.
  def check_ready():
      if time.time() > start + 7:
          return True, 'ready: seven seconds elapsed'
      return False, 'not ready: seven seconds have not elapsed yet'


  if __name__ == '__main__':
      ready_check.add_check(check_ready)

      app.run(host='0.0.0.0', port=8000)


Where a passing health check would look like:

.. code-block:: console

  $ curl -i localhost:8000/health
  HTTP/1.1 200 OK
  Connection: keep-alive
  Keep-Alive: 5
  Content-Length: 2
  Content-Type: text/plain; charset=utf-8

  OK


and a failing health check would look like:

.. code-block:: console

  $ curl -i localhost:8000/health
  HTTP/1.1 500 Internal Server Error
  Connection: keep-alive
  Keep-Alive: 5
  Content-Length: 6
  Content-Type: text/plain; charset=utf-8

  FAILED


