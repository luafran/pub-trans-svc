"""
Tornado base handler to be used as a base for all handlers
"""
import datetime
import json
import logging
import logging.config
import os
import sys
import uuid

import tornado.web
import tornado.httpclient

from pubtrans.common import constants
from pubtrans.common import exceptions
from pubtrans.config import settings
from pubtrans.common.support import Support


class BaseHandler(tornado.web.RequestHandler):
    """
    Tornado base handler to be used as a base for all handlers
    Add some extra functionality like:
    - Hold settings instance to be used by handlers
    - Define (if not received) a new request id the ease debugging
    - Initialize logging and statistics with context information
    - Log requests
    """
    def __init__(self, application, request, **kwargs):
        """
        Constructor
        """
        super(BaseHandler, self).__init__(application, request, **kwargs)

        self.created_time = datetime.datetime.now()

    def data_received(self, chunk):
        pass

    def initialize(self, application_settings=None, handler_name=None):  # pylint: disable=arguments-differ
        """
        Common Handler initialization.
        Build logger with extra information taken from environment and request
        """

        self.application_settings = application_settings
        self.handler_name = handler_name
        self.request_id = self.request.headers.get(constants.REQUEST_ID_HTTP_HEADER,
                                                   'pubtrans-'+str(uuid.uuid4()))

        logging.config.dictConfig(settings.LOGGING)
        logger = logging.getLogger(settings.LOGGER_NAME)

        environment_name = 'PUBTRANS_ENV'

        environment = os.environ.get(environment_name)
        if not environment:
            environment = 'unknown'

        self.environment = environment

        extra_info = {
            'environment': environment,
            'service': self.settings.get('service_name'),
            'handler': handler_name,
            'requestId': self.request_id
        }
        self.support = Support(logger, extra_info)

    def prepare(self):
        """
        Called at the beginning of a request before get/post/etc.
        Log request and update statistics
        """

        try:

            request = self.request

            self.support.notify_debug(
                "[BaseHandler] request: %s %s" % (str(request.method), str(request.uri)))
            self.support.notify_debug(
                "[BaseHandler] request query: %s" % str(request.query))
            self.support.notify_debug(
                "[BaseHandler] request headers: %s" % str(['{0}: {1}'.format(k, v)
                                                           for k, v in request.headers.get_all()]))
            self.support.notify_debug(
                "[BaseHandler] request body: %s" % str(request.body))

            body_size = sys.getsizeof(request.body)
            self.support.stat_increment('net.requests.total_count')
            self.support.stat_increment('net.requests.total_bytes', body_size)
            self.support.stat_increment('net.requests.' + str(request.method) + '_count')
            self.support.stat_increment('net.requests.' + str(request.method) + '_bytes', body_size)

        except exceptions.InfoException as ex:
            self.support.notify_error(ex)
            self.build_response(ex)
        except Exception as ex:  # pylint: disable=broad-except
            self.support.notify_error(ex)
            self.build_response(ex)

    def _handle_request_exception(self, ex):
        """
        Send formatted error responses based upon exceptions thrown by the application
        """
        self.support.notify_error(ex)
        self.build_response(ex)

    def build_response(self, result, status_code=None):
        """
        Build the response data with the required format according to result
        """
        self._build_response_internal(True, result, status_code)

    def build_response_without_format(self, result, status_code=None):
        """
        Build the response data with the required format according to result
        """
        self._build_response_internal(False, result, status_code)

    def _build_response_internal(self, apply_format, result, status_code=None):
        """
        Build the response data with the required format according to result
        """

        if apply_format:
            self.set_header("Content-Type", "application/json")

        if isinstance(result, Exception):
            body = self._build_response_from_exception(result)
            self.write(body)
        else:
            if apply_format:
                body = json.dumps(result)
            else:
                body = result

            if self.request.method == 'GET':
                self.set_status(status_code if status_code is not None else 200)
                self.write(body)
            elif self.request.method == 'POST':
                self.set_status(status_code if status_code is not None else 201)
                self.write(body)
            elif self.request.method == 'PUT':
                self.set_status(status_code if status_code is not None else 204)
            elif self.request.method == 'DELETE':
                self.set_status(status_code if status_code is not None else 200)
            else:
                pass

        if self.request_id:
            self.set_header(constants.REQUEST_ID_HTTP_HEADER, self.request_id)

        self.support.stat_increment('net.responses.total_count')
        self.support.stat_increment('net.responses.total_bytes', sys.getsizeof(body))
        self.support.stat_increment('net.responses.' + str(self.get_status()))

        total_time = datetime.datetime.now() - self.created_time
        timing = int(total_time.total_seconds() * 1000)
        self.support.notify_debug("[BaseHandler] Processing Time: %i ms" % timing)
        self.support.stat_timing('net.responses.time', timing)

        if not isinstance(result, exceptions.NotFoundBase):
            self.support.update_uri_stats(self.request.path, timing)

        self.support.notify_debug(
            "[BaseHandler] response code: %s" % str(self.get_status()))
        self.support.notify_debug(
            "[BaseHandler] response body: %s" % str(body))

        self.finish()

    def _build_response_from_exception(self, ex):
        """
        Build HTTP response from an exception
        """
        if isinstance(ex, exceptions.BadRequestBase):
            self.set_status(400)
        elif isinstance(ex, exceptions.UnauthorizedBase):
            self.set_status(401)
        elif isinstance(ex, exceptions.ForbiddenBase):
            self.set_status(403)
        elif isinstance(ex, exceptions.NotFoundBase):
            self.set_status(404)
        elif isinstance(ex, exceptions.Conflict):
            self.set_status(409)
        elif isinstance(ex, exceptions.PermanentServiceError):
            self.set_status(500)
        elif isinstance(ex, exceptions.TemporaryServiceError):
            self.set_status(503)
        elif isinstance(ex, tornado.web.HTTPError):
            self.set_status(ex.status_code)
            ex = exceptions.GeneralInfoException('Web HTTPError')
        elif isinstance(ex, tornado.httpclient.HTTPError):
            self.set_status(ex.code)
            ex = exceptions.GeneralInfoException('Client HTTPError')
        else:
            self.set_status(500)
            import traceback
            formatted_lines = traceback.format_exc().splitlines()
            ex = exceptions.GeneralInfoException(formatted_lines[-1])

        ex.info[exceptions.REQUEST_ID_KEY] = self.request_id
        response_body = str(ex)
        return response_body
