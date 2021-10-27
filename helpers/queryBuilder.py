from helpers.appConfig import PhAppConfig
from helpers.singleton import singleton


@singleton
class PhSQLQueryBuilder(object):
    filters = []
    sorts = ''
    tableName = ''
    step = 1000
    skip = 0

    def __init__(self):
        self.tableName = 'prod_clean'
        self.sorts = 'Index'

    def querySelectSQL(self):
        sql = "select " + ','.join(PhAppConfig().getConf()['defined_schema']) + \
              " from " + self.tableName
        if len(self.filters) > 0:
            sql = sql + " where " + ' and '.join(self.filters)
        sql = sql + " order by " + self.sorts + " limit " + str(self.step) + " offset " + str(self.skip)
        return sql
