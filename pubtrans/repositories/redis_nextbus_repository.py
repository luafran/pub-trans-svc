"""
Store NextBus entities in a Redis database
"""
import json

import redis
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.config import settings

KEY_AGENCIES = 'agencies'


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
