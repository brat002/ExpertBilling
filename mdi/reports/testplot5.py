#-*-encoding:utf-8-*-
"""PyQt4 port of the richtext/orderform example from Qt v4.x"""

import sys, time
from PyQt4 import QtCore, QtGui
from datetime import datetime
from  pychartdir import *
from billplot import Drawer
#Qbuffer, Qtemporaryfile

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

        self.connect(newAction, QtCore.SIGNAL("triggered()"), self.openDialog)
        self.connect(quitAction, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("close()"))
        self.setCentralWidget(self.letters)
        self.setWindowTitle(self.tr("Order Form"))


    def createLetter(self, name, address, orderItems, sendOffers):
        editor = QtGui.QTextEdit()
        tabIndex = self.letters.addTab(editor, name)
        self.letters.setCurrentIndex(tabIndex)

        cursor = editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        topFrame = cursor.currentFrame()
        topFrameFormat = topFrame.frameFormat()
        topFrameFormat.setPadding(16)
        topFrame.setFrameFormat(topFrameFormat)

        textFormat = QtGui.QTextCharFormat()
        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setFontWeight(QtGui.QFont.Bold)

        referenceFrameFormat = QtGui.QTextFrameFormat()
        referenceFrameFormat.setBorder(1)
        referenceFrameFormat.setPadding(8)
        referenceFrameFormat.setPosition(QtGui.QTextFrameFormat.FloatRight)
        referenceFrameFormat.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 40))
        cursor.insertFrame(referenceFrameFormat)

        cursor.insertText("A company", boldFormat)
        cursor.insertBlock()
        cursor.insertText("321 City Street")
        cursor.insertBlock()
        cursor.insertText("Industry Park")
        cursor.insertBlock()
        cursor.insertText("Another country")

        cursor.setPosition(topFrame.lastPosition())

        cursor.insertText(name, textFormat)
        for line in address.split("\n"):
            cursor.insertBlock()
            cursor.insertText(line)

        cursor.insertBlock()
        cursor.insertBlock()

        date = QtCore.QDate.currentDate()
        cursor.insertText(self.tr("Date: %1").arg(date.toString("d MMMM yyyy")), textFormat)
        cursor.insertBlock()

        bodyFrameFormat = QtGui.QTextFrameFormat()
        bodyFrameFormat.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 100))
        cursor.insertFrame(bodyFrameFormat)

        cursor.insertText(self.tr("I would like to place an order for the "
                          "following items:"), textFormat)
        cursor.insertBlock()
        cursor.insertBlock()
 
        testperf = time.clock()
        #sc = staticMplCanvas( 10, 5, 75, "usertotalbytes", 15, '2008-07-02 17:43:01.296000+03:00', '2008-07-02 18:49:01.296000+03:00', 120)
        #sc = staticMplCanvas(8, 8, 75, "userstotalpie", '2008-07-02 17:43:01.296000+03:00', '2008-07-02 18:49:01.296000+03:00', (15, 16))
        sfm = '%Y-%m-%d %H:%M:%S'
        tm1 = datetime.strptime('2008-06-30 16:16:30', sfm)
        tm6 = datetime.strptime('2008-07-11 18:01:01', sfm)
        #z = []
        #sc = staticMplCanvas(8, 8, 75,  'w', "userstrafpie", tm1, tm6, (15, 16))        
        #sc.draw()
        # The data for the pie chart
        dr = Drawer()
        selstr = "SELECT date_start, octets, direction FROM billservice_netflowstream WHERE (account_id=17) AND (date_start BETWEEN '2008-07-06 11:02:30' AND '2008-07-10 18:02:30') ORDER BY date_start;"
        (times, y_in, y_out, y_tr, bstr) = dr.get_traf(selstr, 300)

        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        ams = (750, 450)
        c = XYChart(*ams)
        
        # Set the plotarea at (55, 65) and of size 350 x 300 pixels, with white background
        # and a light grey border (0xc0c0c0). Turn on both horizontal and vertical grid lines
        # with light grey color (0xc0c0c0)
        c.setPlotArea(55, 65, 650, 300, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1)
        c.setColors(transparentPalette)

        # Add a legend box at (50, 30) (top of the chart) with horizontal layout. Use 12 pts
        # Times Bold Italic font. Set the background and border color to Transparent.
        c.addLegend(50, 30, 0, "FreeSerif.ttf", 12).setBackground(Transparent)
        
        # Add a title to the chart using 18 pts Times Bold Itatic font
        c.addTitle("Traffic by user", "FreeSerif.ttf", 18)
        
        # Add a title to the y axis using 12 pts Arial Bold Italic font
        c.yAxis().setTitle("Траффик", "FreeSerif.ttf", 14)
        
        # Set the y axis line width to 3 pixels
        c.yAxis().setWidth(1)
        
        # Add a title to the x axis using 12 pts Arial Bold Italic font
        c.xAxis().setTitle("Time", "FreeSerif.ttf", 12)
        
        # Set the x axis line width to 3 pixels
        c.xAxis().setWidth(1)
        
        # Add a red (0xff3333) line layer using dataX0 and dataY0
        zzz = (-1, "INPUT")
        layer1 = c.addLineLayer(y_in, *zzz)
        layer1.setXData(times)
        
        # Set the line width to 3 pixels
        layer1.setLineWidth(1)
        
        
        # Add a green (0x33ff33) line layer using dataX1 and dataY1
        layer2 = c.addLineLayer(y_out, -1, "OUTPUT")
        layer2.setXData(times)
        
        # Set the line width to 3 pixels
        layer2.setLineWidth(1)
        

    
        # output the chart
        str = c.makeChart2(0)
        #im = PILImage.fromstring('RGB', sc.get_width_height(), sc.tostring_rgb(), 'raw', 'RGB', 0, 1)
        #imdata=StringIO()
        #im.save(open('zzz.jpg','wb'), format='JPEG')
        #im.save(imdata, format='JPEG')
        #qtbuf = QtCore.QBuffer()
        #qtbuf.open(QtCore.QIODevice.Truncate | QtCore.QIODevice.WriteOnly)
        
        #sc.print_png(qtbuf)

        #img = QtGui.QImage(qtbuf)
        #sc.print_png(qtbuf)
        #im.save(qtbuf, format='JPEG')
        #qtbuf.close()
        #qtbuf.open(QtCore.QIODevice.ReadOnly)
        img = QtGui.QImage()
        #img.load(qtbuf, 'JPEG')
        #img.load(qtbuf, 'png')
        img.loadFromData(str, 'png')
        tdoc = editor.document()
        tdoc.addResource(QtGui.QTextDocument.ImageResource, QtCore.QUrl("mytmi"), QtCore.QVariant(img))
        cursor.insertImage("mytmi")
        print time.clock() - testperf
        orderTableFormat = QtGui.QTextTableFormat()
        orderTableFormat.setAlignment(QtCore.Qt.AlignHCenter)
        orderTable = cursor.insertTable(1, 2, orderTableFormat)

        orderFrameFormat = cursor.currentFrame().frameFormat()
        orderFrameFormat.setBorder(1)
        cursor.currentFrame().setFrameFormat(orderFrameFormat)

        cursor = orderTable.cellAt(0, 0).firstCursorPosition()
        cursor.insertText(self.tr("Product"), boldFormat)
        cursor = orderTable.cellAt(0, 1).firstCursorPosition()
        cursor.insertText(self.tr("Quantity"), boldFormat)

        for item in orderItems:
            row = orderTable.rows()

            orderTable.insertRows(row, 1)
            cursor = orderTable.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(item[0], textFormat)
            cursor = orderTable.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(QtCore.QString("%1").arg(item[1]), textFormat)

        cursor.setPosition(topFrame.lastPosition())

        cursor.insertText(self.tr("Please update my records to take account of the "
                                  "following privacy information:"))
        cursor.insertBlock()

        offersTable = cursor.insertTable(2, 2)

        cursor = offersTable.cellAt(0, 1).firstCursorPosition()
        cursor.insertText(self.tr("I want to receive more information about your "
                                  "company's products and special offers."), textFormat)
        cursor = offersTable.cellAt(1, 1).firstCursorPosition()
        cursor.insertText(self.tr("I do not want to receive any promotional information "
                                  "from your company."), textFormat)

        if sendOffers:
            cursor = offersTable.cellAt(0, 0).firstCursorPosition()
        else:
            cursor = offersTable.cellAt(1, 0).firstCursorPosition()

        cursor.insertText("X", boldFormat)

        cursor.setPosition(topFrame.lastPosition())
        cursor.insertBlock()
        cursor.insertText(self.tr("Sincerely,"), textFormat)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(name)

        self.printAction.setEnabled(True)

    def createSample(self):
        dialog = DetailsDialog("Dialog with default values", self)
        self.createLetter("Mr Smith", "12 High Street\nSmall Town\nThis country",
                          dialog.orderItems(), True)

    def openDialog(self):
        dialog = DetailsDialog(self.tr("Enter Customer Details"), self)

        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.createLetter(dialog.senderName(), dialog.senderAddress(),
                              dialog.orderItems(), dialog.sendOffers())

    def printFile(self):
        editor = self.letters.currentWidget()
        document = editor.document()
        printer = QtGui.QPrinter()

        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return

        document.print_(printer)


class DetailsDialog(QtGui.QDialog):
    def __init__(self, title, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.items = QtCore.QStringList()

        nameLabel = QtGui.QLabel(self.tr("Name:"))
        addressLabel = QtGui.QLabel(self.tr("Address:"))

        self.nameEdit = QtGui.QLineEdit()
        self.addressEdit = QtGui.QTextEdit()
        self.addressEdit.setPlainText("")
        self.offersCheckBox = QtGui.QCheckBox(self.tr("Send offers:"))

        self.setupItemsTable()

        okButton = QtGui.QPushButton(self.tr("OK"))
        cancelButton = QtGui.QPushButton(self.tr("Cancel"))
        okButton.setDefault(True)

        self.connect(okButton, QtCore.SIGNAL("clicked()"), self.verify)
        self.connect(cancelButton, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))

        detailsLayout = QtGui.QGridLayout()
        detailsLayout.addWidget(nameLabel, 0, 0)
        detailsLayout.addWidget(self.nameEdit, 0, 1)
        detailsLayout.addWidget(addressLabel, 1, 0)
        detailsLayout.addWidget(self.addressEdit, 1, 1)
        detailsLayout.addWidget(self.itemsTable, 0, 2, 2, 2)
        detailsLayout.addWidget(self.offersCheckBox, 2, 1, 1, 4)

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(detailsLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle(title)

    def setupItemsTable(self):
        self.items << self.tr("T-shirt") << self.tr("Badge") \
                   << self.tr("Reference book") << self.tr("Coffee cup")

        self.itemsTable = QtGui.QTableWidget(self.items.count(), 2)

        for row in range(self.items.count()):
            name = QtGui.QTableWidgetItem(self.items[row])
            name.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.itemsTable.setItem(row, 0, name)
            quantity = QtGui.QTableWidgetItem("1")
            self.itemsTable.setItem(row, 1, quantity)

    def orderItems(self):
        orderList = []

        for row in range(self.items.count()):
            item = [None, None]
            item[0] = self.itemsTable.item(row, 0).text()
            quantity = self.itemsTable.item(row, 1).data(QtCore.Qt.DisplayRole).toInt()[0]
            item[1] = max(0, quantity)
            orderList.append(item)

        return orderList

    def senderName(self):
        return self.nameEdit.text()

    def senderAddress(self):
        return self.addressEdit.toPlainText()

    def sendOffers(self):
        return self.offersCheckBox.isChecked()

    def verify(self):
        if not self.nameEdit.text().isEmpty() and not self.addressEdit.toPlainText().isEmpty():
            self.accept()
            return

        answer = QtGui.QMessageBox.warning(self, self.tr("Incomplete Form"),
                    self.tr("The form does not contain all the necessary "
                            "information.\nDo you want to discard it?"),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if answer == QtGui.QMessageBox.Yes:
            self.reject()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    window.createSample()
    sys.exit(app.exec_()) 