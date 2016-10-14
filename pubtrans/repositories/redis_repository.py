"""
Store NextBus entities in a Redis database
"""
import json

import redis
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.config import settings

KEY_AGENCIES = 'agencies'
KEY_ROUTE = 'route'
KEY_ROUTES = 'routes'
KEY_ROUTE_SCHEDULE = 'route_schedule'
KEY_ROUTE_MESSAGES = 'route_messages'
KEY_ROUTE_VEHICLES = 'route_vehicles'
KEY_ROUTE_PREDICTIONS = 'route_predictions'


class RedisRepository(object):
    def __init__(self, context):
        self.context = context

    @gen.coroutine
    def get_agencies(self):  # pylint: disable=no-self-use
        r_connection = self.get_redis_connection('slave')
        try:
            data = r_connection.get(KEY_AGENCIES)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get agencies from redis: {0}'.format(ex.message))

        if data is None:
            agencies = None
        else:
            try:
                agencies = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for agencies')

        raise gen.Return(agencies)

    @gen.coroutine
    def store_agencies(self, agencies):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        agencies_ttl = settings.AGENCIES_CACHE_TTL_SECONDS
        try:

            r_connection.set(KEY_AGENCIES, json.dumps(agencies), ex=agencies_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store agencies in redis: {0}'.format(ex.message))

        raise gen.Return(agencies)

    @gen.coroutine
    def get_routes(self, agency_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTES
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get routes from redis: {0}'.format(ex.message))

        if data is None:
            routes = None
        else:
            try:
                routes = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for routes')

        raise gen.Return(routes)

    @gen.coroutine
    def store_routes(self, agency_tag, routes):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        routes_ttl = settings.ROUTES_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTES
            r_connection.set(key_name, json.dumps(routes), ex=routes_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store routes in redis: {0}'.format(ex.message))

        raise gen.Return(routes)

    @gen.coroutine
    def get_route(self, agency_tag, route_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTE + ':' + route_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route from redis: {0}'.format(ex.message))

        if data is None:
            route = None
        else:
            try:
                route = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for route')

        raise gen.Return(route)

    @gen.coroutine
    def store_route(self, agency_tag, route_tag, route):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        routes_ttl = settings.ROUTE_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE + ':' + route_tag
            r_connection.set(key_name, json.dumps(route), ex=routes_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store route in redis: {0}'.format(ex.message))

        raise gen.Return(route)

    @gen.coroutine
    def get_route_schedule(self, agency_tag, route_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTE_SCHEDULE + ':' + route_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route schedule from redis: {0}'.
                                                    format(ex.message))
        if data is None:
            schedule = None
        else:
            try:
                schedule = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for schedule')

        raise gen.Return(schedule)

    @gen.coroutine
    def store_route_schedule(self, agency_tag, route_tag, schedule):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        route_schedule_ttl = settings.SCHEDULE_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE_SCHEDULE + ':' + route_tag
            r_connection.set(key_name, json.dumps(schedule), ex=route_schedule_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store route schedule in redis: {0}'.
                                                    format(ex.message))

        raise gen.Return(schedule)

    @gen.coroutine
    def get_route_messages(self, agency_tag, route_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTE_MESSAGES + ':' + route_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route messages from redis: {0}'.
                                                    format(ex.message))
        if data is None:
            messages = None
        else:
            try:
                messages = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for route messages')

        raise gen.Return(messages)

    @gen.coroutine
    def store_route_messages(self, agency_tag, route_tag, messages):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        route_messages_ttl = settings.ROUTE_MESSAGES_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE_MESSAGES + ':' + route_tag
            r_connection.set(key_name, json.dumps(messages), ex=route_messages_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store route messages in redis: {0}'.
                                                    format(ex.message))

        raise gen.Return(messages)

    @gen.coroutine
    def get_route_vehicles(self, agency_tag, route_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTE_VEHICLES + ':' + route_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route vehicles from redis: {0}'.
                                                    format(ex.message))
        if data is None:
            vehicles = None
        else:
            try:
                vehicles = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for route vehicles')

        raise gen.Return(vehicles)

    @gen.coroutine
    def store_route_vehicles(self, agency_tag, route_tag, vehicles):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        route_messages_ttl = settings.ROUTE_VEHICLES_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE_VEHICLES + ':' + route_tag
            r_connection.set(key_name, json.dumps(vehicles), ex=route_messages_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store route vehicles in redis: {0}'.
                                                    format(ex.message))

        raise gen.Return(vehicles)

    @gen.coroutine
    def get_route_predictions(self, agency_tag, route_tag, stop_tag):  # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('slave')

        try:
            key_name = agency_tag + ':' + KEY_ROUTE_PREDICTIONS + ':' + route_tag + ':' + stop_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route predictions from redis: {0}'.
                                                    format(ex.message))
        if data is None:
            predictions = None
        else:
            try:
                predictions = json.loads(data)
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for route predictions')

        raise gen.Return(predictions)

    @gen.coroutine
    def store_route_predictions(self, agency_tag, route_tag, stop_tag, predictions):
        # pylint: disable=no-self-use

        r_connection = self.get_redis_connection('master')

        route_messages_ttl = settings.ROUTE_PREDICTIONS_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE_PREDICTIONS + ':' + route_tag + ':' + stop_tag
            r_connection.set(key_name, json.dumps(predictions), ex=route_messages_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store route predictions in redis: {0}'.
                                                    format(ex.message))

        raise gen.Return(predictions)

    @staticmethod
    def get_redis_connection(role):

        host = settings.REDIS_MASTER_HOST if role == 'master' else settings.REDIS_SLAVE_HOST

        r_connection = redis.StrictRedis(host=host, port=settings.REDIS_PORT, db=0)

        return r_connection
