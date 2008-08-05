from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as QtFigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from bpmplplot import bpmplDrawer

#base Agg matplotlib canvas
class mplCanvas(FigureCanvas): 
    def __init__(self, width=5, height=4, dpi=100, color='w', *args):
        '''Creates Figure and initializes Canvas with
        @width
        @height
        @dpi
        @color,
        @*args - for plotting'''
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor(color)
        self.axes = fig.add_subplot(111)
        #plot
        self.compute_initial_figure(*args)
        FigureCanvas.__init__(self, fig)
        
    def compute_initial_figure(self, *args):
            pass

#static Agg matplotlib canvas
class staticMplCanvas(mplCanvas):
    def compute_initial_figure(self, *args):
        '''Plots with
        @*args'''
        drwr = bpmplDrawer()
        drwr.bpdraw(self.axes, *args)

#base QTAgg matplotlib canvas, needs a widget parent
class qtMplCanvas(QtFigureCanvas): 
    def __init__(self, parent=None, width=5, height=4, dpi=100, color='w', *args):
        '''Creates Figure and initializes Canvas with
        @parent
        @width
        @height
        @dpi
        @color,
        @*args - for plotting'''
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor(color)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        #plot
        self.compute_initial_figure(*args)
        QtFigureCanvas.__init__(self, fig)
        self.setParent(parent)
        QtFigureCanvas.setSizePolicy(self,
                                    QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Expanding)
        QtFigureCanvas.updateGeometry(self)
        def compute_initial_figure(self, *args):
            pass

#static QTAgg matplotlib canvas
class staticQtMplCanvas(qtMplCanvas):
    def compute_initial_figure(self, *args):
        '''Plots with
        @*args'''
        drwr = bpmplDrawer()
        drwr.bpdraw(self.axes, *args)
