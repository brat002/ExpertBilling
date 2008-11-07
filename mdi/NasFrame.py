#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil

from ebsWindow import ebsTableWindow

NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

actions = {
'mikrotik2.8':{'create':'/ip firewall address-list add list=internet_users address=$account_ipn_ip disabled=no comment=$user_id',
               'remove':'/ip firewall address-list remove [find comment=$user_id];/queue simple remove [find name=$account_ipn_ip]',
               'enable':'/ip firewall address-list set [find comment=$user_id] address=$account_ipn_ip disabled=no',
               'disable': '/ip firewall address-list set [find comment=$user_id] disabled=yes',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit',
               'ipn_speed': '/queue simple remove [find name=$account_ipn_ip]; /queue simple add name=$account_ipn_ip max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit target-addresses=$account_ipn_ip/32',
               'pod': '/interface $access_type-server remove [find user=$username]'
               },
'mikrotik2.9':{'create':'/ip firewall address-list add list=internet_users address=$account_ipn_ip disabled=no comment=$user_id',
               'remove':'/ip firewall address-list remove [find comment=$user_id];/queue simple remove [find name=$account_ipn_ip]',
               'enable':'/ip firewall address-list set [find comment=$user_id] address=$account_ipn_ip disabled=no',
               'disable': '/ip firewall address-list set [find comment=$user_id] disabled=yes',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit',
               'ipn_speed': '/queue simple remove [find name=$account_ipn_ip]; /queue simple add name=$account_ipn_ip max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit target-addresses=$account_ipn_ip/32',
               'pod': '/interface $access_type-server remove [find user=$username]'
               },
'mikrotik3':{'create':'/ip firewall address-list add list=internet_users address=$account_ipn_ip disabled=no comment=$user_id',
               'remove':'/ip firewall address-list remove [find comment=$user_id];/queue simple remove [find comment=$username-$user_id]',
               'enable':'/ip firewall address-list set [find comment=$user_id] address=$account_ipn_ip disabled=no',
               'disable': '/ip firewall address-list set [find comment=$user_id] disabled=yes',
               'vpn_speed': '/queue simple set [find interface=<$access_type-$username>] max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit',
               'ipn_speed': '/queue simple remove [find comment=$username-$user_id]; /queue simple add name=$username max-limit=$max_limit burst-limit=$burst_limit burst-threshold=$burst_treshold burst-time=$burst_time priority=$priority limit-at=$min_limit comment=$username-$user_id  target-addresses=$account_ipn_ip/32',
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
class ConfigureDialog(QtGui.QDialog):
    def __init__(self):
        super(ConfigureDialog, self).__init__()
        self.setObjectName("ConfigureDialog")
        self.resize(354, 484)
        self.setMinimumSize(QtCore.QSize(354, 490))
        self.setMaximumSize(QtCore.QSize(354, 490))
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.groupBox_options = QtGui.QGroupBox(self)
        self.groupBox_options.setObjectName("groupBox_options")
        self.groupBox_pptp = QtGui.QGroupBox(self.groupBox_options)
        self.groupBox_pptp.setGeometry(QtCore.QRect(11, 25, 314, 101))
        self.groupBox_pptp.setCheckable(True)
        self.groupBox_pptp.setChecked(False)
        self.groupBox_pptp.setObjectName("groupBox_pptp")
        self.lineEdit_pptp_ip = QtGui.QLineEdit(self.groupBox_pptp)
        self.lineEdit_pptp_ip.setGeometry(QtCore.QRect(11, 45, 292, 21))
        self.lineEdit_pptp_ip.setObjectName("lineEdit_pptp_ip")
        self.label_pptp_ip = QtGui.QLabel(self.groupBox_pptp)
        self.label_pptp_ip.setGeometry(QtCore.QRect(11, 25, 292, 16))
        self.label_pptp_ip.setObjectName("label_pptp_ip")
        self.checkBox_pptp_pap = QtGui.QCheckBox(self.groupBox_pptp)
        self.checkBox_pptp_pap.setGeometry(QtCore.QRect(11, 71, 93, 19))
        self.checkBox_pptp_pap.setObjectName("checkBox_pptp_pap")
        self.checkBox_pptp_chap = QtGui.QCheckBox(self.groupBox_pptp)
        self.checkBox_pptp_chap.setGeometry(QtCore.QRect(110, 71, 94, 19))
        self.checkBox_pptp_chap.setChecked(True)
        self.checkBox_pptp_chap.setObjectName("checkBox_pptp_chap")
        self.checkBox_pptp_mschap2 = QtGui.QCheckBox(self.groupBox_pptp)
        self.checkBox_pptp_mschap2.setGeometry(QtCore.QRect(210, 71, 93, 19))
        self.checkBox_pptp_mschap2.setObjectName("checkBox_pptp_mschap2")
        self.groupBox_firewall = QtGui.QGroupBox(self.groupBox_options)
        self.groupBox_firewall.setGeometry(QtCore.QRect(11, 270, 314, 61))
        self.groupBox_firewall.setCheckable(False)
        self.groupBox_firewall.setObjectName("groupBox_firewall")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_firewall)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.checkBox_configure_gateway = QtGui.QCheckBox(self.groupBox_firewall)
        self.checkBox_configure_gateway.setObjectName("checkBox_configure_gateway")
        self.gridLayout_4.addWidget(self.checkBox_configure_gateway, 0, 0, 1, 1)
        self.groupBox_radius = QtGui.QGroupBox(self.groupBox_options)
        self.groupBox_radius.setGeometry(QtCore.QRect(10, 140, 311, 122))
        self.groupBox_radius.setCheckable(True)
        self.groupBox_radius.setChecked(False)
        self.groupBox_radius.setObjectName("groupBox_radius")
        self.label_radiu_server_ip = QtGui.QLabel(self.groupBox_radius)
        self.label_radiu_server_ip.setGeometry(QtCore.QRect(11, 25, 289, 16))
        self.label_radiu_server_ip.setObjectName("label_radiu_server_ip")
        self.lineEdit_radius_server_ip = QtGui.QLineEdit(self.groupBox_radius)
        self.lineEdit_radius_server_ip.setGeometry(QtCore.QRect(11, 45, 289, 21))
        self.lineEdit_radius_server_ip.setObjectName("lineEdit_radius_server_ip")
        self.timeEdit_interim_update = QtGui.QTimeEdit(self.groupBox_radius)
        self.timeEdit_interim_update.setGeometry(QtCore.QRect(11, 91, 289, 21))
        self.timeEdit_interim_update.setMinimumTime(QtCore.QTime(0, 0, 30))
        self.timeEdit_interim_update.setCurrentSection(QtGui.QDateTimeEdit.SecondSection)
        self.timeEdit_interim_update.setCalendarPopup(False)
        self.timeEdit_interim_update.setObjectName("timeEdit_interim_update")
        self.label_interim = QtGui.QLabel(self.groupBox_radius)
        self.label_interim.setGeometry(QtCore.QRect(11, 71, 289, 16))
        self.label_interim.setObjectName("label_interim")
        self.groupBox_security = QtGui.QGroupBox(self.groupBox_options)
        self.groupBox_security.setGeometry(QtCore.QRect(11, 340, 314, 86))
        self.groupBox_security.setObjectName("groupBox_security")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_security)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBox_smtp_spamers = QtGui.QCheckBox(self.groupBox_security)
        self.checkBox_smtp_spamers.setObjectName("checkBox_smtp_spamers")
        self.gridLayout_2.addWidget(self.checkBox_smtp_spamers, 0, 0, 1, 1)
        self.checkBox_malicious_trafic = QtGui.QCheckBox(self.groupBox_security)
        self.checkBox_malicious_trafic.setObjectName("checkBox_malicious_trafic")
        self.gridLayout_2.addWidget(self.checkBox_malicious_trafic, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_options, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите нужную конфигурацию", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_options.setTitle(QtGui.QApplication.translate("Dialog", "Выберите нужные опции", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_pptp.setTitle(QtGui.QApplication.translate("Dialog", "Включить PPTP сервер", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_pptp_ip.setToolTip(QtGui.QApplication.translate("Dialog", "Виртуальный адрес, который получит внутренний интерфейс PPTP сервера при подключении клиента.\n"
                                                                      "К примеру 192.168.10.1, 192.168.11.1, 172.31.3.1 и т.д.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_pptp_ip.setText(QtGui.QApplication.translate("Dialog", "Виртуальный IP адрес PPTP сервера", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_pptp_pap.setText(QtGui.QApplication.translate("Dialog", "PAP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_pptp_chap.setText(QtGui.QApplication.translate("Dialog", "CHAP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_pptp_mschap2.setText(QtGui.QApplication.translate("Dialog", "MSCHAP2", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_firewall.setTitle(QtGui.QApplication.translate("Dialog", "Базовая настройка файервола", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_configure_gateway.setText(QtGui.QApplication.translate("Dialog", "Настроить для использования шлюзом в интернет", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius.setTitle(QtGui.QApplication.translate("Dialog", "Включить RADIUS авторизацию для PPTP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radiu_server_ip.setToolTip(QtGui.QApplication.translate("Dialog", "IP адрес сервера с биллингом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radiu_server_ip.setText(QtGui.QApplication.translate("Dialog", "IP адрес RADIUS сервера", None, QtGui.QApplication.UnicodeUTF8))
        self.timeEdit_interim_update.setToolTip(QtGui.QApplication.translate("Dialog", "Интервал времени, через который на RADIUS сервер должны поступать Accounting пакеты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_interim.setText(QtGui.QApplication.translate("Dialog", "Interim Interval", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_security.setTitle(QtGui.QApplication.translate("Dialog", "Безопасность", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_smtp_spamers.setText(QtGui.QApplication.translate("Dialog", "Защитить от SMTP спамеров", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_malicious_trafic.setText(QtGui.QApplication.translate("Dialog", "Защитить от вредоносного трафика", None, QtGui.QApplication.UnicodeUTF8))

        ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/[0-9][0-9]?)?\b")
        ipValidator = QtGui.QRegExpValidator(ipRx, self)
        
        self.lineEdit_pptp_ip.setValidator(ipValidator)
        self.lineEdit_radius_server_ip.setValidator(ipValidator)

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
        self.nas_secret.setEchoMode(QtGui.QLineEdit.Password)
        self.nas_secret.setObjectName("nas_secret")
        
        self.multilink_checkBox = QtGui.QCheckBox(self.general_tab)
        self.multilink_checkBox.setGeometry(QtCore.QRect(10,280,220,20))
        self.multilink_checkBox.setObjectName("multilink_checkBox")
        
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
        self.multilink_checkBox.setText(QtGui.QApplication.translate("Dialog", "Разрешить Multilink подключения", None, QtGui.QApplication.UnicodeUTF8))
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
        
        #Whats is
        self.pushButton.setWhatsThis(QtGui.QApplication.translate("Dialog", "Нажмите на эту кнопку чтобы проверить правильность введённых вами данных.", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_name_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Имя пользователя для доступа по SSH к серверу доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_password_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Пароль для доступа по SSH к серверу доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_name.setWhatsThis(QtGui.QApplication.translate("Dialog", "Имя сервера доступа для RADIUS авторизации.", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_ip.setWhatsThis(QtGui.QApplication.translate("Dialog", "IP адрес сервера доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_secret.setWhatsThis(QtGui.QApplication.translate("Dialog", "Секретная фраза для идентификации сервера доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_comboBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Тип сервера доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.pptp_checkBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Серверу доступа разрешено принимать PPTP подключения.", None, QtGui.QApplication.UnicodeUTF8))
        self.pppoe_checkBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Серверу доступа разрешено принимать PPPOE подключения.", None, QtGui.QApplication.UnicodeUTF8))
        self.multilink_checkBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Разрешить подключаться по PPTP/PPPOE к серверу доступа нескольким пользователям с одним логином.\nПри активации данной функции логин пользователя становиться не привязанным к VPN IP при PPTP подключении и MAC адресу при PPPOE подключении. Внимание, функция может не поддериваться вашим сервером доступа.", None, QtGui.QApplication.UnicodeUTF8))
    def testNAS(self):
        if not self.connection.testCredentials(str(self.nas_ip.text()), str(self.ssh_name_lineEdit.text()), str(self.ssh_password_lineEdit.text())):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не верно указаны параметры для доступа, сервер доступа недоступен или неправильно настроен."))
        else:
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok"))
         
    def refillActions(self):
        self.maintabWidget.setCurrentIndex(1)
        nas_type = unicode(self.nas_comboBox.currentText())

        
        self.create_user_textEdit.setText(actions[nas_type]['create'])
        self.remove_user_textEdit.setText(actions[nas_type]['remove'])
        
        self.enable_user_textEdit.setText(actions[nas_type]['enable'])
        self.disable_user_textEdit.setText(actions[nas_type]['disable'])
        
        self.set_vpn_speed_textEdit.setText(actions[nas_type]['vpn_speed'])
        self.set_ipn_speed_lineEdit.setText(actions[nas_type]['ipn_speed'])
        self.pod_textEdit.setText(actions[nas_type]['pod'])
        if nas_type=='---':
            self.buttonBox.setDisabled(True)
        else:
            self.buttonBox.setDisabled(False)
    
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
        model.multilink = self.multilink_checkBox.checkState()==2

        model.user_add_action= unicode(self.create_user_textEdit.text() or "")
        model.user_delete_action= unicode(self.remove_user_textEdit.text() or "")
        model.user_enable_action= unicode(self.enable_user_textEdit.text() or "")
        model.user_disable_action= unicode(self.disable_user_textEdit.text() or "")
        model.user_disable_action= unicode(self.disable_user_textEdit.text() or "")
        model.vpn_speed_action = unicode(self.set_vpn_speed_textEdit.text() or "")
        model.ipn_speed_action = unicode(self.set_ipn_speed_lineEdit.text() or "")
        model.reset_action = unicode(self.pod_textEdit.text() or "")
        

        

        try:
            self.connection.save(model.save(table="nas_nas"))
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
            self.multilink_checkBox.setChecked(self.model.multilink)
        else:
            self.buttonBox.setDisabled(True)





class NasEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u"id", u"Имя", u"Тип", u"IP"]
        initargs = {"setname":"nas_frame_header", "objname":"NasEbsMDI", "winsize":(0,0,400,400), "wintitle":"Серверы доступа", "tablecolumns":columns}
        super(NasEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))      
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        
    def ebsPostInit(self, initargs):
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.addframe), ("editAction", "Настройки", "images/open.png", self.editframe), ("delAction", "Удалить", "images/del.png", self.delete), ("configureAction", "Конфигурировать", "images/configure.png", self.configure)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction", "configureAction"], self.toolBar:["addAction", "delAction", "configureAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(NasEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    
    def addframe(self):
        model=None
        addf = AddNasFrame(connection=self.connection, model=model)
        addf.exec_()
        self.refresh()

    def configure(self):
        id=self.getSelectedId()
        if id==0:
            return
        child = ConfigureDialog()
        if child.exec_()==1:
            pptp_enable = child.groupBox_pptp.isChecked() == True
            auth_types_pap=False
            auth_types_chap = False
            auth_types_mschap2 = False
            pptp_ip='0.0.0.0'
            if pptp_enable:
                auth_types_pap = child.checkBox_pptp_pap.checkState()==2
                auth_types_chap = child.checkBox_pptp_chap.checkState()==2
                auth_types_mschap2 = child.checkBox_pptp_mschap2.checkState()==2
                pptp_ip = unicode(child.lineEdit_pptp_ip.text())

            radius_enable = child.groupBox_radius.isChecked()
            radius_server_ip='0.0.0.0'
            interim_update='00:00:00'
            if radius_enable:
                radius_server_ip = unicode(child.lineEdit_radius_server_ip.text())
                interim_update = unicode(child.timeEdit_interim_update.text())
                
            configure_smtp = child.checkBox_smtp_spamers.checkState()==2
            configure_gateway = child.checkBox_configure_gateway.checkState()==2
            protect_malicious_trafic = child.checkBox_malicious_trafic.checkState()==2
            
            
            
            if self.connection.configureNAS(id,pptp_enable,auth_types_pap, auth_types_chap, auth_types_mschap2, pptp_ip, radius_enable, radius_server_ip,interim_update, configure_smtp, configure_gateway,protect_malicious_trafic):
                QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Настройка сервера доступа прошла удачно."))
            else:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка во время конфигурирования."))

    def delete(self):
        id=self.getSelectedId()
        if id>0:
            if self.connection.sql("""SELECT id FROM billservice_account WHERE (nas_id=%d)""" % id):
                print "accounts on NAS", self.connection.sql("""SELECT id FROM billservice_account WHERE (nas_id=%d)""" % id)
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Пожалуйста, отцепите сначала всех пользователей от сервера!")
                return
            elif (QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u'''Все связанные с сервером доступа аккаунты \n и вся статистика будут удалены. \nВы уверены, что хотите это сделать?''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
                try:
                    #self.connection.sql("UPDATE nas_nas SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete("nas_nas", id)
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")
        
    def editframe(self):
        try:
            model=self.connection.get("SELECT * FROM nas_nas WHERE id=%d" % self.getSelectedId())
        except:
            model=None

        addf = AddNasFrame(connection=self.connection, model=model)
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/nas.png"))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        #self.tableWidget.setSortingEnabled(False)
        nasses = self.connection.foselect("nas_nas")
        self.tableWidget.setRowCount(len(nasses))
        i=0
        for nas in nasses:
            self.addrow(nas.id, i,0)
            self.addrow(nas.name, i,1)
            self.addrow(nas.type, i,2)
            self.addrow(nas.ipaddress, i,3)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader("nas_frame_header", self.tableWidget)
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.setSortingEnabled(True)
    

    def delNodeLocalAction(self):
        super(NasEbs, self).delNodeLocalAction([self.delAction, self.configureAction])
        
class NasMdiChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        bhdr = HeaderUtil.getBinaryHeader("nas_frame_header")
        super(NasMdiChild, self).__init__()
        #global connection
        self.connection=connection
        self.setObjectName("NasMDI")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,400,400).size()).expandedTo(self.minimumSizeHint()))
        self.tableWidget = QtGui.QTableWidget(self)
        self.setCentralWidget(self.tableWidget)

        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))

        self.addAction = QtGui.QAction(self)
        self.addAction.setIcon(QtGui.QIcon("images/add.png"))

        self.delAction = QtGui.QAction(self)
        self.delAction.setIcon(QtGui.QIcon("images/del.png"))
        
        self.editAction = QtGui.QAction(self)
        self.editAction.setIcon(QtGui.QIcon("images/open.png"))

        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setMenuRole(QtGui.QAction.NoRole)
        
        self.editAction = QtGui.QAction(self)
        self.editAction.setIcon(QtGui.QIcon("images/open.png"))
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.addAction(self.editAction)
        self.tableWidget.addAction(self.addAction)
        self.tableWidget.addAction(self.delAction)
        self.tableWidget.addAction(self.configureAction)
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addAction(self.configureAction)
        

        #===============================================================================
        #        length_edit = QtGui.QComboBox()
        #        self.toolBar.addWidget(length_edit)
        #===============================================================================
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        HeaderUtil.nullifySaved("nas_frame_header")
        self.retranslateUi()
        self.refresh()
        self.tableWidget = tableFormat(self.tableWidget)
        if not bhdr.isEmpty():
                HeaderUtil.setBinaryHeader("nas_frame_header", bhdr)
                HeaderUtil.getHeader("nas_frame_header", self.tableWidget)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        self.connect(self.editAction, QtCore.SIGNAL("triggered()"), self.editframe)
        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        self.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Серверы доступа", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.clear()
        columns=[u"id", u"Имя", u"Тип", u"IP"]
        makeHeaders(columns, self.tableWidget)


        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        self.addAction.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        

        self.delAction.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.editAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))

        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "Конфигурировать", None, QtGui.QApplication.UnicodeUTF8))
        


    def addframe(self):
        model=None
        addf = AddNasFrame(connection=self.connection, model=model)
        addf.exec_()
        self.refresh()

    def configure(self):
        id=self.getSelectedId()
        if id==0:
            return
        child = ConfigureDialog()
        if child.exec_()==1:
            pptp_enable = child.groupBox_pptp.isChecked() == True
            auth_types_pap=False
            auth_types_chap = False
            auth_types_mschap2 = False
            pptp_ip='0.0.0.0'
            if pptp_enable:
                auth_types_pap = child.checkBox_pptp_pap.checkState()==2
                auth_types_chap = child.checkBox_pptp_chap.checkState()==2
                auth_types_mschap2 = child.checkBox_pptp_mschap2.checkState()==2
                pptp_ip = unicode(child.lineEdit_pptp_ip.text())

            radius_enable = child.groupBox_radius.isChecked()
            radius_server_ip='0.0.0.0'
            interim_update='00:00:00'
            if radius_enable:
                radius_server_ip = unicode(child.lineEdit_radius_server_ip.text())
                interim_update = unicode(child.timeEdit_interim_update.text())
                
            configure_smtp = child.checkBox_smtp_spamers.checkState()==2
            configure_gateway = child.checkBox_configure_gateway.checkState()==2
            protect_malicious_trafic = child.checkBox_malicious_trafic.checkState()==2
            
            
            
            if self.connection.configureNAS(id,pptp_enable,auth_types_pap, auth_types_chap, auth_types_mschap2, pptp_ip, radius_enable, radius_server_ip,interim_update, configure_smtp, configure_gateway,protect_malicious_trafic):
                QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Настройка сервера доступа прошла удачно."))
            else:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка во время конфигурирования."))



    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        id=self.getSelectedId()
        if id>0:
            if self.connection.sql("""SELECT id FROM billservice_account WHERE (nas_id=%d)""" % id):
                print self.connection.sql("""SELECT id FROM billservice_account WHERE (nas_id=%d)""" % id)
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Пожалуйста, отцепите сначала всех пользователей от сервера!")
                return
            elif (QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u'''Все связанные с сервером доступа аккаунты \n и вся статистика будут удалены. \nВы уверены, что хотите это сделать?''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
                try:
                    #self.connection.sql("UPDATE nas_nas SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete("nas_nas", id)
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")
        


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
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/nas.png"))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        self.tableWidget.setSortingEnabled(False)
        nasses = self.connection.foselect("nas_nas")
        self.tableWidget.setRowCount(len(nasses))
        i=0
        for nas in nasses:
            self.addrow(nas.id, i,0)
            self.addrow(nas.name, i,1)
            self.addrow(nas.type, i,2)
            self.addrow(nas.ipaddress, i,3)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
        #self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader("nas_frame_header", self.tableWidget)
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSortingEnabled(True)

    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("nas_frame_header", self.tableWidget)    
            
            
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.configureAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.configureAction.setDisabled(False)
            
            

