"""
Tornado handler for route messages resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import service as svc
from pubtrans.handlers import base_handler


class RouteMessagesHandlerV1(base_handler.BaseHandler):
    """
    Tornado handler class for route messages resource
    """

    @gen.coroutine
    def get(self, agency_tag, route_tag):  # pylint: disable=arguments-differ

        if not agency_tag:
            error_response = exceptions.MissingArgumentValue('Missing argument agency')
            self.build_response(error_response)
            return

        if not route_tag:
            error_response = exceptions.MissingArgumentValue('Missing argument route tag')
            self.build_response(error_response)
            return

        repository = self.application_settings.repository

        service = svc.Service(repository, self.support)

        route_messages = yield service.get_route_messages(agency_tag, route_tag)

        self.build_response(route_messages)
