"""
Connector to NextBus Service
"""
from collections import OrderedDict
from tornado import gen

from pubtrans.common import constants
from pubtrans.common import exceptions
from pubtrans.config import settings
from pubtrans.decorators import retry_decorator
from pubtrans.domain import api
from pubtrans.services import base_service as base


class NextBusService(base.BaseService):  # pylint: disable=R0903
    """
    Connector to Next Bus Service
    """

    LOG_TAG = '[NextBus Service] %s'

    QUERY_COMMAND = 'command'
    QUERY_AGENCY = 'a'
    QUERY_ROUTE = 'r'

    COMMAND_AGENCY_LIST = 'agencyList'
    COMMAND_ROUTE_LIST = 'routeList'
    COMMAND_ROUTE_CONFIG = 'routeConfig'
    COMMAND_PREDICTIONS = 'predictions'

    ELEMENT_BODY = 'body'
    ELEMENT_AGENCY = 'agency'
    ELEMENT_ROUTE = 'route'
    ELEMENT_STOP = 'stop'
    ELEMENT_DIRECTION = 'direction'
    ELEMENT_PATH = 'path'
    ELEMENT_POINT = 'point'

    XML_ATTR_TAG = '@tag'
    XML_ATTR_TITLE = '@title'
    XML_ATTR_REGION_TITLE = '@regionTitle'
    XML_ATTR_SHORT_TITLE = '@shortTitle'
    XML_ATTR_LAT = '@lat'
    XML_ATTR_LON = '@lon'
    XML_ATTR_STOP_ID = '@stopId'

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
        Get all agencies
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
        agencies = self.build_agencies_list(validated_response)
        raise gen.Return(agencies)

    @gen.coroutine
    def get_routes(self, agency_tag, route_tag=None):
        """
        Get routes
        """
        if route_tag:
            route = yield self.get_route(agency_tag, route_tag)
            # This method should return a list
            routes = [route]
        else:
            routes = yield self.get_all_routes(agency_tag)

        raise gen.Return(routes)

    @gen.coroutine
    def get_all_routes(self, agency_tag):
        """
        Get all routes
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
        routes = self.build_routes_list(validated_response)
        raise gen.Return(routes)

    @gen.coroutine
    def get_route(self, agency_tag, route_tag):
        """
        Get single route
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
        routes = self.build_route(validated_response)
        raise gen.Return(routes)

    def build_agencies_list(self, validated_response):

        agencies_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_AGENCY)
        if not isinstance(agencies_xml, list):
            agencies_xml = [agencies_xml]

        agencies = []
        for agency_xml in agencies_xml:
            agency = OrderedDict([
                (api.TAG_TAG, agency_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, agency_xml.get(self.XML_ATTR_TITLE)),
                (api.TAG_REGION_TITILE, agency_xml.get(self.XML_ATTR_REGION_TITLE))
            ])
            agencies.append(agency)

        return agencies

    def build_routes_list(self, validated_response):

        routes_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ROUTE)
        if not isinstance(routes_xml, list):
            routes_xml = [routes_xml]

        routes = []
        for route_xml in routes_xml:
            item = OrderedDict([
                (api.TAG_TAG, route_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, route_xml.get(self.XML_ATTR_TITLE))
            ])
            short_title = route_xml.get(self.XML_ATTR_SHORT_TITLE)
            if short_title:
                item[api.TAG_SHORT_TITLE] = short_title
            routes.append(item)

        return routes

    def build_route(self, validated_response):

        route_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ROUTE)

        route = OrderedDict()

        route[api.TAG_TAG] = route_xml.get(self.XML_ATTR_TAG)
        route[api.TAG_TITLE] = route_xml.get(self.XML_ATTR_TITLE)
        route[api.TAG_COLOR] = route_xml.get('@color')
        route[api.TAG_OPPOSITE_COLOR] = route_xml.get('@oppositeColor')
        route[api.TAG_LAT_MIN] = route_xml.get('@latMin')
        route[api.TAG_LAT_MAX] = route_xml.get('@latMax')
        route[api.TAG_LON_MIN] = route_xml.get('@lonMin')
        route[api.TAG_LON_MAX] = route_xml.get('@lonMax')

        route[api.TAG_STOPS] = self.build_stops(route_xml)
        route[api.TAG_DIRECTIONS] = self.build_directions(route_xml)
        route[api.TAG_PATHS] = self.build_path(route_xml)

        return route

    def build_path(self, route_xml):
        # Add paths to route
        paths_xml = route_xml.get(self.ELEMENT_PATH)
        if not isinstance(paths_xml, list):
            paths_xml = [paths_xml]
        paths = []
        for path_xml in paths_xml:
            # Add points to path
            points = []
            points_xml = path_xml.get(self.ELEMENT_POINT)
            if not isinstance(points_xml, list):
                points_xml = [points_xml]
            for point_xml in points_xml:
                point = OrderedDict([
                    (api.TAG_LAT, point_xml.get('@lat')),
                    (api.TAG_LON, point_xml.get('@lon'))
                ])
                points.append(point)
            path = {api.TAG_POINTS: points}
            paths.append(path)
        return paths

    def build_directions(self, route_xml):
        # Add directions to route
        directions_xml = route_xml.get(self.ELEMENT_DIRECTION)
        if not isinstance(directions_xml, list):
            directions_xml = [directions_xml]
        directions = []
        for direction_xml in directions_xml:
            direction = OrderedDict([
                (api.TAG_TAG, direction_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, direction_xml.get(self.XML_ATTR_TITLE)),
                (api.TAG_NAME, direction_xml.get('@name')),
                (api.TAG_USE_FOR_UI, direction_xml.get('@useForUI'))
            ])
            # Add stops to directions
            stops_xml = direction_xml.get(self.ELEMENT_STOP)
            if not isinstance(stops_xml, list):
                stops_xml = [stops_xml]
            stops = []
            for stop_xml in stops_xml:
                stop = OrderedDict([
                    (api.TAG_TAG, stop_xml.get(self.XML_ATTR_TAG))
                ])
                stops.append(stop)
            direction[api.TAG_STOPS] = stops
            directions.append(direction)
        return directions

    def build_stops(self, route_xml):
        # Add stops to route
        stops_xml = route_xml.get(self.ELEMENT_STOP)
        if not isinstance(stops_xml, list):
            stops_xml = [stops_xml]
        stops = []
        for stop_xml in stops_xml:
            stop = OrderedDict([
                (api.TAG_TAG, stop_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, stop_xml.get(self.XML_ATTR_TITLE)),
                (api.TAG_LAT, stop_xml.get(self.XML_ATTR_LAT)),
                (api.TAG_LON, stop_xml.get(self.XML_ATTR_LON)),
                (api.TAG_STOP_ID, stop_xml.get(self.XML_ATTR_STOP_ID))
            ])
            stops.append(stop)
        return stops
