from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel, QLineEdit

from helpers.appConfig import PhAppConfig
from model.queryCondiModel import PhQueryCondiModel


class PhQueryQcFilterCondiDlg(QDialog):
    signal_change_qc_condi = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        ml = QVBoxLayout()

        who_filter_layout = QHBoxLayout()
        who_eq_label = QLabel("who do it")
        who_ed = QLineEdit()
        who_filter_layout.addWidget(who_eq_label)
        who_filter_layout.addWidget(who_ed)

        time_filter_layout = QHBoxLayout()
        time_eq_label = QLabel("time to do it")
        time_ed = QLineEdit()
        time_filter_layout.addWidget(time_eq_label)
        time_filter_layout.addWidget(time_ed)

        btn_layout = QHBoxLayout()
        summit_btn = QPushButton("summit")
        cancel_btn = QPushButton("cancel")
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
        self.signal_change_qc_condi.emit()
        self.deleteLater()

    def on_cancel_btn_click(self):
        self.deleteLater()
