"""
Service main function
Tornado application and URL mappings
"""
import tornado.ioloop
import tornado.web

from pubtrans.config import settings
from pubtrans.handlers import default_handler
from pubtrans.handlers import health
from pubtrans.handlers import agencies
from pubtrans.handlers import routes
from pubtrans.handlers import route_schedule
from pubtrans.repositories import redis_nextbus_repository


def make_app():

    settings.nextbus_repository = redis_nextbus_repository.RedisNextBusRepository(None)

    _the_app = tornado.web.Application(
        [
            (r'.*/v1/agencies$', agencies.AgenciesHandlerV1,
             {'application_settings': settings, 'handler_name': 'AgenciesHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)$', routes.RoutesHandlerV1,
             {'application_settings': settings, 'handler_name': 'RoutesHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)/schedule$', route_schedule.RouteScheduleHandlerV1,
             {'application_settings': settings, 'handler_name': 'ScheduleHandlerV1'}),
            (r'.*/health/?$', health.HealthHandler,
             {'application_settings': settings, 'handler_name': 'Health'}),
        ],
        default_handler_class=default_handler.DefaultHandler,
        service_name='pubtrans',
        autoreload=settings.AUTO_RELOAD)

    return _the_app

if __name__ == "__main__":
    APPLICATION = make_app()
    APPLICATION.listen(settings.DEFAULT_PORT)
    print "Listening at port {0}...".format(settings.DEFAULT_PORT)
    tornado.ioloop.IOLoop.current().start()
