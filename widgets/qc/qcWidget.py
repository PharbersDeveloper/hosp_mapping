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
from widgets.commom.progressLabel import PhProgressLabel
from widgets.commom.webWidget import PhWebWidget
from widgets.dialogs.queryQcFilterCondiDlg import PhQueryQcFilterCondiDlg
from widgets.normal.mainWidget import PhMainWidget


class PhQcWidget(PhMainWidget):
    def setupLayout(self):
        self.tableView = QTableView()
        model = PhHospModel()
        model.isQc = True
        model.signal_data_mod.connect(self.on_data_modify)
        model.signal_no_data.connect(self.on_no_data_for_tmp_user)
        self.tableView.setModel(model)
        self.tableView.verticalScrollBar().valueChanged.connect(self.on_vertical_scrolled)
        self.tableView.setColumnHidden(1, True)

        # 用户信息
        nameLabel = QLabel(PhAppConfig().getConf()['displayName'])

        # 功能按钮
        logoutBtn = QPushButton()
        logoutBtn.setText('注销')
        upLayout = QHBoxLayout()
        synBtn = QPushButton()
        synBtn.setText('同步')
        condiBtn = QPushButton()
        condiBtn.setText('筛选')

        upLayout.addWidget(nameLabel)
        upLayout.addWidget(logoutBtn)

        self.wev = PhWebWidget() # QWebEngineView()
        # self.wev.load(QUrl('https://www.baidu.com'))
        self.wev.load(QUrl('https://cn.bing.com'))


        if PhAppConfig().isAdmin():
            progressLabel = PhProgressLabel()
            upLayout.addWidget(progressLabel)

        upLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        upLayout.addWidget(condiBtn)
        upLayout.addWidget(synBtn)
        logoutBtn.clicked.connect(self.on_logout_btn_clicked)
        synBtn.clicked.connect(self.on_sync_btn_clicked)
        condiBtn.clicked.connect(self.on_qc_filter_condi_btn_clicked)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addItem(upLayout)
        self.mainLayout.addWidget(self.tableView)
        # self.mainLayout.addWidget(self.wev)
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.wev)

    def on_qc_filter_condi_btn_clicked(self):
        PhLogging().console().debug('filter condi btn')
        dlg = PhQueryQcFilterCondiDlg()
        dlg.signal_change_qc_condi.connect(self.on_qc_filter_condi_changed)
        dlg.exec()

    def on_qc_filter_condi_changed(self, condi):
        PhLogging().console().debug('filter condi changed')
        PhLogging().console().debug(condi)
        PhSQLQueryBuilder().filters = condi
        self.tableView.model().updateData(self.queryDatabaseData(PhSQLQueryBuilder().querySelectSQL()))

    def on_no_data_for_tmp_user(self):
        PhLogging().console().debug('none data for temp user')
        dlg = QMessageBox(self)
        dlg.setWindowTitle('没有你需要处理的数据!')
        dlg.setText('没有你需要处理的数据')
        dlg.exec()
