"""
Tornado handler for agencies resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.handlers import base_handler
from pubtrans.services.next_bus import NextBusService


class RouteScheduleHandlerV1(base_handler.BaseHandler):

    @gen.coroutine
    def get(self, agency_tag, route_tag):  # pylint: disable=arguments-differ

        if not agency_tag:
            error_response = exceptions.MissingArgumentValue('Missing argument agency')
            self.build_response(error_response)

        if not route_tag:
            error_response = exceptions.MissingArgumentValue('Missing argument route tag')
            self.build_response(error_response)

        schedule = yield self.get_schedule_from_cache(agency_tag, route_tag)
        if schedule is None:
            # Use service and cache result
            nextbus_service = NextBusService(support=self.support)
            schedule = yield nextbus_service.get_schedule(agency_tag, route_tag)
            yield self.store_schedule_in_cache(agency_tag, route_tag, schedule)

        self.build_response(schedule)

    @gen.coroutine
    def get_schedule_from_cache(self, agency_tag, route_tag):

        nextbus_repository = self.application_settings.nextbus_repository

        try:
            # Try cache first
            if route_tag:
                routes = yield nextbus_repository.get_schedule(agency_tag, route_tag)
            else:
                routes = yield nextbus_repository.get_routes(agency_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            routes = None

        raise gen.Return(routes)

    @gen.coroutine
    def store_schedule_in_cache(self, agency_tag, route_tag, schedule):

        nextbus_repository = self.application_settings.nextbus_repository

        try:
            if route_tag:
                yield nextbus_repository.store_schedule(agency_tag, route_tag, schedule)
            else:
                yield nextbus_repository.store_routes(agency_tag, schedule)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
