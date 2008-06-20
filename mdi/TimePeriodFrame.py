#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import TimePeriod, TimePeriodNode
from time import mktime
import datetime, calendar
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

class AddTimePeriod(QtGui.QDialog):
    def __init__(self, timemodel, nodemodel=None):
        super(AddTimePeriod, self).__init__()
        self.timemodel=timemodel
        self.nodemodel=nodemodel
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,278,198).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(110,160,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10,10,197,16))
        self.label.setObjectName("label")

        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(10,30,261,131))
        self.widget.setObjectName("widget")

        self.gridlayout = QtGui.QGridLayout(self.widget)
        self.gridlayout.setObjectName("gridlayout")

        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,0,0,1,1)

        self.name_edit = QtGui.QLineEdit(self.widget)
        self.name_edit.setObjectName("name_edit")
        self.gridlayout.addWidget(self.name_edit,0,1,1,1)

        self.start_label = QtGui.QLabel(self.widget)
        self.start_label.setObjectName("start_label")
        self.gridlayout.addWidget(self.start_label,1,0,1,1)

        self.start_date_edit = QtGui.QDateTimeEdit(self.widget)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setObjectName("start_date_edit")
        self.gridlayout.addWidget(self.start_date_edit,1,1,1,1)

        self.end_label = QtGui.QLabel(self.widget)
        self.end_label.setObjectName("end_label")
        self.gridlayout.addWidget(self.end_label,2,0,1,1)

        self.end_date_edit = QtGui.QDateTimeEdit(self.widget)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setObjectName("end_date_edit")
        self.gridlayout.addWidget(self.end_date_edit,2,1,1,1)

        self.repeat_label = QtGui.QLabel(self.widget)
        self.repeat_label.setObjectName("repeat_label")
        self.gridlayout.addWidget(self.repeat_label,3,0,1,1)

        self.repeat_edit = QtGui.QComboBox(self.widget)
        self.repeat_edit.setObjectName("repeat_edit")
        self.gridlayout.addWidget(self.repeat_edit,3,1,1,1)

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Период времени", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<b>Укажите временной промежуток</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Окончание", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_label.setText(QtGui.QApplication.translate("Dialog", "Повторять через", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Сутки", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Месяц", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Год", None, QtGui.QApplication.UnicodeUTF8))


    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.nodemodel:
            model=self.nodemodel
        else:
            print 'New sp'
            model=TimePeriodNode()
        
        model.name=unicode(self.name_edit.text())
        model.time_start=self.start_date_edit.dateTime().toPyDateTime()

        model.length=self.start_date_edit.dateTime().secsTo(self.end_date_edit.dateTime())
        print model.length
        
        model.repeat_after=unicode(self.repeat_edit.currentText())
        try:
            id=model.id
            model.save()
            #Если редактируем
            if not id:
                self.timemodel.time_period_nodes.add(model)
        except Exception, e:
            print e
            return



        QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        end=datetime.datetime.now()

        if self.nodemodel:
            self.name_edit.setText(unicode(self.nodemodel.name))
    
            start = QtCore.QDateTime()

            start.setTime_t(int(mktime(self.nodemodel.time_start.timetuple())))

            end = QtCore.QDateTime()
            end.setTime_t(int(mktime((self.nodemodel.time_start+datetime.timedelta(seconds=self.nodemodel.length)).timetuple())))

            self.repeat_edit.setCurrentIndex(self.repeat_edit.findText(self.nodemodel.repeat_after, QtCore.Qt.MatchCaseSensitive))
            
    

        self.start_date_edit.setDateTime(start)
        self.end_date_edit.setDateTime(end)

    def save(self):
        print 'Saved'



class TimePeriodChild(QMainWindow):
    sequenceNumber = 1

    def __init__(self):
        super(TimePeriodChild, self).__init__()
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()).expandedTo(self.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0,0,691,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.timeperiod_list_edit = QtGui.QListWidget(self.splitter)
        self.timeperiod_list_edit.setMaximumSize(QtCore.QSize(150,16777215))
        self.timeperiod_list_edit.setObjectName("timeperiod_list_edit")

        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setCentralWidget(self.splitter)
        
        vh = self.tableWidget.verticalHeader()
        vh.setVisible(False)

        hh = self.tableWidget.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        #hh.setClickable(False)
        hh.ResizeMode(QtGui.QHeaderView.Stretch)
        #hh.setCascadingSectionResizes(True)
        hh.setMovable(True)
        print hh.offset()

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,692,19))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.addPeriodAction = QtGui.QAction(self)
        self.addPeriodAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addPeriodAction.setObjectName("addPeriodAction")

        self.delPeriodAction = QtGui.QAction(self)
        self.delPeriodAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delPeriodAction.setObjectName("delPeriodAction")

        self.addConsAction = QtGui.QAction(self)
        self.addConsAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addConsAction.setObjectName("addConsAction")

        self.delConsAction = QtGui.QAction(self)
        self.delConsAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delConsAction.setObjectName("delConsAction")
        self.toolBar.addAction(self.addPeriodAction)
        self.toolBar.addAction(self.delPeriodAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addConsAction)
        self.toolBar.addAction(self.delConsAction)

        self.retranslateUi()
        self.refresh()
        self.connect(self.addPeriodAction, QtCore.SIGNAL("triggered()"), self.addPeriod)
        self.connect(self.delPeriodAction, QtCore.SIGNAL("triggered()"), self.delPeriod)
        
        self.connect(self.addConsAction, QtCore.SIGNAL("triggered()"),  self.addNode)
        self.connect(self.delConsAction, QtCore.SIGNAL("triggered()"),  self.delNode)
        
        self.connect(self.timeperiod_list_edit, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.editPeriod)
        self.connect(self.timeperiod_list_edit, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.refreshTable)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.timeperiod_list_edit.clear()

        self.tableWidget.clear()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("MainWindow", "id", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "Повторять через", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem4)
        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem4)
        
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.addPeriodAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить период", None, QtGui.QApplication.UnicodeUTF8))
        self.delPeriodAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить период", None, QtGui.QApplication.UnicodeUTF8))
        self.addConsAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить составляющую", None, QtGui.QApplication.UnicodeUTF8))
        self.delConsAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить составляющую", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, True)

    def addPeriod(self):
        text = QInputDialog.getText(self,u"Введите название периода", u"Название:", QLineEdit.Normal);        
        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return
            
        try:
            TimePeriod.objects.create(name=unicode(text[0]))
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Вероятно, такое название уже есть в списке.")
            return

        
        self.refresh()

    def delPeriod(self):
        name=self.getSelectedName()
        try:
            model=TimePeriod.objects.get(name=unicode(name))
        except:
            return

        if id>0 and QMessageBox.question(self, u"Удалить период тарификации?" , u"Удалить период тарификации?\nВместе с ним будут удалены все его составляющие.", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            model.delete()

        self.refresh()


    def editPeriod(self):
        name=unicode(self.getSelectedName())
        text = QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QLineEdit.Normal,name);
        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        try:
            model=TimePeriod.objects.get(name=name)
            model.name=unicode(text[0])
            model.save()                
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Введено недопустимое значение.")
            return
        self.refresh()

    def addNode(self):
        name=self.getSelectedName()
        try:
            model=TimePeriod.objects.get(name=unicode(name))
        except:
            return

        child=AddTimePeriod(timemodel=model)
        child.exec_()
        self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()
        try:
            nodemodel = TimePeriodNode.objects.get(id=id)
        except:
            return
        if QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            nodemodel.delete()
            self.refreshTable()
        
    def editNode(self):
        id = self.getSelectedId()
        try:
            nodemodel = TimePeriodNode.objects.get(id=id)
        except:
            pass
        
        name=self.getSelectedName()
        try:
            model=TimePeriod.objects.get(name=unicode(name))
        except:
            return
        
        child=AddTimePeriod(timemodel=model, nodemodel=nodemodel)
        child.exec_()
        self.refreshTable()
        
    def refreshTable(self, widget=None):
        if not widget:
            text=unicode(self.getSelectedName())
        else:
            text=unicode(widget.text())
        self.tableWidget.clearContents()
        #print text
        model=TimePeriod.objects.get(name=text)

        self.tableWidget.setRowCount(model.time_period_nodes.count())
        i=0        
        for node in model.time_period_nodes.all().order_by('id'):

            self.addrow(node.id, i,0)
            self.addrow(node.name, i,1)
            self.addrow(node.time_start.strftime("%d-%m-%Y %H:%M:%S"), i,2)
            self.addrow((node.time_start+datetime.timedelta(seconds=node.length)).strftime("%d-%m-%Y %H:%M:%S"), i,3)
            self.addrow(node.repeat_after, i,4)
            
            self.tableWidget.setRowHeight(i, 17)
            #self.tableWidget.setColumnHidden(0, True)
# 
 
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.rowHeight(10)


        #child=AddSettlementPeriod(model=model)
        #child.exec_()

        #self.refresh()


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getSelectedName(self):
        return self.timeperiod_list_edit.currentItem().text()
    
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
        self.timeperiod_list_edit.clear()

        periods=TimePeriod.objects.all().order_by('id')

        for period in periods:
            item = QtGui.QListWidgetItem(self.timeperiod_list_edit)
            item.setText(period.name)
            self.timeperiod_list_edit.addItem(item)
        

        

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


