import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestStats(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestStats, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_all_stats(self):
        request = HTTPRequest(
            self.get_url('/v1/stats'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        actual_response = json.loads(response.body)
        uri_count = actual_response.get(api.TAG_URI_COUNT)
        self.assertIsNotNone(uri_count)
        slow_requests = actual_response.get(api.TAG_SLOW_REQUESTS)
        self.assertIsNotNone(slow_requests)

    def test_get_one_stat(self):
        request = HTTPRequest(
            self.get_url('/v1/stats/uri_count'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        actual_response = json.loads(response.body)
        uri_count = actual_response.get(api.TAG_URI_COUNT)
        self.assertIsNotNone(uri_count)
        slow_requests = actual_response.get(api.TAG_SLOW_REQUESTS)
        self.assertIsNone(slow_requests)
