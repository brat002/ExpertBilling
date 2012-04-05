#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from db import AttrDict
from helpers import makeHeaders
from helpers import dateDelim
from helpers import setFirstActive
from helpers import HeaderUtil, SplitterUtil
from ebsWindow import ebsTable_n_TreeWindow
from time import mktime
from helpers import dateDelim
import datetime, calendar
from customwidget import CustomDateTimeWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
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
        nodes = self.connection.get_timenodes()
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
        #self.resize(QtCore.QSize(QtCore.QRect(0,0,278,198).size()).expandedTo(self.minimumSizeHint()))

        self.resize(397, 195)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setObjectName(_fromUtf8("name_edit"))
        self.gridLayout.addWidget(self.name_edit, 1, 2, 1, 1)
        self.start_label = QtGui.QLabel(self)
        self.start_label.setObjectName(_fromUtf8("start_label"))
        self.gridLayout.addWidget(self.start_label, 2, 0, 1, 1)
        self.start_date_edit = CustomDateTimeWidget()
        #self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setObjectName(_fromUtf8("start_date_edit"))
        self.gridLayout.addWidget(self.start_date_edit, 2, 2, 1, 1)
        self.end_label = QtGui.QLabel(self)
        self.end_label.setObjectName(_fromUtf8("end_label"))
        self.gridLayout.addWidget(self.end_label, 3, 0, 1, 1)
        self.end_date_edit = CustomDateTimeWidget()
        #self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setObjectName(_fromUtf8("end_date_edit"))
        self.gridLayout.addWidget(self.end_date_edit, 3, 2, 1, 1)
        self.repeat_label = QtGui.QLabel(self)
        self.repeat_label.setObjectName(_fromUtf8("repeat_label"))
        self.gridLayout.addWidget(self.repeat_label, 4, 0, 1, 2)
        self.repeat_edit = QtGui.QComboBox(self)
        self.repeat_edit.setObjectName(_fromUtf8("repeat_edit"))
        self.gridLayout.addWidget(self.repeat_edit, 4, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 2)


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
            model=AttrDict()
        try:
            
            model.name=unicode(self.name_edit.text())
            model.time_start=self.start_date_edit.currentDate()
    
            model.length=(self.end_date_edit.currentDate()-self.start_date_edit.currentDate()).seconds+(self.end_date_edit.currentDate()-self.start_date_edit.currentDate()).days*86400
            #print model.length
            
            model.repeat_after=unicode(self.repeat_edit.currentText())
    
            if self.nodemodel:
                #Update
                self.connection.timeperiodnode_save(model)
            else:
                #Insert
                self.nodemodel=model
                self.nodemodel.id = self.connection.timeperiodnode_save(model).id
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
        self.refresh()
        
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
                o = AttrDict()
                o.timeperiod=self.getTimeperiodId()
                o.timeperiodnode = node
                self.connection.timeperiodnode_m2m_save(o)
            self.refresh()
            
    def addPeriod(self):        
        text = QtGui.QInputDialog.getText(self,u"Введите название периода", u"Название:", QtGui.QLineEdit.Normal);
        #print text        
        if text[0].isEmpty()==True and text[1]==True:
            QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return
        elif text[1]==False:
            return

        model = AttrDict()
        model.name=unicode(text[0])
        
        try:      
            self.connection.commit()
            if not self.connection.timeperiod_save(model):
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
            if QtGui.QMessageBox.question(self, u"Удалить период тарификации?" , u"Пожалуйста, убедитесь, что с указанным периодом тарификации не связаны какие-либо сущности в системе. Удаление периода тарификации может привести к некорректному поведению системы!", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id='%d'" % model.id)
                    #self.connection.delete("DELETE FROM billservice_timeperiod WHERE id='%d'" % model.id)
                    #self.connection.sql("UPDATE billservice_timeperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.timeperiod_delete(id)
                    self.connection.commit()
                    self.tableWidget.blockSignals(True)
                    self.refresh()
                    self.tableWidget.blockSignals(False)
                    
                    setFirstActive(self.treeWidget)
                        #self.refreshTable()

                except Exception, e:
                    print e
                    self.connection.rollback()
                
            #self.timeperiod_list_edit.setCurrentIndex(0)


    def editPeriod(self):
        model = self.connection.get_timeperiods(id=self.getTimeperiodId())

        text = QtGui.QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QtGui.QLineEdit.Normal,model.name)

        if text[0].isEmpty()==True and text[1]==True:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        if text[1]==False:
            return
        try:
            model.name=unicode(text[0])
            self.connection.timeperiod_save(model)    
            self.connection.commit()            
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Введено недопустимое значение.")
            self.connection.rollback()
            return
        self.refresh()

    def addNode(self):

        try:
            model=self.connection.get_timeperiods(id=self.getTimeperiodId())
        except Exception, e:
            return
        #print model.id
        child=AddTimePeriod(connection=self.connection)
        if child.exec_()==1:
            try:
                node = AttrDict()
                node.timeperiod = model.id
                node.timeperiodnode = child.nodemodel.id
                self.connection.timeperiodnode_m2m_save(node)
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
                #Проверяем используется ли ещё где-нибудь
                self.connection.timeperiodnodes_m2m_delete(period_id=self.getTimeperiodId(), node_id=id)
                
                self.refreshTable()
            except Exception, e:
                print e
                self.connection.rollback()

            
        
    def editNode(self):
        id = self.getSelectedId()
        #print id
        
        try:
            nodemodel = self.connection.get_timenodes(id=unicode(self.getSelectedId()))
            #nodemodel = self.connection.sql("SELECT * FROM billservice_timeperiodnode WHERE id=%d;" % int(id))[0]
        except Exception, e:
            pass
            #import Pyro.util
            #print ''.join(Pyro.util.getPyroTraceback(e))

        
        #name=unicode(self.getSelectedName())
        model=self.connection.get_timeperiods(self.getTimeperiodId())
        if not model:
            return
        self.connection.commit()
        child=AddTimePeriod(connection=self.connection, nodemodel=nodemodel)
        if child.exec_()==1:
            
            self.refreshTable()
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
    
    def refreshTable(self, widget=None):
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        if not widget:
            period_id=self.getTimeperiodId()
        else:
            period_id = widget.id
            
        self.tableWidget.clearContents()
        
        nodes = self.connection.get_timenodes(period_id = period_id)
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
        self.statusBar().showMessage(u"Готово")




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
        periods=self.connection.get_timeperiods()
        self.connection.commit()
        for period in periods:
            #item = QtGui.QListWidgetItem(self.timeperiod_list_edit)
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            item.setText(0, period.name)
            item.id = period.id
        if curItem != -1:
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(curItem))
            
       