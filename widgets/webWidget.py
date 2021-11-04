
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from helpers.phLogging import PhLogging


class PhWebWidget(QWebEngineView):
    def createWindow(self, QWebEnginePage_WebWindowType):
        if QWebEnginePage_WebWindowType == QWebEnginePage.WebBrowserTab:
            self.newWeb = PhWebWidget(self)
            # self.newWeb = MyWebView()  # 不认self为父，就会在新窗口显示，认self作父就能在当前窗口显示
            self.newWeb.setAttribute(Qt.WA_DeleteOnClose, True)  # 加上这个属性能防止Qt Qtwebengineprocess进程关不掉导致崩溃
            self.newWeb.setGeometry(QtCore.QRect(0, 0, 300, 150))
            self.newWeb.show()
            self.newWeb.urlChanged.connect(self.on_url_changed)
            return self.newWeb
        return super(PhWebWidget, self).createWindow(QWebEnginePage_WebWindowType)

    def on_url_changed(self, url):
        PhLogging().console().debug('child url change')
        self.setUrl(url)
        self.newWeb.urlChanged.disconnect()
        self.newWeb.close()
        self.newWeb = None
