from PyQt4 import QtGui        
def tableFormat(table):        
    table.setFrameShape(QtGui.QFrame.Panel)
    table.setFrameShadow(QtGui.QFrame.Sunken)
    table.setAlternatingRowColors(True)
    table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
    table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
    table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
    #table.setGridStyle(QtCore.Qt.DotLine)
    table.setSortingEnabled(False)
    table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
    table.verticalHeader().setHidden(True)
    table.setColumnHidden(0, True)
    hh = table.horizontalHeader()
    hh.setStretchLastSection(True)
    hh.setHighlightSections(False)
    hh.setClickable(False)
    hh.setMovable(False)
    hh.ResizeMode(QtGui.QHeaderView.Stretch)
    return table


        