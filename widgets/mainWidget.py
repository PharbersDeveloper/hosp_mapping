from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView
from model.hospModel import PhHospModel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from helpers.appConfig import PhAppConfig


class PhMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tableView = QTableView()
        model = PhHospModel()
        self.tableView.setModel(model)

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
        conf = PhAppConfig()
        return self.getConf()['scope'] == '*'

    def isTmpUser(self):
        conf = PhAppConfig()
        return ~self.isAdmin()
