from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
import http.client
import json
from helpers.appConfig import PhAppConfig
import datetime
from helpers.phLogging import PhLogging


class PhHospModel(QAbstractTableModel):
    signal_data_mod = pyqtSignal(str)
    signal_no_data = pyqtSignal()
    """
    表格数据模型MVC模式
    """
    def __init__(self):
        super(PhHospModel, self).__init__()
        self._headers = PhAppConfig().getConf()['trans_schema']
        self._data = []
        # self.updateData(self.refreshQueryData())

    def updateData(self, data):
        """
        (自定义)更新数据
        """
        self.beginResetModel()
        self._data = data
        if len(data) == 0:
            self.signal_no_data.emit()
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
        flags = super(PhHospModel, self).flags(index)
        if self._headers[index.column()] in PhAppConfig().getConf()['can_change_cols']:
            flags = flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        # 编辑后更新模型中的数据 View中编辑后，View会调用这个方法修改Model中的数据
        op_col = len(PhAppConfig().getConf()['defined_schema']) - 2
        tm_col = op_col + 1
        if index.isValid() and 0 <= index.row() < len(self._data) and value:
            col = index.column()
            if 0 < col < len(self._headers):
                self.beginResetModel()
                self._data[index.row()][col] = value
                self._data[index.row()][op_col] = PhAppConfig().getConf()['displayName']
                self._data[index.row()][tm_col] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.endResetModel()
                self.signal_data_mod.emit('\t'.join(self._data[index.row()]))
                return True
        else:
            return False
