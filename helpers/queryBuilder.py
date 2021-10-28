from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging
from helpers.singleton import singleton


@singleton
class PhSQLQueryBuilder(object):
    filters = []
    sorts = ''
    tableName = ''
    step = 1000
    skip = 0
    condi_table = ''

    def __init__(self):
        self.tableName = 'prod_clean'
        self.condi_table = 'prod_partition_condi'
        self.sorts = 'Index'

    def querySelectSQL(self):
        sql = "select " + ','.join(PhAppConfig().getConf()['defined_schema']) + \
              " from " + self.tableName
        if len(self.filters) > 0:
            sql = sql + " where " + ' and '.join(self.filters)
        sql = sql + " order by " + self.sorts + " limit " + str(self.step) + " offset " + str(self.skip)
        return sql

    def alertDeleteSQL(self):
        del_sql = 'alter table prod_clean delete where Index in [' + \
                  ','.join(PhAppConfig().getConf()['unsync_steps_index']) + \
                  '];'
        PhLogging().console().debug(del_sql)
        return del_sql

    def alertInsertMultiSQL(self):
        ist_sql = "insert into prod_clean (Index, Id, Hospname, Level, Address, lchange, lop, ltm) VALUES "
        item_insert_lst = []
        for item in PhAppConfig().getConf()['unsync_steps']:
            tmp_sql = "("
            for i, tmp in enumerate(item):
                if i == 0:
                    tmp_sql = tmp_sql + tmp
                else:
                    tmp_sql = tmp_sql + ","
                    tmp_sql = tmp_sql + "'" + tmp + "'"
            tmp_sql = tmp_sql + ")"
            item_insert_lst.append(tmp_sql)
        ist_sql = ist_sql + ','.join(item_insert_lst) + ';'
        PhLogging().console().debug(ist_sql)
        return ist_sql

    def queryCondiSQL(self):
        if PhAppConfig().getConf()['scope'] != '*':
            return "select * from prod_partition_condi where uid='" + PhAppConfig().getConf()['userId'] + "';"
        else:
            return "select * from prod_partition_condi;"

    def deleteAllCandi(self):
        return "alter table prod_partition_condi delete where uid !=''"

    def alterAllCandi(self):
        ist_sql = "insert into prod_partition_condi (uid, uname, condi) VALUES "
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
        return "select count(*) from prod_clean"

    def queryProgressCountSQL(self):
        return "select count(*) from prod_clean where lchange=''"
