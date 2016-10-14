"""
Service main function
Tornado application and URL mappings
"""
import logging
import signal
import time
import tornado.ioloop
import tornado.web

from pubtrans.common import breaker
from pubtrans.common import exceptions
from pubtrans.config import settings
from pubtrans.handlers import default_handler
from pubtrans.handlers import health
from pubtrans.handlers import agencies
from pubtrans.handlers import route_predictions
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

    circuit_breaker = breaker.CircuitBreakerSet(time.time, logging.getLogger('circuit-breaker'))
    circuit_breaker.handle_errors([exceptions.ExternalProviderUnavailableTemporarily,
                                   exceptions.ExternalProviderUnavailablePermanently])

    settings.circuit_breaker_set = circuit_breaker

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
            (r'.*/v1/([^/]*)/routes/?([^/]*)/predictions$', route_predictions.RoutePredictionsHandlerV1,
             {'application_settings': settings, 'handler_name': 'RoutePredictionsHandlerV1'}),
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
