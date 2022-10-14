# Copyright 2016-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
import os

from .strtobool import strtobool

from odoo import http
from odoo.tools import config
from odoo.tools.func import lazy_property

from .session import RedisSessionStore

_logger = logging.getLogger(__name__)

try:
    import redis
    from redis.sentinel import Sentinel
except ImportError:
    redis = None  # noqa
    _logger.debug("Cannot 'import redis'.")


def is_true(strval):
    return bool(strtobool(strval or "0".lower()))


sentinel_host = os.environ.get(
    "ODOO_SESSION_REDIS_SENTINEL_HOST", config.get("redis_sentinel_host")
)
sentinel_master_name = os.environ.get(
    "ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME", config.get("redis_sentinel_master_name")
)
if sentinel_host and not sentinel_master_name:
    raise Exception(
        "ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME must be defined "
        "when using session_redis"
    )
sentinel_port = int(
    os.environ.get(
        "ODOO_SESSION_REDIS_SENTINEL_PORT", config.get("redis_sentinel_port", 26379)
    )
)
host = os.environ.get("ODOO_SESSION_REDIS_HOST", config.get("redis_host", "localhost"))
port = int(os.environ.get("ODOO_SESSION_REDIS_PORT", config.get("redis_port", 6379)))
prefix = os.environ.get("ODOO_SESSION_REDIS_PREFIX", config.get("redis_prefix"))
url = os.environ.get("ODOO_SESSION_REDIS_URL", config.get("redis_url"))
password = os.environ.get("ODOO_SESSION_REDIS_PASSWORD", config.get("redis_password"))
expiration = os.environ.get(
    "ODOO_SESSION_REDIS_EXPIRATION", config.get("redis_expiration")
)
anon_expiration = os.environ.get(
    "ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS", config.get("redis_expiration_anonymous")
)


@lazy_property
def session_store(self):
    if sentinel_host:
        sentinel = Sentinel([(sentinel_host, sentinel_port)], password=password)
        redis_client = sentinel.master_for(sentinel_master_name)
    elif url:
        redis_client = redis.from_url(url)
    else:
        redis_client = redis.Redis(host=host, port=port, password=password)
    return RedisSessionStore(
        redis=redis_client,
        prefix=prefix,
        expiration=expiration,
        anon_expiration=anon_expiration,
        session_class=http.Session,
    )


def purge_fs_sessions(path):
    for fname in os.listdir(path):
        path = os.path.join(path, fname)
        try:
            os.unlink(path)
        except OSError:
            pass


if redis and (
    is_true(os.environ.get("ODOO_SESSION_REDIS")) or config.get("session_redis")
):
    if sentinel_host:
        _logger.debug(
            "HTTP sessions stored in Redis with prefix '%s'. "
            "Using Sentinel on %s:%s",
            prefix or "",
            sentinel_host,
            sentinel_port,
        )
    else:
        _logger.debug(
            "HTTP sessions stored in Redis with prefix '%s' on " "%s:%s",
            prefix or "",
            host,
            port,
        )
    http.Application.session_store = session_store
    if config.get("redis_purge_filesystem_sessions"):
        # clean the existing sessions on the file system
        purge_fs_sessions(config.session_dir)
