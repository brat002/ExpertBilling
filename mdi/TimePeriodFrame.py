#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from helpers import Object as Object
from time import mktime

import datetime, calendar

class AddTimePeriod(QtGui.QDialog):
    def __init__(self, connection, nodemodel=None):
        super(AddTimePeriod, self).__init__()
        self.connection = connection
        self.connection.commit()
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
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "DAY", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "WEEK", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "MONTH", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "YEAR", None, QtGui.QApplication.UnicodeUTF8))


    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.nodemodel:
            model=self.nodemodel
        else:
            model=Object()
        try:
            
            model.name=unicode(self.name_edit.text())
            model.time_start=self.start_date_edit.dateTime().toPyDateTime()
    
            model.length=self.start_date_edit.dateTime().secsTo(self.end_date_edit.dateTime())
            #print model.length
            
            model.repeat_after=unicode(self.repeat_edit.currentText())
    
            if 'id' in model.__dict__:
                #Update
                self.connection.create(model.save("billservice_timeperiodnode"))
            else:
                #Insert
                self.nodemodel=model
                self.nodemodel.id = self.connection.create(model.save("billservice_timeperiodnode"))
                #print self.nodemodel.id
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()

        QtGui.QDialog.accept(self)

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




class TimePeriodChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(TimePeriodChild, self).__init__()
        self.connection = connection
        
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()).expandedTo(self.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0,0,691,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        #self.timeperiod_list_edit = QtGui.QListWidget(self.splitter)
        #self.timeperiod_list_edit = QtGui.QListWidget()
        #self.timeperiod_list_edit.setMaximumSize(QtCore.QSize(150,16777215))
        #self.timeperiod_list_edit.setObjectName("timeperiod_list_edit")

        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        tree_header = self.treeWidget.headerItem()
        tree_header.setHidden(True)
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget = tableFormat(self.tableWidget)
        self.setCentralWidget(self.splitter)
        

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
        
        #self.connect(self.timeperiod_list_edit, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.editPeriod)
        #self.connect(self.timeperiod_list_edit, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.refreshTable)

        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editPeriod)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refreshTable)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.delNodeLocalAction)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        self.addNodeLocalAction()
        self.delNodeLocalAction()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))
        #self.timeperiod_list_edit.clear()

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
        text = QtGui.QInputDialog.getText(self,u"Введите название периода", u"Название:", QtGui.QLineEdit.Normal);        
        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return

        model = Object()
        model.name=unicode(text[0])
        
        try:      
            self.connection.commit()
            if not self.connection.create(model.save(table="billservice_timeperiod")):
                QtGui.QMessageBox.warning(self, u"Ошибка",
                            u"Вероятно, такое название уже есть в списке.")
            self.connection.commit()
        except Exception, e:
            print e
            print "rollback"
            self.connection.rollback()
        
        self.refresh()

    def delPeriod(self):

        try:
            model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d" % self.getTimeperiodId())

        except:
            return

        if id>0 and QtGui.QMessageBox.question(self, u"Удалить период тарификации?" , u"Удалить период тарификации?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id='%d'" % model.id)
                self.connection.delete("DELETE FROM billservice_timeperiod WHERE id='%d'" % model.id)
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                
            #self.timeperiod_list_edit.setCurrentIndex(0)
            self.refresh()


    def editPeriod(self):
        model = self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d;" % self.getTimeperiodId())
        text = QtGui.QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QtGui.QLineEdit.Normal,model.name);

        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        try:
            model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d" % model.id)
            model.name=unicode(text[0])
            self.connection.create(model.save('billservice_timeperiod'))    
            self.conection.commit()            
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Введено недопустимое значение.")
            self.connection.rollback()
            return
        self.refresh()

    def addNode(self):

        try:
            model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d" % self.getTimeperiodId())
        except Exception, e:
            return
        #print model.id
        child=AddTimePeriod(connection=self.connection)
        if child.exec_()==1:
            try:
                self.connection.create("INSERT INTO billservice_timeperiod_time_period_nodes(timeperiod_id, timeperiodnode_id) VALUES(%d, %d)" % (model.id, child.nodemodel.id))
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                
            self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%d" % id)
                self.connection.delete("DELETE FROM billservice_timeperiodnode WHERE id=%d" % id)
                self.connection.commit()
            except Exception, e:
                self.connection.rollback()
            self.refreshTable()
        
    def editNode(self):
        id = self.getSelectedId()
        try:
            nodemodel = self.connection.get("SELECT * FROM billservice_timeperiodnode WHERE id=%d" % id)
        except:
            pass
        
        #name=unicode(self.getSelectedName())
        model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id = %d" % self.getTimeperiodId())
        if not model:
            return
        
        child=AddTimePeriod(connection=self.connection, nodemodel=nodemodel)
        if child.exec_()==1:
            
            self.refreshTable()
        
    def refreshTable(self, widget=None):
        if not widget:
            period_id=self.getTimeperiodId()
        else:
            period_id = widget.id
            
        self.tableWidget.clearContents()


        model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id = %d" % period_id)

        
        nodes = self.connection.sql("""SELECT * FROM billservice_timeperiodnode as timeperiodnode
        JOIN billservice_timeperiod_time_period_nodes as tpn ON tpn.timeperiodnode_id=timeperiodnode.id
        WHERE tpn.timeperiod_id=%d
        """ % model.id)
        self.tableWidget.setRowCount(len(nodes))
        i=0        
        for node in nodes:

            self.addrow(node.id, i,0)
            self.addrow(node.name, i,1)
            self.addrow(node.time_start.strftime("%d-%m-%Y %H:%M:%S"), i,2)
            self.addrow((node.time_start+datetime.timedelta(seconds=node.length)).strftime("%d-%m-%Y %H:%M:%S"), i,3)
            self.addrow(node.repeat_after, i,4)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.resizeColumnsToContents()




    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTimeperiodId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        

    def refresh(self):
        #self.timeperiod_list_edit.clear()
        self.treeWidget.clear()

        periods=self.connection.sql("SELECT * FROM billservice_timeperiod ORDER BY id ASC")
        for period in periods:
            #item = QtGui.QListWidgetItem(self.timeperiod_list_edit)
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            
            item.setText(0, period.name)
            item.id = period.id
            #self.timeperiod_list_edit.addItem(item)
            #self.
        
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delConsAction.setDisabled(True)
        else:
            self.delConsAction.setDisabled(False)


    def addNodeLocalAction(self):
        if self.treeWidget.currentItem() is None:
            self.addConsAction.setDisabled(True)
            self.delConsAction.setDisabled(True)
            self.delPeriodAction.setDisabled(True)
        else:
            self.addConsAction.setDisabled(False)
            self.delConsAction.setDisabled(False)
            self.delPeriodAction.setDisabled(False)
            

