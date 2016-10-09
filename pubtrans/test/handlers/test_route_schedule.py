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
from pubtrans.repositories.redis_nextbus_repository import RedisNextBusRepository
from pubtrans.services.next_bus import NextBusService

app = application.make_app()


class TestRouteScheduleHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteScheduleHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'
        self.route_tag = 'E'

        self.mock_nextbus_response = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright San Francisco Muni 2016."> ' \
            '  <route tag="E" title="E-Embarcadero" scheduleClass="2016T_FALL" serviceClass="wkd" ' \
            'direction="Inbound">' \
            '    <header>' \
            '      <stop tag="5237">King St &amp; 2nd St</stop>' \
            '      <stop tag="5240">King St &amp; 4th St</stop>' \
            '    </header>' \
            '    <tr blockID="9201">' \
            '      <stop tag="5237" epochTime="-1">--</stop>' \
            '    </tr>' \
            '    <tr blockID="9202">' \
            '      <stop tag="5237" epochTime="-1">--</stop>' \
            '      <stop tag="7795" epochTime="32820000">09:07:00</stop>' \
            '    </tr>' \
            '  </route>' \
            '  <route tag="E" title="E-Embarcadero" scheduleClass="2016T_FALL" serviceClass="wkd" ' \
            'direction="Outbound">' \
            '    <header>' \
            '      <stop tag="5184">Jones St &amp; Beach St</stop>' \
            '    </header>' \
            '    <tr blockID="9201">' \
            '      <stop tag="5184" epochTime="-1">--</stop>' \
            '    </tr>' \
            '  </route>' \
            '</body>'

        self.mock_nextbus_response_as_obj = {
            api.TAG_SCHEDULE_CLASS: "2016T_FALL",
            api.TAG_SCHEDULE_ITEMS: [
                {
                    api.TAG_SERVICE_CLASS: "wkd",
                    api.TAG_DIRECTION: "Inbound",
                    api.TAG_HEADER_STOPS: [
                        {
                            api.TAG_TAG: "5237",
                            api.TAG_STOP_TITLE: "King St & 2nd St"
                        },
                        {
                            api.TAG_TAG: "5240",
                            api.TAG_STOP_TITLE: "King St & 4th St"

                        }
                    ],
                    api.TAG_TRS: [
                        {
                            api.TAG_BLOCK_ID: "9201",
                            api.TAG_STOPS: [
                                {
                                    api.TAG_TAG: "5237",
                                    api.TAG_EPOCH_TIME: "-1",
                                    api.TAG_TIME_DATA: "--"
                                }
                            ]
                        },
                        {
                            api.TAG_BLOCK_ID: "9202",
                            api.TAG_STOPS: [
                                {
                                    api.TAG_TAG: "5237",
                                    api.TAG_EPOCH_TIME: "-1",
                                    api.TAG_TIME_DATA: "--"
                                },
                                {
                                    api.TAG_TAG: "7795",
                                    api.TAG_EPOCH_TIME: "32820000",
                                    api.TAG_TIME_DATA: "09:07:00"
                                }
                            ]
                        }
                    ]
                },
                {
                    api.TAG_SERVICE_CLASS: "wkd",
                    api.TAG_DIRECTION: "Outbound",
                    api.TAG_HEADER_STOPS: [
                        {
                            api.TAG_TAG: "5184",
                            api.TAG_STOP_TITLE: "Jones St & Beach St"

                        }
                    ],
                    api.TAG_TRS: [
                        {
                            api.TAG_BLOCK_ID: "9201",
                            api.TAG_STOPS: [
                                {
                                    api.TAG_TAG: "5184",
                                    api.TAG_EPOCH_TIME: "-1",
                                    api.TAG_TIME_DATA: "--"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisNextBusRepository, "store_schedule")
    @mock.patch.object(RedisNextBusRepository, "get_schedule")
    def test_schedule_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_item(agency_tag, route_tag, schedule):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/schedule'),
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
                       'command': NextBusService.COMMAND_SCHEDULE,
                       'r': self.route_tag},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_item = mocked_repo_store.call_args_list[0][0][2]
        self.assertEqual(actual_cached_item[api.TAG_SCHEDULE_CLASS],
                         self.mock_nextbus_response_as_obj[api.TAG_SCHEDULE_CLASS])
        self.assertEqual(len(actual_cached_item[api.TAG_SCHEDULE_ITEMS]),
                         len(self.mock_nextbus_response_as_obj[api.TAG_SCHEDULE_ITEMS]))

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisNextBusRepository, "store_schedule")
    @mock.patch.object(RedisNextBusRepository, "get_schedule")
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
        def store_item(items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/schedule'),
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
