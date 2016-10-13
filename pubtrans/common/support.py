"""
Generic (domain agnostic) stuff to support application
"""
import Queue
from collections import OrderedDict

import redis
import statsd

from pubtrans.common import constants
from pubtrans.config import settings


class Support(object):
    """
    Class used to notify events useful to support the application
    """

    SET_URIS_COUNT = 'uris:count'
    SET_SLOW_REQUESTS = 'uris:slow_requests'

    def __init__(self, logger, extra_info=None):
        """
        Initialize instance with a logger to be used, info related to the request and info related to
        the service
        """

        self._logger = logger

        if not extra_info:
            extra_info = {}

        environment = extra_info.get('environment')

        self._extra = {
            'env': environment,
            'service': extra_info.get('service'),
            'handler': extra_info.get('handler'),
            'requestId': extra_info.get('requestId', constants.NO_REQUEST_ID),
            'details': ''
        }

        self._stats_enabled = settings.STATS_ENABLED

        if self._stats_enabled:
            self._stats_client = statsd.StatsClient(host=settings.STATS_SERVICE_HOSTNAME,
                                                    port=8125, prefix='pubtrans.' + environment)
        self._messages_queue = Queue.Queue()
        self.log_entire_request = settings.LOG_LEVEL in ['CRITICAL', 'ERROR']

    def _log_entire_request(self, log_method):
        try:
            while True:
                message = self._messages_queue.get_nowait()
                log_method(message, extra=self._extra)
        except Queue.Empty:
            pass

    def notify_critical(self, message, details=None):
        """Notify a critical event"""

        self._extra['details'] = details if details else message
        log_method = self._logger.critical
        if self.log_entire_request:
            self._log_entire_request(log_method)
        log_method(message, extra=self._extra)

    def notify_error(self, message, details=None):
        """Notify an error event"""

        self._extra['details'] = details if details else message
        log_method = self._logger.error
        if self.log_entire_request:
            self._log_entire_request(log_method)
        log_method(message, extra=self._extra)

    def notify_warning(self, message, details=None):
        """Notify a warning event"""

        self._extra['details'] = details if details else message
        self._logger.warning(message, extra=self._extra)
        if self.log_entire_request:
            self._messages_queue.put_nowait(message)

    def notify_info(self, message, details=None):
        """Notify an information event"""

        self._extra['details'] = details if details else message
        self._logger.info(message, extra=self._extra)
        if self.log_entire_request:
            self._messages_queue.put_nowait(message)

    def notify_debug(self, message, details=None):
        """Notify a debug event"""

        self._extra['details'] = details if details else message
        self._logger.debug(message, extra=self._extra)
        if self.log_entire_request:
            self._messages_queue.put_nowait(message)

    def stat_increment(self, stat, count=1, rate=1):
        if self._stats_enabled:
            self._stats_client.incr(stat, count, rate)

    def stat_decrement(self, stat, count=1, rate=1):
        if self._stats_enabled:
            self._stats_client.decr(stat, count, rate)

    def stat_gauge(self, stat, value, rate=1, delta=False):
        if self._stats_enabled:
            self._stats_client.gauge(stat, value, rate, delta)

    def stat_set(self, stat, value, rate=1):
        if self._stats_enabled:
            self._stats_client.set(stat, value, rate)

    def stat_timing(self, stat, value, rate=1):
        if self._stats_enabled:
            self._stats_client.timing(stat, value, rate)

    def update_uri_stats(self, uri, timing):
        count = 1
        try:
            r_connection = redis.StrictRedis(host=settings.REDIS_MASTER_HOST, port=settings.REDIS_PORT, db=0)
            r_connection.zincrby(self.SET_URIS_COUNT, uri, count)
            r_connection.zadd(self.SET_SLOW_REQUESTS, timing, uri)

        except redis.ConnectionError as ex:
            # Should not fail if cache is not available
            self.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                             format('Support', ex.message))

    def get_uri_count(self):

        try:
            r_connection = redis.StrictRedis(host=settings.REDIS_MASTER_HOST, port=settings.REDIS_PORT, db=0)
            redis_response = r_connection.zrevrangebyscore(self.SET_URIS_COUNT, '+inf', '-inf',
                                                           withscores=True)
        except redis.ConnectionError as ex:
            # Should not fail if cache is not available
            self.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                             format('Support', ex.message))
            redis_response = []

        response = OrderedDict()
        for uri in redis_response:
            response[uri[0]] = int(uri[1])

        return response

    def get_slow_requests(self, slow_limit):

        try:
            r_connection = redis.StrictRedis(host=settings.REDIS_MASTER_HOST, port=settings.REDIS_PORT, db=0)

            min_score = '-inf'
            if slow_limit:
                min_score = slow_limit

            redis_response = r_connection.zrevrangebyscore(self.SET_SLOW_REQUESTS, '+inf', min_score,
                                                           withscores=True)
        except redis.ConnectionError as ex:
            # Should not fail if cache is not available
            self.notify_info('[{0}] Not using cache. Cache not available: {1}'.
                             format('Support', ex.message))
            redis_response = []

        response = OrderedDict()
        for uri in redis_response:
            response[uri[0]] = int(uri[1])

        return response
