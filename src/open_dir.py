import sys

from view import Example
from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)
ex = Example()
ex.show()
app.exec_()
