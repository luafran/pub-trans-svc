"""
Service main function
Tornado application and URL mappings
"""
import signal
import tornado.ioloop
import tornado.web

from pubtrans.config import settings
from pubtrans.handlers import default_handler
from pubtrans.handlers import health
from pubtrans.handlers import agencies
from pubtrans.handlers import routes
from pubtrans.handlers import route_schedule
from pubtrans.handlers import route_messages
from pubtrans.handlers import route_vehicles
from pubtrans.handlers import stats
from pubtrans.repositories import redis_repository


def shutdown():
    tornado.ioloop.IOLoop.current().stop()


def sig_handler(sig, frame):  # pylint: disable=unused-argument
    print "SIGTERM or SIGINT received"
    tornado.ioloop.IOLoop.current().add_callback(shutdown)


def make_app():

    settings.repository = redis_repository.RedisRepository(None)

    _the_app = tornado.web.Application(
        [
            (r'.*/v1/agencies$', agencies.AgenciesHandlerV1,
             {'application_settings': settings, 'handler_name': 'AgenciesHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)$', routes.RoutesHandlerV1,
             {'application_settings': settings, 'handler_name': 'RoutesHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)/schedule$', route_schedule.RouteScheduleHandlerV1,
             {'application_settings': settings, 'handler_name': 'RouteScheduleHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)/messages$', route_messages.RouteMessagesHandlerV1,
             {'application_settings': settings, 'handler_name': 'RouteMessagesHandlerV1'}),
            (r'.*/v1/([^/]*)/routes/?([^/]*)/vehicles$', route_vehicles.RouteVehiclesHandlerV1,
             {'application_settings': settings, 'handler_name': 'RouteVehiclesHandlerV1'}),
            (r'.*/v1/stats/?([^/]*)$', stats.StatsHandlerV1,
             {'application_settings': settings, 'handler_name': 'StatsHandlerV1'}),
            (r'.*/v1/health/?$', health.HealthHandlerV1,
             {'application_settings': settings, 'handler_name': 'HealthHandlerV1'}),
        ],
        default_handler_class=default_handler.DefaultHandler,
        service_name='pubtrans',
        autoreload=settings.AUTO_RELOAD)

    return _the_app

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    APPLICATION = make_app()
    APPLICATION.listen(settings.DEFAULT_PORT)
    print "Listening at port {0}...".format(settings.DEFAULT_PORT)
    tornado.ioloop.IOLoop.current().start()
