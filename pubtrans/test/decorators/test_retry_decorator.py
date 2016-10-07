"""
Tests for retry decorator
"""
from tornado import gen
from tornado import ioloop
from tornado import testing

import pubtrans.application
from pubtrans.common import exceptions
from pubtrans.decorators import retry_decorator

app = pubtrans.application.make_app()


class TestRetryDecorator(testing.AsyncTestCase):

    def setUp(self):
        super(TestRetryDecorator, self).setUp()
        self.actual_tries = 0

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    @testing.gen_test
    def test_retry_if_exception_to_check(self):

        expected_tries = 3

        @retry_decorator.retry(exceptions.ExternalProviderUnavailableTemporarily,
                               tries=expected_tries, delay=0.1, backoff=0.1)
        @gen.coroutine
        def some_func():
            self.actual_tries += 1
            if self.actual_tries < expected_tries:
                raise exceptions.ExternalProviderUnavailableTemporarily("some error")

        yield some_func()

        self.assertEqual(expected_tries, self.actual_tries)

    @testing.gen_test
    def test_does_not_retry_if_not_exception_to_check(self):

        expected_tries = 1

        @retry_decorator.retry(exceptions.ExternalProviderUnavailableTemporarily,
                               tries=3, delay=0.1, backoff=0.1)
        @gen.coroutine
        def some_func():
            self.actual_tries += 1
            if self.actual_tries < expected_tries:
                raise exceptions.ExternalProviderUnavailablePermanently("some error")

        yield some_func()

        self.assertEqual(expected_tries, self.actual_tries)
