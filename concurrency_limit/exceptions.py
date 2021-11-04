__all__ = [
    'ConcurrencyLimitException',
    'ConcurrencyLimitExceededException',
]


class ConcurrencyLimitException(Exception):
    """
    Base class for all concurrency limit related exceptions.
    """
    _msg_template = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            self._msg_template.format(*args, **kwargs) if self._msg_template else None,
        )


class ConcurrencyLimitExceededException(ConcurrencyLimitException):
    _msg_template = 'Exceeded the concurrency limit of {limit} executions. Waited for {timeout} seconds.'
