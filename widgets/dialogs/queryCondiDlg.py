from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy

from helpers.appConfig import PhAppConfig
from model.queryCondiModel import PhQueryCondiModel


class PhQueryCandiDlg(QDialog):
    signal_change_candi = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tableView = QTableView()
        model = PhQueryCondiModel()
        model.updateData(PhAppConfig().condi)
        self.tableView.setModel(model)

        ml = QVBoxLayout()
        ml.addWidget(self.tableView)
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton()
        cancel_btn.setText('取消')
        summit_btn = QPushButton()
        summit_btn.setText('更新')
        btn_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(summit_btn)
        ml.addItem(btn_layout)

        cancel_btn.clicked.connect(self.on_cancel_btn_click)
        summit_btn.clicked.connect(self.on_summit_btn_click)

        self.setLayout(ml)

    def on_cancel_btn_click(self):
        self.deleteLater()
        pass

    def on_summit_btn_click(self):
        self.signal_change_candi.emit()
        self.deleteLater()
        pass

    def sizeHint(self):
        return QSize(1000, 500)
