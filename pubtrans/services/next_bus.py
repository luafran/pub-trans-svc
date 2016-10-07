"""
Connector to NextBus Service
"""
from tornado import gen

from pubtrans.common import constants
from pubtrans.common import exceptions
from pubtrans.config import settings
from pubtrans.decorators import retry_decorator
from pubtrans.services import base_service as base


class NextBusService(base.BaseService):  # pylint: disable=R0903
    """
    Connector to Next Bus Service
    """

    LOG_TAG = '[NextBus Service] %s'

    COMMAND_AGENCY_LIST = 'agencyList'

    ELEMENT_BODY = 'body'
    ELEMENT_AGENCY = 'agency'

    def __init__(self, support=None):
        endpoint = settings.NEXTBUS_SERVICE_URL
        super(NextBusService, self).__init__(endpoint, support)

        self.headers = {
            constants.ACCEPT_HEADER: "application/xml"
        }

        self.timeout = settings.NEXTBUS_SERVICE_TIMEOUT

    @retry_decorator.retry(exceptions.ExternalProviderUnavailableTemporarily,
                           tries=settings.NEXTBUS_SERVICE_RETRIES,
                           delay=settings.NEXTBUS_SERVICE_RETRIES_DELAY,
                           backoff=settings.NEXTBUS_SERVICE_RETRIES_BACKOFF)
    @gen.coroutine
    def get_all_agencies(self):
        """
        Get all agencies
        """

        query = {
            'command': self.COMMAND_AGENCY_LIST
        }

        response_code, response_body =\
            yield self.rest_adapter.get(query=query,
                                        headers=self.headers,
                                        timeout=self.timeout)

        self.log_response(self.LOG_TAG, response_code, response_body)

        validated_response = self.validate_response(response_code, response_body, 'xml')
        agencies = self.build_agencies_list(validated_response)
        raise gen.Return(agencies)

    def build_agencies_list(self, validated_response):
        agencies_xml = validated_response.get(self.ELEMENT_BODY).get(self.ELEMENT_AGENCY)

        agencies = []
        for agency_xml in agencies_xml:
            agency = {
                'tag': agency_xml.get('@tag'),
                'title': agency_xml.get('@title'),
                'regionTitle': agency_xml.get('@regionTitle')
            }
            agencies.append(agency)

        return agencies
