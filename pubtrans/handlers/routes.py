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
            return

        criteria = {}
        if route_tag:
            criteria[api.CRITERIA_ROUTE_TAG] = route_tag
        not_running_at = self.get_query_argument(api.QUERY_NOT_RUNNING_AT, None)
        if not_running_at:
            if len(not_running_at) == 1:
                not_running_at = '0{0}:00:00'.format(not_running_at)
            elif len(not_running_at) == 2:
                not_running_at = '{0}:00:00'.format(not_running_at)
            elif len(not_running_at) == 4:
                not_running_at = '0{0}:00'.format(not_running_at)
            elif len(not_running_at) == 5:
                not_running_at = '{0}:00'.format(not_running_at)
            elif len(not_running_at) == 8:
                pass
            else:
                error_response2 = exceptions.InvalidArgumentValue('Invalid value {0} for {1} argument'
                                                                  .format(not_running_at,
                                                                          api.QUERY_NOT_RUNNING_AT))
                self.build_response(error_response2)
                return

            criteria[api.CRITERIA_NOT_RUNNING_AT] = not_running_at

        fields = self.get_query_argument(api.QUERY_FIELDS, None)
        fields = fields.split(',') if fields else []

        repository = self.application_settings.repository

        service = svc.Service(repository, self.support)

        if route_tag:
            route = yield service.get_route(agency_tag, route_tag, fields)
            self.build_response(route)
        else:
            routes = yield service.get_routes(agency_tag, criteria)
            response = {
                api.TAG_ROUTES: routes
            }

            self.build_response(response)
