concurrency-limit
=================

[![PyPI](https://badge.fury.io/py/concurrency-limit.svg)](https://pypi.org/project/concurrency-limit/)
[![Test Status](https://github.com/anexia/python-concurrency-limit/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/anexia/python-concurrency-limit/actions/workflows/test.yml)
[![Codecov](https://codecov.io/gh/anexia/python-concurrency-limit/branch/main/graph/badge.svg)](https://codecov.io/gh/anexia/python-concurrency-limit)

`concurrency-limit` is a library that implements a distributed concurrency limiting mechanism using Redis as a
backend. The library allows to limit the number of concurrent executions of code sections, either by waiting until
the currently running execution threads go below the limit, or by raising an exception if there are currently too many
execution threads.

# Installation

With a [correctly configured](https://pipenv.pypa.io/en/latest/basics/#basic-usage-of-pipenv) `pipenv` toolchain:

```sh
pipenv install concurrency-limit
```

You may also use classic `pip` to install the package:

```sh
pip install concurrency-limit
```

# Getting started

## How it works
- A limit of concurrently running scopes of a concurrency group can be defined using the `limit` decorator. A 
  concurrency group is defined by the `key` attribute of the `LimitConfiguration` instance.
- If the count of concurrently running scopes of a concurrency group is below the configured limit, the scope is 
  executed immediately.
- If the count of concurrently running scopes of a concurrency group exceeds the configured limit, the context manager 
  wait unit it goes below the configured limit.
- If the count of concurrently running scopes of a concurrency group does not go below the configured limit with the 
  configured timeout, a `ConcurrencyLimitExceededException` exception is raised.

## Usage

### Example 1

Limit the concurrency group `"example-1"` to `100` concurrently running scopes. If there are already `100` running
scopes, wait until the count of concurrently running scopes go below `100`. Fail if this does not happen within `10` 
seconds by raising a `ConcurrencyLimitExceededException` exception.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration(
    host='127.0.0.1',
    port=6379,
)
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-1',
    limit=100,
    limit_timeout=10,
)

with concurrency_limit.limit(redis_configuration, limit_configuration):
    do_something_magic()
```

### Example 2

Limit the concurrency group `"example-1"` to `100` concurrently running scopes. If there are already `100` running
scopes, wait until the count of concurrently running scopes go below `100`. Fail if this does not happen within `10` 
seconds by raising a `ConcurrencyLimitExceededException` exception. Check if the concurrently running scopes 
are below the limit every `1` second.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration(
    host='127.0.0.1',
    port=6379,
)
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-2',
    limit=100,
    limit_timeout=0,
    limit_interval=1.0,
)

with concurrency_limit.limit(redis_configuration, limit_configuration):
    do_something_magic()
```

### Example 3

Limit the concurrency group `"example-3"` to `100` concurrently running scopes. If there are already `100` running
scopes, fail immediately by raising a `ConcurrencyLimitExceededException` exception.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration(
    host='127.0.0.1',
    port=6379,
)
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-3',
    limit=100,
    limit_timeout=0,
)

with concurrency_limit.limit(redis_configuration, limit_configuration):
    do_something_magic()
```

### Example 4

Limit the concurrency group `"example-4"` to `100` concurrently running scopes. The implementation of the 
concurrency group needs to now the number of the concurrently running scope.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration(
    host='127.0.0.1',
    port=6379,
)
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-4',
    limit=100,
)

with concurrency_limit.limit(redis_configuration, limit_configuration) as group_number:
    do_something_magic(group_number)
```

### Example 5

Limit the concurrency group `"example-5"` to `100` concurrently running scopes. There is already an existing connection
pool to Redis within your application, that `concurrency_limit` should use.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration(
    connection_pool=my_redis_connection_pool,
)
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-5',
    limit=100,
)

with concurrency_limit.limit(redis_configuration, limit_configuration):
    do_something_magic()
```

### Example 6

Limit the concurrency group `"example-6"` to `100` concurrently running scopes. A redis URL will be used instead of
separately specifying host and port for the redis connection.

```python
import concurrency_limit

redis_configuration = concurrency_limit.RedisConfiguration.from_url('redis://127.0.0.1:6379/0')
limit_configuration = concurrency_limit.LimitConfiguration(
    key='example-6',
    limit=100,
)

with concurrency_limit.limit(redis_configuration, limit_configuration):
    do_something_magic()
```

## Configuration options

### `RedisConfiguration`

#### `host: str`

Default: `None`

The hostname or IP of the Redis server.

#### `port: int`

Default: `6379`

The Redis server port.

#### `path: str`

Default: `None`

The socket path used if `unix_socket` is set.

#### `db: int`

Default: `0`

The Redis database to use.

#### `username: str`

Default: `None`

The authentication username.

#### `password: str`

Default: `None`

The authentication password.

#### `max_connections: int`

Default: `10`

The maximum connections on the connection pool for each process.

#### `timeout: int`

Default: `10`

The Redis server connection timeout.

#### `secure: bool`

Default: `False`

Use secure connection to Redis server.

#### `unix_socket: bool`

Default: `False`

Use UNIX socket connection to Redis server. Will ignore `secure`, if set as there is no SSL mode with sockets.

#### `connection_class: typing.Type[redis.Connection]`

Default: `None`

Redis connection class to use instead of `secure` and `unix_socket` fields, if set.

#### `connection_pool: redis.ConnectionPool`

Default: `None`

Use this connection pool instance instead of the other fields, if set. All other fields of the configuration
instance are ignored in this case.

### `LimitConfiguration`

#### `key: str`

The concurrency limit group identifier. Use the same key for different scopes that should use the same concurrency
counter. You may use different limit configurations for scopes that use the same key.

#### `limit: int`

The concurrency limit for the limited concurrency group (defined by the `key`). If there are more concurrent executions
than this limit allows, the execution may wait for the concurrency count to go below the limit, or may
fail by raising a `ConcurrencyLimitExceededException` exception.

#### `limit_timeout: int`

Default: `10`

The timeout that defines how long to wait for the concurrency count to go below the configured limit. The timeout
is configured in seconds. Set to `0` if you want to raise a `ConcurrencyLimitExceededException` exception immediately 
if there are too many concurrent executions.

#### `limit_interval: float`

Default: `0.1`

If there are too many concurrent executions of a scope, and a `limit_timeout` is set to a value greater than `0`, this
configuration defines the interval to re-check the current concurrency count. As soon as the concurrency count is 
below the configured limit, the execution of the scope starts.

#### `limit_expire: int`

Default: `60`

The expiry time of the concurrency count key, configured in seconds. If a concurrency count is untouched for the 
configured time, it will be deleted.

# Supported versions

|             | Supported |
|-------------|-----------|
| Python 3.9  | ✓         |
| Python 3.10 | ✓         |
| Python 3.11 | ✓         |

# List of developers

* Andreas Stocker <AStocker@anexia.com>, Lead Developer
* Patrick Taibel <PTaibel@anexia.com>, Developer
