from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel


class PhRequestNormalWorkDlg(QDialog):
    signal_request_change_candi = pyqtSignal(int)
    g_request_step = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupLayout()

    def setupLayout(self):
        label = QLabel('你将继续向后申请100条数据')

        ml = QVBoxLayout()
        ml.addWidget(label)
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton()
        cancel_btn.setText('取消申请')
        summit_btn = QPushButton()
        summit_btn.setText('确认申请')
        btn_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(summit_btn)
        ml.addItem(btn_layout)

        cancel_btn.clicked.connect(self.on_cancel_btn_click)
        summit_btn.clicked.connect(self.on_summit_btn_click)

        self.setLayout(ml)

    def on_cancel_btn_click(self):
        self.deleteLater()

    def on_summit_btn_click(self):
        self.signal_request_change_candi.emit(self.g_request_step)
        self.deleteLater()

    def sizeHint(self):
        return QSize(500, 500)
