from PyQt4 import QtCore, QtGui
from bpcdplot import cdDrawer


class bpcdQImage(object):
    
    def __init__(self):
        self._cddrawer = cdDrawer()
        
    def bpdraw(self, *args, **kwargs):
        imgs = self._cddrawer.cddraw(*args, **kwargs)
        qimgs = []
        for img in imgs:
            qimg = QtGui.QImage()
            qimg.loadFromData(img, 'png')
            qimgs.append(qimg)
        return qimgs
        
    def get_options(self, chartname):
        return self._cddrawer.get_options(chartname)
    
    def set_options(self, chartname, optdict):
        self._cddrawer.set_options(chartname, optdict)
        
        
        