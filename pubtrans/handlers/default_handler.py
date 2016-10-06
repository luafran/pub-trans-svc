"""
Tornado default handler
"""
from tornado import gen

from pubtrans.common import exceptions
from pubtrans.handlers.base_handler import BaseHandler


class DefaultHandler(BaseHandler):
    """
    Tornado default handler class. It just return a formatted version of not found
    """

    @gen.coroutine
    def get(self):
        self._build_not_found()

    @gen.coroutine
    def post(self):
        self._build_not_found()

    @gen.coroutine
    def put(self):
        self._build_not_found()

    @gen.coroutine
    def delete(self):
        self._build_not_found()

    def _build_not_found(self):
        self.build_response(exceptions.NotFound(self.request.path))
