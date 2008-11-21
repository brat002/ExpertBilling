#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import setFirstActive
from helpers import HeaderUtil, SplitterUtil
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

        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,278,198).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,278,198).size()))

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
        #Whats this
        self.name_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Название периода.", None, QtGui.QApplication.UnicodeUTF8))

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
    
            if model.hasattr('id'):
                #Update
                self.connection.save(model,"billservice_timeperiodnode")
            else:
                #Insert
                self.nodemodel=model
                self.nodemodel.id = self.connection.save(model, "billservice_timeperiodnode")
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
        self.setname = "time_frame_header"
        self.splname = "timeperiod_frame_splitter"
        bspltr = SplitterUtil.getBinarySplitter(self.splname)
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        super(TimePeriodChild, self).__init__()
        self.connection = connection
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.setObjectName("TimePeriodMDI")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()).expandedTo(self.minimumSizeHint()))
        
        #self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()))
        #self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()))

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setGeometry(QtCore.QRect(0,0,191,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")


        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget = tableFormat(self.tableWidget)
        
        
        tree_header = self.treeWidget.headerItem()
        tree_header.setText(0,QtGui.QApplication.translate("MainWindow", "Периоды", None, QtGui.QApplication.UnicodeUTF8))
        hght = self.tableWidget.horizontalHeader().maximumHeight()
        sz = QtCore.QSize()
        sz.setHeight(hght)
        tree_header.setSizeHint(0,sz)
        #tree_header.setHidden(True)
        self.setCentralWidget(self.splitter)
        self.splitter.setSizes([self.width() / 5, self.width() - (self.width() / 5)])
        
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,692,19))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))

        self.addPeriodAction = QtGui.QAction(self)
        self.addPeriodAction.setIcon(QtGui.QIcon("images/folder_add.png"))
        self.addPeriodAction.setObjectName("addPeriodAction")

        self.delPeriodAction = QtGui.QAction(self)
        self.delPeriodAction.setIcon(QtGui.QIcon("images/folder_delete.png"))
        self.delPeriodAction.setObjectName("delPeriodAction")

        self.addConsAction = QtGui.QAction(self)
        self.addConsAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addConsAction.setObjectName("addConsAction")

        self.delConsAction = QtGui.QAction(self)
        self.delConsAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delConsAction.setObjectName("delConsAction")
        
        self.editPeriodAction = QtGui.QAction(self)
        self.editPeriodAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editConsAction = QtGui.QAction(self)
        self.editConsAction.setIcon(QtGui.QIcon("images/open.png"))
        
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.treeWidget.addAction(self.editPeriodAction)
        self.treeWidget.addAction(self.addPeriodAction)
        self.treeWidget.addAction(self.delPeriodAction)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.addAction(self.editConsAction)
        self.tableWidget.addAction(self.addConsAction)
        self.tableWidget.addAction(self.delConsAction)
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.addAction(self.addPeriodAction)
        self.toolBar.addAction(self.delPeriodAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addConsAction)
        self.toolBar.addAction(self.delConsAction)
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.splitter, QtCore.SIGNAL("splitterMoved(int,int)"), self.saveSplitter)
        
        self.retranslateUi()

        self.refresh()
        
        try:
            setFirstActive(self.treeWidget)
            HeaderUtil.nullifySaved(self.setname)
            SplitterUtil.nullifySaved(self.splname)
            self.refreshTable()
            self.tableWidget = tableFormat(self.tableWidget)
            if not bhdr.isEmpty():
                HeaderUtil.setBinaryHeader(self.setname, bhdr)
                HeaderUtil.getHeader(self.setname, self.tableWidget)
            if not bspltr.isEmpty():
                SplitterUtil.setBinarySplitter(self.splname, bspltr)
                SplitterUtil.getSplitter(self.splname, self.splitter)
        except Exception, ex:
            print "Error when setting first element active: ", ex
            pass
        #self.treeWidget.setCurrentItem(self.treeWidget.headerItem().child(1))
        #print self.treeWidget.headerItem().childCount()
        #print self.treeWidget.currentItem()
        #print self.treeWidget.indexOfTopLevelItem()
        #self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
        self.connect(self.addPeriodAction, QtCore.SIGNAL("triggered()"), self.addPeriod)
        self.connect(self.delPeriodAction, QtCore.SIGNAL("triggered()"), self.delPeriod)
        
        self.connect(self.addConsAction, QtCore.SIGNAL("triggered()"),  self.addNode)
        self.connect(self.delConsAction, QtCore.SIGNAL("triggered()"),  self.delNode)

        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editPeriod)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refreshTable)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.connect(self.editPeriodAction, QtCore.SIGNAL("triggered()"), self.editPeriod)
        self.connect(self.editConsAction, QtCore.SIGNAL("triggered()"), self.editNode)
        
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        self.addNodeLocalAction()
        self.delNodeLocalAction()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.clear()
        columns=['Id', u'Название', u'Начало', u'Окончание', u'Повторяется через']
        makeHeaders(columns, self.tableWidget)
        
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.addPeriodAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить период", None, QtGui.QApplication.UnicodeUTF8))
        self.delPeriodAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить период", None, QtGui.QApplication.UnicodeUTF8))
        self.addConsAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить составляющую", None, QtGui.QApplication.UnicodeUTF8))
        self.delConsAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить составляющую", None, QtGui.QApplication.UnicodeUTF8))
        self.editPeriodAction.setText(QtGui.QApplication.translate("MainWindow", "Редактировать", None, QtGui.QApplication.UnicodeUTF8))
        self.editConsAction.setText(QtGui.QApplication.translate("MainWindow", "Редактировать", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.setColumnHidden(0, True)

    def addPeriod(self):
        
        text = QtGui.QInputDialog.getText(self,u"Введите название периода", u"Название:", QtGui.QLineEdit.Normal);
        print text        
        if text[0].isEmpty()==True and text[1]==True:
            QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return
        elif text[1]==False:
            return

        model = Object()
        model.name=unicode(text[0])
        
        try:      
            self.connection.commit()
            if not self.connection.save(model, "billservice_timeperiod"):
                QtGui.QMessageBox.warning(self, u"Ошибка",
                            u"Вероятно, такое название уже есть в списке.")
            self.connection.commit()
        except Exception, e:
            print e
            print "rollback"
            self.connection.rollback()
        
        self.refresh()

    def delPeriod(self):

        '''try:
            model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d" % self.getTimeperiodId())

        except:
            return'''
        id = self.getTimeperiodId()
        
        if id>0:
            if self.connection.sql("""SELECT access_time_id FROM billservice_accessparameters WHERE (access_time_id=%d) UNION SELECT time_period_id FROM billservice_timeaccessnode WHERE (time_period_id=%d) UNION SELECT time_id FROM billservice_timespeed WHERE (time_id=%d)""" % (id, id, id)):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление невозможно, тарифный план используется!")
                return
            elif QtGui.QMessageBox.question(self, u"Удалить период тарификации?" , u"Удалить период тарификации?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id='%d'" % model.id)
                    #self.connection.delete("DELETE FROM billservice_timeperiod WHERE id='%d'" % model.id)
                    #self.connection.sql("UPDATE billservice_timeperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete("billservice_timeperiod", id)
                    self.connection.commit()
                    self.refresh()
                    try:
                        setFirstActive(self.treeWidget)
                        self.refreshTable()
                    except Exception, ex:
                        print ex
                except Exception, e:
                    print e
                    self.connection.rollback()
                
            #self.timeperiod_list_edit.setCurrentIndex(0)


    def editPeriod(self):
        model = self.connection.get_model(self.getTimeperiodId(), "billservice_timeperiod;")
        text = QtGui.QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QtGui.QLineEdit.Normal,model.name);

        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        try:
            model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id=%d" % model.id)
            model.name=unicode(text[0])
            self.connection.save(model, 'billservice_timeperiod')    
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
                self.connection.save("INSERT INTO billservice_timeperiod_time_period_nodes(timeperiod_id, timeperiodnode_id) VALUES(%d, %d)" % (model.id, child.nodemodel.id))
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                
            self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()

        if id >0 and QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%d" % id)
                #self.connection.delete("DELETE FROM billservice_timeperiodnode WHERE id=%d" % id)
                #self.connection.sql("UPDATE billservice_timeperiodnode SET deleted=TRUE WHERE id=%d" % id, False)
                self.connection.iddelete("billservice_timeperiodnode", id)
                self.connection.commit()
                self.refreshTable()
            except Exception, e:
                self.connection.rollback()

            
        
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
        self.connection.commit()
        child=AddTimePeriod(connection=self.connection, nodemodel=nodemodel)
        if child.exec_()==1:
            
            self.refreshTable()
        
    def refreshTable(self, widget=None):
        self.tableWidget.setSortingEnabled(False)
        if not widget:
            period_id=self.getTimeperiodId()
        else:
            period_id = widget.id
            
        self.tableWidget.clearContents()


        #model=self.connection.get("SELECT * FROM billservice_timeperiod WHERE id = %d" % period_id)

        
        nodes = self.connection.sql("""SELECT * FROM billservice_timeperiodnode as timeperiodnode
        JOIN billservice_timeperiod_time_period_nodes as tpn ON tpn.timeperiodnode_id=timeperiodnode.id
        WHERE tpn.timeperiod_id=%d
        """ % period_id)
        self.connection.commit()
        self.tableWidget.setRowCount(len(nodes))
        i=0        
        for node in nodes:

            self.addrow(node.id, i,0)
            self.addrow(node.name, i,1)
            self.addrow(node.time_start.strftime(self.strftimeFormat), i,2)
            self.addrow((node.time_start+datetime.timedelta(seconds=node.length)).strftime(self.strftimeFormat), i,3)
            self.addrow(node.repeat_after, i,4)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)



    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname, self.tableWidget)
    def saveSplitter(self, *args):
        SplitterUtil.saveSplitter(self.splname, self.splitter)    
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTimeperiodId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        self.tableWidget.setItem(x,y,headerItem)
        

    def refresh(self):
        #self.timeperiod_list_edit.clear()
        curItem = -1
        try:
            curItem = self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())
        except Exception, ex:
            print ex
        self.treeWidget.clear()
        periods=self.connection.get_models("billservice_timeperiod")
        self.connection.commit()
        for period in periods:
            #item = QtGui.QListWidgetItem(self.timeperiod_list_edit)
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            item.setText(0, period.name)
            item.id = period.id
        if curItem != -1:
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(curItem))
            
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
            

