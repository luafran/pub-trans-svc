import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application

app = application.make_app()


class TestNextBusAgencies(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestNextBusAgencies, self).setUp()

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
        agencies = actual_response.get('agencies')
        self.assertIsNotNone(agencies)
        self.assertIsNotNone(agencies[0].get('tag'))
