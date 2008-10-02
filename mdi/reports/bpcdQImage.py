from PyQt4 import QtCore, QtGui
#from bpcdplot import cdDrawer


class bpcdQImage(object):
    
    def __init__(self, connection):
        #self._cddrawer = cdDrawer()
        self.connection = connection
        self.options = {}
        
    def bpdraw(self, *args, **kwargs):
        #imgs = self._cddrawer.cddraw(*args, **kwargs)
        if kwargs.has_key('options'):
            kwargs['options'].update(self.options)
        else:
            kwargs['options'] = self.options
        print args
        imgs  = self.connection.makeChart(*args, **kwargs)
        ret = imgs.pop()
        self.options = {}
        kwargs['return'].update(ret)
        
        qimgs = []
        for img in imgs:
            qimg = QtGui.QImage()
            qimg.loadFromData(img, 'png')
            qimgs.append(qimg)
        
        return qimgs
        
    def get_options(self, chartname):
        #return self._cddrawer.get_options(chartname)
        pass
    
    def set_options(self, chartname, optdict):
        #self._cddrawer.set_options(chartname, optdict)
        #self.connection.setChartOptions(chartname, optdict)
        self.options.update(optdict)
        
        
        