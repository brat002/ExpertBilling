#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui

import traceback
import psycopg2
from ebsWindow import ebsTable_n_TreeWindow
from db import Object as Object
from db import AttrDict
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil, SplitterUtil, transip
from types import BooleanType
import copy
from customwidget import CustomDateTimeWidget
from randgen import GenUsername as nameGen , GenPasswd as GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import RadiusAttrsDialog, CheckBoxDialog, ComboBoxDialog, SpeedEditDialog , TransactionForm
import time
from Reports import TransactionsReportEbs as TransactionsReport, SimpleReportEbs

from helpers import tableFormat, check_speed
from helpers import transaction, makeHeaders
from helpers import Worker
from CustomForms import simpleTableImageWidget, tableImageWidget, IPAddressSelectForm, TemplateSelect, RrdReportMainWindow
from CustomForms import CustomWidget, CardPreviewDialog, SuspendedPeriodForm, GroupsDialog, SpeedLimitDialog, InfoDialog, PSCreatedForm, AccountAddonServiceEdit
from MessagesFrame import MessageDialog
from mako.template import Template
from HardwareFrame import AccountHardwareDialog

strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
qtTimeFormat = "YYYY-MM-DD HH:MM:SS"
import IPy
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
class CustomDateTime(QtCore.QDateTime):
    def __init__(self, *args, **kwargs):
        super(CustomDateTime, self).__init__(*args, **kwargs)
        print 321, self
        
    def toString(self, format):
        print 123
        return super(CustomDateTime, self).toString("yyyy.MM.dd")
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

limit_actions = [CashType(0, u"Заблокировать пользователя"), CashType(1,u"Изменить скорость")]

la_list = [u"Заблокировать пользователя", u"Изменить скорость"]

ps_conditions = [CashType(0, u"При любом балансе"), CashType(1,u"При положительном и нулевом балансе"), CashType(2,u"При отрицательном балансе"), CashType(3,u"При положительнои балансе")]
ps_list = [u"При любом балансе", u"При положительном и нулевом балансе", u"При отрицательном балансе", u"При положительнои балансе"]

round_types = [CashType(0, u"Не округлять"),CashType(1, u"В большую сторону")]
class SubaccountLinkDialog(QtGui.QDialog):
    def __init__(self, connection, account, model = None):
        super(SubaccountLinkDialog, self).__init__()
        #self.setObjectName("SubaccountLinkDialog")
        self.connection = connection
        self.account = account
        self.model = model
        self.resize(662, 549)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox_link_parameters = QtGui.QGroupBox(self.tab)
        self.groupBox_link_parameters.setObjectName(_fromUtf8("groupBox_link_parameters"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_link_parameters)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_nas = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_nas.setObjectName(_fromUtf8("label_nas"))
        self.gridLayout.addWidget(self.label_nas, 0, 0, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_nas.setObjectName(_fromUtf8("comboBox_nas"))
        self.gridLayout.addWidget(self.comboBox_nas, 0, 1, 1, 1)
        self.label_link_login = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_login.setObjectName(_fromUtf8("label_link_login"))
        self.gridLayout.addWidget(self.label_link_login, 1, 0, 1, 1)
        self.lineEdit_link_login = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_login.setObjectName(_fromUtf8("lineEdit_link_login"))
        self.gridLayout.addWidget(self.lineEdit_link_login, 1, 1, 1, 4)
        self.label_link_password = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_password.setObjectName(_fromUtf8("label_link_password"))
        self.gridLayout.addWidget(self.label_link_password, 3, 0, 1, 1)
        self.lineEdit_link_password = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_password.setObjectName(_fromUtf8("lineEdit_link_password"))
        self.gridLayout.addWidget(self.lineEdit_link_password, 3, 1, 1, 4)
        self.label_link_vpn_ip_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn_ip_address.setObjectName(_fromUtf8("label_link_vpn_ip_address"))
        self.gridLayout.addWidget(self.label_link_vpn_ip_address, 5, 0, 1, 1)
        self.lineEdit_vpn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_ip_address.setObjectName(_fromUtf8("lineEdit_vpn_ip_address"))
        self.gridLayout.addWidget(self.lineEdit_vpn_ip_address, 5, 1, 1, 1)
        self.label_link_vpn = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn.setObjectName(_fromUtf8("label_link_vpn"))
        self.gridLayout.addWidget(self.label_link_vpn, 7, 0, 1, 1)
        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_ip_address.setObjectName(_fromUtf8("lineEdit_ipn_ip_address"))
        self.gridLayout.addWidget(self.lineEdit_ipn_ip_address, 7, 1, 1, 1)
        self.label_link_ipn_mac_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_ipn_mac_address.setObjectName(_fromUtf8("label_link_ipn_mac_address"))
        self.gridLayout.addWidget(self.label_link_ipn_mac_address, 12, 0, 1, 1)
        self.lineEdit_link_ipn_mac_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_ipn_mac_address.setObjectName(_fromUtf8("lineEdit_link_ipn_mac_address"))
        self.gridLayout.addWidget(self.lineEdit_link_ipn_mac_address, 12, 1, 1, 1)
        self.label_link_switch = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_switch.setObjectName(_fromUtf8("label_link_switch"))
        self.gridLayout.addWidget(self.label_link_switch, 13, 0, 1, 1)
        self.comboBox_link_switch_id = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_link_switch_id.setObjectName(_fromUtf8("comboBox_link_switch_id"))
        self.gridLayout.addWidget(self.comboBox_link_switch_id, 13, 1, 1, 1)
        self.label_vpn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_vpn_speed.setObjectName(_fromUtf8("label_vpn_speed"))
        self.gridLayout.addWidget(self.label_vpn_speed, 16, 0, 1, 1)
        self.lineEdit_vpn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_speed.setObjectName(_fromUtf8("lineEdit_vpn_speed"))
        self.gridLayout.addWidget(self.lineEdit_vpn_speed, 16, 1, 1, 6)
        self.label_ipn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_ipn_speed.setObjectName(_fromUtf8("label_ipn_speed"))
        self.gridLayout.addWidget(self.label_ipn_speed, 17, 0, 1, 1)
        self.lineEdit_ipn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_speed.setObjectName(_fromUtf8("lineEdit_ipn_speed"))
        self.gridLayout.addWidget(self.lineEdit_ipn_speed, 17, 1, 1, 6)
        self.groupBox = QtGui.QGroupBox(self.groupBox_link_parameters)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.toolButton_ipn_added = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_added.setCheckable(True)
        self.toolButton_ipn_added.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton_ipn_added.setObjectName(_fromUtf8("toolButton_ipn_added"))
        self.horizontalLayout.addWidget(self.toolButton_ipn_added)
        self.toolButton_ipn_enabled = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_enabled.setCheckable(True)
        self.toolButton_ipn_enabled.setObjectName(_fromUtf8("toolButton_ipn_enabled"))
        self.horizontalLayout.addWidget(self.toolButton_ipn_enabled)
        self.toolButton_ipn_sleep = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_sleep.setCheckable(True)
        self.toolButton_ipn_sleep.setObjectName(_fromUtf8("toolButton_ipn_sleep"))
        self.horizontalLayout.addWidget(self.toolButton_ipn_sleep)
        self.gridLayout.addWidget(self.groupBox, 0, 2, 1, 4)
        self.toolButton_password = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_password.setObjectName(_fromUtf8("toolButton_password"))
        self.gridLayout.addWidget(self.toolButton_password, 3, 5, 1, 1)
        self.toolButton_login = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_login.setObjectName(_fromUtf8("toolButton_login"))
        self.gridLayout.addWidget(self.toolButton_login, 1, 5, 1, 1)
        self.comboBox_vpn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_vpn_pool.setMinimumSize(QtCore.QSize(160, 0))
        self.comboBox_vpn_pool.setObjectName(_fromUtf8("comboBox_vpn_pool"))
        self.gridLayout.addWidget(self.comboBox_vpn_pool, 5, 2, 1, 3)
        self.toolButton_assign_vpn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_vpn_from_pool.setObjectName(_fromUtf8("toolButton_assign_vpn_from_pool"))
        self.gridLayout.addWidget(self.toolButton_assign_vpn_from_pool, 5, 5, 1, 1)
        self.comboBox_ipn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_ipn_pool.setObjectName(_fromUtf8("comboBox_ipn_pool"))
        self.gridLayout.addWidget(self.comboBox_ipn_pool, 7, 2, 1, 3)
        self.toolButton_assign_ipn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_ipn_from_pool.setObjectName(_fromUtf8("toolButton_assign_ipn_from_pool"))
        self.gridLayout.addWidget(self.toolButton_assign_ipn_from_pool, 7, 5, 1, 1)
        self.label_vpn_ipv6_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_vpn_ipv6_address.setObjectName(_fromUtf8("label_vpn_ipv6_address"))
        self.gridLayout.addWidget(self.label_vpn_ipv6_address, 8, 0, 1, 1)
        self.lineEdit_vpn_ipv6_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_ipv6_address.setObjectName(_fromUtf8("lineEdit_vpn_ipv6_address"))
        self.gridLayout.addWidget(self.lineEdit_vpn_ipv6_address, 8, 1, 1, 1)
        self.comboBox_vpn_ipv6_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_vpn_ipv6_pool.setMinimumSize(QtCore.QSize(160, 0))
        self.comboBox_vpn_ipv6_pool.setObjectName(_fromUtf8("comboBox_vpn_ipv6_pool"))
        self.gridLayout.addWidget(self.comboBox_vpn_ipv6_pool, 8, 2, 1, 3)
        self.toolButton_assign_vpn_ipv6_from_pool_ = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_vpn_ipv6_from_pool_.setObjectName(_fromUtf8("toolButton_assign_vpn_ipv6_from_pool_"))
        self.gridLayout.addWidget(self.toolButton_assign_vpn_ipv6_from_pool_, 8, 5, 1, 1)
        self.label_ipn_ipv6_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_ipn_ipv6_address.setObjectName(_fromUtf8("label_ipn_ipv6_address"))
        self.gridLayout.addWidget(self.label_ipn_ipv6_address, 9, 0, 1, 1)
        self.lineEdit_ipn_ipv6_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_ipv6_address.setObjectName(_fromUtf8("lineEdit_ipn_ipv6_address"))
        self.gridLayout.addWidget(self.lineEdit_ipn_ipv6_address, 9, 1, 1, 1)
        self.comboBox_ipn_ipv6_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_ipn_ipv6_pool.setObjectName(_fromUtf8("comboBox_ipn_ipv6_pool"))
        self.gridLayout.addWidget(self.comboBox_ipn_ipv6_pool, 9, 2, 1, 3)
        self.toolButton_assign_ipn_ipv6_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_ipn_ipv6_from_pool.setObjectName(_fromUtf8("toolButton_assign_ipn_ipv6_from_pool"))
        self.gridLayout.addWidget(self.toolButton_assign_ipn_ipv6_from_pool, 9, 5, 1, 1)
        self.pushButton_detect_nas = QtGui.QPushButton(self.groupBox_link_parameters)
        self.pushButton_detect_nas.setObjectName(_fromUtf8("pushButton_detect_nas"))
        self.gridLayout.addWidget(self.pushButton_detect_nas, 12, 2, 1, 1)
        self.label_vlan = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_vlan.setObjectName(_fromUtf8("label_vlan"))
        self.gridLayout.addWidget(self.label_vlan, 14, 2, 1, 1)
        self.label_link_port = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_port.setObjectName(_fromUtf8("label_link_port"))
        self.gridLayout.addWidget(self.label_link_port, 14, 0, 1, 1)
        self.spinBox_link_port = QtGui.QSpinBox(self.groupBox_link_parameters)
        self.spinBox_link_port.setMaximum(512)
        self.spinBox_link_port.setObjectName(_fromUtf8("spinBox_link_port"))
        self.gridLayout.addWidget(self.spinBox_link_port, 14, 1, 1, 1)
        self.spinBox_vlan = QtGui.QSpinBox(self.groupBox_link_parameters)
        self.spinBox_vlan.setMaximum(4096)
        self.spinBox_vlan.setObjectName(_fromUtf8("spinBox_vlan"))
        self.gridLayout.addWidget(self.spinBox_vlan, 14, 3, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_link_parameters, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_3)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.groupBox_2 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.checkBox_allow_dhcp = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_dhcp.setObjectName(_fromUtf8("checkBox_allow_dhcp"))
        self.gridLayout_7.addWidget(self.checkBox_allow_dhcp, 0, 0, 1, 1)
        self.checkBox_allow_dhcp_with_null = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_dhcp_with_null.setObjectName(_fromUtf8("checkBox_allow_dhcp_with_null"))
        self.gridLayout_7.addWidget(self.checkBox_allow_dhcp_with_null, 1, 0, 1, 1)
        self.checkBox_allow_dhcp_with_minus = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_dhcp_with_minus.setObjectName(_fromUtf8("checkBox_allow_dhcp_with_minus"))
        self.gridLayout_7.addWidget(self.checkBox_allow_dhcp_with_minus, 2, 0, 1, 1)
        self.checkBox_allow_dhcp_with_block = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_dhcp_with_block.setObjectName(_fromUtf8("checkBox_allow_dhcp_with_block"))
        self.gridLayout_7.addWidget(self.checkBox_allow_dhcp_with_block, 3, 0, 1, 1)
        self.checkBox_associate_pptp_ipn_ip = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_associate_pptp_ipn_ip.setObjectName(_fromUtf8("checkBox_associate_pptp_ipn_ip"))
        self.gridLayout_7.addWidget(self.checkBox_associate_pptp_ipn_ip, 13, 0, 1, 1)
        self.checkBox_associate_pppoe_ipn_mac = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_associate_pppoe_ipn_mac.setObjectName(_fromUtf8("checkBox_associate_pppoe_ipn_mac"))
        self.gridLayout_7.addWidget(self.checkBox_associate_pppoe_ipn_mac, 14, 0, 1, 1)
        self.checkBox_allow_addonservice = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_addonservice.setObjectName(_fromUtf8("checkBox_allow_addonservice"))
        self.gridLayout_7.addWidget(self.checkBox_allow_addonservice, 15, 0, 1, 1)
        self.checkBox_allow_vpn_with_block = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_vpn_with_block.setObjectName(_fromUtf8("checkBox_allow_vpn_with_block"))
        self.gridLayout_7.addWidget(self.checkBox_allow_vpn_with_block, 9, 0, 1, 1)
        self.checkBox_allow_vpn_with_null = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_vpn_with_null.setObjectName(_fromUtf8("checkBox_allow_vpn_with_null"))
        self.gridLayout_7.addWidget(self.checkBox_allow_vpn_with_null, 8, 0, 1, 1)
        self.checkBox_allow_vpn_with_minus = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_vpn_with_minus.setObjectName(_fromUtf8("checkBox_allow_vpn_with_minus"))
        self.gridLayout_7.addWidget(self.checkBox_allow_vpn_with_minus, 7, 0, 1, 1)
        self.checkBox_allow_ipn_with_minus = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_ipn_with_minus.setObjectName(_fromUtf8("checkBox_allow_ipn_with_minus"))
        self.gridLayout_7.addWidget(self.checkBox_allow_ipn_with_minus, 12, 0, 1, 1)
        self.checkBox_allow_ipn_with_null = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_ipn_with_null.setObjectName(_fromUtf8("checkBox_allow_ipn_with_null"))
        self.gridLayout_7.addWidget(self.checkBox_allow_ipn_with_null, 11, 0, 1, 1)
        self.checkBox_allow_ipn_with_block = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_ipn_with_block.setObjectName(_fromUtf8("checkBox_allow_ipn_with_block"))
        self.gridLayout_7.addWidget(self.checkBox_allow_ipn_with_block, 10, 0, 1, 1)
        
        self.checkBox_allow_mac_update = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_allow_mac_update.setObjectName(_fromUtf8("checkBox_allow_mac_update"))
        self.gridLayout_7.addWidget(self.checkBox_allow_mac_update, 16, 0, 1, 1)

        
        self.gridLayout_6.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.frame = QtGui.QFrame(self.tab_2)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_4 = QtGui.QGridLayout(self.frame)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.commandLinkButton = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton.setObjectName(_fromUtf8("commandLinkButton"))
        self.gridLayout_4.addWidget(self.commandLinkButton, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame, 1, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.tab_2)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout_5.addWidget(self.tableWidget, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.lineEdit_ipn_ipv6_address.setDisabled(True)
        #self.lineEdit_vpn_ipv6_address.setDisabled(True)
        self.comboBox_ipn_ipv6_pool.setDisabled(True)
        #self.comboBox_vpn_ipv6_pool.setDisabled(True)
        self.toolButton_assign_ipn_ipv6_from_pool.setDisabled(True)
        #self.toolButton_assign_vpn_ipv6_from_pool_.setDisabled(True)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.fixtures()
        self.accountAddonServiceRefresh()

        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)
        
        self.connect(self.toolButton_assign_ipn_from_pool,QtCore.SIGNAL("clicked()"),self.get_ipn_from_pool)
        self.connect(self.toolButton_assign_vpn_from_pool,QtCore.SIGNAL("clicked()"),self.get_vpn_from_pool)
        
        self.connect(self.toolButton_assign_vpn_ipv6_from_pool_,QtCore.SIGNAL("clicked()"),self.get_vpn_ipv6_from_pool)
        
        self.connect(self.toolButton_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_password,QtCore.SIGNAL("clicked()"),self.generate_password)

        self.connect(self.toolButton_ipn_added,QtCore.SIGNAL("clicked()"),self.subaccountAddDel)
        self.connect(self.toolButton_ipn_enabled,QtCore.SIGNAL("clicked()"),self.subaccountEnableDisable)
        self.connect(self.toolButton_ipn_sleep,QtCore.SIGNAL("clicked()"),self.subAccountIpnSleep)
        
        self.connect(self.pushButton_detect_nas,QtCore.SIGNAL("clicked()"),self.detectMac)
        
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.addAddonService)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        
        
        
        
        self.connect(self.comboBox_vpn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_vpn_pool_action)
        self.connect(self.comboBox_vpn_ipv6_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_vpn_ipv6_pool_action)
        self.connect(self.comboBox_ipn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_ipn_pool_action)



    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры субаккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_link_parameters.setTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры связки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("SubAccountDialog", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_login.setText(QtGui.QApplication.translate("SubAccountDialog", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_password.setText(QtGui.QApplication.translate("SubAccountDialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn_ip_address.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN IPv4", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN IPv4", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_ipn_mac_address.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_switch.setText(QtGui.QApplication.translate("SubAccountDialog", "Коммутатор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN скорось", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SubAccountDialog", "IPN статусы", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_added.setText(QtGui.QApplication.translate("SubAccountDialog", "Не добавлен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_enabled.setText(QtGui.QApplication.translate("SubAccountDialog", "Не активен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_sleep.setText(QtGui.QApplication.translate("SubAccountDialog", "Управлять доступом", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_password.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_login.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_vpn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_ipn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ipv6_address.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN IPv6", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_vpn_ipv6_from_pool_.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_ipv6_address.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN IPv6", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_ipn_ipv6_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_detect_nas.setText(QtGui.QApplication.translate("SubAccountDialog", "Определить", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vlan.setText(QtGui.QApplication.translate("SubAccountDialog", "VLAN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_port.setText(QtGui.QApplication.translate("SubAccountDialog", "Порт", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("SubAccountDialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить выдачу адресов по DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pptp_ipn_ip.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPTP авторизацию к IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pppoe_ipn_mac.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPPOE авторизацию к IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_addonservice.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить активацию подключаемых услуг через веб-кабинет", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG/HotSpot авторизацию при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG/HotSpot авторизацию при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG/HotSpot авторизацию при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_mac_update.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить пользователю обновлять MAC-адрес через веб-кабинет", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("SubAccountDialog", "Дополнительные параметры", None, QtGui.QApplication.UnicodeUTF8))
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
        
        self.ipv6Validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$"), self)  

    def addrow(self, widget, value, x, y, id=None, editable=False, widget_type = None):
        headerItem = QtGui.QTableWidgetItem()
        if widget_type == 'checkbox':
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if value==None or value=="None":
            value=''
        if y==0:
            headerItem.id=value
        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))     
        elif type(value)==datetime.datetime:
            #.strftime(self.strftimeFormat)   
            headerItem.setData(QtCore.Qt.DisplayRole, QtCore.QString(unicode(value.strftime(strftimeFormat))))  
        else:            
            headerItem.setData(0, QtCore.QVariant(value))         
        if id:
            headerItem.id=id
            
           
        widget.setItem(x,y,headerItem)
    

        
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).text())
        except:
            return -1
        
    def subAccountIpnSleep(self):
        if self.toolButton_ipn_sleep.isChecked()==True:
            self.toolButton_ipn_sleep.setText(unicode(u"Не управлять доступом"))
        else:
            self.toolButton_ipn_sleep.setText(unicode(u"Управлять доступом"))
            
    def subaccountEnableDisable(self):
        if not self.model: return
        state = True if self.toolButton_ipn_enabled.isChecked() else False
        if state:
            res = self.connection.accountActions(None, self.model.id, 'enable')
            if not res.status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно. %s" % res.message))
                self.toolButton_ipn_enabled.setChecked(QtCore.Qt.Unchecked)
                self.toolButton_ipn_enabled.setText(unicode(u"Не активен"))
            else:
                self.toolButton_ipn_enabled.setText(unicode(u"Активен"))
        else:
             res = self.connection.accountActions(None, self.model.id, 'disable')
             if not res.status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно. %s" % res.message))
                self.toolButton_ipn_enabled.setChecked(QtCore.Qt.Checked)
                self.toolButton_ipn_enabled.setText(unicode(u"Активен"))
                #self.toolButton_ipn_enabled.set
             else:
                self.toolButton_ipn_enabled.setText(unicode(u"Не активен"))    
        #self.checkActions()
        
    def detectMac(self):
        nas_id=self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
        ipn_ip = unicode(self.lineEdit_ipn_ip_address.text())
        mac =''
        if nas_id and ipn_ip:
            res = self.connection.get_mac_for_ip(nas_id, ipn_ip)
            if not res.status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Невозможно определить адрес %s." % res.message))
                return
            mac = res.mac
        if mac:
            self.lineEdit_link_ipn_mac_address.setText(unicode(mac))
            
    def subaccountAddDel(self):
        if not self.model: return
        state = True if self.toolButton_ipn_added.isChecked() else False
        if state==True:
            res = self.connection.accountActions(None, self.model.id,  'create')
            if not res.status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно.%s" % res.message))
                self.toolButton_ipn_added.setChecked(QtCore.Qt.Unchecked)
                self.toolButton_ipn_added.setText(unicode(u"Не добавлен"))
            else:
                self.toolButton_ipn_added.setText(unicode(u"Добавлен"))
        else:
            res = self.connection.accountActions(None, self.model.id,  'delete')
            if not res.status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно. %s" % res.message))
                self.toolButton_ipn_added.setChecked(QtCore.Qt.Checked)
                self.toolButton_ipn_added.setText(unicode(u"Добавлен"))             
            else:
                self.toolButton_ipn_added.setText(unicode(u"Не добавлен"))

        #self.checkActions()

    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        child = AccountAddonServiceEdit(connection=self.connection, subaccount_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        try:
            model = self.connection.get_accountaddonservices(id=i)
           
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

    def combobox_vpn_ipv6_pool_action(self):
        if self.comboBox_vpn_ipv6_pool.itemData(self.comboBox_vpn_ipv6_pool.currentIndex()).toInt()[0]:
            self.lineEdit_vpn_ipv6_address.setDisabled(True)
            self.lineEdit_vpn_ipv6_address.setText(u"::")
        else:
            self.lineEdit_vpn_ipv6_address.setDisabled(False)

        
    def combobox_vpn_pool_action(self):
		#print self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
		if self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]:
			self.lineEdit_vpn_ip_address.setDisabled(True)
			self.lineEdit_vpn_ip_address.setText(u"0.0.0.0")
		else:
			self.lineEdit_vpn_ip_address.setDisabled(False)

    def accountAddonServiceRefresh(self):
        if self.model:

            sp = self.connection.get_accountaddonservices(subaccount_id=self.model.id, normal_fields=True)
            
            self.connection.commit()
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(sp))

            i=0
            for a in sp:
                self.addrow(self.tableWidget, a.id, i, 0)
                self.addrow(self.tableWidget, a.service, i, 1)
                self.addrow(self.tableWidget, a.activated, i, 2)
                try:
                    self.addrow(self.tableWidget, a.deactivated, i, 3)
                except:
                    self.addrow(self.tableWidget, u"Не закончен", i, 3)
                self.addrow(self.tableWidget, a.action_status, i, 4)
                try:
                    self.addrow(self.tableWidget, a.temporary_blocked, i, 5)
                except:
                    self.addrow(self.tableWidget, u"Нет", i, 5)
                i+=1
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.resizeColumnsToContents()
                    
    def fixtures(self):
        nasses=self.connection.get_nasses(fields=['id', 'name'])


        self.connection.commit()
        self.comboBox_nas.addItem(u"---Любой---", QtCore.QVariant(''))
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name, QtCore.QVariant(nas.id))

        switches=self.connection.get_switches(fields=['id', 'name'])

        self.connection.commit()
        
        self.comboBox_link_switch_id.addItem(u"---Не указан---", QtCore.QVariant(''))
        for switch in switches:
            self.comboBox_link_switch_id.addItem(switch.name, QtCore.QVariant(switch.id))
            
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            if self.model.vpn_ipinuse:
                d = self.connection.get_pool_by_ipinuse(ipinuse=self.model.vpn_ipinuse)
                if not d.status:
                     QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе не найден пул, из которого был выдан vpn ip адрес."))
                pool_id = d.result

            
        pools = self.connection.get_ippools(type=0)


        #self.connection.get_models("billservice_ippool", where={'type':'0',})
        
        self.connection.commit()
        i=1
        self.comboBox_vpn_pool.clear()
        self.comboBox_vpn_pool.addItem('---')
        self.comboBox_vpn_pool.setItemData(0, QtCore.QVariant(''))
        for pool in pools:
            self.comboBox_vpn_pool.addItem(pool.name)
            self.comboBox_vpn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.ipv4_vpn_pool:
                    if pool.id==self.model.ipv4_vpn_pool:
                        self.comboBox_vpn_pool.setCurrentIndex(i)
                        self.lineEdit_vpn_ip_address.setDisabled(True)  
                elif self.model.vpn_ipinuse:
                    if pool.id==pool_id:
                        self.comboBox_vpn_pool.setCurrentIndex(i)
                        self.lineEdit_vpn_ip_address.setDisabled(True)
            i+=1

        if self.model:
            if self.model.vpn_ipv6_ipinuse:
                d = self.connection.get_pool_by_ipinuse(ipinuse=self.model.vpn_ipv6_ipinuse)
                if not d.status:
                     QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе не найден пул, из которого был выдан ipv6 vpn ip адрес."))
                ipv6_pool_id = d.result
                
            
        pools = self.connection.get_ippools(type=2)

        
        self.connection.commit()
        i=1
        self.comboBox_vpn_ipv6_pool.clear()
        self.comboBox_vpn_ipv6_pool.addItem('---')
        self.comboBox_vpn_ipv6_pool.setItemData(0, QtCore.QVariant(''))
        for pool in pools:
            self.comboBox_vpn_ipv6_pool.addItem(pool.name)
            self.comboBox_vpn_ipv6_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.vpn_ipv6_ipinuse:
                    if pool.id==ipv6_pool_id:
                        self.comboBox_vpn_ipv6_pool.setCurrentIndex(i)
                        self.lineEdit_vpn_ipv6_address.setDisabled(True)
            i+=1
                        
                        
        if not self.model: self.groupBox.setDisabled(True)

        if self.model:
            if self.model.ipn_ipinuse:
                d = self.connection.get_pool_by_ipinuse(ipinuse=self.model.ipn_ipinuse)
                if not d.status:
                     QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе не найден пул, из которого был выдан ipn ip адрес."))
                pool_id = d.result
        
        pools = self.connection.get_ippools(type=1)


        self.connection.commit()
        i=1
        self.comboBox_ipn_pool.clear()
        self.comboBox_ipn_pool.addItem('---')
        self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(''))
        for pool in pools:
            self.comboBox_ipn_pool.addItem(pool.name)
            self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.ipn_ipinuse:
                    if pool.id==pool_id:
                        self.comboBox_ipn_pool.setCurrentIndex(i)
                        self.lineEdit_ipn_ip_address.setDisabled(True)
            i+=1

            
        if self.model:
            #print "NAS_ID", self.model.nas_id
            if self.model.nas:
                self.comboBox_nas.setCurrentIndex(self.comboBox_nas.findData(self.model.nas))
            if self.model.switch:
                self.comboBox_link_switch_id.setCurrentIndex(self.comboBox_link_switch_id.findData(self.model.switch))                
            self.lineEdit_link_login.setText(unicode(self.model.username))
            self.lineEdit_link_password.setText(unicode(self.model.password))
            self.lineEdit_vpn_ip_address.setText(unicode(self.model.vpn_ip_address))
            self.lineEdit_vpn_ipv6_address.setText(unicode(self.model.vpn_ipv6_ip_address))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
            self.lineEdit_link_ipn_mac_address.setText(unicode(self.model.ipn_mac_address))
            self.spinBox_link_port.setValue(self.model.switch_port if self.model.switch_port else 0)
            self.spinBox_vlan.setValue(self.model.vlan if self.model.vlan else 0)
            self.checkBox_allow_dhcp.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_block==True else QtCore.Qt.Unchecked )
            
            self.checkBox_allow_vpn_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_block==True else QtCore.Qt.Unchecked )

            self.checkBox_allow_ipn_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_ipn_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_ipn_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_block==True else QtCore.Qt.Unchecked )
            
            self.checkBox_associate_pppoe_ipn_mac.setCheckState(QtCore.Qt.Checked if self.model.associate_pppoe_ipn_mac==True else QtCore.Qt.Unchecked )
            self.checkBox_associate_pptp_ipn_ip.setCheckState(QtCore.Qt.Checked if self.model.associate_pptp_ipn_ip==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_addonservice.setCheckState(QtCore.Qt.Checked if self.model.allow_addonservice==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_mac_update.setCheckState(QtCore.Qt.Checked if self.model.allow_mac_update==True else QtCore.Qt.Unchecked )
            self.lineEdit_vpn_speed.setText(unicode(self.model.vpn_speed))
            self.lineEdit_ipn_speed.setText(unicode(self.model.ipn_speed))
            self.checkActions()
            
    def checkActions(self):
        if self.model.ipn_sleep:
            self.toolButton_ipn_sleep.setChecked(self.model.ipn_sleep)
            self.toolButton_ipn_sleep.setText(unicode(u"Не управлять"))
        
        if self.model.ipn_added:
            self.toolButton_ipn_added.setChecked(self.model.ipn_added)
            self.toolButton_ipn_added.setText(unicode(u"Добавлен"))
        
        if self.model.ipn_enabled:
            self.toolButton_ipn_enabled.setChecked(self.model.ipn_enabled)
            self.toolButton_ipn_enabled.setText(unicode(u"Активен"))         
            
            #self.combobox_vpn_pool_action()
            #self.combobox_ipn_pool_action()
                        
    def accept(self):
        if self.model:
            model=self.model
        else:
            model = AttrDict()
            model.account = self.account.id
            
        if self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]!=0:
            model.nas = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0] or ''
        else:
            model.nas = None
        
        if self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0]!=0:
            model.switch = self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0] or ''
        else:
            model.switch = None
        
        model.switch_port = int(self.spinBox_link_port.value() or 0)
        model.vlan = int(self.spinBox_vlan.value() or 0)
        model.username = unicode(self.lineEdit_link_login.text()) or ""
        model.password = unicode(self.lineEdit_link_password.text()) or ""
        #model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"
        #model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"


            
        if self.lineEdit_ipn_ip_address.text():
			if self.ipnValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания IPN IP адреса."))
				self.connection.rollback()
				return

        model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"
		
				
        if self.lineEdit_vpn_ip_address.text():
			if self.ipValidator.validate(self.lineEdit_vpn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания VPN IP адреса."))
				self.connection.rollback()
				return

			
        model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"

        if self.lineEdit_vpn_ipv6_address.text():
            if self.lineEdit_vpn_ipv6_address.text()!='::' and self.ipv6Validator.validate(self.lineEdit_vpn_ipv6_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания IPv6 VPN IP адреса."))
                self.connection.rollback()
                return

            
        model.vpn_ipv6_ip_address = unicode(self.lineEdit_vpn_ipv6_address.text()) or "::"
        
        #---------------
        if self.lineEdit_link_ipn_mac_address.text().isEmpty()==False:
			if self.macValidator.validate(self.lineEdit_link_ipn_mac_address.text(), 0)[0]  == QtGui.QValidator.Acceptable:

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
        
        model.allow_ipn_with_null = self.checkBox_allow_ipn_with_null.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_minus = self.checkBox_allow_ipn_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_block = self.checkBox_allow_ipn_with_block.checkState()==QtCore.Qt.Checked

        model.associate_pppoe_ipn_mac = self.checkBox_associate_pppoe_ipn_mac.checkState()==QtCore.Qt.Checked
        model.associate_pptp_ipn_ip = self.checkBox_associate_pptp_ipn_ip.checkState()==QtCore.Qt.Checked
        model.allow_addonservice = self.checkBox_allow_addonservice.checkState()==QtCore.Qt.Checked
        model.allow_mac_update = self.checkBox_allow_mac_update.checkState()==QtCore.Qt.Checked
        model.vpn_speed=unicode(self.lineEdit_vpn_speed.text()) or ""
        model.ipn_speed=unicode(self.lineEdit_ipn_speed.text()) or ""
        model.ipn_sleep = self.toolButton_ipn_sleep.isChecked()
        model.ipn_added = self.toolButton_ipn_added.isChecked()
        model.ipn_enabled = self.toolButton_ipn_enabled.isChecked()
        
        if self.model:
            if model.ipn_ip_address!=self.model.ipn_ip_address or model.ipn_mac_address!=self.model.ipn_mac_address:
                """
                Если изменили IPN IP адрес-значит нужно добавить новый адрес в лист доступа
                """
                model.ipn_added=False        
                model.ipn_enabled=False        
        model.speed=''
        #Операции с пулом    
    
        pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0] or ''
        if pool_id and model.ipn_ip_address==u'0.0.0.0':
            QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали IPN пул, но не назначили ip адрес."))
            return 
        model.ipv4_ipn_pool = pool_id

        pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0] or ''
        model.ipv4_vpn_pool = pool_id   
         #Операции с vpn ipv6 пулом    

        pool_id = self.comboBox_vpn_ipv6_pool.itemData(self.comboBox_vpn_ipv6_pool.currentIndex()).toInt()[0] or ''
        if pool_id and model.vpn_ipv6_ip_address=='::' and model.vpn_ipv6_ip_address=='':
            QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали IPV6 VPN пул, но не назначили ip адрес."))
            self.connection.rollback()
            return             
        model.ipv6_ipn_pool = pool_id

        
            

        d = self.connection.subaccount_save(model)
        if d.status==True:
            model.id = d.account_id
            self.model = model
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
                
    def get_vpn_ipv6_from_pool(self):
        pool_id = self.comboBox_vpn_ipv6_pool.itemData(self.comboBox_vpn_ipv6_pool.currentIndex()).toInt()[0]
        if pool_id!=0:
            child = IPAddressSelectForm(self.connection, pool_id)
            if child.exec_()==1:
                self.lineEdit_vpn_ipv6_address.setText(child.selected_ip)        

class AddAccountTarif(QtGui.QDialog):
    def __init__(self, connection, account=None, get_info=False, model=None):
        super(AddAccountTarif, self).__init__()
        self.model=model
        self.get_info = get_info
        self.account=account
        self.connection = connection
        self.connection.commit()

        self.resize(460, 113)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_tarif = QtGui.QLabel(self)
        self.label_tarif.setObjectName(_fromUtf8("label_tarif"))
        self.gridLayout.addWidget(self.label_tarif, 1, 0, 1, 1)
        self.comboBox_tarif = QtGui.QComboBox(self)
        self.comboBox_tarif.setObjectName(_fromUtf8("comboBox_tarif"))
        self.gridLayout.addWidget(self.comboBox_tarif, 1, 1, 1, 2)
        self.label_start = QtGui.QLabel(self)
        self.label_start.setObjectName(_fromUtf8("label_start"))
        self.gridLayout.addWidget(self.label_start, 2, 0, 1, 1)
        self.dateTimeEdit_start = CustomDateTimeWidget()
        self.dateTimeEdit_start.setObjectName(_fromUtf8("dateTimeEdit_start"))
        self.gridLayout.addWidget(self.dateTimeEdit_start, 2, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 2)
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_accounttarif_start = QtGui.QLabel(self)
        self.label_accounttarif_start.setText(_fromUtf8(""))
        self.label_accounttarif_start.setObjectName(_fromUtf8("label_accounttarif_start"))
        self.gridLayout.addWidget(self.label_accounttarif_start, 0, 1, 1, 2)




        self.retranslateUi()
        self.fixtures()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)

    def accept(self):
        if self.account and self.get_info==False:
            date=self.dateTimeEdit_start.currentDate()
            #print repr(date)
            #print str(self.date_edit.dateTime().toString())
            date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
            if self.model:
                model=self.model
                model.datetime = date
            else:
                model = AttrDict()
                model.account = self.account.id
                model.tarif =self.comboBox_tarif.itemData(self.comboBox_tarif.currentIndex()).toInt()[0]
                model.datetime = date
                
                #AccountTarif.objects.create(account=self.account, tarif=tarif, datetime=date)

            res = self.connection.accounttarif_save(model)
            if not res:
                return
        QtGui.QDialog.accept(self)


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Смена тарифного плана", None, QtGui.QApplication.UnicodeUTF8))   
        self.label_tarif.setText(QtGui.QApplication.translate("AddAccountTarif", "Укажите новый тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.label_start.setText(QtGui.QApplication.translate("AddAccountTarif", "Дата начала", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddAccountTarif", "Начало текущего тарифа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_accounttarif_start.setText(QtGui.QApplication.translate("AddAccountTarif", "-", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        tarifs=self.connection.get_tariffs(fields=['id', 'name'])
        self.connection.commit()
        for tarif in tarifs:
            self.comboBox_tarif.addItem(tarif.name, QtCore.QVariant(tarif.id))
        now=datetime.datetime.now()
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            self.comboBox_tarif.setCurrentIndex(self.comboBox_tarif.findData(self.model.tarif_id))

            now = QtCore.QDateTime()

            now.setTime_t((mktime(self.model.datetime.timetuple())))
        self.dateTimeEdit_start.setDateTime(now)
        
        
        if self.account:
            curat = self.connection.sql("SELECT datetime FROM billservice_accounttarif WHERE datetime<now() and account_id=%s ORDER BY datetime DESC LIMIT 1" % self.account.id)
            self.connection.commit()
            if curat:
                self.label_accounttarif_start.setText(unicode(curat[0].datetime.strftime(strftimeFormat)))

    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)
        

            
            
class AccountWindow(QtGui.QMainWindow):
    def __init__(self, connection, tarif_id, ttype, model=None, ipn_for_vpn=False, parent=None):
        super(AccountWindow, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection
        self.ipn_for_vpn = ipn_for_vpn
        self.tarif_id = tarif_id
        self.organization = None
        self.bank = None
        self.tab_loaded = []
        self.parent_window=parent
        self.setObjectName("AccountWindow")
        bhdr = HeaderUtil.getBinaryHeader('AccountWindow-account_info')
        self.resize(851, 680)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_general = QtGui.QWidget()
        self.tab_general.setObjectName("tab_general")
        self.gridLayout_8 = QtGui.QGridLayout(self.tab_general)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.groupBox_account_data = QtGui.QGroupBox(self.tab_general)
        #self.groupBox_account_data.setMinimumSize(QtCore.QSize(381, 82))
        #self.groupBox_account_data.setMaximumSize(QtCore.QSize(381, 86))
        self.groupBox_account_data.setObjectName("groupBox_account_data")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_account_data)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_username = QtGui.QLabel(self.groupBox_account_data)
        self.label_username.setMinimumSize(QtCore.QSize(70, 0))
        self.label_username.setObjectName("label_username")
        self.gridLayout_3.addWidget(self.label_username, 0, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox_account_data)
        self.lineEdit_username.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.gridLayout_3.addWidget(self.lineEdit_username, 0, 1, 1, 1)
        self.toolButton_generate_login = QtGui.QToolButton(self.groupBox_account_data)
        self.toolButton_generate_login.setEnabled(True)
        self.toolButton_generate_login.setObjectName("toolButton_generate_login")
        self.gridLayout_3.addWidget(self.toolButton_generate_login, 0, 2, 1, 1)
        self.label_password = QtGui.QLabel(self.groupBox_account_data)
        self.label_password.setObjectName("label_password")
        self.gridLayout_3.addWidget(self.label_password, 1, 0, 1, 1)
        self.lineEdit_password = QtGui.QLineEdit(self.groupBox_account_data)
        self.lineEdit_password.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout_3.addWidget(self.lineEdit_password, 1, 1, 1, 1)
        self.toolButton_generate_password = QtGui.QToolButton(self.groupBox_account_data)
        self.toolButton_generate_password.setObjectName("toolButton_generate_password")
        self.gridLayout_3.addWidget(self.toolButton_generate_password, 1, 2, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_account_data, 0, 0, 1, 1)
        self.groupBox_agreement = QtGui.QGroupBox(self.tab_general)
        self.groupBox_agreement.setMinimumSize(QtCore.QSize(391, 86))
        self.groupBox_agreement.setMaximumSize(QtCore.QSize(3910, 84))
        self.groupBox_agreement.setObjectName("groupBox_agreement")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_agreement)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_agreement_date = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_date.setObjectName("label_agreement_date")
        self.gridLayout_4.addWidget(self.label_agreement_date, 0, 0, 1, 1)
        self.label_agreement_num = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_num.setObjectName("label_agreement_num")
        self.gridLayout_4.addWidget(self.label_agreement_num, 1, 0, 1, 1)
        self.comboBox_agreement_num = QtGui.QComboBox(self.groupBox_agreement)
        self.comboBox_agreement_num.setEditable(True)
        #self.comboBox_agreement_num.mouseDoubleClickEvent=self.mouseDoubleClickEvent
        #self.comboBox_agreement_num.setMinimumSize(QtCore.QSize(0, 20))
        self.comboBox_agreement_num.setObjectName("comboBox_agreement_num")
        self.gridLayout_4.addWidget(self.comboBox_agreement_num, 1, 2, 1, 1)
        self.toolButton_agreement_print = QtGui.QToolButton(self.groupBox_agreement)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/document-print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_agreement_print.setIcon(icon)
        self.toolButton_agreement_print.setObjectName("toolButton_agreement_print")
        self.gridLayout_4.addWidget(self.toolButton_agreement_print, 1, 3, 1, 1)
        self.dateTimeEdit_agreement_date = CustomDateTimeWidget()#QtGui.QDateTimeEdit(self.groupBox_agreement)
        #self.dateTimeEdit_agreement_date.setCalendarPopup(True)
        self.dateTimeEdit_agreement_date.setObjectName("dateTimeEdit_agreement_date")
        self.gridLayout_4.addWidget(self.dateTimeEdit_agreement_date, 0, 2, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_agreement, 0, 1, 1, 1)
        self.groupBox_account_info = QtGui.QGroupBox(self.tab_general)
        #self.groupBox_account_info.setMinimumSize(QtCore.QSize(381, 211))
        #self.groupBox_account_info.setMaximumSize(QtCore.QSize(381, 16381))
        self.groupBox_account_info.setObjectName("groupBox_account_info")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_account_info)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget = QtGui.QTableWidget(self.groupBox_account_info)
        #self.tableWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setObjectName("AccountWindow-account_info")
        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_account_info, 1, 0, 4, 1)

        self.groupBox_urdata = QtGui.QGroupBox(self.tab_general)
        self.groupBox_urdata.setMinimumSize(QtCore.QSize(391, 0))
        self.groupBox_urdata.setMaximumSize(QtCore.QSize(16381, 16381))
        self.groupBox_urdata.setCheckable(True)
        self.groupBox_urdata.setChecked(False)
        self.groupBox_urdata.setObjectName("groupBox_urdata")
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_urdata)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_organization = QtGui.QLabel(self.groupBox_urdata)
        self.label_organization.setObjectName("label_organization")
        self.gridLayout_7.addWidget(self.label_organization, 0, 0, 1, 1)
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_organization.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.gridLayout_7.addWidget(self.lineEdit_organization, 0, 1, 1, 4)
        self.label_bank = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank.setObjectName("label_bank")
        self.gridLayout_7.addWidget(self.label_bank, 13, 0, 1, 1)
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.gridLayout_7.addWidget(self.lineEdit_bank, 13, 1, 1, 1)
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_uraddress.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.gridLayout_7.addWidget(self.lineEdit_uraddress, 6, 1, 1, 4)
        self.label_uraddress = QtGui.QLabel(self.groupBox_urdata)
        self.label_uraddress.setObjectName("label_uraddress")
        self.gridLayout_7.addWidget(self.label_uraddress, 6, 0, 1, 1)
        self.lineEdit_urphone = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_urphone.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_urphone.setObjectName("lineEdit_urphone")
        self.gridLayout_7.addWidget(self.lineEdit_urphone, 7, 1, 1, 4)
        self.label_urphone = QtGui.QLabel(self.groupBox_urdata)
        self.label_urphone.setObjectName("label_urphone")
        self.gridLayout_7.addWidget(self.label_urphone, 7, 0, 1, 1)
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_fax.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.gridLayout_7.addWidget(self.lineEdit_fax, 8, 1, 1, 4)
        self.label_fax = QtGui.QLabel(self.groupBox_urdata)
        self.label_fax.setObjectName("label_fax")
        self.gridLayout_7.addWidget(self.label_fax, 8, 0, 1, 1)
        self.label_bank_code = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank_code.setObjectName("label_bank_code")
        self.gridLayout_7.addWidget(self.label_bank_code, 13, 3, 1, 1)
        self.lineEdit_bank_code = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank_code.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_bank_code.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_bank_code.setObjectName("lineEdit_bank_code")
        self.gridLayout_7.addWidget(self.lineEdit_bank_code, 13, 4, 1, 1)
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_unp.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.gridLayout_7.addWidget(self.lineEdit_unp, 1, 1, 1, 4)
        self.label_unp = QtGui.QLabel(self.groupBox_urdata)
        self.label_unp.setObjectName("label_unp")
        self.gridLayout_7.addWidget(self.label_unp, 1, 0, 1, 1)
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_okpo.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.gridLayout_7.addWidget(self.lineEdit_okpo, 3, 1, 1, 4)
        self.label_okpo = QtGui.QLabel(self.groupBox_urdata)
        self.label_okpo.setObjectName("label_okpo")
        self.gridLayout_7.addWidget(self.label_okpo, 3, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_urdata)
        self.label.setObjectName("label")
        self.gridLayout_7.addWidget(self.label, 2, 0, 1, 1)
        self.lineEdit_kpp = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_kpp.setObjectName("lineEdit_kpp")
        self.gridLayout_7.addWidget(self.lineEdit_kpp, 2, 1, 1, 4)
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_rs.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.gridLayout_7.addWidget(self.lineEdit_rs, 4, 1, 1, 4)
        self.label_rs = QtGui.QLabel(self.groupBox_urdata)
        self.label_rs.setObjectName("label_rs")
        self.gridLayout_7.addWidget(self.label_rs, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_urdata)
        self.label_2.setObjectName("label_2")
        self.gridLayout_7.addWidget(self.label_2, 5, 0, 1, 1)
        self.lineEdit_kor_s = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_kor_s.setObjectName("lineEdit_kor_s")
        self.gridLayout_7.addWidget(self.lineEdit_kor_s, 5, 1, 1, 4)
        self.gridLayout_8.addWidget(self.groupBox_urdata, 1, 1, 1, 1)
        self.groupBox_balance_info = QtGui.QGroupBox(self.tab_general)
        self.groupBox_balance_info.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_balance_info.setMaximumSize(QtCore.QSize(3910, 1656465))
        self.groupBox_balance_info.setObjectName("groupBox_balance_info")
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_balance_info)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_balance = QtGui.QLabel(self.groupBox_balance_info)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_9.addWidget(self.label_balance, 0, 0, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_balance.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_balance.setDisabled(True)
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.gridLayout_9.addWidget(self.lineEdit_balance, 0, 1, 1, 1)
        self.label_credit = QtGui.QLabel(self.groupBox_balance_info)
        self.label_credit.setObjectName("label_credit")
        self.gridLayout_9.addWidget(self.label_credit, 1, 0, 1, 1)
        self.lineEdit_credit = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_credit.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_credit.setObjectName("lineEdit_credit")
        self.gridLayout_9.addWidget(self.lineEdit_credit, 1, 1, 1, 1)
        self.checkBox_credit = QtGui.QCheckBox(self.groupBox_balance_info)
        self.checkBox_credit.setEnabled(False)
        self.checkBox_credit.setChecked(True)
        self.checkBox_credit.setObjectName("checkBox_credit")
        self.gridLayout_9.addWidget(self.checkBox_credit, 2, 0, 1, 2)
        self.gridLayout_8.addWidget(self.groupBox_balance_info, 2, 1, 2, 1)
        self.groupBox_status = QtGui.QGroupBox(self.tab_general)
        self.groupBox_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_status.setObjectName("groupBox_status")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_status)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_status = QtGui.QComboBox(self.groupBox_status)
        self.comboBox_status.setObjectName("comboBox_status")
        self.horizontalLayout.addWidget(self.comboBox_status)
        
        self.groupBox_management_info = QtGui.QGroupBox(self.tab_general)
        self.gridLayout_management = QtGui.QGridLayout(self.groupBox_management_info)
        #self.label_manager = QtGui.QLabel(self.groupBox_management_info)
        #self.gridLayout_management.addWidget(self.label_manager,0,0,1,1)
        self.comboBox_manager = QtGui.QComboBox(self.groupBox_management_info)
        self.gridLayout_management.addWidget(self.comboBox_manager,0,1,1,1)
        self.gridLayout_8.addWidget(self.groupBox_management_info, 5, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_status, 6, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_general)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_19 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.plainTextEdit_comment = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit_comment.setObjectName("plainTextEdit_comment")
        self.gridLayout_19.addWidget(self.plainTextEdit_comment, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox, 5, 1, 2, 1)
        self.tabWidget.addTab(self.tab_general, "")

        self.tab_subaccounts = QtGui.QWidget()
        self.tab_subaccounts.setObjectName("tab_subaccounts")
        self.gridLayout_51 = QtGui.QGridLayout(self.tab_subaccounts)
        self.gridLayout_51.setObjectName("gridLayout_51")
        self.tableWidget_subaccounts = QtGui.QTableWidget(self.tab_subaccounts)
        self.tableWidget_subaccounts.setObjectName("tableWidget_subaccounts")
        self.tableWidget_subaccounts = tableFormat(self.tableWidget_subaccounts)
        self.gridLayout_51.addWidget(self.tableWidget_subaccounts, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_subaccounts, "")        
        #-----
        self.tab_network_settings = QtGui.QWidget()
        self.tab_network_settings.setObjectName("tab_network_settings")
        self.gridLayout_17 = QtGui.QGridLayout(self.tab_network_settings)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.groupBox_nas = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_nas.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_nas.setMaximumSize(QtCore.QSize(11791, 11791))
        self.groupBox_nas.setObjectName("groupBox_nas")
        self.gridLayout_14 = QtGui.QGridLayout(self.groupBox_nas)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.label_nas = QtGui.QLabel(self.groupBox_nas)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_14.addWidget(self.label_nas, 0, 0, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_nas)
        self.comboBox_nas.setMinimumSize(QtCore.QSize(350, 20))
        self.comboBox_nas.setMaximumSize(QtCore.QSize(16777215, 20))
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout_14.addWidget(self.comboBox_nas, 0, 1, 1, 1)
        
        self.label_max_promise = QtGui.QLabel(self.groupBox_nas)
        self.label_max_promise.setObjectName("label_max_promise")
        self.gridLayout_14.addWidget(self.label_max_promise, 1, 0, 1, 1)
        self.lineEdit_max_promise = QtGui.QLineEdit(self.groupBox_nas)
        self.lineEdit_max_promise.setMaximumWidth(200)
        self.lineEdit_max_promise.setObjectName("lineEdit_max_promise")
        self.gridLayout_14.addWidget(self.lineEdit_max_promise, 1, 1, 1, 1)

        self.label_block_writeoff_summ = QtGui.QLabel(self.groupBox_nas)
        self.gridLayout_14.addWidget(self.label_block_writeoff_summ, 2, 0, 1, 1)
        self.lineEdit_block_writeoff_summ = QtGui.QLineEdit(self.groupBox_nas)

        self.gridLayout_14.addWidget(self.lineEdit_block_writeoff_summ, 2, 1, 1, 1)
        
        self.gridLayout_17.addWidget(self.groupBox_nas, 0, 0, 1, 2)
        
####
        self.groupBox_ipn_status = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_ipn_status.setObjectName(_fromUtf8("groupBox_ipn_status"))
        self.horizontalLayout_ipn_status = QtGui.QHBoxLayout(self.groupBox_ipn_status)
        self.horizontalLayout_ipn_status.setObjectName(_fromUtf8("horizontalLayout_ipn_status"))
        self.toolButton_ipn_added = QtGui.QToolButton(self.groupBox_ipn_status)
        self.toolButton_ipn_added.setCheckable(True)
        self.toolButton_ipn_added.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton_ipn_added.setObjectName(_fromUtf8("toolButton_ipn_added"))
        self.horizontalLayout_ipn_status.addWidget(self.toolButton_ipn_added)
        self.toolButton_ipn_enabled = QtGui.QToolButton(self.groupBox_ipn_status)
        self.toolButton_ipn_enabled.setCheckable(True)
        self.toolButton_ipn_enabled.setObjectName(_fromUtf8("toolButton_ipn_enabled"))
        self.horizontalLayout_ipn_status.addWidget(self.toolButton_ipn_enabled)
        self.toolButton_ipn_sleep = QtGui.QToolButton(self.groupBox_ipn_status)
        self.toolButton_ipn_sleep.setCheckable(True)
        self.toolButton_ipn_sleep.setObjectName(_fromUtf8("toolButton_ipn_sleep"))
        self.horizontalLayout_ipn_status.addWidget(self.toolButton_ipn_sleep)
        self.gridLayout_17.addWidget(self.groupBox_ipn_status, 1, 0, 1, 2)
####
        self.groupBox_accessparameters = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_accessparameters.setObjectName("groupBox_accessparameters")
        self.gridLayout_16 = QtGui.QGridLayout(self.groupBox_accessparameters)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.checkBox_allow_webcab = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_webcab.setObjectName("checkBox_allow_webcab")
        self.gridLayout_16.addWidget(self.checkBox_allow_webcab, 0, 0, 1, 1)
        self.checkBox_allow_expresscards = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_expresscards.setObjectName("checkBox_allow_expresscards")
        self.gridLayout_16.addWidget(self.checkBox_allow_expresscards, 1, 0, 1, 1)
        self.checkBox_allow_ipn_with_minus = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_ipn_with_minus.setObjectName("checkBox_allow_ipn_with_minus")
        self.gridLayout_16.addWidget(self.checkBox_allow_ipn_with_minus, 2, 0, 1, 1)
        self.checkBox_allow_ipn_with_block = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_ipn_with_block.setObjectName("checkBox_allow_ipn_with_block")
        self.gridLayout_16.addWidget(self.checkBox_allow_ipn_with_block, 4, 0, 1, 1)
        self.checkBox_allow_ipn_with_null = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_ipn_with_null.setObjectName("checkBox_allow_ipn_with_null")
        self.gridLayout_16.addWidget(self.checkBox_allow_ipn_with_null, 3, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_accessparameters, 2, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_17.addItem(spacerItem, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab_network_settings, "")
        
        self.tab_suspended = QtGui.QWidget()
        self.tab_suspended.setObjectName("tab_suspended")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_suspended)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.tableWidget_suspended = QtGui.QTableWidget(self.tab_suspended)
        self.tableWidget_suspended.setObjectName("tableWidget_suspended")
        self.gridLayout_5.addWidget(self.tableWidget_suspended, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_suspended, "")
#        

        
#        
        self.tab_tarifs = QtGui.QWidget()
        self.tab_tarifs.setObjectName("tab_tarifs")
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_tarifs)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.tableWidget_accounttarif = QtGui.QTableWidget(self.tab_tarifs)
        self.tableWidget_accounttarif.setObjectName("tableWidget_accounttarif")
        self.gridLayout_6.addWidget(self.tableWidget_accounttarif, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_tarifs, "")
        self.tab_addonservice = QtGui.QWidget()
        self.tab_addonservice.setObjectName("tab_addonservice")
        self.gridLayout_7 = QtGui.QGridLayout(self.tab_addonservice)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.tableWidget_addonservice = QtGui.QTableWidget(self.tab_addonservice)
        self.tableWidget_addonservice.setObjectName("tableWidget_addonservice")
        self.gridLayout_7.addWidget(self.tableWidget_addonservice, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_addonservice, "")
        
        self.tab_accounthardware = QtGui.QWidget()
        self.tab_accounthardware.setObjectName("tab_accounthardware")
        self.gridLayout_8 = QtGui.QGridLayout(self.tab_accounthardware)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.tableWidget_accounthardware = QtGui.QTableWidget(self.tab_accounthardware)

        self.tableWidget_accounthardware.setObjectName("tableWidget_accounthardware")
        self.gridLayout_8.addWidget(self.tableWidget_accounthardware, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_accounthardware, "")
        
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSave = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave.setObjectName("actionSave")
        self.actionAdd = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd.setIcon(icon2)
        self.actionAdd.setObjectName("actionAdd")
        self.actionDel = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDel.setIcon(icon3)
        self.actionDel.setObjectName("actionDel")
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionAdd)
        self.toolBar.addAction(self.actionDel)

        #font = QtGui.QFont()
        
        #font.setPointSize(font.pointSize() - 1);
        #ui->comboBox->setFont(font);
        self.comboBox_city = QtGui.QComboBox(self.tableWidget)
        #self.comboBox_city.setFont(font)
        self.comboBox_city.setFixedHeight(19)
        self.comboBox_street = QtGui.QComboBox(self.tableWidget)
        #self.comboBox_street.setFont(font)
        self.comboBox_street.setFixedHeight(19)
        self.comboBox_house = QtGui.QComboBox(self.tableWidget)
        #self.comboBox_house.setFont(font)
        self.comboBox_house.setFixedHeight(19)
        
        #self.comboBox_city.setEditable(True)
        #self.comboBox_street.setEditable(True)
        #self.comboBox_house.setEditable(True)
        
        self.retranslateUi()
        HeaderUtil.nullifySaved(self.tableWidget.objectName())
        self.firsttime = True
        
        self.tabWidget.setCurrentIndex(0)
        
        QtCore.QMetaObject.connectSlotsByName(self)

        
        self.connect(self.toolButton_generate_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_generate_password,QtCore.SIGNAL("clicked()"),self.generate_password)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        #self.connect(self.checkBox_assign_ipn_ip_from_dhcp, QtCore.SIGNAL("stateChanged(int)"), self.dhcpActions)
        self.connect(self.tableWidget_accounttarif, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)
        self.connect(self.tableWidget_addonservice, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        self.connect(self.tableWidget_suspended, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_suspendedperiod)
        self.connect(self.tableWidget_subaccounts, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editSubAccount)
        self.connect(self.tableWidget_accounthardware, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAccounthardware)
        
        self.connect(self.comboBox_city, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_street)
        self.connect(self.comboBox_street, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_house)
        
        
        self.connect(self.tableWidget, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.editAccountInfo)
        
        self.connect(self.actionAdd, QtCore.SIGNAL("triggered()"), self.add_action)
        self.connect(self.actionDel, QtCore.SIGNAL("triggered()"), self.del_action)
        self.connect(self.toolButton_agreement_print, QtCore.SIGNAL("clicked()"), self.printAgreement)

        self.connect(self.toolButton_ipn_added,QtCore.SIGNAL("clicked()"),self.subaccountAddDel)
        self.connect(self.toolButton_ipn_enabled,QtCore.SIGNAL("clicked()"),self.subaccountEnableDisable)
        self.connect(self.toolButton_ipn_sleep,QtCore.SIGNAL("clicked()"),self.subAccountIpnSleep)
        
        shortEditAgreement = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_E), self)

        self.connect(self.tabWidget, QtCore.SIGNAL("currentChanged (int)"), self.loadRequestedTab)
        
        self.fixtures()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.tableWidget.objectName(), bhdr)
            HeaderUtil.getHeader(self.tableWidget.objectName(), self.tableWidget)
        else: self.firsttime = False
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(shortEditAgreement, QtCore.SIGNAL("activated()"), self.edit_agreement)
        
        
        self.dhcpActions()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Профиль аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_management_info.setTitle(QtGui.QApplication.translate("MainWindow", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_account_data.setTitle(QtGui.QApplication.translate("MainWindow", "Учётные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_login.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.label_password.setText(QtGui.QApplication.translate("MainWindow", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_password.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_agreement.setTitle(QtGui.QApplication.translate("MainWindow", "Договор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_date.setText(QtGui.QApplication.translate("MainWindow", "Дата подключения", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_num.setText(QtGui.QApplication.translate("MainWindow", "Номер договора", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_urdata.setTitle(QtGui.QApplication.translate("MainWindow", "Юридическое лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("MainWindow", "Расчётный счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "КПП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Корресп. счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("MainWindow", "Банк, код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_urphone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_balance_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("MainWindow", "Текущий баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("MainWindow", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_credit.setText(QtGui.QApplication.translate("MainWindow", "Работать в кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_general), QtGui.QApplication.translate("MainWindow", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_nas.setTitle(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("MainWindow", "Сервер доступа аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank_code.setText(QtGui.QApplication.translate("MainWindow", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.label_max_promise.setText(QtGui.QApplication.translate("MainWindow", "Максимальный обещаный платёж", None, QtGui.QApplication.UnicodeUTF8))
        self.label_block_writeoff_summ.setText(QtGui.QApplication.translate("MainWindow", "Блокировка списаний после баланса", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_manager.setText(QtGui.QApplication.translate("MainWindow", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, False)
        self.groupBox_nas.setTitle(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_accessparameters.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_webcab.setText(QtGui.QApplication.translate("MainWindow", "Разрешить пользоваться веб-кабинетом", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_expresscards.setText(QtGui.QApplication.translate("MainWindow", "Разрешить активировать карты экспресс-оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_minus.setText(QtGui.QApplication.translate("MainWindow", "Разрешить IPN доступ при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_block.setText(QtGui.QApplication.translate("MainWindow", "Разрешить IPN доступ, если клиент неактивен, заблокирован или находится в режиме простоя", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_null.setText(QtGui.QApplication.translate("MainWindow", "Разрешить IPN доступ при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        #self.dateTimeEdit_agreement_date.setDisplayFormat(QtGui.QApplication.translate("Dialog", "dd.MM.yyyy H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_added.setText(QtGui.QApplication.translate("SubAccountDialog", "Не добавлен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_enabled.setText(QtGui.QApplication.translate("SubAccountDialog", "Не активен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_sleep.setText(QtGui.QApplication.translate("SubAccountDialog", "Управлять доступом", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ipn_status.setTitle(QtGui.QApplication.translate("SubAccountDialog", "IPN статусы", None, QtGui.QApplication.UnicodeUTF8))
        columns = [u"Название", u"Значение"]
        makeHeaders(columns, self.tableWidget)
        #self.tableWidget.
        
        #cities = self.connection.sql("SELECT id, name FROM billservice_city ORDER BY name ASC;")
        #streets = self.connection.sql("SELECT id, name FROM billservice_street ORDER BY name ASC;")
        #houses = self.connection.sql("SELECT id, name FROM billservice_house ORDER BY name ASC;")
        #self.connection.commit()
        self.tableInfo=[
            #['ur', u'Юридическое лицо','checkbox'],
            ['contactperson', u'Контактное лицо',''],
            ['contactperson_phone', u'Тел. Контактного лица',''],
            ['fullname', u'ФИО абонента',''],
            ['email',u'e-mail',''],
            ['phone_h',u'Телефон дом.',''],
            ['phone_m',u'Телефон моб.',''],
            ['passport',u'Паспорт №',''],
            ['private_passport_number',u'Личный номер',''],
            ['passport_given',u'Кем выдан',''],
            ['passport_date',u'Когда выдан',''],
            ['city', u'Город','combobox', self.comboBox_city],
            ['postcode',u'Индекс',''],
            ['region',u'Район',''],
            ['street',u'Улица','combobox', self.comboBox_street],
            ['house',u'Дом','combobox', self.comboBox_house],
            ['house_bulk',u'Корпус',''],
            ['entrance',u'Подъезд',''],
            ['entrance_code',u'Код домофона',''],
            ['row',u'Этаж',''],
            ['elevator_direction',u'Направление от лифта',''],
            ['room', u'Квартира',''],
            ]
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.tableInfo))
        i=0
        for item in self.tableInfo:
            self.addrow(self.tableWidget, item[1], i, 0, id=item[0])
            if item[2]:
                self.addrow(self.tableWidget, '', i, 1, widget_type = item[2], widget_item=item[3])
            i+=1
            

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_network_settings), QtGui.QApplication.translate("MainWindow", "Сетевые параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_subaccounts), QtGui.QApplication.translate("MainWindow", "Субаккаунты", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_suspended), QtGui.QApplication.translate("MainWindow", "Не списывать ПУ", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tarifs), QtGui.QApplication.translate("MainWindow", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addonservice), QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_accounthardware), QtGui.QApplication.translate("MainWindow", "Оборудование на руках", None, QtGui.QApplication.UnicodeUTF8))
        
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDel.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_status.setTitle(QtGui.QApplication.translate("MainWindow", "Статус аккаунта", None, QtGui.QApplication.UnicodeUTF8))

        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        
        self.ipnRx = QtCore.QRegExp(r"\b(?:0\.0\.0\.0(/0)?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.0\.0\.0(?:/[1-8])?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){2}0\.0(?:/(?:9|1[0-6]))?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}0(?:/(?:1[7-9]|2[0-4]))?)|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:2[5-9]|3[0-2]))?)\b")
        self.ipnValidator = QtGui.QRegExpValidator(self.ipnRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)
        
        #self.lineEdit_ipn_ip_address.setValidator(self.ipnValidator)
        #self.lineEdit_vpn_ip_address.setValidator(self.ipValidator)
        #self.lineEdit_ipn_ip_mask.setValidator(self.ipValidator)
        #self.lineEdit_ipn_mac_address.setValidator(self.macValidator)
        
        self.tableWidget_accounttarif.clear()

        columns = ["#", u"С",u"По"]
        self.tableWidget_suspended = tableFormat(self.tableWidget_suspended)
        makeHeaders(columns, self.tableWidget_suspended)
 
        columns=[u'#', u'Имя пользователя', u'Пароль', u'VPN IP', u'IPN IP', u'IPN MAC', u'Сервер доступа', u'IPN статус',]
        self.tableWidget_subaccounts = tableFormat(self.tableWidget_subaccounts)
        makeHeaders(columns, self.tableWidget_subaccounts)
                
        columns=[u'#', u'Тарифный план', u'Дата', u'Период закрыт', u"Начало текущего расчётного периода", u"Конец текущего расчётного периода"]
        self.tableWidget_accounttarif = tableFormat(self.tableWidget_accounttarif)
        makeHeaders(columns, self.tableWidget_accounttarif)


        columns=[u'#', u'Название услуги', u'Субаккаунт', u'Дата активации', u'Дата окончания', u'Активирована на сервере доступа', u"Временная блокировка"]
        self.tableWidget_addonservice = tableFormat(self.tableWidget_addonservice)
        makeHeaders(columns, self.tableWidget_addonservice)
        
        columns=[u'#', u'Тип оборудования', u'Производитель', u'Модель', u'Серийный номер', u'Выдано', u"Возвращено"]
        self.tableWidget_accounthardware = tableFormat(self.tableWidget_accounthardware)
        makeHeaders(columns, self.tableWidget_accounthardware)
        
        self.tableWidget_accounthardware
        
        self.comboBox_status.addItem(u"Активен")
        self.comboBox_status.setItemData(0, QtCore.QVariant(1))
        self.comboBox_status.addItem(u"Неактивен, не списывать периодические услуги")
        self.comboBox_status.setItemData(1, QtCore.QVariant(2))
        self.comboBox_status.addItem(u"Неактивен, списывать периодические услуги")
        self.comboBox_status.setItemData(2, QtCore.QVariant(3))
        self.comboBox_status.addItem(u"Пользовательская блокировка.")
        self.comboBox_status.setItemData(3, QtCore.QVariant(4))
        
    def loadRequestedTab(self, i):
        if i==1 and i not in self.tab_loaded:
            self.subAccountLinkRefresh()
        elif i==3 and i not in self.tab_loaded:
            self.suspendedPeriodRefresh()
        elif i==4 and i not in self.tab_loaded:
            self.accountTarifRefresh()
        elif i==5 and i not in self.tab_loaded:
            self.accountAddonServiceRefresh()
        elif i==6 and i not in self.tab_loaded:
            self.accountHardwareRefresh()
        self.tab_loaded.append(i)

    def refresh_combo_city(self):
        pass
    
    def edit_agreement(self):
        self.comboBox_agreement_num.setDisabled(False)
        
    def refresh_combo_street(self):
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if city_id==0:
            self.comboBox_street.clear()
        if not city_id: return
        streets = self.connection.get_streets(city_id=city_id, fields=['id', 'name'])

        self.connection.commit()
        self.comboBox_street.clear()
        self.comboBox_house.clear()
        i=0
        for street in streets:
            self.comboBox_street.addItem(street.name, QtCore.QVariant(street.id))
            if self.model:
                if self.model.street==street.id:
                    self.comboBox_street.setCurrentIndex(i)
            i+=1

    def refresh_combo_house(self):
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if not street_id: return        
        items = self.connection.get_houses(street_id=street_id)

        self.connection.commit()
        self.comboBox_house.clear()
        i=0
        for item in items:
            self.comboBox_house.addItem(item.name, QtCore.QVariant(item.id))
            if self.model:
                if self.model.house==item.id:
                    self.comboBox_house.setCurrentIndex(i)
            i+=1
    def saveHeader(self, *args):

        HeaderUtil.saveHeader(self.tableWidget.objectName(), self.tableWidget)

    def subAccountIpnSleep(self):
        if self.toolButton_ipn_sleep.isChecked()==True:
            self.toolButton_ipn_sleep.setText(unicode(u"Не управлять доступом"))
            
        else:
            self.toolButton_ipn_sleep.setText(unicode(u"Управлять доступом"))
            
    def subaccountEnableDisable(self):
        if not self.model: return
        state = True if self.toolButton_ipn_enabled.isChecked() else False
        if state:
            if not self.connection.accountActions(self.model.id, None, 'enable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
                self.toolButton_ipn_enabled.setChecked(QtCore.Qt.Unchecked)
                self.toolButton_ipn_enabled.setText(unicode(u"Не активен"))
            else:
                self.toolButton_ipn_enabled.setText(unicode(u"Активен"))
        else:
             if not self.connection.accountActions(self.model.id, None, 'disable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
                self.toolButton_ipn_enabled.setChecked(QtCore.Qt.Checked)
                self.toolButton_ipn_enabled.setText(unicode(u"Активен"))
                #self.toolButton_ipn_enabled.set
             else:
                self.toolButton_ipn_enabled.setText(unicode(u"Не активен"))    
                
    def subaccountAddDel(self):
        if not self.model: return
        state = True if self.toolButton_ipn_added.isChecked() else False
        if state==True:
            if not self.connection.accountActions(self.model.id, None,  'create'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
                self.toolButton_ipn_added.setChecked(QtCore.Qt.Unchecked)
                self.toolButton_ipn_added.setText(unicode(u"Не добавлен"))
            else:
                self.toolButton_ipn_added.setText(unicode(u"Добавлен"))
        else:
            if not self.connection.accountActions(self.model.id, None,  'delete'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
                self.toolButton_ipn_added.setChecked(QtCore.Qt.Checked)
                self.toolButton_ipn_added.setText(unicode(u"Добавлен"))             
            else:
                self.toolButton_ipn_added.setText(unicode(u"Не добавлен"))

    def checkActions(self):
        
        if self.model.ipn_added:
            self.toolButton_ipn_added.setChecked(self.model.ipn_added)
            self.toolButton_ipn_added.setText(unicode(u"Добавлен"))
        
        if self.model.ipn_status:
            self.toolButton_ipn_enabled.setChecked(self.model.ipn_status)
            self.toolButton_ipn_enabled.setText(unicode(u"Активен"))    
            
    def printAgreement(self):
       

        #model_id=self.model
        
        operator = self.connection.get_operator()
        child = TemplateSelect(connection = self.connection)
        if child.exec_():
            template_id = child.id
        else:
            return
        template = self.connection.get_templates(id=template_id)
        templ = Template(template.body, input_encoding='utf-8')
        
        account = self.model
        try:
            data=templ.render_unicode(account=account, operator=operator, connection=self.connection)
        except Exception, e:
            data=unicode(u""" <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body style="text-align:center;">%s</body></html>""" % repr(e))
        self.connection.commit()            
        file= open('templates/tmp/temp.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        a=CardPreviewDialog(url="templates/tmp/temp.html")
        a.exec_()
       


    def generate_login(self):
        self.lineEdit_username.setText(nameGen())

    def generate_password(self):
        self.lineEdit_password.setText(GenPasswd2())
        
    def dhcpActions(self, newstate=0):
        pass
    
    def fixtures(self):


        pools = []

        nasses = self.connection.get_nasses(fields=['id', 'name'])
        self.connection.commit()
        
        self.comboBox_nas.clear()
        self.comboBox_nas.addItem("---")
        self.comboBox_nas.setItemData(0, QtCore.QVariant(None))
        i=1
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name)
            self.comboBox_nas.setItemData(i, QtCore.QVariant(nas.id))
            if self.model:
                if nas.id==self.model.nas:
                    self.comboBox_nas.setCurrentIndex(i)
            
            i+=1
            

        managers = self.connection.get_systemusers(fields=['id', 'username', 'fullname'])
        self.connection.commit()
        
        self.comboBox_manager.clear()
        self.comboBox_manager.addItem("---")
        self.comboBox_manager.setItemData(0, QtCore.QVariant(None))
        i=1
        for manager in managers:
            self.comboBox_manager.addItem( "%s, %s" % (manager.username,manager.fullname))
            self.comboBox_manager.setItemData(i, QtCore.QVariant(manager.id))
            if self.model:
                if manager.id==self.model.systemuser:
                    self.comboBox_manager.setCurrentIndex(i)
            
            i+=1
                        

        cities = self.connection.get_cities(fields = ['id', 'name'])
        self.connection.commit()
        self.comboBox_city.clear()
        self.comboBox_city.addItem(u'-Не указан-', QtCore.QVariant(None))
        i=1
        for city in cities:
            self.comboBox_city.addItem(city.name, QtCore.QVariant(city.id))
            if self.model:
                if self.model.city==city.id:
                    self.comboBox_city.setCurrentIndex(i)
            i+=1
                  
        if not self.model:
            self.actionAdd.setDisabled(True)
            self.actionDel.setDisabled(True)
            self.toolButton_agreement_print.setDisabled(True)
            #self.toolButton_agreement_print.setDisabled(True)
            self.lineEdit_balance.setText(u"0")
            self.lineEdit_credit.setText(u"0")

            self.dateTimeEdit_agreement_date.setDateTime(datetime.datetime.now())
            
        tarif_contracttemplate=None
        if self.tarif_id>0:
            tarif_contracttemplate = self.connection.get_tariffs(id=self.tarif_id, fields=['contracttemplate',])
        self.connection.commit()
        tarif_contracttemplate_id = None
        if tarif_contracttemplate:
            tarif_contracttemplate_id = tarif_contracttemplate.contracttemplate
         
        templatecontracts = self.connection.get_contracttemplates(fields=['id', 'template'])
        self.connection.commit()
        self.comboBox_agreement_num.clear()
        i=0
        if not self.model:
            self.comboBox_agreement_num.addItem('', QtCore.QVariant(None))
            i+=1
            for item in templatecontracts:
                self.comboBox_agreement_num.addItem(item.template, QtCore.QVariant(item.id))
                if tarif_contracttemplate_id==item.id:
                    self.comboBox_agreement_num.setCurrentIndex(i)
                i+=1
                
        if self.model:
            if self.model.contract:
                self.comboBox_agreement_num.addItem(self.model.contract, QtCore.QVariant(0))
                self.comboBox_agreement_num.setDisabled(True)
                i+=1
            else:
                self.comboBox_agreement_num.addItem(u'', QtCore.QVariant(0))
                i+=1
                for item in templatecontracts:
                    self.comboBox_agreement_num.addItem(item.template, QtCore.QVariant(item.id))
                    #if tarif_contracttemplate_id==item.id:
                    #    self.comboBox_agreement_num.setCurrentIndex(i)
                    i+=1
        


                
            
        if self.model:
            self.checkActions()
            #self.comboBox_agreement_num.setText(unicode(self.model.contract))
            print "self.model", self.model
            self.dateTimeEdit_agreement_date.setDateTime(self.model.created)
            if self.tarif_id!=-3000:            
                self.dateTimeEdit_agreement_date.setDisabled(True)

            self.checkBox_allow_expresscards.setChecked(self.model.allow_expresscards)
            self.checkBox_allow_webcab.setChecked(self.model.allow_webcab)
            
            self.checkBox_allow_ipn_with_null.setChecked(self.model.allow_ipn_with_null)
            self.checkBox_allow_ipn_with_minus.setChecked(self.model.allow_ipn_with_minus)
            self.checkBox_allow_ipn_with_block.setChecked(self.model.allow_ipn_with_block)
            
            self.comboBox_status.setCurrentIndex(self.model.status-1)

            self.lineEdit_username.setText(unicode(self.model.username))
            self.lineEdit_password.setText(unicode(self.model.password))
            
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, unicode(self.model.get(self.tableInfo[i][0],'')), i,1)


            self.plainTextEdit_comment.setPlainText(unicode(self.model.comment))
            

            self.lineEdit_balance.setText(unicode(self.model.ballance))
            self.lineEdit_credit.setText(unicode(self.model.credit or 0))
            
            organization = self.connection.get_organizations(account_id=self.model.id)
            #organization = None
            self.connection.commit()
            if organization:
                
                self.organization = organization
                self.groupBox_urdata.setChecked(True)
                self.lineEdit_organization.setText(unicode(organization.name))
                self.lineEdit_uraddress.setText(unicode(organization.uraddress))
                self.lineEdit_urphone.setText(unicode(organization.phone))
                self.lineEdit_fax.setText(unicode(organization.fax))
                self.lineEdit_okpo.setText(unicode(organization.okpo))
                self.lineEdit_unp.setText(unicode(organization.unp))
                self.lineEdit_kpp.setText(unicode(organization.kpp))
                self.lineEdit_kor_s.setText(unicode(organization.kor_s))
                
                #print "bank_id",org.bank_id
                bank = self.connection.get_banks(id=organization.bank)
                self.connection.commit()
                if bank:
                    self.bank = bank
                    self.lineEdit_bank.setText(unicode(bank.bank))
                    self.lineEdit_bank_code.setText(unicode(bank.bankcode))
                    self.lineEdit_rs.setText(unicode(bank.rs))
            
            else:
                #self.groupBox_urdata.setChecked(False)
                pass

        else:
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, '', i,1)

    def mouseDoubleClickEvent(self, event):
        print 123
        event.accept()
        
    def accept(self):
        """
        понаставить проверок
        """

        contracttemplate_id=self.comboBox_agreement_num.itemData(self.comboBox_agreement_num.currentIndex()).toInt()[0]
        if self.model:
            model=self.model
            if self.tarif_id==-3000:
                model.created = self.dateTimeEdit_agreement_date.currentDate().strftime('%Y-%m-%d %H:%M:%S')
        else:
            #print 'New account'
            if self.connection.check_account_exists(username=unicode(self.lineEdit_username.text())).status:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                self.connection.rollback()
                return

            model=AttrDict()
            model.created = self.dateTimeEdit_agreement_date.currentDate().strftime('%Y-%m-%d %H:%M:%S')
            model.disabled_by_limit = False
            model.vpn_ipinuse_id = None
            model.ipn_ipinuse_id = None

            #model.user_id=1
        model.ipn_status = self.toolButton_ipn_enabled.isChecked()
        model.ipn_added = self.toolButton_ipn_added.isChecked()
        #model.suspended = self.toolButton_ipn_sleep.isChecked()

            
        if unicode(self.comboBox_agreement_num.currentText())=='':
            contracttemplate_id = None
        if not contracttemplate_id:
            model.contract=unicode(self.comboBox_agreement_num.currentText())
            print "model.contract", model.contract
        else:
            model.contract=unicode(self.comboBox_agreement_num.currentText())
            model.contracttemplate_id = contracttemplate_id

                
        model.username = unicode(self.lineEdit_username.text())
        
        if model.username=='':
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не указали имя пользователя."))
            return 
        #print 1
        model.password = unicode(self.lineEdit_password.text())
        #model.contract = unicode(self.comboBox_agreement_num.text())
        model.status = self.comboBox_status.itemData(self.comboBox_status.currentIndex()).toInt()[0]
        for i in xrange(self.tableWidget.rowCount()):
            model[self.tableInfo[i][0]] = unicode(self.tableWidget.item(i,1).text()) 
            #self.tableWidget.item(i,1).setText(unicode(self.model.__dict__.get(self.tableInfo[i][0])))
            

        model.nas = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0] or ''
        model.systemuser = self.comboBox_manager.itemData(self.comboBox_manager.currentIndex()).toInt()[0] or ''

        #model.ballance = unicode(self.lineEdit_balance.text()) or 0
        model.credit = unicode(self.lineEdit_credit.text()) or 0
        model.comment = unicode(self.plainTextEdit_comment.toPlainText())
        
        model.allow_expresscards = self.checkBox_allow_expresscards.checkState()==QtCore.Qt.Checked
        model.allow_webcab = self.checkBox_allow_webcab.checkState()==QtCore.Qt.Checked
        
        model.allow_ipn_with_null = self.checkBox_allow_ipn_with_null.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_minus = self.checkBox_allow_ipn_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_block = self.checkBox_allow_ipn_with_block.checkState()==QtCore.Qt.Checked
        
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if city_id:
            model.city = city_id or ''
            
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if street_id:
            model.street = street_id or ''
            
        house_id = self.comboBox_house.itemData(self.comboBox_house.currentIndex()).toInt()[0]
        if house_id:
            model.house = house_id or ''
            
        #print model.__dict__  

        organization = {}
        bank = {}
        if self.groupBox_urdata.isChecked():
            if unicode(self.lineEdit_organization.text())=="" or unicode(self.lineEdit_bank.text())=="":
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указаны реквизиты юридического лица(название организации, банк)."))
                return

            if self.organization:
                organization = self.organization
            else:
                organization = AttrDict()
                organization.bank = None
                
            organization.name = unicode(self.lineEdit_organization.text())
            organization.uraddress = unicode(self.lineEdit_uraddress.text())
            organization.phone = unicode(self.lineEdit_urphone.text())
            organization.fax = unicode(self.lineEdit_fax.text())
            organization.okpo = unicode(self.lineEdit_okpo.text())
            organization.unp = unicode(self.lineEdit_unp.text())
            organization.kpp = unicode(self.lineEdit_kpp.text())
            organization.kor_s = unicode(self.lineEdit_kor_s.text())
            
            if organization.bank:
                bank = self.bank
            else:
                bank = AttrDict()
                
            bank.bank = unicode(self.lineEdit_bank.text())
            bank.bankcode = unicode(self.lineEdit_bank_code.text())
            bank.rs = unicode(self.lineEdit_rs.text())
            bank.currency = ''

                
        d = self.connection.account_save(model, organization, bank, tarif_id=self.tarif_id,template_id=contracttemplate_id)
        
        if not d: return

        self.model = self.connection.get_account(id=d.id)
        
        self.fixtures()
        print "fixtures"
        #self.model = self.connection.get_model(model.id, "billservice_account")
        self.connection.commit()
        #self.fixtures()
        if self.parent_window:
            self.parent_window.refresh()
        self.actionAdd.setDisabled(False)
        self.actionDel.setDisabled(False)      
        self.toolButton_agreement_print.setDisabled(False)     

        
    def accountTarifRefresh(self):
        if self.model:
            ac = self.connection.get_accounttariffs(self.model.id)

                
            self.tableWidget_accounttarif.setRowCount(len(ac))

            i=0
            #print ac
            for a in ac:
                sp_start, sp_end,length = "","",""
                #if a.settlement_period_id:
                #    sp_start, sp_end,length = self.connection.sp_info(a.settlement_period_id, a.datetime)
                    
                self.addrow(self.tableWidget_accounttarif, a.id, i,0)
                self.addrow(self.tableWidget_accounttarif, a.tarif, i,1)
                self.addrow(self.tableWidget_accounttarif, a.datetime, i,2)
                self.addrow(self.tableWidget_accounttarif, u"Да" if a.periodical_billed else u"Нет", i,3)
                #if sp_start and sp_end:
                #    self.addrow(self.tableWidget_accounttarif, sp_start, i,4)
                #    self.addrow(self.tableWidget_accounttarif, sp_end, i,5)
                i+=1

            self.tableWidget_accounttarif.setColumnHidden(0, True)
            self.tableWidget_accounttarif.resizeColumnsToContents()
            self.connection.commit()
    
    def editAccountInfo(self, item):
        if item.column()==1:
            self.tableWidget.editItem(item)
            
    def suspendedPeriodRefresh(self):
        if self.model:
            sp = self.connection.get_suspendedperiods(account_id=self.model.id)
            
            self.tableWidget_suspended.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_suspended, a.id, i, 0)
                self.addrow(self.tableWidget_suspended, a.start_date, i, 1)
                try:
                    self.addrow(self.tableWidget_suspended, a.end_date, i, 2)
                except:
                    self.addrow(self.tableWidget_suspended, u"Не закончен", i, 2)
                i+=1
            self.tableWidget_suspended.setColumnHidden(0, True)
      
      
    def accountAddonServiceRefresh(self):
        if self.model:
            sp = self.connection.get_accountaddonservices(account_id = self.model.id, normal_fields=True)
            self.connection.commit()
            self.tableWidget_addonservice.clearContents()
            self.tableWidget_addonservice.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_addonservice, a.id, i, 0)
                self.addrow(self.tableWidget_addonservice, a.service, i, 1)
                self.addrow(self.tableWidget_addonservice, a.subaccount, i, 2)
                
                self.addrow(self.tableWidget_addonservice, a.activated, i, 3)
                try:
                    self.addrow(self.tableWidget_addonservice, a.deactivated, i, 4)
                except:
                    self.addrow(self.tableWidget_addonservice, u"Не закончен", i, 4)
                self.addrow(self.tableWidget_addonservice, a.action_status, i, 5)
                try:
                    self.addrow(self.tableWidget_addonservice, a.temporary_blocked, i, 6)
                except:
                    pass
                i+=1
            self.tableWidget_addonservice.setColumnHidden(0, True)
            self.tableWidget_addonservice.resizeColumnsToContents()
            
    def accountHardwareRefresh(self):
        if self.model:
            [u'#', u'Тип оборудования', u'Производитель', u'Модель', u'Серийный номер', u'Выдано', u"Возвращено"]
            sp = self.connection.sql("""
            SELECT ahw.id,ahw.datetime,ahw.returned,ahw.comment, hw.sn, hw.name as hwname , model.name as model, m.name as manufacturer, hwtype.name as hwtype_name
            FROM billservice_accounthardware as ahw 
            JOIN billservice_hardware as hw ON ahw.hardware_id=hw.id
            JOIN billservice_model as model ON model.id=hw.model_id
            JOIN billservice_hardwaretype as hwtype ON hwtype.id=model.hardwaretype_id
            JOIN billservice_manufacturer as m ON m.id=model.manufacturer_id
            WHERE ahw.account_id=%s ORDER BY ahw.returned,ahw.datetime
            """ % self.model.id)
            
            #sp = self.connection.get_accounthardware(account_id=self.model.id)

            self.connection.commit()
            self.tableWidget_accounthardware.clearContents()
            self.tableWidget_accounthardware.setSortingEnabled(False)
            self.tableWidget_accounthardware.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_accounthardware, a.id, i, 0)
                self.addrow(self.tableWidget_accounthardware, a.hwtype, i, 1)
                self.addrow(self.tableWidget_accounthardware, a.manufacturer, i, 2)
                self.addrow(self.tableWidget_accounthardware, a.model, i, 3)
                self.addrow(self.tableWidget_accounthardware, a.sn, i, 4)
                self.addrow(self.tableWidget_accounthardware, a.datetime, i, 5)
                self.addrow(self.tableWidget_accounthardware, a.returned, i, 6)
                
                self.addrow(self.tableWidget_accounthardware, a.comment, i, 7)
              

                i+=1
            self.tableWidget_accounthardware.setColumnHidden(0, True)
            self.tableWidget_accounthardware.setSortingEnabled(True)
            self.tableWidget_accounthardware.resizeColumnsToContents()
            
    def subAccountLinkRefresh(self):
        if self.model:
            sp = self.connection.get_subaccounts(account_id=self.model.id)
            self.connection.commit()
            self.tableWidget_subaccounts.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_subaccounts, a.id, i, 0)
                self.addrow(self.tableWidget_subaccounts, a.username, i, 1)
                self.addrow(self.tableWidget_subaccounts, a.password, i, 2)
                self.addrow(self.tableWidget_subaccounts, a.vpn_ip_address, i, 3)
                self.addrow(self.tableWidget_subaccounts, a.ipn_ip_address, i, 4)
                self.addrow(self.tableWidget_subaccounts, a.ipn_mac_address, i, 5)
                self.addrow(self.tableWidget_subaccounts, a.nas, i, 6)
                self.tableWidget_subaccounts.setCellWidget(i,7,tableImageWidget(ipn_sleep=a.ipn_sleep, ipn_status=a.ipn_enabled, ipn_added=a.ipn_added))
                #self.addrow(self.tableWidget_subaccounts, a.start_date.strftime(strftimeFormat), i, 1)
                #try:
                #    self.addrow(self.tableWidget_subaccounts, a.end_date.strftime(strftimeFormat), i, 2)
                #except:
                #    self.addrow(self.tableWidget_subaccounts, u"Не закончен", i, 2)
                i+=1
            self.tableWidget_subaccounts.setColumnHidden(0, False)  
    
    def addrow(self, widget, value, x, y, id=None, editable=False, widget_type = None, widget_item=None):
        headerItem = QtGui.QTableWidgetItem()
        if widget_type == 'checkbox':
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if widget_type == 'combobox':
            #headerItem = QtGui.QComboBox(self)
            widget.setCellWidget(x,y,widget_item)
            return
        if value==None or value=="None":
            value=''
        if y==0:
            headerItem.id=value
            
        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))     
        elif type(value)==datetime.datetime:
            #.strftime(self.strftimeFormat)   

            headerItem.setData(QtCore.Qt.DisplayRole, QtCore.QString(unicode(value.strftime(strftimeFormat))))      
 
        else:            
            headerItem.setData(0, QtCore.QVariant(value))         
            
        if id:
            headerItem.id=id
            
           
        widget.setItem(x,y,headerItem)
        
    
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).text())
        except:
            return -1

    def add_action(self):
        if self.tabWidget.currentIndex()==4:
            self.add_accounttarif()
        elif self.tabWidget.currentIndex()==3:
            self.add_suspendedperiod()
        elif self.tabWidget.currentIndex()==5:
            self.addAddonService()
        elif self.tabWidget.currentIndex()==1:
            self.addSubAccountLink()
        elif self.tabWidget.currentIndex()==6:
            self.addAccountHardware()
                
    def del_action(self):
        if self.tabWidget.currentIndex()==4:
            self.del_accounttarif()
        elif self.tabWidget.currentIndex()==3:
            self.del_suspendedperiod()
        elif self.tabWidget.currentIndex()==1:
            self.delSubAccountLink()
        elif self.tabWidget.currentIndex()==6:
            self.delAccountHardware()
            
    def addSubAccountLink(self):
        child=SubaccountLinkDialog(connection=self.connection, account=self.model)
        if child.exec_()==1:
            self.subAccountLinkRefresh()
            
    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        child = AccountAddonServiceEdit(connection=self.connection, account_model = self.model.id)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def addAccountHardware(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        child = AccountHardwareDialog(connection=self.connection, account_model = self.model.id)
        if child.exec_()==1:
            self.accountHardwareRefresh()
    
    def editAccounthardware(self):
        i=self.getSelectedId(self.tableWidget_accounthardware)
        try:
            model = self.connection.get_model(i, "billservice_accounthardware")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountHardwareDialog(connection=self.connection, model=model, account_model = self.model.id)
        if child.exec_()==1:
            self.accountHardwareRefresh()
            
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        try:
            model = self.connection.get_model(i, "billservice_accountaddonservice")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountAddonServiceEdit(connection=self.connection, model=model, account_model = self.model.id)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editSubAccount(self):
        i=self.getSelectedId(self.tableWidget_subaccounts)
        try:
            model = self.connection.get_subaccounts(id=i, normal_fields=False)
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = SubaccountLinkDialog(connection=self.connection, model=model, account = self.model)
        if child.exec_()==1:
            self.subAccountLinkRefresh()
            
    def del_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)

        self.connection.accounttariff_delete(i)

 
        self.accountTarifRefresh()

    def delSubAccountLink(self):
        i=self.getSelectedId(self.tableWidget_subaccounts)

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            d = self.connection.subaccount_delete(i)
            if not d:return
            self.subAccountLinkRefresh()
            
    def delAccountHardware(self):
        i=self.getSelectedId(self.tableWidget_accounthardware)
        try:
            model = self.connection.get_model(i, "billservice_accounthardware", fields=['id'])
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
     
        
        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы\nЛучшим решением будет установить дату возврата?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_accounthardware")
            self.accountHardwareRefresh()
            
    def add_suspendedperiod(self):
        child=SuspendedPeriodForm()

        if child.exec_()==1:
            model = AttrDict()
            model.account = self.model.id
            model.start_date = child.start_date
            model.end_date = child.end_date
            self.connection.suspendedperiod_save(model)
            self.connection.commit()
            self.suspendedPeriodRefresh()

    def edit_suspendedperiod(self):
        
        i=self.getSelectedId(self.tableWidget_suspended)
        model = self.connection.get_suspendedperiods(id=i)
        self.connection.commit()
        child=SuspendedPeriodForm(model)

        if child.exec_()==1:
            model.start_date = child.start_date
            model.end_date = child.end_date
            self.connection.suspendedperiod_save(model)
            self.connection.commit()
            self.suspendedPeriodRefresh()
            
    def del_suspendedperiod(self):
        i=self.getSelectedId(self.tableWidget_suspended)
        ###

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.delete_suspendedperiod(i)
            self.suspendedPeriodRefresh()
    
    def edit_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)
        try:
            model=self.connection.get_model(i, "billservice_accounttarif")
        except:
            return

        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        child=AddAccountTarif(connection=self.connection, ttype=self.ttype, model=model)
        if child.exec_()==1:
            self.accountTarifRefresh()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() in (QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter) and self.tableWidget.hasFocus():
            i=self.tableWidget.currentRow()
            #print i
            self.tableWidget.setCurrentCell(i+1,1)
            self.tableWidget.editItem(self.tableWidget.currentItem())

