import sys, os, random
from PyQt4 import QtGui, QtCore
from bpcanvas import staticQtMplCanvas
import time
from datetime import datetime, tzinfo

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)


        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        aa = time.clock()
        sfm = '%Y-%m-%d %H:%M:%S'
        tm1 = datetime.strptime('2008-06-30 16:16:30', sfm)
        tm2 = datetime.strptime('2008-06-30 16:27:01', sfm)
        tm3 = datetime.strptime('2008-06-28 16:02:30', sfm)
        tm4 = datetime.strptime('2008-06-28 16:36:01', sfm)
        tm5 = datetime.strptime('2008-07-06 11:02:30', sfm)
        tm6 = datetime.strptime('2008-07-10 18:15:01', sfm)
        #z = []

        #sc = staticQtMplCanvas(self.main_widget, 6, 6, 96, 'w', "userstrafpie", tm1, tm6, (15, 16)) 
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "sessions", 15, tm1, tm2)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "trans_crd",  tm3, tm4, 240)
        sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_user_traf", 17, tm5, tm6, 300)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_user_traf", 17, tm5, tm6, 600)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_total_traf",  tm5, tm6, 1200)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_total_traf_bydir",  tm5, tm6, 600)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_total_speed_bydir",  tm5, tm6, 1200)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_total_speed",  tm5, tm6, 1200)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_port_speed", 113, tm5, tm6, 600)
        #sc = staticQtMplCanvas(self.main_widget, 7, 3, 96, 'w', "nfs_user_speed", 17, tm5, tm6, 600)
        '''tm = sc.figure.get_axes()
        for line in tm[0].get_lines():
            print list(line.get_xdata())'''
        l.addWidget(sc)
        print time.clock() - aa
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()



qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("zOMG das works")
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()