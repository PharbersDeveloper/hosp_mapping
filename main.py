import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QLockFile
from PyQt5.QtWidgets import QMessageBox

from widgets.login import PhLoginWidget
import os
import platform
import ssl



if __name__ == '__main__':
    # ptf = platform.system()
    # if ptf == "Darwin":
    #     cwd = os.path.abspath(sys.argv[0])
    #     cwd = cwd[0:cwd.index('/', cwd.index('.app'))]
    #     os.chdir(cwd)

    ssl._create_default_https_context = ssl._create_unverified_context
    app = QtWidgets.QApplication(sys.argv)

    lockFile = QLockFile("./appName.app.lock")
    if lockFile.tryLock(2000):
        widget = PhLoginWidget()
        widget.show()
        sys.exit(app.exec_())
    else:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("提示")
        msg_box.setText("软件已在运行!")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.addButton("确定", QMessageBox.YesRole)
        msg_box.exec()
        sys.exit(-1)

