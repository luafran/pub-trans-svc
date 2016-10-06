"""
Service main function
Tornado application and URL mappings
"""
import tornado.ioloop
import tornado.web

from pubtrans.config import settings
from pubtrans.handlers import default_handler
from pubtrans.handlers import health


def make_app():

    _the_app = tornado.web.Application(
        [
            (r'.*/health/?$', health.HealthHandler,
             {'application_settings': settings, 'handler_name': 'Health'}),
        ],
        default_handler_class=default_handler.DefaultHandler,
        service_name='omli',
        autoreload=settings.AUTO_RELOAD)

    return _the_app

if __name__ == "__main__":
    APPLICATION = make_app()
    APPLICATION.listen(settings.DEFAULT_PORT)
    print "Listening at port {0}...".format(settings.DEFAULT_PORT)
    tornado.ioloop.IOLoop.current().start()
