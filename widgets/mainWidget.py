import re

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QTableView, QPushButton, QLabel, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from helpers.localStorage import PhLocalStorage
from helpers.phLogging import PhLogging
from model.hospModel import PhHospModel
from PyQt5.QtCore import Qt, pyqtSignal
from helpers.appConfig import PhAppConfig
import http.client
import json
from helpers.queryBuilder import PhSQLQueryBuilder
from widgets.dialogs.queryCondiDlg import PhQueryCandiDlg
from widgets.progressLabel import PhProgressLabel
from widgets.webWidget import PhWebWidget


class PhMainWidget(QWidget):
    user_logout = pyqtSignal()
    current_dy = 0
    last_dy = 0
    show_count = 0
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tableView = QTableView()
        model = PhHospModel()
        model.signal_data_mod.connect(self.on_data_modify)
        model.signal_no_data.connect(self.on_no_data_for_tmp_user)
        self.tableView.setModel(model)
        self.tableView.verticalScrollBar().valueChanged.connect(self.on_vertical_scrolled)

        self.tableView.setColumnHidden(1,True)

        self.wev = PhWebWidget() # QWebEngineView()
        # self.wev.load(QUrl('https://www.baidu.com'))
        self.wev.load(QUrl('https://cn.bing.com'))

        # 用户信息
        nameLabel = QLabel(PhAppConfig().getConf()['displayName'])

        # 功能按钮
        logoutBtn = QPushButton()
        logoutBtn.setText('注销')
        upLayout = QHBoxLayout()
        synBtn = QPushButton()
        synBtn.setText('同步')
        refreshBtn = QPushButton()
        refreshBtn.setText('刷新')
        candiBtn = QPushButton()
        candiBtn.setText('任务分配')

        if PhAppConfig().isTmpUser():
            candiBtn.setEnabled(False)
            self.tableView.setColumnHidden(14, True)
            self.tableView.setColumnHidden(15, True)
            self.tableView.setColumnHidden(16, True)
            self.tableView.setColumnHidden(17, True)

        upLayout.addWidget(nameLabel)
        upLayout.addWidget(logoutBtn)

        if PhAppConfig().isAdmin():
            progressLabel = PhProgressLabel()
            upLayout.addWidget(progressLabel)

        upLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        upLayout.addWidget(candiBtn)
        upLayout.addWidget(refreshBtn)
        upLayout.addWidget(synBtn)
        logoutBtn.clicked.connect(self.on_logout_btn_clicked)
        candiBtn.clicked.connect(self.on_candi_btn_clicked)
        synBtn.clicked.connect(self.on_sync_btn_clicked)
        refreshBtn.clicked.connect(self.on_refresh_btn_clicked)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addItem(upLayout)
        self.mainLayout.addWidget(self.tableView)
        self.mainLayout.addWidget(self.wev)
        self.setLayout(self.mainLayout)

    # event handler
    def keyPressEvent(self, event):
        key = event.key()
        handlers = {
            Qt.Key_F1: self.searchWithText,
            Qt.Key_F2: self.searchWithQcc
        }
        handler = handlers.get(key)
        if handler:
            select = self.tableView.currentIndex().data()
            handler(select)

    def searchWithText(self, msg):
        # self.wev.load(QUrl('https://www.baidu.com/s?wd=' + msg))
        self.wev.load(QUrl('https://cn.bing.com/search?q=' + msg))

    def searchWithQcc(self, msg):
        self.wev.load(QUrl('https://www.qcc.com/web/search?key=' + msg))

    def on_data_modify(self, value):
        # 1. 添加log count
        print(PhLocalStorage().getStorage()['unsync_step_count'])
        PhLocalStorage().getStorage()['unsync_step_count'] = PhLocalStorage().getStorage()['unsync_step_count'] + 1
        # PhLogging().countfile().info(PhLocalStorage().getStorage()['unsync_step_count'])
        # 2. 添加operation log
        # 修改一下，先插入到db中
        # PhLogging().opfile().info(value)
        PhLocalStorage().pushUnsavedStep(value)
        # 3. 同步内存缓存数据
        tmp = value.split('\t')
        try:
            idx = PhLocalStorage().getStorage()['unsync_steps_index'].index(tmp[0])
            PhLocalStorage().getStorage()['unsync_steps'][idx] = tmp
        except Exception:
            PhLocalStorage().getStorage()['unsync_steps_index'].append(tmp[0])
            PhLocalStorage().getStorage()['unsync_steps'].append(tmp)

        # 3. 固定滚动条
        self.tableView.verticalScrollBar().setValue(self.last_dy)

    def on_vertical_scrolled(self, dy):
        self.last_dy = self.current_dy
        self.current_dy = dy
        if dy == self.tableView.verticalScrollBar().maximum():
            PhSQLQueryBuilder().nextPage()
            self.tableView.model().appendData(self.queryDatabaseData(PhSQLQueryBuilder().querySelectSQL()))

    def on_sync_btn_clicked(self):
        # TODO: 这个地方有个事务问题没解决, 线上的分布式锁的问题也没有解决
        # 如果同步的过程中，前端程序崩溃，数据不可恢复
        # 如果多人同时同步，可能会有些许问题

        unidx = self.check_nun_values()
        if len(unidx) > 0:
            PhLogging().console().fatal('某行出现错误')
            QMessageBox.critical(self, "同步错误", "{}行出现错误".format(''.join(str(unidx))))
            return

        if len(PhLocalStorage().getStorage()['unsync_steps_index']) == 0:
            PhLogging().console().debug('没有需要同步的信息')
            QMessageBox.information(self, "同步成功", "同步数据成功")
            return

        if not self.updataDBQuery(PhSQLQueryBuilder().alertDeleteSQL(PhLocalStorage().getStorage()['unsync_steps_index'])):
            PhLogging().console().fatal('错误，请联系管理员')
            QMessageBox.critical(self, "同步错误", "同步错误，请联系管理员")
            return

        if not self.updataDBQuery(PhSQLQueryBuilder().alertInsertMultiSQL(PhLocalStorage().getStorage()['unsync_steps'])):
            PhLogging().console().fatal('错误，请联系管理员')
            QMessageBox.critical(self, "同步错误", "同步错误，请联系管理员")
            return

        # 清除本地操作缓存
        PhLocalStorage().getStorage()['unsync_step_count'] = 0
        # PhLogging().countfile().info(PhLocalStorage().getStorage()['unsync_step_count'])
        PhLocalStorage().getStorage()['unsync_steps'] = []
        PhLocalStorage().getStorage()['unsync_steps_index'] = []
        PhLocalStorage().afterSyncUnsavedSteps()

        QMessageBox.information(self, "同步成功", "同步数据成功")


    def on_refresh_btn_clicked(self):
        self.tableView.model().updateData(self.queryDatabaseData(PhSQLQueryBuilder().querySelectSQL()))

    def on_logout_btn_clicked(self):
        self.close()

    def on_no_data_for_tmp_user(self):
        PhLogging().console().debug('none data for temp user')
        dlg = QMessageBox(self)
        dlg.setWindowTitle('没有你需要处理的数据!')
        dlg.setText('没有你需要处理的数据，或者管理员分配语句出错，请联系你的管理员处理该情况')
        dlg.exec()

    def on_candi_btn_clicked(self):
        dlg = PhQueryCandiDlg()
        dlg.signal_change_candi.connect(self.on_condi_change)
        dlg.exec()

    def on_condi_change(self):
        if not self.updataDBQuery(PhSQLQueryBuilder().deleteAllCandi()):
            PhLogging().console().fatal('错误，请联系管理员')
            return
        if not self.updataDBQuery(PhSQLQueryBuilder().alterAllCandi()):
            PhLogging().console().fatal('错误，请联系管理员')
            return

    def updataDBQuery(self, sql):
        parameters = {
            'query': sql
        }
        conf = PhAppConfig()
        conn = http.client.HTTPSConnection("api.pharbers.com")
        payload = json.dumps(parameters)
        headers = {
            'Authorization': conf.getConf()['access_token'],
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        conn.request("POST", "/phchproxyupdate", payload, headers)
        res = conn.getresponse()

        if (res.status == 200) & (res.reason == 'OK'):
            msg = {'message': 'update db success'}
            conn.close()
            PhLogging().console().debug(msg)
            return True
        else:
            error = {'message': 'query db error'}
            conn.close()
            PhLogging().console().debug(error)
            return False

    def queryDatabaseData(self, sql):
        parameters = {
            # 'query': "select * from prod_clean order by Index limit 1000",
            'query': sql,
            'schema': PhAppConfig().getConf()['defined_schema']
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
            return list(map(self.serverDataAdapter, result))
        else:
            error = res.read().decode('utf-8')
            PhLogging().console().debug(error)
            conn.close()
            return []

    def serverDataAdapter(self, item):
        steps = PhLocalStorage().getStorage()['unsync_steps']
        tmp = item['Index']
        steps_index = [index for index, f in enumerate(steps) if f[0] == tmp]
        if len(steps_index) == 0:
            result = []
            for idx in PhAppConfig().getConf()['defined_schema']:
                result.append(item[idx])
            return result
        else:
            return steps[steps_index[0]]

    def check_nun_values(self):
        not_none_cols = PhAppConfig().getConf()['non_null_cols']
        schema = PhAppConfig().getConf()['trans_schema']
        not_none_idx = []
        for item in not_none_cols:
            not_none_idx.append(schema.index(item))

        not_fill_unsaved_steps_idx = []
        for row in PhLocalStorage().getStorage()['unsync_steps']:
            for cell_idx in not_none_idx:
                if row[cell_idx] == '':
                    not_fill_unsaved_steps_idx.append(row[0])
                    break
        return not_fill_unsaved_steps_idx

    def showEvent(self, a0: QtGui.QShowEvent):
        if self.show_count == 0:
            self.tableView.model().updateData(self.queryDatabaseData(PhSQLQueryBuilder().querySelectSQL()))
        self.show_count = self.show_count + 1

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.on_sync_btn_clicked()
        self.user_logout.emit()
