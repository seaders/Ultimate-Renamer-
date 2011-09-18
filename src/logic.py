import os, re

from epguides import find_or_add as getShow
from genericpath import isdir
from PyQt4.QtCore import Qt

"""
    This is the list of regular expressions that get run through sequentially while it's still looking for either the season, or the episode.
    Valid list:
        Season 01\...avi will capture the season info as '1'
        ...s01e02...avi will capture season as '1', episode as '2'
        ...0103...avi will capture seaason as '1, episode as '3'
        ...104...avi will capture seaason as '1, episode as '4'
        05...avi will capture episode as '5'
"""
CHECKS = [{"type": "folder", "pattern"  : "(?P<season>\d{1,2})(?# capture the season from the folder name, can be 1 or 2 digits anywhere in the folder name)"},
          {"type": "filename", "pattern": "S(?P<season>\d{1,2})E(?P<episode>\d{1,2})(?# capture season and episode, in s01e02 format)"},
          {"type": "filename", "pattern": "(?<!\d{1})(?P<season>\d{1,2})(?P<episode>\d{2})(?!\d{1})(?# capture season and episode, in 0102 or 102 format, lookahead and lookbehind to ensure no other digits touch the group)"},
          {"type": "filename", "pattern": "(?<=^)(?P<episode>\d{2})(?!\d{1})(?# capture season and episode, in '02...', lookbehind to ensure that it's at the beginning of the filename)"}]

DEFAULT_R = "~"
# Invalid characters, with suggested valid replacements, this may need to be extended depending on some operating systems
REPLACERS = {"|": ";", "\"": "'", ":": ";", "<": DEFAULT_R, ">": DEFAULT_R, "\\": DEFAULT_R, "/": DEFAULT_R, "*": DEFAULT_R, "?": DEFAULT_R}

VIEW = None

def setView(view):
    global VIEW
    VIEW = view

def initTable(show):
    VIEW.currentShow = str(show)
    VIEW.showLocation = os.path.join(VIEW.location, VIEW.currentShow)
    epguideShow = getShow(VIEW.currentShow)
    VIEW.setLabelText(VIEW.after, epguideShow.showurl if epguideShow else "")
    
    list = []
    scanDir(root=VIEW.showLocation, list=list)
    
    numRows = len(list)
    
    for row in range(numRows):
        file = list[row]
        row = VIEW.table.rowCount()
        filename = file["filename"]
        ext = filename[-3:]
        if not ext in ["avi", "mkv", "mpg", "wmv", "mp4"]:
            continue
        
        VIEW.table.insertRow(row)
        VIEW.table.setItem(row, 0, VIEW.newCheckboxTWidgetItem())
        VIEW.table.setItem(row, 1, VIEW.newTextTWidgetItem(filename))
        season = None
        episode = None
        folder = file["folder"]
        defaultFirstSeason = not folder 
        
        for check in CHECKS:
            type = check["type"]
            if type == "folder" and defaultFirstSeason:
                continue
            
            matchObj = re.match(r".*{0}".format(check["pattern"]), folder if type == "folder" else filename, re.I)
            if matchObj:
                res = matchObj.groupdict()
                season = season if season else res.get("season")
                episode = episode if episode else res.get("episode")
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
                VIEW.table.setItem(row, 5, VIEW.newTextTWidgetItem(epguideShow.eps[season][episode]["name"]))
                
    VIEW.table.sortItems(4) #sort items by episode number
    VIEW.table.sortItems(3) #then season
    VIEW.table.insertRow(0) 
    rows = VIEW.table.rowCount()-1
    for col in range(VIEW.table.columnCount()):
        VIEW.table.setItem(0, col, VIEW.table.takeItem(rows, col))
    VIEW.table.removeRow(rows)
           
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
            list.append({"filename": f,
                         "folder": folder,
                         "from_root": None if root == VIEW.showLocation else os.path.relpath(root, VIEW.showLocation)})
    
def goClicked():
    for rowIndex in range(1, VIEW.table.rowCount()):
        if Qt.Checked == VIEW.table.item(rowIndex, 0).checkState():
            oldName = VIEW.beforeText(rowIndex)
            print "{}".format(oldName)
            newDir, newName = VIEW.afterText(rowIndex)
            name = ""
            for c in newName:
                name += c if not REPLACERS.get(c) else REPLACERS[c]
            newName = os.path.join(newDir, name)
            if not oldName == newName:
                os.renames(oldName, newName)
    VIEW.initTable()
