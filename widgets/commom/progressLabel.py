from PyQt5.QtWidgets import QLabel

from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging
from helpers.queryBuilder import PhSQLQueryBuilder
import http.client
import json


class PhProgressLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refreshProgress()

    def refreshProgress(self):
        total = self.queryDatabaseData(PhSQLQueryBuilder().queryTotalCountSQL())
        progress = self.queryDatabaseData(PhSQLQueryBuilder().queryProgressCountSQL())
        self.setText('当前进度: {0} / {1}'.format(progress, total))

    def conuntAdapter(self, item):
        return int(item[0]['count'])

    def queryDatabaseData(self, sql):
        parameters = {
            # 'query': "select * from prod_clean order by Index limit 1000",
            'query': sql,
            'schema': ['count']
        }
        PhLogging().console().debug(parameters)
        conf = PhAppConfig()
        conn = http.client.HTTPSConnection("api.pharbers.com")
        payload = json.dumps(parameters)
        headers = {
            'Authorization': conf.getConf()['access_token'],
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        conn.request("POST", "/phchproxyquery", payload, headers)
        res = conn.getresponse()

        if (res.status == 200) & (res.reason == 'OK'):
            login_data = res.read().decode('utf-8')
            result = json.loads(login_data)
            conn.close()
            return self.conuntAdapter(result)
            # return list(map(self.serverDataAdapter, result))
        else:
            error = res.read().decode('utf-8')
            PhLogging().console().debug(error)
            conn.close()
            return 0
