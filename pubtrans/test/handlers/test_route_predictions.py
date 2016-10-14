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


class TestRoutePredictionsHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRoutePredictionsHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'
        self.route_tag = 'E'
        self.stopTag = '4502'

        self.mock_nextbus_response = \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '<predictions agencyTitle="San Francisco Muni" routeTitle="E-Embarcadero" routeTag="E" ' \
            'stopTitle="The Embarcadero &amp; Bay St" stopTag="4502">' \
            '  <direction title="Outbound to Mission Bay">' \
            '    <prediction epochTime="1476394913877" seconds="361" minutes="6" isDeparture="false" ' \
            'affectedByLayover="true" dirTag="E____O_F00" vehicle="1006" block="9204" tripTag="7273070" />' \
            '    <prediction epochTime="1476395414877" seconds="862" minutes="14" isDeparture="false" ' \
            'affectedByLayover="true" dirTag="E____O_F00" vehicle="1015" block="9205" tripTag="7273071" />' \
            '    <prediction epochTime="1476397334877" seconds="2782" minutes="46" isDeparture="false" ' \
            'affectedByLayover="true" dirTag="E____O_F00" vehicle="1009" block="9202" tripTag="7273073" />' \
            '  </direction>' \
            '  <message text="We&apos;re on Twitter: @sfmta_muni" priority="Low"/>' \
            '  <message text="Sign up for email &amp; text service alerts at sfmta.com." priority="Low"/>' \
            '  <message text="Seeing &quot;registering&quot;? The system is being upgraded to 3G." ' \
            'priority="Low"/>' \
            '</predictions>' \
            '</body>'

        self.mock_nextbus_response_as_obj = {
            api.TAG_DIRECTIONS: [
                {
                    api.TAG_TITLE: "Outbound to Mission Bay",
                    api.TAG_PREDICTIONS: [
                        {
                            api.TAG_EPOCH_TIME: "1476394913877",
                            api.TAG_SECONDS: "361",
                            api.TAG_MINUTES: "6",
                            api.TAG_IS_DEPARTURE: "false",
                            api.TAG_AFFECTED_BY_LAYOVER: "true",
                            api.TAG_DIR_TAG: "E____O_F00",
                            api.TAG_VEHICLE: "1006",
                            api.TAG_BLOCK: "9204",
                            api.TAG_TRIP_TAG: "7273070"
                        },
                        {
                            api.TAG_EPOCH_TIME: "1476395414877",
                            api.TAG_SECONDS: "862",
                            api.TAG_MINUTES: "14",
                            api.TAG_IS_DEPARTURE: "false",
                            api.TAG_AFFECTED_BY_LAYOVER: "true",
                            api.TAG_DIR_TAG: "E____O_F00",
                            api.TAG_VEHICLE: "1015",
                            api.TAG_BLOCK: "9205",
                            api.TAG_TRIP_TAG: "7273071"
                        },
                        {
                            api.TAG_EPOCH_TIME: "1476397334877",
                            api.TAG_SECONDS: "2782",
                            api.TAG_MINUTES: "46",
                            api.TAG_IS_DEPARTURE: "false",
                            api.TAG_AFFECTED_BY_LAYOVER: "true",
                            api.TAG_DIR_TAG: "E____O_F00",
                            api.TAG_VEHICLE: "1009",
                            api.TAG_BLOCK: "9202",
                            api.TAG_TRIP_TAG: "7273073"
                        }
                    ]
                }
            ]
        }

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisRepository, "store_route_predictions")
    @mock.patch.object(RedisRepository, "get_route_predictions")
    def test_predictions_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag, stop_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_item(agency_tag, route_tag, stop_tag, predictions):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/predictions?' +
                             api.QUERY_STOP_TAG + '=' + self.stopTag),
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
                       'command': NextBusService.COMMAND_PREDICTIONS,
                       'r': self.route_tag,
                       's': self.stopTag},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_item = mocked_repo_store.call_args_list[0][0][3]
        self.assertDictEqual(actual_cached_item, self.mock_nextbus_response_as_obj)

        self.assertDictEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisRepository, "store_route_predictions")
    @mock.patch.object(RedisRepository, "get_route_predictions")
    def test_predictions_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag, stop_tag):  # pylint: disable=unused-argument
            schedule = self.mock_nextbus_response_as_obj

            raise gen.Return(schedule)

        @gen.coroutine
        def store_item(agency_tag, route_tag, stop_tag, predictions):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/predictions?' +
                             api.QUERY_STOP_TAG + '=' + self.stopTag),
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
