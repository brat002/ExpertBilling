#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat
import datetime, calendar
from helpers import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil

class AddSettlementPeriod(QtGui.QDialog):
    def __init__(self, connection,model=None):
        super(AddSettlementPeriod, self).__init__()
        self.model=model
        self.connection=connection
        self.connection.commit()

        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,410,156).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,410,156).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,410,156).size()))
        
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
        
        self.autostart_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Расчётный период у каждого пользователя будет начинаться с момента привязки аккаунта к тарифному плану.", None, QtGui.QApplication.UnicodeUTF8))
        self.autostart_checkbox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Расчётный период у каждого пользователя будет начинаться с момента привязки аккаунта к тарифному плану.\nПри этом начало расчётного периода из настроек расчётного периода учитываться не будет.", None, QtGui.QApplication.UnicodeUTF8))
        
        
        self.length_edit.setToolTip(QtGui.QApplication.translate("Dialog", "DAY - расчётный период будет повторяться через 86400 с,\n"
        "WEEKDAY - расчётный период будет повторяться через неделю. Пример : с понедельника по понедельник\n"+
        "MONTH - расчётный период будет повторяться через календарный месяц (январь 31 день, февраль 29/28 дней). Пример: с 15 января по 15 февраля\n"
        "YEAR - расчётный период будет повторяться через год (с учётом високосных). Пример: с 1 января 2006 по 1 января 2007\n"+
        "--- - особый расчётный период"+
        "DONT_REPEAT - расчётный период без повторения", None, QtGui.QApplication.UnicodeUTF8))

        self.length_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "DAY - расчётный период будет повторяться через 86400 с,\n"
        "WEEKDAY - расчётный период будет повторяться через неделю. Пример : с понедельника по понедельник\n"+
        "MONTH - расчётный период будет повторяться через календарный месяц (январь 31 день, февраль 29/28 дней). Пример: с 15 января по 15 февраля\n"
        "YEAR - расчётный период будет повторяться через год (с учётом високосных). Пример: с 1 января 2006 по 1 января 2007\n"+
        "--- - особый расчётный период"+
        "DONT_REPEAT - расчётный период без повторения", None, QtGui.QApplication.UnicodeUTF8))



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
            print 'New sp'
            model=Object()

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
            self.connection.create(model.save("billservice_settlementperiod"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            return



        QtGui.QDialog.accept(self)

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



class SettlementPeriodChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(SettlementPeriodChild, self).__init__()
        self.connection=connection
        self.setObjectName("SettlementPeriodMDI")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,827,476).size()).expandedTo(self.minimumSizeHint()))
        self.setname = "setper_frame_period"
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0,0,821,401))

        self.tableWidget = tableFormat(self.tableWidget)
        
        self.setCentralWidget(self.tableWidget)
        
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

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

        self.addAction = QtGui.QAction(self)
        self.addAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addAction.setObjectName("addAction")

        self.delAction = QtGui.QAction(self)
        self.delAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delAction.setObjectName("delAction")
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        
        self.editAction = QtGui.QAction(self)
        self.editAction.setIcon(QtGui.QIcon("images/open.png"))
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.addAction(self.editAction)
        self.tableWidget.addAction(self.addAction)
        self.tableWidget.addAction(self.delAction)



        self.retranslateUi()
        HeaderUtil.nullifySaved(self.setname)
        self.refresh()
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)

        self.connect(self.addAction,  QtCore.SIGNAL("triggered()"), self.add_period)
        self.connect(self.delAction,  QtCore.SIGNAL("triggered()"), self.del_period)
        self.connect(self.editAction, QtCore.SIGNAL("triggered()"), self.edit_period)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_period)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        self.delNodeLocalAction()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Расчётные периоды", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        
        columns=['Id', u'Название', u'Начинается при активации', u'Начало', u'Продолжительность в периодах', u'Продолжительность в секундах']
        makeHeaders(columns, self.tableWidget)
        
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.delAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.editAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        
    def add_period(self):
        child=AddSettlementPeriod(connection=self.connection)
        child.exec_()
        self.refresh()

    def del_period(self):
        '''id=self.getSelectedId()

        if id>0 and QtGui.QMessageBox.question(self, u"Удалить расчётный период?" , u"Все связанные тарифные планы и вся статистика будут удалены.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.delete("DELETE FROM billservice_settlementperiod WHERE id=%d" % id)

        self.refresh()'''
        id=self.getSelectedId()
        if id>0:
            if self.connection.sql("""SELECT id FROM billservice_tariff WHERE (settlement_period_id=%d)""" % id):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Данный период используется в тарифных планах, удаление невозможно!!")
                return
            elif QtGui.QMessageBox.question(self, u"Удалить расчётный период?" , u"Все связанные тарифные планы и вся статистика будут удалены.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete("billservice_settlementperiod", id)
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_period(self):
        id=self.getSelectedId()
        try:
            model=self.connection.get("SELECT * FROM billservice_settlementperiod WHERE id=%d" %id)
        except:
            return


        child=AddSettlementPeriod(connection=self.connection, model=model)
        child.exec_()

        self.refresh()


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/sp.png"))
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)
    def saveHeader(self, *args):
        HeaderUtil.saveHeader(self.setname, self.tableWidget)
    def refresh(self):
        self.tableWidget.setSortingEnabled(False)
        #periods=SettlementPeriod.objects.all().order_by('id')
        #periods=self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE deleted=FALSE ORDER BY id")
        periods = self.connection.foselect("billservice_settlementperiod")
        #self.tableWidget.setRowCount(periods.count())
        self.tableWidget.setRowCount(len(periods))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for period in periods:
            self.addrow(period.id, i,0)
            self.addrow(period.name, i,1)
            self.addrow(period.autostart, i,2)
            self.addrow(period.time_start.strftime(self.strftimeFormat), i,3)
            self.addrow(period.length_in, i,4)
            
            self.addrow(period.length, i,5)
            self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
            
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)

