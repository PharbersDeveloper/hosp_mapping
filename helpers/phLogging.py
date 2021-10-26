import logging
import logging.config
from helpers.singleton import singleton


@singleton
class PhLogging(object):
    def __init__(self):
        self.conf = {}
        logging.config.fileConfig('config/logging.conf')

    def console(self):
        return logging.getLogger()

    def opfile(self):
        return logging.getLogger('opLog')

    def countfile(self):
        return logging.getLogger('countLog')
