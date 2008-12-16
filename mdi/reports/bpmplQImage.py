from PyQt4 import QtCore, QtGui
from bpcanvas import staticQtMplCanvas


class bpmplQImage(object):
    
    def __init__(self):
        pass
        
    def bpdraw(self, *args, **kwargs):
        sc = staticQtMplCanvas( None, 7, 3, 96, 'w', *args)
        sc.draw()
        qtbuf = QtCore.QBuffer()
        qtbuf.open(QtCore.QIODevice.Truncate | QtCore.QIODevice.WriteOnly)
        sc.print_png(qtbuf)
        qtbuf.close()
        qtbuf.open(QtCore.QIODevice.ReadOnly)
        img = QtGui.QImage()
        img.load(qtbuf, 'png')
        img.save('tms.png')
        return img
    
        
    def get_options(self, chartname):
        pass
    
    def set_options(self, chartname, optdict):
        pass