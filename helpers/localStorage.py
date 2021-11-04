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
        self.storage['unsync_step_count'] = self.queryUnsavedStepsCount()
        self.storage['unsync_steps'] = self.queryUnsavedSteps()
        self.storage['last_login_user'] = self.queryLastLoginUser()

    # def getConf(self):
    #     return self.conf

    def getStorage(self):
        return self.storage

    def queryUnsavedStepsCount(self):
        PhLogging().console().debug('query unsave steps count')
        self.cur.execute(PhSQLQueryBuilder().local_queryUnsavedCount())
        tails = self.cur.fetchall()
        return tails[0][0]

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

    def afterSyncUnsavedSteps(self):
        PhLogging().console().debug('after sync unsaved steps')
        self.cur.execute(PhSQLQueryBuilder().local_clearUnsavedEidt())
        self.cx.commit()

    def queryLastLoginUser(self):
        PhLogging().console().debug('query laster login user')
        self.cur.execute(PhSQLQueryBuilder().local_createLastLoginUser())
        self.cx.commit()

        self.cur.execute(PhSQLQueryBuilder().local_queryLastLoginUser())
        tails = self.cur.fetchall()
        if len(tails) == 0:
            return ''
        else:
            return tails[0][0]

    def pushLastLoginUser(self, uid):
        PhLogging().console().debug('push last login user')
        PhLogging().console().debug(uid)
        self.cur.execute(PhSQLQueryBuilder().local_pushLastLoginUser(uid))
        self.cx.commit()
