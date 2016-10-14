from tornado import gen

from pubtrans.common import breaker
from pubtrans.common import exceptions
from pubtrans.services.next_bus import NextBusService


class Service(object):
    def __init__(self, app_settings):
        self.support = app_settings.support
        self.breaker_set = app_settings.circuit_breaker_set
        self.repository = app_settings.repository

    @gen.coroutine
    def get_agencies(self):

        agencies = yield self.get_agencies_from_cache()

        if agencies is None:
            # Use service and cache result
            self.support.notify_debug('agencies not found in cache. Using service')

            try:
                with self.breaker_set.context('next_bus'):
                    nextbus_service = NextBusService(support=self.support)
                    agencies = yield nextbus_service.get_agencies()
            except breaker.CircuitOpenError:
                self.support.notify_debug('[Service] Call to service provider failed. Circuit is open')
                raise exceptions.ExternalProviderUnavailableTemporarily('NextBus')

            yield self.store_agencies_in_cache(agencies)

        raise gen.Return(agencies)

    @gen.coroutine
    def get_agencies_from_cache(self):

        try:
            agencies = yield self.repository.get_agencies()
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
            agencies = None

        raise gen.Return(agencies)

    @gen.coroutine
    def store_agencies_in_cache(self, agencies):

        try:
            yield self.repository.store_agencies(agencies)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format('Service', ex.message))
