from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
import http.client
import json
from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging
import re
import traceback


class PhQueryCondiModel(QAbstractTableModel):
    signal_data_mod = pyqtSignal(str)
    signal_no_data = pyqtSignal()
    """
    表格数据模型MVC模式
    """
    def __init__(self):
        super(PhQueryCondiModel, self).__init__()
        # self._headers = PhAppConfig().getConf()['condi_schema']
        self._headers = PhAppConfig().getConf()['condi_schema_local']
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
            if index.column() < 3:
                value = self._data[index.row()][index.column()]
            else:
                condi = self._data[index.row()][2]
                min, max = self.condi2IndexRange(condi)
                if index.column() == self._headers.index("min"):
                    value = min
                else:
                    value = max
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
        # if index.column() == self._headers.index('condi'):
        if (index.column() == int(self._headers.index('min'))) | \
            (index.column() == int(self._headers.index('max'))):
            flags = flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        try:
            if index.isValid() and 0 <= index.row() < len(self._data) and value:
                col = index.column()
                col_condi = self._headers.index('condi')
                val_min, val_max = self.condi2IndexRange(self._data[index.row()][col_condi])
                if col == self._headers.index('min'):
                    val_min = int(value)
                else:
                    val_max = int(value)
                re_condi = self.IndexRange2Condi(val_min, val_max)

                if 0 < col < len(self._headers):
                    self.beginResetModel()
                    # self._data[index.row()][col] = value
                    self._data[index.row()][col_condi] = re_condi
                    self.endResetModel()
                    PhAppConfig().condi[index.row()][col_condi] = re_condi
                    PhLogging().console().debug(PhAppConfig().condi)
                    return True
            else:
                return False
        except Exception as e:
            PhLogging().console().debug(e.args)
            PhLogging().console().debug('============>')
            PhLogging().console().debug(traceback.format_exc())
            return False

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
        if min > 0:
            result.append('Index >= ' + str(min))

        if max > 0:
            result.append('Index < ' + str(max))

        if len(result) > 0:
            return ' and '.join(result)
        else:
            return 'Index == -1'
