import time
import threading
import collections
import functools


__all__ = [
    'RedisMock',
    'concurrent',
]


class RedisMock:

    _lock = threading.Lock()
    _keys = collections.defaultdict(lambda: 0)
    _expires = collections.defaultdict(lambda: time.time() + 2 ** 32)

    def incr(self, name, amount=1):
        with self._lock:
            if time.time() > self._expires[name]:
                del self._keys[name]
                del self._expires[name]

            self._keys[name] += amount
            return self._keys[name]

    def decr(self, name, amount=1):
        return self.incr(name, amount=amount * -1)

    def setnx(self, name, value):
        with self._lock:
            if time.time() > self._expires[name]:
                del self._keys[name]
                del self._expires[name]

            if name not in self._keys:
                self._keys[name] = value
                return 1
            return 0

    def expire(self, name, ttl):
        with self._lock:
            if name in self._keys:
                self._expires[name] = time.time() + ttl
                return 1
            return 0


def concurrent(threads: int):
    class ExceptionAwareThread(threading.Thread):
        def run(self):
            try:
                setattr(self, '_ret', self._target(*self._args, **self._kwargs))
            except BaseException as e:
                setattr(self, '_exc', e)

        def join(self, timeout=None):
            super().join(timeout=timeout)

            exc = getattr(self, '_exc', None)
            ret = getattr(self, '_ret', None)

            if exc:
                raise exc
            else:
                return ret

    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            ts = []

            # create the threads
            for i in range(threads):
                ts.append(ExceptionAwareThread(target=func, args=args, kwargs=kwargs))

            # start the threads
            for t in ts:
                t.start()

            # wait for all threads to finish
            for t in ts:
                t.join()

        return _wrapper

    return _decorator
