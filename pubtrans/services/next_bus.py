"""
Connector to NextBus Service
"""
from tornado import gen

from pubtrans.common import constants
from pubtrans.common import exceptions
from pubtrans.config import settings
from pubtrans.decorators import retry_decorator
from pubtrans.services import base_service as base
from pubtrans.services import next_bus_xml


class NextBusService(base.BaseService):  # pylint: disable=R0903
    """
    Connector to Next Bus Service
    """

    LOG_TAG = '[NextBus Service] %s'

    QUERY_COMMAND = 'command'
    QUERY_AGENCY = 'a'
    QUERY_ROUTE = 'r'
    QUERY_LAST_TIME = 't'
    QUERY_STOP_TAG = 's'

    COMMAND_AGENCY_LIST = 'agencyList'
    COMMAND_ROUTE_LIST = 'routeList'
    COMMAND_ROUTE_CONFIG = 'routeConfig'
    COMMAND_PREDICTIONS = 'predictions'
    COMMAND_SCHEDULE = 'schedule'
    COMMAND_MESSAGES = 'messages'
    COMMAND_VEHICLE_LOCATIONS = 'vehicleLocations'

    def __init__(self, support=None):
        endpoint = settings.NEXTBUS_SERVICE_URL
        super(NextBusService, self).__init__(endpoint, support=support)

        self.headers = {
            constants.ACCEPT_HEADER: "application/xml"
        }

        self.timeout = settings.NEXTBUS_SERVICE_TIMEOUT

    @retry_decorator.retry(exceptions.ExternalProviderUnavailableTemporarily,
                           tries=settings.NEXTBUS_SERVICE_RETRIES,
                           delay=settings.NEXTBUS_SERVICE_RETRIES_DELAY,
                           backoff=settings.NEXTBUS_SERVICE_RETRIES_BACKOFF)
    @gen.coroutine
    def get_agencies(self):
        """
        Get all agencies using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_AGENCY_LIST
        }

        response_code, response_body =\
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        agencies = next_bus_xml.build_agencies_list(validated_response)
        raise gen.Return(agencies)

    @gen.coroutine
    def get_routes(self, agency_tag):
        """
        Get all routes using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_ROUTE_LIST,
            self.QUERY_AGENCY: agency_tag
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        routes = next_bus_xml.build_routes_list(validated_response)
        raise gen.Return(routes)

    @gen.coroutine
    def get_route(self, agency_tag, route_tag):
        """
        Get single route using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_ROUTE_CONFIG,
            self.QUERY_AGENCY: agency_tag,
            self.QUERY_ROUTE: route_tag
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        route = next_bus_xml.build_route(validated_response)
        raise gen.Return(route)

    @gen.coroutine
    def get_route_schedule(self, agency_tag, route_tag):
        """
        Get route schedule using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_SCHEDULE,
            self.QUERY_AGENCY: agency_tag,
            self.QUERY_ROUTE: route_tag
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        route_schedule = next_bus_xml.build_schedule(validated_response)
        raise gen.Return(route_schedule)

    @gen.coroutine
    def get_route_messages(self, agency_tag, route_tag):
        """
        Get route messages using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_MESSAGES,
            self.QUERY_AGENCY: agency_tag,
            self.QUERY_ROUTE: route_tag
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        route_messages = next_bus_xml.build_route_messages(validated_response)
        raise gen.Return(route_messages)

    @gen.coroutine
    def get_route_vehicles(self, agency_tag, route_tag, last_time):
        """
        Get route vehicles using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_VEHICLE_LOCATIONS,
            self.QUERY_AGENCY: agency_tag,
            self.QUERY_ROUTE: route_tag,
            self.QUERY_LAST_TIME: last_time
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        route_messages = next_bus_xml.build_route_vehicles(validated_response)
        raise gen.Return(route_messages)

    @gen.coroutine
    def get_route_predictions(self, agency_tag, route_tag, stop_tag):
        """
        Get route predictions using NextBus service
        """

        query = {
            self.QUERY_COMMAND: self.COMMAND_PREDICTIONS,
            self.QUERY_AGENCY: agency_tag,
            self.QUERY_ROUTE: route_tag,
            self.QUERY_STOP_TAG: stop_tag
        }

        response_code, response_body = \
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        next_bus_xml.handle_error(validated_response)
        route_messages = next_bus_xml.build_route_predictions(validated_response)
        raise gen.Return(route_messages)
