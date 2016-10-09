"""
Tornado handler for agencies resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.domain import api
from pubtrans.handlers import base_handler
from pubtrans.services.next_bus import NextBusService


class AgenciesHandlerV1(base_handler.BaseHandler):

    @gen.coroutine
    def get(self):
        # pylint: disable=arguments-differ

        agencies = yield self.get_agencies_from_cache()

        if agencies is None:
            # Use service
            nextbus_service = NextBusService(support=self.support)
            agencies = yield nextbus_service.get_agencies()

            yield self.store_agencies_in_cache(agencies)

        response = {
            api.TAG_AGENCIES: agencies
        }

        self.build_response(response)

    @gen.coroutine
    def get_agencies_from_cache(self):

        nextbus_repository = self.application_settings.nextbus_repository

        try:
            agencies = yield nextbus_repository.get_agencies()
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            agencies = None

        raise gen.Return(agencies)

    @gen.coroutine
    def store_agencies_in_cache(self, agencies):
        nextbus_repository = self.application_settings.nextbus_repository

        try:
            yield nextbus_repository.store_agencies(agencies)
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
