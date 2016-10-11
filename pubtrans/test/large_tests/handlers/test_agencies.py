import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestAgencies(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestAgencies, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_all_agencies(self):
        request = HTTPRequest(
            self.get_url('/v1/agencies'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        actual_response = json.loads(response.body)
        agencies = actual_response.get(api.TAG_AGENCIES)
        self.assertIsNotNone(agencies)
        self.assertGreater(len(agencies), 1)
        self.assertIsNotNone(agencies[0].get(api.TAG_TAG))
        self.assertIsNotNone(agencies[0].get(api.TAG_TITLE))
        self.assertIsNotNone(agencies[0].get(api.TAG_REGION_TITLE))
