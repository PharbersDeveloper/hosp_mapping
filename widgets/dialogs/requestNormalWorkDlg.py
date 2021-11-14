from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel, \
    QMessageBox

from helpers.appConfig import PhAppConfig
from helpers.localStorage import PhLocalStorage
from helpers.phLogging import PhLogging


class PhRequestNormalWorkDlg(QDialog):
    signal_change_candi = pyqtSignal()
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
        # self.signal_change_candi.emit()
        # self.deleteLater()
        # 1. 看有没有需要再次同步的数据
        # TODO: 这个地方不对, 不是未同步的是未做的
        if PhLocalStorage().getStorage()['unsync_step_count'] > 0:
            QMessageBox.warning(self, '错误', '你有未完成的工作，请做完工作在认领新工作，如有疑问，请联系管理员')
            return

        # 2. 查找没有被分配的最大的Index
        startIdx = PhAppConfig().findMaxRequestIndex()
        PhLogging().console().debug(startIdx)

        # 3. 更新Condi
        endIdx = startIdx + self.g_request_step
        for item in PhAppConfig().condi:
            if item[0] == PhAppConfig().getConf()['userId']:
                item[2] = PhAppConfig().IndexRange2Condi(startIdx, endIdx)
                break

        PhLogging().console().debug(PhAppConfig().condi)
        self.signal_change_candi.emit()

        self.deleteLater()

    def sizeHint(self):
        return QSize(500, 500)
