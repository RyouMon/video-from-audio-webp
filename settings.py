DEBUG = False

PIPELINES = [
    'pipelines.background.SocialMediaBlackBackgroundPipeline',
    'pipelines.slideshow.SlideShowPipeline',
    'pipelines.masking.MaskingPipeline',
    'pipelines.text.ContinuousTextPipeline',
    'pipelines.text.SubtitlePipeline',
]

OVERWRITE_OUTPUT = True

FPS = 10

THREAD_QUEUE_SIZE = 1000000

DEFAULT_FONT_FILE = 'sample_files/msyh.ttc'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
