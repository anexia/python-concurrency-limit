import time

import redis

from ._connections import *
from .configuration import *

__all__ = ["limit_clean", "limit_iter"]


def limit_clean(
    redis_configuration: RedisConfiguration, limit_configuration: LimitConfiguration
):
    """
    Cleans stale limit locks in the hash for the given limit configuration.

    :param redis_configuration: RedisConfiguration object containing the configuration details for connecting to Redis.
    :param limit_configuration: LimitConfiguration object containing the configuration details for the limit.
    :return: Number of cleaned items
    """
    client = get_redis(redis_configuration)
    current = int(time.time())
    count = 0

    lock_key = limit_configuration.key

    # If the key does not contain a hash, Redis fails with a WRONGTYPE exception that
    # we handle by deleting the key and re-trying.
    try:
        for scan_lock_id, scan_lock_expire in client.hscan_iter(lock_key):
            try:
                clean_lock = current >= int(scan_lock_expire)
            except (ValueError, TypeError):
                clean_lock = True

            if clean_lock:
                count += client.hdel(lock_key, scan_lock_id)

    except redis.ResponseError as exc:
        if str(exc).startswith("WRONGTYPE"):
            client.delete(lock_key)
            return 1

        raise  # pragma: no cover

    return count


def limit_iter(redis_configuration: RedisConfiguration, key_pattern: str):
    """
    Return an iterator over the items in Redis specified by `key_pattern`
    using the Redis connection specified by `redis_configuration`.

    :param redis_configuration: The configuration for connecting to Redis.
    :param key_pattern: The pattern for Redis to iterate over.
    :return: Scan Iterator
    """
    return get_redis(redis_configuration).scan_iter(key_pattern)
