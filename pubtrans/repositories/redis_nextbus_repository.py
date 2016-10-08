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


class RedisNextBusRepository(object):
    def __init__(self, context):
        self.context = context

    @gen.coroutine
    def get_agencies(self):  # pylint: disable=no-self-use
        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        try:
            data = r_connection.get(KEY_AGENCIES)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get agencies from redis: {0}'.format(ex.message))

        if data is None:
            response = None
        else:
            try:
                agencies = json.loads(data)
                response = agencies
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for agencies')

        return response

    @gen.coroutine
    def store_agencies(self, agencies):  # pylint: disable=no-self-use

        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        agencies_ttl = settings.NEXTBUS_CACHE_TTL_SECONDS
        try:

            r_connection.set(KEY_AGENCIES, json.dumps(agencies), ex=agencies_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store agencies in redis: {0}'.format(ex.message))

        response = agencies

        return response

    @gen.coroutine
    def get_routes(self, agency_tag):  # pylint: disable=no-self-use
        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        try:
            key_name = agency_tag + ':' + KEY_ROUTES
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get routes from redis: {0}'.format(ex.message))

        if data is None:
            response = None
        else:
            try:
                routes = json.loads(data)
                response = routes
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for routes')

        return response

    @gen.coroutine
    def store_routes(self, agency_tag, routes):  # pylint: disable=no-self-use

        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        routes_ttl = settings.NEXTBUS_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTES
            r_connection.set(key_name, json.dumps(routes), ex=routes_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store routes in redis: {0}'.format(ex.message))

        response = routes

        return response

    @gen.coroutine
    def get_route(self, agency_tag, route_tag):  # pylint: disable=no-self-use
        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        try:
            key_name = agency_tag + ':' + KEY_ROUTE + ':' + route_tag
            data = r_connection.get(key_name)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot get route from redis: {0}'.format(ex.message))

        if data is None:
            response = None
        else:
            try:
                route = json.loads(data)
                response = [route]
            except TypeError:
                raise exceptions.DatabaseOperationError('Invalid format for route')

        return response

    @gen.coroutine
    def store_route(self, agency_tag, route_tag, route):  # pylint: disable=no-self-use

        r_connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        routes_ttl = settings.NEXTBUS_CACHE_TTL_SECONDS
        try:
            key_name = agency_tag + ':' + KEY_ROUTE + ':' + route_tag
            r_connection.set(key_name, json.dumps(route), ex=routes_ttl)
        except redis.ConnectionError as ex:
            raise exceptions.DatabaseOperationError('Cannot store routes in redis: {0}'.format(ex.message))

        response = route

        return response
