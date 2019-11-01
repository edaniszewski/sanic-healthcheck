"""Example Sanic application showcasing sanic-healthcheck."""

import time
import random
from sanic import Sanic, response
from sanic_healthcheck import HealthCheck, ReadyCheck

app = Sanic()
health_check = HealthCheck(app, no_cache=True)
ready_check = ReadyCheck(app)

start = time.time()


@app.route('/')
async def test(request):
    return response.json({'hello', 'world'})


# Define checks for the health check.
def check_health_random():
    if random.random() > 0.9:
        return False, 'the random number is > 0.9'
    return True, 'the random number is <= 0.9'


# Define checks for the ready check.
def check_ready():
    if time.time() > start + 7:
        return True, 'ready: seven seconds elapsed'
    return False, 'not ready: seven seconds have not elapsed yet'


if __name__ == '__main__':
    health_check.add_check(check_health_random)
    ready_check.add_check(check_ready)
    app.run(host='0.0.0.0', port=8000)
