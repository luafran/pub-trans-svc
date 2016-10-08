import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestNextBusAgencies(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestNextBusAgencies, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_all_routes(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        actual_response = json.loads(response.body)
        routes = actual_response.get(api.TAG_ROUTES)
        self.assertIsNotNone(routes)
        self.assertGreater(len(routes), 1)
        self.assertIsNotNone(routes[0].get(api.TAG_TAG))
        self.assertIsNotNone(routes[0].get(api.TAG_TITLE))

    def test_get_a_single_routes(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        actual_response = json.loads(response.body)
        self.assertIsNotNone(actual_response.get(api.TAG_TAG))
        self.assertIsNotNone(actual_response.get(api.TAG_TITLE))
        self.assertIsNotNone(actual_response.get(api.TAG_COLOR))
        self.assertIsNotNone(actual_response.get(api.TAG_OPPOSITE_COLOR))
