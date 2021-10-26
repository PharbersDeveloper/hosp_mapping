from helpers.singleton import singleton
import tailer
import os

@singleton
class PhAppConfig(object):
    def __init__(self):
        self.conf = {}
        self.conf['unsync_step_count'] = self.queryUnsavedStepsCound()

    def getConf(self):
        return self.conf

    def queryUnsavedStepsCound(self):
        if ~os.path.exists('./logs/count_logs.out'):
            return 0
        else:
            tails = tailer.tail(open('./logs/count_logs.out'), 1)
            if len(tails) == 0:
                return 0
            else:
                return int(tails[0])
