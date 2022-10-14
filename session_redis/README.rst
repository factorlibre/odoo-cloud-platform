Sessions in Redis
=================

This addon allows to store the web sessions in Redis.

Configuration
-------------

The storage of sessions in Redis is activated using environment variables or enabling
the keys in odoo cfg

* ``ODOO_SESSION_REDIS`` in env has to be ``1`` or ``true``. In odoo cfg ``session_redis`` has to be True
* ``ODOO_SESSION_REDIS_HOST`` in env ``redis_host`` in cfg: is the redis hostname (default is ``localhost``)
* ``ODOO_SESSION_REDIS_PORT`` in env ``redis_port`` in cfg: is the redis port (default is ``6379``)
* ``ODOO_SESSION_REDIS_PASSWORD`` in env ``redis_password`` in cfg: is the password for the AUTH command
  (optional)
* ``ODOO_SESSION_REDIS_URL`` in env ``redis_url`` in cfg: is an alternative way to define the Redis server
  address. It's the preferred way when you're using the ``rediss://`` protocol.
* ``ODOO_SESSION_REDIS_PREFIX`` in env ``redis_prefix`` in cfg: is the prefix for the session keys (optional)
* ``ODOO_SESSION_REDIS_EXPIRATION`` in env ``redis_expiration`` in cfg: is the time in seconds before expiration of
  the sessions (default is 7 days)
* ``ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS`` in env ``redis_expiration`` in cfg: is the time in seconds before expiration of
  the anonymous sessions (default is 3 hours)


The keys are set to ``session:<session id>``.
When a prefix is defined, the keys are ``session:<prefix>:<session id>``

This addon must be added in the server wide addons with (``--load`` option):

``--load=web,session_redis``

Limitations
-----------

* The server has to be restarted in order for the sessions to be stored in
  Redis.
* All the users will have to login again as their previous session will be
  dropped.
* The addon monkey-patch ``odoo.http.Root.session_store`` with a custom
  method when the Redis mode is active, so incompatibilities with other addons
  is possible if they do the same.
