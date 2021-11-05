import threading
import redis

from .configuration import *


__all__ = [
    'get_redis',
]

_connection_pool_map = {}
_connection_pool_lock = threading.Lock()


def get_redis(configuration: RedisConfiguration) -> redis.Redis:
    """
    Gets the Redis client used to store the concurrency keys.

    :param configuration: Redis connection configuration
    :return: Redis client
    """
    if configuration.connection_pool:
        return _get_redis_by_connection_pool(configuration)

    else:
        return _get_redis_by_credentials(configuration)


def _get_redis_by_credentials(configuration: RedisConfiguration) -> redis.Redis:
    """
    Gets the Redis client used to store the concurrency keys using the connection credentials on the configuration
    object. This method creates a connection pool using the credentials, als will use this connection pool for
    all subsequent calls of this method with the same configuration.

    :param configuration: Redis connection configuration
    :return: Redis client
    """
    global _connection_pool_map
    global _connection_pool_lock

    with _connection_pool_lock:
        if configuration not in _connection_pool_map:
            _connection_pool_map[configuration] = redis.BlockingConnectionPool(
                host=configuration.host,
                port=configuration.port,
                db=configuration.db,
                username=configuration.username,
                password=configuration.password,
                max_connections=configuration.max_connections,
                timeout=configuration.timeout,
                connection_class=redis.SSLConnection if configuration.secure else redis.Connection,
            )

        return redis.Redis(connection_pool=_connection_pool_map[configuration])


def _get_redis_by_connection_pool(configuration: RedisConfiguration) -> redis.Redis:
    """
    Gets the Redis client used to store the concurrency keys using the connection pool on the configuration
    object.

    :param configuration: Redis connection configuration
    :return: Redis client
    """
    return redis.Redis(connection_pool=configuration.connection_pool)
