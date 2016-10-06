"""
Service settings
"""
AUTO_RELOAD = True
DEFAULT_PORT = 8888

REDIS_HOST = "redis"
REDIS_PORT = 6379
MEDIA_CACHE_TTL_SECONDS = 86400

STATS_ENABLED = False
STATS_SERVICE_HOSTNAME = "localhost"

INSTAGRAM_SERVICE_URL = 'https://api.instagram.com/v1'
INSTAGRAM_ACCESS_TOKEN = '3179077230.398a23d.4c96a4175eec4cfb957fff8daf02a52f'
INSTAGRAM_SERVICE_TIMEOUT = 5
INSTAGRAM_SERVICE_RETRIES = 3
INSTAGRAM_SERVICE_RETRIES_DELAY = 0
INSTAGRAM_SERVICE_RETRIES_BACKOFF = 0

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
