

from PyQt4.QtGui import *


class Example(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setGeometry(250, 200, 350, 250)
        self.initUI()


    def initUI(self):
        hbox = QHBoxLayout(self)
        hbox.setSizeConstraint(QLayout.SetNoConstraint)
        widget = QListWidget()
#        policy = QSizePolicy()
#        policy.setHorizontalPolicy(QSizePolicy.Expanding)
#        policy.setVerticalPolicy(QSizePolicy.Expanding)
#        widget.setSizePolicy(policy)
#        widget.setMaximumSize(16777215, 16777215)
        
        hbox.addWidget(widget)

    def onChanged(self, text):
        self.label.setText(text)
        self.label.adjustSize()


def main():
  
    app = QApplication([])
    exm = Example()
    exm.show()
    app.exec_()  


if __name__ == '__main__':
    main()   