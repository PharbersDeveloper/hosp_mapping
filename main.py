import sys

from PyQt5 import QtWidgets
from widgets.login import PhLoginWidget


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = PhLoginWidget()
    widget.show()
    sys.exit(app.exec_())
