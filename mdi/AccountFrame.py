#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui

import traceback
import psycopg2
from ebsWindow import ebsTable_n_TreeWindow
from db import Object as Object
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil, SplitterUtil, transip
from types import BooleanType
import copy

from randgen import nameGen, GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import RadiusAttrsDialog, CheckBoxDialog, ComboBoxDialog, SpeedEditDialog , TransactionForm
import time
from Reports import TransactionsReportEbs as TransactionsReport, SimpleReportEbs

from helpers import tableFormat, check_speed
from helpers import transaction, makeHeaders
from helpers import Worker
from CustomForms import simpleTableImageWidget, tableImageWidget, IPAddressSelectForm, TemplateSelect, RrdReportMainWindow, ReportMainWindow
from CustomForms import CustomWidget, CardPreviewDialog, SuspendedPeriodForm, GroupsDialog, SpeedLimitDialog, InfoDialog, PSCreatedForm, AccountAddonServiceEdit
from MessagesFrame import MessageDialog
from AccountEditFrame import AccountWindow, AddAccountTarif
from mako.template import Template
from AccountFilter import AccountFilterDialog

strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
qtTimeFormat = "YYYY-MM-DD HH:MM:SS"
import IPy

class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

limit_actions = [CashType(0, u"Заблокировать пользователя"), CashType(1,u"Изменить скорость")]

la_list = [u"Заблокировать пользователя", u"Изменить скорость"]

ps_conditions = [CashType(0, u"При любом балансе"), CashType(1,u"При положительном и нулевом балансе"), CashType(2,u"При отрицательном балансе"), CashType(3,u"При положительнои балансе")]
ps_list = [u"При любом балансе", u"При положительном и нулевом балансе", u"При отрицательном балансе", u"При положительнои балансе"]
round_types = [CashType(0, u"Не округлять"),CashType(1, u"В большую сторону")]
direction_types = [CashType(0, u"Входящий"),CashType(1, u"Исходящий"),CashType(2, u"Вх.+Исх."),CashType(3, u"Большее направление")]
class SubaccountLinkDialog(QtGui.QDialog):
    def __init__(self, connection, account, model = None):
        super(SubaccountLinkDialog, self).__init__()
        #self.setObjectName("SubaccountLinkDialog")
        self.connection = connection
        self.account = account
        self.model = model
        self.resize(690, 729)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtGui.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_link_parameters = QtGui.QGroupBox(self.tab)
        self.groupBox_link_parameters.setObjectName("groupBox_link_parameters")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_link_parameters)
        self.gridLayout.setObjectName("gridLayout")
        self.label_nas = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout.addWidget(self.label_nas, 0, 1, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout.addWidget(self.comboBox_nas, 0, 2, 1, 1)
        self.label_link_login = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_login.setObjectName("label_link_login")
        self.gridLayout.addWidget(self.label_link_login, 1, 1, 1, 1)
        self.lineEdit_link_login = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_login.setObjectName("lineEdit_link_login")
        self.gridLayout.addWidget(self.lineEdit_link_login, 1, 2, 1, 3)
        self.label_link_password = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_password.setObjectName("label_link_password")
        self.gridLayout.addWidget(self.label_link_password, 3, 1, 1, 1)
        self.lineEdit_link_password = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_password.setObjectName("lineEdit_link_password")
        self.gridLayout.addWidget(self.lineEdit_link_password, 3, 2, 1, 3)
        self.label_link_vpn_ip_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn_ip_address.setObjectName("label_link_vpn_ip_address")
        self.gridLayout.addWidget(self.label_link_vpn_ip_address, 5, 1, 1, 1)
        self.lineEdit_vpn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_ip_address.setObjectName("lineEdit_vpn_ip_address")
        self.gridLayout.addWidget(self.lineEdit_vpn_ip_address, 5, 2, 1, 1)
        self.comboBox_vpn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_vpn_pool.setObjectName("comboBox_vpn_pool")
        self.gridLayout.addWidget(self.comboBox_vpn_pool, 5, 3, 1, 2)
        self.label_link_vpn = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn.setObjectName("label_link_vpn")
        self.gridLayout.addWidget(self.label_link_vpn, 7, 1, 1, 1)
        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_ip_address.setObjectName("lineEdit_ipn_ip_address")
        self.gridLayout.addWidget(self.lineEdit_ipn_ip_address, 7, 2, 1, 1)
        self.comboBox_ipn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_ipn_pool.setObjectName("comboBox_ipn_pool")
        self.gridLayout.addWidget(self.comboBox_ipn_pool, 7, 3, 1, 2)
        self.label_link_ipn_mac_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_ipn_mac_address.setObjectName("label_link_ipn_mac_address")
        self.gridLayout.addWidget(self.label_link_ipn_mac_address, 8, 1, 1, 1)
        self.lineEdit_link_ipn_mac_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_ipn_mac_address.setObjectName("lineEdit_link_ipn_mac_address")
        self.gridLayout.addWidget(self.lineEdit_link_ipn_mac_address, 8, 2, 1, 4)
        self.label_link_switch = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_switch.setObjectName("label_link_switch")
        self.gridLayout.addWidget(self.label_link_switch, 9, 1, 1, 1)
        self.comboBox_link_switch_id = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_link_switch_id.setObjectName("comboBox_link_switch_id")
        self.gridLayout.addWidget(self.comboBox_link_switch_id, 9, 2, 1, 4)
        self.label_link_port = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_port.setObjectName("label_link_port")
        self.gridLayout.addWidget(self.label_link_port, 10, 1, 1, 1)
        self.spinBox_link_port = QtGui.QSpinBox(self.groupBox_link_parameters)
        self.spinBox_link_port.setMaximum(512)
        self.spinBox_link_port.setObjectName("spinBox_link_port")
        self.gridLayout.addWidget(self.spinBox_link_port, 10, 2, 1, 4)
        self.label_vpn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_vpn_speed.setObjectName("label_vpn_speed")
        self.gridLayout.addWidget(self.label_vpn_speed, 21, 1, 1, 1)
        self.lineEdit_vpn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_speed.setObjectName("lineEdit_vpn_speed")
        self.gridLayout.addWidget(self.lineEdit_vpn_speed, 21, 2, 1, 5)
        self.label_ipn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_ipn_speed.setObjectName("label_ipn_speed")
        self.gridLayout.addWidget(self.label_ipn_speed, 22, 1, 1, 1)
        self.lineEdit_ipn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_speed.setObjectName("lineEdit_ipn_speed")
        self.gridLayout.addWidget(self.lineEdit_ipn_speed, 22, 2, 1, 5)
        self.checkBox_allow_addonservice = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_addonservice.setObjectName("checkBox_allow_addonservice")
        self.gridLayout.addWidget(self.checkBox_allow_addonservice, 20, 1, 1, 6)
        self.checkBox_associate_pppoe_ipn_mac = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_associate_pppoe_ipn_mac.setObjectName("checkBox_associate_pppoe_ipn_mac")
        self.gridLayout.addWidget(self.checkBox_associate_pppoe_ipn_mac, 19, 1, 1, 5)
        self.checkBox_associate_pptp_ipn_ip = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_associate_pptp_ipn_ip.setObjectName("checkBox_associate_pptp_ipn_ip")
        self.gridLayout.addWidget(self.checkBox_associate_pptp_ipn_ip, 18, 1, 1, 5)
        self.checkBox_allow_vpn_with_null = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_null.setObjectName("checkBox_allow_vpn_with_null")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_null, 15, 1, 1, 5)
        self.checkBox_allow_vpn_with_block = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_block.setObjectName("checkBox_allow_vpn_with_block")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_block, 17, 1, 1, 5)
        self.checkBox_allow_vpn_with_minus = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_minus.setObjectName("checkBox_allow_vpn_with_minus")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_minus, 16, 1, 1, 5)
        self.checkBox_allow_dhcp_with_block = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_block.setObjectName("checkBox_allow_dhcp_with_block")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_block, 14, 1, 1, 5)
        self.checkBox_allow_dhcp_with_minus = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_minus.setObjectName("checkBox_allow_dhcp_with_minus")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_minus, 13, 1, 1, 5)
        self.checkBox_allow_dhcp_with_null = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_null.setObjectName("checkBox_allow_dhcp_with_null")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_null, 12, 1, 1, 5)
        self.groupBox = QtGui.QGroupBox(self.groupBox_link_parameters)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toolButton_ipn_added = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_added.setCheckable(True)
        self.toolButton_ipn_added.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton_ipn_added.setObjectName("toolButton_ipn_added")
        self.horizontalLayout.addWidget(self.toolButton_ipn_added)
        self.toolButton_ipn_enabled = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_enabled.setCheckable(True)
        self.toolButton_ipn_enabled.setObjectName("toolButton_ipn_enabled")
        self.horizontalLayout.addWidget(self.toolButton_ipn_enabled)
        self.toolButton_ipn_sleep = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_sleep.setCheckable(True)
        self.toolButton_ipn_sleep.setObjectName("toolButton_ipn_sleep")
        self.horizontalLayout.addWidget(self.toolButton_ipn_sleep)
        self.gridLayout.addWidget(self.groupBox, 0, 3, 1, 3)
        self.toolButton_assign_ipn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_ipn_from_pool.setObjectName("toolButton_assign_ipn_from_pool")
        self.gridLayout.addWidget(self.toolButton_assign_ipn_from_pool, 7, 5, 1, 1)
        self.toolButton_assign_vpn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_vpn_from_pool.setObjectName("toolButton_assign_vpn_from_pool")
        self.gridLayout.addWidget(self.toolButton_assign_vpn_from_pool, 5, 5, 1, 1)
        self.toolButton_password = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_password.setObjectName("toolButton_password")
        self.gridLayout.addWidget(self.toolButton_password, 3, 5, 1, 1)
        self.toolButton_login = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_login.setObjectName("toolButton_login")
        self.gridLayout.addWidget(self.toolButton_login, 1, 5, 1, 1)
        self.checkBox_allow_dhcp = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp.setObjectName("checkBox_allow_dhcp")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp, 11, 1, 1, 5)
        self.gridLayout_3.addWidget(self.groupBox_link_parameters, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frame = QtGui.QFrame(self.tab_2)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_4 = QtGui.QGridLayout(self.frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.commandLinkButton = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.gridLayout_4.addWidget(self.commandLinkButton, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame, 1, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.tab_2)
        self.tableWidget.setObjectName("tableWidget")
        self.gridLayout_5.addWidget(self.tableWidget, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.fixtures()
        self.accountAddonServiceRefresh()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)
        
        self.connect(self.toolButton_assign_ipn_from_pool,QtCore.SIGNAL("clicked()"),self.get_ipn_from_pool)
        self.connect(self.toolButton_assign_vpn_from_pool,QtCore.SIGNAL("clicked()"),self.get_vpn_from_pool)
        
        self.connect(self.toolButton_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_password,QtCore.SIGNAL("clicked()"),self.generate_password)

        self.connect(self.toolButton_ipn_added,QtCore.SIGNAL("clicked()"),self.subaccountAddDel)
        self.connect(self.toolButton_ipn_enabled,QtCore.SIGNAL("clicked()"),self.subaccountEnableDisable)
        
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.addAddonService)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        
        self.connect(self.comboBox_vpn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_vpn_pool_action)
        self.connect(self.comboBox_ipn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_ipn_pool_action)



    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры субаккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_link_parameters.setTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры связки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("SubAccountDialog", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_login.setText(QtGui.QApplication.translate("SubAccountDialog", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_password.setText(QtGui.QApplication.translate("SubAccountDialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn_ip_address.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_ipn_mac_address.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_switch.setText(QtGui.QApplication.translate("SubAccountDialog", "Коммутатор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_port.setText(QtGui.QApplication.translate("SubAccountDialog", "Порт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN скорось", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_addonservice.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить активацию подключаемых услуг через веб-кабинет", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pppoe_ipn_mac.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPPOE авторизацию к IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pptp_ipn_ip.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPTP авторизацию к IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SubAccountDialog", "IPN статусы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Состояние записей в Address-листах на указанном сервере доступа. Только для IPN способов доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_added.setText(QtGui.QApplication.translate("SubAccountDialog", "Добавлен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_enabled.setText(QtGui.QApplication.translate("SubAccountDialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_sleep.setText(QtGui.QApplication.translate("SubAccountDialog", "Не управлять", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_ipn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_ipn_from_pool.setToolTip(QtGui.QApplication.translate("MainWindow", "Выбрать IP-адрес из указанного IPN-пула", None, QtGui.QApplication.UnicodeUTF8))        
        self.toolButton_assign_vpn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_vpn_from_pool.setToolTip(QtGui.QApplication.translate("MainWindow", "Выбрать IP-адрес из указанного VPN-пула", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_password.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_password.setToolTip(QtGui.QApplication.translate("SubAccountDialog", "Сгенерировать пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_login.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_login.setToolTip(QtGui.QApplication.translate("SubAccountDialog", "Сгенерировать логин", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить выдачу адресов по DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("SubAccountDialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setText(QtGui.QApplication.translate("SubAccountDialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("SubAccountDialog", "Добавить подключаемую услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("SubAccountDialog", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_vpn_speed.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_vpn_speed.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ipn_speed.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ipn_speed.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        columns=[u'#', u'Название', u'Начата', u'Закрыта', u'Активирована на сервере доступа', u"Временная блокировка"]
        self.tableWidget = tableFormat(self.tableWidget)
        makeHeaders(columns, self.tableWidget)
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        
        self.ipnRx = QtCore.QRegExp(r"\b(?:0\.0\.0\.0(/0)?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.0\.0\.0(?:/[1-8])?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){2}0\.0(?:/(?:9|1[0-6]))?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}0(?:/(?:1[7-9]|2[0-4]))?)|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:2[5-9]|3[0-2]))?)\b")
        self.ipnValidator = QtGui.QRegExpValidator(self.ipnRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)  

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
        
          
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).text())
        except:
            return -1
              
    def subaccountEnableDisable(self):
        if not self.model: return
        state = True if self.toolButton_ipn_enabled.isChecked() else False
        if state:
            if not self.connection.accountActions(None, self.model.id, 'enable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        else:
             if not self.connection.accountActions(None, self.model.id, 'disable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        #self.refresh()
        

    def subaccountAddDel(self):
        if not self.model: return
        state = True if self.toolButton_ipn_added.isChecked() else False
        if state==True:
            if not self.connection.accountActions(None, self.model.id,  'create'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        else:
            if not self.connection.accountActions(None, self.model.id,  'delete'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))            


    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        child = AccountAddonServiceEdit(connection=self.connection, subaccount_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        try:
            model = self.connection.get_model(i, "billservice_accountaddonservice")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountAddonServiceEdit(connection=self.connection, model=model, subaccount_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()


    def combobox_ipn_pool_action(self):
		#print self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
		if self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]:
			self.lineEdit_ipn_ip_address.setDisabled(True)
			self.lineEdit_ipn_ip_address.setText(u"0.0.0.0")
		else:
			self.lineEdit_ipn_ip_address.setDisabled(False)

    def combobox_vpn_pool_action(self):
		#print self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
		if self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]:
			self.lineEdit_vpn_ip_address.setDisabled(True)
			self.lineEdit_vpn_ip_address.setText(u"0.0.0.0")
		else:
			self.lineEdit_vpn_ip_address.setDisabled(False)

    def accountAddonServiceRefresh(self):
        if self.model:
            sp = self.connection.sql("""
            SELECT accadd.*, adds.name as addonservice_name, adds.id as addonservice_id FROM billservice_accountaddonservice as accadd
            JOIN billservice_addonservice as adds ON adds.id=accadd.service_id
            WHERE subaccount_id=%s ORDER BY id DESC
            """ % self.model.id)
            self.connection.commit()
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget, a.id, i, 0)
                self.addrow(self.tableWidget, a.addonservice_name, i, 1)
                self.addrow(self.tableWidget, a.activated.strftime(strftimeFormat), i, 2)
                try:
                    self.addrow(self.tableWidget, a.deactivated.strftime(strftimeFormat), i, 3)
                except:
                    self.addrow(self.tableWidget, u"Не закончен", i, 3)
                self.addrow(self.tableWidget, a.action_status, i, 4)
                try:
                    self.addrow(self.tableWidget, a.temporary_blocked.strftime(strftimeFormat), i, 5)
                except:
                    self.addrow(self.tableWidget, u"Нет", i, 5)
                i+=1
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.resizeColumnsToContents()
                    
    def fixtures(self):
        nasses=self.connection.sql("SELECT id, name FROM nas_nas ORDER BY name;")
        self.connection.commit()
        self.comboBox_nas.addItem(u"---Любой---", QtCore.QVariant(0))
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name, QtCore.QVariant(nas.id))

        self.comboBox_link_switch_id.addItem(u"---Не указан---", QtCore.QVariant(0))
        for nas in nasses:
            self.comboBox_link_switch_id.addItem(nas.name, QtCore.QVariant(nas.id))
            
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            if self.model.isnull('vpn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.vpn_ipinuse_id, return_response=True)[0]
                #print "vpnipinuse pool_id", pool_id
            
        pools = self.connection.get_models("billservice_ippool", where={'type':'0',})
        
        self.connection.commit()
        i=1
        self.comboBox_vpn_pool.clear()
        self.comboBox_vpn_pool.addItem('---')
        self.comboBox_vpn_pool.setItemData(0, QtCore.QVariant(0))
        for pool in pools:
            self.comboBox_vpn_pool.addItem(pool.name)
            self.comboBox_vpn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.isnull('vpn_ipinuse_id')==False:
                    if pool.id==pool_id.pool_id:
                        self.comboBox_vpn_pool.setCurrentIndex(i)
                        self.lineEdit_vpn_ip_address.setDisabled(True)
            
            i+=1

        if not self.model: self.groupBox.setDisabled(True)
        if self.model:
            if self.model.isnull('ipn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.ipn_ipinuse_id, return_response=True)[0]
            
        pools = self.connection.get_models("billservice_ippool", where={'type':'1',})
        self.connection.commit()
        i=1
        self.comboBox_ipn_pool.clear()
        self.comboBox_ipn_pool.addItem('---')
        self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(0))
        for pool in pools:
            self.comboBox_ipn_pool.addItem(pool.name)
            self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.isnull('ipn_ipinuse_id')==False:
                    if pool.id==pool_id.pool_id:
                        self.comboBox_ipn_pool.setCurrentIndex(i)
                        self.lineEdit_ipn_ip_address.setDisabled(True)
            i+=1

            
        if self.model:
            #print "NAS_ID", self.model.nas_id
            if self.model.nas_id:
                self.comboBox_nas.setCurrentIndex(self.comboBox_nas.findData(self.model.nas_id))
            if self.model.switch_id:
                self.comboBox_link_switch_id.setCurrentIndex(self.comboBox_link_switch_id.findData(self.model.switch_id))                
            self.lineEdit_link_login.setText(unicode(self.model.username))
            self.lineEdit_link_password.setText(unicode(self.model.password))
            self.lineEdit_vpn_ip_address.setText(unicode(self.model.vpn_ip_address))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
            self.lineEdit_link_ipn_mac_address.setText(unicode(self.model.ipn_mac_address))
            self.spinBox_link_port.setValue(self.model.switch_port if self.model.switch_port else 0)
            self.checkBox_allow_dhcp.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_block==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_block==True else QtCore.Qt.Unchecked )
            self.checkBox_associate_pppoe_ipn_mac.setCheckState(QtCore.Qt.Checked if self.model.associate_pppoe_ipn_mac==True else QtCore.Qt.Unchecked )
            self.checkBox_associate_pptp_ipn_ip.setCheckState(QtCore.Qt.Checked if self.model.associate_pptp_ipn_ip==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_addonservice.setCheckState(QtCore.Qt.Checked if self.model.allow_addonservice==True else QtCore.Qt.Unchecked )
            self.lineEdit_vpn_speed.setText(unicode(self.model.vpn_speed))
            self.lineEdit_ipn_speed.setText(unicode(self.model.ipn_speed))
            self.toolButton_ipn_sleep.setChecked(self.model.ipn_sleep)
            self.toolButton_ipn_added.setChecked(self.model.ipn_added)
            self.toolButton_ipn_enabled.setChecked(self.model.ipn_enabled)
            
            
            #self.combobox_vpn_pool_action()
            #self.combobox_ipn_pool_action()
                        
    def accept(self):
        if self.model:
            model=self.model
        else:
            model = Object()
            model.account_id = self.account.id
        if self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]!=0:
            model.nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
        else:
            model.nas_id = None
        
        if self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0]!=0:
            model.switch_id = self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0]
        else:
            model.switch_id = None
        
        model.switch_port = int(self.spinBox_link_port.value() or 0)
        model.username = unicode(self.lineEdit_link_login.text()) or ""
        model.password = unicode(self.lineEdit_link_password.text()) or ""
        #model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"
        #model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"
        #------------------
        if self.lineEdit_ipn_ip_address.text():
			if self.ipnValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания IPN IP адреса."))
				self.connection.rollback()
				return
			try:
				ipn_address_account_id = self.connection.get("SELECT id FROM billservice_subaccount WHERE ipn_ip_address='%s'" % unicode(self.lineEdit_ipn_ip_address.text())).id
				if ipn_address_account_id!=model.id and unicode(self.lineEdit_ipn_ip_address.text())!='0.0.0.0':
					QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе уже существует такой IPN IP адрес."))
					#self.connection.rollback()
					#return  			  
			except Exception, ex:
				pass
        model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"
		
				
        if self.lineEdit_vpn_ip_address.text():
			if self.ipValidator.validate(self.lineEdit_vpn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания VPN IP адреса."))
				self.connection.rollback()
				return
			try:
				vpn_address_account_id = self.connection.get("SELECT id FROM billservice_subaccount WHERE vpn_ip_address='%s'" % unicode(self.lineEdit_vpn_ip_address.text())).id
				#print "vpn_address_account_id", vpn_address_account_id
				if vpn_address_account_id!=model.id and unicode(self.lineEdit_vpn_ip_address.text())!='0.0.0.0':
					QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе уже существует такой VPN IP адрес."))	  
			except Exception, ex:
				pass
			
        model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"

        #---------------
        if self.lineEdit_link_ipn_mac_address.text().isEmpty()==False:
			if self.macValidator.validate(self.lineEdit_link_ipn_mac_address.text(), 0)[0]  == QtGui.QValidator.Acceptable:
				try:
					id = self.connection.get("SELECT id FROM billservice_account WHERE ipn_mac_address='%s'" % unicode(self.lineEdit_ipn_mac_address.text()).upper()).id
					if id!=model.id :
						QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
						#self.connection.rollback()
						return
				except:
					pass
				model.ipn_mac_address = unicode(self.lineEdit_link_ipn_mac_address.text()).upper()
			else:
				QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Указан некорректный MAC адрес."))
				self.connection.rollback()
				return
        else:
			model.ipn_mac_address=u""
                
        #model.ipn_mac_address = unicode(self.lineEdit_link_ipn_mac_address.text()) or ""
            
        model.allow_dhcp = self.checkBox_allow_dhcp.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_null = self.checkBox_allow_dhcp_with_null.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_minus = self.checkBox_allow_dhcp_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_block = self.checkBox_allow_dhcp_with_block.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_null = self.checkBox_allow_vpn_with_null.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_minus = self.checkBox_allow_vpn_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_block = self.checkBox_allow_vpn_with_block.checkState()==QtCore.Qt.Checked
        model.associate_pppoe_ipn_mac = self.checkBox_associate_pppoe_ipn_mac.checkState()==QtCore.Qt.Checked
        model.associate_pptp_ipn_ip = self.checkBox_associate_pptp_ipn_ip.checkState()==QtCore.Qt.Checked
        model.allow_addonservice = self.checkBox_allow_addonservice.checkState()==QtCore.Qt.Checked
        model.vpn_speed=unicode(self.lineEdit_vpn_speed.text()) or ""
        model.ipn_speed=unicode(self.lineEdit_ipn_speed.text()) or ""
        model.ipn_sleep = self.toolButton_ipn_sleep.isChecked()
        model.ipn_added = self.toolButton_ipn_added.isChecked()
        model.ipn_enabled = self.toolButton_ipn_enabled.isChecked()
        
        if self.model:
            if model.ipn_ip_address!=self.model.ipn_ip_address:
    			"""
    			Если изменили IPN IP адрес-значит нужно добавить новый адрес в лист доступа
    			"""
    			model.ipn_added=False        
    			model.ipn_enabled=False        
        model.speed=''
		 #Операции с пулом    
        try:
			pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
			if pool_id!=0 and model.ipn_ip_address==u'0.0.0.0':
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали IPN пул, но не назначили ip адрес."))
				self.connection.rollback()
				return 
			if  model.__dict__.get('ipn_ipinuse_id'):
				ipninuse_model = self.connection.get_model(model.ipn_ipinuse_id, "billservice_ipinuse")
				
				if ipninuse_model.id!=pool_id or ipninuse_model.ip!=model.ipn_ip_address:
					self.connection.iddelete(ipninuse_model.id, "billservice_ipinuse")
					model.ipn_ipinuse_id=None
					
			
			if pool_id!=0:
				ipninuse_model= Object()
				ipninuse_model.pool_id=pool_id
				ipninuse_model.ip=model.ipn_ip_address
				ipninuse_model.datetime='now()'
				ipninuse_model.id = self.connection.save(ipninuse_model, "billservice_ipinuse")
				model.ipn_ipinuse_id=ipninuse_model.id
				#self.connection.save(model, "billservice_account")
        except Exception, e:
			print e
			QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте настройки IPN IP адресов. Возможно выбранный IP адрес не принадлежит пулу."))
			self.connection.rollback()
			return 

		 #Операции с пулом    
        try:
			pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
			if pool_id!=0 and model.vpn_ip_address==u'0.0.0.0':
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали VPN пул, но не назначили ip адрес."))
				self.connection.rollback()
				return 			
			if  model.__dict__.get('vpn_ipinuse_id'):
				ipninuse_model = self.connection.get_model(model.vpn_ipinuse_id, "billservice_ipinuse")
				
				if ipninuse_model.id!=pool_id or ipninuse_model.ip!=model.vpn_ip_address:
					self.connection.iddelete(ipninuse_model.id, "billservice_ipinuse")
					model.vpn_ipinuse_id=None
					
			
			if pool_id!=0:
				ipninuse_model= Object()
				ipninuse_model.pool_id=pool_id
				ipninuse_model.ip=model.vpn_ip_address
				ipninuse_model.datetime='now()'
				ipninuse_model.id = self.connection.save(ipninuse_model, "billservice_ipinuse")
				model.vpn_ipinuse_id=ipninuse_model.id
				#self.connection.save(model, "billservice_account")
        except Exception, e:
			print e
			QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте настройки VPN IP адресов. Возможно выбранный IP адрес не принадлежит пулу."))
			self.connection.rollback()
			return 
                
                
            
        try:
            self.connection.save(model,"billservice_subaccount")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        QtGui.QDialog.accept(self)

    def generate_login(self):
        self.lineEdit_link_login.setText(nameGen())

    def generate_password(self):
        self.lineEdit_link_password.setText(GenPasswd2())
        
    def get_ipn_from_pool(self):
        pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
        if pool_id!=0:
            child = IPAddressSelectForm(self.connection, pool_id)
            if child.exec_()==1:
                self.lineEdit_ipn_ip_address.setText(child.selected_ip)

                
    def get_vpn_from_pool(self):
        pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
        if pool_id!=0:
            child = IPAddressSelectForm(self.connection, pool_id)
            if child.exec_()==1:
                self.lineEdit_vpn_ip_address.setText(child.selected_ip)



        
class TarifFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(TarifFrame, self).__init__()
        
        self.model=model
        self.connection = connection
        self.connection.commit()
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,623,630).size()).expandedTo(self.minimumSizeHint()))
        
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,623,630).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,623,630).size()))
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(210,590,191,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0,10,621,561))
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setObjectName("tabWidget")

        self.tab_1 = QtGui.QWidget()
        self.tab_1.setObjectName("tab_1")

        self.checkBoxAllowExpressPay = QtGui.QCheckBox(self.tab_1)
        self.checkBoxAllowExpressPay.setGeometry(QtCore.QRect(150,320,597,16))

        self.tarif_description_edit = QtGui.QTextEdit(self.tab_1)
        self.tarif_description_edit.setGeometry(QtCore.QRect(11,365,597,132))
        self.tarif_description_edit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.NoTextInteraction|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.tarif_description_edit.setObjectName("tarif_description_edit")

        self.tarif_description_label = QtGui.QLabel(self.tab_1)
        self.tarif_description_label.setGeometry(QtCore.QRect(10,345,198,16))
        self.tarif_description_label.setObjectName("tarif_description_label")

        self.tarif_status_edit = QtGui.QCheckBox(self.tab_1)
        self.tarif_status_edit.setGeometry(QtCore.QRect(13,500,105,19))
        self.tarif_status_edit.setObjectName("tarif_status_edit")

        self.tarif_name_label = QtGui.QLabel(self.tab_1)
        self.tarif_name_label.setGeometry(QtCore.QRect(10,20,71,20))
        self.tarif_name_label.setObjectName("tarif_name_label")

        self.sp_groupbox = QtGui.QGroupBox(self.tab_1)
        self.sp_groupbox.setGeometry(QtCore.QRect(10,60,395,161))
        self.sp_groupbox.setObjectName("sp_groupbox")
        self.sp_groupbox.setCheckable(True)

        #self.sp_type_edit = QtGui.QCheckBox(self.sp_groupbox)
        #self.sp_type_edit.setGeometry(QtCore.QRect(11,20,466,19))
        #self.sp_type_edit.setObjectName("sp_type_edit")

        self.sp_name_label = QtGui.QLabel(self.sp_groupbox)
        self.sp_name_label.setGeometry(QtCore.QRect(10,50,100,21))
        self.sp_name_label.setObjectName("sp_name_label")

        self.sp_name_edit = QtGui.QComboBox(self.sp_groupbox)
        self.sp_name_edit.setGeometry(QtCore.QRect(140,50,241,21))
        self.sp_name_edit.setObjectName("sp_name_edit")

        self.tarif_cost_label = QtGui.QLabel(self.sp_groupbox)
        self.tarif_cost_label.setGeometry(QtCore.QRect(10,80,125,21))
        self.tarif_cost_label.setObjectName("tarif_cost_label")

        self.reset_tarif_cost_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.reset_tarif_cost_edit.setGeometry(QtCore.QRect(9,120,453,19))
        self.reset_tarif_cost_edit.setObjectName("reset_tarif_cost_edit")

        self.require_tarif_cost_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.require_tarif_cost_edit.setGeometry(QtCore.QRect(9,138,453,19))
        self.require_tarif_cost_edit.setObjectName("require_tarif_cost_edit")

        self.tarif_cost_edit = QtGui.QLineEdit(self.sp_groupbox)
        self.tarif_cost_edit.setGeometry(QtCore.QRect(139,80,241,21))
        self.tarif_cost_edit.setObjectName("tarif_cost_edit")
        self.tarif_cost_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([\.]?)([0-9]+)"), self))

        self.ps_null_ballance_checkout_edit = QtGui.QCheckBox(self.tab_1)
        self.ps_null_ballance_checkout_edit.setGeometry(QtCore.QRect(10,230,451,30))
        self.ps_null_ballance_checkout_edit.setObjectName("ps_null_ballance_checkout_edit")
        self.ps_null_ballance_checkout_edit.setHidden(True)

        self.label_systemgroup = QtGui.QLabel(self.tab_1)
        self.label_systemgroup.setGeometry(QtCore.QRect(10,231,121,21))
        self.label_systemgroup.setObjectName("label_systemgroup")

        self.comboBox_system_group = QtGui.QComboBox(self.tab_1)
        self.comboBox_system_group.setGeometry(QtCore.QRect(150,230,241,21))
        self.comboBox_system_group.setObjectName("comboBox_system_group")

        self.access_type_edit = QtGui.QComboBox(self.tab_1)
        self.access_type_edit.setGeometry(QtCore.QRect(150,260,241,21))
        self.access_type_edit.setObjectName("access_type_edit")
        #if self.model: self.access_type_edit.setDisabled(True)

        self.access_time_edit = QtGui.QComboBox(self.tab_1)
        self.access_time_edit.setGeometry(QtCore.QRect(150,290,241,21))
        self.access_time_edit.setObjectName("access_time_edit")

        self.access_type_label = QtGui.QLabel(self.tab_1)
        self.access_type_label.setGeometry(QtCore.QRect(10,261,121,21))
        self.access_type_label.setObjectName("access_type_label")

        self.access_time_label = QtGui.QLabel(self.tab_1)
        self.access_time_label.setGeometry(QtCore.QRect(10,293,131,16))
        self.access_time_label.setObjectName("access_time_label")

        self.tarif_name_edit = QtGui.QLineEdit(self.tab_1)
        self.tarif_name_edit.setGeometry(QtCore.QRect(110,20,381,20))
        self.tarif_name_edit.setObjectName("tarif_name_edit")

        self.ipn_for_vpn = QtGui.QCheckBox(self.tab_1)
        self.ipn_for_vpn.setGeometry(QtCore.QRect(400,260,200,20))
        self.ipn_for_vpn.setObjectName("ipn_for_vpn")
        
        self.components_groupBox = QtGui.QGroupBox(self.tab_1)
        self.components_groupBox.setGeometry(QtCore.QRect(420,60,190,190))
        self.components_groupBox.setObjectName("components_groupBox")

        self.widget = QtGui.QWidget(self.components_groupBox)
        self.widget.setGeometry(QtCore.QRect(11,20,198,151))
        self.widget.setObjectName("widget")

        self.vboxlayout = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.transmit_service_checkbox = QtGui.QCheckBox(self.widget)
        self.transmit_service_checkbox.setObjectName("transmit_service_checkbox")
        self.vboxlayout.addWidget(self.transmit_service_checkbox)

        self.time_access_service_checkbox = QtGui.QCheckBox(self.widget)
        self.time_access_service_checkbox.setObjectName("time_access_service_checkbox")
        self.vboxlayout.addWidget(self.time_access_service_checkbox)
        
        self.radius_traffic_access_service_checkbox = QtGui.QCheckBox(self.widget)
        self.radius_traffic_access_service_checkbox.setObjectName("radius_traffic_access_service_checkbox")
        self.vboxlayout.addWidget(self.radius_traffic_access_service_checkbox)


        self.onetime_services_checkbox = QtGui.QCheckBox(self.widget)
        self.onetime_services_checkbox.setObjectName("onetime_services_checkbox")
        self.vboxlayout.addWidget(self.onetime_services_checkbox)

        self.periodical_services_checkbox = QtGui.QCheckBox(self.widget)
        self.periodical_services_checkbox.setObjectName("periodical_services_checkbox")
        self.vboxlayout.addWidget(self.periodical_services_checkbox)

        self.limites_checkbox = QtGui.QCheckBox(self.widget)
        self.limites_checkbox.setObjectName("limites_checkbox")
        self.vboxlayout.addWidget(self.limites_checkbox)

        self.checkBox_addon_services = QtGui.QCheckBox(self.widget)
        self.checkBox_addon_services.setObjectName("checkBox_addon_services")
        self.vboxlayout.addWidget(self.checkBox_addon_services)        

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.speed_access_groupBox = QtGui.QGroupBox(self.tab_2)
        self.speed_access_groupBox.setGeometry(QtCore.QRect(10,10,598,245))
        self.speed_access_groupBox.setObjectName("speed_access_groupBox")

        self.speed_priority_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_priority_edit.setGeometry(QtCore.QRect(110,210,331,21))
        self.speed_priority_edit.setObjectName("speed_priority_edit")
        self.speed_priority_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[1-8]{1,1}"), self))

        self.speed_max_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_max_out_edit.setGeometry(QtCore.QRect(276,45,161,21))
        self.speed_max_out_edit.setObjectName("speed_max_out_edit")
        self.speed_max_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))
        
        self.speed_burst_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_out_edit.setGeometry(QtCore.QRect(276,111,164,21))
        self.speed_burst_out_edit.setObjectName("speed_burst_out_edit")
        self.speed_burst_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_burst_time_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_time_out_edit.setGeometry(QtCore.QRect(276,177,164,21))
        self.speed_burst_time_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_min_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_in_edit.setGeometry(QtCore.QRect(109,78,161,21))
        self.speed_min_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_burst_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_label.setGeometry(QtCore.QRect(11,111,89,21))
        self.speed_burst_label.setObjectName("speed_burst_label")

        self.speed_burst_treshold_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_out_edit.setGeometry(QtCore.QRect(276,144,164,21))
        self.speed_burst_treshold_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_priority_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_priority_label.setGeometry(QtCore.QRect(11,210,89,21))
        self.speed_priority_label.setObjectName("speed_priority_label")

        self.speed_burst_time_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_time_label.setGeometry(QtCore.QRect(11,177,89,21))
        self.speed_burst_time_label.setObjectName("speed_burst_time_label")

        self.speed_burst_treshold_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_treshold_label.setGeometry(QtCore.QRect(11,144,89,21))
        self.speed_burst_treshold_label.setObjectName("speed_burst_treshold_label")

        self.speed_burst_time_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_time_in_edit.setGeometry(QtCore.QRect(109,177,161,21))
        self.speed_burst_time_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_burst_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_in_edit.setGeometry(QtCore.QRect(109,111,161,21))
        self.speed_burst_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_out_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_out_label.setGeometry(QtCore.QRect(276,21,164,18))
        self.speed_out_label.setObjectName("speed_out_label")

        self.speed_in_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_in_label.setGeometry(QtCore.QRect(106,21,164,18))
        self.speed_in_label.setObjectName("speed_in_label")

        self.speed_max_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_max_label.setGeometry(QtCore.QRect(11,45,89,21))
        self.speed_max_label.setObjectName("speed_max_label")

        self.speed_max_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_max_in_edit.setGeometry(QtCore.QRect(109,45,161,21))
        self.speed_max_in_edit.setFrame(True)
        self.speed_max_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_min_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_min_label.setGeometry(QtCore.QRect(11,78,89,21))
        self.speed_min_label.setObjectName("speed_min_label")

        self.speed_min_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_out_edit.setGeometry(QtCore.QRect(276,78,164,21))
        self.speed_min_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_burst_treshold_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_in_edit.setGeometry(QtCore.QRect(109,144,161,21))
        self.speed_burst_treshold_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([kM]?)"), self))

        self.speed_table = QtGui.QTableWidget(self.tab_2)
        self.speed_table.setGeometry(QtCore.QRect(9,290,595,239))
        self.speed_table.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        #-------------
        #self.speed_table = tableFormat(self.speed_table)
        #-------------
        

        
        


        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.reset_traffic_edit = QtGui.QCheckBox(self.tab_4)
        self.reset_traffic_edit.setGeometry(QtCore.QRect(12,498,398,19))
        self.reset_traffic_edit.setObjectName("reset_traffic_edit")

        self.trafficcost_tableWidget = QtGui.QTableWidget(self.tab_4)
        self.trafficcost_tableWidget.setGeometry(QtCore.QRect(8,60,601,247))
        #--------------
        #self.trafficcost_tableWidget = tableFormat(self.trafficcost_tableWidget)
        #--------------
        
        
        self.trafficcost_label = QtGui.QLabel(self.tab_4)
        self.trafficcost_label.setGeometry(QtCore.QRect(10,10,161,16))
        self.trafficcost_label.setObjectName("trafficcost_label")

        self.traffic_cost_panel = QtGui.QFrame(self.tab_4)
        self.traffic_cost_panel.setGeometry(QtCore.QRect(10,30,598,27))
        self.traffic_cost_panel.setFrameShape(QtGui.QFrame.Box)
        self.traffic_cost_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.traffic_cost_panel.setObjectName("traffic_cost_panel")

        
        

        self.del_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel)
        self.del_traffic_cost_button.setGeometry(QtCore.QRect(41,3,25,20))
        self.del_traffic_cost_button.setObjectName("del_traffic_cost_button")

        self.add_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel)
        self.add_traffic_cost_button.setGeometry(QtCore.QRect(7,3,24,20))
        self.add_traffic_cost_button.setObjectName("add_traffic_cost_button")

        self.prepaid_tableWidget = QtGui.QTableWidget(self.tab_4)
        self.prepaid_tableWidget.setGeometry(QtCore.QRect(10,370,599,121))
        #--------------
        #self.prepaid_tableWidget = tableFormat(self.prepaid_tableWidget)
        #--------------

        self.prepaid_traffic_cost_label = QtGui.QLabel(self.tab_4)
        self.prepaid_traffic_cost_label.setGeometry(QtCore.QRect(10,320,203,16))
        self.prepaid_traffic_cost_label.setObjectName("prepaid_traffic_cost_label")

        self.prepaid_traffic_panel = QtGui.QFrame(self.tab_4)
        self.prepaid_traffic_panel.setGeometry(QtCore.QRect(10,340,600,27))
        self.prepaid_traffic_panel.setFrameShape(QtGui.QFrame.Box)
        self.prepaid_traffic_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.prepaid_traffic_panel.setObjectName("prepaid_traffic_panel")

        self.del_prepaid_traffic_button = QtGui.QToolButton(self.prepaid_traffic_panel)
        self.del_prepaid_traffic_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_prepaid_traffic_button.setObjectName("del_prepaid_traffic_button")

        self.add_prepaid_traffic_button = QtGui.QToolButton(self.prepaid_traffic_panel)
        self.add_prepaid_traffic_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_prepaid_traffic_button.setObjectName("add_prepaid_traffic_button")
        
        self.tabWidget.addTab(self.tab_1,"")
        self.tabWidget.addTab(self.tab_2,"")
        self.tabWidget.addTab(self.tab_4,"")

        
        #
        self.speed_panel = QtGui.QFrame(self.tab_2)
        self.speed_panel.setGeometry(QtCore.QRect(9,260,597,27))
        self.speed_panel.setFrameShape(QtGui.QFrame.Box)
        self.speed_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.speed_panel.setObjectName("speed_panel")

        self.del_speed_button = QtGui.QToolButton(self.speed_panel)
        self.del_speed_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_speed_button.setObjectName("del_speed_button")

        self.add_speed_button = QtGui.QToolButton(self.speed_panel)
        self.add_speed_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_speed_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.add_speed_button.setObjectName("add_speed_button")
        
        #======================================================
        self.tab_radius_traffic = QtGui.QWidget()
        self.tab_radius_traffic.setObjectName(_fromUtf8("tab_radius_traffic"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_radius_traffic)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.commandLinkButton_add_radius_trafficcost = QtGui.QCommandLinkButton(self.tab_radius_traffic)
        self.commandLinkButton_add_radius_trafficcost.setDefault(True)
        self.commandLinkButton_add_radius_trafficcost.setObjectName(_fromUtf8("commandLinkButton_add_radius_trafficcost"))
        self.gridLayout_5.addWidget(self.commandLinkButton_add_radius_trafficcost, 0, 0, 1, 1)
        self.commandLinkButton_del_radius_trafficcost = QtGui.QCommandLinkButton(self.tab_radius_traffic)
        self.commandLinkButton_del_radius_trafficcost.setObjectName(_fromUtf8("commandLinkButton_del_radius_trafficcost"))
        self.gridLayout_5.addWidget(self.commandLinkButton_del_radius_trafficcost, 0, 1, 1, 1)
        self.tableWidget_radius_traffic_trafficcost = QtGui.QTableWidget(self.tab_radius_traffic)
        self.tableWidget_radius_traffic_trafficcost.setObjectName(_fromUtf8("tableWidget_radius_traffic_trafficcost"))
        self.tableWidget_radius_traffic_trafficcost.setColumnCount(3)
        self.tableWidget_radius_traffic_trafficcost.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_radius_traffic_trafficcost.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_radius_traffic_trafficcost.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_radius_traffic_trafficcost.setHorizontalHeaderItem(2, item)
        self.gridLayout_5.addWidget(self.tableWidget_radius_traffic_trafficcost, 1, 0, 1, 2)
        self.groupBox_radius_traffic_tarification_settings = QtGui.QGroupBox(self.tab_radius_traffic)
        self.groupBox_radius_traffic_tarification_settings.setObjectName(_fromUtf8("groupBox_radius_traffic_tarification_settings"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_radius_traffic_tarification_settings)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_radius_traffic_direction = QtGui.QLabel(self.groupBox_radius_traffic_tarification_settings)
        self.label_radius_traffic_direction.setObjectName(_fromUtf8("label_radius_traffic_direction"))
        self.gridLayout_4.addWidget(self.label_radius_traffic_direction, 0, 0, 2, 1)
        self.comboBox_radius_traffic_direction = QtGui.QComboBox(self.groupBox_radius_traffic_tarification_settings)
        self.comboBox_radius_traffic_direction.setObjectName(_fromUtf8("comboBox_radius_traffic_direction"))
        self.gridLayout_4.addWidget(self.comboBox_radius_traffic_direction, 0, 1, 2, 2)
        self.label_radius_traffic_tarification_step = QtGui.QLabel(self.groupBox_radius_traffic_tarification_settings)
        self.label_radius_traffic_tarification_step.setObjectName(_fromUtf8("label_radius_traffic_tarification_step"))
        self.gridLayout_4.addWidget(self.label_radius_traffic_tarification_step, 2, 0, 1, 1)
        self.label_radius_traffic_rounding = QtGui.QLabel(self.groupBox_radius_traffic_tarification_settings)
        self.label_radius_traffic_rounding.setObjectName(_fromUtf8("label_radius_traffic_rounding"))
        self.gridLayout_4.addWidget(self.label_radius_traffic_rounding, 3, 0, 1, 1)
        self.comboBox_radius_traffic_rounding = QtGui.QComboBox(self.groupBox_radius_traffic_tarification_settings)
        self.comboBox_radius_traffic_rounding.setObjectName(_fromUtf8("comboBox_radius_traffic_rounding"))
        self.gridLayout_4.addWidget(self.comboBox_radius_traffic_rounding, 3, 1, 1, 2)
        self.spinBox_radius_traffic_tarification_step = QtGui.QSpinBox(self.groupBox_radius_traffic_tarification_settings)
        self.spinBox_radius_traffic_tarification_step.setMinimum(1)
        self.spinBox_radius_traffic_tarification_step.setMaximum(999999999)
        self.spinBox_radius_traffic_tarification_step.setObjectName(_fromUtf8("spinBox_radius_traffic_tarification_step"))
        self.gridLayout_4.addWidget(self.spinBox_radius_traffic_tarification_step, 2, 1, 1, 2)
        self.gridLayout_5.addWidget(self.groupBox_radius_traffic_tarification_settings, 3, 0, 1, 2)
        self.groupBox_radius_prepaidtraffic = QtGui.QGroupBox(self.tab_radius_traffic)
        self.groupBox_radius_prepaidtraffic.setObjectName(_fromUtf8("groupBox_radius_prepaidtraffic"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_radius_prepaidtraffic)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_radius_traffic_prepaid_direction = QtGui.QLabel(self.groupBox_radius_prepaidtraffic)
        self.label_radius_traffic_prepaid_direction.setObjectName(_fromUtf8("label_radius_traffic_prepaid_direction"))
        self.gridLayout_6.addWidget(self.label_radius_traffic_prepaid_direction, 0, 0, 1, 1)
        self.comboBox_radius_traffic_prepaid_direction = QtGui.QComboBox(self.groupBox_radius_prepaidtraffic)
        self.comboBox_radius_traffic_prepaid_direction.setObjectName(_fromUtf8("comboBox_radius_traffic_prepaid_direction"))
        self.gridLayout_6.addWidget(self.comboBox_radius_traffic_prepaid_direction, 0, 1, 1, 1)
        self.spinBox_radius_traffic_prepaid_volume = QtGui.QSpinBox(self.groupBox_radius_prepaidtraffic)
        self.spinBox_radius_traffic_prepaid_volume.setMaximum(999999999)
        self.spinBox_radius_traffic_prepaid_volume.setObjectName(_fromUtf8("spinBox_radius_traffic_prepaid_volume"))
        self.gridLayout_6.addWidget(self.spinBox_radius_traffic_prepaid_volume, 1, 1, 1, 1)
        self.label_radius_traffic_prepaid_volume = QtGui.QLabel(self.groupBox_radius_prepaidtraffic)
        self.label_radius_traffic_prepaid_volume.setObjectName(_fromUtf8("label_radius_traffic_prepaid_volume"))
        self.gridLayout_6.addWidget(self.label_radius_traffic_prepaid_volume, 1, 0, 1, 1)
        self.checkBox_radius_traffic_reset_prepaidtraffic = QtGui.QCheckBox(self.groupBox_radius_prepaidtraffic)
        self.checkBox_radius_traffic_reset_prepaidtraffic.setObjectName(_fromUtf8("checkBox_radius_traffic_reset_prepaidtraffic"))
        self.gridLayout_6.addWidget(self.checkBox_radius_traffic_reset_prepaidtraffic, 2, 0, 1, 2)
        self.gridLayout_5.addWidget(self.groupBox_radius_prepaidtraffic, 2, 0, 1, 2)
        self.tabWidget.addTab(self.tab_radius_traffic, _fromUtf8(""))
        self.tab_radius_time = QtGui.QWidget()
        self.tab_radius_time.setObjectName(_fromUtf8("tab_radius_time"))
        self.gridLayout = QtGui.QGridLayout(self.tab_radius_time)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.timeaccess_table = QtGui.QTableWidget(self.tab_radius_time)
        self.timeaccess_table.setFrameShape(QtGui.QFrame.Panel)
        self.timeaccess_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.timeaccess_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.timeaccess_table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.timeaccess_table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.timeaccess_table.setGridStyle(QtCore.Qt.DotLine)
        self.timeaccess_table.setObjectName(_fromUtf8("timeaccess_table"))
        self.timeaccess_table.setColumnCount(3)
        self.timeaccess_table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.timeaccess_table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.timeaccess_table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.timeaccess_table.setHorizontalHeaderItem(2, item)
        self.gridLayout.addWidget(self.timeaccess_table, 2, 0, 1, 2)
        self.groupBox_radius_time_tarification_settings = QtGui.QGroupBox(self.tab_radius_time)
        self.groupBox_radius_time_tarification_settings.setObjectName(_fromUtf8("groupBox_radius_time_tarification_settings"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_radius_time_tarification_settings)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.comboBox_radius_time_rounding = QtGui.QComboBox(self.groupBox_radius_time_tarification_settings)
        self.comboBox_radius_time_rounding.setObjectName(_fromUtf8("comboBox_radius_time_rounding"))
        self.gridLayout_3.addWidget(self.comboBox_radius_time_rounding, 0, 1, 1, 1)
        self.label_radius_time_rounding = QtGui.QLabel(self.groupBox_radius_time_tarification_settings)
        self.label_radius_time_rounding.setObjectName(_fromUtf8("label_radius_time_rounding"))
        self.gridLayout_3.addWidget(self.label_radius_time_rounding, 0, 0, 1, 1)
        self.label_radius_time_tarification_step = QtGui.QLabel(self.groupBox_radius_time_tarification_settings)
        self.label_radius_time_tarification_step.setObjectName(_fromUtf8("label_radius_time_tarification_step"))
        self.gridLayout_3.addWidget(self.label_radius_time_tarification_step, 1, 0, 1, 1)
        self.spinBox_radius_time_tarification_step = QtGui.QSpinBox(self.groupBox_radius_time_tarification_settings)
        self.spinBox_radius_time_tarification_step.setMinimum(1)
        self.spinBox_radius_time_tarification_step.setMaximum(999999999)
        self.spinBox_radius_time_tarification_step.setObjectName(_fromUtf8("spinBox_radius_time_tarification_step"))
        self.gridLayout_3.addWidget(self.spinBox_radius_time_tarification_step, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_radius_time_tarification_settings, 4, 0, 1, 2)
        self.commandLinkButton_add_radius_timecost = QtGui.QCommandLinkButton(self.tab_radius_time)
        self.commandLinkButton_add_radius_timecost.setDefault(True)
        self.commandLinkButton_add_radius_timecost.setObjectName(_fromUtf8("commandLinkButton_add_radius_timecost"))
        self.gridLayout.addWidget(self.commandLinkButton_add_radius_timecost, 0, 0, 1, 1)
        self.commandLinkButton_del_radius_timecost = QtGui.QCommandLinkButton(self.tab_radius_time)
        self.commandLinkButton_del_radius_timecost.setObjectName(_fromUtf8("commandLinkButton_del_radius_timecost"))
        self.gridLayout.addWidget(self.commandLinkButton_del_radius_timecost, 0, 1, 1, 1)
        self.groupBox_radius_time_prepaid = QtGui.QGroupBox(self.tab_radius_time)
        self.groupBox_radius_time_prepaid.setObjectName(_fromUtf8("groupBox_radius_time_prepaid"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_radius_time_prepaid)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.prepaid_time_label = QtGui.QLabel(self.groupBox_radius_time_prepaid)
        self.prepaid_time_label.setObjectName(_fromUtf8("prepaid_time_label"))
        self.gridLayout_7.addWidget(self.prepaid_time_label, 0, 0, 1, 1)
        self.prepaid_time_edit = QtGui.QSpinBox(self.groupBox_radius_time_prepaid)
        self.prepaid_time_edit.setMaximum(999999999)
        self.prepaid_time_edit.setObjectName(_fromUtf8("prepaid_time_edit"))
        self.gridLayout_7.addWidget(self.prepaid_time_edit, 0, 1, 1, 1)
        self.reset_time_checkbox = QtGui.QCheckBox(self.groupBox_radius_time_prepaid)
        self.reset_time_checkbox.setObjectName(_fromUtf8("reset_time_checkbox"))
        self.gridLayout_7.addWidget(self.reset_time_checkbox, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox_radius_time_prepaid, 3, 0, 1, 2)
        self.tabWidget.addTab(self.tab_radius_time, _fromUtf8(""))        

        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName("tab_6")

        self.onetime_tableWidget = QtGui.QTableWidget(self.tab_6)
        self.onetime_tableWidget.setGeometry(QtCore.QRect(10,40,597,486))
        #--------------
        #self.onetime_tableWidget = tableFormat(self.onetime_tableWidget)
        #--------------


        self.onetime_panel = QtGui.QFrame(self.tab_6)
        self.onetime_panel.setGeometry(QtCore.QRect(10,10,596,27))
        self.onetime_panel.setFrameShape(QtGui.QFrame.Box)
        self.onetime_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.onetime_panel.setObjectName("onetime_panel")

        self.del_onetime_button = QtGui.QToolButton(self.onetime_panel)
        self.del_onetime_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_onetime_button.setObjectName("del_onetime_button")

        self.add_onetime_button = QtGui.QToolButton(self.onetime_panel)
        self.add_onetime_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_onetime_button.setObjectName("add_onetime_button")
        self.tabWidget.addTab(self.tab_6,"")
        

        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName("tab_5")

        self.periodical_tableWidget = QtGui.QTableWidget(self.tab_5)
        self.periodical_tableWidget.setGeometry(QtCore.QRect(10,40,597,486))
        #--------------
        #self.periodical_tableWidget = tableFormat(self.periodical_tableWidget)
        #--------------

        self.periodical_panel = QtGui.QFrame(self.tab_5)
        self.periodical_panel.setGeometry(QtCore.QRect(10,10,596,27))
        self.periodical_panel.setFrameShape(QtGui.QFrame.Box)
        self.periodical_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.periodical_panel.setObjectName("periodical_panel")

        self.del_periodical_button = QtGui.QToolButton(self.periodical_panel)
        self.del_periodical_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_periodical_button.setObjectName("del_periodical_button")

        self.add_periodical_button = QtGui.QToolButton(self.periodical_panel)
        self.add_periodical_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_periodical_button.setObjectName("add_periodical_button")
        self.tabWidget.addTab(self.tab_5,"")

        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName("tab_7")

        self.limit_tableWidget = QtGui.QTableWidget(self.tab_7)
        self.limit_tableWidget.setGeometry(QtCore.QRect(10,40,597,486))
        #--------------------
        #self.limit_tableWidget = tableFormat(self.limit_tableWidget)


        self.limit_panel = QtGui.QFrame(self.tab_7)
        self.limit_panel.setGeometry(QtCore.QRect(10,10,596,27))
        self.limit_panel.setFrameShape(QtGui.QFrame.Box)
        self.limit_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.limit_panel.setObjectName("limit_panel")

        self.del_limit_button = QtGui.QToolButton(self.limit_panel)
        self.del_limit_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_limit_button.setObjectName("del_limit_button")

        self.add_limit_button = QtGui.QToolButton(self.limit_panel)
        self.add_limit_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_limit_button.setObjectName("add_limit_button")
        self.tabWidget.addTab(self.tab_7,"")
        
#
        self.tab_8 = QtGui.QWidget()
        self.tab_8.setObjectName("tab_8")

        self.tableWidget_addonservices = QtGui.QTableWidget(self.tab_8)
        self.tableWidget_addonservices.setGeometry(QtCore.QRect(10,40,597,486))
        #--------------------
        #self.limit_tableWidget = tableFormat(self.limit_tableWidget)


        self.panel_addonservice = QtGui.QFrame(self.tab_8)
        self.panel_addonservice.setGeometry(QtCore.QRect(10,10,596,27))
        self.panel_addonservice.setFrameShape(QtGui.QFrame.Box)
        self.panel_addonservice.setFrameShadow(QtGui.QFrame.Raised)
        self.panel_addonservice.setObjectName("limit_panel")

        self.del_addonservice_button = QtGui.QToolButton(self.panel_addonservice)
        self.del_addonservice_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_addonservice_button.setObjectName("del_addonservice_button")

        self.add_addonservice_button = QtGui.QToolButton(self.panel_addonservice)
        self.add_addonservice_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_addonservice_button.setObjectName("add_addonservice_button")
        self.tabWidget.addTab(self.tab_8,"")
#        
        
        
        
        
        self.tarif_description_label.setBuddy(self.tarif_description_edit)
        self.speed_burst_label.setBuddy(self.speed_burst_in_edit)
        self.speed_burst_time_label.setBuddy(self.speed_burst_time_in_edit)
        self.speed_burst_treshold_label.setBuddy(self.speed_burst_treshold_in_edit)
        self.speed_max_label.setBuddy(self.speed_max_in_edit)
        self.speed_min_label.setBuddy(self.speed_min_in_edit)
        
        self.ipn_for_vpn_state = 0
        QtCore.QObject.connect(self.access_type_edit, QtCore.SIGNAL("currentIndexChanged (const QString&)"), self.onAccessTypeChange)
        self.retranslateUi()
        self.fixtures()
        self.speed_table = tableFormat(self.speed_table)
        self.timeaccess_table = tableFormat(self.timeaccess_table)
        self.limit_tableWidget = tableFormat(self.limit_tableWidget, no_vsection_size=True)
        self.periodical_tableWidget = tableFormat(self.periodical_tableWidget)
        self.onetime_tableWidget = tableFormat(self.onetime_tableWidget)
        self.prepaid_tableWidget = tableFormat(self.prepaid_tableWidget, no_vsection_size=True)
        self.trafficcost_tableWidget = tableFormat(self.trafficcost_tableWidget, no_vsection_size=True)
        self.tableWidget_radius_traffic_trafficcost = tableFormat(self.tableWidget_radius_traffic_trafficcost)
        self.tableWidget_addonservices = tableFormat(self.tableWidget_addonservices, no_vsection_size=True)
        self.tabWidget.setCurrentIndex(0)
        
#------------Connects

        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.trafficcost_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.trafficCostCellEdit)
        QtCore.QObject.connect(self.prepaid_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.prepaidTrafficEdit)
        QtCore.QObject.connect(self.limit_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.limitClassEdit)
        
        QtCore.QObject.connect(self.onetime_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.oneTimeServicesEdit)
        
        
        QtCore.QObject.connect(self.timeaccess_table, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.timeAccessServiceEdit)
        
        QtCore.QObject.connect(self.tableWidget_radius_traffic_trafficcost, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.radiusTrafficEdit)
        
        QtCore.QObject.connect(self.periodical_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.periodicalServicesEdit)
        
        
        QtCore.QObject.connect(self.speed_table, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.speedEdit)
        
        QtCore.QObject.connect(self.tableWidget_addonservices, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.addonserviceEdit)
        
        QtCore.QObject.connect(self.add_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.addTrafficCostRow)
        QtCore.QObject.connect(self.del_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.delTrafficCostRow)

        QtCore.QObject.connect(self.add_limit_button, QtCore.SIGNAL("clicked()"), self.addLimitRow)
        QtCore.QObject.connect(self.del_limit_button, QtCore.SIGNAL("clicked()"), self.delLimitRow)       

        QtCore.QObject.connect(self.add_onetime_button, QtCore.SIGNAL("clicked()"), self.addOneTimeRow)
        QtCore.QObject.connect(self.del_onetime_button, QtCore.SIGNAL("clicked()"), self.delOneTimeRow)        
        
        QtCore.QObject.connect(self.commandLinkButton_add_radius_timecost, QtCore.SIGNAL("clicked()"), self.addTimeAccessRow)
        QtCore.QObject.connect(self.commandLinkButton_del_radius_timecost, QtCore.SIGNAL("clicked()"), self.delTimeAccessRow)

        QtCore.QObject.connect(self.commandLinkButton_add_radius_trafficcost, QtCore.SIGNAL("clicked()"), self.addRadiusTrafficRow)
        QtCore.QObject.connect(self.commandLinkButton_del_radius_trafficcost, QtCore.SIGNAL("clicked()"), self.delRadiusTrafficRow)

        QtCore.QObject.connect(self.add_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.addPrepaidTrafficRow)
        QtCore.QObject.connect(self.del_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.delPrepaidTrafficRow)        
        
        QtCore.QObject.connect(self.add_speed_button, QtCore.SIGNAL("clicked()"), self.addSpeedRow)
        QtCore.QObject.connect(self.del_speed_button, QtCore.SIGNAL("clicked()"), self.delSpeedRow)   
        
        QtCore.QObject.connect(self.add_periodical_button, QtCore.SIGNAL("clicked()"), self.addPeriodicalRow)
        QtCore.QObject.connect(self.del_periodical_button, QtCore.SIGNAL("clicked()"), self.delPeriodicalRow)   

        QtCore.QObject.connect(self.add_addonservice_button, QtCore.SIGNAL("clicked()"), self.addAddonServiceRow)
        QtCore.QObject.connect(self.del_addonservice_button, QtCore.SIGNAL("clicked()"), self.delAddonServiceRow)   
        
        #QtCore.QObject.connect(self.sp_type_edit, QtCore.SIGNAL("stateChanged(int)"), self.filterSettlementPeriods)
        
        QtCore.QObject.connect(self.transmit_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.transmitTabActivityActions)
        
        QtCore.QObject.connect(self.time_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.timeaccessTabActivityActions)
        QtCore.QObject.connect(self.radius_traffic_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.radiusTrafficTabActivityActions)
        
        QtCore.QObject.connect(self.onetime_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.onetimeTabActivityActions)
        
        QtCore.QObject.connect(self.periodical_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.periodicalServicesTabActivityActions)
        
        QtCore.QObject.connect(self.limites_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.limitTabActivityActions)
        QtCore.QObject.connect(self.checkBox_addon_services, QtCore.SIGNAL("stateChanged(int)"), self.addonservicesTabActivityActions)
        QtCore.QObject.connect(self.ipn_for_vpn, QtCore.SIGNAL("stateChanged(int)"), self.ipn_for_vpnActions)

        QtCore.QObject.connect(self.sp_name_edit, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.spChangedActions)
        
        QtCore.QObject.connect(self.comboBox_radius_time_rounding, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.timeRoundingActions)
        QtCore.QObject.connect(self.comboBox_radius_traffic_rounding, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.trafficRoundingActions)
        #-----------------------
        self.timeRoundingActions()        
        self.trafficRoundingActions()
        

        
    def retranslateUi(self):
        if self.model:
            self.setWindowTitle(u"Настройки тарифного плана %s" % self.model.name)
        else:
            self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки нового тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("Dialog", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Статус тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("Dialog", "Расчётный период тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setToolTip(QtGui.QApplication.translate("Dialog", "Расчётный период необходим для начисления/списания предоплаченного времени/трафика \nи доснятия денег до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        #self.sp_type_edit.setText(QtGui.QApplication.translate("Dialog", "Начать при активации у пользователя данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("Dialog", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("Dialog", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Опция позволяет получить от абонента за расчётный период \nсумму денег не менее той, которая указана в стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.require_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Требовать наличия всей суммы", None, QtGui.QApplication.UnicodeUTF8))
        self.require_tarif_cost_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Требовать наличия всей суммы в начале расчётного периода.\nЕсли суммы на балансе не хватает - пользователь блокируется.", None, QtGui.QApplication.UnicodeUTF8))
        #self.ps_null_ballance_checkout_edit.setText(QtGui.QApplication.translate("Dialog", "Производить снятие денег при нулевом балансе пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setText(QtGui.QApplication.translate("Dialog", "Способ доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setText(QtGui.QApplication.translate("Dialog", "Время доступа", None, QtGui.QApplication.UnicodeUTF8))
        
        self.label_systemgroup.setText(QtGui.QApplication.translate("Dialog", "Группа доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Набор компонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setToolTip(QtGui.QApplication.translate("Dialog", "Набор компонентов тарифного плана, которые будут участвовать в тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за трафик(NetFlow)", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Тарификация трафика по NetFlow статистике.\nПозволяет строить правила тарификации в зависимости от классов и групп трафика.", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_for_vpn.setText(QtGui.QApplication.translate("Dialog", "Производить IPN действия", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Оплата за время по протоколу RADIUS", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Единоразовые списания \nпри подключении абонента на данный тарифный план.\nСписание будет выполнено каждый раз при его назначении абоненту тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Абонентская плата", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setText(QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Ограничения на объём потребления трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setText(QtGui.QApplication.translate("Dialog", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setToolTip(QtGui.QApplication.translate("Dialog", "Тарификация дополнительных услуг и сервисов. ", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_access_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Настройки скорости по-умолчанию", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_label.setText(QtGui.QApplication.translate("Dialog", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_priority_label.setText(QtGui.QApplication.translate("Dialog", "Приоритет", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_time_label.setText(QtGui.QApplication.translate("Dialog", "Burst Time(c)", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_treshold_label.setText(QtGui.QApplication.translate("Dialog", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("Dialog", "OUT(bytes/k/M)", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("Dialog", "IN(bytes/k/M)", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_max_label.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_min_label.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxAllowExpressPay.setText(QtGui.QApplication.translate("Dialog", "Разрешить активацию карт экспресс-оплаты", None, QtGui.QApplication.UnicodeUTF8))
        
        self.speed_table.clear()
        columns=[u'#',u'Время', u'MAX', u'MIN', u'Burst', u'Burst Treshold', u'Burst Time', u'Priority']
        
        makeHeaders(columns, self.speed_table) 
        
        self.del_speed_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_speed_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_time_label.setText(QtGui.QApplication.translate("Dialog", "Предоплачено, с", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_time_checkbox.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце расчётного периода предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.clear()

        columns=[u'#', u'Время', u'Цена за минуту']
        
        makeHeaders(columns, self.timeaccess_table)     
        
        #self.del_timecost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        #self.add_timecost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        
        self.reset_traffic_edit.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце периода предоплаченый трафик", None, QtGui.QApplication.UnicodeUTF8))
        
        self.trafficcost_tableWidget.clear()
        columns=[u'#', u'От МБ', u'До МБ', u'Группа', u'Время', u'Цена за МБ']
        
        makeHeaders(columns, self.trafficcost_tableWidget)
        self.trafficcost_tableWidget.setColumnHidden(1, True)
        self.trafficcost_tableWidget.setColumnHidden(2, True)     
        #self.trafficcost_tableWidget.setColumnHidden(2, True)

        self.trafficcost_label.setText(QtGui.QApplication.translate("Dialog", "Цена за МБ трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.del_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        
        self.prepaid_tableWidget.clear()
        columns=[u'#', u'Группа',  u'МБ']
        
        makeHeaders(columns, self.prepaid_tableWidget)                
                
        self.prepaid_traffic_cost_label.setText(QtGui.QApplication.translate("Dialog", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.del_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("Dialog", "Оплата за трафик", None, QtGui.QApplication.UnicodeUTF8))
        
        self.onetime_tableWidget.clear()

        columns=[u'#', u'Название', u'Стоимость']
        
        makeHeaders(columns, self.onetime_tableWidget)
        
        self.del_onetime_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_onetime_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        
        self.periodical_tableWidget.clear()
        columns=[u'#', u'Название', u'Период', u"Начало списаний", u'Способ снятия', u'Стоимость', u"Условие", u"Отключить услугу с"]
        
        makeHeaders(columns, self.periodical_tableWidget)
        
        self.del_periodical_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_periodical_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.clear()

        columns=[u'#', u'Название', u'За последний', u'Период', u'Группа', u'МБ',u"Действие", u"Скорость"]
        
        makeHeaders(columns, self.limit_tableWidget)
        
        self.del_limit_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_limit_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        

        columns=[u'#', u'Название', u'Количество активаций', u'За период времени']
        
        makeHeaders(columns, self.tableWidget_addonservices)
        
        self.del_addonservice_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_addonservice_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), QtGui.QApplication.translate("Dialog", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))

        self.commandLinkButton_add_radius_trafficcost.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add_radius_trafficcost.setDescription(QtGui.QApplication.translate("Dialog", "Добавить цену", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del_radius_trafficcost.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del_radius_trafficcost.setDescription(QtGui.QApplication.translate("Dialog", "Удалить цену", None, QtGui.QApplication.UnicodeUTF8))
        columns=['#',u'Объём', u'Период тарификации', u'Цена за МБ.(после достижения объёма)']
        makeHeaders(columns, self.tableWidget_radius_traffic_trafficcost)     
        self.groupBox_radius_traffic_tarification_settings.setTitle(QtGui.QApplication.translate("Dialog", "Параметры тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_direction.setText(QtGui.QApplication.translate("Dialog", "Направление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_tarification_step.setText(QtGui.QApplication.translate("Dialog", "Единица тарификации, кб.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_rounding.setText(QtGui.QApplication.translate("Dialog", "Способ округления", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_prepaidtraffic.setTitle(QtGui.QApplication.translate("Dialog", "Предоплаченный трафик, мб.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_prepaid_direction.setText(QtGui.QApplication.translate("Dialog", "Направление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_prepaid_volume.setText(QtGui.QApplication.translate("Dialog", "Объём", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_radius_traffic_reset_prepaidtraffic.setText(QtGui.QApplication.translate("Dialog", "Cбрасывать в конце расчётного периода предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_radius_traffic), QtGui.QApplication.translate("Dialog", "Radius трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_radius_time), QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_time_tarification_settings.setTitle(QtGui.QApplication.translate("Dialog", "Параметры тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_time_rounding.setText(QtGui.QApplication.translate("Dialog", "Способ округления", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_time_tarification_step.setText(QtGui.QApplication.translate("Dialog", "Период тарификации, сек.", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add_radius_timecost.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add_radius_timecost.setDescription(QtGui.QApplication.translate("Dialog", "Добавить цену", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del_radius_timecost.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del_radius_timecost.setDescription(QtGui.QApplication.translate("Dialog", "Удалить цену", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_time_prepaid.setTitle(QtGui.QApplication.translate("Dialog", "Предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.radius_traffic_access_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "RADIUS трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.radius_traffic_access_service_checkbox.setToolTip(QtGui.QApplication.translate("Dialog", "Тарификация трафика по протоколу RADIUS", None, QtGui.QApplication.UnicodeUTF8))

        
    def spChangedActions(self, text):
        if text == '':
            self.reset_tarif_cost_edit.setDisabled(True)
            self.reset_tarif_cost_edit.setChecked(False)
            
            self.reset_traffic_edit.setDisabled(True)
            self.reset_traffic_edit.setChecked(False)

            self.reset_time_checkbox.setDisabled(True)
            self.reset_time_checkbox.setChecked(False)
        else:
            self.reset_tarif_cost_edit.setDisabled(False)
            self.reset_traffic_edit.setDisabled(False)
            self.reset_time_checkbox.setDisabled(False)

    def timeRoundingActions(self):
        if self.comboBox_radius_time_rounding.itemData(self.comboBox_radius_time_rounding.currentIndex()).toInt()[0]==0:
            self.spinBox_radius_time_tarification_step.setValue(1)
            self.spinBox_radius_time_tarification_step.setDisabled(True)
        else:
            self.spinBox_radius_time_tarification_step.setDisabled(False)
                        
    def trafficRoundingActions(self):
        if self.comboBox_radius_traffic_rounding.itemData(self.comboBox_radius_traffic_rounding.currentIndex()).toInt()[0]==0:
            self.spinBox_radius_traffic_tarification_step.setValue(1)
            self.spinBox_radius_traffic_tarification_step.setDisabled(True)
        else:
            self.spinBox_radius_traffic_tarification_step.setDisabled(False)
                        
    def ipn_for_vpnActions(self, value):
        if self.model is not None:
            if value==2 and self.connection.get("SELECT count(*) as accounts FROM billservice_account WHERE ipn_ip_address='0.0.0.0' and get_tarif(id)=%s" % self.model.id).accounts>0:
                self.ipn_for_vpn.setChecked(0)
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Вы не можете выбрать эту опцию, так как не у всех у пользователей \nданного тарифного плана указан IPN IP адрес."))
                 
    def addrow(self, widget, value, x, y, item_type=None, id=None):
        if value==None:
            value=''
            
        if not item_type:
            item = QtGui.QTableWidgetItem()
            item.setText(unicode(value))
            #item.setTextAlignment (QtCore.Qt.AlignRight)               
            widget.setItem(x, y, item)
            
        if item_type=='checkbox':
            item = QtGui.QCheckBox()
            #item = QtGui.QTableWidgetItem()
            #item.setText(u"Да")
            #print "value", value
            #item.setTextAlignment (QtCore.Qt.AlignRight)
            #item.setCheckState(value == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #item.setChecked(True)
            widget.setCellWidget(x,y, item)
            widget.cellWidget(x,y).setChecked(value)
            #widget.cellWidget(x,y).setAlignment(QtCore.Qt.AlignRight)
            #widget.setItem(x, y, item)
        
        if item_type == 'combobox':
            item = QtGui.QTableWidgetItem()
            item.setText(unicode(value))
            
            widget.setItem(x, y, item)


        item.id=id    
        #if type(value)==BooleanType and value==True:
        #    item.setIcon(QtGui.QIcon("images/ok.png"))
        #elif type(value)==BooleanType and value==False:
        #    item.setIcon(QtGui.QIcon("images/false.png"))
            
    def timeAccessRowEdit(self):
        pass
 
    #-----------------------------Добавление строк в таблицы       
    def addTrafficCostRow(self):
        current_row = self.trafficcost_tableWidget.currentRow()+1
        self.trafficcost_tableWidget.insertRow(current_row)
        self.addrow(self.trafficcost_tableWidget, '0', current_row, 1)
        self.addrow(self.trafficcost_tableWidget, '0', current_row, 2)
        #self.addrow(self.trafficcost_tableWidget, True, current_row, 4, item_type='checkbox')
        #self.addrow(self.trafficcost_tableWidget, True, current_row, 5, item_type='checkbox')
        #self.addrow(self.trafficcost_tableWidget, True, current_row, 6, item_type='checkbox')
        
    
    def delTrafficCostRow(self):
        current_row = self.trafficcost_tableWidget.currentRow()
        
        id = self.getIdFromtable(self.trafficcost_tableWidget, current_row)
        if id!=-1:
            #self.connection.iddelete("DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=%d" % id)
            #self.connection.delete("DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=%d" % id)
            self.connection.iddelete(id, "billservice_traffictransmitnodes")
        self.trafficcost_tableWidget.removeRow(current_row)
        
        
    def addLimitRow(self):
        current_row = self.limit_tableWidget.rowCount()
        self.limit_tableWidget.insertRow(current_row)
        self.addrow(self.limit_tableWidget, True, current_row, 2, item_type='checkbox')

        #self.addrow(self.limit_tableWidget, True, current_row, 5, item_type='checkbox')
        #self.addrow(self.limit_tableWidget, True, current_row, 6, item_type='checkbox')
        #self.addrow(self.limit_tableWidget, True, current_row, 7, item_type='checkbox')

    
    def delLimitRow(self):
        current_row = self.limit_tableWidget.currentRow()
        id = self.getIdFromtable(self.limit_tableWidget, current_row)
        if id!=-1:
            self.connection.iddelete(id, "billservice_trafficlimit")
        self.limit_tableWidget.removeRow(current_row)

    def addOneTimeRow(self):
        current_row = self.onetime_tableWidget.rowCount()
        self.onetime_tableWidget.insertRow(current_row)
    
    def delOneTimeRow(self):
        current_row = self.onetime_tableWidget.currentRow()     
        id = self.getIdFromtable(self.onetime_tableWidget, current_row)
        
        if id!=-1:
            self.connection.iddelete(id, "billservice_onetimeservice")

        self.onetime_tableWidget.removeRow(current_row)

    def addTimeAccessRow(self):
        current_row = self.timeaccess_table.rowCount()
        self.timeaccess_table.insertRow(current_row)
        
    def addRadiusTrafficRow(self):
        current_row = self.tableWidget_radius_traffic_trafficcost.rowCount()
        self.tableWidget_radius_traffic_trafficcost.insertRow(current_row)

    def delRadiusTrafficRow(self):
        current_row = self.tableWidget_radius_traffic_trafficcost.rowCount() 
        id = self.getIdFromtable(self.tableWidget_radius_traffic_trafficcost, current_row)
        
        if id!=-1:
            self.connection.iddelete(id ,"billservice_radiustraffic")
            #TimeAccessNode.objects.get(id=id).delete()
    
        self.tableWidget_radius_traffic_trafficcost.removeRow(current_row)

        
    def delTimeAccessRow(self):
        current_row = self.timeaccess_table.currentRow()   
        id = self.getIdFromtable(self.timeaccess_table, current_row)
        
        if id!=-1:
            self.connection.iddelete(id ,"billservice_timeaccessnode")
            #TimeAccessNode.objects.get(id=id).delete()
    
        self.timeaccess_table.removeRow(current_row)

    def addPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.rowCount()
        self.prepaid_tableWidget.insertRow(current_row)
        
        #self.addrow(self.prepaid_tableWidget, True, current_row, 2, item_type='checkbox')
        #self.addrow(self.prepaid_tableWidget, True, current_row, 3, item_type='checkbox')
        
        #self.addrow(self.prepaid_tableWidget, True, current_row, 4, item_type='checkbox')
    
    def delPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.currentRow()  
        id = self.getIdFromtable(self.prepaid_tableWidget, current_row)
        
        if id!=-1:
            #d = Object()
            #d.prepaidtraffic_id = id
            #self.connection.delete(d, "billservice_prepaidtraffic_traffic_class")
            self.connection.iddelete(id, "billservice_prepaidtraffic")
            #PrepaidTraffic.objects.get(id=id).delete()
     
        self.prepaid_tableWidget.removeRow(current_row)

    def addSpeedRow(self):
        current_row = self.speed_table.rowCount()
        self.speed_table.insertRow(current_row)
    
    def delSpeedRow(self):
        current_row = self.speed_table.currentRow()
        id = self.getIdFromtable(self.speed_table, current_row)
        
        if id!=-1:
            self.connection.iddelete(id, "billservice_timespeed")
            #service.delete()    
        self.speed_table.removeRow(current_row)

                
    def addPeriodicalRow(self):
        current_row = self.periodical_tableWidget.rowCount()
        self.periodical_tableWidget.insertRow(current_row)
        self.addrow(self.periodical_tableWidget, ps_list[0], current_row, 6)
        self.addrow(self.periodical_tableWidget, '', current_row, 7)
        self.addrow(self.periodical_tableWidget, '', current_row, 3)
        #if QtGui.QMessageBox.question(self, u"Внимание!!!" , 
        #                                    u'''Вы хотите, чтобы по новой периодической услуге были поизведены списания с начала текущего расчётного периода?''', \
        #                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.No:
        #    self.periodical_tableWidget.item(current_row,5).created='now()'
        #else:
        #    self.periodical_tableWidget.item(current_row,5).created=None
        self.periodical_tableWidget.item(current_row,6).selected_id=0
        self.periodical_tableWidget.item(current_row,7).deactivated=None
        
        
    def delPeriodicalRow(self):
        current_row = self.periodical_tableWidget.currentRow()
        id = self.getIdFromtable(self.periodical_tableWidget, current_row)
        
        if id!=-1:
            #self.connection.iddelete(id, "billservice_periodicalservice")
            self.connection.sql("UPDATE billservice_periodicalservice SET deleted=True, deactivated=now() WHERE id=%s" % id)
            
        self.periodical_tableWidget.removeRow(current_row)

         
    def addAddonServiceRow(self):
        current_row = self.tableWidget_addonservices.rowCount()
        self.tableWidget_addonservices.insertRow(current_row)
        
        
    def delAddonServiceRow(self):
        current_row = self.tableWidget_addonservices.currentRow()
        id = self.getIdFromtable(self.tableWidget_addonservices, current_row)
        
        if id!=-1:
            self.connection.iddelete(id, "billservice_addonservicetarif")
  
        self.tableWidget_addonservices.removeRow(current_row)
        
    #-----------------------------
    def onAccessTypeChange(self, *args):
        if args[0] == "IPN":
            if self.ipn_for_vpn.isEnabled():
                self.ipn_for_vpn_state = self.ipn_for_vpn.checkState()
                self.ipn_for_vpn.setChecked(True)
                self.ipn_for_vpn.setDisabled(True)
        elif args[0] == "HotSpot":
            self.ipn_for_vpn_state = self.ipn_for_vpn.checkState()
            self.ipn_for_vpn.setChecked(False)
            self.ipn_for_vpn.setDisabled(True)
        else:
            if not self.ipn_for_vpn.isEnabled():
                self.ipn_for_vpn.setEnabled(True)
                self.ipn_for_vpn.setCheckState(self.ipn_for_vpn_state)

           
    #------------------tab actions         
    def timeaccessTabActivityActions(self):
        if self.time_access_service_checkbox.checkState()!=2:
            self.tab_radius_time.setDisabled(True)
            #self.tab_3.hide()
            #self.tabWidget.removeTab(3)
        else:
            self.tab_radius_time.setDisabled(False)
            #self.tab_3.sho
            #self.tabWidget.insertTab(3, self.tab_3,"")
            #self.retranslateUi()
    
    def radiusTrafficTabActivityActions(self):
        if self.radius_traffic_access_service_checkbox.checkState()!=2:
            self.tab_radius_traffic.setDisabled(True)
            #self.tab_3.hide()
            #self.tabWidget.removeTab(3)
        else:
            self.tab_radius_traffic.setDisabled(False)
            #self.tab_3.sho
            #self.tabWidget.insertTab(3, se
                               
    def transmitTabActivityActions(self):
        if self.transmit_service_checkbox.checkState()!=2:
            self.tab_4.setDisabled(True)
            #self.tabWidget.removeTab(2)
        else:
            self.tab_4.setDisabled(False)
            #self.tabWidget.insertTab(2, self.tab_4,"")
            #self.retranslateUi()
            
    def onetimeTabActivityActions(self):
        
        if self.onetime_services_checkbox.checkState()!=2:
            self.tab_6.setDisabled(True)
            #self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_6))

        else:
            self.tab_6.setDisabled(False)
            #self.tabWidget.insertTab(5, self.tab_6,"")
            #self.retranslateUi()
                        
    def periodicalServicesTabActivityActions(self):
        if self.periodical_services_checkbox.checkState()!=2:
            self.tab_5.setDisabled(True)
            #self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_5))
        else:
            self.tab_5.setDisabled(False)
            #self.tabWidget.insertTab(6, self.tab_5,"")
            #self.retranslateUi()
            
    def limitTabActivityActions(self):
        if self.limites_checkbox.checkState()!=2:
            self.tab_7.setDisabled(True)
            #self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_7))
        else:
            self.tab_7.setDisabled(False)
            #self.tabWidget.insertTab(7, self.tab_7,"")
            #self.retranslateUi()        
            #-------------------

    def addonservicesTabActivityActions(self):
        if self.checkBox_addon_services.checkState()!=2:
            self.tab_8.setDisabled(True)
            #self.tabWidget.removeTab(self.tabWidget.indexOf(self.tab_7))
        else:
            self.tab_8.setDisabled(False)
            #self.tabWidget.insertTab(7, self.tab_7,"")
            #self.retranslateUi()    


    #-----------------------------Обработка редактирования таблиц
    def prepaidTrafficEdit(self,y,x):
        if x==1:
            item = self.prepaid_tableWidget.item(y,x)
            try:
                default_id = item.id
            except:
                default_id=-1
            child = GroupsDialog(self.connection, default_id)
            
            if child.exec_()==1 and child.selected_group!=-1:
                group = self.connection.get_model(child.selected_group, "billservice_group")
                self.addrow(self.prepaid_tableWidget, group.name, y,x, id=group.id)
                if child.selected_group>0:
                    #self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.prepaid_tableWidget.resizeColumnsToContents()
                    self.prepaid_tableWidget.resizeRowsToContents()
        
        if x==2:
            item = self.prepaid_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Объём:", u"Введите количество предоплаченных мегабайт", default_text)        
           
            self.prepaid_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
 
 
    def speedEdit(self,y,x):
        if x==1:
            item = self.speed_table.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=self.connection.get_models("billservice_timeperiod"), selected_item = default_text )
            if child.exec_()==1:
                self.speed_table.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))
        if x in (2, 3, 4, 5, 6):
            item = self.speed_table.item(y,x)
            try:
                text = unicode(item.text())
            except:
                text=""
            if x==2:
                child = SpeedEditDialog(item=text, title=u"Максимальная скорость")
            if x==3:
                child = SpeedEditDialog(item=text, title=u"Гарантированная скорость")
            if x==4:
                child = SpeedEditDialog(item=text, title=u"Пиковая скорость")
            if x==5:
                child = SpeedEditDialog(item=text, title=u"Средняя скорость для достижения пика")
            if x==6:
                child = SpeedEditDialog(item=text, title=u"Время для подсчёта средней скорости")                                
                                
            if child.exec_()==1:
                self.speed_table.setItem(y,x, QtGui.QTableWidgetItem(child.resultstring))
            
        if x==7:
            item = self.speed_table.item(y,x)
            try:
                default_text=int(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getInteger(self, u"Приоритет", u"Введите приоритет от 1 до 8", default_text, 1, 8, 1)        
            
            self.speed_table.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))


    def limitClassEdit(self,y,x):
        if x==4:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_id = item.id
            except:
                default_id=-1
            child = GroupsDialog(self.connection, default_id)
            
            if child.exec_()==1 and child.selected_group!=-1:
                group = self.connection.get_model(child.selected_group, "billservice_group")
                self.addrow(self.limit_tableWidget, group.name, y,x, id=group.id)
                if child.selected_group>0:
                    #self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.limit_tableWidget.resizeColumnsToContents()
                    self.limit_tableWidget.resizeRowsToContents()
                    
        if x==3:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_models("billservice_settlementperiod"), selected_item = default_text )
            self.connection.commit()
            if child.exec_()==1:
                self.addrow(self.limit_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)

        if x==1:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QtGui.QInputDialog.getText(self,u"Введите название название", u"Название:", QtGui.QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[2]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            
            self.limit_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(text[0]))
             
        if x==5:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getInteger(self, u"Размер:", u"Введите размер лимита в МБ, после которого произойдёт отключение", default_text)        
           
            self.limit_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                
        if x==6:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
                       
            child = ComboBoxDialog(items=limit_actions, selected_item = default_text )
            self.connection.commit()
            if child.exec_()==1:
                self.addrow(self.limit_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)
            if child.selected_id==0:
                try:
                    self.limit_tableWidget.item(y, 7).setText("")
                    self.limit_tableWidget.item(y, 7).model=None
                except:
                    pass
                
        if x==7:

            if not self.limit_tableWidget.item(y,6): return
            if self.limit_tableWidget.item(y,6).id==0: return
            #print "self.limit_tableWidget.item(y,6).id", self.limit_tableWidget.item(y,6).id
            item = self.limit_tableWidget.item(y,x)
            #limit_id = unicode(self.limit_tableWidget.item(y,0).text())
            try:
                model = item.model
            except:
                model = None
            #print "speedlimit_model=", model
            #print "speedmodel=", model
            child = SpeedLimitDialog(self.connection, model)
            
            if child.exec_()==1 and child.model:
                self.addrow(self.limit_tableWidget, u"%s/%s %s/%s %s/%s %s/%s %s %s/%s" % (child.model.max_tx, child.model.max_rx, child.model.burst_tx, child.model.burst_rx, child.model.burst_treshold_tx, child.model.burst_treshold_rx, child.model.burst_time_tx, child.model.burst_time_rx, child.model.priority, child.model.min_tx, child.model.min_rx) , y,x)
                self.limit_tableWidget.item(y,x).model = child.model
                self.limit_tableWidget.resizeColumnsToContents()
                self.limit_tableWidget.resizeRowsToContents()
                    
    def oneTimeServicesEdit(self,y,x):
        if x==1:
            item = self.onetime_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QtGui.QInputDialog.getText(self,u"Введите название название", u"Название:", QtGui.QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[1]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            
            self.onetime_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(text[0]))        

        if x==2:
            item = self.onetime_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость разовой услуги", default_text)        
           
            self.onetime_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                

    def timeAccessServiceEdit(self,y,x):
        if x==1:
            item = self.timeaccess_table.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_models("billservice_timeperiod"), selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.timeaccess_table, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==2:
            item = self.timeaccess_table.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость", default_text,0,99999999,2)        
           
            self.timeaccess_table.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                
                                     
    def radiusTrafficEdit(self,y,x):
        if x==1:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Объём(МБ):", u"Введите объём трафика за расчётный период", default_text,0,99999999,2)        
           
            self.tableWidget_radius_traffic_trafficcost.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
        
        if x==2:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_models("billservice_timeperiod"), selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.tableWidget_radius_traffic_trafficcost, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==3:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите цену", default_text,0,99999999,2)        
           
            self.tableWidget_radius_traffic_trafficcost.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                                             
    def trafficCostCellEdit(self,y,x):
        
        #Стоимость за трафик
        [u'#', u'От МБ', u'До МБ', u'Группа', u'Время', u'Цена за МБ']
        if x==3:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_id = item.id
            except:
                default_id=-1
            child = GroupsDialog(self.connection, default_id)
            
            if child.exec_()==1 and child.selected_group!=-1:
                group = self.connection.get_model(child.selected_group, "billservice_group")
                self.addrow(self.trafficcost_tableWidget, group.name, y,x, id=group.id)
                if child.selected_group>0:
                    #self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                    self.trafficcost_tableWidget.resizeRowsToContents()
                    
                
        if x==4:
            try:
                models = self.trafficcost_tableWidget.item(y,x).models
            except:
                models = []
            child = CheckBoxDialog(all_items=self.connection.get_models("billservice_timeperiod"), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setItem(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                self.trafficcost_tableWidget.resizeColumnsToContents()
                self.trafficcost_tableWidget.resizeRowsToContents()

        if x==5:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Цена за МБ:", u"Введите цену", default_text,0,1000000,2)      
           
            self.trafficcost_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
            
        if x==1:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"От (МБ):", u"Укажите нижнюю границу в МБ, после которой настройки цены будут актуальны", default_text)        
           
            self.trafficcost_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
        
        if x==2:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            text = QtGui.QInputDialog.getDouble(self, u"До (МБ):", u"Укажите верхнюю границу в МБ, до которой настройки цены будут актуальны", default_text)        
            self.trafficcost_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))

    def periodicalServicesEdit(self,y,x):
        
        [u'#', u'Название', u'Период', u"Начало действия", u'Способ снятия', u'Стоимость', u"Условие", u"Отключить услугу с"]          
        if x==2:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=self.connection.get_models("billservice_settlementperiod"), selected_item = default_text )
            if child.exec_()==1:
                #self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))
                #print "selected_id", child.selected_id
                self.addrow(self.periodical_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)

        if x==1:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QtGui.QInputDialog.getText(self,u"Введите название", u"Название:", QtGui.QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[1]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            elif text[1]==False:
                return
            
            self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(text[0]))

        if x==4:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=cash_types, selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.periodical_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)
             
        if x==5:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Цена:", u"Введите цену", default_text)        
           
            self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))


        if x==6:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""


            child = ComboBoxDialog(items=ps_conditions, selected_item = default_text )
            self.connection.commit()
            if child.exec_()==1:
                self.periodical_tableWidget.item(y,x).setText(child.comboBox.currentText())
                self.periodical_tableWidget.item(y,x).selected_id=child.selected_id
            #print "created=", self.periodical_tableWidget.item(y,x).selected_id


        if x==3:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.created
            except:
                default_text = None
                

            child = PSCreatedForm(date = default_text )
            #self.connection.commit()
            if child.exec_()==1:

                if child.date:
                    self.periodical_tableWidget.item(y,x).setText(child.date.strftime(strftimeFormat))
                else:
                    self.periodical_tableWidget.item(y,x).setText(u"С начала расчётного периода")
                self.periodical_tableWidget.item(y,x).created=child.date
            #print "created=", self.periodical_tableWidget.item(y,x).selected_id
            
        if x==7:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.deactivated
            except:
                default_text = None
                

            child = PSCreatedForm(date = default_text, only_date=True )
            #self.connection.commit()
            if child.exec_()==1:

                if child.date:
                    self.periodical_tableWidget.item(y,x).setText(child.date.strftime(strftimeFormat))
                else:
                    self.periodical_tableWidget.item(y,x).setText(u"")
                self.periodical_tableWidget.item(y,x).deactivated=child.date
            #print "created=", self.periodical_tableWidget.item(y,x).selected_id
            
   
    
       
    
    
    def addonserviceEdit(self,y,x):

        if x==1:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text = item.id
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_models("billservice_addonservice"), selected_item = default_text )

            if child.exec_()==1:
                self.addrow(self.tableWidget_addonservices, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==2:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getInteger(self, u"Количество активаций:", u"Количество активаций", default_text)        
           
            #self.tableWidget_addonservices.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
            self.addrow(self.tableWidget_addonservices, text[0], y, x, id=unicode(text[0]))
            
        if x==3:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text = item.id
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_models("billservice_settlementperiod"), selected_item = default_text )
            
            if child.exec_()==1:
                self.addrow(self.tableWidget_addonservices, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  
            
    
    def getIdFromtable(self, tablewidget, row=0):
        tmp=tablewidget.item(row, 0)
        if tmp is not None:
            return int(tmp.text())
        return -1
        
    
    def fixtures(self):
        
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                #print "self.model.settlement_period_id", self.model.settlement_period_id
                settlement_period=self.connection.get_model(self.model.settlement_period_id, "billservice_settlementperiod")
                self.sp_groupbox.setChecked(True)
                #if settlement_period.autostart==True:
                    
                #    self.sp_type_edit.setChecked(True)
                        
               #     settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=True")
                
                #else:
            else:
                self.sp_groupbox.setChecked(False)
        settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod")
        for sp in settlement_periods:
            self.sp_name_edit.addItem(sp.name)
            
        #print settlement_period.name




        access_types = ["PPTP", "PPPOE", "IPN", "HotSpot", 'lISG', "DHCP"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = self.connection.get_models("billservice_timeperiod")
        
        for at in access_time:
            self.access_time_edit.addItem(unicode(at.name))

        systemgroups = self.connection.get_models("billservice_systemgroup")
        

        self.comboBox_system_group.addItem(unicode(u"--Доступно всем--"))
        self.comboBox_system_group.setItemData(0, QtCore.QVariant(0))
        i=1
        for systemgroup in systemgroups:
            self.comboBox_system_group.addItem(unicode(systemgroup.name))
            self.comboBox_system_group.setItemData(i, QtCore.QVariant(systemgroup.id))
            i+=1
        
        
        i=0
        for round_type in round_types:
            self.comboBox_radius_time_rounding.addItem(unicode(round_type.name))
            self.comboBox_radius_time_rounding.setItemData(i, QtCore.QVariant(round_type.id))
            self.comboBox_radius_traffic_rounding.addItem(unicode(round_type.name))
            self.comboBox_radius_traffic_rounding.setItemData(i, QtCore.QVariant(round_type.id))
            i+=1        

        
        
        i=0
        for direction_type in direction_types:
            self.comboBox_radius_traffic_direction.addItem(unicode(direction_type.name))
            self.comboBox_radius_traffic_direction.setItemData(i, QtCore.QVariant(direction_type.id))
            self.comboBox_radius_traffic_prepaid_direction.addItem(unicode(direction_type.name))
            self.comboBox_radius_traffic_prepaid_direction.setItemData(i, QtCore.QVariant(direction_type.id))
            i+=1  
                    
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                self.sp_name_edit.setCurrentIndex(self.sp_name_edit.findText(settlement_period.name, QtCore.Qt.MatchCaseSensitive))
                
            try:
                if self.model.systemgroup_id:
                    self.comboBox_system_group.setCurrentIndex(self.comboBox_system_group.findData(QtCore.QVariant(self.model.systemgroup_id)))
            except Exception, e:
                print e

                
            self.require_tarif_cost_edit.setCheckState(self.model.require_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.tarif_status_edit.setCheckState(self.model.active == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.checkBoxAllowExpressPay.setChecked(bool(self.model.allow_express_pay))
            self.tarif_name_edit.setText(self.model.name)
            self.tarif_cost_edit.setText(unicode(self.model.cost))
            self.tarif_description_edit.setText(self.model.description)
            self.reset_tarif_cost_edit.setCheckState(self.model.reset_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.ps_null_ballance_checkout_edit.setCheckState(self.model.ps_null_ballance_checkout == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            access_parameters = self.connection.get_model(self.model.access_parameters_id, "billservice_accessparameters")
            #Speed default parameters
            try:
                max_limit_in, max_limit_out = access_parameters.max_limit.split("/")
            except:
                max_limit_in, max_limit_out = "",""
            
            self.speed_max_in_edit.setText(max_limit_in)
            self.speed_max_out_edit.setText(max_limit_out)
            
            try:
                min_limit_in, min_limit_out = access_parameters.min_limit.split("/")
            except:
                min_limit_in, min_limit_out = "",""

            self.speed_min_in_edit.setText(min_limit_in)
            self.speed_min_out_edit.setText(min_limit_out)

            try:
                burst_limit_in, burst_limit_out = access_parameters.burst_limit.split("/")
            except:
                burst_limit_in, burst_limit_out = "",""

            self.speed_burst_in_edit.setText(burst_limit_in)
            self.speed_burst_out_edit.setText(burst_limit_out)

            try:
                burst_treshold_in, burst_treshold_out = access_parameters.burst_treshold.split("/")
            except:
                burst_treshold_in, burst_treshold_out = "",""

            self.speed_burst_treshold_in_edit.setText(burst_treshold_in)
            self.speed_burst_treshold_out_edit.setText(burst_treshold_out)

            try:
                burst_time_in, burst_time_out = access_parameters.burst_time.split("/")
            except:
                burst_time_in, burst_time_out = "",""

            self.speed_burst_time_in_edit.setText(burst_time_in)
            self.speed_burst_time_out_edit.setText(burst_time_out)

            access_parameters = self.connection.get("""SELECT accessparameters.*,timeperiod.name as time_name  FROM billservice_accessparameters as accessparameters 
            JOIN billservice_timeperiod as timeperiod ON timeperiod.id=accessparameters.access_time_id
            WHERE accessparameters.id=%d""" % self.model.access_parameters_id)
            self.speed_priority_edit.setText(unicode(access_parameters.priority))   
            
            #self.speed_table.clear()
            speeds = self.connection.sql("""SELECT timespeed.*, timeperiod.name as time_name FROM billservice_timespeed as timespeed 
            JOIN billservice_timeperiod as timeperiod ON timeperiod.id=timespeed.time_id
            WHERE timespeed.access_parameters_id=%d""" % access_parameters.id)
            #speeds = self.model.access_parameters.access_speed.all()
            self.speed_table.setRowCount(len(speeds))
            i=0
            for speed in speeds:
                self.addrow(self.speed_table, speed.id,i, 0)
                self.addrow(self.speed_table, speed.time_name,i, 1)
                self.addrow(self.speed_table, speed.max_limit,i, 2)
                self.addrow(self.speed_table, speed.min_limit,i, 3)
                self.addrow(self.speed_table, speed.burst_limit,i, 4)
                self.addrow(self.speed_table, speed.burst_treshold,i, 5)
                self.addrow(self.speed_table, speed.burst_time,i, 6)
                self.addrow(self.speed_table, u"%s" % speed.priority, i, 7)
                i+=1
            self.speed_table.setColumnHidden(0, True)
            self.speed_table.resizeColumnsToContents()
            
            #Time Access Service
            #print "self.model.time_access_service_id=", self.model.time_access_service_id
            if not self.model.isnull('time_access_service_id'):
                self.time_access_service_checkbox.setChecked(True)
                time_access_service = self.connection.get_model(self.model.time_access_service_id, "billservice_timeaccessservice")
                self.prepaid_time_edit.setValue(time_access_service.prepaid_time)
                self.spinBox_radius_time_tarification_step.setValue(time_access_service.tarification_step)
                self.comboBox_radius_time_rounding.setCurrentIndex(self.comboBox_radius_time_rounding.findData(QtCore.QVariant(time_access_service.rounding)))
                self.reset_time_checkbox.setCheckState(time_access_service.reset_time == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                #nodes = self.model.time_access_service.time_access_nodes.all()
                nodes = self.connection.sql("""SELECT timeaccessnode.*, timeperiod.name as time_period_name, timeperiod.id as timeperiod_id FROM billservice_timeaccessnode as timeaccessnode  
                JOIN billservice_timeperiod as timeperiod ON timeperiod.id=timeaccessnode.time_period_id
                WHERE timeaccessnode.time_access_service_id=%d""" % self.model.time_access_service_id)
                self.timeaccess_table.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.timeaccess_table, node.id,i, 0)
                    self.addrow(self.timeaccess_table, node.time_period_name,i, 1, 'combobox', node.timeperiod_id)
                    self.addrow(self.timeaccess_table, node.cost,i, 2)
                    i+=1                
            self.timeaccess_table.setColumnHidden(0, True)

            if not self.model.isnull('radius_traffic_transmit_service_id'):
                self.radius_traffic_access_service_checkbox.setChecked(True)
                radius_traffic_transmit_service = self.connection.get_model(self.model.radius_traffic_transmit_service_id, "billservice_radiustraffic")
                self.spinBox_radius_traffic_prepaid_volume.setValue(int(radius_traffic_transmit_service.prepaid_value/(1024*1024)))
                self.comboBox_radius_traffic_prepaid_direction.setCurrentIndex(self.comboBox_radius_traffic_prepaid_direction.findData(QtCore.QVariant(radius_traffic_transmit_service.prepaid_direction)))
                self.spinBox_radius_traffic_tarification_step.setValue(radius_traffic_transmit_service.tarification_step)
                self.comboBox_radius_traffic_direction.setCurrentIndex(self.comboBox_radius_traffic_direction.findData(QtCore.QVariant(radius_traffic_transmit_service.direction)))
                self.comboBox_radius_traffic_rounding.setCurrentIndex(self.comboBox_radius_traffic_rounding.findData(QtCore.QVariant(radius_traffic_transmit_service.rounding)))
                
                #self.checkBox_radius_traffic_reset_prepaidtraffic.setValue(rad.prepaid_time)
                self.checkBox_radius_traffic_reset_prepaidtraffic.setCheckState(radius_traffic_transmit_service.reset_prepaid_traffic == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                #nodes = self.model.time_access_service.time_access_nodes.all()
                
                nodes = self.connection.sql("""SELECT node.id, node.value, timeperiod.name as time_period_name, timeperiod.id as timeperiod_id, node.cost FROM billservice_radiustrafficnode as node  
                JOIN billservice_timeperiod as timeperiod ON timeperiod.id=node.timeperiod_id
                WHERE node.radiustraffic_id=%d ORDER BY value ASC""" % self.model.radius_traffic_transmit_service_id)
                self.tableWidget_radius_traffic_trafficcost.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.id,i, 0)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.value,i, 1)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.time_period_name,i, 2, 'combobox', node.timeperiod_id)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.cost,i, 3)
                    i+=1                
                self.tableWidget_radius_traffic_trafficcost.setColumnHidden(0, True)
                        
            #PeriodicalService
            periodical_services = self.connection.sql("""SELECT periodicalservice.*, settlementperiod.name as settlement_period_name
            FROM billservice_periodicalservice as periodicalservice
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id = periodicalservice.settlement_period_id
            WHERE periodicalservice.tarif_id = %d   
            """ % self.model.id)
            if len(periodical_services)>0:
                self.periodical_services_checkbox.setChecked(True)
                nodes = periodical_services
                self.periodical_tableWidget.setRowCount(len(nodes))
                i=0
                
                for node in nodes:
                    self.addrow(self.periodical_tableWidget, node.id,i, 0)
                    self.addrow(self.periodical_tableWidget, node.name,i, 1)
                    self.addrow(self.periodical_tableWidget, node.settlement_period_name,i, 2, 'combobox', node.settlement_period_id)
                    self.addrow(self.periodical_tableWidget, node.cash_method, i, 4)
                    self.addrow(self.periodical_tableWidget, node.cost,i, 5)
                    self.addrow(self.periodical_tableWidget, ps_list[node.condition],i, 6)
                    self.periodical_tableWidget.item(i, 6).selected_id = node.condition
                    if node.created:
                        self.addrow(self.periodical_tableWidget, node.created.strftime(strftimeFormat),i, 3)
                    else:
                        self.addrow(self.periodical_tableWidget, u"С начала расчётного периода",i, 3)
                    self.periodical_tableWidget.item(i, 3).created = node.created
                    try:
                        self.addrow(self.periodical_tableWidget, node.deactivated.strftime(strftimeFormat),i, 7)
                    except:
                        self.addrow(self.periodical_tableWidget, '',i, 7)
                        self.periodical_tableWidget.item(i, 7).deactivated = node.deactivated
                    #print "node created", node.created
                    i+=1                   
            self.periodical_tableWidget.setColumnHidden(0, True)
            
            #Onetime Service
            onetime_services = self.connection.sql("""SELECT onetimeservice.* FROM billservice_onetimeservice as onetimeservice
            WHERE onetimeservice.tarif_id=%d
             """ % self.model.id)
            if len(onetime_services)>0:
                self.onetime_services_checkbox.setChecked(True)
                nodes = onetime_services
                self.onetime_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.onetime_tableWidget, node.id,i, 0)
                    self.addrow(self.onetime_tableWidget, node.name,i, 1)
                    self.addrow(self.onetime_tableWidget, node.cost,i, 2)
                    i+=1   
            self.onetime_tableWidget.setColumnHidden(0, True)
            
            #Limites
            traffic_limites = self.connection.sql(""" SELECT trafficlimit.*, settlementperiod.name as settlement_period_name, settlementperiod.id as settlementperiod_id, gr.name as group_name
            FROM billservice_trafficlimit as trafficlimit
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id=trafficlimit.settlement_period_id
            LEFT JOIN billservice_group AS gr ON gr.id=trafficlimit.group_id
            WHERE trafficlimit.tarif_id=%d
            """ % self.model.id)
             
            
            if len(traffic_limites)>0:

                self.limites_checkbox.setChecked(True)
                nodes = traffic_limites
                self.limit_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    speedmodel = self.connection.sql("SELECT * FROM billservice_speedlimit WHERE limit_id=%s" % node.id)
                    self.connection.commit()
                    self.addrow(self.limit_tableWidget, node.id,i, 0)
                    self.addrow(self.limit_tableWidget, node.name,i, 1)
                    self.addrow(self.limit_tableWidget, node.mode,i, 2, item_type='checkbox')
                    self.addrow(self.limit_tableWidget, node.settlement_period_name,i, 3, item_type='combobox', id=node.settlementperiod_id)
                    self.addrow(self.limit_tableWidget, node.group_name,i, 4, id=node.group_id)
                    #self.limit_tableWidget.setItem(i,4, CustomWidget(parent=self.limit_tableWidget, models=traffic_classes))
                    self.addrow(self.limit_tableWidget, unicode(node.size/(1048576)),i, 5)
                    self.addrow(self.limit_tableWidget, la_list[node.action],i, 6, id = node.action)
                    if len(speedmodel)>0:
                        #print "speedmodel", speedmodel
                        self.addrow(self.limit_tableWidget, u"%s/%s %s/%s %s/%s %s/%s %s %s/%s" % (speedmodel[0].max_tx, speedmodel[0].max_rx, speedmodel[0].burst_tx, speedmodel[0].burst_rx, speedmodel[0].burst_treshold_tx, speedmodel[0].burst_treshold_rx, speedmodel[0].burst_time_tx, speedmodel[0].burst_time_rx, speedmodel[0].priority, speedmodel[0].min_tx, speedmodel[0].min_rx),i, 7)
                        self.limit_tableWidget.item(i, 7).model = speedmodel[0]
                        #for x in speedmodel[0].__dict__:
                        #    print x, speedmodel[0].__dict__[x]
                            
                    #self.addrow(self.limit_tableWidget, node.in_direction, i, 5, item_type='checkbox')
                    #self.addrow(self.limit_tableWidget, node.out_direction, i, 6, item_type='checkbox')
                    #self.addrow(self.limit_tableWidget, node.transit_direction, i, 7, item_type='checkbox')
                    
                    i+=1
                    self.limit_tableWidget.resizeColumnsToContents()
                    self.limit_tableWidget.resizeRowsToContents()
            self.limit_tableWidget.setColumnHidden(0, True)
            
            
            #billservice_addonservicetarif
            #AddonServices
            addon_services = self.connection.sql(""" SELECT addonservicetarif.*, settlementperiod.name as settlement_period_name, settlementperiod.id as settlementperiod_id, adds.name as addonservice_name, adds.id as addonservice_id
            FROM billservice_addonservicetarif as addonservicetarif
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id=addonservicetarif.activation_count_period_id
            LEFT JOIN billservice_addonservice AS adds ON adds.id=addonservicetarif.service_id
            WHERE addonservicetarif.tarif_id=%d
            """ % self.model.id)
             
            self.connection.commit()
            if len(addon_services)>0:

                self.checkBox_addon_services.setChecked(True)
                nodes = addon_services
                self.tableWidget_addonservices.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    
                    self.addrow(self.tableWidget_addonservices, node.id,i, 0)
                    self.addrow(self.tableWidget_addonservices, node.addonservice_name,i, 1, id=node.addonservice_id)
                    self.addrow(self.tableWidget_addonservices, node.activation_count if node.activation_count!=0  else 'unlimited',i, 2, id = node.activation_count)
                    self.addrow(self.tableWidget_addonservices, node.settlement_period_name,i, 3, id= node.settlementperiod_id)
                    
                    i+=1
                    self.tableWidget_addonservices.resizeColumnsToContents()
                    self.tableWidget_addonservices.resizeRowsToContents()
            self.tableWidget_addonservices.setColumnHidden(0, True)
                        
            
            #print "self.model.traffic_transmit_service_id=", self.model.traffic_transmit_service_id 
            #Prepaid Traffic
            if not self.model.isnull('traffic_transmit_service_id'):
                self.transmit_service_checkbox.setChecked(True)
                prepaid_traffic = self.connection.sql("""SELECT prepaidtraffic.*, (SELECT name FROM billservice_group WHERE id=prepaidtraffic.group_id) as group_name FROM billservice_prepaidtraffic as prepaidtraffic WHERE prepaidtraffic.traffic_transmit_service_id=%d""" % self.model.traffic_transmit_service_id)
                #print 'self.model.traffic_transmit_service_id', self.model.traffic_transmit_service_id
                if len(prepaid_traffic)>0:
                    nodes = prepaid_traffic
                    #self.model.traffic_transmit_service.prepaid_traffic.all()
                    #print nodes
                    self.prepaid_tableWidget.setRowCount(len(nodes))
                    i=0
                    for node in nodes:
              
                        self.addrow(self.prepaid_tableWidget, node.id,i, 0)
                        self.addrow(self.prepaid_tableWidget, node.group_name,i, 1, id=node.group_id)
                        #self.prepaid_tableWidget.setItem(i,1, CustomWidget(parent=self.prepaid_tableWidget, models=traffic_classes))

                        #self.addrow(self.prepaid_tableWidget, node.in_direction, i, 2, item_type='checkbox')
                        #self.addrow(self.prepaid_tableWidget, node.out_direction, i, 3, item_type='checkbox')
                        #self.addrow(self.prepaid_tableWidget, node.transit_direction, i, 4, item_type='checkbox')
                        
                        self.addrow(self.prepaid_tableWidget, float(node.size)/(1048576),i, 2)
                        i+=1       
                    
                    self.prepaid_tableWidget.resizeRowsToContents() 
                         
                self.prepaid_tableWidget.setColumnHidden(0, True)
                
                
                traffic_transmit_nodes = self.connection.sql("""
                SELECT traffictransmitnodes.* FROM billservice_traffictransmitnodes as traffictransmitnodes
                WHERE traffictransmitnodes.traffic_transmit_service_id=%d ORDER BY edge_value ASC
                """ % self.model.traffic_transmit_service_id)
                #print "traffic_transmit_nodes=", traffic_transmit_nodes
                #print "traffic_transmit_service_id=", self.model.traffic_transmit_service_id
               
                if len(traffic_transmit_nodes)>0:
                    traffic_transmit_service = self.connection.get_model(self.model.traffic_transmit_service_id, "billservice_traffictransmitservice")
                    self.reset_traffic_edit.setCheckState(traffic_transmit_service.reset_traffic == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                    nodes = traffic_transmit_nodes
                    self.trafficcost_tableWidget.setRowCount(len(nodes))
                    i = 0
                    for node in nodes:
                        group = self.connection.sql(""" 
                        SELECT name FROM billservice_group WHERE id=%d
                        """ % node.group_id)[0]
              
                        
                        
                        time_nodes = self.connection.sql(""" 
                        SELECT timeperiod.* FROM billservice_timeperiod as timeperiod
                        JOIN billservice_traffictransmitnodes_time_nodes as tn ON tn.timeperiod_id=timeperiod.id
                        WHERE tn.traffictransmitnodes_id=%d  
                        """ % node.id)
                        
                        #print node.id
                        self.addrow(self.trafficcost_tableWidget, node.id, i, 0)
                        self.addrow(self.trafficcost_tableWidget, node.edge_value/(1024*1024), i, 1)
                        self.addrow(self.trafficcost_tableWidget, node.edge_end, i, 2)
                        self.addrow(self.trafficcost_tableWidget, group.name, i, 3, id=node.group_id)
                        self.trafficcost_tableWidget.setItem(i,4, CustomWidget(parent=self.trafficcost_tableWidget, models=time_nodes))
                        self.addrow(self.trafficcost_tableWidget, node.cost, i, 5)
                        i+=1
                        
                    self.trafficcost_tableWidget.resizeRowsToContents()
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                    self.trafficcost_tableWidget.setColumnHidden(0, True)
            if access_parameters.access_type == 'IPN':
                self.access_type_edit.setDisabled(True)
                self.ipn_for_vpn.setDisabled(True)
            elif access_parameters.access_type == 'HotSpot':
                self.access_type_edit.setDisabled(True)
                self.ipn_for_vpn.setDisabled(True)
                self.ipn_for_vpn.setChecked(False)
            elif access_parameters.access_type == 'lISG':
                self.access_type_edit.setDisabled(True)
                self.ipn_for_vpn.setDisabled(False)
            else:
                self.access_type_edit.removeItem(3)
                self.access_type_edit.removeItem(2)
            self.access_type_edit.setCurrentIndex(self.access_type_edit.findText(access_parameters.access_type, QtCore.Qt.MatchCaseSensitive))
            self.access_time_edit.setCurrentIndex(self.access_time_edit.findText(access_parameters.time_name, QtCore.Qt.MatchCaseSensitive))
            self.ipn_for_vpn.setChecked(access_parameters.ipn_for_vpn)
        self.timeaccessTabActivityActions()
        self.transmitTabActivityActions()
        self.onetimeTabActivityActions()
        self.periodicalServicesTabActivityActions()
        self.radiusTrafficTabActivityActions()
        self.limitTabActivityActions()
        self.addonservicesTabActivityActions()
        self.trafficcost_tableWidget.resizeRowsToContents()
        self.trafficcost_tableWidget.resizeColumnsToContents()
        self.connection.commit()
        
        #self.trafficcost_tableWidget.resizeRowsToContents()

    def accept(self):
        if self.model:
            model=copy.deepcopy(self.model)
            access_parameters = Object()
            access_parameters.id=self.model.access_parameters_id
            access_parameters = self.connection.get(access_parameters.get("billservice_accessparameters"))
            self.connection.commit()
            previous_ipn_for_vpn_state = access_parameters.ipn_for_vpn
        else:
            model=Object()
            access_parameters = Object()
            previous_ipn_for_vpn_state = False
            
        if unicode(self.tarif_name_edit.text())=="":
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не указали название тарифного плана")
            return

        if unicode(self.access_time_edit.currentText())=="":
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не выбрали разрешённый период доступа")
            return

        if (unicode(self.access_time_edit.currentText()) == 'IPN') and self.ipn_for_vpn.checkState()==2:
            QtGui.QMessageBox.warning(self, u"Ошибка", u"'Производить IPN действия' может быть выбрано только для VPN планов")
            return

        if self.sp_groupbox.isChecked()==False and (self.prepaid_tableWidget.rowCount()>0 or self.reset_traffic_edit.isChecked()==True):
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного трафика необходимо указать расчётный период")
            return

        if self.sp_groupbox.isChecked()==False and (self.spinBox_radius_traffic_prepaid_volume.value()!=0 or self.checkBox_radius_traffic_reset_prepaidtraffic.isChecked()==True):
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного RADIUS трафика необходимо указать расчётный период")
            return

        if self.sp_groupbox.isChecked()==False and (self.reset_time_checkbox.isChecked()==True or self.prepaid_time_edit.value()!=0):
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного времени необходимо указать расчётный период")
            return
        
        try:
            
            model.name = unicode(self.tarif_name_edit.text())
            
            model.description = unicode(self.tarif_description_edit.toPlainText())
            
            model.ps_null_ballance_checkout = self.ps_null_ballance_checkout_edit.checkState()==2
            
            model.active = self.tarif_status_edit.checkState()==2
            model.allow_express_pay = self.checkBoxAllowExpressPay.checkState()==2
            
            access_parameters.access_type = unicode(self.access_type_edit.currentText())
            access_parameters.access_time_id = self.connection.get("SELECT * FROM billservice_timeperiod WHERE name='%s'" % unicode(self.access_time_edit.currentText())).id
            access_parameters.max_limit = u"%s/%s" % (self.speed_max_in_edit.text() or 0, self.speed_max_out_edit.text() or 0)
            access_parameters.min_limit = u"%s/%s" % (self.speed_min_in_edit.text() or 0, self.speed_min_out_edit.text() or 0)
            access_parameters.burst_limit = u"%s/%s" % (self.speed_burst_in_edit.text() or 0, self.speed_burst_out_edit.text() or 0)
            access_parameters.burst_treshold = u"%s/%s" % (self.speed_burst_treshold_in_edit.text() or 0, self.speed_burst_treshold_out_edit.text() or 0)
            access_parameters.burst_time = u"%s/%s" % (self.speed_burst_time_in_edit.text() or 0, self.speed_burst_time_out_edit.text() or 0)
            access_parameters.priority = unicode(self.speed_priority_edit.text()) or 8
            access_parameters.ipn_for_vpn = self.ipn_for_vpn.checkState()==2
            
            if check_speed([access_parameters.max_limit, access_parameters.burst_limit, access_parameters.burst_treshold, access_parameters.burst_time, access_parameters.priority, access_parameters.min_limit])==False:
                QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка в настройках скорости")
#                print 1
                self.connection.rollback()
                return              

            model.access_parameters_id=self.connection.save(access_parameters, "billservice_accessparameters")
            
            gr_id = self.comboBox_system_group.itemData(self.comboBox_system_group.currentIndex()).toInt()[0]
            model.systemgroup_id = None if gr_id == 0 else gr_id
            self.connection.commit()
            #Таблица скоростей
            
            for i in xrange(0, self.speed_table.rowCount()):
                id = self.getIdFromtable(self.speed_table, i)
                if id!=-1:
                    #Если такая запись уже есть
                    speed = self.connection.get_model(id, "billservice_timespeed")
                else:
                    #Иначе создаём новую
                    speed = Object()
                speed.access_parameters_id=model.access_parameters_id
    
                try:
                    speed.max_limit = u"%s" % self.speed_table.item(i,2).text()
                except:
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не указали максимальную скорость")
                    self.connection.rollback()
                    return
                
                try:
                    speed.min_limit = u"%s" % self.speed_table.item(i,3).text() or ''
                except:
                    speed.min_limit=""
                try:
                    speed.burst_limit = u"%s" % self.speed_table.item(i,4).text() or ''
                except:
                    speed.burst_limit = ""
                try:
                    speed.burst_treshold = u"%s" % self.speed_table.item(i,5).text() or ''
                except:
                    speed.burst_treshold = ""
                try:
                    speed.burst_time = u"%s" % self.speed_table.item(i,6).text() or ''
                except:
                    speed.burst_time = ""
                try:
                    speed.priority = unicode(self.speed_table.item(i,7).text()) or 8
                except:
                    speed.priority = 8
                
                if speed.max_limit=="" and speed.priority==8 and (speed.min_limit!="" or speed.burst_limit!="" or speed.burst_treshold!="" or speed.burst_time!=""):
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"Проверьте настройки скорости в таблице")
                    self.connection.rollback()
                    return                 
    
                if unicode(self.speed_table.item(i,1).text())=="":
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"Укажите периоды времени для настроек скорости")
                    self.connection.rollback()
                    return
                
                speed.time_id = self.connection.get("SELECT * FROM billservice_timeperiod WHERE name='%s'" % unicode(self.speed_table.item(i,1).text())).id
                #try:
                if check_speed([speed.max_limit, speed.burst_limit, speed.burst_treshold, speed.burst_time, speed.priority, speed.min_limit])==False:
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка в настройках скорости")
                    #print 1
                    self.connection.rollback()
                    return    
                #except:
                #    print "speed compare error"
                self.connection.save(speed, "billservice_timespeed")
            
            #Период
            sp=unicode(self.sp_name_edit.currentText())
            if self.sp_groupbox.isChecked()==True and sp!='':
                model.settlement_period_id = self.connection.get( "SELECT * FROM billservice_settlementperiod WHERE name='%s'" % sp).id
                model.cost = unicode(self.tarif_cost_edit.text()) or 0
                model.reset_tarif_cost = self.reset_tarif_cost_edit.checkState()==2
                model.require_tarif_cost = self.require_tarif_cost_edit.checkState()==2
                
            else:
                model.settlement_period_id=None
                model.reset_tarif_cost=False
                model.require_tarif_cost = False
                model.cost = 0

            model.id = self.connection.save(model, "billservice_tariff")


            #Доступ по времени
            
            if self.time_access_service_checkbox.checkState()==2:
                    
                if not model.isnull('time_access_service_id'):
                    time_access_service = self.connection.get_model(self.model.time_access_service_id, "billservice_timeaccessservice" )
                else:
                    time_access_service=Object()
                #print 1
                time_access_service.reset_time = self.reset_time_checkbox.checkState()==2
                time_access_service.prepaid_time = unicode(self.prepaid_time_edit.text())
                time_access_service.rounding = self.comboBox_radius_time_rounding.itemData(self.comboBox_radius_time_rounding.currentIndex()).toInt()[0]
                time_access_service.tarification_step = unicode(self.spinBox_radius_time_tarification_step.value())


                
                model.time_access_service_id = self.connection.save(time_access_service, 'billservice_timeaccessservice')
                
                for i in xrange(0, self.timeaccess_table.rowCount()):
                    #print "pre save"
                    if self.timeaccess_table.item(i,1)==None or self.timeaccess_table.item(i,2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки оплаты за время")
                        self.connection.rollback()
                        return

                        
                    #print "post save"
                    id = self.getIdFromtable(self.timeaccess_table, i)
                    if id!=-1:
                        time_access_node = self.connection.get_model(id, "billservice_timeaccessnode")
                    else:
                        time_access_node = Object()
                    
                    time_access_node.time_access_service_id=model.time_access_service_id
                    
                    time_access_node.time_period_id = self.timeaccess_table.item(i,1).id
                    time_access_node.cost = unicode(self.timeaccess_table.item(i,2).text())
                    self.connection.save(time_access_node, "billservice_timeaccessnode")
            
            elif self.time_access_service_checkbox.checkState()==0 and model.hasattr("time_access_service_id"):
                if  not model.isnull("time_access_service_id"):
                    
                    self.connection.iddelete(self.model.time_access_service_id, "billservice_timeaccessnode" )
                    
                    time_access_service_id=model.time_access_service_id
                    model.time_access_service_id=None
                    self.connection.save(model, "billservice_tariff")
                    self.connection.iddelete(time_access_service_id, "billservice_timeaccessservice")
                    
                    model.time_access_service_id = None
            
                else:
                    model.time_access_service_id = None
                    
                    
            #RADIUS траффик
            if self.radius_traffic_access_service_checkbox.checkState()==2:
                    
                if not model.isnull('radius_traffic_transmit_service_id'):
                    radius_traffic_service = self.connection.get_model(self.model.radius_traffic_transmit_service_id, "billservice_radiustraffic" )
                else:
                    radius_traffic_service=Object()
                #print 1
                radius_traffic_service.reset_prepaid_traffic = self.checkBox_radius_traffic_reset_prepaidtraffic.checkState()==2
                radius_traffic_service.prepaid_value = unicode(self.spinBox_radius_traffic_prepaid_volume.value()*1024*1024)
                radius_traffic_service.direction = self.comboBox_radius_traffic_direction.itemData(self.comboBox_radius_traffic_direction.currentIndex()).toInt()[0]
                radius_traffic_service.prepaid_direction = self.comboBox_radius_traffic_prepaid_direction.itemData(self.comboBox_radius_traffic_prepaid_direction.currentIndex()).toInt()[0]
                radius_traffic_service.rounding = self.comboBox_radius_traffic_rounding.itemData(self.comboBox_radius_traffic_rounding.currentIndex()).toInt()[0]
                radius_traffic_service.tarification_step = unicode(self.spinBox_radius_traffic_tarification_step.value())
                model.radius_traffic_transmit_service_id = self.connection.save(radius_traffic_service, 'billservice_radiustraffic')
                
                for i in xrange(0, self.tableWidget_radius_traffic_trafficcost.rowCount()):
                    #print "pre save"
                    if self.tableWidget_radius_traffic_trafficcost.item(i,1)==None or self.tableWidget_radius_traffic_trafficcost.item(i,2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки оплаты за radius трафик")
                        self.connection.rollback()
                        return
 
                    #print "post save"
                    id = self.getIdFromtable(self.tableWidget_radius_traffic_trafficcost, i)
                    if id!=-1:
                        radius_traffic_node = self.connection.get_model(id, "billservice_radiustrafficnode")
                    else:
                        radius_traffic_node = Object()
                    
                    radius_traffic_node.radiustraffic_id=model.radius_traffic_transmit_service_id
                    
                    radius_traffic_node.value = unicode(self.tableWidget_radius_traffic_trafficcost.item(i,1).text())
                    radius_traffic_node.timeperiod_id = self.tableWidget_radius_traffic_trafficcost.item(i,2).id
                    radius_traffic_node.cost = unicode(self.tableWidget_radius_traffic_trafficcost.item(i,3).text())
                    self.connection.save(radius_traffic_node, "billservice_radiustrafficnode")
            
            elif self.radius_traffic_access_service_checkbox.checkState()==0 and model.hasattr("radius_traffic_transmit_service_id"):
                if  not model.isnull("radius_traffic_transmit_service_id"):
                    
                    self.connection.iddelete(self.model.radius_traffic_transmit_service_id, "billservice_radiustraffic" )
                    
                    radius_traffic_transmit_service_id=model.radius_traffic_transmit_service_id
                    model.radius_traffic_transmit_service_id=None
                    self.connection.save(model, "billservice_tariff")
                    self.connection.iddelete(radius_traffic_transmit_service_id, "billservice_radiustraffic")
                    
                    model.radius_traffic_transmit_service_id = None
            
                else:
                    model.radius_traffic_transmit_service_id = None
                                
            
            #Разовые услуги
            
            if self.onetime_tableWidget.rowCount()>0 and self.onetime_services_checkbox.checkState()==2:
                #onetimeservices = self.connection.sql("SELECT * FROM billservice_tariff_onetime_services WHERE tariff_id=%d" % model.id)
                for i in xrange(0, self.onetime_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.onetime_tableWidget, i)
                    
                    if id!=-1:
                        onetime_service = self.connection.get_model(id ,"billservice_onetimeservice")
                    else:
                        onetime_service = Object()
                    
                    onetime_service.tarif_id = model.id
                    onetime_service.name=unicode(self.onetime_tableWidget.item(i, 1).text())
                    onetime_service.cost=unicode(self.onetime_tableWidget.item(i, 2).text())
                    onetime_service.created = datetime.datetime.now() 
                    self.connection.save(onetime_service, "billservice_onetimeservice")
                    

            elif self.onetime_services_checkbox.checkState()==0:
                self.connection.iddelete(model.id, "billservice_onetimeservice")
                                                   
            
            #Периодические услуги
            if self.periodical_tableWidget.rowCount()>0 and self.periodical_services_checkbox.checkState()==2:
                for i in xrange(0, self.periodical_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.periodical_tableWidget, i)
                    
                    if self.periodical_tableWidget.item(i, 1)==None or self.periodical_tableWidget.item(i, 2)==None or self.periodical_tableWidget.item(i, 3)==None or self.periodical_tableWidget.item(i, 4)==None or self.periodical_tableWidget.item(i, 6)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки периодических услуг")
                        self.connection.rollback()
                        return
                    
                    if id!=-1:
                        periodical_service = self.connection.get_model(id, "billservice_periodicalservice")
                    else:
                        periodical_service = Object()
                    [u'#', u'Название', u'Период', u"Начало списаний", u'Способ снятия', u'Стоимость', u"Условие", u"Отключить услугу с"]
                    periodical_service.tarif_id = model.id
                    periodical_service.name=unicode(self.periodical_tableWidget.item(i, 1).text())
                    periodical_service.settlement_period_id = unicode(self.periodical_tableWidget.item(i, 2).id)
                    periodical_service.cash_method = unicode(self.periodical_tableWidget.item(i, 4).text())
                    periodical_service.cost=unicode(self.periodical_tableWidget.item(i, 5).text())
                    periodical_service.condition = self.periodical_tableWidget.item(i,6).selected_id
                    periodical_service.created = self.periodical_tableWidget.item(i,3).created
                    periodical_service.deactivated = self.periodical_tableWidget.item(i,7).deactivated
                    
                    self.connection.save(periodical_service, "billservice_periodicalservice")    
                      
            elif self.periodical_services_checkbox.checkState()==0:
                #!!!DAMN ERROR
                #self.connection.iddelete(model.id, "billservice_periodicalservice")
                for i in xrange(0, self.periodical_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.periodical_tableWidget, i)
                    self.connection.iddelete(id, "billservice_periodicalservice")
                

            #Лимиты
            if self.limit_tableWidget.rowCount()>0 and self.limites_checkbox.checkState()==2:
                for i in xrange(0, self.limit_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.limit_tableWidget, i)
                    #print self.limit_tableWidget.item(i, 1), self.limit_tableWidget.item(i, 3), self.limit_tableWidget.item(i, 8), self.limit_tableWidget.cellWidget(i, 4)
                    if self.limit_tableWidget.item(i, 6)==None or (self.limit_tableWidget.item(i, 6).id==1 and self.limit_tableWidget.item(i, 7)==None) or self.limit_tableWidget.item(i, 1)==None or self.limit_tableWidget.item(i, 3)==None or self.limit_tableWidget.item(i, 5)==None or self.limit_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки лимитов")
                        self.connection.rollback()
                        return
                   
                    if id!=-1:                        
                        limit = self.connection.get_model(id, "billservice_trafficlimit")
                    else:
                        limit = Object()
                    
                    limit.tarif_id = model.id
                    limit.name=unicode(self.limit_tableWidget.item(i, 1).text())
                    limit.settlement_period_id = self.limit_tableWidget.item(i, 3).id
                    limit.mode = self.limit_tableWidget.cellWidget(i,2).checkState()==2
                    limit.size=unicode(int(float(unicode(self.limit_tableWidget.item(i, 5).text()))*1048576))
                    limit.group_id = self.limit_tableWidget.item(i, 4).id
                    limit.action = self.limit_tableWidget.item(i, 6).id
                    
                    
                    #limit.in_direction = self.limit_tableWidget.cellWidget(i,5).checkState()==2
                    #limit.out_direction = self.limit_tableWidget.cellWidget(i,6).checkState()==2
                    #limit.transit_direction = self.limit_tableWidget.cellWidget(i,7).checkState()==2
                    
                    limit.id = self.connection.save(limit, "billservice_trafficlimit")
                    try:
                        speedlimit_model = self.limit_tableWidget.item(i, 7).model
                        if limit.action==1: 
                            speedlimit_model.limit_id = limit.id
                            self.connection.save(speedlimit_model, "billservice_speedlimit")
                        elif limit.action==0:
                            self.connection.iddelete(speedlimit_model, "billservice_speedlimit")
                    except Exception, e:
                        pass

            elif self.limites_checkbox.checkState()==0:
                d = Object()
                d.tarif_id = model.id
                self.connection.delete(d, "billservice_trafficlimit")

            #Подключаемые услуги
            if self.tableWidget_addonservices.rowCount()>0 and self.checkBox_addon_services.checkState()==2:
                for i in xrange(0, self.tableWidget_addonservices.rowCount()):
                    id = self.getIdFromtable(self.tableWidget_addonservices, i)
                    
                    if self.tableWidget_addonservices.item(i, 1)==None and (self.tableWidget_addonservices.item(i, 3)!=None and self.tableWidget_addonservices.item(i, 2) in [None, 0]):
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки подключаемых услуг")
                        self.connection.rollback()
                        return
                    if id!=-1:
                        addon_service = self.connection.get_model(id, "billservice_addonservicetarif")
                    else:
                        addon_service = Object()
                    
                    addon_service.tarif_id = model.id
                    addon_service.service_id=unicode(self.tableWidget_addonservices.item(i, 1).id)
                    if self.tableWidget_addonservices.item(i, 2):
                        addon_service.activation_count = unicode(self.tableWidget_addonservices.item(i, 2).id)
                    else:
                        addon_service.activation_count = 0
                    if self.tableWidget_addonservices.item(i, 3):
                        addon_service.activation_count_period_id = unicode(self.tableWidget_addonservices.item(i, 3).id)
                    else:
                        addon_service.activation_count_period_id = None

                    
                    self.connection.save(addon_service, "billservice_addonservicetarif")    
                      
            elif self.periodical_services_checkbox.checkState()==0:
                #!!!DAMN ERROR!
                #self.connection.iddelete(model.id, "billservice_addonservicetarif")
                for i in xrange(0, self.tableWidget_addonservices.rowCount()):
                    id = self.getIdFromtable(self.tableWidget_addonservices, i)
                    self.connection.iddelete(id, "billservice_addonservicetarif")
                                
            #Доступ по трафику 
            if self.transmit_service_checkbox.checkState()==2:
                if not model.isnull('traffic_transmit_service_id'):
                    traffic_transmit_service = self.connection.get_model(self.model.traffic_transmit_service_id, "billservice_traffictransmitservice")
                else:
                    traffic_transmit_service = Object()
                
                #traffic_transmit_service.period_check='SP_START'
                traffic_transmit_service.reset_traffic=self.reset_traffic_edit.checkState()==2
                traffic_transmit_service.id = self.connection.save(traffic_transmit_service, "billservice_traffictransmitservice")
                
                    
     
                for i in xrange(0, self.trafficcost_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.trafficcost_tableWidget, i)
                    
                    if self.trafficcost_tableWidget.item(i, 1)==None or self.trafficcost_tableWidget.item(i, 2)==None or self.trafficcost_tableWidget.item(i, 3)==None or self.trafficcost_tableWidget.item(i, 4)==None or self.trafficcost_tableWidget.item(i, 5)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для оплаты за трафик")
                        self.connection.rollback()
                        return
              
                                                   
                    if id!=-1:
                        transmit_node = self.connection.get_model(id, "billservice_traffictransmitnodes")
                    else:
                        transmit_node = Object()
                    
                    
                    transmit_node.traffic_transmit_service_id = traffic_transmit_service.id
                    transmit_node.edge_value =float(self.trafficcost_tableWidget.item(i,1).text() or 0)*(1024*1024)
                    transmit_node.edge_end = float(self.trafficcost_tableWidget.item(i,2).text() or 0)
                    transmit_node.group_id = self.trafficcost_tableWidget.item(i,3).id
                    #transmit_node.in_direction = self.trafficcost_tableWidget.cellWidget(i,4).checkState()==2
                    #transmit_node.out_direction = self.trafficcost_tableWidget.cellWidget(i,5).checkState()==2
                    #transmit_node.transit_direction = self.trafficcost_tableWidget.cellWidget(i,6).checkState()==2
                    transmit_node.cost = unicode(self.trafficcost_tableWidget.item(i,5).text())
                    
                    
                    transmit_node.id = self.connection.save(transmit_node, "billservice_traffictransmitnodes")
                    
                            
                    time_period_models = [x.id for x in self.trafficcost_tableWidget.item(i, 4).models]
                    if len(time_period_models)==0:
                        return
                    
                    time_periods_for_node = self.connection.sql("""SELECT timeperiod.* FROM billservice_timeperiod as timeperiod
                                                                JOIN billservice_traffictransmitnodes_time_nodes as tn ON tn.timeperiod_id=timeperiod.id
                                                                WHERE tn.traffictransmitnodes_id=%d
                                                                """ % transmit_node.id)
                    time_periods_for_node = [x.id for x in time_periods_for_node]
                    for cl in time_period_models:
                        if cl not in time_periods_for_node:
                            tc = Object()
                            tc.traffictransmitnodes_id = transmit_node.id
                            tc.timeperiod_id = cl
                            self.connection.save(tc, "billservice_traffictransmitnodes_time_nodes")

                    for cl in time_periods_for_node:
                        if cl not in time_period_models:
                            d = Object()
                            d.traffictransmitnodes_id = transmit_node.id
                            d.timeperiod_id = cl
                            self.connection.delete(d, "billservice_traffictransmitnodes_time_nodes")


                model.traffic_transmit_service_id = traffic_transmit_service.id

                #Предоплаченный трафик
                for i in xrange(self.prepaid_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.prepaid_tableWidget, i)
                    
                    if self.prepaid_tableWidget.item(i, 1)==None or self.prepaid_tableWidget.item(i, 2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для предоплаченного трафика")
                        self.connection.rollback()
                        return

                        
                    if id!=-1:
                        #print "prepaid_id=", id
                        prepaid_node = self.connection.get_model(id, "billservice_prepaidtraffic")
                    else:
                        prepaid_node = Object()

                    #print "i=", self.prepaid_tableWidget.item(i,2)

                    prepaid_node.traffic_transmit_service_id = traffic_transmit_service.id
                    prepaid_node.group_id = self.prepaid_tableWidget.item(i,1).id
                    #prepaid_node.out_direction = self.prepaid_tableWidget.cellWidget(i,3).checkState()==2
                    #prepaid_node.transit_direction = self.prepaid_tableWidget.cellWidget(i,4).checkState()==2
                    prepaid_node.size = unicode(int(float(self.prepaid_tableWidget.item(i,2).text())*1048576))


                    #traffic_class_models = [x.id for x in self.prepaid_tableWidget.item(i, 1).models]
                    #if len(traffic_class_models)==0:
                    #    return

                    prepaid_node.id = self.connection.save(prepaid_node,"billservice_prepaidtraffic")


    
            elif (self.transmit_service_checkbox.checkState()==0) and not model.isnull("traffic_transmit_service_id"):
                tsid = model.traffic_transmit_service_id
                model.traffic_transmit_service_id=None
                self.connection.save(model, "billservice_tariff")
                self.connection.iddelete(tsid, "billservice_traffictransmitservice" )

                
                            
        
            
            self.connection.save(model, "billservice_tariff")
            self.connection.commit()
            
            #Было ли изменено состояние ipn_for_vpn 
            if previous_ipn_for_vpn_state!=access_parameters.ipn_for_vpn:
                if self.model is not None and not self.accountActions(previous_ipn_for_vpn_state, access_parameters.ipn_for_vpn):
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"При синхронизации пользователей на сервере доступа возникли проблемы.\nПроверьте правильность указания IPN IP и синхронизируйте пользователей вручную через контекстное меню.")
            #print True
            
        except Exception, e:
            print e
            traceback.print_exc()
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка сохранения тарифного плана")
            return

        QtGui.QDialog.accept(self)
             
    def accountActions(self, prev, now):

        accounts = self.connection.sql("SELECT id FROM billservice_account WHERE get_tarif(id)=%s" % self.model.id)
        self.connection.commit()
        x = [d.id for d in accounts]
        if prev==False and now==True:
            return self.connection.accountActions(x, {}, "create")
        elif prev==True and now==False:
            return self.connection.accountActions(x, {}, "delete")
            
    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)        
            
            

class AccountsMdiEbs(ebsTable_n_TreeWindow):
    def __init__(self, connection, parent, selected_account=None):
        columns=[u'#', u'Имя пользователя', u'Баланс', u'Кредит', u'Имя', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u"MAC адрес", u'', u"Дата создания", u"Комментарий"]
        initargs = {"setname":"account_frame", "objname":"AccountEbsMDI", "winsize":(0,0,1100,600), "wintitle":"Пользователи", "tablecolumns":columns, "spltsize":(0,0,391,411), "treeheader":"Тарифы", "tbiconsize":(18,18)}
        self.parent = parent
        self.selected_account = selected_account
        self.sql = ''
        self.filter_dialog = None
        self.last_click = QtCore.QTime(0, 0, 0, 0)
        super(AccountsMdiEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tarif_treeWidget = self.treeWidget
        self.getTarifId = self.getTreeId
        self.refresh_ = self.refresh
        
        self.tb = QtGui.QToolButton(self)
        self.tb.setIcon(QtGui.QIcon("images/documents.png"))
        self.tb.setText(u"Документы")
        self.tb.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.menu = QtGui.QMenu(self.toolBar)
        
        self.reports_tb = QtGui.QToolButton(self)
        self.reports_tb.setIcon(QtGui.QIcon("images/easytag.png"))
        self.reports_tb.setText(u"Отчёты")
        self.reports_tb.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.reports_menu = QtGui.QMenu(self.toolBar)
        
        
        #self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.refreshTree)

        actList=[("addAction", "Добавить аккаунт", "images/add.png", self.addframe), \
                 ("delAction", "Удалить аккаунт", "images/del.png", self.delete), \
                 ("addTarifAction", "Добавить тариф", "images/folder_add.png", self.addTarif), \
                 ("delTarifAction", "Удалить тариф", "images/folder_delete.png", self.delTarif), \
                 ("transactionAction", "Пополнить счёт", "images/pay.png", self.makeTransation), \
                 ("transactionReportAction", "Платежи и списания", "images/moneybook.png", self.transactionReport), \
                 ("messageDialogAction", "Сообщения", "images/mesages.png", self.messageDialogForm), \
                 
                 ("actionEnableSession", "Включить на сервере доступа", "images/add.png", self.accountEnable), \
                 ("actionDisableSession", "Отключить на сервере доступа", "images/del.png", self.accountDisable), \
                 ("actionAddAccount", "Добавить на сервер доступа", "images/add.png", self.accountAdd), \
                 ("actionDeleteAccount", "Удалить с сервера доступа", "images/del.png", self.accountDelete), \
                 ("editTarifAction", "Редактировать", "images/edit.png", self.editTarif),\
                 ("editAccountAction", "Редактировать", "images/configure.png", self.editframe),\
                 ("connectionAgreementAction", "Договор на подключение", "", self.pass_),\
                 ("actionChangeTarif", "Сменить тарифный план", "images/tarif_change.png", self.changeTariff),\
                 ("actionSetSuspendedPeriod", "Отключить списание периодических услуг", "", self.suspended_period),\
                 ("actionLimitInfo", "Остаток трафика по лимитам", "", self.limit_info),\
                 ("actionPrepaidTrafficInfo", "Остаток предоплаченного трафика", "", self.prepaidtraffic_info),\
                 ("actionPrepaidRadiusTrafficInfo", "Остаток RADIUS трафика", "", self.radiusprepaidtraffic_info),\
                 ("actionSettlementPeriodInfo", "Информация по расчётным периодам", "", self.settlementperiod_info),\
                 ("rrdTrafficInfo", "График использования канала", "images/bandwidth.png", self.rrdtraffic_info),\
                 ("radiusauth_logInfo", "Логи RADIUS авторизаций", "images/easytag.png", self.radiusauth_log),\
                 ("actionRadiusAttrs", "RADIUS атрибуты", "images/configure.png", self.radius_attrs),\
                 ("actionBalanceLog", "История изменения баланса", "images/money.png", self.balance_log),\
                 ("actionAccountFilter", "Поиск аккаунтов", "images/search_accounts.png", self.accountFilter),\
                 ("actionReports", "Отчёты и документы", "images/moneybook.png", self.reportForm),\
                 
                ]
                


        objDict = {self.treeWidget :["editTarifAction", "addTarifAction", "delTarifAction"], \
                   self.tableWidget:["transactionAction", "addAction", "editAccountAction",  "delAction",  "actionAddAccount", "actionEnableSession", "actionDisableSession", "actionDeleteAccount", "messageDialogAction", "radiusauth_logInfo", "actionBalanceLog"], \
                   self.toolBar    :["addTarifAction", "delTarifAction", "separator", "actionAccountFilter", "addAction", "delAction", "separator", "transactionAction", "transactionReportAction", "messageDialogAction"],\
                   self.menu       :[ "actionChangeTarif", "separator", "actionRadiusAttrs", "separator", 'actionSettlementPeriodInfo', 'separator', "actionSetSuspendedPeriod", "separator", "actionLimitInfo", "separator", "actionPrepaidTrafficInfo", 'actionPrepaidRadiusTrafficInfo', "separator", "rrdTrafficInfo", 'radiusauth_logInfo', "actionBalanceLog", "separator"],\
                   self.reports_menu :["actionReports",],
                  }
        self.actionCreator(actList, objDict)
        
    def ebsPostInit(self, initargs):
        
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.tb.setMenu(self.menu)
        self.reports_tb.setMenu(self.reports_menu)
        #self.tb.setDisabled(True)
        self.toolBar.addWidget(self.tb)
        self.toolBar.addWidget(self.reports_tb)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.editRow = self.editTarif
        #self.connectTree()
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        self.restoreWindow()
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #
        self.treeWidget.setAcceptDrops(True)
        self.treeWidget.setDragEnabled(True)
        self.treeWidget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        
    def retranslateUI(self, initargs):
        super(AccountsMdiEbs, self).retranslateUI(initargs)
        self.tableWidget.setColumnHidden(0, False)
        
    def messageDialogForm(self):
        ids = self.get_selected_accounts()
        child = MessageDialog(accounts = ids, connection=self.connection)
        child.exec_()
    
    def reportForm(self):
        child = TemplateSelect(connection = self.connection)
        if child.exec_():
            template_id = child.id
        else:
            return
        accounts = self.get_selected_accounts()
        window = ReportMainWindow(template_id=template_id, accounts=accounts, connection = self.connection)
        self.parent.workspace.addWindow(window)
        window.show()
    
    def rrdtraffic_info(self):
        ids = self.get_selected_accounts()
        if ids:
            id=ids[0]
        window = RrdReportMainWindow(account=id, connection=self.connection)
        self.parent.workspace.addWindow(window)
        window.show()

    def radiusauth_log(self):
        id = self.getSelectedId()
        window = SimpleReportEbs(connection=self.connection, report_type='radius_authlog', account_id=id)
        self.parent.workspace.addWindow(window)
        window.show()
    
    def balance_log(self):
        id = self.getSelectedId()
        window = SimpleReportEbs(connection=self.connection, report_type='balance_log', account_id=id)
        self.parent.workspace.addWindow(window)
        window.show()
                

    def accountFilter(self):
        
        if not self.filter_dialog:
            self.filter_dialog = AccountFilterDialog(connection=self.connection)
        
        if self.filter_dialog.exec_()==1:
            self.tarif_treeWidget.setCurrentItem(self.filter_item)
            self.sql=self.filter_dialog.sql
            self.refresh()
        
    def addTarif(self):
        #print connection
        tarifframe = TarifFrame(connection=self.connection)
        if tarifframe.exec_() == 1:
            #import datetime
            #print datetime.datetime.now()
            self.refreshTree()
            self.refresh()
        
    def get_selected_accounts(self):
        ids = []
        for r in self.tableWidget.selectedItems():
            if r.column()==0:
                ids.append(r.id)
        return ids
    
    def changeTariff(self):
        tarif_id = None
        ids = self.get_selected_accounts()
        child=AddAccountTarif(connection=self.connection, account=None, get_info = True)
        if child.exec_()==1:
            tarif_id = child.tarif_edit.itemData(child.tarif_edit.currentIndex()).toInt()[0]
            date = child.date_edit.dateTime().toPyDateTime()
        if not tarif_id: return
        if not self.connection.change_tarif(ids, tarif_id, date):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Во время выполнения операции произошла ошибка."))
        else:
            self.refresh()
        
        
    def limit_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="limit", account_id=id)
            child.exec_()
        
    def prepaidtraffic_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="prepaidtraffic", account_id=id)
            child.exec_()

    def radiusprepaidtraffic_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="radiusprepaidtraffic", account_id=id)
            child.exec_()

    def settlementperiod_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="settlementperiods", account_id=id)
            child.exec_()
    
        
    def radius_attrs(self):
        id = self.getTarifId()
        if id>=0:
            child = RadiusAttrsDialog(tarif_id = id, connection = self.connection)
            child.exec_()
            
    def suspended_period(self):
        ids = []
        #import Pyro
        for index in self.tableWidget.selectedIndexes():
            #print index.row(), index.column()
            if not index.column()==0:
                continue

            i=unicode(self.tableWidget.item(index.row(), 0).id)
            try:
                ids.append(int(i))
            except Exception, e:
                print "can not convert id to int"      
                
        #print ids
        child=SuspendedPeriodForm()

        if child.exec_()==1:
            for id in ids:
                model = Object()
                model.account_id = id
                model.start_date = child.start_date
                model.end_date = child.end_date
                self.connection.save(model, "billservice_suspendedperiod")
                self.connection.commit()
                #self.suspendedPeriodRefresh()
            self.connection.commit()
    

    def delTarif(self):
        tarif_id = self.getTarifId()
        
        if tarif_id>0 and QtGui.QMessageBox.question(self, u"Удалить тарифный план?" , u"Вы уверены, что хотите удалить тарифный план?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            #print 1
            accounts=self.connection.sql("""SELECT account.id 
                    FROM billservice_account as account
                    JOIN billservice_accounttarif as accounttarif ON accounttarif.id=(SELECT id FROM billservice_accounttarif WHERE account_id=account.id AND datetime<now() ORDER BY datetime DESC LIMIT 1 )
                    WHERE accounttarif.tarif_id=%d ORDER BY account.username ASC;""" % tarif_id)
            print 2
            self.connection.commit()
            if len(accounts)>0:

                tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
                tarifs = self.connection.sql("SELECT id, name FROM billservice_tariff WHERE id <> %d AND deleted IS NOT TRUE;" % (tarif_id,))

                child = ComboBoxDialog(items = tarifs, title = u"Выберите тарифный план, куда нужно перенести пользователей")
                
                if child.exec_()==1:
                    tarif = self.connection.get("SELECT * FROM billservice_tariff WHERE name='%s'" % unicode(child.comboBox.currentText()))
    
                    try:    
                        for account in accounts:
                            accounttarif = Object()
                            accounttarif.account_id = account.id
                            accounttarif.tarif_id = tarif.id
                            accounttarif.datetime = datetime.datetime.now() 
                            self.connection.save(accounttarif, "billservice_accounttarif")
                    
                    
                        #self.connection.create("UPDATE billservice_tariff SET deleted = True WHERE id=%s" % tarif_id)
                        self.connection.sql("UPDATE billservice_tariff SET deleted = True WHERE id=%d RETURNING id" % tarif_id)
                        self.connection.commit()
                    except Exception, e:
                        print e
                        self.connection.rollback()
                        return
            else:

                try:
                    #self.connection.create("UPDATE billservice_tariff SET deleted = True WHERE id=%s" % tarif_id)
                    self.connection.iddelete(tarif_id, "billservice_tariff")
                    self.connection.commit()

                except Exception, e:
                    print e

                    self.connection.rollback()
                    return
            #self.tarif_treeWidget.setCurrentItem(self.tarif_treeWidget.topLevelItem(0))
            self.refreshTree()

            try:
                setFirstActive(self.tarif_treeWidget)
            except Exception, ex:
                print ex
            #self.refresh()
        
    def editTarif(self, *args, **kwargs):
        model = self.connection.get_model(self.getTarifId(), "billservice_tariff" )
        
        tarifframe = TarifFrame(connection=self.connection, model=model)
        #self.parent.workspace.addWindow(tarifframe)
        if tarifframe.exec_()==1:
            self.refreshTree()
            self.refresh()
            
    
    def addframe(self):
        if self.getTarifId() not in [-1000, -2000]: return
        tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
        self.connection.commit()
        #self.connection.flush()
        id = self.getTarifId()
        ipn_for_vpn = self.connection.get("""SELECT ap.ipn_for_vpn as ipn_for_vpn FROM billservice_accessparameters as ap 
        JOIN billservice_tariff as tarif ON tarif.access_parameters_id=ap.id
        WHERE tarif.id=%s""" % id).ipn_for_vpn
        self.connection.commit()
        #child = AddAccountFrame(connection=self.connection, tarif_id=id, ttype=tarif_type, ipn_for_vpn=ipn_for_vpn)
        child = AccountWindow(connection=self.connection, tarif_id=id, ttype=tarif_type, ipn_for_vpn=ipn_for_vpn)
        self.parent.workspace.addWindow(child)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        child.show()
        return
        #self.connection.commit()
        #child = AddAccountFrame(connection=self.connection)


    def makeTransation(self):
        id = self.getSelectedId()
        account = self.connection.get_model(id, "billservice_account")
        child = TransactionForm(connection=self.connection, account = account)
        if child.exec_()==1:
            self.refresh()
       
    def prepaidReport(self):
        pass                                
            
    def transactionReport(self):
        id = self.getSelectedId()
        account = self.connection.get_model(id, "billservice_account")
        tr = TransactionsReport(connection=self.connection, account = account)
        self.parent.workspace.addWindow(tr)
        tr.show()
            
    
    def getSelectedId(self):
        return self.tableWidget.item(self.tableWidget.currentRow(), 0).id


    def pass_(self):
        pass
    
    def delete(self):
        
        ids = self.get_selected_accounts()
        if not ids:return
        if QtGui.QMessageBox.question(self, u"Удалить аккаунты?" , u"Вы уверены, что хотите удалить пользователей из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.No:
            return

        for id in ids:
            if id>0:
                self.connection.accountActions(id, None, 'delete')
                self.connection.iddelete(id, "billservice_account")
                self.connection.commit()
                self.refresh()


    @connlogin
    def editframe(self, *args, **kwargs):
        #print self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        id=self.getSelectedId()
        #print id
        if id == 0:
            return
        try:
            model = self.connection.get_model(id ,"billservice_account")
        except Exception, e:
            print e
            return
        #print 'model', model

        
        ipn_for_vpn = self.connection.get("""SELECT ap.ipn_for_vpn as ipn_for_vpn FROM billservice_accessparameters as ap 
        JOIN billservice_tariff as tarif ON tarif.access_parameters_id=ap.id
        WHERE tarif.id=get_tarif(%s)""" % model.id).ipn_for_vpn
        tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
        #addf = AddAccountFrame(connection=self.connection,tarif_id=self.getTarifId(), ttype=tarif_type, model=model, ipn_for_vpn=ipn_for_vpn)
        child = AccountWindow(connection=self.connection,tarif_id=self.getTarifId(), ttype=tarif_type, model=model, ipn_for_vpn=ipn_for_vpn)
        
        self.parent.workspace.addWindow(child)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        child.show()
        return
        

    def addrow(self, value, x, y, id=None, color=None, enabled=True, ctext=None, setdata=False):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if float(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
            elif float(value)==0:
                headerItem.setBackgroundColor(QtGui.QColor("#ffdc51"))
                #headerItem.setTextColor(QtGui.QColor('#ffffff'))
                                
        if enabled!=1:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        
            
        if y==1:
            if enabled==True:
                headerItem.setIcon(QtGui.QIcon("images/user.png"))
            else:
                headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
        #if setdata:
            #headerItem.setData(39, QtCore.QVariant(value))
        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))        
        else:            
            headerItem.setData(0, QtCore.QVariant(value))         
            '''if ctext is not None:                headerItem.setText(unicode(ctext))            else:                headerItem.setText(unicode(value))'''        
        headerItem.id = id
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)

    def refreshTree(self):
        self.disconnectTree()
        curItem = -1
        try:
            curItem = self.tarif_treeWidget.indexOfTopLevelItem(self.tarif_treeWidget.currentItem())
        except Exception, ex:
            print ex
        self.tarif_treeWidget.clear()

        #tariffs = self.connection.foselect("billservice_tariff")
        tariffs = self.connection.get_tariffs()
        self.connection.commit()
        self.tableWidget.setColumnHidden(0, True)
        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -2000
        item.tarif_type = 'all'
        item.setText(0, u"Результаты поиска")
        item.setIcon(0,QtGui.QIcon("images/folder.png"))        
        self.filter_item = item
        
        for tarif in tariffs:
            item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
            item.id = tarif.id
            item.tarif_type = tarif.ttype
            item.setText(0, u"%s %s" % (tarif.ttype, tarif.name))
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            #tariff_type = self.connection.get("SELECT get_tariff_type(%d);" % tarif.id)
            #item.setText(1, tarif.ttype)
            if not tarif.active:
                item.setIcon(0, QtGui.QIcon("images/folder_disabled.png"))
        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -1000
        item.tarif_type = 'all'
        item.setText(0, u"Все аккаунты")
        item.setIcon(0,QtGui.QIcon("images/folder.png"))
        

        self.connectTree()
        if curItem != -1:
            self.tarif_treeWidget.setCurrentItem(self.tarif_treeWidget.topLevelItem(curItem))
        

    #def dragEnterEvent(self, event):
    #    print 123
    #    event.accept()

    def treeWidgetDropEvent(self, event):
      item = self.treeWidget.currentItem()
      self.treeWidget.addTopLevelItem(item)
      event.accept()

    #def dropMoveEvent(event):
    #    print 321
    #    event.accept()
        
    def refresh(self, item=None, k=''):
        if item and not self.last_click:
            self.last_click = QtCore.QTime.currentTime()
            return
        now = QtCore.QTime.currentTime()
        if item and ((now.second() + now.msec()) - (1000*self.last_click.second()+self.last_click.msec())  )<500:
            print "doubleclick"
            print ((1000*now.second() + now.msec()) - (1000*self.last_click.second()+self.last_click.msec()) )
            self.last_click = None
            return
        else:
            print "singleclick"        
            
        
        self.tableWidget.setSortingEnabled(False)
        self.statusBar().showMessage(u"Ожидание ответа")
        self.treeWidget.dropEvent=self.treeWidgetDropEvent


        
        #print item
        if item:
            id=item.id
            if id==-1000 or id==-2000:
                self.addAction.setDisabled(True)
                self.delAction.setDisabled(True)
                
            else:
                self.addAction.setDisabled(False)
                self.delAction.setDisabled(False)
        else:
            try:
                id=self.getTarifId()
                if id==-1000 or id==-2000:
                    self.addAction.setDisabled(True)
                    self.delAction.setDisabled(True)
                    
                else:
                    self.addAction.setDisabled(False)
                    self.delAction.setDisabled(False)
            except:
                return
        
        if id==-1000 or id==-2000:
            #self.sql=''
            columns=[u'#', u'Имя пользователя', u"Договор",u'Тарифный план', u'Баланс', u'Кредит', u'Имя',  u'Сервер доступа', u'',  u"Нулевой баланс c", u"Дата создания", u"Комментарий"]
            makeHeaders(columns, self.tableWidget)
        else:
            columns=[u'#', u'Имя пользователя',  u"Договор", u'Баланс', u'Кредит', u'Имя', u'Сервер доступа', u'',  u"Нулевой баланс c", u"Дата создания", u"Комментарий"]
            makeHeaders(columns, self.tableWidget)

        print "sql=", self.sql            
        if id==-2000 and self.sql:
            accounts = self.connection.get_accounts_for_tilter(self.sql)
        else:
            accounts = self.connection.get_accounts_for_tarif(self.getTarifId())
        #print accounts
        #print self.getTarifId()
        self.connection.commit()
        #self.connection.commit()
        #print accounts

        #print "after acc"
        self.tableWidget.setRowCount(len(accounts))
        self.tableWidget.clearContents()
        
        m_ballance = 0
        disabled_accounts = 0
        
        i=0
        for a in accounts:    
            
            self.addrow(i, i,0, id=a.id, enabled=a.status, ctext=str(i+1), setdata=True)
            self.addrow(a.username, i,1, enabled=a.status)
            self.addrow(a.contract, i,2, enabled=a.status)
            #print "status", a
            disabled_accounts += 1 if a.status<>1 else 0
            if id==-1000 or id==-2000:
                self.addrow(a.tarif_name, i,3, enabled=a.status)
                self.addrow(float("%.02f" % float(a.ballance)), i,4, color="red", enabled=a.status)
                self.addrow(float(a.credit), i,5, enabled=a.status)
                self.addrow(a.fullname, i,6, enabled=a.status)
                self.addrow(a.nas_name,i,7, enabled=a.status)
                #self.addrow(a.vpn_ip_address, i,7, enabled=a.status)
                #self.addrow(a.ipn_ip_address, i,8, enabled=a.status)
                #self.addrow(a.ipn_mac_address, i,9, enabled=a.status)
                #self.addrow(a.suspended, i,10, enabled=a.status)
                #self.addrow(a.balance_blocked, i,11, enabled=a.status)
                self.tableWidget.setCellWidget(i,8,simpleTableImageWidget(balance_blocked=a.balance_blocked, trafic_limit=a.disabled_by_limit, ipn_status=a.ipn_status, ipn_added=a.ipn_added))
                #self.addrow(a.disabled_by_limit,i,12, enabled=a.status)
                if a.last_balance_null:
                    self.addrow(a.last_balance_null.strftime(self.strftimeFormat), i,9, enabled=a.status)
                self.addrow(a.created.strftime(self.strftimeFormat), i,10, enabled=a.status)
                self.addrow(a.comment, i,11, enabled=a.status)
                #self.addrow(a.created, i,11, enabled=a.status)
            else:
                #self.addrow("%.2f" % a.ballance, i,2, color="red", enabled=a.status)
                self.addrow("%.02f" % float(a.ballance), i,3, color="red", enabled=a.status)
                self.addrow(float(a.credit), i,4, enabled=a.status)
                self.addrow(a.fullname, i,5, enabled=a.status)
                self.addrow(a.nas_name,i,6, enabled=a.status)
                #self.addrow(a.vpn_ip_address, i,6, enabled=a.status)
                #self.addrow(a.ipn_ip_address, i,7, enabled=a.status)
                #self.addrow(a.ipn_mac_address, i,8, enabled=a.status)
                #self.addrow(a.suspended, i,10, enabled=a.status)
                #self.addrow(a.balance_blocked, i,11, enabled=a.status)
                self.tableWidget.setCellWidget(i,7,simpleTableImageWidget(balance_blocked=a.balance_blocked, trafic_limit=a.disabled_by_limit, ipn_status=a.ipn_status, ipn_added=a.ipn_added))
                #self.addrow(a.disabled_by_limit,i,12, enabled=a.status)
                if a.last_balance_null:
                    self.addrow(a.last_balance_null.strftime(self.strftimeFormat), i,8, enabled=a.status)
                
                self.addrow(a.created.strftime(self.strftimeFormat), i,9, enabled=a.status)
                
                self.addrow(a.comment, i,10, enabled=a.status)
                #self.addrow(a.created, i,11, enabled=a.status)
                
            m_ballance += float(a.ballance)
            #self.tableWidget.setRowHeight(i, 17)

            if self.selected_account:
                if self.selected_account.id == a.id:
                    self.tableWidget.setRangeSelected(QtGui.QTableWidgetSelectionRange(i,0,i,12), True)
            i+=1
            
        self.statusBar().showMessage(u'Учётных записей:%s. Средний баланс: %s. Общий баланс: %.2f. Неактивно: %s' % (len(accounts), m_ballance/(1 if len(accounts)==0 else len(accounts)), m_ballance, disabled_accounts))
        self.tableWidget.setColumnHidden(0, False)
        #HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.delNodeLocalAction()
        #self.tablewidget.setShowGrid(False)
        self.tableWidget.setSortingEnabled(True)
        
        #self.setCentralWidget(QtGui.QWidget(self))
        

    def accountEnable(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, {}, 'enable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        


    def accountAdd(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, {},  'create'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        
    def accountDelete(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, {}, 'delete'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()

    def accountDisable(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, {}, 'disable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        
    
    def addNodeLocalAction(self):
        super(AccountsMdiEbs, self).addNodeLocalAction([self.addAction,self.delTarifAction])
        
    def delNodeLocalAction(self):
        super(AccountsMdiEbs, self).delNodeLocalAction([self.delAction,self.transactionAction,self.transactionReportAction])
        
