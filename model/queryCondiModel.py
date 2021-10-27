from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
import http.client
import json
from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging


class PhQueryCondiModel(QAbstractTableModel):
    signal_data_mod = pyqtSignal(str)
    signal_no_data = pyqtSignal()
    """
    表格数据模型MVC模式
    """
    def __init__(self):
        super(PhQueryCondiModel, self).__init__()
        self._headers = PhAppConfig().getConf()['condi_schema']
        self._data = []

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

    def flags(self, index: QModelIndex):
        flags = super(PhQueryCondiModel, self).flags(index)
        if index.column() == self._headers.index('condi'):
            flags = flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        # 编辑后更新模型中的数据 View中编辑后，View会调用这个方法修改Model中的数据
        if index.isValid() and 0 <= index.row() < len(self._data) and value:
            col = index.column()
            if 0 < col < len(self._headers):
                self.beginResetModel()
                self._data[index.row()][col] = value
                self.endResetModel()
                PhAppConfig().condi[index.row()][col] = value
                return True
        else:
            return False
