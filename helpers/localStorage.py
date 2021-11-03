# -*- coding:utf-8 -*-
from helpers.phLogging import PhLogging
from helpers.queryBuilder import PhSQLQueryBuilder
from helpers.singleton import singleton
import sqlite3


@singleton
class PhLocalStorage(object):
    # condi = []

    def __init__(self):
        self.storage = {}
        self.cx = sqlite3.connect('./logs/operations.db')
        self.cx.execute(PhSQLQueryBuilder().local_createIfExist())
        self.cur = self.cx.cursor()
        self.storage['unsync_steps'] = self.queryUnsavedSteps()

    # def getConf(self):
    #     return self.conf

    def getStorage(self):
        return self.storage

    def queryUnsavedSteps(self):
        PhLogging().console().debug('loading unsaved steps')
        self.storage['unsync_steps_index'] = []
        self.cur.execute(PhSQLQueryBuilder().local_queryUnsavedEdit())
        tails = self.cur.fetchall()
        tmp = []
        result = []
        for item in tails:
            if item[0] not in tmp:
                tmp.append(str(item[0]))
                result.append(list(item))
        self.storage['unsync_steps_index'] = tmp
        return result

    def pushUnsavedStep(self, value):
        self.cur.execute(PhSQLQueryBuilder().local_pushUnsavedEdit(value))
        self.cx.commit()
