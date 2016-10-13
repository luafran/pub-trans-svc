import json
import mock
from tornado import ioloop
from tornado import testing
from tornado import gen
from tornado.httpclient import HTTPRequest

from pubtrans import application
from pubtrans.common.rest_adapter import RestAdapter
from pubtrans.config import settings
from pubtrans.domain import api
from pubtrans.repositories.redis_repository import RedisRepository
from pubtrans.services.next_bus import NextBusService

app = application.make_app()


class TestRouteVehiclesHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteVehiclesHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'
        self.route_tag = 'E'
        self.lastTime = '1476314411287'

        self.mock_nextbus_response = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '  <vehicle id="1008" routeTag="E" dirTag="E____I_F00" lat="37.7747" lon="-122.39613" ' \
            'secsSinceReport="4" predictable="true" heading="219" speedKmHr="0"/>' \
            '  <vehicle id="1015" routeTag="E" dirTag="E____O_F00" lat="37.8076099" lon="-122.41738" ' \
            'secsSinceReport="81" predictable="true" heading="173" speedKmHr="0"/>' \
            '  <vehicle id="1007" routeTag="E" dirTag="E____I_F00" lat="37.79235" lon="-122.391" ' \
            'secsSinceReport="68" predictable="true" heading="328" speedKmHr="24"/>' \
            '  <lastTime time="1476314411287"/>' \
            '</body>'

        self.mock_nextbus_response_as_obj = {
            api.TAG_VEHICLES: [
                {
                    api.TAG_ID: "1008",
                    api.TAG_DIR_TAG: "E____I_F00",
                    api.TAG_LAT: "37.7747",
                    api.TAG_LON: "-122.39613",
                    api.TAG_SECS_SINCE_REPORT: "4",
                    api.TAG_PREDICTABLE: "true",
                    api.TAG_HEADING: "219",
                    api.TAG_SPEED_KM_HR: "0"
                },
                {
                    api.TAG_ID: "1015",
                    api.TAG_DIR_TAG: "E____O_F00",
                    api.TAG_LAT: "37.8076099",
                    api.TAG_LON: "-122.41738",
                    api.TAG_SECS_SINCE_REPORT: "81",
                    api.TAG_PREDICTABLE: "true",
                    api.TAG_HEADING: "173",
                    api.TAG_SPEED_KM_HR: "0"
                },
                {
                    api.TAG_ID: "1007",
                    api.TAG_DIR_TAG: "E____I_F00",
                    api.TAG_LAT: "37.79235",
                    api.TAG_LON: "-122.391",
                    api.TAG_SECS_SINCE_REPORT: "68",
                    api.TAG_PREDICTABLE: "true",
                    api.TAG_HEADING: "328",
                    api.TAG_SPEED_KM_HR: "24"
                }
            ],
            api.TAG_LAST_TIME: self.lastTime
        }

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisRepository, "store_route_vehicles")
    @mock.patch.object(RedisRepository, "get_route_vehicles")
    def test_schedule_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_item(agency_tag, route_tag, vehicles):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/vehicles?' +
                             api.QUERY_LAST_TIME + '=' + self.lastTime),
                method='GET'
            )

            mocked_repo_get.side_effect = get_item
            mocked_repo_store.side_effect = store_item
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.maxDiff = None
        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = self.mock_nextbus_response_as_obj

        headers = {
            "Accept": "application/xml"
        }

        mocked_rest_adapter.assert_called_once_with(
                query={'a': self.agency_tag,
                       'command': NextBusService.COMMAND_VEHICLE_LOCATIONS,
                       'r': self.route_tag,
                       't': self.lastTime},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_item = mocked_repo_store.call_args_list[0][0][2]
        self.assertDictEqual(actual_cached_item, self.mock_nextbus_response_as_obj)

        self.assertDictEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisRepository, "store_route_vehicles")
    @mock.patch.object(RedisRepository, "get_route_vehicles")
    def test_schedule_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            schedule = self.mock_nextbus_response_as_obj

            raise gen.Return(schedule)

        @gen.coroutine
        def store_item(agency_tag, route_tag, vehicles):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/vehicles?' +
                             api.QUERY_LAST_TIME + '=' + self.lastTime),
                method='GET'
            )

            mocked_repo_get.side_effect = get_item
            mocked_repo_store.side_effect = store_item
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = self.mock_nextbus_response_as_obj

        mocked_repo_get.assert_called_once()
        self.assertFalse(mocked_rest_adapter.called)
        self.assertFalse(mocked_repo_store.called)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)
