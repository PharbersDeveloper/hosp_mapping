from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView

from helpers.phLogging import PhLogging
from model.hospModel import PhHospModel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from helpers.appConfig import PhAppConfig


class PhMainWidget(QWidget):
    current_dy = 0
    last_dy = 0
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tableView = QTableView()
        model = PhHospModel()
        model.signal_data_mod.connect(self.on_data_modify)
        self.tableView.setModel(model)
        self.tableView.verticalScrollBar().valueChanged.connect(self.on_vertical_scrolled)

        self.wev = QWebEngineView()
        self.wev.load(QUrl('https://www.baidu.com'))

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tableView)
        self.mainLayout.addWidget(self.wev)
        self.setLayout(self.mainLayout)

    # event handler
    def keyPressEvent(self, event):
        key = event.key()
        handlers = {
            Qt.Key_F1: self.searchWithText
        }
        handler = handlers.get(key)
        if handler:
            select = self.tableView.currentIndex().data()
            handler(select)

    def searchWithText(self, msg):
        self.wev.load(QUrl('https://www.baidu.com/s?wd=' + msg))

    def isAdmin(self):
        return PhAppConfig().getConf()['scope'] == '*'

    def isTmpUser(self):
        return ~self.isAdmin()

    def on_data_modify(self, value):
        # 1. 添加log count
        print(PhAppConfig().getConf()['unsync_step_count'])
        PhAppConfig().getConf()['unsync_step_count'] = PhAppConfig().getConf()['unsync_step_count'] + 1
        PhLogging().countfile().info(PhAppConfig().getConf()['unsync_step_count'])
        # 2. 添加operation log
        PhLogging().opfile().info(value)
        self.tableView.verticalScrollBar().setValue(self.last_dy)

    def on_vertical_scrolled(self, dy):
        self.last_dy = self.current_dy
        self.current_dy = dy
