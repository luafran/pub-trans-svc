"""
Tornado handler for agencies resource
"""
from tornado import gen


from pubtrans.domain import api
from pubtrans.domain import service as svc
from pubtrans.handlers import base_handler


class AgenciesHandlerV1(base_handler.BaseHandler):

    @gen.coroutine
    def get(self):

        repository = self.application_settings.repository

        service = svc.Service(repository, self.support)
        agencies = yield service.get_agencies()

        response = {
            api.TAG_AGENCIES: agencies
        }

        self.build_response(response)
