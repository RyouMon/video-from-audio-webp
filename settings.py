
THREAD_QUEUE_SIZE = 10000

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'pipelines.log',
            'level': 'DEBUG',
            'encoding': 'utf-8',
            'formatter': 'basic',
        },
    },
    'loggers': {
        'maker': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
    'formatters': {
        'basic': {
            'style': '{',
            'format': '{asctime:s}:{levelname:s}:{name:s}:{message:s}',
        },
    },
}
