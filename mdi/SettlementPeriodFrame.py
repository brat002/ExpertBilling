#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import SettlementPeriod
from nas.models import IPAddressPool, Nas
import datetime, calendar
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

class AddSettlementPeriod(QtGui.QDialog):
    def __init__(self, model=None):
        super(AddSettlementPeriod, self).__init__()
        self.model=model

        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,410,156).size()).expandedTo(self.minimumSizeHint()))

        self.start_label = QtGui.QLabel(self)
        self.start_label.setGeometry(QtCore.QRect(12,67,73,20))
        self.start_label.setObjectName("start_label")

        self.autostart_checkbox = QtGui.QCheckBox(self)
        self.autostart_checkbox.setGeometry(QtCore.QRect(12,43,390,18))
        self.autostart_checkbox.setObjectName("autostart_checkbox")

        self.datetime_edit = QtGui.QDateTimeEdit(self)
        self.datetime_edit.setGeometry(QtCore.QRect(91,67,130,20))
        self.datetime_edit.setFrame(True)
        self.datetime_edit.setCurrentSection(QtGui.QDateTimeEdit.DaySection)
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setObjectName("datetime_edit")

        self.length_seconds_edit = QtGui.QLineEdit(self)
        self.length_seconds_edit.setGeometry(QtCore.QRect(227,93,133,20))
        self.length_seconds_edit.setObjectName("length_seconds_edit")


        self.length_label = QtGui.QLabel(self)
        self.length_label.setGeometry(QtCore.QRect(12,93,73,20))
        self.length_label.setObjectName("length_label")

        self.length_edit = QtGui.QComboBox(self)
        self.length_edit.setGeometry(QtCore.QRect(91,93,130,20))
        self.length_edit.setObjectName("length_edit")

        self.seconds_label = QtGui.QLabel(self)
        self.seconds_label.setGeometry(QtCore.QRect(366,93,36,20))
        self.seconds_label.setObjectName("seconds_label")

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20,120,375,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.name_label = QtGui.QLabel(self)
        self.name_label.setGeometry(QtCore.QRect(12,10,73,20))
        self.name_label.setObjectName("name_label")

        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setGeometry(QtCore.QRect(91,10,311,20))
        self.name_edit.setObjectName("name_edit")
        self.start_label.setBuddy(self.datetime_edit)
        self.length_label.setBuddy(self.length_edit)
        self.seconds_label.setBuddy(self.length_seconds_edit)
        self.name_label.setBuddy(self.name_edit)

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)

        self.connect(self.autostart_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.checkbox_behavior)
        self.connect(self.length_edit, QtCore.SIGNAL("currentIndexChanged(int)"), self.length_behavior)


        #QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.setTabOrder(self.name_edit,self.autostart_checkbox)
        self.setTabOrder(self.autostart_checkbox,self.datetime_edit)
        self.setTabOrder(self.datetime_edit,self.length_edit)
        self.setTabOrder(self.length_edit,self.length_seconds_edit)
        self.setTabOrder(self.length_seconds_edit,self.buttonBox)

        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало в", None, QtGui.QApplication.UnicodeUTF8))
        self.autostart_checkbox.setText(QtGui.QApplication.translate("Dialog", "Период начинается при назначении пользователю тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.length_label.setText(QtGui.QApplication.translate("Dialog", "Длительность", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "DAY", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "WEEK", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "MONTH", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "YEAR", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "DONT_REPEAT", None, QtGui.QApplication.UnicodeUTF8))
        self.length_edit.addItem(QtGui.QApplication.translate("Dialog", "---", None, QtGui.QApplication.UnicodeUTF8))
        self.seconds_label.setText(QtGui.QApplication.translate("Dialog", "секунд", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))





    def checkbox_behavior(self):
        if self.autostart_checkbox.checkState()==2:
            self.datetime_edit.setEnabled(False)
        else:
            self.datetime_edit.setEnabled(True)

    def length_behavior(self):
        if self.length_edit.currentText()==u"---":
            self.length_seconds_edit.setEnabled(True)
            self.length_seconds_edit.setText("")
        else:
            self.length_seconds_edit.setEnabled(False)



    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:
            model=self.model
        else:
            print 'New sp'
            model=SettlementPeriod()

        if unicode(self.name_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано название"))
            return
        else:
            model.name=unicode(self.name_edit.text())

        if unicode(self.length_edit.currentText())==u"---" and self.length_seconds_edit.text()==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указаны параметры длительности расчётного периода"))
            return
        elif unicode(self.length_edit.currentText())==u"---" :
            model.length=int(unicode(self.length_seconds_edit.text()))
            model.length_in=""
        else:
            model.length_in=unicode(self.length_edit.currentText())
            model.length=0

        model.autostart = self.autostart_checkbox.checkState() == 2

        model.time_start=self.datetime_edit.dateTime().toPyDateTime()

        try:
            model.save()
        except Exception, e:
            print e
            return



        QDialog.accept(self)

    def fixtures(self):
        now=datetime.datetime.now()
        if self.model:
            self.name_edit.setText(unicode(self.model.name))
            self.autostart_checkbox.setCheckState(self.model.autostart == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            if self.model.autostart == True:
                self.datetime_edit.setEnabled(False)

            now = QtCore.QDateTime()

            now.setTime_t(calendar.timegm(self.model.time_start.timetuple()))




            if self.model.length_in=="":
                self.length_edit.setCurrentIndex(self.length_edit.findText("---", QtCore.Qt.MatchCaseSensitive))
                self.length_seconds_edit.setText(unicode(self.model.length))
            else:
                self.length_edit.setCurrentIndex(self.length_edit.findText(self.model.length_in, QtCore.Qt.MatchCaseSensitive))
                self.length_seconds_edit.setEnabled(False)

        self.datetime_edit.setDateTime(now)

    def save(self):
        print 'Saved'



class SettlementPeriodChild(QMainWindow):
    sequenceNumber = 1

    def __init__(self):
        super(SettlementPeriodChild, self).__init__()


        self.resize(QtCore.QSize(QtCore.QRect(0,0,827,476).size()).expandedTo(self.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0,0,821,401))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setLineWidth(1)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setObjectName("tableWidget")
        self.setCentralWidget(self.tableWidget)
        vh = self.tableWidget.verticalHeader()
        vh.setVisible(False)
        hh = self.tableWidget.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        #hh.setClickable(False)
        hh.ResizeMode(QtGui.QHeaderView.Stretch)
        hh.setMovable(True)

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,827,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.addAction = QtGui.QAction(self)
        self.addAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addAction.setObjectName("addAction")

        self.delAction = QtGui.QAction(self)
        self.delAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delAction.setObjectName("delAction")
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)

        self.retranslateUi()
        self.refresh()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.connect(self.addAction,  QtCore.SIGNAL("triggered()"), self.add_period)
        self.connect(self.delAction,  QtCore.SIGNAL("triggered()"), self.del_period)

        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_period)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Расчётные периоды", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("MainWindow", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "Начало при активации", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Дата и время начала", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "Продолжительность в периодах", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        headerItem5.setText(QtGui.QApplication.translate("MainWindow", "Продолжительность в секундах", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem5)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.delAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))

    def add_period(self):
        child=AddSettlementPeriod()
        child.exec_()
        self.refresh()

    def del_period(self):
        id=self.getSelectedId()
        try:
            model=SettlementPeriod.objects.get(id=id)
        except:
            return

        if id>0 and QMessageBox.question(self, u"Удалить расчётный период?" , u"Все связанные тарифные планы и вся статистика будут удалены.\nВы уверены, что хотите это сделать?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            model.delete()

        self.refresh()


    def edit_period(self):
        id=self.getSelectedId()
        try:
            model=SettlementPeriod.objects.get(id=id)
        except:
            return


        child=AddSettlementPeriod(model=model)
        child.exec_()

        self.refresh()


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def editframe(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=Nas.objects.get(id=self.getSelectedId())
        except:
            model=None

        addf = AddNasFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)

    def refresh(self):

        periods=SettlementPeriod.objects.all().order_by('id')
        self.tableWidget.setRowCount(periods.count())
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for period in periods:
            self.addrow(period.id, i,0)
            self.addrow(period.name, i,1)
            self.addrow(period.autostart, i,2)
            self.addrow(period.time_start, i,3)
            self.addrow(period.length_in, i,4)
            self.addrow(period.length, i,5)
            self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)


            i+=1
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.rowHeight(10)

    def newFile(self):
        self.isUntitled = True
        #self.curFile = self.tr("iplist").arg(MdiChild.sequenceNumber)
        #MdiChild.sequenceNumber += 1
        #self.setWindowTitle(self.curFile+"[*]")

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                        self.tr("Cannot read file %1:\n%2.")
                        .arg(fileName)
                        .arg(file.errorString()))
            return False

        instr = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPlainText(instr.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def save(self):
        if self.isUntitled:
            return self.saveAs()
        else:
            return self.saveFile(self.curFile)

    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),
                        self.curFile)
        if fileName.isEmpty:
            return False

        return self.saveFile(fileName)

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)

        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("Cannot write file %1:\n%2.")
                    .arg(fileName)
                    .arg(file.errorString()))
            return False

        outstr = QtCore.QTextStream(file)
        QtCore.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outstr << self.toPlainText()
        QtCore.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def userFriendlyCurrentFile(self):
        return self.strippedName(self.curFile)

    def currentFile(self):
        return self.curFile

    def closeEvent(self, event):
        #if self.maybeSave():
        #    event.accept()
        #else:
        #    event.ignore()
        pass

    def documentWasModified(self):
        self.setWindowModified(self.document().isModified())

    def maybeSave(self):
        if self.document().isModified():
            ret = QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("'%1' has been modified.\n"\
                            "Do you want to save your changes?")
                    .arg(self.userFriendlyCurrentFile()),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
            if ret == QtGui.QMessageBox.Yes:
                return self.save()
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def setCurrentFile(self, fileName):
        self.curFile = QtCore.QFileInfo(fileName).canonicalFilePath()
        self.isUntitled = False
        self.document().setModified(False)
        self.setWindowModified(False)
        self.setWindowTitle(self.userFriendlyCurrentFile() + "[*]")

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()


