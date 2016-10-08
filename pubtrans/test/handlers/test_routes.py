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


class TestRoutesHandlerV1(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestRoutesHandlerV1, self).setUp()

        self.agency_tag = 'sf-muni'

        self.mock_nextbus_response = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '    <route tag="E" title="E-Embarcadero"/>' \
            '    <route tag="F" title="F-Market &amp; Wharves"/>' \
            '    <route tag="J" title="J-Church"/>' \
            '</body>'

        self.mock_nextbus_response_as_list = [
            {
                api.TAG_TAG: 'E',
                api.TAG_TITLE: 'E-Embarcadero'
            },
            {
                api.TAG_TAG: 'F',
                api.TAG_TITLE: 'F-Market & Wharves'
            },
            {
                api.TAG_TAG: 'J',
                api.TAG_TITLE: 'J-Church'
            }
        ]

        self.mock_nextbus_response_with_short_title = \
            '<?xml version="1.0" encoding="utf-8" ?>' \
            '<body copyright="All data copyright San Francisco Muni 2016.">' \
            '    <route tag="E" title="E-Embarcadero" shortTitle="s1"/>' \
            '    <route tag="F" title="F-Market &amp; Wharves" shortTitle="s2"/>' \
            '    <route tag="J" title="J-Church" shortTitle="s3"/>' \
            '</body>'

        self.mock_nextbus_response_with_short_title_as_list = [
            {
                api.TAG_TAG: 'E',
                api.TAG_TITLE: 'E-Embarcadero',
                api.TAG_SHORT_TITLE: 's1'
            },
            {
                api.TAG_TAG: 'F',
                api.TAG_TITLE: 'F-Market & Wharves',
                api.TAG_SHORT_TITLE: 's2'
            },
            {
                api.TAG_TAG: 'J',
                api.TAG_TITLE: 'J-Church',
                api.TAG_SHORT_TITLE: 's3'
            }
        ]

    def get_app(self):  # pylint: disable=unused-argument
        return app

    def get_new_ioloop(self):  # pylint: disable=unused-argument
        return ioloop.IOLoop.instance()

    def test_when_no_agency_should_return_400(self):
        request = HTTPRequest(
            self.get_url('/v1//routes'),
            method='GET'
        )

        self.http_client.fetch(request, self.stop)
        response = self.wait()

        self.assertEqual(response.code, 400)
        actual_response = json.loads(response.body)
        expected_response = {
            "context": "Missing argument agency",
            "developer_message": "No value provided for an argument with required value",
            "user_message": "No value provided for an argument with required value"
        }
        self.assertDictContainsSubset(expected_response, actual_response)

    @mock.patch.object(RedisNextBusRepository, "store_routes")
    @mock.patch.object(RedisNextBusRepository, "get_routes")
    def test_routes_not_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_items(agency_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_items(agency_tag, items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/'+self.agency_tag+'/routes'),
                method='GET'
            )

            mocked_repo_get.side_effect = get_items
            mocked_repo_store.side_effect = store_items
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = {
            api.TAG_ROUTES: self.mock_nextbus_response_as_list
        }

        headers = {
            "Accept": "application/xml"
        }

        mocked_rest_adapter.assert_called_once_with(
                query={'a': self.agency_tag, 'command': NextBusService.COMMAND_ROUTE_LIST},
                headers=headers,
                timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_items = mocked_repo_store.call_args_list[0][0][1]
        self.assertEquals(len(self.mock_nextbus_response_as_list), len(actual_cached_items))
        self.assertEquals(actual_cached_items, self.mock_nextbus_response_as_list)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisNextBusRepository, "store_routes")
    @mock.patch.object(RedisNextBusRepository, "get_routes")
    def test_routes_in_cache(self, mocked_repo_get, mocked_repo_store):

        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response))

        @gen.coroutine
        def get_items(agency_tag):  # pylint: disable=unused-argument
            agencies = self.mock_nextbus_response_as_list

            raise gen.Return(agencies)

        @gen.coroutine
        def store_items(agency_tag, items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/'+self.agency_tag+'/routes'),
                method='GET'
            )

            mocked_repo_get.side_effect = get_items
            mocked_repo_store.side_effect = store_items
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = {
            "routes": self.mock_nextbus_response_as_list
        }

        mocked_repo_get.assert_called_once()
        self.assertFalse(mocked_rest_adapter.called)
        self.assertFalse(mocked_repo_store.called)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)

    @mock.patch.object(RedisNextBusRepository, "store_routes")
    @mock.patch.object(RedisNextBusRepository, "get_routes")
    def test_routes_not_in_cache_with_short_titles(self, mocked_repo_get, mocked_repo_store):
        @gen.coroutine
        def get_success(path=None, body=None, query=None,
                        headers=None, timeout=None):  # pylint: disable=unused-argument

            raise gen.Return((200, self.mock_nextbus_response_with_short_title))

        @gen.coroutine
        def get_items(agency_tag):  # pylint: disable=unused-argument
            raise gen.Return(None)

        @gen.coroutine
        def store_items(agency_tag, items):  # pylint: disable=unused-argument
            raise gen.Return(None)

        with mock.patch.object(RestAdapter, 'get') as mocked_rest_adapter:
            mocked_rest_adapter.side_effect = get_success
            request = HTTPRequest(
                self.get_url('/v1/' + self.agency_tag + '/routes'),
                method='GET'
            )

            mocked_repo_get.side_effect = get_items
            mocked_repo_store.side_effect = store_items
            self.http_client.fetch(request, self.stop)
            response = self.wait()

        self.assertEqual(response.code, 200)
        actual_service_response = json.loads(response.body)

        expected_service_response = {
            api.TAG_ROUTES: self.mock_nextbus_response_with_short_title_as_list
        }

        headers = {
            "Accept": "application/xml"
        }

        mocked_rest_adapter.assert_called_once_with(
            query={'a': self.agency_tag, 'command': NextBusService.COMMAND_ROUTE_LIST},
            headers=headers,
            timeout=settings.NEXTBUS_SERVICE_TIMEOUT)

        mocked_repo_get.assert_called_once()
        actual_cached_items = mocked_repo_store.call_args_list[0][0][1]
        self.assertEquals(len(self.mock_nextbus_response_with_short_title_as_list), len(actual_cached_items))
        self.assertEquals(actual_cached_items, self.mock_nextbus_response_with_short_title_as_list)

        self.maxDiff = None
        self.assertEqual(expected_service_response, actual_service_response)
