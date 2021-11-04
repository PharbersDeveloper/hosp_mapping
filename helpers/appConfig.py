# -*- coding:utf-8 -*-
from helpers.phLogging import PhLogging
from helpers.singleton import singleton
import tailer
import os
import json
import sqlite3


@singleton
class PhAppConfig(object):
    condi = []

    def __init__(self):
        self.conf = {}
        self.queryDefinedSchemas()
        self.conf['unsync_step_count'] = self.queryUnsavedStepsCount()
        self.conf['last_login_user'] = self.queryLastLoginUser()

    def getConf(self):
        return self.conf

    def queryUnsavedStepsCount(self):
        if not os.path.exists('./logs/count_logs.out'):
            return 0
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/count_logs.out', encoding='utf-8'), 1))
            tails.reverse()
            if len(tails) == 0:
                return 0
            else:
                return int(tails[0])

    def queryDefinedSchemas(self):
        f = open('./config/projectDataConfig.json')
        tmp = json.loads(f.read(1024))
        self.conf['defined_schema'] = tmp['schema']
        self.conf['condi_schema'] = tmp['condi_schema']
        self.conf['trans_schema'] = tmp['trans_schema']
        self.conf['table'] = tmp['table']
        self.conf['count_condi'] = tmp['count_condi']
        self.conf['can_change_cols'] = tmp['can_change_cols']

    def queryLastLoginUser(self):
        if not os.path.exists('./logs/user_logs.out'):
            return None
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/user_logs.out', encoding='utf-8'), 1))
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
