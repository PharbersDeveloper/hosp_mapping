from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QMessageBox

from helpers.phLogging import PhLogging
from ui.login import Ui_Form
from widgets.mainWidget import PhMainWidget
import http.client
import hashlib
from urllib.parse import urlencode
import json
from helpers.appConfig import PhAppConfig


class PhLoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.summitBtn.clicked.connect(self._summitBtn_Clicked)
        self.mw = None

    def _summitBtn_Clicked(self):
        userName = self.ui.userLineEdit.text()
        pwd = self.ui.pwdLineEdit.text()

        login_result = self.loginOAuthPwdRequest(userName, pwd)
        if (login_result['status'] == 200) & (login_result['reason'] == 'OK'):
            conf = PhAppConfig()
            conf.getConf()['access_token'] = login_result['access_token']
            conf.getConf()['refresh_token'] = login_result['refresh_token']
            conf.getConf()['expiresIn'] = login_result['expiresIn']
            conf.getConf()['scope'] = login_result['scope']
            conf.getConf()['userId'] = login_result['user']['id']
            conf.getConf()['displayName'] = login_result['user']['firstName'] + login_result['user']['lastName']
            PhLogging().console().debug(login_result)
            self.hide()
            if self.mw is None:
                self.mw = PhMainWidget()
            self.mw.showMaximized()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle('Login Failed!')
            dlg.setText('login failed')
            dlg.exec()

    def loginOAuthPwdRequest(self, userName, pwd):
        parameters = {
            'grant_type': 'password',
            'username': userName,
            'password': hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        }
        conn = http.client.HTTPSConnection("apiv2.pharbers.com")
        payload = urlencode(parameters)
        headers = {
            'Authorization': 'Basic NXFVZFJRYTlqMG40aG1KNzpiMmZmOTY0ZWExZTM5N2E4ZmZkNDMwMGIyNDY5ZmU0MWE0MWUxNTZmYTk5MzMyMDgxMTgxMDcwYjEwYTg3MWE0',
            'Accept': 'application/x-www-form-urlencoded',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        conn.request("POST", "/oauth/token", payload, headers)
        res = conn.getresponse()
        login_data = res.read().decode('utf-8')
        result = json.loads(login_data)
        result['status'] = res.status
        result['reason'] = res.reason

        conn.close()
        return result
