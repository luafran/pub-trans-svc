"""
Tornado handler for route messages resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import agency
from pubtrans.domain import api
from pubtrans.handlers import base_handler


class RoutePredictionsHandlerV1(base_handler.BaseHandler):
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

        stop_tag = self.get_query_argument(api.QUERY_STOP_TAG, None)
        if not stop_tag:
            error_response3 = exceptions.MissingArgumentValue('Missing argument {0}'.
                                                              format(api.QUERY_STOP_TAG))
            self.build_response(error_response3)
            return

        agency_obj = agency.Agency(agency_tag, self.application_settings)

        route_messages = yield agency_obj.get_route_predictions(agency_tag, route_tag, stop_tag)

        self.build_response(route_messages)
