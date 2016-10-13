"""
Connector to NextBus Service
"""
import re
import sys
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
    QUERY_LAST_TIME = 't'

    COMMAND_AGENCY_LIST = 'agencyList'
    COMMAND_ROUTE_LIST = 'routeList'
    COMMAND_ROUTE_CONFIG = 'routeConfig'
    COMMAND_PREDICTIONS = 'predictions'
    COMMAND_SCHEDULE = 'schedule'
    COMMAND_MESSAGES = 'messages'
    COMMAND_VEHICLE_LOCATIONS = 'vehicleLocations'

    ELEMENT_BODY = 'body'
    ELEMENT_AGENCY = 'agency'
    ELEMENT_ROUTE = 'route'
    ELEMENT_STOP = 'stop'
    ELEMENT_DIRECTION = 'direction'
    ELEMENT_PATH = 'path'
    ELEMENT_POINT = 'point'
    ELEMENT_HEADER = 'header'
    ELEMENT_TR = 'tr'
    ELEMENT_MESSAGE = 'message'
    ELEMENT_TEXT = 'text'
    ELEMENT_ROUTE_CONFIGURED_FOR_MESSAGE = 'routeConfiguredForMessage'
    ELEMENT_INTERVAL = 'interval'
    ELEMENT_VEHICLE = 'vehicle'
    ELEMENT_LAST_TIME = 'lastTime'
    ELEMENT_ERROR = 'Error'

    XML_ATTR_TAG = '@tag'
    XML_ATTR_TITLE = '@title'
    XML_ATTR_REGION_TITLE = '@regionTitle'
    XML_ATTR_SHORT_TITLE = '@shortTitle'
    XML_ATTR_LAT = '@lat'
    XML_ATTR_LON = '@lon'
    XML_ATTR_STOP_ID = '@stopId'
    XML_ATTR_SCHEDULE_CLASS = '@scheduleClass'
    XML_ATTR_SERVICE_CLASS = '@serviceClass'
    XML_ATTR_DIRECTION = '@direction'
    XML_ATTR_EPOCH_TIME = '@epochTime'
    XML_ATTR_BLOCK_ID = '@blockID'
    XML_ATTR_ID = '@id'
    XML_ATTR_SEND_TO_BUSES = '@sendToBuses'
    XML_ATTR_PRIORITY = '@priority'
    XML_ATTR_START_DAY = '@startDay'
    XML_ATTR_START_TIME = '@startTime'
    XML_ATTR_END_DAY = '@endDay'
    XML_ATTR_END_TIME = '@endTime'
    XML_ATTR_DIR_TAG = '@dirTag'
    XML_ATTR_SECS_SINCE_REPORT = '@secsSinceReport'
    XML_ATTR_PREDICTABLE = '@predictable'
    XML_ATTR_HEADING = '@heading'
    XML_ATTR_SPEED_KM_HR = '@speedKmHr'
    XML_ATTR_TIME = '@time'

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
        self.handle_error(validated_response)
        agencies = self.build_agencies_list(validated_response)
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
        self.handle_error(validated_response)
        routes = self.build_routes_list(validated_response)
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
        self.handle_error(validated_response)
        route = self.build_route(validated_response)
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
        self.handle_error(validated_response)
        route_schedule = self.build_schedule(validated_response)
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
        self.handle_error(validated_response)
        route_messages = self.build_route_messages(validated_response)
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
        self.handle_error(validated_response)
        route_messages = self.build_route_vehicles(validated_response)
        raise gen.Return(route_messages)

    def handle_error(self, validated_response):
        error = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ERROR)
        if error:
            text = error.get('#text')
            if 'Could not get route' in text or re.search('route r=.* is (not valid|invalid)', text):
                raise exceptions.NotFound(text)
            else:
                raise exceptions.BadRequest(text)

    def build_agencies_list(self, validated_response):

        agencies_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_AGENCY)
        if not isinstance(agencies_xml, list):
            agencies_xml = [] if agencies_xml is None else [agencies_xml]

        agencies = []
        for agency_xml in agencies_xml:
            agency = OrderedDict([
                (api.TAG_TAG, agency_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, agency_xml.get(self.XML_ATTR_TITLE)),
                (api.TAG_REGION_TITLE, agency_xml.get(self.XML_ATTR_REGION_TITLE))
            ])
            agencies.append(agency)

        return agencies

    def build_routes_list(self, validated_response):

        routes_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ROUTE)
        if not isinstance(routes_xml, list):
            routes_xml = [] if routes_xml is None else [routes_xml]

        routes = []
        for route_xml in routes_xml:
            route = OrderedDict([
                (api.TAG_TAG, route_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, route_xml.get(self.XML_ATTR_TITLE))
            ])
            short_title = route_xml.get(self.XML_ATTR_SHORT_TITLE)
            if short_title:
                route[api.TAG_SHORT_TITLE] = short_title
            routes.append(route)

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
            paths_xml = [] if paths_xml is None else [paths_xml]

        paths = []
        for path_xml in paths_xml:
            # Add points to path

            points_xml = path_xml.get(self.ELEMENT_POINT)
            if not isinstance(points_xml, list):
                points_xml = [] if points_xml is None else [points_xml]

            points = []
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
            directions_xml = [] if directions_xml is None else [directions_xml]

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
                stops_xml = [] if stops_xml is None else [stops_xml]

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

        stops_xml = route_xml.get(self.ELEMENT_STOP)
        if not isinstance(stops_xml, list):
            stops_xml = [] if stops_xml is None else [stops_xml]

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

    def build_schedule(self, validated_response):

        routes_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ROUTE)
        if not isinstance(routes_xml, list):
            routes_xml = [] if routes_xml is None else [routes_xml]

        schedule = OrderedDict()

        schedule[api.TAG_SCHEDULE_CLASS] = routes_xml[0].get(self.XML_ATTR_SCHEDULE_CLASS)

        schedule[api.TAG_SCHEDULE_ITEMS] = OrderedDict()
        for route_xml in routes_xml:

            schedule_item = self.build_schedule_item(route_xml)
            schedule_item_key = schedule_item[api.TAG_SERVICE_CLASS].lower() + ':' + \
                schedule_item[api.TAG_DIRECTION].lower()
            schedule[api.TAG_SCHEDULE_ITEMS][schedule_item_key] = schedule_item

        return schedule

    def build_schedule_rows(self, route_xml):

        trs_xml = route_xml.get(self.ELEMENT_TR)
        if not isinstance(trs_xml, list):
            trs_xml = [] if trs_xml is None else [trs_xml]

        trs_result = []
        for tr_xml in trs_xml:
            tr_result = OrderedDict([
                (api.TAG_BLOCK_ID, tr_xml.get(self.XML_ATTR_BLOCK_ID))
            ])

            stops_xml = tr_xml.get(self.ELEMENT_STOP)
            if not isinstance(stops_xml, list):
                stops_xml = [] if stops_xml is None else [stops_xml]

            stops = []
            for stop_xml in stops_xml:
                stop = OrderedDict([
                    (api.TAG_TAG, stop_xml.get(self.XML_ATTR_TAG)),
                    (api.TAG_EPOCH_TIME, stop_xml.get(self.XML_ATTR_EPOCH_TIME)),
                    (api.TAG_TIME_DATA, stop_xml.get('#text'))
                ])
                stops.append(stop)
            tr_result[api.TAG_STOPS] = stops

            trs_result.append(tr_result)

        return trs_result

    def build_schedule_item(self, route_xml):

        schedule_item = OrderedDict([
            (api.TAG_SERVICE_CLASS, route_xml.get(self.XML_ATTR_SERVICE_CLASS)),
            (api.TAG_DIRECTION, route_xml.get(self.XML_ATTR_DIRECTION))
        ])

        schedule_item[api.TAG_STOPS] = self.build_schedule_stops(route_xml)

        trs_xml = route_xml.get(self.ELEMENT_TR)
        if not isinstance(trs_xml, list):
            trs_xml = [] if trs_xml is None else [trs_xml]

        min_epoch = sys.maxint
        max_epoch = -1
        min_start_time_str = ''
        max_start_time_str = ''
        for tr_xml in trs_xml:

            stops_xml = tr_xml.get(self.ELEMENT_STOP)
            if not isinstance(stops_xml, list):
                stops_xml = [] if stops_xml is None else [stops_xml]

            for stop_xml in stops_xml:
                stop_tag = stop_xml.get(self.XML_ATTR_TAG)
                stop = OrderedDict()
                epoch_time = stop_xml.get(self.XML_ATTR_EPOCH_TIME)
                if epoch_time != '-1':
                    stop[api.TAG_EPOCH_TIME] = epoch_time
                    stop[api.TAG_TIME_DATA] = stop_xml.get('#text')
                    schedule_item[api.TAG_STOPS][stop_tag][api.TAG_SCHEDULED_ARRIVALS].append(stop)

                    epoch = int(stop.get(api.TAG_EPOCH_TIME))
                    if epoch > 0:
                        if epoch < min_epoch:
                            min_epoch = epoch
                            min_start_time_str = stop.get(api.TAG_TIME_DATA)
                        if epoch > max_epoch:
                            max_epoch = epoch
                            max_start_time_str = stop.get(api.TAG_TIME_DATA)

        schedule_item[api.TAG_SCHEDULE_START_TIME] = min_start_time_str
        schedule_item[api.TAG_SCHEDULE_END_TIME] = max_start_time_str

        return schedule_item

    def build_schedule_stops(self, route_xml):

        header_stops_xml = route_xml.get(self.ELEMENT_HEADER).get(self.ELEMENT_STOP)
        if not isinstance(header_stops_xml, list):
            header_stops_xml = [] if header_stops_xml is None else [header_stops_xml]

        header_stops = {}
        for header_stop_xml in header_stops_xml:
            header_stop = OrderedDict([
                (api.TAG_TAG, header_stop_xml.get(self.XML_ATTR_TAG)),
                (api.TAG_TITLE, header_stop_xml.get('#text')),
                (api.TAG_SCHEDULED_ARRIVALS, [])
            ])
            header_stops[header_stop[api.TAG_TAG]] = header_stop

        return header_stops

    def build_route_messages(self, validated_response):

        routes_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_ROUTE)
        if not isinstance(routes_xml, list):
            routes_xml = [] if routes_xml is None else [routes_xml]

        messages_all = []
        messages_route = []
        for route_xml in routes_xml:
            route_tag = route_xml.get(self.XML_ATTR_TAG)
            messages = messages_all if route_tag == 'all' else messages_route

            messages_xml = route_xml.get(self.ELEMENT_MESSAGE)
            for message_xml in messages_xml:

                message = self.build_message(message_xml, route_tag)

                messages.append(message)

        route_messages = OrderedDict()
        if messages_all:
            route_messages[api.TAG_ALL_MESSAGES] = messages_all
        if messages_route:
            route_messages[api.TAG_ROUTE_MESSAGES] = messages_route

        return route_messages

    def build_message(self, message_xml, route_tag):
        message = OrderedDict([
            (api.TAG_ID, message_xml.get(self.XML_ATTR_ID)),
            (api.TAG_SEND_TO_BUSES, message_xml.get(self.XML_ATTR_SEND_TO_BUSES)),
            (api.TAG_PRIORITY, message_xml.get(self.XML_ATTR_PRIORITY)),
            (api.TAG_TEXT, message_xml.get(self.ELEMENT_TEXT))
        ])
        if route_tag != 'all':
            message[api.TAG_STOPS] = []
            route_configured_xml = message_xml.get(self.ELEMENT_ROUTE_CONFIGURED_FOR_MESSAGE)
            stops_xml = route_configured_xml.get(self.ELEMENT_STOP) if route_configured_xml else []
            for stop_xml in stops_xml:
                stop = OrderedDict([
                    (api.TAG_TAG, stop_xml.get(self.XML_ATTR_TAG)),
                    (api.TAG_TITLE, stop_xml.get(self.XML_ATTR_TITLE))
                ])
                message[api.TAG_STOPS].append(stop)
            intervals_xml = message_xml.get(self.ELEMENT_INTERVAL)
            if intervals_xml:
                message[api.TAG_INTERVALS] = []
            for interval_xml in intervals_xml:
                interval = OrderedDict([
                    (api.TAG_START_DAY, interval_xml.get(self.XML_ATTR_START_DAY)),
                    (api.TAG_START_TIME, interval_xml.get(self.XML_ATTR_START_TIME)),
                    (api.TAG_END_DAY, interval_xml.get(self.XML_ATTR_END_DAY)),
                    (api.TAG_END_TIME, interval_xml.get(self.XML_ATTR_END_TIME))
                ])
                message[api.TAG_INTERVALS].append(interval)
        return message

    def build_route_vehicles(self, validated_response):

        route_vehicles = OrderedDict()
        route_vehicles[api.TAG_VEHICLES] = []

        vehicles_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_VEHICLE)
        if not isinstance(vehicles_xml, list):
            vehicles_xml = [] if vehicles_xml is None else [vehicles_xml]

        for vehicle_xml in vehicles_xml:
            vehicle = OrderedDict([
                (api.TAG_ID, vehicle_xml.get(self.XML_ATTR_ID)),
                (api.TAG_DIR_TAG, vehicle_xml.get(self.XML_ATTR_DIR_TAG)),
                (api.TAG_LAT, vehicle_xml.get(self.XML_ATTR_LAT)),
                (api.TAG_LON, vehicle_xml.get(self.XML_ATTR_LON)),
                (api.TAG_SECS_SINCE_REPORT, vehicle_xml.get(self.XML_ATTR_SECS_SINCE_REPORT)),
                (api.TAG_PREDICTABLE, vehicle_xml.get(self.XML_ATTR_PREDICTABLE)),
                (api.TAG_HEADING, vehicle_xml.get(self.XML_ATTR_HEADING)),
                (api.TAG_SPEED_KM_HR, vehicle_xml.get(self.XML_ATTR_SPEED_KM_HR))
            ])

            route_vehicles[api.TAG_VEHICLES].append(vehicle)

        route_vehicles[api.TAG_LAST_TIME] = validated_response.get(self.ELEMENT_BODY).\
            get(self.ELEMENT_LAST_TIME).get(self.XML_ATTR_TIME)

        return route_vehicles
