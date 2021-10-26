from PyQt5.QtCore import Qt, QAbstractTableModel
import http.client
import json
from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging


class PhHospModel(QAbstractTableModel):
    """
    表格数据模型MVC模式
    """
    def __init__(self):
        super(PhHospModel, self).__init__()
        self._headers = ['Index', 'Id', 'Hospname', 'Level', 'Address', 'lop', 'ltm']
        self._data = []
        self.updateData(self.refreshQueryData())

    def refreshQueryData(self):
        parameters = {
            'query': "select * from prod_clean limit 1000",
            'schema': self._headers
        }
        conf = PhAppConfig()
        conn = http.client.HTTPSConnection("api.pharbers.com")
        payload = json.dumps(parameters)
        PhLogging().console().debug(conf.getConf()['access_token'])
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
            return list(map(self.serverDataAdapter, result))
        else:
            error = {'message': 'query db error'}
            conn.close()
            return error

    def serverDataAdapter(self, item):
        return [item['Index'], item['Id'], item['Hospname'], item['Level'], item['Address'], item['lop'], item['ltm']]

    def updateData(self, data):
        """
        (自定义)更新数据
        """
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            return value

        if role == Qt.DecorationRole:
            pass

    def rowCount(self, parent=None, *args, **kwargs):
        """
        行数
        """
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        """
        列数
        """
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        标题定义
        """
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return int(section + 1)

    def flags(self, index):
        return super(PhHospModel, self).flags(index) | Qt.ItemIsEditable
