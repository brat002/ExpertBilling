#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from helpers import Object as Object
   
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

class AddNasFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(AddNasFrame, self).__init__()
        self.model = model
        self.connection = connection
        self.connection.commit()


        #self.setObjectName("self")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,422,338).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(70,300,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)


        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(10,10,401,281))

        self.tab = QtGui.QWidget()


        self.groupBox = QtGui.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(210,130,171,121))


        self.testButton = QtGui.QPushButton(self.groupBox)
        self.testButton.setGeometry(QtCore.QRect(50,80,75,24))


        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(10,20,161,58))


        self.gridlayout = QtGui.QGridLayout(self.widget)


        self.label_5 = QtGui.QLabel(self.widget)

        self.gridlayout.addWidget(self.label_5,0,0,1,1)

        self.ssh_name_edit = QtGui.QLineEdit(self.widget)

        self.gridlayout.addWidget(self.ssh_name_edit,0,1,1,1)

        self.label_6 = QtGui.QLabel(self.widget)
        self.gridlayout.addWidget(self.label_6,1,0,1,1)

        self.ssh_password_edit = QtGui.QLineEdit()

        self.gridlayout.addWidget(self.ssh_password_edit,1,1,1,1)

        self.groupBox_2 = QtGui.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(10,140,171,111))


        self.widget1 = QtGui.QWidget(self.groupBox_2)
        self.widget1.setGeometry(QtCore.QRect(10,20,88,78))


        self.gridlayout1 = QtGui.QGridLayout(self.widget1)


        self.pptp_edit = QtGui.QCheckBox(self.widget1)

        self.gridlayout1.addWidget(self.pptp_edit,0,0,1,1)

        self.pppoe_edit = QtGui.QCheckBox(self.widget1)

        self.gridlayout1.addWidget(self.pppoe_edit,1,0,1,1)

        self.ipn_edit = QtGui.QCheckBox(self.widget1)

        self.gridlayout1.addWidget(self.ipn_edit,2,0,1,1)

        self.widget2 = QtGui.QWidget(self.tab)
        self.widget2.setGeometry(QtCore.QRect(10,20,371,120))


        self.gridlayout2 = QtGui.QGridLayout(self.widget2)


        self.label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.label,0,0,1,1)

        self.nas_type_edit = QtGui.QComboBox(self.widget2)

        self.gridlayout2.addWidget(self.nas_type_edit,0,1,1,1)

        self.label_2 = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.label_2,1,0,1,1)

        self.nas_name_edit = QtGui.QLineEdit()

        self.gridlayout2.addWidget(self.nas_name_edit,1,1,1,1)

        self.label_3 = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.label_3,2,0,1,1)

        self.nas_ip_edit = QtGui.QLineEdit(self.widget2)

        self.gridlayout2.addWidget(self.nas_ip_edit,2,1,1,1)

        self.label_4 = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.label_4,3,0,1,1)

        self.nas_secret_edit = QtGui.QLineEdit(self.widget2)

        self.gridlayout2.addWidget(self.nas_secret_edit,3,1,1,1)
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()

        self.tabWidget_2 = QtGui.QTabWidget(self.tab_2)
        self.tabWidget_2.setGeometry(QtCore.QRect(10,10,381,480))


        self.tab_3 = QtGui.QWidget()


        self.widget3 = QtGui.QWidget(self.tab_3)
        self.widget3.setGeometry(QtCore.QRect(10,110,361,91))


        self.vboxlayout = QtGui.QVBoxLayout(self.widget3)


        self.label_8 = QtGui.QLabel(self.widget3)

        self.vboxlayout.addWidget(self.label_8)

        self.user_remove_edit = QtGui.QTextEdit(self.widget3)

        self.vboxlayout.addWidget(self.user_remove_edit)

        self.widget4 = QtGui.QWidget(self.tab_3)
        self.widget4.setGeometry(QtCore.QRect(10,10,361,91))


        self.vboxlayout1 = QtGui.QVBoxLayout(self.widget4)


        self.label_7 = QtGui.QLabel(self.widget4)

        self.vboxlayout1.addWidget(self.label_7)

        self.user_add_edit = QtGui.QTextEdit("")

        self.vboxlayout1.addWidget(self.user_add_edit)
        self.tabWidget_2.addTab(self.tab_3,"")

        self.tab_4 = QtGui.QWidget()


        self.widget5 = QtGui.QWidget(self.tab_4)
        self.widget5.setGeometry(QtCore.QRect(10,110,361,91))


        self.vboxlayout2 = QtGui.QVBoxLayout(self.widget5)


        self.label_10 = QtGui.QLabel(self.widget5)

        self.vboxlayout2.addWidget(self.label_10)

        self.user_disable_edit = QtGui.QTextEdit(self.widget5)

        self.vboxlayout2.addWidget(self.user_disable_edit)

        self.widget6 = QtGui.QWidget(self.tab_4)
        self.widget6.setGeometry(QtCore.QRect(10,10,361,91))

        self.vboxlayout3 = QtGui.QVBoxLayout(self.widget6)



        self.label_9 = QtGui.QLabel(self.widget6)

        self.vboxlayout3.addWidget(self.label_9)

        self.user_enable_edit = QtGui.QTextEdit(self.widget6)
        self.vboxlayout3.addWidget(self.user_enable_edit)

        self.tabWidget_2.addTab(self.tab_4,"")
        self.tabWidget.addTab(self.tab_2,"")


        self.label_5.setBuddy(self.ssh_name_edit)
        self.label_6.setBuddy(self.ssh_password_edit)
        self.label.setBuddy(self.nas_type_edit)
        self.label_2.setBuddy(self.nas_name_edit)
        self.label_3.setBuddy(self.nas_ip_edit)
        self.label_4.setBuddy(self.nas_secret_edit)
        self.label_8.setBuddy(self.user_remove_edit)
        self.label_7.setBuddy(self.user_add_edit)
        self.label_10.setBuddy(self.user_disable_edit)
        self.label_9.setBuddy(self.user_enable_edit)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)

        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        QtCore.QObject.connect(self.testButton,QtCore.SIGNAL("clicked()"),self.testNAS)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        #QtCore.QMetaObject.connectSlotsByName(self)

    def testNAS(self):
        if not self.connection.testCredentials(str(self.nas_ip_edit.text()), str(self.ssh_name_edit.text()), str(self.ssh_password_edit.text())):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не верно указаны параметры для доступа, сервер доступа недоступен или неправильно настроен."))
        else:
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok"))
        

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры SSH", None, QtGui.QApplication.UnicodeUTF8))
        self.testButton.setText(QtGui.QApplication.translate("Dialog", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "<b>Имя</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "<b>Пароль</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Разрешённые сервисы", None, QtGui.QApplication.UnicodeUTF8))
        self.pptp_edit.setText(QtGui.QApplication.translate("Dialog", "PPTP", None, QtGui.QApplication.UnicodeUTF8))
        self.pppoe_edit.setText(QtGui.QApplication.translate("Dialog", "PPPOE", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_edit.setText(QtGui.QApplication.translate("Dialog", "IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<b>Тип</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "<b>Identify</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "<b>IP</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_ip_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "<b>Secret</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Настройки доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Действие при удалении пользователя: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Действие при создании пользователя: ", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Создание/Удаление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Dialog", "Действие при запрещении работы пользователя: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Действие при разрешении работы пользователя:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), QtGui.QApplication.translate("Dialog", "Активация/Деактивация", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Команды управления", None, QtGui.QApplication.UnicodeUTF8))


        #self.connect(self.button_add,  QtCore.SIGNAL("clicked()"), self.save)
        #self.connect(self.button_add, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))


        self.fixtures()

    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:
            model=self.model
        else:
            print 'New nas'
            model=Object()

        if unicode(self.nas_name_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан идентификатор сервера доступа"))
            return

        if unicode(self.ssh_name_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано имя пользователя для SSH"))
            return

        if unicode(self.ssh_password_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан пароль для SSH"))
            return

        if unicode(self.nas_ip_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан IP адрес сервера доступа"))
            return

        if unicode(self.nas_secret_edit.text())==u"":
            QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана секретная фраза"))
            return

        model.login = unicode(self.ssh_name_edit.text())
        model.password = unicode(self.ssh_password_edit.text())
        model.type = unicode(self.nas_type_edit.currentText())
        model.name = unicode(self.nas_name_edit.text())
        model.ipaddress = unicode(self.nas_ip_edit.text())
        model.secret = unicode(self.nas_secret_edit.text())

        model.allow_pptp = self.pptp_edit.checkState()==2
        model.allow_pppoe = self.pppoe_edit.checkState()==2
        model.allow_ipn = self.ipn_edit.checkState()==2

        model.user_add_action= unicode(self.user_add_edit.toPlainText() or "")
        model.user_delete_action= unicode(self.user_remove_edit.toPlainText() or "")
        model.user_enable_action= unicode(self.user_enable_edit.toPlainText() or "")
        model.user_disable_action= unicode(self.user_disable_edit.toPlainText() or "")

        

        try:
            self.connection.create(model.save(table="nas_nas"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()

        QtGui.QDialog.accept(self)

    def fixtures(self):


        nasses = NAS_LIST
        for nas, value in nasses:
            self.nas_type_edit.addItem(nas)

        if self.model:
            self.nas_name_edit.setText(unicode(self.model.name))
            self.nas_ip_edit.setText(unicode(self.model.ipaddress))
            self.nas_secret_edit.setText(unicode(self.model.secret))
            self.nas_ip_edit.setText(unicode(self.model.ipaddress))
            self.ssh_name_edit.setText(unicode(self.model.login))
            self.ssh_password_edit.setText(unicode(self.model.password))

            self.user_add_edit.setText(unicode(self.model.user_add_action))
            self.user_remove_edit.setText(unicode(self.model.user_delete_action))
            self.user_enable_edit.setText(unicode(self.model.user_enable_action))
            self.user_disable_edit.setText(unicode(self.model.user_disable_action))

            self.nas_type_edit.setCurrentIndex(self.nas_type_edit.findText(self.model.type, QtCore.Qt.MatchCaseSensitive))

            self.pptp_edit.setCheckState(self.model.allow_pptp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.pppoe_edit.setCheckState(self.model.allow_pppoe == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.ipn_edit.setCheckState(self.model.allow_ipn == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )





class NasMdiChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(NasMdiChild, self).__init__()
        #global connection
        self.connection=connection
        #MainWindow.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,300,300).size()).expandedTo(self.minimumSizeHint()))


        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget = tableFormat(self.tableWidget)


        self.setCentralWidget(self.tableWidget)

        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        #self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.addAction = QtGui.QAction(self)
        self.addAction.setIcon(QtGui.QIcon("images/add.png"))

        self.delAction = QtGui.QAction(self)
        self.delAction.setIcon(QtGui.QIcon("images/del.png"))

        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setMenuRole(QtGui.QAction.NoRole)

        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addAction(self.configureAction)
        
        
#===============================================================================
#        length_edit = QtGui.QComboBox()
#        self.toolBar.addWidget(length_edit)
#===============================================================================

        self.retranslateUi()
        self.refresh()
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        #self.show()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Управление серевами доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns=["id", "Name", "Type", "IP", '']
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)



        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        self.addAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)

        self.delAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)

        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "Конфигурировать", None, QtGui.QApplication.UnicodeUTF8))
        self.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)


    def addframe(self):

        model=None
        addf = AddNasFrame(connection=self.connection, model=model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def configure(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=self.connection.get("SELECT * FROM nas_nas WHERE id=%d" % self.getSelectedId())
        except:
            return
        import Pyro.core

        if self.connection.configureNAS(str(model.ipaddress), str(model.login), str(model.password), str(model.confstring)):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Настройка сервера доступа прошла удачно."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка во время конфигурирования."))



    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u"Все связанные с сервером доступа аккаунты \n и вся статистика будут удалены. Вы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                self.connection.delete("DELETE FROM nas_nas WHERE id=%d" % self.getSelectedId())
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
        self.refresh()


    def editframe(self):
        try:
            model=self.connection.get("SELECT * FROM nas_nas WHERE id=%d" % self.getSelectedId())
        except:
            model=None

        addf = AddNasFrame(connection=self.connection, model=model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):

        #nasses=Nas.objects.all().order_by('id')
        nasses=self.connection.sql("SELECT * FROM nas_nas ORDER BY id")
        #self.tableWidget.setRowCount(nasses.count())
        self.tableWidget.setRowCount(len(nasses))
        i=0
        for nas in nasses:
            self.addrow(nas.id, i,0)
            self.addrow(nas.name, i,1)
            self.addrow(nas.type, i,2)
            self.addrow(nas.ipaddress, i,3)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

            
        self.tableWidget.resizeColumnsToContents()

    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.configureAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.configureAction.setDisabled(False)
            