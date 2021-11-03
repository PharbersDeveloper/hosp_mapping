from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox

from helpers.localStorage import PhLocalStorage
from helpers.phLogging import PhLogging
from helpers.queryBuilder import PhSQLQueryBuilder
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

            # last_login_user = PhAppConfig().getConf()['last_login_user']
            last_login_user = PhLocalStorage().getStorage()['last_login_user']
            PhLogging().console().debug(last_login_user)
            PhLogging().console().debug(conf.getConf()['userId'])
            if (last_login_user is not None) and (last_login_user != conf.getConf()['userId']):
                if QMessageBox.question(self, "提问", "这次登录与上次登录的用户不一致，如果继续将丢失上个用户未同步的操作信息",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
                    PhLocalStorage().getStorage()['unsync_step_count'] = 0
                    # PhLogging().countfile().info(PhLocalStorage().getStorage()['unsync_step_count'])
                    PhLocalStorage().getStorage()['unsync_steps'] = []
                    PhLocalStorage().getStorage()['unsync_steps_index'] = []
                    PhLocalStorage().afterSyncUnsavedSteps()
                else:
                    return

            # PhLogging().userfile().info(PhLocalStorage().getStorage()['userId'])
            PhLocalStorage().pushLastLoginUser(conf.getConf()['userId'])
            self.appPrepareQueryCondi()
            self.hide()
            if self.mw is None:
                self.mw = PhMainWidget()
                self.mw.user_logout.connect(self.on_user_logout_event)
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

    def appPrepareQueryCondi(self):
        parameters = {
            'query': PhSQLQueryBuilder().queryCondiSQL(PhAppConfig().getConf()['userId']),
            'schema': PhAppConfig().getConf()['condi_schema']
        }
        PhLogging().console().debug(parameters)
        conf = PhAppConfig()
        conn = http.client.HTTPSConnection("api.pharbers.com")
        payload = json.dumps(parameters)
        headers = {
            'Authorization': conf.getConf()['access_token'],
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        conn.request("POST", "/phchproxyquery", payload, headers)
        res = conn.getresponse()

        if (res.status == 200) & (res.reason == 'OK'):
            login_data = res.read().decode('utf-8')
            result = json.loads(login_data)
            conn.close()
            PhAppConfig().condi = list(map(self.serverCondiAdapter, result))
            PhLogging().console().debug(PhAppConfig().condi)
            if PhAppConfig().isTmpUser():
                PhSQLQueryBuilder().filters.append(PhAppConfig().condi[0][2])
        else:
            error = res.read().decode('utf-8')
            PhLogging().console().debug(error)
            conn.close()

    def on_user_logout_event(self):
        # PhAppConfig().configClear()
        PhLocalStorage().getStorage()['last_login_user'] = PhLocalStorage().queryLastLoginUser()
        PhSQLQueryBuilder().filters = []
        self.mw.hide()
        self.mw.deleteLater()
        self.mw = None
        self.ui.userLineEdit.setText('')
        self.ui.pwdLineEdit.setText('')
        self.show()

    def serverCondiAdapter(self, item):
        return [item['uid'], item['uname'], item['condi']]

