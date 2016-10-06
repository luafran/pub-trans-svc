"""
Tests for health resource
"""
from tornado import testing

import pubtrans.application

app = pubtrans.application.make_app()


class TestHealthCheck(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestHealthCheck, self).setUp()

    def tearDown(self):
        pass

    def get_app(self):
        return app

    def test_when_ok_returns_200(self):
        self.http_client.fetch(self.get_url('/health'), self.stop, method='GET')
        response = self.wait()
        self.assertEqual(200, response.code, "Response should be 200, got %s instead" % response.code)
