#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from db import Object as Object
from db import AttrDict
from helpers import makeHeaders
from helpers import HeaderUtil
from CustomForms import RrdReportMainWindow
from ebsWindow import ebsTableWindow
from CustomForms import RadiusAttrsDialog
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'mikrotik4',u'Mikrotik 4'),
                (u'mikrotik5',u'Mikrotik 5'),
                (u'cisco',u'cisco'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                (u'localhost',u'Выполнение команд локально'),
                (u'switch',u'Коммутатор(switch)'),
                )

SNMP_LIST = (
             ('', '---'),
             (u'v1', 'v1'),
             (u'v2c', 'v2c'),
             )
            
actions = {
'mikrotik2.9':{'user_add_action':'',
               'subacc_add_action':'/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
               'user_delete_action':'',
               'subacc_delete_action':'/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
               'user_enable_action':'',
               'subacc_enable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
               'user_disable_action': '',
               'subacc_disable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
               'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
               'ipn_speed_action': '',
               'subacc_ipn_speed_action':'/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
               'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
               'radius_speed': {'vendor1':14988, 'attrid1':8, 'value1':'$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx', 'vendor2':'', 'attrid2':'', 'value2':''},
               },
'mikrotik3':{'user_add_action':'',
               'subacc_add_action':'/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
               'user_delete_action':'',
               'subacc_delete_action':'/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
               'user_enable_action':'',
               'subacc_enable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
               'user_disable_action': '',
               'subacc_disable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
               'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
               'ipn_speed_action': '',
               'subacc_ipn_speed_action':'/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
               'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
               'radius_speed': {'vendor1':14988, 'attrid1':8, 'value1':'$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx', 'vendor2':'', 'attrid2':'', 'value2':''},
               },             
'mikrotik4':{'user_add_action':'',
               'subacc_add_action':'/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
               'user_delete_action':'',
               'subacc_delete_action':'/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
               'user_enable_action':'',
               'subacc_enable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
               'user_disable_action': '',
               'subacc_disable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
               'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
               'ipn_speed_action': '',
               'subacc_ipn_speed_action':'/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
               'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
               'radius_speed': {'vendor1':14988, 'attrid1':8, 'value1':'$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx', 'vendor2':'', 'attrid2':'', 'value2':''},
               },     
'mikrotik5':{'user_add_action':'',
               'subacc_add_action':'/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
               'user_delete_action':'',
               'subacc_delete_action':'/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
               'user_enable_action':'',
               'subacc_enable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
               'user_disable_action': '',
               'subacc_disable_action':'/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
               'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
               'ipn_speed_action': '',
               'subacc_ipn_speed_action':'/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
               'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
               'radius_speed': {'vendor1':14988, 'attrid1':8, 'value1':'$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx', 'vendor2':'', 'attrid2':'', 'value2':''},
               },                       
'common_ssh':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': ''
               },
'common_radius':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': ''
               },
'localhost':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': ''
               },               
'cisco':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': '',
               'radius_speed': {'vendor1':9, 'attrid1':1, 'value1':'lcp:interface-config#1=rate-limit input $max_limit_tx 8000 8000 conform-action transmit exceed-action drop', 'vendor2':9, 'attrid2':1, 'value2':'lcp:interface-config#1=rate-limit output $max_limit_tx 8000 8000 conform-action transmit exceed-action drop'},
               },
'switch':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': '',
               'radius_speed': { 'vendor1':'', 'attrid1':'', 'value1':'', 'vendor2':'', 'attrid2':'', 'value2':''},
               },               
'---':{'user_add_action':'',
              'subacc_add_action':'',
               'user_delete_action':'',
               'subacc_delete_action':'',
               'user_enable_action':'',
               'subacc_enable_action':'',
               'subacc_disable_action':'',
               'user_disable_action':'',
               'vpn_speed_action': '',
               'ipn_speed_action': '',
               'reset_action': '',
               'radius_speed': { 'vendor1':'', 'attrid1':'', 'value1':'', 'vendor2':'', 'attrid2':'', 'value2':''},
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
        #self.timeEdit_interim_update.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
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
        #self.connection.commit()
        self.setObjectName("AddNasFrame")
        self.resize(408, 520)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.maintabWidget = QtGui.QTabWidget(self)
        self.maintabWidget.setObjectName("maintabWidget")
        self.general_tab = QtGui.QWidget()
        self.general_tab.setObjectName("general_tab")
        self.gridLayout_4 = QtGui.QGridLayout(self.general_tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_name = QtGui.QLabel(self.general_tab)
        self.label_name.setObjectName("label_name")
        self.gridLayout_4.addWidget(self.label_name, 0, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.general_tab)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout_4.addWidget(self.lineEdit_name, 0, 1, 1, 1)
        self.identify_groupBox = QtGui.QGroupBox(self.general_tab)
        self.identify_groupBox.setObjectName("identify_groupBox")
        self.gridLayout_6 = QtGui.QGridLayout(self.identify_groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.type_label = QtGui.QLabel(self.identify_groupBox)
        self.type_label.setObjectName("type_label")
        self.gridLayout_6.addWidget(self.type_label, 0, 0, 1, 1)
        self.nas_comboBox = QtGui.QComboBox(self.identify_groupBox)
        self.nas_comboBox.setObjectName("nas_comboBox")

        self.gridLayout_6.addWidget(self.nas_comboBox, 0, 1, 1, 1)
        self.name_label = QtGui.QLabel(self.identify_groupBox)
        self.name_label.setObjectName("name_label")
        self.gridLayout_6.addWidget(self.name_label, 1, 0, 1, 1)
        self.nas_name = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_name.setObjectName("nas_name")
        self.gridLayout_6.addWidget(self.nas_name, 1, 1, 1, 1)
        self.ip_label = QtGui.QLabel(self.identify_groupBox)
        self.ip_label.setObjectName("ip_label")
        self.gridLayout_6.addWidget(self.ip_label, 2, 0, 1, 1)
        self.nas_ip = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_ip.setObjectName("nas_ip")
        self.gridLayout_6.addWidget(self.nas_ip, 2, 1, 1, 1)
        self.secret_label = QtGui.QLabel(self.identify_groupBox)
        self.secret_label.setObjectName("secret_label")
        self.gridLayout_6.addWidget(self.secret_label, 3, 0, 1, 1)
        self.nas_secret = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_secret.setObjectName("nas_secret")
        self.gridLayout_6.addWidget(self.nas_secret, 3, 1, 1, 1)

        self.label_interim = QtGui.QLabel(self.identify_groupBox)
        self.label_interim.setObjectName("label_interim")
        self.gridLayout_6.addWidget(self.label_interim, 4, 0, 1, 1)
        #self.nas_interim_update = QtGui.QLineEdit(self.identify_groupBox)
        self.nas_interim_update = QtGui.QSpinBox(self.identify_groupBox)
        self.nas_interim_update.setMaximum(999999)
        self.nas_interim_update.setObjectName("nas_interim_update")
        self.gridLayout_6.addWidget(self.nas_interim_update, 4, 1, 1, 1)
        self.snmp_label = QtGui.QLabel(self.identify_groupBox)
        self.snmp_label.setObjectName("snmp_label")
        self.gridLayout_6.addWidget(self.snmp_label, 5, 0, 1, 1)
        self.snmp_comboBox = QtGui.QComboBox(self.identify_groupBox)
        self.snmp_comboBox.setObjectName("snmp_comboBox")
        self.gridLayout_6.addWidget(self.snmp_comboBox, 5, 1, 1, 1)
        self.toolButton_default_actions = QtGui.QToolButton(self.identify_groupBox)
        self.toolButton_default_actions.setObjectName("toolButton_default_actions")
        self.gridLayout_6.addWidget(self.toolButton_default_actions, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.identify_groupBox, 1, 0, 1, 2)
        self.groupBox_radius_speed = QtGui.QGroupBox(self.general_tab)
        self.groupBox_radius_speed.setObjectName("groupBox_radius_speed")
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_radius_speed)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_vendor1 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_vendor1.setObjectName("label_vendor1")
        self.gridLayout_2.addWidget(self.label_vendor1, 0, 0, 1, 1)
        self.label_attr_id1 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_attr_id1.setObjectName("label_attr_id1")
        self.gridLayout_2.addWidget(self.label_attr_id1, 0, 1, 1, 1)
        self.lineEdit_vendor1 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_vendor1.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_vendor1.setObjectName("lineEdit_vendor1")
        self.gridLayout_2.addWidget(self.lineEdit_vendor1, 1, 0, 1, 1)
        self.lineEdit_attr_id1 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_attr_id1.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_attr_id1.setObjectName("lineEdit_attr_id1")
        self.gridLayout_2.addWidget(self.lineEdit_attr_id1, 1, 1, 1, 1)
        self.label_vendor2 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_vendor2.setObjectName("label_vendor2")
        self.gridLayout_2.addWidget(self.label_vendor2, 2, 0, 1, 1)
        self.label_attr_id2 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_attr_id2.setObjectName("label_attr_id2")
        self.gridLayout_2.addWidget(self.label_attr_id2, 2, 1, 1, 1)
        self.lineEdit_vendor2 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_vendor2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_vendor2.setObjectName("lineEdit_vendor2")
        self.gridLayout_2.addWidget(self.lineEdit_vendor2, 3, 0, 1, 1)
        self.lineEdit_attr_id2 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_attr_id2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_attr_id2.setObjectName("lineEdit_attr_id2")
        self.gridLayout_2.addWidget(self.lineEdit_attr_id2, 3, 1, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_value1 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_value1.setObjectName("label_value1")
        self.verticalLayout.addWidget(self.label_value1)
        self.lineEdit_value1 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_value1.setObjectName("lineEdit_value1")
        self.verticalLayout.addWidget(self.lineEdit_value1)
        self.label_value2 = QtGui.QLabel(self.groupBox_radius_speed)
        self.label_value2.setObjectName("label_value2")
        self.verticalLayout.addWidget(self.label_value2)
        self.lineEdit_value2 = QtGui.QLineEdit(self.groupBox_radius_speed)
        self.lineEdit_value2.setObjectName("lineEdit_value2")
        self.verticalLayout.addWidget(self.lineEdit_value2)
        self.gridLayout_7.addLayout(self.verticalLayout, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_radius_speed, 2, 0, 1, 2)
        self.ssh_groupBox = QtGui.QGroupBox(self.general_tab)
        self.ssh_groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.ssh_groupBox.setObjectName("ssh_groupBox")
        self.gridLayout_3 = QtGui.QGridLayout(self.ssh_groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.ssh_name_label = QtGui.QLabel(self.ssh_groupBox)
        self.ssh_name_label.setObjectName("ssh_name_label")
        self.gridLayout_3.addWidget(self.ssh_name_label, 0, 0, 1, 1)
        self.ssh_name_lineEdit = QtGui.QLineEdit(self.ssh_groupBox)
        self.ssh_name_lineEdit.setObjectName("ssh_name_lineEdit")
        self.gridLayout_3.addWidget(self.ssh_name_lineEdit, 0, 1, 1, 1)
        self.ssh_password_label = QtGui.QLabel(self.ssh_groupBox)
        self.ssh_password_label.setObjectName("ssh_password_label")
        self.gridLayout_3.addWidget(self.ssh_password_label, 1, 0, 1, 1)
        self.ssh_password_lineEdit = QtGui.QLineEdit(self.ssh_groupBox)
        self.ssh_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.ssh_password_lineEdit.setObjectName("ssh_password_lineEdit")
        self.gridLayout_3.addWidget(self.ssh_password_lineEdit, 1, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.ssh_groupBox)
        self.pushButton.setMaximumSize(QtCore.QSize(120, 16777215))
        self.pushButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 2, 1, 1, 1)
        self.gridLayout_4.addWidget(self.ssh_groupBox, 3, 0, 1, 2)
        self.maintabWidget.addTab(self.general_tab, "")
        self.commands_tab = QtGui.QWidget()
        self.commands_tab.setObjectName("commands_tab")
        self.gridLayout_5 = QtGui.QGridLayout(self.commands_tab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.tableWidget = QtGui.QTableWidget(self.commands_tab)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)

        self.gridLayout_5.addWidget(self.tableWidget, 0, 0, 2, 1)
        self.maintabWidget.addTab(self.commands_tab, "")
        self.gridLayout.addWidget(self.maintabWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.type_label.setBuddy(self.nas_comboBox)
        self.name_label.setBuddy(self.nas_name)
        self.ip_label.setBuddy(self.nas_ip)
        self.secret_label.setBuddy(self.nas_secret)
        self.ssh_name_label.setBuddy(self.ssh_name_lineEdit)
        self.ssh_password_label.setBuddy(self.ssh_password_lineEdit)

        self.maintabWidget.setCurrentIndex(0)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"), self.testNAS)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.editNasInfo)
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        QtCore.QObject.connect(self.toolButton_default_actions,QtCore.SIGNAL("clicked()"), self.refillActions)
        self.retranslateUi()
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки сервера доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.identify_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Сетевая идентификация", None, QtGui.QApplication.UnicodeUTF8))
        self.type_label.setText(QtGui.QApplication.translate("Dialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Сетевое имя", None, QtGui.QApplication.UnicodeUTF8))
        self.ip_label.setText(QtGui.QApplication.translate("Dialog", "IP", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_ip.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.snmp_label.setText(QtGui.QApplication.translate("Dialog", "SNMP", None, QtGui.QApplication.UnicodeUTF8))
        self.secret_label.setText(QtGui.QApplication.translate("Dialog", "Секретная фраза", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_default_actions.setWhatsThis(QtGui.QApplication.translate("Dialog", "Заполнить параметрами по-умолчанию", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_default_actions.setText(QtGui.QApplication.translate("Dialog", "Fill", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_speed.setTitle(QtGui.QApplication.translate("Dialog", "Установка скорости через RADIUS атрибуты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vendor1.setText(QtGui.QApplication.translate("Dialog", "Vendor", None, QtGui.QApplication.UnicodeUTF8))
        self.label_attr_id1.setText(QtGui.QApplication.translate("Dialog", "Attr ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vendor2.setText(QtGui.QApplication.translate("Dialog", "Vendor", None, QtGui.QApplication.UnicodeUTF8))
        self.label_attr_id2.setText(QtGui.QApplication.translate("Dialog", "Attr ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_value1.setText(QtGui.QApplication.translate("Dialog", "Значение", None, QtGui.QApplication.UnicodeUTF8))
        self.label_value2.setText(QtGui.QApplication.translate("Dialog", "Значение", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "SSH", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_name_label.setText(QtGui.QApplication.translate("Dialog", "Имя", None, QtGui.QApplication.UnicodeUTF8))
        self.ssh_password_label.setText(QtGui.QApplication.translate("Dialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.label_interim.setText(QtGui.QApplication.translate("Dialog", "Accounting interval", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.maintabWidget.setTabText(self.maintabWidget.indexOf(self.general_tab), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.maintabWidget.setTabText(self.maintabWidget.indexOf(self.commands_tab), QtGui.QApplication.translate("Dialog", "Команды", None, QtGui.QApplication.UnicodeUTF8))
        columns = [u"Действие",u"Значение"]
        makeHeaders(columns, self.tableWidget)
        self.tableInfo=[
            ['user_add_action', u'Добавить абонента',''],
            ['subacc_add_action', u'Добавить субаккаунт',''],
            ['user_delete_action', u'Удалить абонента',''],
            ['subacc_delete_action', u'Удалить субаккаунт',''],
            ['user_enable_action', u'Включить абонента',''],
            ['subacc_enable_action', u'Включить субаккаунт',''],
            ['user_disable_action',u'Отключить абонента',''],
            ['subacc_disable_action', u'Отключить субаккаунт',''],
            ['vpn_speed_action',u'Установить скорость для VPN',''],
            ['ipn_speed_action',u'Установить скорость для IPN аккаунта',''],
            ['subacc_ipn_speed_action',u'Установить скорость для IPN субаккаунта',''],
            ['reset_action',u'Сбросить сессию',''],
            ]
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.tableInfo))
        i=0
        for item in self.tableInfo:
            self.addrow(self.tableWidget, item[1], i, 0, id=item[0])
            if item[2]:
                self.addrow(self.tableWidget, '', i, 1, widget_type = item[2])
            i+=1

    def editNasInfo(self, item):
        if item.column()==1:
            self.tableWidget.editItem(item)
            
    def addrow(self, widget, value, x, y, id=None, editable=False, widget_type = None):
        headerItem = QtGui.QTableWidgetItem()
        if widget_type == 'checkbox':
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if value==None or value=="None":
            value=''
        if y==0:
            headerItem.id=value
        headerItem.setText(unicode(value))
        if id:
            headerItem.id=id
            
           
        widget.setItem(x,y,headerItem)
        
        
    def testNAS(self):
        d = self.connection.testCredentials(str(self.nas_ip.text()), str(self.ssh_name_lineEdit.text()), str(self.ssh_password_lineEdit.text()))
        if not d.status:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не верно указаны параметры для доступа, сервер доступа недоступен или неправильно настроен.\n %s" % d.message))
        else:
            QtGui.QMessageBox.information(self, u"Ok", unicode(u"Тестирование прошло успешно"))
         
    def refillActions(self):
        if (QtGui.QMessageBox.question(self, u"Внимание?" , u"Перезаписать действия сервера доступа на действия по умолчанию для этого типа серверов доступа?.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
            #self.maintabWidget.setCurrentIndex(1)
            nas_type = unicode(self.nas_comboBox.currentText())

            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, unicode(actions[nas_type].get(self.tableInfo[i][0],'')), i,1)
            
            self.tableWidget.resizeColumnsToContents()
            self.lineEdit_vendor1.setText(unicode(actions[nas_type].get('radius_speed').get('vendor1')))
            self.lineEdit_attr_id1.setText(unicode(actions[nas_type].get('radius_speed').get('attrid1')))
            self.lineEdit_value1.setText(unicode(actions[nas_type].get('radius_speed').get('value1')))

            self.lineEdit_vendor2.setText(unicode(actions[nas_type].get('radius_speed').get('vendor2')))
            self.lineEdit_attr_id2.setText(unicode(actions[nas_type].get('radius_speed').get('attrid2')))
            self.lineEdit_value2.setText(unicode(actions[nas_type].get('radius_speed').get('value2')))
                        
            #radius_speed
    
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
            model.id=self.model.id
        else:
            #print 'New nas'
            model=AttrDict()

        if unicode(self.nas_name.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан идентификатор сервера доступа"))
            return

        if unicode(self.ssh_name_lineEdit.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано имя пользователя для SSH"))
            return

        #if unicode(self.ssh_password_lineEdit.text())==u"":
        #    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан пароль для SSH"))
        #    return

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
        model.name = unicode(self.lineEdit_name.text())
        model.identify = unicode(self.nas_name.text())
        model.ipaddress = unicode(self.nas_ip.text())
        model.secret = unicode(self.nas_secret.text())
        model.acct_interim_interval = int(self.nas_interim_update.value())
        model.snmp_version = unicode(self.snmp_comboBox.itemData(self.snmp_comboBox.currentIndex()).toString())

        
        for i in xrange(self.tableWidget.rowCount()):
            if self.tableWidget.item(i,1):
                setattr(model, self.tableInfo[i][0], unicode(self.tableWidget.item(i,1).text()))
            
        try:
            model.speed_vendor_1 = int(unicode(self.lineEdit_vendor1.text() or 0))
            model.speed_vendor_2 = int(unicode(self.lineEdit_vendor2.text() or 0))
            model.speed_attr_id1 = int(unicode(self.lineEdit_attr_id1.text() or 0))
            model.speed_attr_id2 = int(unicode(self.lineEdit_attr_id2.text() or 0))
            model.speed_value1 = unicode(self.lineEdit_value1.text())
            model.speed_value2 = unicode(self.lineEdit_value2.text())
            
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Параметры Vendor и Attr Id должны быть целыми положительными числами."))
            return
        

        #print model

        try:
            
            d = self.connection.nas_save(model)
            if d.status==False:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode('\n'.join(["%s %s" % (x, ';'.join(d.message.get(x))) for x in d.message])))
            #self.connection.commit()
        except Exception, e:
            print e
            return

        QtGui.QDialog.accept(self)

    def fixtures(self):


        nasses = NAS_LIST
        self.nas_comboBox.addItem('---')
        for nas, value in nasses:
            self.nas_comboBox.addItem(nas)

        snmps = SNMP_LIST
        i=0
        for snmp in snmps:
            self.snmp_comboBox.addItem(snmp[1])
            self.snmp_comboBox.setItemData(i, QtCore.QVariant(snmp[0]))
            if self.model and self.model.snmp_version==snmp[0]:
                self.snmp_comboBox.setCurrentIndex(i)
            i+=1

        print self.model
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            self.nas_name.setText(unicode(self.model.identify))
            self.nas_ip.setText(unicode(self.model.ipaddress))
            self.nas_secret.setText(unicode(self.model.secret))
            self.ssh_name_lineEdit.setText(unicode(self.model.login))
            self.ssh_password_lineEdit.setText(unicode(self.model.password))
            
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, unicode(getattr(self.model,self.tableInfo[i][0],'')), i,1)
            
            self.tableWidget.resizeColumnsToContents()
            self.nas_comboBox.setCurrentIndex(self.nas_comboBox.findText(self.model.type, QtCore.Qt.MatchCaseSensitive))

            self.lineEdit_vendor1.setText(unicode(self.model.speed_vendor_1 or ''))
            self.lineEdit_vendor2.setText(unicode(self.model.speed_vendor_2 or ''))
            self.lineEdit_attr_id1.setText(unicode(self.model.speed_attr_id1 or ''))
            self.lineEdit_attr_id2.setText(unicode(self.model.speed_attr_id2 or ''))
            self.lineEdit_value1.setText(unicode(self.model.speed_value1))
            self.lineEdit_value2.setText(unicode(self.model.speed_value2))
            
            self.nas_interim_update.setValue(self.model.acct_interim_interval)
        else:
            self.lineEdit_vendor1.setText('')
            self.lineEdit_vendor2.setText('')
            self.lineEdit_attr_id1.setText('')
            self.lineEdit_attr_id2.setText('')
            self.lineEdit_value1.setText('')
            self.lineEdit_value2.setText('')    
            self.nas_interim_update.setValue(60)
            
        #else:
        #    self.buttonBox.setDisabled(True)





class NasEbs(ebsTableWindow):
    def __init__(self, connection, parent):
        columns=[u"id", u"Имя", u"Identify", u"Тип", u"IP"]
        initargs = {"setname":"nas_frame_header", "objname":"NasEbsMDI", "winsize":(0,0,400,400), "wintitle":"Серверы доступа", "tablecolumns":columns}
        self.parent=parent
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

        actList=[("addAction", "Добавить", "images/add.png", self.addframe), ("editAction", "Настройки", "images/open.png", self.editframe), ("delAction", "Удалить", "images/del.png", self.delete), ("actionRadiusAttrs", "RADIUS атрибуты", "images/configure.png", self.radius_attrs), ("rrdNasTrafficInfo", "График загрузки сервера доступа", "images/bandwidth.png", self.rrdtraffic_info),]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction", 'rrdReportAction'], self.toolBar:["addAction", "delAction", "actionRadiusAttrs","rrdNasTrafficInfo"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        self.tableWidget = tableFormat(self.tableWidget)
        
    def retranslateUI(self, initargs):
        super(NasEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        
    def radius_attrs(self):
        id=self.getSelectedId()
        if id>0:
            child = RadiusAttrsDialog(nas_id = id, connection = self.connection)
            child.exec_()
            
    def rrdtraffic_info(self):
        id = self.getSelectedId()
        if id:
            window = RrdReportMainWindow(item_id=id, type='nas', connection=self.connection)
            self.parent.workspace.addWindow(window)
            window.show()
            
    def addframe(self):
        model=None
        addf = AddNasFrame(connection=self.connection, model=model)
        if addf.exec_()==1:
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
                QtGui.QMessageBox.information(self, u"Ok", unicode(u"Настройка сервера доступа прошла удачно."))
            else:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка во время конфигурирования."))

    def delete(self):
        id=self.getSelectedId()
        if id>0:
            if QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u'''Это не безопасная операция. Проверьте не привязаны ли к этому серверу доступа аккаунты.\nВы уверены, что хотите это сделать?''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                
                    #self.connection.sql("UPDATE nas_nas SET deleted=TRUE WHERE id=%d" % id, False)
                self.connection.nas_delete(id)
                self.refresh()
  
    def editframe(self):
        try:
            model=self.connection.get_nasses(id=self.getSelectedId())
            if not model: return
            model = model.records[0]
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
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.clearContents()
        nasses = self.connection.get_nasses(fields=['id','name', 'identify','type','ipaddress'])
        #self.connection.commit()
        self.tableWidget.setRowCount(nasses.totalCount)
        #print nasses
        i=0
        for nas in nasses.records:
            #print nas
            self.addrow(nas.id, i,0)
            self.addrow(nas.name, i,1)
            self.addrow(nas.identify, i,2)
            self.addrow(nas.type, i,3)
            self.addrow(nas.ipaddress, i,4)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.statusBar().showMessage(u"Готово")
    

    def delNodeLocalAction(self):
        super(NasEbs, self).delNodeLocalAction([self.delAction, self.rrdNasTrafficInfo])
        
