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
        self.cx = sqlite3.connect('./logs/operations.db')
        self.cx.execute("create table if not exists clean_operations ( Idx INT PRIMARY KEY,Id TEXT,Hospname TEXT,Level TEXT,Address TEXT,lchange TEXT,lop TEXT,ltm TEXT );")
        self.cur = self.cx.cursor()
        self.conf['unsync_step_count'] = self.queryUnsavedStepsCound()
        self.conf['unsync_steps'] = self.queryUnsavedSteps()
        self.conf['last_login_user'] = self.queryLastLoginUser()

    def getConf(self):
        return self.conf

    def queryUnsavedStepsCound(self):
        if not os.path.exists('./logs/count_logs.out'):
            return 0
        else:
            tails = self.filterEmpty(tailer.tail(open('./logs/count_logs.out', encoding='utf-8'), 1))
            tails.reverse()
            if len(tails) == 0:
                return 0
            else:
                return int(tails[0])

    def queryUnsavedSteps(self):
        PhLogging().console().debug('loading unsaved steps')
        self.conf['unsync_steps_index'] = []
        self.cur.execute("select * from clean_operations order by ltm DESC limit " + str(self.conf['unsync_step_count']))
        tails = self.cur.fetchall()
        tmp = []
        result = []
        for item in tails:
            if item[0] not in tmp:
                tmp.append(str(item[0]))
                result.append(list(item))
        self.conf['unsync_steps_index'] = tmp
        return result

    def pushUnsavedStep(self, value):
        PhLogging().console().debug(value)
        tmp_sql = "insert into clean_operations (Idx, Id, Hospname, Level, Address, lchange, lop, ltm) VALUES ("
        for i, tmp in enumerate(value.split('\t')):
            if i == 0:
                tmp_sql = tmp_sql + tmp
            else:
                tmp_sql = tmp_sql + ","
                tmp_sql = tmp_sql + "'" + tmp + "'"
        tmp_sql = tmp_sql + ")"
        PhLogging().console().debug(tmp_sql)
        self.cur.execute(tmp_sql)
        self.cx.commit()

    def queryDefinedSchemas(self):
        f = open('./config/projectDataConfig.json')
        tmp = json.loads(f.read(1024))
        self.conf['defined_schema'] = tmp['schema']
        self.conf['condi_schema'] = tmp['condi_schema']

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
