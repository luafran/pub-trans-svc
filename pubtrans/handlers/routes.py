"""
Tornado handler for agencies resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import api
from pubtrans.domain import service as svc
from pubtrans.handlers import base_handler


class RoutesHandlerV1(base_handler.BaseHandler):

    @gen.coroutine
    def get(self, agency_tag, route_tag):  # pylint: disable=arguments-differ

        if not agency_tag:
            error_response = exceptions.MissingArgumentValue('Missing argument agency')
            self.build_response(error_response)

        fields = self.get_query_argument(api.QUERY_FIELDS, None)
        fields = fields.split(',') if fields else []

        repository = self.application_settings.repository

        service = svc.Service(repository, self.support)

        if route_tag:
            route = yield service.get_route(agency_tag, route_tag, fields)
            self.build_response(route)
        else:
            routes = yield service.get_routes(agency_tag)
            response = {
                api.TAG_ROUTES: routes
            }

            self.build_response(response)
