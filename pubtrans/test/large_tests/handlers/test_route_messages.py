import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestRouteMessages(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteMessages, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_messages(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/messages'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        route_messages = json.loads(response.body)

        self.assertIsNotNone(route_messages)
        self.assertIsNotNone(route_messages.get(api.TAG_ALL_MESSAGES))
