#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from helpers import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from time import mktime
from CustomForms import ComboBoxDialog
import datetime, calendar
from helpers import transaction
class AddCards(QtGui.QDialog):
    def __init__(self, connection, group, last_series=0):
        super(AddCards, self).__init__()
        self.connection = connection
        self.last_series=last_series
        self.group = group
        self.connection.commit()
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,307,319).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(120,280,181,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.period_groupBox = QtGui.QGroupBox(self)
        self.period_groupBox.setGeometry(QtCore.QRect(10,10,291,91))
        self.period_groupBox.setObjectName("period_groupBox")

        self.end_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.end_dateTimeEdit.setGeometry(QtCore.QRect(70,50,194,22))
        self.end_dateTimeEdit.setCalendarPopup(True)
        self.end_dateTimeEdit.setObjectName("end_dateTimeEdit")

        self.start_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.start_dateTimeEdit.setGeometry(QtCore.QRect(70,20,194,22))
        self.start_dateTimeEdit.setCalendarPopup(True)
        self.start_dateTimeEdit.setObjectName("start_dateTimeEdit")

        self.start_label = QtGui.QLabel(self.period_groupBox)
        self.start_label.setGeometry(QtCore.QRect(10,20,46,21))
        self.start_label.setObjectName("start_label")

        self.end_label = QtGui.QLabel(self.period_groupBox)
        self.end_label.setGeometry(QtCore.QRect(10,50,46,16))
        self.end_label.setObjectName("end_label")

        self.params_groupBox = QtGui.QGroupBox(self)
        self.params_groupBox.setGeometry(QtCore.QRect(10,110,291,161))
        self.params_groupBox.setObjectName("params_groupBox")

        self.nominal_lineEdit = QtGui.QLineEdit(self.params_groupBox)
        self.nominal_lineEdit.setGeometry(QtCore.QRect(110,50,171,20))
        self.nominal_lineEdit.setObjectName("nominal_lineEdit")

        self.count_label = QtGui.QLabel(self.params_groupBox)
        self.count_label.setGeometry(QtCore.QRect(10,80,60,16))
        self.count_label.setObjectName("count_label")

        self.pin_label = QtGui.QLabel(self.params_groupBox)
        self.pin_label.setGeometry(QtCore.QRect(10,110,59,16))
        self.pin_label.setObjectName("pin_label")

        self.series_label = QtGui.QLabel(self.params_groupBox)
        self.series_label.setGeometry(QtCore.QRect(10,20,46,16))
        self.series_label.setObjectName("series_label")

        self.nominal_label = QtGui.QLabel(self.params_groupBox)
        self.nominal_label.setGeometry(QtCore.QRect(10,50,46,16))
        self.nominal_label.setObjectName("nominal_label")

        self.pin_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.pin_spinBox.setGeometry(QtCore.QRect(110,110,101,22))
        self.pin_spinBox.setMaximum(32)
        self.pin_spinBox.setObjectName("pin_spinBox")

        self.l_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.l_checkBox.setGeometry(QtCore.QRect(220,110,31,21))
        self.l_checkBox.setObjectName("l_checkBox")

        self.numbers_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.numbers_checkBox.setGeometry(QtCore.QRect(250,110,31,21))
        self.numbers_checkBox.setObjectName("numbers_checkBox")

        self.count_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.count_spinBox.setGeometry(QtCore.QRect(110,80,171,22))
        self.count_spinBox.setFrame(True)
        self.count_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.count_spinBox.setAccelerated(True)
        self.count_spinBox.setMaximum(999999999)
        self.count_spinBox.setObjectName("count_spinBox")

        self.series_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.series_spinBox.setGeometry(QtCore.QRect(110,20,171,22))
        self.series_spinBox.setMaximum(999999999)
        self.series_spinBox.setObjectName("series_spinBox")
        

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры серии", None, QtGui.QApplication.UnicodeUTF8))
        self.period_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Период действия", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры генерации", None, QtGui.QApplication.UnicodeUTF8))
        self.count_label.setText(QtGui.QApplication.translate("Dialog", "Количество", None, QtGui.QApplication.UnicodeUTF8))
        self.pin_label.setText(QtGui.QApplication.translate("Dialog", "Длина пина", None, QtGui.QApplication.UnicodeUTF8))
        self.series_label.setText(QtGui.QApplication.translate("Dialog", "Серия", None, QtGui.QApplication.UnicodeUTF8))
        self.nominal_label.setText(QtGui.QApplication.translate("Dialog", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.l_checkBox.setText(QtGui.QApplication.translate("Dialog", "Б", None, QtGui.QApplication.UnicodeUTF8))
        self.numbers_checkBox.setText(QtGui.QApplication.translate("Dialog", "Ц", None, QtGui.QApplication.UnicodeUTF8))


    def accept(self):
        """
        понаставить проверок
        """
        if self.l_checkBox.checkState()==0 and self.numbers_checkBox.checkState()==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не выбрали состави PIN-кода"))
            return
        
        if self.nominal_lineEdit.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан номинал"))
            return
        
        if self.count_spinBox.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не eуказано количество генерируемых карнточек"))
            return
        
        if self.pin_spinBox.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана длина PIN-кода"))
            return        
        
        from randgen import GenPasswd2
        import string
        
        mask=[]
        if self.l_checkBox.checkState()==2:
            mask+=string.letters
        if self.numbers_checkBox.checkState()==2:
            mask+=string.digits
            
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))
        for x in xrange(0, self.count_spinBox.text().toInt()[0]):
            model = Object()
            model.card_group_id = self.group
            model.series = unicode(self.series_spinBox.text())
            model.pin = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=mask)
            model.nominal = self.nominal_lineEdit.text()
            model.start_date = self.start_dateTimeEdit.dateTime().toPyDateTime()
            model.end_date = self.end_dateTimeEdit.dateTime().toPyDateTime()
            #model.sold=False
            #model.activated=False
            
            print model.pin
            self.connection.create(model.save("billservice_card"))
        
        self.connection.commit()


        QtGui.QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        #end=datetime.datetime.now()

        self.series_spinBox.setMinimum(self.last_series)
        self.start_dateTimeEdit.setMinimumDate(start)
        self.end_dateTimeEdit.setMinimumDate(start)




class CardsChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(CardsChild, self).__init__()
        self.connection = connection
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.setObjectName("CardsMDI")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()).expandedTo(self.minimumSizeHint()))

        #self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()))
        #self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,692,483).size()))

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setGeometry(QtCore.QRect(0,0,191,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")


        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        tree_header = self.treeWidget.headerItem()
        tree_header.setHidden(True)
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
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

        self.actionAddGroup = QtGui.QAction(self)
        self.actionAddGroup.setIcon(QtGui.QIcon("images/add.png"))
        self.actionAddGroup.setObjectName("actionAddSeries")

        self.actionDelGroup = QtGui.QAction(self)
        self.actionDelGroup.setIcon(QtGui.QIcon("images/del.png"))
        self.actionDelGroup.setObjectName("actionDelSeries")

        self.actionEnableGroup = QtGui.QAction(self)
        self.actionEnableGroup.setIcon(QtGui.QIcon("images/ok.png"))
        self.actionEnableGroup.setObjectName("actionEnableSeries")

        self.actionDisableGroup = QtGui.QAction(self)
        self.actionDisableGroup.setIcon(QtGui.QIcon("images/false.png"))
        self.actionDisableGroup.setObjectName("actionDisableSeries")

        self.actionGenerateCards = QtGui.QAction(self)
        self.actionGenerateCards.setIcon(QtGui.QIcon("images/add.png"))
        self.actionGenerateCards.setObjectName("actionAddSeries")
        

        self.actionEnableCard = QtGui.QAction(self)
        self.actionEnableCard.setIcon(QtGui.QIcon("images/ok.png"))
        self.actionEnableCard.setObjectName("actionEnable")

        self.actionDisableCard = QtGui.QAction(self)
        self.actionDisableCard.setIcon(QtGui.QIcon("images/false.png"))
        self.actionDisableCard.setObjectName("actionDisable")

        self.actionSellCard = QtGui.QAction(self)
        self.actionSellCard.setIcon(QtGui.QIcon("images/new.png"))
        self.actionSellCard.setObjectName("actionSellCard")

        self.actionActivateCard = QtGui.QAction(self)
        self.actionActivateCard.setIcon(QtGui.QIcon("images/paste.png"))
        self.actionActivateCard.setObjectName("actionActivateCard")

        self.actionPrintCard = QtGui.QAction(self)
        self.actionPrintCard.setIcon(QtGui.QIcon("images/account.png"))
        self.actionPrintCard.setObjectName("actionPrintCard")
        self.toolBar.addAction(self.actionAddGroup)
        self.toolBar.addAction(self.actionDelGroup)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionEnableGroup)
        self.toolBar.addAction(self.actionDisableGroup)
        self.toolBar.addAction(self.actionGenerateCards)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPrintCard)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionEnableCard)
        self.toolBar.addAction(self.actionDisableCard)
        self.toolBar.addAction(self.actionSellCard)
        self.toolBar.addAction(self.actionActivateCard)
        self.toolBar.addSeparator()

        self.retranslateUi()
        self.refresh()
#===============================================================================
        self.connect(self.actionAddGroup, QtCore.SIGNAL("triggered()"), self.addGroup)
        self.connect(self.actionDelGroup, QtCore.SIGNAL("triggered()"), self.delGroup)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editGroup)
#        
        self.connect(self.actionEnableGroup, QtCore.SIGNAL("triggered()"),  self.enableGroup)
        self.connect(self.actionDisableGroup, QtCore.SIGNAL("triggered()"),  self.disableGroup)
     
        self.connect(self.actionEnableCard, QtCore.SIGNAL("triggered()"),  self.enableCard)
        self.connect(self.actionDisableCard, QtCore.SIGNAL("triggered()"),  self.disableCard)   
        self.connect(self.actionActivateCard, QtCore.SIGNAL("triggered()"),  self.activateCard)   

        self.connect(self.actionSellCard, QtCore.SIGNAL("triggered()"),  self.sellCard)   

        
        
        
        self.connect(self.actionGenerateCards, QtCore.SIGNAL("triggered()"),  self.generateCards)
# 
#        
#        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refreshTable)
#        
#        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)
#        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
#        
#        
#        
#        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
#        
#        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
#===============================================================================
        #self.addNodeLocalAction()
        #self.delNodeLocalAction()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Карты оплаты", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.clear()
        
        columns=['#', u'Серия', u'Номинал', u'PIN', u'С', u'По']
        makeHeaders(columns, self.tableWidget)
        
        #self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Карты оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAddGroup.setText(QtGui.QApplication.translate("MainWindow", "Add Series", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelGroup.setText(QtGui.QApplication.translate("MainWindow", "Del Series", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEnableGroup.setText(QtGui.QApplication.translate("MainWindow", "Enable Series", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisableGroup.setText(QtGui.QApplication.translate("MainWindow", "Disable Series", None, QtGui.QApplication.UnicodeUTF8))
        #self.actionSell.setText(QtGui.QApplication.translate("MainWindow", "SellSeries", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEnableCard.setText(QtGui.QApplication.translate("MainWindow", "Enable", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisableCard.setText(QtGui.QApplication.translate("MainWindow", "Disable", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSellCard.setText(QtGui.QApplication.translate("MainWindow", "Sell Card", None, QtGui.QApplication.UnicodeUTF8))
        self.actionActivateCard.setText(QtGui.QApplication.translate("MainWindow", "Activate Card", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrintCard.setText(QtGui.QApplication.translate("MainWindow", "PrintCard", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, True)

    def sellCard(self):
        try:
            id=self.getSelectedId()
        except:
            return
        
        model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % id)
        model.sold=datetime.datetime.now()
        self.connection.create(model.save("billservice_card"))
        self.connection.commit()
        self.refresh()
        
    def activateCard(self):
        accounts = self.connection.sql("SELECT username as name FROM billservice_account;")
        child = ComboBoxDialog(items=accounts)
        
        if child.exec_()==1:
            account = self.connection.get("SELECT * FROM billservice_account WHERE username='%s'" %  unicode(child.comboBox.currentText()))
            print "account_id", account.id
        else:
            return
        now = datetime.datetime.now()
        for index in self.tableWidget.selectedIndexes():
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            
            try:
                #print "int(i)", int(i)
                model=self.connection.get("SELECT id, card_group_id, series, disabled, activated_by_id, pin, nominal,start_date, end_date::timestamp without time zone FROM billservice_card WHERE id=%s" % int(i))

                if model.activated_by_id==None and model.end_date>=now and model.disabled==False:
                    model.sold=now
                    model.activated=now
                    model.activated_by_id = account.id
                    self.connection.create(model.save("billservice_card"))
                    tr = transaction(account.id, "ACTIVATION_CARD", True, "", model.nominal*(-1), u"%s-%s" % (model.series, model.pin))
                    self.connection.create(tr)
                    self.connection.commit()
                
 
            except Exception, e:
                print e
                
        self.refreshTable()
        

    
    def addGroup(self):
        text = QtGui.QInputDialog.getText(self,u"Введите название пачки", u"Название:", QtGui.QLineEdit.Normal);
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
            if not self.connection.create(model.save(table="billservice_cardgroup")):
                QtGui.QMessageBox.warning(self, u"Ошибка",
                            u"Вероятно, такое название уже есть в списке.")
            self.connection.commit()
        except Exception, e:
            print e
            print "rollback"
            self.connection.rollback()
        
        self.refresh()

    def delGroup(self):

        try:
            id=self.getTimeperiodId()

        except:
            return

        if id>0 and QtGui.QMessageBox.question(self, u"Удалить группу карточек?" , u"Удалить группу карточек?.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_card WHERE card_group_id='%d'" % id)
                #self.connection.delete("DELETE FROM billservice_cardgroup WHERE id='%d'" % id)
                self.connection.indelete("billservice_cardgroup", id)
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                
            #self.timeperiod_list_edit.setCurrentIndex(0)
            self.refresh()

    def enableGroup(self):
        try:
            id=self.getTimeperiodId()
        except:
            return
        
        model=self.connection.get("SELECT * FROM billservice_cardgroup WHERE id=%s" % id)
        model.disabled=False
        self.connection.create(model.save("billservice_cardgroup"))
        self.connection.commit()
        self.refresh()
    
    def disableGroup(self):
        try:
            id=self.getTimeperiodId()
        except:
            return
        
        model=self.connection.get("SELECT * FROM billservice_cardgroup WHERE id=%s" % id)
        model.disabled=False
        self.connection.create(model.save("billservice_cardgroup"))
        self.connection.commit()
        self.refresh()

    def enableCard(self):
        for index in self.tableWidget.selectedIndexes():
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=False
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()
 
            except Exception, e:
                pass   
        
        self.refreshTable()
    
    def disableCard(self):
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=True
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()

            except Exception, e:
                pass        
        
        self.refreshTable()
        
    def editGroup(self):
        model = self.connection.get("SELECT * FROM billservice_cardgroup WHERE id=%d;" % self.getTimeperiodId())
        text = QtGui.QInputDialog.getText(self,unicode(u"Введите название группы"), unicode(u"Название:"), QtGui.QLineEdit.Normal,model.name);

        if text[0].isEmpty()==True and text[1]:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        try:
            model=self.connection.get("SELECT * FROM billservice_cardgroup WHERE id=%d" % model.id)
            model.name=unicode(text[0])
            self.connection.create(model.save('billservice_cardgroup'))    
            self.connection.commit()            
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Введено недопустимое значение.")
            self.connection.rollback()
            print e
            return
        self.refresh()

    def generateCards(self):

        try:
            model=self.getTimeperiodId()
        except Exception, e:
            return
        
        #print model.id
        
        last_series = self.connection.get("SELECT MAX(series) as series FROM billservice_card").series
        if last_series==None:
            last_series=0
        else:
            last_series+=1
        child=AddCards(connection=self.connection, group=model, last_series=last_series)
        if child.exec_()==1:
            self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=%d" % id)
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
        self.tableWidget.setSortingEnabled(False)
        if not widget:
            group_id=self.getTimeperiodId()
        else:
            group_id = widget.id
            
        self.tableWidget.clearContents()

        nodes = self.connection.sql("""SELECT * FROM billservice_card WHERE card_group_id=%d ORDER BY id """ % group_id)
        self.tableWidget.setRowCount(len(nodes))
        i=0        
        columns=['Id', u'Серия', u'Номинал', u'PIN', u'С', u'По']
        for node in nodes:

            self.addrow(node.id, i,0, status = node.disabled, activated=node.activated)
            self.addrow(node.series, i,1, status = node.disabled, activated=node.activated)
            self.addrow(node.nominal, i,2, status = node.disabled, activated=node.activated)
            self.addrow(node.pin, i,3, status = node.disabled, activated=node.activated)
            self.addrow(node.start_date.strftime(self.strftimeFormat), i,4, status = node.disabled, activated=node.activated)
            self.addrow(node.end_date.strftime(self.strftimeFormat), i,5, status = node.disabled, activated=node.activated)
            self.tableWidget.setRowHeight(i, 17)
            i+=1
            
        self.tableWidget.setColumnHidden(0, False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSortingEnabled(True)




    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTimeperiodId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y, status, activated):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        #print 'activated',activated
        if status==True:
            headerItem.setTextColor(QtGui.QColor('#FF0100'))
        if activated == 'Null' and y==0:
            headerItem.setIcon(QtGui.QIcon("images/ok.png"))
        elif activated!='Null' and y==0:
            headerItem.setIcon(QtGui.QIcon("images/false.png"))
    
        self.tableWidget.setItem(x,y,headerItem)
        

    def refresh(self):
        #self.timeperiod_list_edit.clear()
        self.treeWidget.clear()

        groups=self.connection.sql("SELECT * FROM billservice_cardgroup ORDER BY name ASC")
        for group in groups:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.setText(0, group.name)
            if group.disabled==True:
                item.setDisabled(True)
                item.setBackgroundColor(0,QtGui.QColor('lightgrey'))
            else:
                item.setDisabled(False)
            item.id = group.id
        
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
            

