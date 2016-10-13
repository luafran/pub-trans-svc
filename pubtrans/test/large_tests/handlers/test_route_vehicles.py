import json
from tornado import ioloop
from tornado import testing
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.domain import api

app = application.make_app()


class TestRouteVehicles(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteVehicles, self).setUp()

    def get_app(self):
        return app

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def test_get_vehicles_without_last_time_should_return_400(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/vehicles'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 400)
        actual_response = json.loads(response.body)

        expected_response = {
            "context": "Missing argument lastTime",
            "developer_message": "No value provided for an argument with required value",
            "user_message": "No value provided for an argument with required value"
        }
        self.assertDictContainsSubset(expected_response, actual_response)

    def test_get_vehicles(self):
        request = HTTPRequest(
            self.get_url('/v1/sf-muni/routes/E/vehicles?lastTime=1476314411287'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 200)
        route_vehicles = json.loads(response.body)

        self.assertIsNotNone(route_vehicles)
        self.assertIsNotNone(route_vehicles.get(api.TAG_VEHICLES))
        self.assertIsNotNone(route_vehicles.get(api.TAG_LAST_TIME))
