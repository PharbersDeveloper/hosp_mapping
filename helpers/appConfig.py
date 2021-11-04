# -*- coding:utf-8 -*-
from helpers.singleton import singleton
import json


@singleton
class PhAppConfig(object):
    condi = []

    def __init__(self):
        self.conf = {}
        self.queryDefinedSchemas()

    def getConf(self):
        return self.conf

    def queryDefinedSchemas(self):
        f = open('./config/projectDataConfig.json', encoding='utf-8')
        tmp = json.loads(f.read(1024))
        self.conf['defined_schema'] = tmp['schema']
        self.conf['condi_schema'] = tmp['condi_schema']
        self.conf['trans_schema'] = tmp['trans_schema']
        self.conf['table'] = tmp['table']
        self.conf['count_condi'] = tmp['count_condi']
        self.conf['can_change_cols'] = tmp['can_change_cols']

    def configClear(self):
        self.condi = []
        self.conf = {}

    def isAdmin(self):
        return self.getConf()['scope'] == '*'

    def isTmpUser(self):
        return not self.isAdmin()

    def filterEmpty(self, lst):
        return list(filter(lambda x: x != '', lst))
