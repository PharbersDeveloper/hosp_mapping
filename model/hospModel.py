from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
import http.client
import json
from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging


class PhHospModel(QAbstractTableModel):
    signal_data_mod = pyqtSignal(str)
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

    def setData(self, index, value, role=Qt.EditRole):
        # 编辑后更新模型中的数据 View中编辑后，View会调用这个方法修改Model中的数据
        if index.isValid() and 0 <= index.row() < len(self._data) and value:
            col = index.column()
            if 0 < col < len(self._headers):
                self.beginResetModel()
                self._data[index.row()][col] = value
                self.endResetModel()
                self.signal_data_mod.emit('\t'.join(self._data[index.row()]))
                return True
        else:
            return False
