# -*- encoding: utf-8 -*-

# @File        :   logger.py
# @Time        :   2021/04/13 16:21:23
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")


class CustomFormatter(logging.Formatter):

    fmt = "%(asctime)-15s %(levelname)-8s %(message)s"

    def __init__(self) -> None:
        super(CustomFormatter, self).__init__(self.fmt)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': "%(asctime)-15s %(levelname)-8s %(module)s:%(funcName)s:%(lineno)d %(message)s"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "parser.log"),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 30,
            'formatter': 'default',
            'encoding': 'utf-8',
        },
        'warn': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "parser-warn.log"),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 30,
            'formatter': 'default',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "parser-error.log"),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 30,
            'formatter': 'default',
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'default', 'warn', 'error'],
            'level': 'INFO',
            # 'propagate': True,
        },
    },
}
