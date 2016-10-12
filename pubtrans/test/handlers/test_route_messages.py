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


class TestRouteMessagesHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRouteMessagesHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'
        self.route_tag = 'E'

        self.mock_nextbus_response = \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '  <route tag="all">' \
            '    <message id="18419" sendToBuses="false" priority="Low">' \
            '      <text>We&apos;re on Twitter: @sfmta_muni</text>' \
            '    </message>' \
            '    <message id="20137" sendToBuses="false" priority="Low">' \
            '      <text>Sign up for email &amp; text service alerts at sfmta.com.</text>' \
            '    </message>' \
            '    <message id="21868" sendToBuses="false" priority="Low">' \
            '      <text>Seeing &quot;registering&quot;? The system is being upgraded to 3G.</text>' \
            '    </message>' \
            '  </route>' \
            '  <route tag="E">' \
            '    <message id="100" sendToBuses="false" priority="Medium">' \
            '      <text>Route message 1</text>' \
            '    </message>' \
            '    <message id="101" sendToBuses="true" priority="Low">' \
            '      <text>Route message 2</text>' \
            '    </message>' \
            '    <message id="102" sendToBuses="false" priority="Low">' \
            '      <text>Route message 3</text>' \
            '    </message>' \
            '  </route>' \
            '</body>'

        self.mock_nextbus_response_as_obj = {
            api.TAG_ALL_MESSAGES: [
                {
                    api.TAG_ID: "18419",
                    api.TAG_SEND_TO_BUSES: "false",
                    api.TAG_PRIORITY: "Low",
                    api.TAG_TEXT: "We're on Twitter: @sfmta_muni"
                },
                {
                    api.TAG_ID: "20137",
                    api.TAG_SEND_TO_BUSES: "false",
                    api.TAG_PRIORITY: "Low",
                    api.TAG_TEXT: "Sign up for email & text service alerts at sfmta.com."
                },
                {
                    api.TAG_ID: "21868",
                    api.TAG_SEND_TO_BUSES: "false",
                    api.TAG_PRIORITY: "Low",
                    api.TAG_TEXT: 'Seeing "registering"? The system is being upgraded to 3G.'
                }
            ],
            api.TAG_ROUTE_MESSAGES: [
                {
                    api.TAG_ID: "100",
                    api.TAG_SEND_TO_BUSES: "false",
                    api.TAG_PRIORITY: "Medium",
                    api.TAG_TEXT: "Route message 1"
                },
                {
                    api.TAG_ID: "101",
                    api.TAG_SEND_TO_BUSES: "true",
                    api.TAG_PRIORITY: "Low",
                    api.TAG_TEXT: "Route message 2"
                },
                {
                    api.TAG_ID: "102",
                    api.TAG_SEND_TO_BUSES: "false",
                    api.TAG_PRIORITY: "Low",
                    api.TAG_TEXT: "Route message 3"
                }
            ]
        }

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisRepository, "store_route_messages")
    @mock.patch.object(RedisRepository, "get_route_messages")
    def test_route_messages_not_in_cache(self, mocked_repo_get, mocked_repo_store):

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
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/messages'),
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
                       'command': NextBusService.COMMAND_MESSAGES,
                       'r': self.route_tag},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_item = mocked_repo_store.call_args_list[0][0][2]
        self.assertEqual(actual_cached_item, self.mock_nextbus_response_as_obj)
        self.assertEqual(len(actual_cached_item[api.TAG_ALL_MESSAGES]),
                         len(self.mock_nextbus_response_as_obj[api.TAG_ALL_MESSAGES]))

        self.maxDiff = None
        self.assertDictEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisRepository, "store_route_messages")
    @mock.patch.object(RedisRepository, "get_route_messages")
    def test_route_messages_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_item(agency_tag, route_tag):  # pylint: disable=unused-argument
            route_messages = self.mock_nextbus_response_as_obj

            raise gen.Return(route_messages)

        @gen.coroutine
        def store_item(items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes/' + self.route_tag + '/messages'),
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
