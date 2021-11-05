import contextlib
import time

from ._connections import *
from .configuration import *
from .exceptions import *


__all__ = [
    'limit',
]


@contextlib.contextmanager
def limit(
        redis_configuration: RedisConfiguration,
        limit_configuration: LimitConfiguration,
):
    """
    Context manager that limits concurrency within its scope as defined on the given limit configuration. This is
    done with the logic as follows:
     - If the count of concurrently running scopes is below the configured limit, the scope is executed immediately.
     - If the count of concurrently running scopes exceeds the configured limit, the context manager wait unit it
       goes below the configured limit.
     - If the count of concurrently running scopes does not go below the configured limit with the configured
       timeout, a `ConcurrencyLimitExceededException` exception is raised.

    :param redis_configuration: Redis configuration
    :param limit_configuration: Limit configuration
    :raise ConcurrencyLimitExceededException: Configured concurrency limit not under-run within configured timeout
    :return:
    """
    client = get_redis(redis_configuration)
    start = time.time()
    executed = False

    try:
        # we loop as long as it was not possible to execute the context manager's scope.
        while not executed:
            # first we try to acquire an execution slot by increasing the concurrency counter and checking if the
            # counter is below the configured limit. if it is, we execute the scope. if it is not, we immediately
            # decrease the concurrency counter as we are not able to execute the scope.
            count = client.incr(limit_configuration.key, 1)
            client.expire(limit_configuration.key, limit_configuration.limit_expire)

            # if there is no available execution slot.
            if count > limit_configuration.limit:
                client.decr(limit_configuration.key, 1)
                elapsed = time.time() - start

                # if we are waiting longer than the configured timeout, we raise a `ConcurrencyLimitExceededException`
                # exception. executing the context manager's scope failed in this case.
                if elapsed > limit_configuration.limit_timeout:
                    raise ConcurrencyLimitExceededException(
                        limit=limit_configuration.limit,
                        timeout=limit_configuration.limit_timeout,
                    )

                # we failed to acquire an execution slot for the context manager's scope, but we want to try again.
                # however, we wait the configured interval before we do so.
                time.sleep(limit_configuration.limit_interval)

            # if we successfully acquired an execution slot for the context manager's scope.
            else:
                executed = True
                yield count

    finally:
        if executed:
            client.setnx(limit_configuration.key, 1)
            count = client.decr(limit_configuration.key, 1)

            # if there are nested concurrency contexts on the same key, and the outer concurrency timed out, we might
            # end up with a negative count. we reset to 0 if this happens.
            if count < 0:
                client.decr(limit_configuration.key, count)

        del client
