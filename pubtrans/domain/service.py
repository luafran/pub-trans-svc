from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import api
from pubtrans.services.next_bus import NextBusService


class Service(object):
    def __init__(self, repository, support=None):
        self.repository = repository
        self.support = support

    @gen.coroutine
    def get_agencies(self):

        agencies = yield self.get_agencies_from_cache()

        if agencies is None:
            # Use service and cache result
            self.support.notify_debug('agencies not found in cache. Using service')
            nextbus_service = NextBusService(support=self.support)
            agencies = yield nextbus_service.get_agencies()

            yield self.store_agencies_in_cache(agencies)

        raise gen.Return(agencies)

    @gen.coroutine
    def get_agency(self, agency_tag):
        agencies = yield self.get_agencies_from_cache()

        if agencies is None:
            # Use service and cache result
            self.support.notify_debug('agency {0} not found in cache. Using service'.format(agency_tag))
            nextbus_service = NextBusService(support=self.support)
            agencies = yield nextbus_service.get_agencies()

            yield self.store_agencies_in_cache(agencies)

            # This is not nice but since we have just a couple of agencies we can improve it later
            agency = None
            for agency in agencies:
                if agency[api.TAG_TAG] == agency_tag:
                    break

        raise gen.Return(agency)

    @gen.coroutine
    def get_routes(self, agency_tag):

        routes = yield self.get_routes_from_cache(agency_tag)

        if routes is None:
            # Use service and cache result
            self.support.notify_debug('routes for {0} not found in cache. Using service'.format(agency_tag))
            nextbus_service = NextBusService(support=self.support)
            routes = yield nextbus_service.get_routes(agency_tag)

            yield self.store_routes_in_cache(agency_tag, routes)

        # for route in routes:
        #     route_schedule = yield self.get_route_schedule(agency_tag, route[api.TAG_TAG])

        raise gen.Return(routes)

    @gen.coroutine
    def get_route(self, agency_tag, route_tag, fields=None):

        route = yield self.get_route_from_cache(agency_tag, route_tag)

        if route is None:
            # Use service and cache result
            self.support.notify_debug('route {0}/{1} not found in cache. Using service'.
                                      format(agency_tag, route_tag))
            nextbus_service = NextBusService(support=self.support)
            route = yield nextbus_service.get_route(agency_tag, route_tag)

            yield self.store_route_in_cache(agency_tag, route_tag, route)

        filtered_route = {}
        if fields:
            for field in fields:
                filtered_route[field] = route.get(field)
            route = filtered_route

        raise gen.Return(route)

    @gen.coroutine
    def get_route_schedule(self, agency_tag, route_tag):

        schedule = yield self.get_schedule_from_cache(agency_tag, route_tag)

        if schedule is None:
            # Use service and cache result
            self.support.notify_debug('schedule for {0}/{1} not found in cache. Using service'.
                                      format(agency_tag, route_tag))
            nextbus_service = NextBusService(support=self.support)
            schedule = yield nextbus_service.get_schedule(agency_tag, route_tag)
            yield self.store_schedule_in_cache(agency_tag, route_tag, schedule)

        raise gen.Return(schedule)

    @gen.coroutine
    def get_agencies_from_cache(self):

        try:
            agencies = yield self.repository.get_agencies()
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            agencies = None

        raise gen.Return(agencies)

    @gen.coroutine
    def store_agencies_in_cache(self, agencies):

        try:
            yield self.repository.store_agencies(agencies)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))

    @gen.coroutine
    def get_routes_from_cache(self, agency_tag):

        try:
            routes = yield self.repository.get_routes(agency_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            routes = None

        raise gen.Return(routes)

    @gen.coroutine
    def get_route_from_cache(self, agency_tag, route_tag):

        try:
            route = yield self.repository.get_route(agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            route = None

        raise gen.Return(route)

    @gen.coroutine
    def store_routes_in_cache(self, agency_tag, routes):

        try:
            yield self.repository.store_routes(agency_tag, routes)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))

    @gen.coroutine
    def store_route_in_cache(self, agency_tag, route_tag, route):

        try:
            yield self.repository.store_route(agency_tag, route_tag, route)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))

    @gen.coroutine
    def get_schedule_from_cache(self, agency_tag, route_tag):

        try:
            routes = yield self.repository.get_schedule(agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            routes = None

        raise gen.Return(routes)

    @gen.coroutine
    def store_schedule_in_cache(self, agency_tag, route_tag, schedule):

        try:
            yield self.repository.store_schedule(agency_tag, route_tag, schedule)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
