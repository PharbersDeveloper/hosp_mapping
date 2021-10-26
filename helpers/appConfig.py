from helpers.singleton import singleton


@singleton
class PhAppConfig(object):
    def __init__(self):
        self.conf = {}

    def getConf(self):
        return self.conf

