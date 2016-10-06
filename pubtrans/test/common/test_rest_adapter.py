import mock

from tornado import httpclient
from tornado import testing
from tornado.httpclient import AsyncHTTPClient

from pubtrans.common import constants
from pubtrans.common import dictionaries
from pubtrans.common.context import Context
from pubtrans.common.rest_adapter import RestAdapter


class TestRestAdapter(testing.AsyncTestCase):

    def setUp(self):
        super(TestRestAdapter, self).setUp()

        self.endpoint = 'endpoint'
        self.path = '/path'
        self.url = self.endpoint + self.path

        self.request_id = '823123'
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.expected_headers = {
            constants.REQUEST_ID_HTTP_HEADER: self.request_id,
            constants.CONTENT_TYPE_HEADER: 'application/json'
        }

        self.query = {
            "key": "value"
        }
        self.expected_query = "?key=value"

    def _create_context(self):

        context_dict = {"headers": {constants.REQUEST_ID_HTTP_HEADER: self.request_id}}
        context = Context(dictionaries.DictAsObject(context_dict))
        return context

    @staticmethod
    def _create_request(*args, **kwargs):
        return httpclient.HTTPRequest(*args, **kwargs)

    @mock.patch.object(RestAdapter, "_create_request")
    def test_request_sends_request_id(self, mock_create_request):
        mock_create_request.return_value = httpclient.HTTPRequest("/tmp")
        rest_adapter = RestAdapter(self.endpoint, self._create_context(), None)
        rest_adapter.get('/a_get')

        request_headers = mock_create_request.call_args_list[0][1]['headers']
        self.assertEquals(request_headers[constants.REQUEST_ID_HTTP_HEADER], "823123")

    @mock.patch.object(AsyncHTTPClient, "fetch")
    def test_post(self, mock_fetch):

        rest_adapter = RestAdapter(self.endpoint, self._create_context(), None)
        body = '{"foo": "bar"}'
        rest_adapter.post(self.path, headers=self.headers, body=body)

        mock_fetch.assert_called_once()
        actual_request = mock_fetch.call_args_list[0][0][0]
        self.assertEquals(actual_request.method, 'POST')
        self.assertEquals(actual_request.url, self.url)
        self.assertEquals(actual_request.headers, self.expected_headers)
        self.assertEquals(actual_request.body, body)

    @mock.patch.object(AsyncHTTPClient, "fetch")
    def test_get(self, mock_fetch):
        rest_adapter = RestAdapter(self.endpoint, self._create_context(), None)
        rest_adapter.get(self.path, query=self.query)

        mock_fetch.assert_called_once()
        actual_request = mock_fetch.call_args_list[0][0][0]
        self.assertEquals(actual_request.method, 'GET')
        self.assertEquals(actual_request.url, self.url+self.expected_query)

    @mock.patch.object(AsyncHTTPClient, "fetch")
    def test_put(self, mock_fetch):
        rest_adapter = RestAdapter(self.endpoint, self._create_context(), None)
        body = '{"foo": "bar"}'
        rest_adapter.put(self.path, query=self.query, headers=self.headers, body=body)

        mock_fetch.assert_called_once()
        actual_request = mock_fetch.call_args_list[0][0][0]

        self.assertEquals(actual_request.method, 'PUT')
        self.assertEquals(actual_request.url, self.url + self.expected_query)
        self.assertEquals(actual_request.headers, self.expected_headers)
        self.assertEquals(actual_request.body, body)

    @mock.patch.object(AsyncHTTPClient, "fetch")
    def test_delete(self, mock_fetch):
        rest_adapter = RestAdapter(self.endpoint, self._create_context(), None)
        rest_adapter.delete(self.path, query=self.query)

        mock_fetch.assert_called_once()
        actual_request = mock_fetch.call_args_list[0][0][0]
        self.assertEquals(actual_request.method, 'DELETE')
        self.assertEquals(actual_request.url, self.url + self.expected_query)
