from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from helpers.phLogging import PhLogging
from model.hospModel import PhHospModel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from helpers.appConfig import PhAppConfig
import http.client
import json


class PhMainWidget(QWidget):
    current_dy = 0
    last_dy = 0
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tableView = QTableView()
        model = PhHospModel()
        model.updateData(self.queryDatabaseData("select * from prod_clean order by Index limit 1000"))
        model.signal_data_mod.connect(self.on_data_modify)
        self.tableView.setModel(model)
        self.tableView.verticalScrollBar().valueChanged.connect(self.on_vertical_scrolled)

        self.wev = QWebEngineView()
        self.wev.load(QUrl('https://www.baidu.com'))

        # 同步按钮
        upLayout = QHBoxLayout()
        synBtn = QPushButton()
        synBtn.setText('同步')
        refreshBtn = QPushButton()
        refreshBtn.setText('刷新')
        upLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        upLayout.addWidget(refreshBtn)
        upLayout.addWidget(synBtn)
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
        # 3. 同步内存缓存数据
        tmp = value.split('\t')
        try:
            idx = PhAppConfig().getConf()['unsync_steps_index'].index(tmp[0])
            PhAppConfig().getConf()['unsync_steps'][idx] = tmp
        except Exception:
            PhAppConfig().getConf()['unsync_steps_index'].append(tmp[0])
            PhAppConfig().getConf()['unsync_steps'].append(tmp)

        # 3. 固定滚动条
        self.tableView.verticalScrollBar().setValue(self.last_dy)

    def on_vertical_scrolled(self, dy):
        self.last_dy = self.current_dy
        self.current_dy = dy
        # TODO: 到底了之后继续加载数据
        pass

    def on_sync_btn_clicked(self):
        # TODO: 这个地方有个事务问题没解决, 线上的分布式锁的问题也没有解决
        # 如果同步的过程中，前端程序崩溃，数据不可恢复
        # 如果多人同时同步，可能会有些许问题
        if len(PhAppConfig().getConf()['unsync_steps_index']) == 0:
            PhLogging().console().debug('没有需要同步的信息')
            return
        # 1. construct delete SQL
        del_sql = 'alter table prod_clean delete where Index in [' + \
                  ','.join(PhAppConfig().getConf()['unsync_steps_index']) + \
                  '];'
        PhLogging().console().debug(del_sql)
        if not self.updataDBQuery(del_sql):
            PhLogging().console().fatal('错误，请联系管理员')
            return

        # 2. construct insert SQL
        ist_sql = "insert into prod_clean(Index, Id, Hospname, Level, Address, lop, ltm) VALUES "
        item_insert_lst = []
        for item in PhAppConfig().getConf()['unsync_steps']:
            tmp_sql = "("
            for i, tmp in enumerate(item):
                if i == 0:
                    tmp_sql = tmp_sql + tmp
                else:
                    tmp_sql = tmp_sql + ","
                    tmp_sql = tmp_sql + "'" + tmp + "'"
            tmp_sql = tmp_sql + ")"
            item_insert_lst.append(tmp_sql)
        ist_sql = ist_sql + ','.join(item_insert_lst) + ';'
        PhLogging().console().debug(ist_sql)
        if not self.updataDBQuery(ist_sql):
            PhLogging().console().fatal('错误，请联系管理员')
            return

        # 3. 清除本地操作缓存
        PhAppConfig().getConf()['unsync_step_count'] = 0
        PhLogging().countfile().info(PhAppConfig().getConf()['unsync_step_count'])
        PhAppConfig().getConf()['unsync_steps'] = []

    def on_refresh_btn_clicked(self):
        self.tableView.model() \
            .updateData(self.queryDatabaseData("select * from prod_clean order by Index limit 1000"))

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
            error = {'message': 'query db error'}
            PhLogging().console().debug(error)
            conn.close()
            return error

    def serverDataAdapter(self, item):
        steps = PhAppConfig().getConf()['unsync_steps']
        tmp = item['Index']
        steps_index = [index for index, f in enumerate(steps) if f[0] == tmp]
        if len(steps_index) == 0:
            return [item['Index'], item['Id'], item['Hospname'], item['Level'], item['Address'], item['lop'], item['ltm']]
        else:
            return steps[steps_index[0]]
