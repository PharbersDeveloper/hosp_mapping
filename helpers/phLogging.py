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

    def userfile(self):
        return logging.getLogger('userLog')

    def check_nun_values(self,data):
        flag = True
        for item in data:
            if '' in item[7:12]:
                flag = False
                break
        return flag






