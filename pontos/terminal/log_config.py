import sys
import logging
from logging.config import dictConfig

logging_config = dict(
    version=1,
    formatters={
        'verbose': {
            'format': ("[%(asctime)s] %(message)s"),
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    handlers={
        'process-logger': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'level': logging.DEBUG,
            'filename': 'process.log',
            'maxBytes': 52428800,
            'backupCount': 7,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': sys.stderr,
        },
    },
    loggers={
        'process_logger': {
            'handlers': ['process-logger'],
            'level': logging.DEBUG,
        }
    },
)

dictConfig(logging_config)

process_logger = logging.getLogger('process_logger')
