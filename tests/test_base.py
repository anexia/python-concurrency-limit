import collections
import fnmatch
import functools
import threading
import time

__all__ = ["RedisMock", "concurrent"]


class RedisMock:
    def __init__(self):
        self._lock = threading.Lock()
        self._hashes = collections.defaultdict(lambda: {})
        self._expires = collections.defaultdict(lambda: time.time() + 2 ** 32)

    def scan_iter(self, match):
        for key in fnmatch.filter(self._hashes.keys(), match):
            yield key

    def hlen(self, name):
        with self._lock:
            self._clean_expired(name)
            return len(self._hashes[name])

    def hset(self, name, key, value):
        with self._lock:
            self._hashes[name][key] = str(value)

    def hdel(self, name, *keys):
        count = 0

        with self._lock:
            for key in keys:
                try:
                    del self._hashes[name][key]
                    count += 1
                except KeyError:
                    pass

        return count

    def hscan_iter(self, name):
        with self._lock:
            self._clean_expired(name)
            _hash = dict(self._hashes[name])

        for hkey, hvalue in _hash.items():
            yield hkey, hvalue

    def expire(self, name, _time):
        with self._lock:
            self._expires[name] = _time + time.time()

    def pipeline(self):
        client = self

        class _Pipeline:
            def __init__(self):
                self.buffer = []

            def __getattr__(self, item):
                def _wrapper(*args, **kwargs):
                    self.buffer.append(wrapped(*args, **kwargs))
                    return self

                wrapped = getattr(client, item)

                return _wrapper

            def execute(self):
                try:
                    return self.buffer
                finally:
                    self.buffer = []

        return _Pipeline()

    def _clean_expired(self, name):
        if time.time() > self._expires[name]:
            del self._expires[name]

            try:
                del self._hashes[name]
            except KeyError:
                pass


def concurrent(threads: int):
    class ExceptionAwareThread(threading.Thread):
        def run(self):
            try:
                setattr(self, "_ret", self._target(*self._args, **self._kwargs))
            except BaseException as e:
                setattr(self, "_exc", e)

        def join(self, timeout=None):
            super().join(timeout=timeout)

            exc = getattr(self, "_exc", None)
            ret = getattr(self, "_ret", None)

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
