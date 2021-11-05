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

    # def check_nun_values(self,data):
    #     for i in data:
    #         if '' in data[7:12]:
    #             return False
    #     else:
    #         pass
    #     return






