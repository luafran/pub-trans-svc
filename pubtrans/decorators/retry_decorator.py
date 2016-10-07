"""
Decorator that retries a given function a number of times if the given exception is raised
"""
import functools
import time

from tornado import gen
from tornado import ioloop


def retry(exception_to_check, tries=3, delay=3, backoff=2):
    """
    Retry calling the decorated function using an exponential backoff

    @param exception_to_check: may be one exception or a tuple of them
    @param tries: number of times to try
    @param delay: initial delay between retries in seconds
    @param backoff: backoff multiplier. E.g. value of 2 will double the delay after each retry
    """

    def decorator_retry(function):
        """
        Decorator to retry function calls using an exponential backoff
        @param function function to decorate
        """

        @gen.coroutine
        @functools.wraps(function)
        def function_retry(*args, **kwargs):
            """
            Retry algorithm using an exponential backoff
            """

            number_of_tries = tries
            delay_seconds = delay

            while number_of_tries > 1:
                try:
                    response = yield function(*args, **kwargs)
                    raise gen.Return(response)
                except exception_to_check:
                    yield gen.Task(ioloop.IOLoop.current().add_timeout,
                                   time.time() + delay_seconds)
                    number_of_tries -= 1
                    delay_seconds *= backoff

            response = yield function(*args, **kwargs)
            raise gen.Return(response)

        return function_retry   # Decorator

    return decorator_retry
