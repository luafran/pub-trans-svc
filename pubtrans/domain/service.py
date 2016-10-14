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
            self.support.notify_debug('[Service] agency {0} not found in cache. Using service'.
                                      format(agency_tag))
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
