"""
Tornado handler for route schedule resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import agency
from pubtrans.handlers import base_handler


class RouteScheduleHandlerV1(base_handler.BaseHandler):
    """
    Tornado handler class for route schedule resource
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

        agency_obj = agency.Agency(agency_tag, self.application_settings)

        schedule = yield agency_obj.get_route_schedule(agency_tag, route_tag)

        self.build_response(schedule)
