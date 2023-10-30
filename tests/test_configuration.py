import typing

import redis.connection

import pytest

from concurrency_limit import RedisConfiguration


@pytest.mark.parametrize(
    "url,config",
    [
        (
            "redis://127.0.0.1:6379/1",
            RedisConfiguration(host="127.0.0.1", port=6379, db=1),
        ),
        (
            "redis://test-user:test-pw@127.0.0.1:6379/1",
            RedisConfiguration(
                host="127.0.0.1",
                port=6379,
                db=1,
                username="test-user",
                password="test-pw",
            ),
        ),
        (
            "rediss://127.0.0.1:6379/1",
            RedisConfiguration(
                host="127.0.0.1", port=6379, db=1, connection_class=redis.SSLConnection
            ),
        ),
        (
            "rediss://test-user:test-pw@127.0.0.1:6379/1",
            RedisConfiguration(
                host="127.0.0.1",
                port=6379,
                db=1,
                username="test-user",
                password="test-pw",
                connection_class=redis.SSLConnection,
            ),
        ),
        (
            "unix:///run/redis.sock?db=1",
            RedisConfiguration(
                path="/run/redis.sock",
                port=6379,
                db=1,
                connection_class=redis.UnixDomainSocketConnection,
            ),
        ),
        (
            "unix://test-user:test-pw@/run/redis.sock?db=1",
            RedisConfiguration(
                path="/run/redis.sock",
                port=6379,
                db=1,
                username="test-user",
                password="test-pw",
                connection_class=redis.UnixDomainSocketConnection,
            ),
        ),
    ],
)
def test_configuration_from_url(url: str, config: RedisConfiguration):
    assert RedisConfiguration.from_url(url) == config


@pytest.mark.parametrize(
    "url,kwargs,config",
    [
        (
            "redis://127.0.0.1:6379/1",
            {"connection_class": redis.SSLConnection},
            RedisConfiguration(
                host="127.0.0.1", port=6379, db=1, connection_class=redis.SSLConnection
            ),
        ),
        (
            "redis://127.0.0.1:6379/1",
            {"connection_class": redis.UnixDomainSocketConnection},
            RedisConfiguration(
                host="127.0.0.1",
                port=6379,
                db=1,
                connection_class=redis.UnixDomainSocketConnection,
            ),
        ),
    ],
)
def test_configuration_from_url_with_kwargs(
    url: str, kwargs: dict, config: RedisConfiguration
):
    assert RedisConfiguration.from_url(url, **kwargs) == config


@pytest.mark.parametrize(
    "config,expected_class",
    [
        (RedisConfiguration(), redis.Connection),
        (RedisConfiguration(secure=True), redis.SSLConnection),
        (RedisConfiguration(unix_socket=True), redis.UnixDomainSocketConnection),
        (RedisConfiguration(connection_class=redis.Connection), redis.Connection),
        (RedisConfiguration(connection_class=redis.SSLConnection), redis.SSLConnection),
        (
            RedisConfiguration(connection_class=redis.UnixDomainSocketConnection),
            redis.UnixDomainSocketConnection,
        ),
        (
            RedisConfiguration(secure=True, unix_socket=True),
            redis.UnixDomainSocketConnection,
        ),
        (
            RedisConfiguration(
                secure=True, unix_socket=True, connection_class=redis.Connection
            ),
            redis.Connection,
        ),
    ],
)
def test_configuration_get_connection_class(
    config: RedisConfiguration, expected_class: typing.Type[redis.Connection]
):
    assert config.get_connection_class() == expected_class
