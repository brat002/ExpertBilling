import Pyro.errors
#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import setFirstActive
from helpers import HeaderUtil, SplitterUtil
from ebsWindow import ebsTable_n_TreeWindow
from time import mktime
from helpers import dateDelim
import datetime, calendar

class TimePeriodSelect(QtGui.QDialog):
    def __init__(self, connection, exclude):
        super(TimePeriodSelect, self).__init__()
        self.connection=connection
        self.models = []
        self.exclude=exclude
        self.setObjectName("TimePeriodSelect")
        bhdr = HeaderUtil.getBinaryHeader(self.objectName())
        self.resize(577, 434)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        self.firsttime = True
        HeaderUtil.nullifySaved(self.objectName())
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.objectName(), bhdr)
            HeaderUtil.getHeader(self.objectName(), self.tableWidget)
        else: self.firsttime = False
        
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.objectName(), self.tableWidget)
            
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Существующие составляющие", None, QtGui.QApplication.UnicodeUTF8))

        columns=(u"#", u"Название", u"Начало", u"Конец", u"Период повторения")
        makeHeaders(columns, self.tableWidget)
        
    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if y!=0:
            headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
                                 
    def fixtures(self):
        nodes = self.connection.get_models("billservice_timeperiodnode")
        self.connection.commit()
        #self.tableWidget.setRowCount(len(nodes))
        i=0
        
        for x in nodes:
            if x.id in self.exclude: continue
            self.tableWidget.insertRow(i)
            self.addrow(x.id, i, 0)
            self.addrow(x.name, i, 1)
            self.addrow(x.time_start.strftime(self.strftimeFormat), i, 2)
            self.addrow((x.time_start+datetime.timedelta(seconds=x.length)).strftime(self.strftimeFormat), i, 3)
            self.addrow(x.repeat_after, i, 4)
            i+=1
    def accept(self):
        for x in xrange(self.tableWidget.rowCount()):
            if self.tableWidget.item(x,0).checkState()==QtCore.Qt.Checked:
                self.models.append(self.tableWidget.item(x,0).id)
        QtGui.QDialog.accept(self)
        
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
            #print unicode(self.nodemodel.name)
            self.name_edit.setText(unicode(self.nodemodel.name))
    
            start = QtCore.QDateTime()

            start.setTime_t(int(mktime(self.nodemodel.time_start.timetuple())))

            end = QtCore.QDateTime()
            end.setTime_t(int(mktime((self.nodemodel.time_start+datetime.timedelta(seconds=self.nodemodel.length)).timetuple())))

            self.repeat_edit.setCurrentIndex(self.repeat_edit.findText(self.nodemodel.repeat_after, QtCore.Qt.MatchCaseSensitive))
            
    

        self.start_date_edit.setDateTime(start)
        self.end_date_edit.setDateTime(end)




class TimePeriodChildEbs(ebsTable_n_TreeWindow):
    def __init__(self, connection):
        columns  = ['Id', u'Название', u'Начало', u'Окончание', u'Повторяется через']
        initargs = {"setname":"timeperiod_frame", "objname":"TimePeriodChildEbs", "winsize":(0,0,692,483), "wintitle":"Периоды тарификации", "tablecolumns":columns, "spltsize":(0,0,191,411), "treeheader":"Периоды", "menubarsize":(0,0,692,19), "tbiconsize":(18,18)}
        
        super(TimePeriodChildEbs, self).__init__(connection, initargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        
    def ebsInterInit(self, initargs):
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        self.refreshTree = self.refresh
        #self.refresh_ = self.refresh
        
        self.getTimeperiodId = self.getTreeId
        
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refreshTable)        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editPeriod)  
             
        actList=[("addPeriodAction", "Добавить период", "images/folder_add.png", self.addPeriod), \
                 ("delPeriodAction", "Удалить период", "images/folder_delete.png", self.delPeriod), \
                 ("editPeriodAction", "Редактировать", "images/open.png", self.editPeriod), \
                 ("addConsAction", "Добавить составляющую", "images/add.png", self.addNode), \
                 ("delConsAction", "Удалить составляющую", "images/del.png", self.delNode), \
                 ("editConsAction", "Редактировать", "images/open.png", self.editNode),
                 ("selectConsAction", "Выбрать из списка", "images/open.png", self.selectNode)
                ]



        objDict = {self.treeWidget :["editPeriodAction", "addPeriodAction", "delPeriodAction"], \
                   self.tableWidget:["editConsAction", "addConsAction", "delConsAction"], \
                   self.toolBar    :["addPeriodAction", "delPeriodAction", "separator", "addConsAction", "delConsAction","selectConsAction"]
                  }
        self.actionCreator(actList, objDict)
        
    def ebsPostInit(self, initargs):        

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.connectTree()
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        self.restoreWindow()
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
    def retranslateUI(self, initargs):
        super(TimePeriodChildEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Периоды тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, True)
        
    def addNodeLocalAction(self):
        super(TimePeriodChildEbs, self).addNodeLocalAction([self.addConsAction, self.delConsAction, self.delPeriodAction])
    def delNodeLocalAction(self):
        super(TimePeriodChildEbs, self).delNodeLocalAction([self.delConsAction])
        self.tableWidget.setColumnHidden(0, True)
        
    def selectNode(self):
        a=[]
        for x in xrange(self.tableWidget.rowCount()):
            a.append(self.tableWidget.item(x,0).id)
        
        child=TimePeriodSelect(connection=self.connection, exclude = a)
        if child.exec_()==1:
            #print "nodes len", len(child.models)
            for node in child.models:
                o = Object()
                o.timeperiod_id=self.getTimeperiodId()
                o.timeperiodnode_id = node
                self.connection.save(o, "billservice_timeperiod_time_period_nodes")
            self.refresh()
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
            if self.connection.sql("SELECT access_time_id FROM billservice_accessparameters WHERE access_time_id=%d" % id):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление невозможно, тарифный план используется!")
                return
            elif QtGui.QMessageBox.question(self, u"Удалить период тарификации?" , u"Удалить период тарификации?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id='%d'" % model.id)
                    #self.connection.delete("DELETE FROM billservice_timeperiod WHERE id='%d'" % model.id)
                    #self.connection.sql("UPDATE billservice_timeperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_timeperiod")
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
        model = self.connection.get_model(self.getTimeperiodId(), "billservice_timeperiod")

        text = QtGui.QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QtGui.QLineEdit.Normal,model.name)

        if text[0].isEmpty()==True and text[1]==True:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        if text[1]==False:
            return
        try:
            model=self.connection.get_model(model.id, "billservice_timeperiod")
            model.name=unicode(text[0])
            self.connection.save(model, 'billservice_timeperiod')    
            self.connection.commit()            
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
                node = Object()
                node.timeperiod_id = model.id
                node.timeperiodnode_id = child.nodemodel.id
                self.connection.save(node, "billservice_timeperiod_time_period_nodes")
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                
            self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()

        if id > 0 and QtGui.QMessageBox.question(self, u"Удалить запись?", u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%d" % id)
                #self.connection.delete("DELETE FROM billservice_timeperiodnode WHERE id=%d" % id)
                #self.connection.sql("UPDATE billservice_timeperiodnode SET deleted=TRUE WHERE id=%d" % id, False)
                self.connection.command("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%s and timeperiod_id=%s;" % (id, self.getTimeperiodId()))
                #Проверяем используется ли ещё где-нибудь
                nums = self.connection.sql("SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%s;" % id)
                self.connection.commit()
                if not nums:
                    #Если не используется-удаляем
                    self.connection.iddelete(id, "billservice_timeperiodnode")
                    self.connection.commit()
                self.refreshTable()
            except Exception, e:
                print e
                self.connection.rollback()

            
        
    def editNode(self):
        id = self.getSelectedId()
        #print id
        
        try:
            nodemodel = self.connection.get_model(unicode(self.getSelectedId()), "billservice_timeperiodnode")
            #nodemodel = self.connection.sql("SELECT * FROM billservice_timeperiodnode WHERE id=%d;" % int(id))[0]
        except Exception, e:
            import Pyro.util
            print ''.join(Pyro.util.getPyroTraceback(e))

        
        #name=unicode(self.getSelectedName())
        model=self.connection.get_model(self.getTimeperiodId(), "billservice_timeperiod")
        if not model:
            return
        self.connection.commit()
        child=AddTimePeriod(connection=self.connection, nodemodel=nodemodel)
        if child.exec_()==1:
            
            self.refreshTable()
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
    def refreshTable(self, widget=None):
        self.tableWidget.setSortingEnabled(False)
        if not widget:
            period_id=self.getTimeperiodId()
        else:
            period_id = widget.id
            
        self.tableWidget.clearContents()
        
        nodes = self.connection.sql("""SELECT * FROM billservice_timeperiodnode as timeperiodnode
        WHERE id IN (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=%s)""" % period_id)
        self.connection.commit()
        self.tableWidget.setRowCount(len(nodes))
        i=0        
        for node in nodes:
            #print "node_id=", node.id
            self.addrow(node.id, i,0)
            self.addrow(node.name, i,1)
            self.addrow(node.time_start.strftime(self.strftimeFormat), i,2)
            self.addrow((node.time_start+datetime.timedelta(seconds=node.length)).strftime(self.strftimeFormat), i,3)
            self.addrow(node.repeat_after, i,4)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(False)





    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
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
            
       