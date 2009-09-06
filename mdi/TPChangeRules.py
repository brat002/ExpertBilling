#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil

class TPRulesAdd(QtGui.QDialog):
    def __init__(self, connection,model=None):
        super(TPRulesAdd, self).__init__()
        self.model=model
        self.connection=connection
        self.connection.commit()

        self.resize(552, 453)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_from = QtGui.QLabel(self.groupBox)
        self.label_from.setObjectName("label_from")
        self.gridLayout.addWidget(self.label_from, 0, 0, 1, 1)
        self.comboBox_from = QtGui.QComboBox(self.groupBox)
        self.comboBox_from.setObjectName("comboBox_from")
        self.gridLayout.addWidget(self.comboBox_from, 0, 1, 1, 1)
        self.label_cost = QtGui.QLabel(self.groupBox)
        self.label_cost.setObjectName("label_cost")
        self.gridLayout.addWidget(self.label_cost, 1, 0, 1, 1)
        self.lineEdit_cost = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_cost.setObjectName("lineEdit_cost")
        self.gridLayout.addWidget(self.lineEdit_cost, 1, 1, 1, 1)
        self.label_oldtptime = QtGui.QLabel(self.groupBox)
        self.label_oldtptime.setObjectName("label_oldtptime")
        self.gridLayout.addWidget(self.label_oldtptime, 2, 0, 1, 1)
        self.comboBox_oldtptime = QtGui.QComboBox(self.groupBox)
        self.comboBox_oldtptime.setObjectName("comboBox_oldtptime")
        self.gridLayout.addWidget(self.comboBox_oldtptime, 2, 1, 1, 1)
        self.label_balance_min = QtGui.QLabel(self.groupBox)
        self.label_balance_min.setObjectName("label_balance_min")
        self.gridLayout.addWidget(self.label_balance_min, 3, 0, 1, 1)
        self.lineEdit_balance_min = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_balance_min.setObjectName("lineEdit_balance_min")
        self.gridLayout.addWidget(self.lineEdit_balance_min, 3, 1, 1, 1)
        self.label_to = QtGui.QLabel(self.groupBox)
        self.label_to.setObjectName("label_to")
        self.gridLayout.addWidget(self.label_to, 4, 0, 1, 1)
        self.listWidget_to = QtGui.QListWidget(self.groupBox)
        self.listWidget_to.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.listWidget_to.setObjectName("listWidget_to")
        self.gridLayout.addWidget(self.listWidget_to, 4, 1, 2, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.checkBox_bidirectional = QtGui.QCheckBox(self.groupBox)
        self.checkBox_bidirectional.setObjectName("checkBox_bidirectional")
        self.gridLayout.addWidget(self.checkBox_bidirectional, 6, 0, 1, 1)
        self.checkBox_disable = QtGui.QCheckBox(self.groupBox)
        self.checkBox_disable.setObjectName("checkBox_disable")
        self.gridLayout.addWidget(self.checkBox_disable, 7, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi()

        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.comboBox_from,QtCore.SIGNAL("currentIndexChanged(int)"),self.refreshList)
        #self.connect(self.autostart_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.checkbox_behavior)
        #self.connect(self.length_edit, QtCore.SIGNAL("currentIndexChanged(int)"), self.length_behavior)


        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Правило смены тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Настройки смены тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.label_from.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.label_cost.setText(QtGui.QApplication.translate("Dialog", "Стоимость перехода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_oldtptime.setText(QtGui.QApplication.translate("Dialog", "Миниальное время на старом тарифном план", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance_min.setText(QtGui.QApplication.translate("Dialog", "Минимум на балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.label_to.setText(QtGui.QApplication.translate("Dialog", "На", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_bidirectional.setText(QtGui.QApplication.translate("Dialog", "Двунаправленная связь", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_disable.setText(QtGui.QApplication.translate("Dialog", "Временно запретить переход", None, QtGui.QApplication.UnicodeUTF8))


    def checkbox_behavior(self):
        if self.autostart_checkbox.checkState()==2:
            self.datetime_edit.setEnabled(False)
            if not unicode(self.name_edit.text()).startswith('+'):
                self.name_edit.setText("+"+self.name_edit.text())
                
        else:
            self.datetime_edit.setEnabled(True)
            if unicode(self.name_edit.text()).startswith('+'):
                self.name_edit.setText(self.name_edit.text()[1:])

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
            #print 'New sp'
            model=Object()

        if unicode(self.lineEdit_cost.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана цена"))
            return
        else:
            model.cost=unicode(self.lineEdit_cost.text())

        if unicode(self.lineEdit_balance_min.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан минимально возможный баланс абонента"))
            return
        else:
            model.ballance_min=float(unicode(self.lineEdit_balance_min.text()))
            

        model.disabled = self.checkBox_disable.checkState()==2
        model.settlement_period_id = self.comboBox_oldtptime.itemData(self.comboBox_oldtptime.currentIndex()).toInt()[0]
        #print "model.settlement_period_id", model.settlement_period_id
        from_id = self.comboBox_from.itemData(self.comboBox_from.currentIndex()).toInt()[0]
        self.connection.commit()
        for i in xrange(self.listWidget_to.count()):
            x=self.listWidget_to.item(i)
            if x.checkState()==QtCore.Qt.Checked:
                model.from_tariff_id = from_id
                model.to_tariff_id = x.id
                #print "save"
                try:
                    self.connection.save(model,"billservice_tpchangerule")
                except:
                    self.connection.rollback()
                    
                if self.checkBox_bidirectional.isChecked():
                    model.to_tariff_id=from_id
                    model.from_tariff_id = x.id
                    try:
                        self.connection.save(model,"billservice_tpchangerule")
                    except Exception, e:
                        print e
                        self.connection.rollback()                

        try:
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            return



        QtGui.QDialog.accept(self)

    def fixtures(self):
        self.disconnect(self.comboBox_from,QtCore.SIGNAL("currentIndexChanged(int)"),self.refreshList)
        tariffs = self.connection.sql("SELECT id, name FROM billservice_tariff WHERE deleted IS NOT TRUE ORDER BY NAME ASC;")
        self.connection.commit()
        i=0
        self.comboBox_from.clear()
        for tariff in tariffs:
            self.comboBox_from.addItem(tariff.name)
            self.comboBox_from.setItemData(i, QtCore.QVariant(tariff.id))
            if self.model:
                if tariff.id==self.model.from_tariff_id:
                    self.comboBox_from.setCurrentIndex(i)
            
            i+=1
            
        self.connect(self.comboBox_from,QtCore.SIGNAL("currentIndexChanged(int)"),self.refreshList)

        items = self.connection.get_models("billservice_settlementperiod", where={'autostart':True,})
        self.connection.commit()
        self.comboBox_oldtptime.addItem(u"--нет--")
        self.comboBox_oldtptime.setItemData(0, QtCore.QVariant(0))
        i = 1
        for item in items:
            self.comboBox_oldtptime.addItem(item.name)
            self.comboBox_oldtptime.setItemData(i, QtCore.QVariant(item.id))
            i+=1


            
        if self.model:
            self.lineEdit_balance_min.setText(unicode(self.model.ballance_min))
            self.lineEdit_cost.setText(unicode(self.model.cost))
            
            self.checkBox_disable.setChecked(self.model.disabled)
            for i in xrange(self.comboBox_oldtptime.count()):
                if self.comboBox_oldtptime.itemData(i).toInt()[0]==self.model.settlement_period_id:
                    self.comboBox_oldtptime.setCurrentIndex(i)    
                    
        self.refreshList(0)

            
        
    def refreshList(self, i):
        tariffs = self.connection.sql("SELECT id, name FROM billservice_tariff WHERE deleted IS NOT TRUE ORDER BY NAME ASC;")
        self.connection.commit()
        self.listWidget_to.clear()
        for tariff in tariffs:
            item = QtGui.QListWidgetItem(unicode(tariff.name))
            item.setCheckState(QtCore.Qt.Unchecked)
            item.id = tariff.id
            self.listWidget_to.addItem(item)
            if self.model:
                if tariff.id==self.model.from_tariff_id:
                    item.setHidden(True)
                if tariff.id == self.model.to_tariff_id:
                    item.setCheckState(QtCore.Qt.Checked)
                    
            if self.comboBox_from.itemData(self.comboBox_from.currentIndex()).toInt()[0]==tariff.id:
                item.setHidden(True)
                        

    def save(self):
        print 'Saved'




class TPRulesEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'С', u'На', u'Временно запрещено', u'Стоимость', u'Минимум на балансе', u"Минимум на старом ТП"]
        initargs = {"setname":"tprules_frame", "objname":"TPRulesEbs", "winsize":(0,0,827,476), "wintitle":"Правила смены тарифных планов", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(TPRulesEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,827,21))
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
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def ebsPostInit(self, initargs):
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_rule)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.add_rule), ("editAction", "Настройки", "images/open.png", self.edit_rule), ("delAction", "Удалить", "images/del.png", self.del_rule)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(TPRulesEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_rule(self):
        child=TPRulesAdd(connection=self.connection)
        if child.exec_():
            self.refresh()

    def del_rule(self):
        id=self.getSelectedId()
        if id>0:
            try:
                self.connection.iddelete(id, "billservice_tpchangerule")
                self.connection.commit()
                self.refresh()
            except Exception, e:
                print e
                self.connection.rollback()
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_rule(self):
        id=self.getSelectedId()
        try:
            model=self.connection.get_model(id, "billservice_tpchangerule")
        except:
            return

        self.connection.commit()
        child=TPRulesAdd(connection=self.connection, model=model)
        if child.exec_():

            self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tprule.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        self.tableWidget.setSortingEnabled(False)
        rules = self.connection.sql(" SELECT tpch.*,(SELECT name FROM billservice_tariff WHERE id=tpch.from_tariff_id and deleted IS NOT TRUE ) as from_tariff_name, (SELECT name FROM billservice_tariff WHERE id=tpch.to_tariff_id and deleted IS NOT TRUE ) as to_tariff_name, (SELECT name FROM billservice_settlementperiod WHERE id=tpch.settlement_period_id) as settlement_period_name FROM billservice_tpchangerule as tpch ORDER BY tpch.from_tariff_id")
        self.connection.commit()
        self.tableWidget.setRowCount(len(rules))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for rule in rules:
            self.addrow(rule.id, i,0)
            self.addrow(rule.from_tariff_name, i,1)
            self.addrow(rule.to_tariff_name, i,2)
            self.addrow(rule.disabled, i,3)
            self.addrow(rule.cost, i,4)
            self.addrow(rule.ballance_min, i,5)
            self.addrow("" if rule.settlement_period_name == None else rule.settlement_period_name, i,6)
            #self.addrow(period.time_start.strftime(self.strftimeFormat), i,3)
            #self.addrow(period.length_in, i,4)            
            #self.addrow(period.length, i,5)
            #self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
            
    def delNodeLocalAction(self):
        super(TPRulesEbs, self).delNodeLocalAction([self.delAction])

