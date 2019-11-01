
sanic-healthcheck
=================

``sanic-healthcheck`` provides a simple way to add health checks and readiness checks to
your `Sanic <https://github.com/huge-success/sanic>`_ application. This makes it easier to
monitor your application and ensure it is running in a health state. Monitoring or management
tools can ping these endpoints to determine application uptime and status, as well as perform
application restart to ensure your application isn't running in a degraded state.

``sanic-healthcheck`` was inspired by and borrows from `Runscope/healthcheck <https://github.com/Runscope/healthcheck>`_.

Installing
----------

.. code-block:: bash

   pip install sanic-healthcheck


Use Cases
---------

Docker Compose
~~~~~~~~~~~~~~

Docker Compose allows you to specify `health checks <https://docs.docker.com/compose/compose-file/#healthcheck>`_
in your compose file configuration. With a health check enabled in your application, you can configure
your Compose deployment to monitor the health of your application (running on port ``3000``):

.. code-block:: yaml

   healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/health']
      interval: 10s
      timeout: 3s
      retries: 2
      start_period: 10s


Kubernetes
~~~~~~~~~~

Kubernetes allows you to define `liveness and readiness probes <https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/>`_.
A health check is effectively equivalent to a liveness check.

.. code-block:: yaml

   apiVersion: v1
   kind: Pod
   metadata:
     labels:
       app: my-application
     name: my-application
   spec:
     containers:
     - name: my-application
       image: my/application:1.0
       livenessProbe:
         httpGet:
           path: /health
           port: 3000
         initialDelaySeconds: 10s
         periodSeconds: 10s
       readinessProbe:
         httpGet:
           path: /ready
           port: 3000


License
-------

sanic-healthcheck is licensed under the MIT license. See the project's
`LICENSE <https://github.com/edaniszewski/sanic-healthcheck/blob/master/LICENSE>`_ file for details.

.. toctree::
   :maxdepth: 2
   :hidden:

   usage
   api_reference

