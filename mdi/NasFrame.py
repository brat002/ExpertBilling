#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders

NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

actions = {
'mikrotik2.8':{'create':'/ip firewall address-list remove [find comment=$user_id];/ip firewall address-list add address=$ipaddress comment=$user_id list=internet_list',
               'remove':'/ip firewall address-list remove [find comment=$user_id]',
               'enable':'/ip firewall address-list set [find comment=$user_id] disabled=no',
               'disable': '/ip firewall address-list set [find comment=$user_id] disabled=yes',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit',
               'ipn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit ',
               'pod': '/interface $access_type-server remove [find user=$username]'
               },
'mikrotik2.9':{'create':'/ip firewall address-list add list=internet_users address=$ipaddress disabled=no',
               'remove':'/ip firewall address-list remove $user_id',
               'enable':'/ip firewall address-list add address=$ipaddress list=allow_ip comment=$user_id disabled=no',
               'disable': '/ip firewall address-list remove $user_id',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit ',
               'ipn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit ',
               'pod': '/interface $access_type-server remove [find user=$username]'
               },
'mikrotik3':{'create':'/ip firewall address-list add list=internet_users address=$ipaddress disabled=no',
               'remove':'/ip firewall address-list remove $user_id',
               'enable':'/ip firewall address-list add address=$ipaddress list=allow_ip comment=$user_id disabled=no',
               'disable': '/ip firewall address-list remove $user_id',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit ',
               'ipn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit ',
               'pod': '/interface $access_type-server remove [find user=$username]'
               },
'common_ssh':{'create':'',
               'remove':'',
               'enable':'',
               'disable':'',
               'vpn_speed': '',
               'ipn_speed': '',
               'pod': ''
               },
'common_radius':{'create':'',
               'remove':'',
               'enable':'',
               'disable':'',
               'vpn_speed': '',
               'ipn_speed': '',
               'pod': ''
               },
'---':{'create':'',
               'remove':'',
               'enable':'',
               'disable':'',
               'vpn_speed': '',
               'ipn_speed': '',
               'pod': ''
               },
}

class AddNasFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(AddNasFrame, self).__init__()
        self.model = model
        self.connection = connection
        self.connection.commit()


        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,403,445).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(60,410,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.maintabWidget = QtGui.QTabWidget(self)
        self.maintabWidget.setGeometry(QtCore.QRect(10,10,391,391))
        self.maintabWidget.setObjectName("maintabWidget")

        self.general_tab = QtGui.QWidget()
        self.general_tab.setObjectName("general_tab")

        self.ssh_groupBox = QtGui.QGroupBox(self.general_tab)
        self.ssh_groupBox.setGeometry(QtCore.QRect(210,150,171,111))
        self.ssh_groupBox.setObjectName("ssh_groupBox")

        self.pushButton = QtGui.QPushButton(self.ssh_groupBox)
        self.pushButton.setGeometry(QtCore.QRect(50,80,75,24))
        self.pushButton.setObjectName("pushButton")

        self.ssh_name_label = QtGui.QLabel(self.ssh_groupBox)
        self.ssh_name_label.setGeometry(QtCore.QRect(11,22,37,20))
        self.ssh_name_label.setObjectName("ssh_name_label")

        self.ssh_name_lineEdit = QtGui.QLineEdit(self.ssh_groupBox)
        self.ssh_name_lineEdit.setGeometry(QtCore.QRect(54,22,106,20))
        self.ssh_name_lineEdit.setObjectName("ssh_name_lineEdit")

        self.ssh_password_label = QtGui.QLabel(self.ssh_groupBox)
        self.ssh_password_label.setGeometry(QtCore.QRect(11,49,37,20))
        self.ssh_password_label.setObjectName("ssh_password_label")

        self.ssh_password_lineEdit = QtGui.QLineEdit(self.ssh_groupBox)
        self.ssh_password_lineEdit.setGeometry(QtCore.QRect(54,49,106,20))
        self.ssh_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.ssh_password_lineEdit.setObjectName("ssh_password_lineEdit")

        self.services_groupBox = QtGui.QGroupBox(self.general_tab)
        self.services_groupBox.setGeometry(QtCore.QRect(10,150,171,111))
        self.services_groupBox.setObjectName("services_groupBox")

        self.pptp_checkBox = QtGui.QCheckBox(self.services_groupBox)
        self.pptp_checkBox.setGeometry(QtCore.QRect(11,21,56,18))
        self.pptp_checkBox.setObjectName("pptp_checkBox")

        self.pppoe_checkBox = QtGui.QCheckBox(self.services_groupBox)
        self.pppoe_checkBox.setGeometry(QtCore.QRect(11,45,56,18))
        self.pppoe_checkBox.setObjectName("pppoe_checkBox")

        self.ipn_checkBox = QtGui.QCheckBox(self.services_groupBox)
        self.ipn_checkBox.setGeometry(QtCore.QRect(11,69,56,18))
        self.ipn_checkBox.setObjectName("ipn_checkBox")

        self.identify_groupBox = QtGui.QGroupBox(self.general_tab)
        self.identify_groupBox.setGeometry(QtCore.QRect(10,10,371,131))
        self.identify_groupBox.setObjectName("identify_groupBox")

        self.name_label = QtGui.QLabel(self.identify_groupBox)
        self.name_label.setGeometry(QtCore.QRect(10,50,131,20))
        self.name_label.setObjectName("name_label")

        self.nas_ip = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_ip.setGeometry(QtCore.QRect(140,76,221,20))
        self.nas_ip.setObjectName("nas_ip")

        self.nas_comboBox = QtGui.QComboBox(self.identify_groupBox)
        self.nas_comboBox.setGeometry(QtCore.QRect(140,24,221,20))
        self.nas_comboBox.setObjectName("nas_comboBox")

        self.ip_label = QtGui.QLabel(self.identify_groupBox)
        self.ip_label.setGeometry(QtCore.QRect(10,76,131,20))
        self.ip_label.setObjectName("ip_label")

        self.secret_label = QtGui.QLabel(self.identify_groupBox)
        self.secret_label.setGeometry(QtCore.QRect(10,102,131,20))
        self.secret_label.setObjectName("secret_label")

        self.nas_name = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_name.setGeometry(QtCore.QRect(140,50,221,20))
        self.nas_name.setObjectName("nas_name")

        self.type_label = QtGui.QLabel(self.identify_groupBox)
        self.type_label.setGeometry(QtCore.QRect(10,24,131,20))
        self.type_label.setObjectName("type_label")

        self.nas_secret = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_secret.setGeometry(QtCore.QRect(140,102,221,20))
        self.nas_secret.setObjectName("nas_secret")
        self.maintabWidget.addTab(self.general_tab,"")

        self.commands_tab = QtGui.QWidget()
        self.commands_tab.setObjectName("commands_tab")

        self.create_user_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.create_user_textEdit.setGeometry(QtCore.QRect(10,30,371,20))
        self.create_user_textEdit.setObjectName("create_user_textEdit")

        self.create_user_label = QtGui.QLabel(self.commands_tab)
        self.create_user_label.setGeometry(QtCore.QRect(10,10,371,16))
        self.create_user_label.setObjectName("create_user_label")

        self.remove_user_label = QtGui.QLabel(self.commands_tab)
        self.remove_user_label.setGeometry(QtCore.QRect(10,60,371,16))
        self.remove_user_label.setObjectName("remove_user_label")

        self.remove_user_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.remove_user_textEdit.setGeometry(QtCore.QRect(10,80,371,20))
        self.remove_user_textEdit.setObjectName("remove_user_textEdit")

        self.enable_user_label = QtGui.QLabel(self.commands_tab)
        self.enable_user_label.setGeometry(QtCore.QRect(10,110,371,16))
        self.enable_user_label.setObjectName("enable_user_label")

        self.enable_user_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.enable_user_textEdit.setGeometry(QtCore.QRect(10,130,371,20))
        self.enable_user_textEdit.setObjectName("enable_user_textEdit")

        self.disable_user_label = QtGui.QLabel(self.commands_tab)
        self.disable_user_label.setGeometry(QtCore.QRect(10,160,371,16))
        self.disable_user_label.setObjectName("disable_user_label")

        self.disable_user_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.disable_user_textEdit.setGeometry(QtCore.QRect(10,180,371,20))
        self.disable_user_textEdit.setObjectName("disable_user_textEdit")

        self.pod_label = QtGui.QLabel(self.commands_tab)
        self.pod_label.setGeometry(QtCore.QRect(10,210,371,16))
        self.pod_label.setObjectName("pod_label")

        self.pod_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.pod_textEdit.setGeometry(QtCore.QRect(10,230,371,20))
        self.pod_textEdit.setObjectName("pod_textEdit")

        self.set_vpn_speed_label = QtGui.QLabel(self.commands_tab)
        self.set_vpn_speed_label.setGeometry(QtCore.QRect(10,260,371,16))
        self.set_vpn_speed_label.setObjectName("set_vpn_speed_label")

        self.set_vpn_speed_textEdit = QtGui.QLineEdit(self.commands_tab)
        self.set_vpn_speed_textEdit.setGeometry(QtCore.QRect(10,280,371,20))
        self.set_vpn_speed_textEdit.setObjectName("set_vpn_speed_textEdit")

        self.set_ipn_speed_label = QtGui.QLabel(self.commands_tab)
        self.set_ipn_speed_label.setGeometry(QtCore.QRect(10,310,371,16))
        self.set_ipn_speed_label.setObjectName("set_ipn_speed_label")

        self.set_ipn_speed_lineEdit = QtGui.QLineEdit(self.commands_tab)
        self.set_ipn_speed_lineEdit.setGeometry(QtCore.QRect(10,330,371,20))
        self.set_ipn_speed_lineEdit.setObjectName("set_ipn_speed_lineEdit")
        
        self.maintabWidget.addTab(self.commands_tab,"")
        self.ssh_name_label.setBuddy(self.ssh_name_lineEdit)
        self.ssh_password_label.setBuddy(self.ssh_password_lineEdit)
        self.name_label.setBuddy(self.nas_name)
        self.ip_label.setBuddy(self.nas_ip)
        self.secret_label.setBuddy(self.nas_secret)
        self.type_label.setBuddy(self.nas_comboBox)

        
        self.setTabOrder(self.maintabWidget,self.nas_comboBox)
        self.setTabOrder(self.nas_comboBox,self.nas_name)
        self.setTabOrder(self.nas_name,self.nas_ip)
        self.setTabOrder(self.nas_ip,self.nas_secret)
        self.setTabOrder(self.nas_secret,self.pptp_checkBox)
        self.setTabOrder(self.pptp_checkBox,self.pppoe_checkBox)
        self.setTabOrder(self.pppoe_checkBox,self.ipn_checkBox)
        self.setTabOrder(self.ipn_checkBox,self.ssh_name_lineEdit)
        self.setTabOrder(self.ssh_name_lineEdit,self.ssh_password_lineEdit)
        self.setTabOrder(self.ssh_password_lineEdit,self.pushButton)
        self.setTabOrder(self.pushButton,self.buttonBox)

        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.testNAS)

                
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.fixtures()
        QtCore.QObject.connect(self.nas_comboBox,QtCore.SIGNAL("currentIndexChanged(int)"),self.refillActions)
        self.retranslateUi()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки сервера доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "SSH", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_name_label.setText(QtGui.QApplication.translate("Dialog", "Имя", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_password_label.setText(QtGui.QApplication.translate("Dialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.services_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Разрешённые сервисы", None, QtGui.QApplication.UnicodeUTF8))
        self.pptp_checkBox.setText(QtGui.QApplication.translate("Dialog", "PPTP", None, QtGui.QApplication.UnicodeUTF8))
        self.pppoe_checkBox.setText(QtGui.QApplication.translate("Dialog", "PPPOE", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_checkBox.setText(QtGui.QApplication.translate("Dialog", "IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.identify_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Сетевая идентификация", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Сетевое имя", None, QtGui.QApplication.UnicodeUTF8))
        #self.nas_ip.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_ip.setValidator(self.ipValidator)
        self.ip_label.setText(QtGui.QApplication.translate("Dialog", "IP", None, QtGui.QApplication.UnicodeUTF8))
        self.secret_label.setText(QtGui.QApplication.translate("Dialog", "Секретная фраза", None, QtGui.QApplication.UnicodeUTF8))
        self.type_label.setText(QtGui.QApplication.translate("Dialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.maintabWidget.setTabText(self.maintabWidget.indexOf(self.general_tab), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.create_user_label.setText(QtGui.QApplication.translate("Dialog", "Создать пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_user_label.setText(QtGui.QApplication.translate("Dialog", "Удалить пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.enable_user_label.setText(QtGui.QApplication.translate("Dialog", "Активировать пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.disable_user_label.setText(QtGui.QApplication.translate("Dialog", "Деактивировать пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.pod_label.setText(QtGui.QApplication.translate("Dialog", "Сбросить сессию пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.set_vpn_speed_label.setText(QtGui.QApplication.translate("Dialog", "Установить скорость для VPN клиента", None, QtGui.QApplication.UnicodeUTF8))
        self.set_ipn_speed_label.setText(QtGui.QApplication.translate("Dialog", "Установить скорость для IPN клиента", None, QtGui.QApplication.UnicodeUTF8))
        self.maintabWidget.setTabText(self.maintabWidget.indexOf(self.commands_tab), QtGui.QApplication.translate("Dialog", "Команды", None, QtGui.QApplication.UnicodeUTF8))



    def testNAS(self):
        if not self.connection.testCredentials(str(self.nas_ip.text()), str(self.ssh_name_lineEdit.text()), str(self.ssh_password_lineEdit.text())):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не верно указаны параметры для доступа, сервер доступа недоступен или неправильно настроен."))
        else:
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok"))
         
    def refillActions(self):
        self.maintabWidget.setCurrentIndex(1)
        nas_type = unicode(self.nas_comboBox.currentText())
        if nas_type=='---':
            return
        
        self.create_user_textEdit.setText(actions[nas_type]['create'])
        self.remove_user_textEdit.setText(actions[nas_type]['remove'])
        
        self.enable_user_textEdit.setText(actions[nas_type]['enable'])
        self.disable_user_textEdit.setText(actions[nas_type]['disable'])
        
        self.set_vpn_speed_textEdit.setText(actions[nas_type]['vpn_speed'])
        self.set_ipn_speed_lineEdit.setText(actions[nas_type]['ipn_speed'])
        self.pod_textEdit.setText(actions[nas_type]['pod'])
        pass
    
    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if unicode(self.nas_comboBox.currentText())==u"---":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не выбрали тип сервера доступа"))
            return
            
        if self.model:
            model=self.model
        else:
            print 'New nas'
            model=Object()

        if unicode(self.nas_name.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан идентификатор сервера доступа"))
            return

        if unicode(self.ssh_name_lineEdit.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано имя пользователя для SSH"))
            return

        if unicode(self.ssh_password_lineEdit.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан пароль для SSH"))
            return

        if unicode(self.nas_ip.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан IP адрес сервера доступа"))
            return
        
        if self.ipValidator.validate(self.nas_ip.text(), 0)[0]  != QtGui.QValidator.Acceptable:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите IP адрес сервера доступа до конца."))
            return

        if unicode(self.nas_secret.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана секретная фраза"))
            return

        model.login = unicode(self.ssh_name_lineEdit.text())
        model.password = unicode(self.ssh_password_lineEdit.text())
        model.type = unicode(self.nas_comboBox.currentText())
        model.name = unicode(self.nas_name.text())
        model.ipaddress = unicode(self.nas_ip.text())
        model.secret = unicode(self.nas_secret.text())

        model.allow_pptp = self.pptp_checkBox.checkState()==2
        model.allow_pppoe = self.pppoe_checkBox.checkState()==2
        model.allow_ipn = self.ipn_checkBox.checkState()==2

        model.user_add_action= unicode(self.create_user_textEdit.text() or "")
        model.user_delete_action= unicode(self.remove_user_textEdit.text() or "")
        model.user_enable_action= unicode(self.enable_user_textEdit.text() or "")
        model.user_disable_action= unicode(self.disable_user_textEdit.text() or "")
        model.user_disable_action= unicode(self.disable_user_textEdit.text() or "")
        model.vpn_speed_action = unicode(self.set_vpn_speed_textEdit.text() or "")
        model.ipn_speed_action = unicode(self.set_ipn_speed_lineEdit.text() or "")
        model.reset_action = unicode(self.pod_textEdit.text() or "")
        

        

        try:
            self.connection.create(model.save(table="nas_nas"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()

        QtGui.QDialog.accept(self)

    def fixtures(self):


        nasses = NAS_LIST
        self.nas_comboBox.addItem('---')
        for nas, value in nasses:
            self.nas_comboBox.addItem(nas)

        if self.model:
            self.nas_name.setText(unicode(self.model.name))
            self.nas_ip.setText(unicode(self.model.ipaddress))
            self.nas_secret.setText(unicode(self.model.secret))
            self.ssh_name_lineEdit.setText(unicode(self.model.login))
            self.ssh_password_lineEdit.setText(unicode(self.model.password))

            self.create_user_textEdit.setText(unicode(self.model.user_add_action))
            self.remove_user_textEdit.setText(unicode(self.model.user_delete_action))
            self.enable_user_textEdit.setText(unicode(self.model.user_enable_action))
            self.disable_user_textEdit.setText(unicode(self.model.user_disable_action))
            
            
            self.set_vpn_speed_textEdit.setText(unicode(self.model.vpn_speed_action))
            self.set_ipn_speed_lineEdit.setText(unicode(self.model.ipn_speed_action))
            
            
            self.pod_textEdit.setText(unicode(self.model.reset_action))
            

            self.nas_comboBox.setCurrentIndex(self.nas_comboBox.findText(self.model.type, QtCore.Qt.MatchCaseSensitive))

            self.pptp_checkBox.setCheckState(self.model.allow_pptp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.pppoe_checkBox.setCheckState(self.model.allow_pppoe == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.ipn_checkBox.setCheckState(self.model.allow_ipn == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )





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

        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        self.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        #self.show()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Серверы доступа", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.clear()
        columns=[u"id", u"Имя", u"Тип", u"IP"]
        makeHeaders(columns, self.tableWidget)


        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        self.addAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        

        self.delAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        

        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "Конфигурировать", None, QtGui.QApplication.UnicodeUTF8))
        


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
            