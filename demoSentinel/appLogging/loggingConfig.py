'''Define logging configuration'''

import logging
import time

#configure a logging.Formatter class to make sure this logs utc
class UtcFormatter(logging.Formatter):
    '''A class to override the logging.Formatter converter to use utc'''
    converter = time.gmtime

loggingConfig = {
    'version': 1,
    'formatters': {
        'default': {
            '()': UtcFormatter,
            'format': '%(asctime)s [%(levelname)s] %(module)s %(lineno)4d: %(message)s',
            'datefmt': '%Y%m%dT%H%M%S'
            }
        },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
            },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default'
            }
        },
    'loggers': {
        '': {
            'handlers': ['console','file'],
            'level': 'DEBUG',
            'propogate': True
            }
        }
        
}