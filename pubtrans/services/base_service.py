"""
Base connector to interact with external services
"""
import json
import xmltodict

from pubtrans.common import exceptions
from pubtrans.common import rest_adapter


class BaseService(object):

    """
    Base connector to interact with external services
    """

    def __init__(self, endpoint, context=None, support=None, use_system_proxies=False):
        self.rest_adapter = rest_adapter.RestAdapter(
            endpoint, context, support, use_system_proxies=use_system_proxies)

        self._context = context
        self._support = support

    def log_response(self, log_tag, response_code, response_body):
        if not self._support:
            return

        if 200 <= response_code <= 399:
            self._support.notify_debug(
                log_tag % ('response code: %i' % response_code))
            self._support.notify_debug(
                log_tag % ('response body: %s' % response_body))
        else:
            self._support.notify_error(
                log_tag % ('response code: %i' % response_code))
            self._support.notify_error(
                log_tag % ('response body: %s' % response_body))

    def validate_response(self, response_code, response_body, response_format=None):
        """
        Validate external response
        """
        # pylint: disable=R0201
        success_response_codes = [200, 201, 202, 204, ]
        error_response_codes = {
            # 4xx Client Error
            400: exceptions.BadRequest,
            401: exceptions.Unauthorized,
            403: exceptions.Forbidden,
            404: exceptions.NotFound,
            405: exceptions.MethodNotAllowed,
            # 5xx Server Error
            500: exceptions.ExternalProviderUnavailablePermanently,
            503: exceptions.ExternalProviderUnavailableTemporarily,
            598: exceptions.ExternalProviderUnavailableTemporarily,
            599: exceptions.ExternalProviderUnavailableTemporarily,
        }

        formatter_mapping = {
            'text': unicode,
            'json': lambda x: json.loads(x) if x else {},
            'xml': lambda x: xmltodict.parse(x) if x else {}
        }

        if response_code not in success_response_codes:
            try:
                raise error_response_codes[response_code](response_body)
            except KeyError:
                raise exceptions.GeneralInfoException(response_body)

        try:
            formatter = (response_format if response_format is not None else 'json')
            formatted_response_body = formatter_mapping[formatter](response_body)
            return formatted_response_body
        except KeyError:
            raise NotImplementedError(formatter)
        except (TypeError, ValueError) as ex:
            raise ValueError('Invalid response body: %s' % ex)
