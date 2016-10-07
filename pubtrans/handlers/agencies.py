"""
Tornado handler for agencies resource
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.handlers import base_handler
from pubtrans.services.next_bus import NextBusService

TAG_AGENCIES = 'agencies'


class AgenciesHandlerV1(base_handler.BaseHandler):

    @gen.coroutine
    def get(self, agency_tag):  # pylint: disable=unused-argument
        # pylint: disable=arguments-differ

        nextbus_repository = self.application_settings.nextbus_repository

        try:
            # Try cache first
            agencies = yield nextbus_repository.get_agencies()
        except exceptions.DatabaseOperationError as ex:
            # We should work even if cache is not working
            self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                     format(self.handler_name, ex.message))
            agencies = None

        if agencies is None:
            # Use service
            nextbus_service = NextBusService()
            agencies = yield nextbus_service.get_all_agencies()
            try:
                yield nextbus_repository.store_agencies(agencies)
            except exceptions.DatabaseOperationError as ex:
                # We should work even if cache is not working
                self.support.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                                         format(self.handler_name, ex.message))

        response = {
            TAG_AGENCIES: agencies
        }

        self.build_response(response)
