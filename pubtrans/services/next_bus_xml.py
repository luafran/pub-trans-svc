import re
import sys
from collections import OrderedDict

from pubtrans.common import exceptions
from pubtrans.domain import api

ELEMENT_BODY = 'body'
ELEMENT_AGENCY = 'agency'
ELEMENT_ROUTE = 'route'
ELEMENT_STOP = 'stop'
ELEMENT_DIRECTION = 'direction'
ELEMENT_DIRECTIONS = 'directions'
ELEMENT_PREDICTION = 'prediction'
ELEMENT_PREDICTIONS = 'predictions'
ELEMENT_PATH = 'path'
ELEMENT_POINT = 'point'
ELEMENT_HEADER = 'header'
ELEMENT_TR = 'tr'
ELEMENT_MESSAGE = 'message'
ELEMENT_TEXT = 'text'
ELEMENT_ROUTE_CONF_FOR_MSG = 'routeConfiguredForMessage'
ELEMENT_INTERVAL = 'interval'
ELEMENT_VEHICLE = 'vehicle'
ELEMENT_LAST_TIME = 'lastTime'
ELEMENT_ERROR = 'Error'

ATTR_TAG = '@tag'
ATTR_TITLE = '@title'
ATTR_REGION_TITLE = '@regionTitle'
ATTR_SHORT_TITLE = '@shortTitle'
ATTR_LAT = '@lat'
ATTR_LON = '@lon'
ATTR_LAT_MIN = '@latMin'
ATTR_LAT_MAX = '@latMax'
ATTR_LON_MIN = '@lonMin'
ATTR_LON_MAX = '@lonMax'
ATTR_STOP_ID = '@stopId'
ATTR_SCHEDULE_CLASS = '@scheduleClass'
ATTR_SERVICE_CLASS = '@serviceClass'
ATTR_DIRECTION = '@direction'
ATTR_EPOCH_TIME = '@epochTime'
ATTR_BLOCK_ID = '@blockID'
ATTR_ID = '@id'
ATTR_SEND_TO_BUSES = '@sendToBuses'
ATTR_PRIORITY = '@priority'
ATTR_START_DAY = '@startDay'
ATTR_START_TIME = '@startTime'
ATTR_END_DAY = '@endDay'
ATTR_END_TIME = '@endTime'
ATTR_DIR_TAG = '@dirTag'
ATTR_SECS_SINCE_REPORT = '@secsSinceReport'
ATTR_PREDICTABLE = '@predictable'
ATTR_HEADING = '@heading'
ATTR_SPEED_KM_HR = '@speedKmHr'
ATTR_TIME = '@time'
ATTR_COLOR = '@color'
ATTR_OPPOSITE_COLOR = '@oppositeColor'
ATTR_SECONDS = '@seconds'
ATTR_MINUTES = '@minutes'
ATTR_IS_DEPARTURE = '@isDeparture'
ATTR_AFFECTED_BY_LAYOVER = '@affectedByLayover'
ATTR_VEHICLE = '@vehicle'
ATTR_BLOCK = '@block'
ATTR_TRIP_TAG = '@tripTag'
ATTR_NAME = '@name'
ATTR_USE_FOR_UI = '@useForUI'


def handle_error(validated_response):
    error = validated_response.get(ELEMENT_BODY).get(ELEMENT_ERROR)
    if error:
        text = error.get('#text')
        if 'Could not get route' in text or re.search('route r=.* is (not valid|invalid)', text):
            raise exceptions.NotFound(text)
        else:
            raise exceptions.BadRequest(text)


def build_agencies_list(validated_response):

    agencies_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_AGENCY)
    if not isinstance(agencies_xml, list):
        agencies_xml = [] if agencies_xml is None else [agencies_xml]

    agencies = []
    for agency_xml in agencies_xml:
        agency = OrderedDict([
            (api.TAG_TAG, agency_xml.get(ATTR_TAG)),
            (api.TAG_TITLE, agency_xml.get(ATTR_TITLE)),
            (api.TAG_REGION_TITLE, agency_xml.get(ATTR_REGION_TITLE))
        ])
        agencies.append(agency)

    return agencies


def build_routes_list(validated_response):

    routes_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_ROUTE)
    if not isinstance(routes_xml, list):
        routes_xml = [] if routes_xml is None else [routes_xml]

    routes = []
    for route_xml in routes_xml:
        route = OrderedDict([
            (api.TAG_TAG, route_xml.get(ATTR_TAG)),
            (api.TAG_TITLE, route_xml.get(ATTR_TITLE))
        ])
        short_title = route_xml.get(ATTR_SHORT_TITLE)
        if short_title:
            route[api.TAG_SHORT_TITLE] = short_title
        routes.append(route)

    return routes


def build_route(validated_response):

    route_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_ROUTE)

    route = OrderedDict()

    route[api.TAG_TAG] = route_xml.get(ATTR_TAG)
    route[api.TAG_TITLE] = route_xml.get(ATTR_TITLE)
    route[api.TAG_COLOR] = route_xml.get(ATTR_COLOR)
    route[api.TAG_OPPOSITE_COLOR] = route_xml.get(ATTR_OPPOSITE_COLOR)
    route[api.TAG_LAT_MIN] = route_xml.get(ATTR_LAT_MIN)
    route[api.TAG_LAT_MAX] = route_xml.get(ATTR_LAT_MAX)
    route[api.TAG_LON_MIN] = route_xml.get(ATTR_LON_MIN)
    route[api.TAG_LON_MAX] = route_xml.get(ATTR_LON_MAX)

    route[api.TAG_STOPS] = build_stops(route_xml)
    route[api.TAG_DIRECTIONS] = build_directions(route_xml)
    route[api.TAG_PATHS] = build_path(route_xml)

    return route


def build_path(route_xml):

    # Add paths to route
    paths_xml = route_xml.get(ELEMENT_PATH)
    if not isinstance(paths_xml, list):
        paths_xml = [] if paths_xml is None else [paths_xml]

    paths = []
    for path_xml in paths_xml:
        # Add points to path

        points_xml = path_xml.get(ELEMENT_POINT)
        if not isinstance(points_xml, list):
            points_xml = [] if points_xml is None else [points_xml]

        points = []
        for point_xml in points_xml:
            point = OrderedDict([
                (api.TAG_LAT, point_xml.get(ATTR_LAT)),
                (api.TAG_LON, point_xml.get(ATTR_LON))
            ])
            points.append(point)
        path = {api.TAG_POINTS: points}
        paths.append(path)

    return paths


def build_directions(route_xml):

    # Add directions to route
    directions_xml = route_xml.get(ELEMENT_DIRECTION)
    if not isinstance(directions_xml, list):
        directions_xml = [] if directions_xml is None else [directions_xml]

    directions = []
    for direction_xml in directions_xml:
        direction = OrderedDict([
            (api.TAG_TAG, direction_xml.get(ATTR_TAG)),
            (api.TAG_TITLE, direction_xml.get(ATTR_TITLE)),
            (api.TAG_NAME, direction_xml.get(ATTR_NAME)),
            (api.TAG_USE_FOR_UI, direction_xml.get(ATTR_USE_FOR_UI))
        ])

        # Add stops to directions
        stops_xml = direction_xml.get(ELEMENT_STOP)
        if not isinstance(stops_xml, list):
            stops_xml = [] if stops_xml is None else [stops_xml]

        stops = []
        for stop_xml in stops_xml:
            stop = OrderedDict([
                (api.TAG_TAG, stop_xml.get(ATTR_TAG))
            ])
            stops.append(stop)

        direction[api.TAG_STOPS] = stops
        directions.append(direction)

    return directions


def build_stops(route_xml):

    stops_xml = route_xml.get(ELEMENT_STOP)
    if not isinstance(stops_xml, list):
        stops_xml = [] if stops_xml is None else [stops_xml]

    stops = []
    for stop_xml in stops_xml:
        stop = OrderedDict([
            (api.TAG_TAG, stop_xml.get(ATTR_TAG)),
            (api.TAG_TITLE, stop_xml.get(ATTR_TITLE)),
            (api.TAG_LAT, stop_xml.get(ATTR_LAT)),
            (api.TAG_LON, stop_xml.get(ATTR_LON)),
            (api.TAG_STOP_ID, stop_xml.get(ATTR_STOP_ID))
        ])
        stops.append(stop)

    return stops


def build_schedule(validated_response):

    routes_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_ROUTE)
    if not isinstance(routes_xml, list):
        routes_xml = [] if routes_xml is None else [routes_xml]

    schedule = OrderedDict()

    schedule[api.TAG_SCHEDULE_CLASS] = routes_xml[0].get(ATTR_SCHEDULE_CLASS)

    schedule[api.TAG_SCHEDULE_ITEMS] = OrderedDict()
    for route_xml in routes_xml:

        schedule_item = build_schedule_item(route_xml)
        schedule_item_key = schedule_item[api.TAG_SERVICE_CLASS].lower() + ':' + \
            schedule_item[api.TAG_DIRECTION].lower()
        schedule[api.TAG_SCHEDULE_ITEMS][schedule_item_key] = schedule_item

    return schedule


def build_schedule_rows(route_xml):

    trs_xml = route_xml.get(ELEMENT_TR)
    if not isinstance(trs_xml, list):
        trs_xml = [] if trs_xml is None else [trs_xml]

    trs_result = []
    for tr_xml in trs_xml:
        tr_result = OrderedDict([
            (api.TAG_BLOCK_ID, tr_xml.get(ATTR_BLOCK_ID))
        ])

        stops_xml = tr_xml.get(ELEMENT_STOP)
        if not isinstance(stops_xml, list):
            stops_xml = [] if stops_xml is None else [stops_xml]

        stops = []
        for stop_xml in stops_xml:
            stop = OrderedDict([
                (api.TAG_TAG, stop_xml.get(ATTR_TAG)),
                (api.TAG_EPOCH_TIME, stop_xml.get(ATTR_EPOCH_TIME)),
                (api.TAG_TIME_DATA, stop_xml.get('#text'))
            ])
            stops.append(stop)
        tr_result[api.TAG_STOPS] = stops

        trs_result.append(tr_result)

    return trs_result


def build_schedule_item(route_xml):

    schedule_item = OrderedDict([
        (api.TAG_SERVICE_CLASS, route_xml.get(ATTR_SERVICE_CLASS)),
        (api.TAG_DIRECTION, route_xml.get(ATTR_DIRECTION))
    ])

    schedule_item[api.TAG_STOPS] = build_schedule_stops(route_xml)

    trs_xml = route_xml.get(ELEMENT_TR)
    if not isinstance(trs_xml, list):
        trs_xml = [] if trs_xml is None else [trs_xml]

    min_epoch = sys.maxint
    max_epoch = -1
    min_start_time_str = ''
    max_start_time_str = ''
    for tr_xml in trs_xml:

        stops_xml = tr_xml.get(ELEMENT_STOP)
        if not isinstance(stops_xml, list):
            stops_xml = [] if stops_xml is None else [stops_xml]

        for stop_xml in stops_xml:
            stop_tag = stop_xml.get(ATTR_TAG)
            stop = OrderedDict()
            epoch_time = stop_xml.get(ATTR_EPOCH_TIME)
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


def build_schedule_stops(route_xml):

    header_stops_xml = route_xml.get(ELEMENT_HEADER).get(ELEMENT_STOP)
    if not isinstance(header_stops_xml, list):
        header_stops_xml = [] if header_stops_xml is None else [header_stops_xml]

    header_stops = {}
    for header_stop_xml in header_stops_xml:
        header_stop = OrderedDict([
            (api.TAG_TAG, header_stop_xml.get(ATTR_TAG)),
            (api.TAG_TITLE, header_stop_xml.get('#text')),
            (api.TAG_SCHEDULED_ARRIVALS, [])
        ])
        header_stops[header_stop[api.TAG_TAG]] = header_stop

    return header_stops


def build_route_messages(validated_response):

    routes_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_ROUTE)
    if not isinstance(routes_xml, list):
        routes_xml = [] if routes_xml is None else [routes_xml]

    messages_all = []
    messages_route = []
    for route_xml in routes_xml:
        route_tag = route_xml.get(ATTR_TAG)
        messages = messages_all if route_tag == 'all' else messages_route

        messages_xml = route_xml.get(ELEMENT_MESSAGE)
        for message_xml in messages_xml:

            message = build_message(message_xml, route_tag)

            messages.append(message)

    route_messages = OrderedDict()
    if messages_all:
        route_messages[api.TAG_ALL_MESSAGES] = messages_all
    if messages_route:
        route_messages[api.TAG_ROUTE_MESSAGES] = messages_route

    return route_messages


def build_message(message_xml, route_tag):
    message = OrderedDict([
        (api.TAG_ID, message_xml.get(ATTR_ID)),
        (api.TAG_SEND_TO_BUSES, message_xml.get(ATTR_SEND_TO_BUSES)),
        (api.TAG_PRIORITY, message_xml.get(ATTR_PRIORITY)),
        (api.TAG_TEXT, message_xml.get(ELEMENT_TEXT))
    ])
    if route_tag != 'all':
        message[api.TAG_STOPS] = []
        route_configured_xml = message_xml.get(ELEMENT_ROUTE_CONF_FOR_MSG)
        stops_xml = route_configured_xml.get(ELEMENT_STOP) if route_configured_xml else []
        for stop_xml in stops_xml:
            stop = OrderedDict([
                (api.TAG_TAG, stop_xml.get(ATTR_TAG)),
                (api.TAG_TITLE, stop_xml.get(ATTR_TITLE))
            ])
            message[api.TAG_STOPS].append(stop)
        intervals_xml = message_xml.get(ELEMENT_INTERVAL)
        if intervals_xml:
            message[api.TAG_INTERVALS] = []
        for interval_xml in intervals_xml:
            interval = OrderedDict([
                (api.TAG_START_DAY, interval_xml.get(ATTR_START_DAY)),
                (api.TAG_START_TIME, interval_xml.get(ATTR_START_TIME)),
                (api.TAG_END_DAY, interval_xml.get(ATTR_END_DAY)),
                (api.TAG_END_TIME, interval_xml.get(ATTR_END_TIME))
            ])
            message[api.TAG_INTERVALS].append(interval)

    return message


def build_route_vehicles(validated_response):

    route_vehicles = OrderedDict()
    route_vehicles[api.TAG_VEHICLES] = []

    vehicles_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_VEHICLE)
    if not isinstance(vehicles_xml, list):
        vehicles_xml = [] if vehicles_xml is None else [vehicles_xml]

    for vehicle_xml in vehicles_xml:
        vehicle = OrderedDict([
            (api.TAG_ID, vehicle_xml.get(ATTR_ID)),
            (api.TAG_DIR_TAG, vehicle_xml.get(ATTR_DIR_TAG)),
            (api.TAG_LAT, vehicle_xml.get(ATTR_LAT)),
            (api.TAG_LON, vehicle_xml.get(ATTR_LON)),
            (api.TAG_SECS_SINCE_REPORT, vehicle_xml.get(ATTR_SECS_SINCE_REPORT)),
            (api.TAG_PREDICTABLE, vehicle_xml.get(ATTR_PREDICTABLE)),
            (api.TAG_HEADING, vehicle_xml.get(ATTR_HEADING)),
            (api.TAG_SPEED_KM_HR, vehicle_xml.get(ATTR_SPEED_KM_HR))
        ])

        route_vehicles[api.TAG_VEHICLES].append(vehicle)

    route_vehicles[api.TAG_LAST_TIME] = validated_response.get(ELEMENT_BODY).\
        get(ELEMENT_LAST_TIME).get(ATTR_TIME)

    return route_vehicles


def build_route_predictions(validated_response):

    route_predictions = OrderedDict()

    directions_xml = validated_response.get(ELEMENT_BODY).get(ELEMENT_PREDICTIONS).\
        get(ELEMENT_DIRECTION)

    if not isinstance(directions_xml, list):
        directions_xml = [] if directions_xml is None else [directions_xml]

    route_predictions[api.TAG_DIRECTIONS] = []
    for direction_xml in directions_xml:

        direction = OrderedDict([
            (api.TAG_TITLE, direction_xml.get(ATTR_TITLE))
        ])

        predictions_xml = direction_xml.get(ELEMENT_PREDICTION)
        if not isinstance(predictions_xml, list):
            predictions_xml = [] if predictions_xml is None else [predictions_xml]

        direction[api.TAG_PREDICTIONS] = []
        for prediction_xml in predictions_xml:
            prediction = OrderedDict([
                (api.TAG_EPOCH_TIME, prediction_xml.get(ATTR_EPOCH_TIME)),
                (api.TAG_SECONDS, prediction_xml.get(ATTR_SECONDS)),
                (api.TAG_MINUTES, prediction_xml.get(ATTR_MINUTES)),
                (api.TAG_IS_DEPARTURE, prediction_xml.get(ATTR_IS_DEPARTURE)),
                (api.TAG_AFFECTED_BY_LAYOVER, prediction_xml.get(ATTR_AFFECTED_BY_LAYOVER)),
                (api.TAG_DIR_TAG, prediction_xml.get(ATTR_DIR_TAG)),
                (api.TAG_VEHICLE, prediction_xml.get(ATTR_VEHICLE)),
                (api.TAG_BLOCK, prediction_xml.get(ATTR_BLOCK)),
                (api.TAG_TRIP_TAG, prediction_xml.get(ATTR_TRIP_TAG))
            ])

            direction[api.TAG_PREDICTIONS].append(prediction)

        route_predictions[api.TAG_DIRECTIONS].append(direction)

    return route_predictions
