import os
from genericpath import isdir

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, SIGNAL as qsignal

import logic

class AwesomeRenamer(QtGui.QMainWindow):
  
    def __init__(self):
        super(AwesomeRenamer, self).__init__()
        
        logic.setView(self)
        self.initUI()
        
        self.exampleLocation = os.path.join(os.path.dirname(__file__), "Example")
        self.autoPilot()
        
    def initUI(self):
        self.setGeometry(100, 100, 1000, 500)
        self.container = QtGui.QWidget()
        self.setCentralWidget(self.container)
        
        self.initMenuBar()
        self.initListView()
        
        self.setWindowTitle('Awesome Renamer')
        
    def autoPilot(self):
        self.location = self.exampleLocation
        self.initList()
        self.initTable('Battlestar Galactica')
    
    def initMenuBar(self):
        openFile = QtGui.QAction(QtGui.QIcon('open.png'), '&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        self.connect(openFile, qsignal('triggered()'), self.showDialog)

        fileMenu = self.menuBar().addMenu('&File')
        fileMenu.addAction(openFile)
        
    def initListView(self):
        self.before = QtGui.QLabel()
        self.before.setMaximumHeight(20)
        self.after = QtGui.QLabel()
        self.after.setMaximumHeight(20)
        self.go = QtGui.QPushButton('Go!')
        self.go.width = 40
        self.connect(self.go, qsignal('clicked()'), logic.goClicked)
        
        self.list = QtGui.QListWidget()
        self.connect(self.list, qsignal('itemClicked (QListWidgetItem *)'), self.listItemClicked)
        
        self.createTable()

        splitter = QtGui.QSplitter(Qt.Horizontal)
        splitter.addWidget(self.list)
        splitter.addWidget(self.table)
        splitter.setSizes([1, 200])
        
        mainbox = QtGui.QHBoxLayout()
        mainbox.setSizeConstraint(QtGui.QHBoxLayout.SetNoConstraint)
        mainbox.addWidget(splitter)
        
        tophbox = QtGui.QHBoxLayout()
        tophbox.setSizeConstraint(QtGui.QHBoxLayout.SetNoConstraint)
        
        topvbox = QtGui.QVBoxLayout()
        topvbox.addWidget(self.before)
        topvbox.addWidget(self.after)
        
        topgbox = QtGui.QGroupBox()
        topgbox.setLayout(topvbox)
        
        tophbox.addWidget(topgbox)
        tophbox.addWidget(self.go)
        
        vbox = QtGui.QVBoxLayout(self.container)
        vbox.setSizeConstraint(QtGui.QVBoxLayout.SetNoConstraint)
        vbox.addLayout(tophbox)
        vbox.addLayout(mainbox)
        
    def createTable(self):
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.connect(self.table, qsignal('itemClicked (QTableWidgetItem *)'), self.tableItemClicked)
        
    def showDialog(self):
        self.location = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose shows root directory', self.exampleLocation))
        self.initList()
            
    def initList(self):
        if not self.location:
            return
        
        self.table.clearContents()
        self.list.clear()
        for f in os.listdir(self.location):
            dir = os.path.join(str(self.location), f)
            if isdir(dir):
                item = QtGui.QListWidgetItem(self.list)
                item.setText(f)
            
        self.list.sortItems()
            
    def listItemClicked(self, widget):
        self.initTable(widget.text())
        
    def setLabelText(self, label, text):
        label.setText(text)
        label.adjustSize()
        
    def getText(self, item):
        return '' if item is None else str(item.text().toAscii())
    
    def getTIText(self, row, col):
        return self.getText(self.table.item(row, col))
    
    def beforeText(self, row):
        return os.path.join(self.showLocation, self.getTIText(row, 2), self.getTIText(row, 1))
    
    def afterText(self, row):
        return os.path.join(self.showLocation, 'Season {}'.format(int(self.getTIText(row, 3))) ), '{:02d} - {}{}'.format(int(self.getTIText(row, 4)), self.getTIText(row, 5), self.getTIText(row, 1)[-4:])
        
    def tableItemClicked(self, widget):
        row = widget.row()
        if row > 0:
            self.setLabelText(self.before, self.beforeText(row))
            afterDir, afterName = self.afterText(row)
            self.setLabelText(self.after, os.path.join(afterDir, afterName))
        else:
            for rowIndex in range(1, self.table.rowCount()):
                self.table.item(rowIndex, 0).setCheckState(self.table.item(0, 0).checkState())
    
    def initTableHeader(self):
        self.table.setRowCount(1)
        
        self.table.setItem(0, 0, self.newCheckboxTWidgetItem())
        self.table.item(0, 0).setBackground(QtGui.QBrush("#c56c00"))
        
        labels = ['File Name', 'Parent Folder', 'Season', 'Episode', 'Title']
        for index in range(len(labels)):
            self.table.setItem(0, index+1, self.newTextTWidgetItem(labels[index]))
            
        bg = QtGui.QBrush(QtGui.QColor(150, 150, 150))
        font = self.table.item(0, 0).font()
        font.setBold(True)
        for col in range(self.table.columnCount()):
            self.table.item(0, col).setBackground(bg)
            self.table.item(0, col).setFont(font)
        
    def newTextTWidgetItem(self, text):
        item = QtGui.QTableWidgetItem(QtGui.QTableWidgetItem.Type)
        item.setText(str(text))
        return item
    
    def newCheckboxTWidgetItem(self):
        item = QtGui.QTableWidgetItem()
        item.setCheckState(Qt.Unchecked)
        return item
    
    def initTable(self, show=None):
        if show is None:
            show = self.currentShow
        self.table.clearContents()
        self.initTableHeader()
        logic.initTable(show)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        