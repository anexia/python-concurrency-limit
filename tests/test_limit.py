import time

import pytest
import pytest_mock

import concurrency_limit

from test_base import *


def test_limit_without_concurrency(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    with concurrency_limit.limit(
        concurrency_limit.RedisConfiguration(),
        concurrency_limit.LimitConfiguration(key="key-1", limit=1),
    ) as slot_id:
        assert slot_id == 1


def test_limit_slot_ids(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    slot_ids = []

    @concurrent(threads=10)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(
                key="key-1", limit=10, limit_timeout=0
            ),
        ) as slot_id:
            slot_ids.append(slot_id)
            time.sleep(1)

    _concurrent_function()

    slot_ids.sort()
    assert slot_ids == list(range(1, 11))


def test_limit_within_limit(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    @concurrent(threads=1)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(key="key-1", limit=1, limit_timeout=0),
        ):
            time.sleep(1)

    _concurrent_function()


def test_limit_exceeded_limit_without_timeout(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    @concurrent(threads=10)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(key="key-1", limit=1, limit_timeout=0),
        ):
            time.sleep(1)

    with pytest.raises(concurrency_limit.ConcurrencyLimitException):
        _concurrent_function()


def test_limit_exceeded_limit_within_timeout(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    @concurrent(threads=10)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(key="key-1", limit=5, limit_timeout=5),
        ):
            time.sleep(1)

    _concurrent_function()


def test_limit_exceeded_limit_exceeded_timeout(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    @concurrent(threads=10)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(key="key-1", limit=5, limit_timeout=5),
        ):
            time.sleep(10)

    with pytest.raises(concurrency_limit.ConcurrencyLimitException):
        _concurrent_function()


def test_limit_within_limit_expire(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    with concurrency_limit.limit(
        concurrency_limit.RedisConfiguration(),
        concurrency_limit.LimitConfiguration(
            key="key-1", limit=1, limit_expire=5, limit_timeout=0
        ),
    ):
        time.sleep(1)

        with pytest.raises(concurrency_limit.ConcurrencyLimitException):
            with concurrency_limit.limit(
                concurrency_limit.RedisConfiguration(),
                concurrency_limit.LimitConfiguration(
                    key="key-1", limit=1, limit_expire=5, limit_timeout=0
                ),
            ):
                time.sleep(1)


def test_limit_exceeded_limit_expire(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    with concurrency_limit.limit(
        concurrency_limit.RedisConfiguration(),
        concurrency_limit.LimitConfiguration(
            key="key-1", limit=1, limit_expire=5, limit_timeout=0
        ),
    ):
        time.sleep(10)

        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(
                key="key-1", limit=1, limit_expire=5, limit_timeout=0
            ),
        ):
            time.sleep(1)


def test_limit_with_high_load(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "concurrency_limit.context_managers.get_redis", return_value=RedisMock()
    )

    counter = 0

    @concurrent(threads=10_000)
    def _concurrent_function():
        with concurrency_limit.limit(
            concurrency_limit.RedisConfiguration(),
            concurrency_limit.LimitConfiguration(
                key="key-1", limit=500, limit_timeout=1
            ),
        ) as slot_id:
            nonlocal counter

            counter += 1

            assert 1 <= slot_id <= 500
            assert 1 <= counter <= 500

            time.sleep(1.5)
            counter -= 1

    with pytest.raises(concurrency_limit.ConcurrencyLimitException):
        _concurrent_function()


def test_limit_clean(mocker: pytest_mock.MockerFixture):
    client = RedisMock()
    mocker.patch("concurrency_limit.context_managers.get_redis", return_value=client)

    client.hset("key-1", "expired-1", int(time.time()) - 10)
    client.hset("key-1", "expired-2", int(time.time()) - 10)
    client.hset("key-1", "unexpired-1", int(time.time()) + 10)
    client.hset("key-1", "unexpired-2", int(time.time()) + 10)

    assert client.hlen("key-1") == 4
    assert concurrency_limit.limit_clean(
        concurrency_limit.RedisConfiguration(),
        concurrency_limit.LimitConfiguration(key="key-1", limit=1),
    ) == 2
    assert client.hlen("key-1") == 2

    for scan_key in concurrency_limit.limit_iter(concurrency_limit.RedisConfiguration(), "key-*"):
        for scan_lock_id, _ in client.hscan_iter(scan_key):
            assert scan_lock_id.startswith("unexpired-")
