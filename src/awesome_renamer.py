import sys

from view import AwesomeRenamer
from PyQt4 import QtGui
app = QtGui.QApplication(sys.argv)
ex = AwesomeRenamer()
ex.show()
app.exec_()
