import dataclasses
import typing

import redis
import redis.connection

__all__ = ["RedisConfiguration", "LimitConfiguration"]


@dataclasses.dataclass(eq=True, frozen=True)
class RedisConfiguration:
    """
    Redis connection configuration.
    """

    host: str = None
    "The hostname or IP of the Redis server."

    port: int = 6379
    "The Redis server port."

    path: str = None
    "The socket path used if `unix_socket` is set."

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

    unix_socket: bool = False
    "Use UNIX socket connection to Redis server. Will ignore `secure`, if set."

    connection_class: typing.Type[redis.connection.AbstractConnection] = None
    "Redis connection class to use instead of `secure` and `unix_socket` fields, if set."

    connection_pool: redis.ConnectionPool = None
    "Use this connection pool instance instead of the other fields, if set."

    def get_connection_class(self) -> typing.Type[redis.connection.AbstractConnection]:
        """
        Returns the `redis.Connection` class to use based on this configuration.

        Priority of configuration values:

        1. `connection_class` if set
        2. `redis.UnixDomainSocketConnection` if `unix_socket` is set
        3. `redis.SSLConnection` if `secure` is set
        4. `redis.Connection` as last resort

        :return: Determined `redis.Connection` class
        """
        if self.connection_class is not None:
            return self.connection_class

        if self.unix_socket:
            return redis.UnixDomainSocketConnection

        if self.secure:
            return redis.SSLConnection

        return redis.Connection

    @classmethod
    def from_url(cls, url, **kwargs):
        """
        Returns a `RedisConfiguration` object based on the given URL. This behaves exactly the same as the `from_url`
        methods of the `redis-py` package.

        Examples:

        - redis://[[username]:[password]]@localhost:6379/0
        - rediss://[[username]:[password]]@localhost:6379/0
        - unix://[[username]:[password]]@/path/to/socket.sock?db=0

        :param url: Redis URL to generate a `RedisConfiguration` from
        :param kwargs: Additional arguments to set for the configuration object
        """
        url_options = redis.connection.parse_url(url)

        if "connection_class" in kwargs:
            url_options["connection_class"] = kwargs["connection_class"]

        kwargs.update(url_options)
        return cls(**kwargs)


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
