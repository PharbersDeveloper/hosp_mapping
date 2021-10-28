import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from widgets.login import PhLoginWidget
import os
import platform


if __name__ == '__main__':
    # ptf = platform.system()
    # if ptf == "Darwin":
    #     cwd = os.path.abspath(sys.argv[0])
    #     cwd = cwd[0:cwd.index('/', cwd.index('.app'))]
    #     os.chdir(cwd)

    app = QtWidgets.QApplication(sys.argv)
    widget = PhLoginWidget()
    widget.show()
    sys.exit(app.exec_())
