import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestRoutePredictions(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRoutePredictions, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_predictions_without_stop_tag_should_return_400(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/predictions'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 400)
        actual_response = json.loads(response.body)

        expected_response = {
            "context": "Missing argument stopTag",
            "developer_message": "No value provided for an argument with required value",
            "user_message": "No value provided for an argument with required value"
        }
        self.assertDictContainsSubset(expected_response, actual_response)

    def test_get_vehicles(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/predictions?stopTag=4502'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        route_predictions = json.loads(response.body)

        self.assertIsNotNone(route_predictions)
        self.assertIsNotNone(route_predictions.get(api.TAG_DIRECTIONS))
