from datetime import datetime, timedelta

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, \
    QLabel, QLineEdit, QComboBox

from helpers.appConfig import PhAppConfig
from helpers.phLogging import PhLogging
from model.queryCondiModel import PhQueryCondiModel


class PhQueryQcFilterCondiDlg(QDialog):
    signal_change_qc_condi = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)

        ml = QVBoxLayout()

        who_filter_layout = QHBoxLayout()
        who_eq_label = QLabel("who do it")

        user_name_lst = ['杨渊']
        for item in PhAppConfig().condi:
            user_name_lst.append(item[1])
        self.who_ed = QComboBox()
        self.who_ed.addItems(user_name_lst)

        who_filter_layout.addWidget(who_eq_label)
        who_filter_layout.addWidget(self.who_ed)

        time_filter_layout = QHBoxLayout()
        time_eq_label = QLabel("time to do it")

        date_lst = []
        today = datetime.today()
        for idx in range(11):
            tmp = today + timedelta(days=(idx - 10))
            date_lst.append(tmp.strftime("%Y-%m-%d"))

        self.time_ed = QComboBox()
        date_lst.reverse()
        self.time_ed.addItems(date_lst)
        time_filter_layout.addWidget(time_eq_label)
        time_filter_layout.addWidget(self.time_ed)

        btn_layout = QHBoxLayout()
        summit_btn = QPushButton("summit")
        cancel_btn = QPushButton("clear condition")
        btn_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        btn_layout.addWidget(summit_btn)
        btn_layout.addWidget(cancel_btn)

        ml.addItem(who_filter_layout)
        ml.addItem(time_filter_layout)
        ml.addItem(btn_layout)

        summit_btn.clicked.connect(self.on_summit_btn_click)
        cancel_btn.clicked.connect(self.on_cancel_btn_click)

        self.setLayout(ml)

    def on_summit_btn_click(self):
        sql_where_condi = ["lop='" + self.who_ed.currentText() + "'", "ltm LIKE '%"+ self.time_ed.currentText() + "%'"]
        self.signal_change_qc_condi.emit(sql_where_condi)
        self.deleteLater()

    def on_cancel_btn_click(self):
        self.signal_change_qc_condi.emit([])
        self.deleteLater()
