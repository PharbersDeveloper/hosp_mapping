import re

from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging
from helpers.singleton import singleton
import uuid


@singleton
class PhSQLQueryBuilder(object):
    filters = []
    sorts = ''
    tableName = PhAppConfig().getConf()['table']
    count_condi = PhAppConfig().getConf()['count_condi']
    step = 1000
    skip = 0
    condi_table = ''

    def __init__(self):
        self.sorts = 'Index'

    def nextPage(self):
        self.skip = self.skip + self.step

    def revertToBasePage(self):
        self.skip = 0

    def querySelectSQL(self):
        sql = "select " + ','.join(PhAppConfig().getConf()['defined_schema']) + \
              " from " + self.tableName
        if len(self.filters) > 0:
            sql = sql + " where " + ' and '.join(self.filters)
        sql = sql + " order by " + self.sorts + " limit " + str(self.step) + " offset " + str(self.skip)
        return sql

    def alertDeleteSQL(self, indices):
        del_sql = 'alter table ' + self.tableName + ' delete where Index in [' + \
                  ','.join(indices) + \
                  '];'
        PhLogging().console().debug(del_sql)
        return del_sql

    def alertInsertMultiSQL(self, unsync_steps):
        ist_sql = "insert into " + self.tableName + " (" + ','.join(PhAppConfig().getConf()['defined_schema']) + ") VALUES "
        item_insert_lst = []
        for item in unsync_steps:
            tmp_sql = "("
            for i, tmp in enumerate(item):
                if i == 0:
                    tmp_sql = tmp_sql + str(tmp)
                else:
                    tmp_sql = tmp_sql + ","
                    tmp_sql = tmp_sql + "'" + tmp + "'"
            tmp_sql = tmp_sql + ")"
            item_insert_lst.append(tmp_sql)
        ist_sql = ist_sql + ','.join(item_insert_lst) + ';'
        PhLogging().console().debug(ist_sql)
        return ist_sql

    def queryCondiSQL(self, uid):
        return "select * from prod_partition_condi;"
        # if PhAppConfig().getConf()['scope'] != '*':
        #     return "select * from prod_partition_condi where uid='" + uid + "';"
        # else:
        #     return "select * from prod_partition_condi;"

    def deleteAllCandi(self):
        return "alter table prod_partition_condi delete where uid !=''"

    def alterAllCandi(self):
        ist_sql = "insert into prod_partition_condi (" + ','.join(PhAppConfig().getConf()['condi_schema']) + ") VALUES "
        item_insert_lst = []
        for item in PhAppConfig().condi:
            tmp_sql = "("
            for i, tmp in enumerate(item):
                if i == 0:
                    tmp_sql = tmp_sql + "'" + tmp + "'"
                else:
                    tmp_sql = tmp_sql + ","
                    tmp_sql = tmp_sql + "'" + tmp + "'"
            tmp_sql = tmp_sql + ")"
            item_insert_lst.append(tmp_sql)
        ist_sql = ist_sql + ','.join(item_insert_lst) + ';'
        PhLogging().console().debug(ist_sql)
        return ist_sql

    def queryTotalCountSQL(self):
        return "select count(*) from " + self.tableName

    def queryProgressCountSQL(self):
        return "select count(*) from " + self.tableName + " where " + self.count_condi

    def local_createIfExist(self):
        tmp = PhAppConfig().getConf()['defined_schema'].copy()
        tmp.append("TMPID")

        create_sql = "create table if not exists clean_operations ( " + \
                     " TEXT,".join(tmp).replace("Index", "Idx", 1) + " TEXT PRIMARY KEY);"
        # create_sql = "create table if not exists clean_operations ( " + \
        #     " TEXT,".join(tmp).replace("TEXT", "INT", 1).replace("Index", "Idx", 1) + " TEXT PRIMARY KEY);"
        PhLogging().console().debug(create_sql)
        return create_sql

    def local_queryUnsavedEdit(self):
        sql = "select " + ",".join(PhAppConfig().getConf()['defined_schema']) + \
            " from clean_operations order by ltm DESC " # + str(PhLocalStorage().getStorage()['unsync_step_count'])
        sql = sql.replace("Index", "Idx", 1)
        PhLogging().console().debug(sql)
        return sql

    def local_pushUnsavedEdit(self, value):
        tmp = PhAppConfig().getConf()['defined_schema'].copy()
        tmp.append("TMPID")
        tmp_sql = "insert into clean_operations (" + ",".join(tmp) + ") VALUES ("
        for i, tmp in enumerate(value.split('\t')):
            if i == 0:
                tmp_sql = tmp_sql + "'" + tmp + "'"
            else:
                tmp_sql = tmp_sql + ","
                tmp_sql = tmp_sql + "'" + tmp + "'"
        tmp_sql = tmp_sql + "," + "'" + str(uuid.uuid4()) + "'" + ");"
        tmp_sql = tmp_sql.replace("Index", "Idx", 1)
        PhLogging().console().debug(tmp_sql)
        return tmp_sql

    def local_clearUnsavedEidt(self):
        return "delete from clean_operations WHERE TMPID!='';"

    def local_queryUnsavedCount(self):
        return "select count(*) from clean_operations WHERE TMPID!='';"

    def local_createLastLoginUser(self):
        create_sql = "create table if not exists last_user ( uid TEXT, id INT PRIMARY KEY)"
        PhLogging().console().debug(create_sql)
        return create_sql

    def local_queryLastLoginUser(self):
        sql = "select uid from last_user where id=1"
        PhLogging().console().debug(sql)
        return sql

    def local_pushLastLoginUser(self, uid):
        if uid == "":
            uid = str(uuid.uuid4())

        sql = "insert or replace into last_user ( uid, id ) VALUES ( '" + uid + "', 1);"
        PhLogging().console().debug(sql)
        return sql
