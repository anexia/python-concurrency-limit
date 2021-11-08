import dataclasses
import redis


__all__ = [
    'RedisConfiguration',
    'LimitConfiguration',
]


@dataclasses.dataclass(eq=True, frozen=True)
class RedisConfiguration:
    """
    Redis connection configuration.
    """
    host: str = None
    "The hostname or IP of the Redis server."

    port: int = 6379
    "The Redis server port."

    db: int = 0
    "The Redis database to use."

    username: str = None
    "The authentication username."

    password: str = None
    "The authentication password."

    max_connections: int = 10
    "The maximum connections on the connection pool."

    timeout: int = 10
    "The Redis server connection timeout."

    secure: bool = False
    "Use secure connection to Redis server."

    connection_pool: redis.ConnectionPool = None
    "Use this connection pool instance instead of the other fields, if set."


@dataclasses.dataclass(eq=True, frozen=True)
class LimitConfiguration:
    """
    Concurrency limit configuration.
    """
    key: str
    "The concurrency limit group identifier."

    limit: int
    "The limit for concurrently running executions of a concurrency group."

    limit_timeout: int = 10
    "Wait time for acquiring an execution slot before raising a `ConcurrencyLimitExceededException` exception."

    limit_interval: float = 0.1
    "Wait time between attempts to acquire an execution slot."

    limit_expire: int = 60
    "Expire time for the concurrency counter on Redis."
