import os, re

from epguides import find_or_add as getShow
from genericpath import isdir
from PyQt4.QtCore import Qt

CHECKS = [{'type': 'folder', 'pattern': '(?P<season>\d{1,2})'},
          {'type': 'filename', 'pattern': 'S(?P<season>\d{2})E(?P<episode>\d{2})'},
          {'type': 'filename', 'pattern': '(?!\d{5,})(?P<season>\d{2})(?P<episode>\d{2})(?<!\d{5})'},
          {'type': 'filename', 'pattern': '(?!\d{4,})(?P<season>\d{1})(?P<episode>\d{2})(?<!\d{4})'},
          {'type': 'filename', 'pattern': '(?<=^)(?P<episode>\d{2})'}]

INVALID_CHARS = ['<', '>', '|', '"', '\\', '/', ':', '*', '?']

VIEW = None

def setView(view):
    global VIEW
    VIEW = view

def initTable(show):
    VIEW.currentShow = str(show)
    VIEW.showLocation = os.path.join(VIEW.location, VIEW.currentShow)
    epguideShow = getShow(VIEW.currentShow)
    VIEW.setLabelText(VIEW.after, epguideShow.showurl if epguideShow else '')
    
    list = []
    scanDir(root=VIEW.showLocation, list=list)
    
    numRows = len(list)
    
    for row in range(numRows):
        file = list[row]
        row = VIEW.table.rowCount()
        filename = file['filename']
        ext = filename[-3:]
        if not ext in ['avi', 'mkv', 'mpg', 'wmv', 'mp4']:
            continue
        
        VIEW.table.insertRow(row)
        VIEW.table.setItem(row, 0, VIEW.newCheckboxTWidgetItem())
        VIEW.table.setItem(row, 1, VIEW.newTextTWidgetItem(filename))
        season = None
        episode = None
        folder = file['folder']
        defaultFirstSeason = not folder 
        
        for check in CHECKS:
            type = check['type']
            if type == 'folder' and defaultFirstSeason:
                continue
            
            matchObj = re.match(r".*{0}".format(check['pattern']), folder if type == 'folder' else filename, re.I)
            if matchObj:
                res = matchObj.groupdict()
                season = season if season else res.get('season')
                episode = episode if episode else res.get('episode')
                if season and episode:
                    break
                
        if not defaultFirstSeason:
            VIEW.table.setItem(row, 2, VIEW.newTextTWidgetItem(folder))
        elif not season:
            season = 1
        
        if season:
            season = int(season)
            VIEW.table.setItem(row, 3, VIEW.newTextTWidgetItem(season))
        if episode:
            episode = int(episode)
            VIEW.table.setItem(row, 4, VIEW.newTextTWidgetItem(episode))
            
        if season and episode and epguideShow:
            if epguideShow.eps.get(season) and epguideShow.eps[season].get(episode):
                VIEW.table.setItem(row, 5, VIEW.newTextTWidgetItem(epguideShow.eps[season][episode]['name']))

        
def checkMatch(matchObj, season, episode):
    both = False
    if matchObj:
        bits = matchObj.groups()
        season = season if season else bits[0]
        episode = episode if episode else bits[1]
        both = True
    return season, episode, both
        
def scanDir(list, root, folder=None):
    if not folder is None:
        root = os.path.join(root, folder)
        
    for f in os.listdir(root):
        path = os.path.join(root, f)
        if isdir(path):
            scanDir(list, root, f)
        else:
            list.append({'filename': f,
                         'folder': folder,
                         'from_root': None if root == VIEW.showLocation else os.path.relpath(root, VIEW.showLocation)})
    
def goClicked():
    for rowIndex in range(1, VIEW.table.rowCount()):
        if Qt.Checked == VIEW.table.item(rowIndex, 0).checkState():
            oldName = VIEW.beforeText(rowIndex)
            print "{}".format(oldName)
            newDir, newName = VIEW.afterText(rowIndex)
            newName = os.path.join(newDir, ''.join(c for c in newName if c not in INVALID_CHARS))
            
            if not oldName == newName:
                os.renames(oldName, newName)
