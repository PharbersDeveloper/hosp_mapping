# -*- coding:utf-8 -*-
from helpers.phLogging import PhLogging
from helpers.singleton import singleton
import json
from config.projectDataConfig import project_default_conf
import re
from functools import reduce


@singleton
class PhAppConfig(object):
    condi = []

    def __init__(self):
        self.conf = {}
        self.queryDefinedSchemas()

    def getConf(self):
        return self.conf

    def queryDefinedSchemas(self):
        # Bug: windows 可能出现的编码问题，现在把所有的文件读取全部去掉
        # f = open('./config/projectDataConfig.json', encoding='utf-8')
        # tmp = json.loads(f.read(4096))
        tmp = project_default_conf
        self.conf['defined_schema'] = tmp['schema']
        self.conf['condi_schema'] = tmp['condi_schema']
        self.conf['condi_schema_local'] = tmp['condi_schema_local']
        self.conf['trans_schema'] = tmp['trans_schema']
        self.conf['table'] = tmp['table']
        self.conf['count_condi'] = tmp['count_condi']
        self.conf['can_change_cols'] = tmp['can_change_cols']
        self.conf['non_null_cols'] = tmp['non_null_cols']
        self.conf['qc_can_change_cols'] = tmp['qc_can_change_cols']

    def configClear(self):
        self.condi = []
        self.conf = {}

    def isAdmin(self):
        return self.getConf()['scope'] == '*'

    def isTmpUser(self):
        return not self.isAdmin()

    def filterEmpty(self, lst):
        return list(filter(lambda x: x != '', lst))

    def condi2IndexRange(self, condi):
        regex = r"\d+"
        matches = re.finditer(regex, condi, re.MULTILINE)
        result = []
        for matchNum, match in enumerate(matches, start=1):
            result.append(int(match.group()))

        if len(result) > 1:
            return min(result), max(result)
        elif len(result) == 1:
            return min(result), -1
        else:
            return -1, -1

    def IndexRange2Condi(self, min, max):
        result = []
        if min >= 0:
            result.append('Index >= ' + str(min))

        if max >= 0:
            result.append('Index < ' + str(max))

        if len(result) > 0:
            return ' and '.join(result)
        else:
            return 'Index == -1'

    def findMaxRequestIndex(self):
        all_indices = list(map(lambda x: list(self.condi2IndexRange(x[2])), self.condi))
        all_indices = reduce(lambda x, y: x + y, all_indices)
        return max(all_indices)
