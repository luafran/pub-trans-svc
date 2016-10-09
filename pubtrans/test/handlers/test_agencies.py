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


class TestAgenciesHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestAgenciesHandlerV1, self).setUp()

        self.mock_nextbus_response = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright agencies listed below and NextBus Inc 2016.">' \
            '  <agency tag="actransit" title="AC Transit" regionTitle="California-Northern"/>' \
            '  <agency tag="jhu-apl" title="APL" regionTitle="Maryland"/>' \
            '</body>'

        self.mock_nextbus_response_as_list = [
            {
                'tag': 'actransit',
                'title': 'AC Transit',
                'regionTitle': 'California-Northern'
            },
            {
                'tag': 'jhu-apl',
                'title': 'APL',
                'regionTitle': 'Maryland'
            }
        ]

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    @mock.patch.object(RedisNextBusRepository, "store_agencies")
    @mock.patch.object(RedisNextBusRepository, "get_agencies")
    def test_agencies_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_items():
            raise gen.Return(None)

        @gen.coroutine
        def store_items(items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/agencies'),
                method='GET'
            )

            mocked_repo_get.side_effect = get_items
            mocked_repo_store.side_effect = store_items
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = {
            api.TAG_AGENCIES: self.mock_nextbus_response_as_list
        }

        headers = {
            "Accept": "application/xml"
        }

        mocked_rest_adapter.assert_called_once_with(
                query={'command': NextBusService.COMMAND_AGENCY_LIST},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_items = mocked_repo_store.call_args_list[0][0][0]
        self.assertEquals(2, len(actual_cached_items))
        self.assertEquals(actual_cached_items, self.mock_nextbus_response_as_list)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisNextBusRepository, "store_agencies")
    @mock.patch.object(RedisNextBusRepository, "get_agencies")
    def test_agencies_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_items():
            agencies = self.mock_nextbus_response_as_list

            raise gen.Return(agencies)

        @gen.coroutine
        def store_items(items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/agencies'),
                method='GET'
            )

            mocked_repo_get.side_effect = get_items
            mocked_repo_store.side_effect = store_items
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = {
            api.TAG_AGENCIES: self.mock_nextbus_response_as_list
        }

        mocked_repo_get.assert_called_once()
        self.assertFalse(mocked_rest_adapter.called)
        self.assertFalse(mocked_repo_store.called)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)
