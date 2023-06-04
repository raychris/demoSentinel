'''Set up logging'''

import datetime
import logging
import logging.config
import os.path

from demoSentinel.appLogging.loggingConfig import loggingConfig

def enableLogging():
    '''Return a log object after setting up a logger'''
    nowUtc = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    if 'LOGDIR' in os.environ.keys():
        logDir = os.environ['LOGDIR']
    else:
        logDir = os.environ['HOME']
    loggingConfig['handlers']['file']['filename'] = os.path.join(logDir,''.join(['fbkChallenge','_',nowUtc,'.log']))
    logging.config.dictConfig(loggingConfig)
    log = logging.getLogger()
    return log