"""
Tornado handler for health resource
"""
import json
import tornado.gen

from pubtrans.common import version
from pubtrans.handlers.base_handler import BaseHandler


class HealthHandlerV1(BaseHandler):
    """
    Tornado handler class for health resource
    """

    HEALTH_STATUS = (STATUS_OK, STATUS_WARNING, STATUS_ERROR) = ((0, 'OK'), (1, 'WARNING'), (2, 'ERROR'))
    HEALTH_EXPOSURE = (LOW, MEDIUM, HIGH) = ('LOW', 'MEDIUM', 'HIGH')

    @tornado.gen.coroutine
    def get(self):
        """
        /health GET handler
        """

        self.set_header("Content-Type", "application/json")

        service_name = self.settings.get('service_name')
        service_health, details, service_version = yield self.get_health()

        response_body = {
            "status": {
                "health": service_health,
                "details": details,
                "service": service_name,
                "version": service_version
            }
        }

        self.set_status(200)
        self.write(json.dumps(response_body))

        self.finish()

    @tornado.gen.coroutine
    def get_health(self):

        service_health = self.STATUS_OK
        details = []

        raise tornado.gen.Return((service_health, details, version.get_version()))
