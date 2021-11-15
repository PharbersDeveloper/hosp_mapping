import re

from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal, QModelIndex
import http.client
import json
from helpers.appConfig import PhAppConfig
import datetime
from helpers.phLogging import PhLogging


class PhHospModel(QAbstractTableModel):
    signal_data_mod = pyqtSignal(str)
    signal_no_data = pyqtSignal()
    signal_all_data = pyqtSignal()
    isQc = False
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

    def appendData(self, data):
        """
        (自定义)追加数据
        """
        self.beginResetModel()
        self._data = self._data + data
        if len(data) == 0:
            self.signal_all_data.emit()
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
        if self.isQc:
            if self._headers[index.column()] in PhAppConfig().getConf()['qc_can_change_cols']:
                flags = flags | Qt.ItemIsEditable
        else:
            if self._headers[index.column()] in PhAppConfig().getConf()['can_change_cols']:
                flags = flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        # 编辑后更新模型中的数据 View中编辑后，View会调用这个方法修改Model中的数据
        value = value.replace("\t", "")
        if not self.isQc:
            lop_col = PhAppConfig().getConf()['defined_schema'].index('lop')
            ltm_col = PhAppConfig().getConf()['defined_schema'].index('ltm')
            if index.isValid() and 0 <= index.row() < len(self._data) and value:
                col = index.column()
                if 0 < col < len(self._headers):
                    self.beginResetModel()
                    self._data[index.row()][col] = value
                    self._data[index.row()][lop_col] = PhAppConfig().getConf()['displayName']
                    self._data[index.row()][ltm_col] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.endResetModel()
                    self.signal_data_mod.emit('\t'.join(self._data[index.row()]))
                    return True
            else:
                return False
        else:
            cop_col = PhAppConfig().getConf()['defined_schema'].index('cop')
            ctm_col = PhAppConfig().getConf()['defined_schema'].index('ctm')
            if index.isValid() and 0 <= index.row() < len(self._data) and value:
                col = index.column()
                if 0 < col < len(self._headers):
                    self.beginResetModel()
                    self._data[index.row()][col] = value
                    self._data[index.row()][cop_col] = PhAppConfig().getConf()['displayName']
                    self._data[index.row()][ctm_col] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.endResetModel()
                    self.signal_data_mod.emit('\t'.join(self._data[index.row()]))
                    return True
            else:
                return False

    def isRequestJobDone(self):
        try:
            check_cols = PhAppConfig().getConf()['non_null_cols']
            schema = PhAppConfig().getConf()['define_schema']
            idnices = []
            for iter in check_cols:
                idnices.append(schema.index(iter))

            for item in self._data:
                for check_idx in idnices:
                    if item[check_idx] == '':
                        raise Exception()
            return True
        except Exception as e:
            return False
