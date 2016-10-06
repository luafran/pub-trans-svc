"""
Tests for health resource
"""
from tornado import testing

import pubtrans.application

app = pubtrans.application.make_app()


class TestDefaultHandler(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestDefaultHandler, self).setUp()

    def tearDown(self):
        pass

    def get_app(self):
        return app

    def test_get_notfound(self):
        self.http_client.fetch(self.get_url('/notfound'), self.stop, method='GET')
        response = self.wait()
        self.assertEqual(404, response.code, "Response should be 404, got %s instead" % response.code)

    def test_post_notfound(self):
        self.http_client.fetch(self.get_url('/notfound'), self.stop, method='POST', body='')
        response = self.wait()
        self.assertEqual(404, response.code, "Response should be 404, got %s instead" % response.code)

    def test_put_notfound(self):
        self.http_client.fetch(self.get_url('/notfound'), self.stop, method='PUT', body='')
        response = self.wait()
        self.assertEqual(404, response.code, "Response should be 404, got %s instead" % response.code)

    def test_delete_notfound(self):
        self.http_client.fetch(self.get_url('/notfound'), self.stop, method='DELETE')
        response = self.wait()
        self.assertEqual(404, response.code, "Response should be 404, got %s instead" % response.code)
