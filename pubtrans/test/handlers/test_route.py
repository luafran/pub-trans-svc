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


class TestRouteHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'
        self.route_tag = 'E'

        self.mock_nextbus_response = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '<route tag="E" title="E-Embarcadero" color="667744" oppositeColor="ffffff" ' \
            'latMin="37.7762699" latMax="37.8085899" lonMin="-122.41732" lonMax="-122.38798">' \
            '<stop tag="5184" title="Jones St &amp; Beach St" lat="37.8071299" lon="-122.41732" ' \
            'stopId="15184"/>' \
            '<stop tag="3095" title="Beach St &amp; Stockton St" lat="37.8078399" lon="-122.41081" ' \
            'stopId="13095"/>' \
            '<stop tag="7283" title="The Embarcadero &amp; Ferry Building" lat="37.7948299" ' \
            'lon="-122.39377" stopId="17283"/>' \
            '<direction tag="E____O_F00" title="Outbound to Mission Bay" name="Outbound" useForUI="true">' \
            '  <stop tag="5184" />' \
            '  <stop tag="3095" />' \
            '  <stop tag="7283" />' \
            '</direction>' \
            '<direction tag="E____I_F00" title="Inbound to Fisherman&apos;s Wharf" name="Inbound" ' \
            'useForUI="true">' \
            '  <stop tag="5240" />' \
            '  <stop tag="5237" />' \
            '  <stop tag="7145" />' \
            '</direction>' \
            '<path>' \
            '  <point lat="37.80835" lon="-122.41029"/>' \
            '  <point lat="37.80833" lon="-122.4105"/>' \
            '  <point lat="37.80784" lon="-122.41081"/>' \
            '</path>' \
            '<path>' \
            '  <point lat="37.77962" lon="-122.38982"/>' \
            '</path>' \
            '<path>' \
            '  <point lat="37.80835" lon="-122.41029"/>' \
            '  <point lat="37.80862" lon="-122.4124"/>' \
            '</path>' \
            '</route>' \
            '</body>'

        self.mock_nextbus_response_as_obj = {
            api.TAG_TAG: 'E',
            api.TAG_TITLE: 'E-Embarcadero',
            api.TAG_COLOR: '667744',
            api.TAG_OPPOSITE_COLOR: 'ffffff',
            api.TAG_LAT_MIN: '37.7762699',
            api.TAG_LAT_MAX: "37.8085899",
            api.TAG_LON_MIN: "-122.41732",
            api.TAG_LON_MAX: "-122.38798",
            api.TAG_STOPS: [
                {
                    api.TAG_TAG: "5184",
                    api.TAG_TITLE: "Jones St &amp; Beach St",
                    api.TAG_LAT: "37.8071299",
                    api.TAG_LON: "-122.41732",
                    api.TAG_STOP_ID: "15184"
                },
                {
                    api.TAG_TAG: "3095",
                    api.TAG_TITLE: "Beach St &amp; Stockton St",
                    api.TAG_LAT: "37.8078399",
                    api.TAG_LON: "-122.41081",
                    api.TAG_STOP_ID: "13095"
                },
                {
                    api.TAG_TAG: "7283",
                    api.TAG_TITLE: "The Embarcadero & Ferry Building",
                    api.TAG_LAT: "37.7948299",
                    api.TAG_LON: "-122.39377",
                    api.TAG_STOP_ID: "17283"
                }
            ],
            api.TAG_DIRECTIONS: [
                {
                    api.TAG_TAG: "E____O_F00",
                    api.TAG_TITLE: "Outbound to Mission Bay",
                    api.TAG_NAME: "Outbound",
                    api.TAG_USE_FOR_UI: "true",
                    api.TAG_STOPS: [
                        {
                            api.TAG_TAG: "5184"
                        },
                        {
                            api.TAG_TAG: "3095"
                        },
                        {
                            api.TAG_TAG: "7283"
                        }
                    ]
                },
                {
                    api.TAG_TAG: "E____I_F00",
                    api.TAG_TITLE: "Inbound to Fisherman's Wharf",
                    api.TAG_NAME: "Inbound",
                    api.TAG_USE_FOR_UI: "true",
                    api.TAG_STOPS: [
                        {
                            api.TAG_TAG: "5240"
                        },
                        {
                            api.TAG_TAG: "5237"
                        },
                        {
                            api.TAG_TAG: "7145"
                        }
                    ]
                }
            ],
            api.TAG_PATHS: [
                {
                    api.TAG_POINTS: [
                        {
                            api.TAG_LAT: "37.80835",
                            api.TAG_LON: "-122.41029"
                        },
                        {
                            api.TAG_LAT: "37.80833",
                            api.TAG_LON: "-122.4105"
                        },
                        {
                            api.TAG_LAT: "37.80784",
                            api.TAG_LON: "-122.41081"
                        }
                    ]
                },
                {
                    api.TAG_POINTS: [
                        {
                            api.TAG_LAT: "37.77962",
                            api.TAG_LON: "-122.38982"
                        }
                    ]
                },
                {
                    api.TAG_POINTS: [
                        {
                            api.TAG_LAT: "37.80835",
                            api.TAG_LON: "-122.41029"
                        },
                        {
                            api.TAG_LAT: "37.80862",
                            api.TAG_LON: "-122.4124"
                        }
                    ]
                }
            ]
        }

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisRepository, "store_route")
    @mock.patch.object(RedisRepository, "get_route")
    def test_route_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_item(agency_tag, route_tag, route):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/'+self.agency_tag+'/routes/'+self.route_tag),
                method='GET'
            )

            mocked_repo_get.side_effect = get_item
            mocked_repo_store.side_effect = store_item
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = self.mock_nextbus_response_as_obj

        headers = {
            "Accept": "application/xml"
        }

        mocked_rest_adapter.assert_called_once_with(
                query={'a': self.agency_tag,
                       'command': NextBusService.COMMAND_ROUTE_CONFIG,
                       'r': self.route_tag},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_item = mocked_repo_store.call_args_list[0][0][2]
        self.assertEqual(actual_cached_item[api.TAG_TAG],
                         self.mock_nextbus_response_as_obj[api.TAG_TAG])

        self.maxDiff = None
        self.assertEqual(actual_service_response[api.TAG_DIRECTIONS],
                         expected_service_response[api.TAG_DIRECTIONS])

    @mock.patch.object(RedisRepository, "store_route")
    @mock.patch.object(RedisRepository, "get_route")
    def test_route_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            route = self.mock_nextbus_response_as_obj

            raise gen.Return(route)

        @gen.coroutine
        def store_item(agency_tag, route_tag, route):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag),
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
