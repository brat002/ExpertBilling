#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import AttrDict
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil

class TPRulesAdd(QtGui.QDialog):
    def __init__(self, connection,model=None):
        super(TPRulesAdd, self).__init__()
        self.model=model
        self.connection=connection
        self.connection.commit()

        self.resize(512, 453)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_from = QtGui.QLabel(self.groupBox)
        self.label_from.setObjectName("label_from")
        self.gridLayout.addWidget(self.label_from, 0, 0, 1, 1)
        self.label_cost = QtGui.QLabel(self.groupBox)
        self.label_cost.setObjectName("label_cost")
        self.gridLayout.addWidget(self.label_cost, 4, 0, 1, 1)
        self.label_oldtptime = QtGui.QLabel(self.groupBox)
        self.label_oldtptime.setObjectName("label_oldtptime")
        self.gridLayout.addWidget(self.label_oldtptime, 5, 0, 1, 1)
        self.comboBox_oldtptime = QtGui.QComboBox(self.groupBox)
        self.comboBox_oldtptime.setObjectName("comboBox_oldtptime")
        self.gridLayout.addWidget(self.comboBox_oldtptime, 5, 1, 1, 1)
        self.comboBox_from = QtGui.QComboBox(self.groupBox)
        self.comboBox_from.setObjectName("comboBox_from")
        self.gridLayout.addWidget(self.comboBox_from, 0, 1, 1, 1)
        self.label_balance_min = QtGui.QLabel(self.groupBox)
        self.label_balance_min.setObjectName("label_balance_min")
        self.gridLayout.addWidget(self.label_balance_min, 6, 0, 1, 1)
        self.lineEdit_cost = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_cost.setObjectName("lineEdit_cost")
        self.gridLayout.addWidget(self.lineEdit_cost, 4, 1, 1, 1)
        self.lineEdit_balance_min = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_balance_min.setObjectName("lineEdit_balance_min")
        self.gridLayout.addWidget(self.lineEdit_balance_min, 6, 1, 1, 1)
        self.groupBox_activation_type = QtGui.QGroupBox(self.groupBox)
        self.groupBox_activation_type.setObjectName("groupBox_activation_type")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_activation_type)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radioButton_activation_on_change = QtGui.QRadioButton(self.groupBox_activation_type)
        self.radioButton_activation_on_change.setChecked(True)
        self.radioButton_activation_on_change.setObjectName("radioButton_activation_on_change")
        self.gridLayout_3.addWidget(self.radioButton_activation_on_change, 0, 0, 1, 1)
        self.radioButton_activation_on_next_sp = QtGui.QRadioButton(self.groupBox_activation_type)
        self.radioButton_activation_on_next_sp.setObjectName("radioButton_activation_on_next_sp")
        self.gridLayout_3.addWidget(self.radioButton_activation_on_next_sp, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_activation_type, 8, 1, 1, 1)
        self.checkBox_bidirectional = QtGui.QCheckBox(self.groupBox)
        self.checkBox_bidirectional.setObjectName("checkBox_bidirectional")
        self.gridLayout.addWidget(self.checkBox_bidirectional, 9, 1, 1, 1)
        self.checkBox_disable = QtGui.QCheckBox(self.groupBox)
        self.checkBox_disable.setObjectName("checkBox_disable")
        self.gridLayout.addWidget(self.checkBox_disable, 10, 1, 1, 1)
        self.listWidget_to = QtGui.QListWidget(self.groupBox)
        self.listWidget_to.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.listWidget_to.setObjectName("listWidget_to")
        self.gridLayout.addWidget(self.listWidget_to, 2, 1, 2, 1)
        self.label_to = QtGui.QLabel(self.groupBox)
        self.label_to.setObjectName("label_to")
        self.gridLayout.addWidget(self.label_to, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
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
        self.label_from.setText(QtGui.QApplication.translate("Dialog", "С тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.label_cost.setText(QtGui.QApplication.translate("Dialog", "Стоимость перехода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_oldtptime.setText(QtGui.QApplication.translate("Dialog", "Не менее ч. на старом тарифе", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance_min.setText(QtGui.QApplication.translate("Dialog", "Минимум на балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_activation_type.setTitle(QtGui.QApplication.translate("Dialog", "Активация нового тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_activation_on_change.setText(QtGui.QApplication.translate("Dialog", "В момент смены", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_activation_on_next_sp.setText(QtGui.QApplication.translate("Dialog", "Следующий расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_bidirectional.setText(QtGui.QApplication.translate("Dialog", "Двунаправленная связь", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_disable.setText(QtGui.QApplication.translate("Dialog", "Временно запретить переход", None, QtGui.QApplication.UnicodeUTF8))
        self.label_to.setText(QtGui.QApplication.translate("Dialog", "На тарифные планы", None, QtGui.QApplication.UnicodeUTF8))

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
            model=AttrDict()

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
            
        if self.radioButton_activation_on_next_sp.isChecked()==True:
            model.on_next_sp = True
        else:
            model.on_next_sp = False
        model.disabled = self.checkBox_disable.checkState()==2
        sp_id = self.comboBox_oldtptime.itemData(self.comboBox_oldtptime.currentIndex()).toInt()[0]
        model.settlement_period = None if sp_id==0 else sp_id 
        #print "model.settlement_period_id", model.settlement_period_id
        from_id = self.comboBox_from.itemData(self.comboBox_from.currentIndex()).toInt()[0]
        self.connection.commit()
        for i in xrange(self.listWidget_to.count()):
            x=self.listWidget_to.item(i)
            if x.checkState()==QtCore.Qt.Checked:
                model.from_tariff = from_id
                model.to_tariff = x.id
                #print "save"
                try:
                    self.connection.tpchangerules_save(model)
                except Exception, e:
                    print e
                    self.connection.rollback()

                if self.checkBox_bidirectional.isChecked():
                    model.to_tariff=from_id
                    model.from_tariff = x.id
                    try:
                        self.connection.tpchangerules_save(model)
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
        self.refreshList(0)
        self.disconnect(self.comboBox_from,QtCore.SIGNAL("currentIndexChanged(int)"),self.refreshList)
        tariffs = self.connection.get_tariffs(fields=['id', 'name'])
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

        items = self.connection.get_settlementperiods(autostart=True)
        self.connection.commit()
        self.comboBox_oldtptime.addItem(u"--нет--")
        self.comboBox_oldtptime.setItemData(0, QtCore.QVariant(None))
        i = 1
        for item in items:
            self.comboBox_oldtptime.addItem(item.name)
            self.comboBox_oldtptime.setItemData(i, QtCore.QVariant(item.id))
            i+=1


            
        if self.model:
            self.radioButton_activation_on_next_sp.setChecked(self.model.on_next_sp)
            self.lineEdit_balance_min.setText(unicode(self.model.ballance_min))
            self.lineEdit_cost.setText(unicode(self.model.cost))
            
            self.checkBox_disable.setChecked(self.model.disabled)
            for i in xrange(self.comboBox_oldtptime.count()):
                if self.comboBox_oldtptime.itemData(i).toInt()[0]==self.model.settlement_period:
                    self.comboBox_oldtptime.setCurrentIndex(i)    
                    
        

            
        
    def refreshList(self, i):
        tariffs = self.connection.get_tariffs(fields = ['id', 'name'])
        self.connection.commit()
        self.listWidget_to.clear()
        for tariff in tariffs:
            item = QtGui.QListWidgetItem(unicode(tariff.name))
            item.setCheckState(QtCore.Qt.Unchecked)
            item.id = tariff.id
            self.listWidget_to.addItem(item)
            if self.model:
                if tariff.id==self.model.from_tariff:
                    item.setHidden(True)
                if tariff.id == self.model.to_tariff:
                    item.setCheckState(QtCore.Qt.Checked)

                


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
            
            if self.connection.tpchangerules_delete(id):
                self.connection.commit()
                self.refresh()
            else:
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_rule(self):
        id=self.getSelectedId()
        try:
            model=self.connection.get_tpchangerules(id)
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
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        rules = self.connection.get_tpchangerules(normal_fields=True)
        self.connection.commit()
        self.tableWidget.setRowCount(len(rules))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for rule in rules:
            self.addrow(rule.id, i,0)
            self.addrow(rule.from_tariff, i,1)
            self.addrow(rule.to_tariff, i,2)
            self.addrow(rule.disabled, i,3)
            self.addrow(rule.cost, i,4)
            self.addrow(rule.ballance_min, i,5)
            self.addrow("" if rule.settlement_period == None else rule.settlement_period, i,6)
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
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(TPRulesEbs, self).delNodeLocalAction([self.delAction])

