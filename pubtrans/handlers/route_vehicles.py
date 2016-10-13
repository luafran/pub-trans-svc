"""
Tornado handler for route messages resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import api
from pubtrans.domain import service as svc
from pubtrans.handlers import base_handler


class RouteVehiclesHandlerV1(base_handler.BaseHandler):
    """
    Tornado handler class for route messages resource
    """

    @gen.coroutine
    def get(self, agency_tag, route_tag):  # pylint: disable=arguments-differ

        if not agency_tag:
            error_response1 = exceptions.MissingArgumentValue('Missing argument agency')
            self.build_response(error_response1)
            return

        if not route_tag:
            error_response2 = exceptions.MissingArgumentValue('Missing argument route tag')
            self.build_response(error_response2)
            return

        last_time = self.get_query_argument(api.QUERY_LAST_TIME, None)
        if not last_time:
            error_response3 = exceptions.MissingArgumentValue('Missing argument {0}'.
                                                              format(api.QUERY_LAST_TIME))
            self.build_response(error_response3)
            return

        repository = self.application_settings.repository

        service = svc.Service(repository, self.support)

        route_messages = yield service.get_route_vehicles(agency_tag, route_tag, last_time)

        self.build_response(route_messages)
