# -*- coding:utf-8 -*-

from helpers.singleton import singleton
import tailer
import os
import json

@singleton
class PhAppConfig(object):
    condi = []

    def __init__(self):
        self.conf = {}
        self.queryDefinedSchemas()
        self.conf['unsync_step_count'] = self.queryUnsavedStepsCound()
        self.conf['unsync_steps'] = self.queryUnsavedSteps()
        self.conf['last_login_user'] = self.queryLastLoginUser()

    def getConf(self):
        return self.conf

    def queryUnsavedStepsCound(self):
        if not os.path.exists('./logs/count_logs.out'):
            return 0
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/count_logs.out'), 1))
            tails.reverse()
            if len(tails) == 0:
                return 0
            else:
                return int(tails[0])

    def queryUnsavedSteps(self):
        if not os.path.exists('./logs/op_logs.out'):
            return []
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/op_logs.out', encoding='unicode_escape'), self.conf['unsync_step_count']))
            tails.reverse()
            # tails = tails[1:]
            tails = list(map(lambda x: x.encode('unicode_escape').decode('utf-8').split('\t'), tails))
            tmp = []
            result = []
            for item in tails:
                if item[0] not in tmp:
                    tmp.append(item[0])
                    result.append(item)
            self.conf['unsync_steps_index'] = tmp
            return result

    def queryDefinedSchemas(self):
        f = open('./config/projectDataConfig.json')
        tmp = json.loads(f.read(1024))
        self.conf['defined_schema'] = tmp['schema']
        self.conf['condi_schema'] = tmp['condi_schema']

    def queryLastLoginUser(self):
        if not os.path.exists('./logs/user_logs.out'):
            return None
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/user_logs.out'), 1))
            tails.reverse()
            if len(tails) == 0:
                return None
            else:
                return tails[0]

    def configClear(self):
        self.condi = []
        self.conf = {}

    def isAdmin(self):
        return self.getConf()['scope'] == '*'

    def isTmpUser(self):
        return not self.isAdmin()

    def filterEmpty(self, lst):
        return list(filter(lambda x: x != '', lst))
