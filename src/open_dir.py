import sys, os, re
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, SIGNAL as qsignal
from genericpath import isdir
from epguides import find_or_add as getShow

class Example(QtGui.QMainWindow):
  
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1000, 300)
        self.container = QtGui.QWidget()
        self.setCentralWidget(self.container)
        
        self.initMenuBar()
        self.initListView()      
        
        self.setWindowTitle('OpenFile')
        
        self.autoPilot()
    
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
        
        self.list = QtGui.QListWidget()
        self.connect(self.list, qsignal('itemClicked (QListWidgetItem *)'), self.listItemClicked)
 
        self.table = QtGui.QTableWidget()
        self.initTableHeader()
        self.connect(self.table, qsignal('itemClicked (QTableWidgetItem *)'), self.tableItemClicked)

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
        
        
    def showDialog(self):
        self.location = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose Directory', 'Y:/vids/shows'))
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
        return '' if item is None else str(item.text())
    
    def getTIText(self, row, col):
        return self.getText(self.table.item(row, col))
        
    def tableItemClicked(self, widget):
        row = widget.row()
        before = os.path.join(self.showLocation, self.getTIText(row, 2), self.getTIText(row, 1))
        self.setLabelText(self.before, before)
        after = os.path.join( self.showLocation, 'Season %d' % int(self.getTIText(row, 3)), '%02d - %s' % (int(self.getTIText(row, 4)), self.getTIText(row, 5)) )
        self.setLabelText(self.after, after)
    
    CHECKS = [{'type': 'folder', 'pattern': '(?P<season>\d{1,2})'},
              {'type': 'filename', 'pattern': 'S(?P<season>\d{2})E(?P<episode>\d{2})'},
              {'type': 'filename', 'pattern': '(?P<season>\d{2})(?P<episode>\d{2})'},
              {'type': 'filename', 'pattern': '(?P<season>\d{1})(?P<episode>\d{2})'},
              {'type': 'filename', 'pattern': '(?P<episode>\d{2}) +- +'}]
    
    def initTable(self, show):
        self.currentShow = str(show)
        self.showLocation = os.path.join(self.location, self.currentShow)
        epguideShow = getShow(self.currentShow)
        self.setLabelText(self.after, epguideShow.showurl if epguideShow else '')
        
        list = []
        self.scanDir(root=self.showLocation, list=list)
        
        self.table.clearContents()
        numRows = len(list)
        self.table.setRowCount(numRows)
        
        for row in range(numRows):
            file = list[row]
            filename = file['filename']
            if not filename.endswith('avi') and not filename.endswith('mkv'):
                continue
            
            self.table.setItem(row, 0, self.newCheckboxTWidgetItem())
            self.table.setItem(row, 1, self.newTextTWidgetItem(filename))
            season = None
            episode = None
            folder = file['folder']
            defaultFirstSeason = not folder 
            both = False
            
            for check in self.CHECKS:
                if both:
                    break
                
                type = check['type']
                if type == 'folder' and defaultFirstSeason:
                    continue
                
                matchObj = re.match(r".*{0}".format(check['pattern']), folder if type == 'folder' else filename, re.I)
                if matchObj:
                    res = matchObj.groupdict()
                    season = season if season else res.get('season')
                    episode = episode if episode else res.get('episode')
                    both = season and episode
                    
            if not defaultFirstSeason:
                self.table.setItem(row, 2, self.newTextTWidgetItem(folder))
            elif not season:
                season = 1
            
            if season:
                season = int(season)
                self.table.setItem(row, 3, self.newTextTWidgetItem(season))
            if episode:
                episode = int(episode)
                self.table.setItem(row, 4, self.newTextTWidgetItem(episode))
                
            if season and episode and epguideShow:
                if epguideShow.eps.get(season) and epguideShow.eps[season].get(episode):
                    self.table.setItem(row, 5, self.newTextTWidgetItem(epguideShow.eps[season][episode]['name']))

            
    def checkMatch(self, matchObj, season, episode):
        both = False
        if matchObj:
            bits = matchObj.groups()
            season = season if season else bits[0]
            episode = episode if episode else bits[1]
            both = True
        return season, episode, both
            
    def initTableHeader(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderItem(0, self.newCheckboxTWidgetItem())

        labels = ['File Name', 'Parent Folder', 'Season', 'Episode', 'Title']
        for index in range(len(labels)):
            self.table.setHorizontalHeaderItem(index+1, self.newTextTWidgetItem(labels[index]))
            
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
            
    def newTextTWidgetItem(self, text):
        item = QtGui.QTableWidgetItem(QtGui.QTableWidgetItem.Type)
        item.setText(str(text))
        return item
    
    def newCheckboxTWidgetItem(self):
        item = QtGui.QTableWidgetItem()
        item.setCheckState(Qt.Unchecked)
        return item
        
    def scanDir(self, list, root, folder=None):
        if not folder is None:
            root = os.path.join(root, folder)
            
        for f in os.listdir(root):
            path = os.path.join(root, f)
            if isdir(path):
                self.scanDir(list, root, f)
            else:
                list.append({'filename': f,
                             'folder': folder,
                             'from_root': None if root == self.showLocation else os.path.relpath(root, self.showLocation)})
        
    def autoPilot(self):
        self.location = 'Y:\\vids\\shows\\'
        self.initTable('Caprica')

app = QtGui.QApplication(sys.argv)
ex = Example()
ex.show()
app.exec_()