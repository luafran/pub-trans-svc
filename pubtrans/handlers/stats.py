"""
Tornado handler for stats resource
"""
import tornado.gen

from pubtrans.domain import api
from pubtrans.handlers.base_handler import BaseHandler


class StatsHandlerV1(BaseHandler):
    """
    Tornado handler class for stats resource
    """

    @tornado.gen.coroutine
    def get(self, stat_name):  # pylint: disable=arguments-differ
        """
        /stats GET handler
        """
        response = {}

        if stat_name in [api.STAT_RESOURCE_URI_COUNT, '']:
            uri_count = self.support.get_uri_count()
            response[api.TAG_URI_COUNT] = uri_count

        if stat_name in [api.STAT_RESOURCE_SLOW_REQUESTS, '']:
            slow_limit = self.get_query_argument(api.QUERY_SLOW_LIMIT, None)
            slow_requests = self.support.get_slow_requests(slow_limit)
            response[api.TAG_SLOW_REQUESTS] = slow_requests

        self.build_response(response)
