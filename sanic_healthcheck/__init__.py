"""sanic_healthcheck: health checks for your Sanic applications."""

__title__ = 'sanic_healthcheck'
__version__ = '0.1.0'
__description__ = 'Health checks for your Sanic applications'
__author__ = 'Erick Daniszewski'
__author_email__ = 'edaniszewski@gmail.com'
__url__ = 'https://github.com/vapor-ware/sanic-healthcheck'
__license__ = 'MIT'


import logging

from .health import HealthCheck
from .ready import ReadyCheck

logging.getLogger(__name__).addHandler(logging.NullHandler())


__all__ = [
    'HealthCheck',
    'ReadyCheck',
]
