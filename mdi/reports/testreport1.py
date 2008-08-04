#-*-encoding:utf-8-*-
from PyQt4 import QtCore, QtGui
from bpreportedit import bpReportEdit
import sys
from datetime import datetime, tzinfo
import time

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        fileMenu = QtGui.QMenu(self.tr("&File"), self)
        newAction = fileMenu.addAction(self.tr("&New..."))
        newAction.setShortcut(self.tr("Ctrl+N"))
        self.printAction = fileMenu.addAction(self.tr("&Print..."), self.printFile)
        self.printAction.setShortcut(self.tr("Ctrl+P"))
        self.printAction.setEnabled(False)
        quitAction = fileMenu.addAction(self.tr("E&xit"))
        quitAction.setShortcut(self.tr("Ctrl+Q"))
        self.menuBar().addMenu(fileMenu)

        self.letters = QtGui.QTabWidget()

        self.connect(quitAction, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("close()"))
        self.setCentralWidget(self.letters)
        self.setWindowTitle(self.tr("Order Form"))


    def createLetter(self, datafile, rargs):
        brep = bpReportEdit()
        editor = brep.createreport(datafile, rargs)

        self.printAction.setEnabled(True)
        return editor

    def createSample(self):
        sfm = '%Y-%m-%d %H:%M:%S'
        tm1 = datetime.strptime('2008-07-01 11:02:30', sfm)
        tm2 = datetime.strptime('2008-07-03 11:02:30', sfm)
        tm3 = datetime.strptime('2008-07-17 16:17:30', sfm)
        tm4 = datetime.strptime('2008-06-30 16:57:30', sfm)
        tm5 = datetime.strptime('2008-07-08 11:02:30', sfm)
        tm6 = datetime.strptime('2008-07-18 20:15:01', sfm)
        tm7 = datetime.strptime('2008-06-27 16:17:30', sfm)
        tm8 = datetime.strptime('2008-06-30 16:57:30', sfm)
        tm6 = datetime.strptime('2008-07-16 20:15:01', sfm)
        
        aa = time.clock()
        #editor = self.createLetter("xml/report3_nas.xml", [(17, tm5, tm6, (1,2,3))])
        #editor = self.createLetter("xml/report3_nas_nas.xml", [(2, tm5, tm6)])
        #editor = self.createLetter("xml/report3_nass.xml", [((1,2,3), tm5, tm6)])
        #editor = self.createLetter("xml/report3_ttr_nas.xml", [(tm7, tm6, (1,2,3))])
        editor = self.createLetter("xml/report3_tutr_nas.xml", [(tm7, tm6, (1,2,3))])
        #editor = self.createLetter("xml/report3_tus_nas.xml", [((15, 16, 17, 20, 21, 22), tm1, tm6, (1, 2, 3))])
        
        #editor = self.createLetter("xml/report3_nas.xml", [(17, tm5, tm6), (1,2,3)])
        #editor = self.createLetter("xml/report3_port.xml", [((21, 80, 113), tm1, tm6)])
        #tdoc = editor.document()
        #qf.open(QtCore.QIODevice.WriteOnly)
        #qf.writeData(tdoc.toHtml())
        #qf.close()
        #f = open('tmpp.html', 'wb')
        #f.write(tdoc.toHtml())
        #f.close()
        #editor = self.createLetter("xml/report3_pie.xml", [((15, 16, 17), tm1, tm2)])
        #editor = self.createLetter("xml/report3_sess.xml", [((15, 16, 17), tm3, tm4)])
        #editor = self.createLetter("xml/report3_tr.xml", [(tm3, tm6)])
        print time.clock() - aa
        tabIndex = self.letters.addTab(editor, "zomg")
        self.letters.setCurrentIndex(tabIndex)




    def printFile(self):
        editor = self.letters.currentWidget()
        document = editor.document()
        printer = QtGui.QPrinter()

        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return

        document.print_(printer)







if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    window.createSample()
    sys.exit(app.exec_()) 