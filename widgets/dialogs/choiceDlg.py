from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel

from helpers.appConfig import PhAppConfig
from model.queryCondiModel import PhQueryCondiModel


class PhChoiceDlg(QDialog):
    signal_normal_work = pyqtSignal()
    signal_qc_work = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        label = QLabel("Choose your work type")
        ml = QVBoxLayout()
        ml.addWidget(label)
        btn_layout = QHBoxLayout()
        normal_btn = QPushButton()
        normal_btn.setText('normal')
        qc_btn = QPushButton()
        qc_btn.setText('qc')
        # btn_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        btn_layout.addWidget(normal_btn)
        btn_layout.addWidget(qc_btn)
        ml.addItem(btn_layout)

        normal_btn.clicked.connect(self.on_normal_btn_click)
        qc_btn.clicked.connect(self.on_qc_btn_click)

        self.setLayout(ml)

    def on_normal_btn_click(self):
        self.signal_normal_work.emit()

    def on_qc_btn_click(self):
        self.signal_qc_work.emit()
