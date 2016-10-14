import datetime

from tornado import gen

from pubtrans.common import breaker
from pubtrans.common import exceptions
from pubtrans.domain import api
from pubtrans.services.next_bus import NextBusService


class Agency(object):

    def __init__(self, agency_tag, app_settings):
        self.agency_tag = agency_tag
        self.support = app_settings.support
        self.breaker_set = app_settings.circuit_breaker_set
        self.repository = app_settings.repository

    @gen.coroutine
    def get_routes(self, criteria):

        routes = yield self.get_routes_from_cache()

        if routes is None:
            # Use service and cache result
            self.support.notify_debug('[Agency] routes for {0} not found in cache. Using service'.
                                      format(self.agency_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    routes = yield nextbus_service.get_routes(self.agency_tag)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_routes_in_cache(routes)

        not_running_at = criteria.get(api.CRITERIA_NOT_RUNNING_AT)

        if not_running_at:
            routes = yield self.get_routes_not_running_at(routes, not_running_at)

        raise gen.Return(routes)

    @gen.coroutine
    def get_route(self, route_tag, fields=None):

        route = yield self.get_route_from_cache(route_tag)

        if route is None:
            # Use service and cache result
            self.support.notify_debug('[Agency] route {0}/{1} not found in cache. Using service'.
                                      format(self.agency_tag, route_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    route = yield nextbus_service.get_route(self.agency_tag, route_tag)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_route_in_cache(route_tag, route)

        filtered_route = {}
        if fields:
            for field in fields:
                filtered_route[field] = route.get(field)
            route = filtered_route

        raise gen.Return(route)

    @gen.coroutine
    def get_routes_not_running_at(self, routes, not_running_at):
        service_class = ['sun', 'sat', 'wkd', 'wkd', 'wkd', 'wkd', 'wkd']
        now_weekday = datetime.datetime.now().strftime("%w")
        schedule_item_key = service_class[int(now_weekday)] + ':inbound'
        self.support.notify_debug('[Service] not_running_at: {0}'.format(not_running_at))
        self.support.notify_debug('[Service] now_weekday: {0}'.format(now_weekday))
        self.support.notify_debug('[Service] schedule_item_key: {0}'.format(schedule_item_key))

        filtered_routes = []
        for route in routes:
            route_schedule = yield self.get_route_schedule(self.agency_tag, route[api.TAG_TAG])
            schedule_item = route_schedule.get(api.TAG_SCHEDULE_ITEMS).get(schedule_item_key)
            if schedule_item is None or \
                    ((not_running_at < schedule_item.get(api.TAG_SCHEDULE_START_TIME)) and
                     (not_running_at > schedule_item.get(api.TAG_SCHEDULE_END_TIME))):
                filtered_routes.append(route)

        raise gen.Return(filtered_routes)

    @gen.coroutine
    def get_route_schedule(self, agency_tag, route_tag):

        schedule = yield self.get_route_schedule_from_cache(agency_tag, route_tag)

        if schedule is None:
            # Use service and cache result
            self.support.notify_debug('schedule for route {0}/{1} not found in cache. Using service'.
                                      format(agency_tag, route_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    schedule = yield nextbus_service.get_route_schedule(agency_tag, route_tag)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_route_schedule_in_cache(agency_tag, route_tag, schedule)

        raise gen.Return(schedule)

    @gen.coroutine
    def get_route_predictions(self, agency_tag, route_tag, stop_tag):

        predictions = yield self.get_predictions_from_cache(agency_tag, route_tag, stop_tag)

        if predictions is None:
            # Use service and cache result
            self.support.notify_debug('predictions for route {0}/{1} and stop {2} not found in cache. '
                                      'Using service'.format(agency_tag, route_tag, stop_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    predictions = yield nextbus_service.get_route_predictions(agency_tag, route_tag, stop_tag)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_predictions_in_cache(agency_tag, route_tag, stop_tag, predictions)

        raise gen.Return(predictions)

    @gen.coroutine
    def get_route_messages(self, agency_tag, route_tag):

        messages = yield self.get_route_messages_from_cache(agency_tag, route_tag)

        if messages is None:
            # Use service and cache result
            self.support.notify_debug('messages for route {0}/{1} not found in cache. Using service'.
                                      format(agency_tag, route_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    messages = yield nextbus_service.get_route_messages(agency_tag, route_tag)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_route_messages_in_cache(agency_tag, route_tag, messages)

        raise gen.Return(messages)

    @gen.coroutine
    def get_route_vehicles(self, agency_tag, route_tag, last_time):

        vehicles = yield self.get_route_vehicles_from_cache(agency_tag, route_tag)

        if vehicles is None:
            # Use service and cache result
            self.support.notify_debug('vehicles for route {0}/{1} not found in cache. Using service'.
                                      format(agency_tag, route_tag))
            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    vehicles = yield nextbus_service.get_route_vehicles(agency_tag, route_tag, last_time)
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Agency] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_route_vehicles_in_cache(agency_tag, route_tag, vehicles)

        raise gen.Return(vehicles)

    @gen.coroutine
    def get_routes_from_cache(self):

        try:
            routes = yield self.repository.get_routes(self.agency_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Agency', ex.message))
            routes = None

        raise gen.Return(routes)

    @gen.coroutine
    def get_route_from_cache(self, route_tag):

        try:
            route = yield self.repository.get_route(self.agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Agency', ex.message))
            route = None

        raise gen.Return(route)

    @gen.coroutine
    def store_routes_in_cache(self, routes):

        try:
            yield self.repository.store_routes(self.agency_tag, routes)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Agency', ex.message))

    @gen.coroutine
    def store_route_in_cache(self, route_tag, route):

        try:
            yield self.repository.store_route(self.agency_tag, route_tag, route)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Agency', ex.message))

    @gen.coroutine
    def get_route_schedule_from_cache(self, agency_tag, route_tag):

        try:
            routes = yield self.repository.get_route_schedule(agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
            routes = None

        raise gen.Return(routes)

    @gen.coroutine
    def store_route_schedule_in_cache(self, agency_tag, route_tag, schedule):

        try:
            yield self.repository.store_route_schedule(agency_tag, route_tag, schedule)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))

    @gen.coroutine
    def get_route_messages_from_cache(self, agency_tag, route_tag):

        try:
            messages = yield self.repository.get_route_messages(agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
            messages = None

        raise gen.Return(messages)

    @gen.coroutine
    def store_route_messages_in_cache(self, agency_tag, route_tag, messages):

        try:
            yield self.repository.store_route_messages(agency_tag, route_tag, messages)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))

    @gen.coroutine
    def get_route_vehicles_from_cache(self, agency_tag, route_tag):

        try:
            vehicles = yield self.repository.get_route_vehicles(agency_tag, route_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
            vehicles = None

        raise gen.Return(vehicles)

    @gen.coroutine
    def store_route_vehicles_in_cache(self, agency_tag, route_tag, vehicles):

        try:
            yield self.repository.store_route_vehicles(agency_tag, route_tag, vehicles)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))

    @gen.coroutine
    def get_predictions_from_cache(self, agency_tag, route_tag, stop_tag):

        try:
            predictions = yield self.repository.get_route_predictions(agency_tag, route_tag, stop_tag)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
            predictions = None

        raise gen.Return(predictions)

    @gen.coroutine
    def store_predictions_in_cache(self, agency_tag, route_tag, stop_tag, predictions):

        try:
            yield self.repository.store_route_predictions(agency_tag, route_tag, stop_tag, predictions)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
