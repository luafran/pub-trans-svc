"""
Service settings
"""
AUTO_RELOAD = True
DEFAULT_PORT = 80

REDIS_MASTER_HOST = "redis-master"
REDIS_SLAVE_HOST = "redis-slave"
REDIS_PORT = 6379
NEXTBUS_CACHE_TTL_SECONDS = 60

STATS_ENABLED = False
STATS_SERVICE_HOSTNAME = "localhost"

NEXTBUS_SERVICE_URL = 'http://webservices.nextbus.com/service/publicXMLFeed'
NEXTBUS_SERVICE_TIMEOUT = 5
NEXTBUS_SERVICE_RETRIES = 3
NEXTBUS_SERVICE_RETRIES_DELAY = 0
NEXTBUS_SERVICE_RETRIES_BACKOFF = 0

LOG_LEVEL = 'DEBUG'
LOGGER_NAME = 'service'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(env)s %(service)s %(handler)s %(requestId)s '
                      '%(message)s'
        },
    },
    'handlers': {
        'local_internal': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        LOGGER_NAME: {
            'handlers': ['local_internal'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    }
}
