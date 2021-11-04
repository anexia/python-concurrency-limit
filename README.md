python-concurrency-limit
========================

`python-concurrency-limit` is a library that implements a distributed concurrency limiting mechanism using Redis as a
backend. The library allows to limit the number of concurrent executions of code sections, either by waiting until
the currently running execution threads go below the limit, or by raising an exception if there are currently too many
execution threads.


# Installation

With a [correctly configured](https://pipenv.pypa.io/en/latest/basics/#basic-usage-of-pipenv) `pipenv` toolchain:

```sh
pipenv install git+https://github.com/anexia-it/python-concurrency-limit.git@main
```

You may also use classic `pip` to install the package:

```sh
pip install git+https://github.com/anexia-it/python-concurrency-limit.git@main
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

# List of developers

* Andreas Stocker <AStocker@anexia-it.com>, Lead Developer
