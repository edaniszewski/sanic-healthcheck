# sanic-healthcheck

``sanic-healthcheck`` provides a simple way to add health checks and readiness checks to
your [Sanic](https://github.com/huge-success/sanic) application. This makes it easier to
monitor your application and ensure it is running in a health state. Monitoring or management
tools can ping these endpoints to determine application uptime and status, as well as perform
application restart to ensure your application isn't running in a degraded state.

``sanic-healthcheck`` was inspired by and borrows from [Runscope/healthcheck](https://github.com/Runscope/healthcheck).

## Installing

```
pip install sanic-healthcheck
```

## Documentation

For full project documentation, see: https://sanic-healthcheck.readthedocs.io/en/latest/

## Example

Below is a trivial example showcasing basic usage of sanic-healthcheck

```python
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
```

## License

`sanic-healthcheck` is licensed under the MIT license. See [LICENSE](LICENSE) for details.