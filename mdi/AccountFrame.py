#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui

import traceback
import psycopg2
from ebsWindow import ebsTable_n_TreeWindow, ebsTableView_n_TreeWindow
from db import Object as Object
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil, SplitterUtil, transip
#from helpers import AccountsFilterThread, AccountsRefreshThread
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
from CustomForms import simpleTableImageWidget, tableImageWidget, IPAddressSelectForm, TemplateSelect, RrdReportMainWindow, ReportMainWindow, ContractTemplateEdit
from CustomForms import CustomWidget, CardPreviewDialog, SuspendedPeriodForm, GroupsDialog, SpeedLimitDialog, InfoDialog, PSCreatedForm, AccountAddonServiceEdit
from MessagesFrame import MessageDialog
from AccountEditFrame import AccountWindow, AddAccountTarif
from mako.template import Template
from AccountFilter import AccountFilterDialog
from datamodels import MyTableModel

strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
qtTimeFormat = "YYYY-MM-DD HH:MM:SS"
import IPy
from db import AttrDict

class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

limit_actions = [CashType(0, u"Заблокировать пользователя"), CashType(1,u"Изменить скорость")]

la_list = [u"Заблокировать пользователя", u"Изменить скорость"]

ps_conditions = [CashType(0, u"При любом балансе"), CashType(1,u"При положительном и нулевом балансе"), CashType(2,u"При отрицательном балансе"), CashType(3,u"При положительнои балансе")]
ps_list = [u"При любом балансе", u"При положительном и нулевом балансе", u"При отрицательном балансе", u"При положительнои балансе"]
round_types = [CashType(0, u"Не округлять"),CashType(1, u"В большую сторону")]
addonservice_activation_types = [CashType(0, u"Аккаунт"),CashType(1, u"Субаккаунт")]
direction_types = [CashType(0, u"Входящий"),CashType(1, u"Исходящий"),CashType(2, u"Вх.+Исх."),CashType(3, u"Большее направление")]

class TarifWindow(QtGui.QMainWindow):
    def __init__(self, connection, model=None, parent=None):
        super(TarifWindow, self).__init__()
        self.connection=connection
        self.connection.commit()
        self.model=model
        self.parent=parent
        self.setObjectName(_fromUtf8("TarifWindow"))
        self.resize(707, 701)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(21, 0))
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_1 = QtGui.QWidget()
        self.tab_1.setObjectName(_fromUtf8("tab_1"))
        self.gridLayout_28 = QtGui.QGridLayout(self.tab_1)
        self.gridLayout_28.setObjectName(_fromUtf8("gridLayout_28"))
        self.tarif_name_label = QtGui.QLabel(self.tab_1)
        self.tarif_name_label.setObjectName(_fromUtf8("tarif_name_label"))
        self.gridLayout_28.addWidget(self.tarif_name_label, 0, 0, 1, 1)
        self.tarif_name_edit = QtGui.QLineEdit(self.tab_1)
        self.tarif_name_edit.setObjectName(_fromUtf8("tarif_name_edit"))
        self.gridLayout_28.addWidget(self.tarif_name_edit, 0, 1, 1, 3)
        self.sp_groupbox = QtGui.QGroupBox(self.tab_1)
        self.sp_groupbox.setCheckable(False)
        self.sp_groupbox.setChecked(False)
        self.sp_groupbox.setObjectName(_fromUtf8("sp_groupbox"))
        self.gridLayout_8 = QtGui.QGridLayout(self.sp_groupbox)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.tarif_cost_edit = QtGui.QLineEdit(self.sp_groupbox)
        self.tarif_cost_edit.setObjectName(_fromUtf8("tarif_cost_edit"))
        self.gridLayout_8.addWidget(self.tarif_cost_edit, 0, 1, 1, 1)
        self.tarif_cost_label = QtGui.QLabel(self.sp_groupbox)
        self.tarif_cost_label.setObjectName(_fromUtf8("tarif_cost_label"))
        self.gridLayout_8.addWidget(self.tarif_cost_label, 0, 0, 1, 1)
        self.reset_tarif_cost_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.reset_tarif_cost_edit.setObjectName(_fromUtf8("reset_tarif_cost_edit"))
        self.gridLayout_8.addWidget(self.reset_tarif_cost_edit, 2, 0, 1, 2)
        self.require_tarif_cost_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.require_tarif_cost_edit.setObjectName(_fromUtf8("require_tarif_cost_edit"))
        self.gridLayout_8.addWidget(self.require_tarif_cost_edit, 1, 0, 1, 2)
        self.gridLayout_28.addWidget(self.sp_groupbox, 1, 0, 1, 5)
        self.sp_name_label = QtGui.QLabel(self.tab_1)
        self.sp_name_label.setObjectName(_fromUtf8("sp_name_label"))
        self.gridLayout_28.addWidget(self.sp_name_label, 2, 0, 1, 1)
        self.sp_name_edit = QtGui.QComboBox(self.tab_1)
        self.sp_name_edit.setObjectName(_fromUtf8("sp_name_edit"))
        self.gridLayout_28.addWidget(self.sp_name_edit, 2, 1, 1, 4)
        self.label_contracttemplate = QtGui.QLabel(self.tab_1)
        self.label_contracttemplate.setObjectName(_fromUtf8("label_contracttemplate"))
        self.gridLayout_28.addWidget(self.label_contracttemplate, 3, 0, 1, 1)
        self.comboBox_contracttemplate = QtGui.QComboBox(self.tab_1)
        self.comboBox_contracttemplate.setObjectName(_fromUtf8("comboBox_contracttemplate"))
        self.gridLayout_28.addWidget(self.comboBox_contracttemplate, 3, 1, 1, 3)
        self.label_sessionscount = QtGui.QLabel(self.tab_1)
        self.label_sessionscount.setObjectName(_fromUtf8("label_sessionscount"))
        self.gridLayout_28.addWidget(self.label_sessionscount, 4, 0, 1, 1)
        self.lineEdit_sessioncount = QtGui.QLineEdit(self.tab_1)
        self.lineEdit_sessioncount.setObjectName(_fromUtf8("lineEdit_sessioncount"))
        self.gridLayout_28.addWidget(self.lineEdit_sessioncount, 4, 1, 1, 4)
        self.access_time_label = QtGui.QLabel(self.tab_1)
        self.access_time_label.setObjectName(_fromUtf8("access_time_label"))
        self.gridLayout_28.addWidget(self.access_time_label, 5, 0, 1, 1)
        self.access_time_edit = QtGui.QComboBox(self.tab_1)
        self.access_time_edit.setObjectName(_fromUtf8("access_time_edit"))
        self.gridLayout_28.addWidget(self.access_time_edit, 5, 1, 1, 4)
        self.access_type_label = QtGui.QLabel(self.tab_1)
        self.access_type_label.setObjectName(_fromUtf8("access_type_label"))
        self.gridLayout_28.addWidget(self.access_type_label, 6, 0, 1, 1)
        self.access_type_edit = QtGui.QComboBox(self.tab_1)
        self.access_type_edit.setObjectName(_fromUtf8("access_type_edit"))
        self.gridLayout_28.addWidget(self.access_type_edit, 6, 1, 1, 4)
        self.label_vpn_ippool = QtGui.QLabel(self.tab_1)
        self.label_vpn_ippool.setObjectName(_fromUtf8("label_vpn_ippool"))
        self.gridLayout_28.addWidget(self.label_vpn_ippool, 7, 0, 1, 1)
        self.comboBox_vpn_ippool = QtGui.QComboBox(self.tab_1)
        self.comboBox_vpn_ippool.setObjectName(_fromUtf8("comboBox_vpn_ippool"))
        self.gridLayout_28.addWidget(self.comboBox_vpn_ippool, 7, 1, 1, 4)
        self.groupBox_allowuserblock = QtGui.QGroupBox(self.tab_1)
        self.groupBox_allowuserblock.setCheckable(True)
        self.groupBox_allowuserblock.setObjectName(_fromUtf8("groupBox_allowuserblock"))
        self.gridLayout_10 = QtGui.QGridLayout(self.groupBox_allowuserblock)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.label_userblock_cost = QtGui.QLabel(self.groupBox_allowuserblock)
        self.label_userblock_cost.setObjectName(_fromUtf8("label_userblock_cost"))
        self.gridLayout_10.addWidget(self.label_userblock_cost, 0, 0, 1, 1)
        self.lineEdit_userblock_cost = QtGui.QLineEdit(self.groupBox_allowuserblock)
        self.lineEdit_userblock_cost.setObjectName(_fromUtf8("lineEdit_userblock_cost"))
        self.gridLayout_10.addWidget(self.lineEdit_userblock_cost, 0, 1, 1, 1)
        self.label_max_block_days = QtGui.QLabel(self.groupBox_allowuserblock)
        self.label_max_block_days.setObjectName(_fromUtf8("label_max_block_days"))
        self.gridLayout_10.addWidget(self.label_max_block_days, 2, 0, 1, 1)
        self.spinBox_max_block_days = QtGui.QSpinBox(self.groupBox_allowuserblock)
        self.spinBox_max_block_days.setObjectName(_fromUtf8("spinBox_max_block_days"))
        self.gridLayout_10.addWidget(self.spinBox_max_block_days, 2, 1, 1, 1)
        self.label_userblock_minballance = QtGui.QLabel(self.groupBox_allowuserblock)
        self.label_userblock_minballance.setObjectName(_fromUtf8("label_userblock_minballance"))
        self.gridLayout_10.addWidget(self.label_userblock_minballance, 1, 0, 1, 1)
        self.lineEdit_userblock_minballance = QtGui.QLineEdit(self.groupBox_allowuserblock)
        self.lineEdit_userblock_minballance.setObjectName(_fromUtf8("lineEdit_userblock_minballance"))
        self.gridLayout_10.addWidget(self.lineEdit_userblock_minballance, 1, 1, 1, 1)
        self.gridLayout_28.addWidget(self.groupBox_allowuserblock, 11, 0, 1, 6)
        self.tarif_description_label = QtGui.QLabel(self.tab_1)
        self.tarif_description_label.setObjectName(_fromUtf8("tarif_description_label"))
        self.gridLayout_28.addWidget(self.tarif_description_label, 12, 0, 1, 1)
        self.tarif_description_edit = QtGui.QTextEdit(self.tab_1)
        self.tarif_description_edit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.tarif_description_edit.setObjectName(_fromUtf8("tarif_description_edit"))
        self.gridLayout_28.addWidget(self.tarif_description_edit, 14, 0, 1, 6)
        self.tarif_status_edit = QtGui.QCheckBox(self.tab_1)
        self.tarif_status_edit.setObjectName(_fromUtf8("tarif_status_edit"))
        self.gridLayout_28.addWidget(self.tarif_status_edit, 15, 0, 1, 1)
        self.components_groupBox = QtGui.QGroupBox(self.tab_1)
        self.components_groupBox.setObjectName(_fromUtf8("components_groupBox"))
        self.gridLayout_9 = QtGui.QGridLayout(self.components_groupBox)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.transmit_service_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.transmit_service_checkbox.setObjectName(_fromUtf8("transmit_service_checkbox"))
        self.gridLayout_9.addWidget(self.transmit_service_checkbox, 0, 0, 1, 1)
        self.time_access_service_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.time_access_service_checkbox.setObjectName(_fromUtf8("time_access_service_checkbox"))
        self.gridLayout_9.addWidget(self.time_access_service_checkbox, 1, 0, 1, 1)
        self.radius_traffic_access_service_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.radius_traffic_access_service_checkbox.setObjectName(_fromUtf8("radius_traffic_access_service_checkbox"))
        self.gridLayout_9.addWidget(self.radius_traffic_access_service_checkbox, 2, 0, 1, 1)
        self.onetime_services_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.onetime_services_checkbox.setObjectName(_fromUtf8("onetime_services_checkbox"))
        self.gridLayout_9.addWidget(self.onetime_services_checkbox, 3, 0, 1, 1)
        self.periodical_services_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.periodical_services_checkbox.setObjectName(_fromUtf8("periodical_services_checkbox"))
        self.gridLayout_9.addWidget(self.periodical_services_checkbox, 4, 0, 1, 1)
        self.limites_checkbox = QtGui.QCheckBox(self.components_groupBox)
        self.limites_checkbox.setObjectName(_fromUtf8("limites_checkbox"))
        self.gridLayout_9.addWidget(self.limites_checkbox, 5, 0, 1, 1)
        self.checkBox_addon_services = QtGui.QCheckBox(self.components_groupBox)
        self.checkBox_addon_services.setObjectName(_fromUtf8("checkBox_addon_services"))
        self.gridLayout_9.addWidget(self.checkBox_addon_services, 6, 0, 1, 1)
        self.checkBox_ip_telephony = QtGui.QCheckBox(self.components_groupBox)
        self.checkBox_ip_telephony.setObjectName(_fromUtf8("checkBox_ip_telephony"))
        self.gridLayout_9.addWidget(self.checkBox_ip_telephony, 7, 0, 1, 1)
        self.gridLayout_28.addWidget(self.components_groupBox, 0, 5, 5, 1)
        self.checkBox_ipn_actions = QtGui.QCheckBox(self.tab_1)
        self.checkBox_ipn_actions.setObjectName(_fromUtf8("checkBox_ipn_actions"))
        self.gridLayout_28.addWidget(self.checkBox_ipn_actions, 6, 5, 1, 1)
        self.toolButton = QtGui.QToolButton(self.tab_1)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.gridLayout_28.addWidget(self.toolButton, 3, 4, 1, 1)
        self.checkBox_allow_expresscards_activation = QtGui.QCheckBox(self.tab_1)
        self.checkBox_allow_expresscards_activation.setObjectName(_fromUtf8("checkBox_allow_expresscards_activation"))
        self.gridLayout_28.addWidget(self.checkBox_allow_expresscards_activation, 9, 1, 1, 5)
        self.checkBox_allow_moneytransfer = QtGui.QCheckBox(self.tab_1)
        self.checkBox_allow_moneytransfer.setObjectName(_fromUtf8("checkBox_allow_moneytransfer"))
        self.gridLayout_28.addWidget(self.checkBox_allow_moneytransfer, 10, 1, 1, 5)
        self.comboBox_vpn_guest_ippool = QtGui.QComboBox(self.tab_1)
        self.comboBox_vpn_guest_ippool.setObjectName(_fromUtf8("comboBox_vpn_guest_ippool"))
        self.gridLayout_28.addWidget(self.comboBox_vpn_guest_ippool, 8, 1, 1, 4)
        self.label_vpn_guest_ippool = QtGui.QLabel(self.tab_1)
        self.label_vpn_guest_ippool.setObjectName(_fromUtf8("label_vpn_guest_ippool"))
        self.gridLayout_28.addWidget(self.label_vpn_guest_ippool, 8, 0, 1, 1)
        self.tabWidget.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_12 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.speed_access_groupBox = QtGui.QGroupBox(self.tab_2)
        self.speed_access_groupBox.setObjectName(_fromUtf8("speed_access_groupBox"))
        self.gridLayout_11 = QtGui.QGridLayout(self.speed_access_groupBox)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.speed_in_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_in_label.setObjectName(_fromUtf8("speed_in_label"))
        self.gridLayout_11.addWidget(self.speed_in_label, 0, 1, 1, 1)
        self.speed_out_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_out_label.setObjectName(_fromUtf8("speed_out_label"))
        self.gridLayout_11.addWidget(self.speed_out_label, 0, 2, 1, 1)
        self.speed_max_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_max_label.setObjectName(_fromUtf8("speed_max_label"))
        self.gridLayout_11.addWidget(self.speed_max_label, 1, 0, 1, 1)
        self.speed_max_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_max_in_edit.setFrame(True)
        self.speed_max_in_edit.setObjectName(_fromUtf8("speed_max_in_edit"))
        self.gridLayout_11.addWidget(self.speed_max_in_edit, 1, 1, 1, 1)
        self.speed_max_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_max_out_edit.setObjectName(_fromUtf8("speed_max_out_edit"))
        self.gridLayout_11.addWidget(self.speed_max_out_edit, 1, 2, 1, 1)
        self.speed_min_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_min_label.setObjectName(_fromUtf8("speed_min_label"))
        self.gridLayout_11.addWidget(self.speed_min_label, 2, 0, 1, 1)
        self.speed_min_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_in_edit.setObjectName(_fromUtf8("speed_min_in_edit"))
        self.gridLayout_11.addWidget(self.speed_min_in_edit, 2, 1, 1, 1)
        self.speed_min_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_out_edit.setObjectName(_fromUtf8("speed_min_out_edit"))
        self.gridLayout_11.addWidget(self.speed_min_out_edit, 2, 2, 1, 1)
        self.speed_burst_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_label.setObjectName(_fromUtf8("speed_burst_label"))
        self.gridLayout_11.addWidget(self.speed_burst_label, 3, 0, 1, 1)
        self.speed_burst_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_in_edit.setObjectName(_fromUtf8("speed_burst_in_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_in_edit, 3, 1, 1, 1)
        self.speed_burst_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_out_edit.setObjectName(_fromUtf8("speed_burst_out_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_out_edit, 3, 2, 1, 1)
        self.speed_burst_treshold_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_treshold_label.setObjectName(_fromUtf8("speed_burst_treshold_label"))
        self.gridLayout_11.addWidget(self.speed_burst_treshold_label, 4, 0, 1, 1)
        self.speed_burst_treshold_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_in_edit.setObjectName(_fromUtf8("speed_burst_treshold_in_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_treshold_in_edit, 4, 1, 1, 1)
        self.speed_burst_treshold_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_out_edit.setObjectName(_fromUtf8("speed_burst_treshold_out_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_treshold_out_edit, 4, 2, 1, 1)
        self.speed_burst_time_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_time_label.setObjectName(_fromUtf8("speed_burst_time_label"))
        self.gridLayout_11.addWidget(self.speed_burst_time_label, 5, 0, 1, 1)
        self.speed_burst_time_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_time_in_edit.setObjectName(_fromUtf8("speed_burst_time_in_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_time_in_edit, 5, 1, 1, 1)
        self.speed_burst_time_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_time_out_edit.setObjectName(_fromUtf8("speed_burst_time_out_edit"))
        self.gridLayout_11.addWidget(self.speed_burst_time_out_edit, 5, 2, 1, 1)
        self.speed_priority_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_priority_label.setObjectName(_fromUtf8("speed_priority_label"))
        self.gridLayout_11.addWidget(self.speed_priority_label, 6, 0, 1, 1)
        self.speed_priority_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_priority_edit.setObjectName(_fromUtf8("speed_priority_edit"))
        self.gridLayout_11.addWidget(self.speed_priority_edit, 6, 1, 1, 2)
        self.gridLayout_12.addWidget(self.speed_access_groupBox, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_2)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_25 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_25.setObjectName(_fromUtf8("gridLayout_25"))
        self.speed_panel = QtGui.QFrame(self.groupBox)
        self.speed_panel.setFrameShape(QtGui.QFrame.Box)
        self.speed_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.speed_panel.setObjectName(_fromUtf8("speed_panel"))
        self.gridLayout_13 = QtGui.QGridLayout(self.speed_panel)
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.add_speed_button = QtGui.QToolButton(self.speed_panel)
        self.add_speed_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.add_speed_button.setObjectName(_fromUtf8("add_speed_button"))
        self.gridLayout_13.addWidget(self.add_speed_button, 0, 0, 1, 1)
        self.del_speed_button = QtGui.QToolButton(self.speed_panel)
        self.del_speed_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_speed_button.setObjectName(_fromUtf8("del_speed_button"))
        self.gridLayout_13.addWidget(self.del_speed_button, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_13.addItem(spacerItem, 0, 2, 1, 1)
        self.gridLayout_25.addWidget(self.speed_panel, 0, 0, 1, 1)
        self.speed_table = QtGui.QTableWidget(self.groupBox)
        self.gridLayout_25.addWidget(self.speed_table, 1, 0, 1, 1)
        self.gridLayout_12.addWidget(self.groupBox, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.gridLayout_14 = QtGui.QGridLayout(self.tab_4)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.trafficcost_label = QtGui.QLabel(self.tab_4)
        self.trafficcost_label.setObjectName(_fromUtf8("trafficcost_label"))
        self.gridLayout_14.addWidget(self.trafficcost_label, 0, 0, 1, 1)
        self.traffic_cost_panel = QtGui.QFrame(self.tab_4)
        self.traffic_cost_panel.setFrameShape(QtGui.QFrame.Box)
        self.traffic_cost_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.traffic_cost_panel.setObjectName(_fromUtf8("traffic_cost_panel"))
        self.gridLayout_16 = QtGui.QGridLayout(self.traffic_cost_panel)
        self.gridLayout_16.setObjectName(_fromUtf8("gridLayout_16"))
        self.add_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel)
        self.add_traffic_cost_button.setObjectName(_fromUtf8("add_traffic_cost_button"))
        self.gridLayout_16.addWidget(self.add_traffic_cost_button, 0, 0, 1, 1)
        self.del_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel)
        self.del_traffic_cost_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_traffic_cost_button.setObjectName(_fromUtf8("del_traffic_cost_button"))
        self.gridLayout_16.addWidget(self.del_traffic_cost_button, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_16.addItem(spacerItem1, 0, 2, 1, 1)
        self.gridLayout_14.addWidget(self.traffic_cost_panel, 1, 0, 1, 1)
        self.trafficcost_tableWidget = QtGui.QTableWidget(self.tab_4)
        self.gridLayout_14.addWidget(self.trafficcost_tableWidget, 2, 0, 1, 1)
        self.prepaid_traffic_cost_label = QtGui.QLabel(self.tab_4)
        self.prepaid_traffic_cost_label.setObjectName(_fromUtf8("prepaid_traffic_cost_label"))
        self.gridLayout_14.addWidget(self.prepaid_traffic_cost_label, 3, 0, 1, 1)
        self.prepaid_traffic_panel = QtGui.QFrame(self.tab_4)
        self.prepaid_traffic_panel.setFrameShape(QtGui.QFrame.Box)
        self.prepaid_traffic_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.prepaid_traffic_panel.setObjectName(_fromUtf8("prepaid_traffic_panel"))
        self.gridLayout_15 = QtGui.QGridLayout(self.prepaid_traffic_panel)
        self.gridLayout_15.setObjectName(_fromUtf8("gridLayout_15"))
        self.add_prepaid_traffic_button = QtGui.QToolButton(self.prepaid_traffic_panel)
        self.add_prepaid_traffic_button.setObjectName(_fromUtf8("add_prepaid_traffic_button"))
        self.gridLayout_15.addWidget(self.add_prepaid_traffic_button, 0, 0, 1, 1)
        self.del_prepaid_traffic_button = QtGui.QToolButton(self.prepaid_traffic_panel)
        self.del_prepaid_traffic_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_prepaid_traffic_button.setObjectName(_fromUtf8("del_prepaid_traffic_button"))
        self.gridLayout_15.addWidget(self.del_prepaid_traffic_button, 0, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_15.addItem(spacerItem2, 0, 2, 1, 1)
        self.gridLayout_14.addWidget(self.prepaid_traffic_panel, 4, 0, 1, 1)
        self.prepaid_tableWidget = QtGui.QTableWidget(self.tab_4)
        self.gridLayout_14.addWidget(self.prepaid_tableWidget, 5, 0, 1, 1)
        self.reset_traffic_edit = QtGui.QCheckBox(self.tab_4)
        self.reset_traffic_edit.setObjectName(_fromUtf8("reset_traffic_edit"))
        self.gridLayout_14.addWidget(self.reset_traffic_edit, 6, 0, 1, 1)
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.tab_radius_traffic = QtGui.QWidget()
        self.tab_radius_traffic.setObjectName(_fromUtf8("tab_radius_traffic"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_radius_traffic)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.traffic_cost_panel_2 = QtGui.QFrame(self.tab_radius_traffic)
        self.traffic_cost_panel_2.setFrameShape(QtGui.QFrame.Box)
        self.traffic_cost_panel_2.setFrameShadow(QtGui.QFrame.Raised)
        self.traffic_cost_panel_2.setObjectName(_fromUtf8("traffic_cost_panel_2"))
        self.gridLayout_17 = QtGui.QGridLayout(self.traffic_cost_panel_2)
        self.gridLayout_17.setObjectName(_fromUtf8("gridLayout_17"))
        self.add_radius_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel_2)
        self.add_radius_traffic_cost_button.setObjectName(_fromUtf8("add_radius_traffic_cost_button"))
        self.gridLayout_17.addWidget(self.add_radius_traffic_cost_button, 0, 0, 1, 1)
        self.del_radius_traffic_cost_button = QtGui.QToolButton(self.traffic_cost_panel_2)
        self.del_radius_traffic_cost_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_radius_traffic_cost_button.setObjectName(_fromUtf8("del_radius_traffic_cost_button"))
        self.gridLayout_17.addWidget(self.del_radius_traffic_cost_button, 0, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_17.addItem(spacerItem3, 0, 2, 1, 1)
        self.gridLayout_5.addWidget(self.traffic_cost_panel_2, 0, 0, 1, 1)
        self.tableWidget_radius_traffic_trafficcost = QtGui.QTableWidget(self.tab_radius_traffic)
        self.tableWidget_radius_traffic_trafficcost.setObjectName(_fromUtf8("tableWidget_radius_traffic_trafficcost"))
        self.gridLayout_5.addWidget(self.tableWidget_radius_traffic_trafficcost, 1, 0, 1, 1)
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
        self.gridLayout_5.addWidget(self.groupBox_radius_prepaidtraffic, 2, 0, 1, 1)
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
        self.spinBox_radius_traffic_tarification_step.setMaximum(999999999)
        self.spinBox_radius_traffic_tarification_step.setObjectName(_fromUtf8("spinBox_radius_traffic_tarification_step"))
        self.gridLayout_4.addWidget(self.spinBox_radius_traffic_tarification_step, 2, 1, 1, 2)
        self.gridLayout_5.addWidget(self.groupBox_radius_traffic_tarification_settings, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab_radius_traffic, _fromUtf8(""))
        self.tab_radius_time = QtGui.QWidget()
        self.tab_radius_time.setObjectName(_fromUtf8("tab_radius_time"))
        self.gridLayout = QtGui.QGridLayout(self.tab_radius_time)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.traffic_cost_panel_3 = QtGui.QFrame(self.tab_radius_time)
        self.traffic_cost_panel_3.setFrameShape(QtGui.QFrame.Box)
        self.traffic_cost_panel_3.setFrameShadow(QtGui.QFrame.Raised)
        self.traffic_cost_panel_3.setObjectName(_fromUtf8("traffic_cost_panel_3"))
        self.gridLayout_18 = QtGui.QGridLayout(self.traffic_cost_panel_3)
        self.gridLayout_18.setObjectName(_fromUtf8("gridLayout_18"))
        self.add_time_cost_button = QtGui.QToolButton(self.traffic_cost_panel_3)
        self.add_time_cost_button.setObjectName(_fromUtf8("add_time_cost_button"))
        self.gridLayout_18.addWidget(self.add_time_cost_button, 0, 0, 1, 1)
        self.del_time_cost_button = QtGui.QToolButton(self.traffic_cost_panel_3)
        self.del_time_cost_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_time_cost_button.setObjectName(_fromUtf8("del_time_cost_button"))
        self.gridLayout_18.addWidget(self.del_time_cost_button, 0, 1, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_18.addItem(spacerItem4, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.traffic_cost_panel_3, 0, 0, 1, 1)
        self.timeaccess_table = QtGui.QTableWidget(self.tab_radius_time)
        self.gridLayout.addWidget(self.timeaccess_table, 1, 0, 1, 1)
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
        self.gridLayout.addWidget(self.groupBox_radius_time_prepaid, 2, 0, 1, 1)
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
        self.spinBox_radius_time_tarification_step.setMaximum(999999999)
        self.spinBox_radius_time_tarification_step.setObjectName(_fromUtf8("spinBox_radius_time_tarification_step"))
        self.gridLayout_3.addWidget(self.spinBox_radius_time_tarification_step, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_radius_time_tarification_settings, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab_radius_time, _fromUtf8(""))
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName(_fromUtf8("tab_6"))
        self.gridLayout_19 = QtGui.QGridLayout(self.tab_6)
        self.gridLayout_19.setObjectName(_fromUtf8("gridLayout_19"))
        self.onetime_panel = QtGui.QFrame(self.tab_6)
        self.onetime_panel.setFrameShape(QtGui.QFrame.Box)
        self.onetime_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.onetime_panel.setObjectName(_fromUtf8("onetime_panel"))
        self.gridLayout_20 = QtGui.QGridLayout(self.onetime_panel)
        self.gridLayout_20.setObjectName(_fromUtf8("gridLayout_20"))
        self.add_onetime_button = QtGui.QToolButton(self.onetime_panel)
        self.add_onetime_button.setObjectName(_fromUtf8("add_onetime_button"))
        self.gridLayout_20.addWidget(self.add_onetime_button, 0, 0, 1, 1)
        self.del_onetime_button = QtGui.QToolButton(self.onetime_panel)
        self.del_onetime_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_onetime_button.setObjectName(_fromUtf8("del_onetime_button"))
        self.gridLayout_20.addWidget(self.del_onetime_button, 0, 1, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_20.addItem(spacerItem5, 0, 2, 1, 1)
        self.gridLayout_19.addWidget(self.onetime_panel, 0, 0, 1, 1)
        self.onetime_tableWidget = QtGui.QTableWidget(self.tab_6)
        self.gridLayout_19.addWidget(self.onetime_tableWidget, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_6, _fromUtf8(""))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.gridLayout_22 = QtGui.QGridLayout(self.tab_5)
        self.gridLayout_22.setObjectName(_fromUtf8("gridLayout_22"))
        self.periodical_panel = QtGui.QFrame(self.tab_5)
        self.periodical_panel.setFrameShape(QtGui.QFrame.Box)
        self.periodical_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.periodical_panel.setObjectName(_fromUtf8("periodical_panel"))
        self.gridLayout_21 = QtGui.QGridLayout(self.periodical_panel)
        self.gridLayout_21.setObjectName(_fromUtf8("gridLayout_21"))
        self.del_periodical_button = QtGui.QToolButton(self.periodical_panel)
        self.del_periodical_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_periodical_button.setObjectName(_fromUtf8("del_periodical_button"))
        self.gridLayout_21.addWidget(self.del_periodical_button, 0, 1, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(544, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_21.addItem(spacerItem6, 0, 2, 1, 1)
        self.add_periodical_button = QtGui.QToolButton(self.periodical_panel)
        self.add_periodical_button.setMinimumSize(QtCore.QSize(21, 0))
        self.add_periodical_button.setObjectName(_fromUtf8("add_periodical_button"))
        self.gridLayout_21.addWidget(self.add_periodical_button, 0, 0, 1, 1)
        self.gridLayout_22.addWidget(self.periodical_panel, 0, 0, 1, 1)
        self.periodical_tableWidget = QtGui.QTableWidget(self.tab_5)
        self.gridLayout_22.addWidget(self.periodical_tableWidget, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_5, _fromUtf8(""))
        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName(_fromUtf8("tab_7"))
        self.gridLayout_23 = QtGui.QGridLayout(self.tab_7)
        self.gridLayout_23.setObjectName(_fromUtf8("gridLayout_23"))
        self.limit_panel = QtGui.QFrame(self.tab_7)
        self.limit_panel.setFrameShape(QtGui.QFrame.Box)
        self.limit_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.limit_panel.setObjectName(_fromUtf8("limit_panel"))
        self.gridLayout_24 = QtGui.QGridLayout(self.limit_panel)
        self.gridLayout_24.setObjectName(_fromUtf8("gridLayout_24"))
        self.add_limit_button = QtGui.QToolButton(self.limit_panel)
        self.add_limit_button.setObjectName(_fromUtf8("add_limit_button"))
        self.gridLayout_24.addWidget(self.add_limit_button, 0, 0, 1, 1)
        self.del_limit_button = QtGui.QToolButton(self.limit_panel)
        self.del_limit_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_limit_button.setObjectName(_fromUtf8("del_limit_button"))
        self.gridLayout_24.addWidget(self.del_limit_button, 0, 1, 1, 1)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_24.addItem(spacerItem7, 0, 2, 1, 1)
        self.gridLayout_23.addWidget(self.limit_panel, 0, 0, 1, 1)
        self.limit_tableWidget = QtGui.QTableWidget(self.tab_7)
        self.gridLayout_23.addWidget(self.limit_tableWidget, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_7, _fromUtf8(""))
        self.tab_8 = QtGui.QWidget()
        self.tab_8.setObjectName(_fromUtf8("tab_8"))
        self.gridLayout_27 = QtGui.QGridLayout(self.tab_8)
        self.gridLayout_27.setObjectName(_fromUtf8("gridLayout_27"))
        self.limit_panel_2 = QtGui.QFrame(self.tab_8)
        self.limit_panel_2.setFrameShape(QtGui.QFrame.Box)
        self.limit_panel_2.setFrameShadow(QtGui.QFrame.Raised)
        self.limit_panel_2.setObjectName(_fromUtf8("limit_panel_2"))
        self.gridLayout_26 = QtGui.QGridLayout(self.limit_panel_2)
        self.gridLayout_26.setObjectName(_fromUtf8("gridLayout_26"))
        self.add_addonservice_button = QtGui.QToolButton(self.limit_panel_2)
        self.add_addonservice_button.setObjectName(_fromUtf8("add_addonservice_button"))
        self.gridLayout_26.addWidget(self.add_addonservice_button, 0, 0, 1, 1)
        self.del_addonservice_button = QtGui.QToolButton(self.limit_panel_2)
        self.del_addonservice_button.setMinimumSize(QtCore.QSize(21, 0))
        self.del_addonservice_button.setObjectName(_fromUtf8("del_addonservice_button"))
        self.gridLayout_26.addWidget(self.del_addonservice_button, 0, 1, 1, 1)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_26.addItem(spacerItem8, 0, 2, 1, 1)
        self.gridLayout_27.addWidget(self.limit_panel_2, 0, 0, 1, 1)
        self.tableWidget_addonservices = QtGui.QTableWidget(self.tab_8)
        self.gridLayout_27.addWidget(self.tableWidget_addonservices, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_8, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionRefresh = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/reload.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon)
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.actionSave = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8("images/save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionRefresh)
        self.tarif_description_label.setBuddy(self.tarif_description_edit)
        self.speed_max_label.setBuddy(self.speed_max_in_edit)
        self.speed_min_label.setBuddy(self.speed_min_in_edit)
        self.speed_burst_label.setBuddy(self.speed_burst_in_edit)
        self.speed_burst_treshold_label.setBuddy(self.speed_burst_treshold_in_edit)
        self.speed_burst_time_label.setBuddy(self.speed_burst_time_in_edit)
        
        
        self.tabordering()
        self.format_tables()
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.ipn_for_vpn_state = 0
        QtCore.QObject.connect(self.access_type_edit, QtCore.SIGNAL("currentIndexChanged (const QString&)"), self.onAccessTypeChange)
        
        self.fixtures()
        self.tabWidget.setCurrentIndex(0)
        

        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"), self.accept)     
        self.connect(self.actionRefresh, QtCore.SIGNAL("triggered()"), self.fixtures)
        self.connect(self.toolButton, QtCore.SIGNAL("clicked()"), self.contracttemplate)
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
        
        QtCore.QObject.connect(self.add_time_cost_button, QtCore.SIGNAL("clicked()"), self.addTimeAccessRow)
        QtCore.QObject.connect(self.del_time_cost_button, QtCore.SIGNAL("clicked()"), self.delTimeAccessRow)

        QtCore.QObject.connect(self.add_radius_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.addRadiusTrafficRow)
        QtCore.QObject.connect(self.del_radius_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.delRadiusTrafficRow)

        QtCore.QObject.connect(self.add_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.addPrepaidTrafficRow)
        QtCore.QObject.connect(self.del_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.delPrepaidTrafficRow)        
        
        QtCore.QObject.connect(self.add_speed_button, QtCore.SIGNAL("clicked()"), self.addSpeedRow)
        QtCore.QObject.connect(self.del_speed_button, QtCore.SIGNAL("clicked()"), self.delSpeedRow)   
        
        QtCore.QObject.connect(self.add_periodical_button, QtCore.SIGNAL("clicked()"), self.addPeriodicalRow)
        QtCore.QObject.connect(self.del_periodical_button, QtCore.SIGNAL("clicked()"), self.delPeriodicalRow)   

        QtCore.QObject.connect(self.add_addonservice_button, QtCore.SIGNAL("clicked()"), self.addAddonServiceRow)
        QtCore.QObject.connect(self.del_addonservice_button, QtCore.SIGNAL("clicked()"), self.delAddonServiceRow)   
        
        #QtCore.QObject.connect(self.require_tarif_cost_edit, QtCore.SIGNAL("stateChanged(int)"), self.filterSettlementPeriods)
        
        QtCore.QObject.connect(self.transmit_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.transmitTabActivityActions)
        
        QtCore.QObject.connect(self.time_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.timeaccessTabActivityActions)
        QtCore.QObject.connect(self.radius_traffic_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.radiusTrafficTabActivityActions)
        
        QtCore.QObject.connect(self.onetime_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.onetimeTabActivityActions)
        
        QtCore.QObject.connect(self.periodical_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.periodicalServicesTabActivityActions)
        
        QtCore.QObject.connect(self.limites_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.limitTabActivityActions)
        QtCore.QObject.connect(self.checkBox_addon_services, QtCore.SIGNAL("stateChanged(int)"), self.addonservicesTabActivityActions)
        QtCore.QObject.connect(self.checkBox_ipn_actions, QtCore.SIGNAL("stateChanged(int)"), self.ipn_for_vpnActions)

        QtCore.QObject.connect(self.sp_name_edit, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.spChangedActions)
        
        QtCore.QObject.connect(self.comboBox_radius_time_rounding, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.timeRoundingActions)
        QtCore.QObject.connect(self.comboBox_radius_traffic_rounding, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.trafficRoundingActions)
        #-----------------------
        self.timeRoundingActions()        
        self.trafficRoundingActions()
        self.checkBox_ip_telephony.setDisabled(True)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("TarifWindow", "Редактирование тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Уникальное название тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Уникальное название тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("MainWindow", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Уникальное название тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Уникальное название тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Предоставление тарифного плана как пакета на срок расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Предоставление тарифного плана как пакета на срок расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("MainWindow", "Пакетный тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Стоимость пакета. Поле не используется для тарификации пакета.", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Стоимость пакета. Поле не используется для тарификации пакета.", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Стоимость пакета. Поле не используется для тарификации пакета.", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Стоимость пакета. Поле не используется для тарификации пакета.", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("MainWindow", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "В конце расчётного периода будет произведено доснятие неизрасходованных средств до указанной стоимости пакета.", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("MainWindow", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.require_tarif_cost_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "В случае, если на начало расчётного периода у абонента не будет указанной стоимости пакета - он будет заблокирован", None, QtGui.QApplication.UnicodeUTF8))
        self.require_tarif_cost_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "В случае, если на начало расчётного периода у абонента не будет указанной стоимости пакета - он будет заблокирован", None, QtGui.QApplication.UnicodeUTF8))
        self.require_tarif_cost_edit.setText(QtGui.QApplication.translate("MainWindow", "Требовать наличия всей суммы в начале расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Расчётный период тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Расчётный период тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("MainWindow", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Расчётный период тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Расчётный период тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contracttemplate.setToolTip(QtGui.QApplication.translate("MainWindow", "Шаблон номера договора для создаваемых на данном тарифном плане абонентов.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contracttemplate.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Шаблон номера договора для создаваемых на данном тарифном плане абонентов.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contracttemplate.setText(QtGui.QApplication.translate("MainWindow", "Шаблон номера договора", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_contracttemplate.setToolTip(QtGui.QApplication.translate("MainWindow", "Шаблон номера договора для создаваемых на данном тарифном плане абонентов.", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_contracttemplate.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Шаблон номера договора для создаваемых на данном тарифном плане абонентов.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sessionscount.setToolTip(QtGui.QApplication.translate("MainWindow", "Количество одноверменных RADIUS сессий на субаккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sessionscount.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Количество одноверменных RADIUS сессий на субаккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sessionscount.setText(QtGui.QApplication.translate("MainWindow", "RADIUS сессий на субаккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_sessioncount.setToolTip(QtGui.QApplication.translate("MainWindow", "Количество одноверменных RADIUS сессий на субаккаунт для PPTP/PPPOE/L2TP тарифных планов", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_sessioncount.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Количество одноверменных RADIUS сессий на субаккаунт для PPTP/PPPOE/L2TP тарифных планов", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешённое время доступа/авторизации для абонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешённое время доступа/авторизации для абонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setText(QtGui.QApplication.translate("MainWindow", "Время доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешённое время доступа/авторизации для абонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешённое время доступа/авторизации для абонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Способ доступа абонента", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Способ доступа абонента", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setText(QtGui.QApplication.translate("MainWindow", "Способ доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Способ доступа абонента", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Способ доступа абонента", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ippool.setToolTip(QtGui.QApplication.translate("MainWindow", "IPv4 пул по-умолчанию для динамической выдачи IP адресов клиентам при VPN авторизации.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ippool.setWhatsThis(QtGui.QApplication.translate("MainWindow", "IPv4 пул по-умолчанию для динамической выдачи IP адресов клиентам при VPN авторизации.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ippool.setText(QtGui.QApplication.translate("MainWindow", "VPN пул", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_vpn_ippool.setToolTip(QtGui.QApplication.translate("MainWindow", "IPv4 пул по-умолчанию для динамической выдачи IP адресов клиентам при VPN авторизации.", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_vpn_ippool.setWhatsThis(QtGui.QApplication.translate("MainWindow", "IPv4 пул по-умолчанию для динамической выдачи IP адресов клиентам при VPN авторизации.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_allowuserblock.setTitle(QtGui.QApplication.translate("MainWindow", "Разрешить пользовательскую блокировку", None, QtGui.QApplication.UnicodeUTF8))
        self.label_userblock_cost.setText(QtGui.QApplication.translate("MainWindow", "Стоимость активации блокировки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_max_block_days.setText(QtGui.QApplication.translate("MainWindow", "Максимальная продолжительность блокировки, дней", None, QtGui.QApplication.UnicodeUTF8))
        self.label_userblock_minballance.setText(QtGui.QApplication.translate("MainWindow", "Минимальный баланс для установки блокировки", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setToolTip(QtGui.QApplication.translate("MainWindow", "Текстовое описание тарифного плана для печати накладных и работы с договорами", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Текстовое описание тарифного плана для печати накладных и работы с договорами", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("MainWindow", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Текстовое описание тарифного плана для печати накладных и работы с договорами", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Текстовое описание тарифного плана для печати накладных и работы с договорами", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setToolTip(QtGui.QApplication.translate("MainWindow", "Признак возможности работы абонента на данном тарифном плане", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Признак возможности работы абонента на данном тарифном плане", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("MainWindow", "Тарифный план активен", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Набор компонентов тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Набор компонентов тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Набор компонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию трафика по протоколу NetFlow", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setText(QtGui.QApplication.translate("MainWindow", "NetFlow тарификация", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию времени по RADIUS Accounting", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию времени по RADIUS Accounting", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Radius время", None, QtGui.QApplication.UnicodeUTF8))
        self.radius_traffic_access_service_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию трафика по RADIUS Accounting", None, QtGui.QApplication.UnicodeUTF8))
        self.radius_traffic_access_service_checkbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию трафика по RADIUS Accounting", None, QtGui.QApplication.UnicodeUTF8))
        self.radius_traffic_access_service_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Radius трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить первоначальное списание за услуги при подключении абонента на тарифный план.", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить первоначальное списание за услуги при подключении абонента на тарифный план.", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию периодических услуг(Абонентская плата и другие периодические списания)", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию периодических услуг(Абонентская плата и другие периодические списания)", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить использование квот NetFlow трафика.", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить использование квот NetFlow трафика.", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Лимиты трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить активацию подключаемых услуг абонентом", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить активацию подключаемых услуг абонентом", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setText(QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ip_telephony.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию IP телефонии", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ip_telephony.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить тарификацию IP телефонии", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ip_telephony.setText(QtGui.QApplication.translate("MainWindow", "IP телефония", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ipn_actions.setToolTip(QtGui.QApplication.translate("MainWindow", "Производить дополнительно IPN действия на сервере доступа для данного способа доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ipn_actions.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Производить дополнительно IPN действия на сервере доступа для данного способа доступа.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ipn_actions.setText(QtGui.QApplication.translate("MainWindow", "Производить IPN действия", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_expresscards_activation.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить активацию карт экспресс-оплаты на данном тарифном плане.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_expresscards_activation.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить активацию карт экспресс-оплаты на данном тарифном плане.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_expresscards_activation.setText(QtGui.QApplication.translate("MainWindow", "Разрешить активацию карт экспресс-оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_moneytransfer.setToolTip(QtGui.QApplication.translate("MainWindow", "Разрешить активацию карт экспресс-оплаты на данном тарифном плане.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_moneytransfer.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Разрешить активацию карт экспресс-оплаты на данном тарифном плане.", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_moneytransfer.setText(QtGui.QApplication.translate("MainWindow", "Разрешить услугу \"Поделись балансом\"", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QtGui.QApplication.translate("MainWindow", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_access_groupBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Настройки скорости абонентской линии по-умолчанию для абонентов данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_access_groupBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Настройки скорости абонентской линии по-умолчанию для абонентов данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_access_groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Настройки скорости по-умолчанию", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("MainWindow", "IN", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("MainWindow", "OUT", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_max_label.setText(QtGui.QApplication.translate("MainWindow", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_min_label.setText(QtGui.QApplication.translate("MainWindow", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_label.setText(QtGui.QApplication.translate("MainWindow", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_treshold_label.setText(QtGui.QApplication.translate("MainWindow", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_time_label.setText(QtGui.QApplication.translate("MainWindow", "Burst Time", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_priority_label.setText(QtGui.QApplication.translate("MainWindow", "Приоритет", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Настройки скорости в зависимости от времени(периода тарификации)", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Настройки скорости в зависимости от времени(периода тарификации)", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Настройки скорости по времени", None, QtGui.QApplication.UnicodeUTF8))
        self.add_speed_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_speed_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setSortingEnabled(False)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_label.setText(QtGui.QApplication.translate("MainWindow", "Цена за МБ трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.add_traffic_cost_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_traffic_cost_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_traffic_cost_label.setText(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.add_prepaid_traffic_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_prepaid_traffic_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_traffic_edit.setText(QtGui.QApplication.translate("MainWindow", "Сбрасывать в конце периода предоплаченый трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "NetFlow тарификация", None, QtGui.QApplication.UnicodeUTF8))
        self.add_radius_traffic_cost_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_radius_traffic_cost_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_prepaidtraffic.setTitle(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_prepaid_direction.setText(QtGui.QApplication.translate("MainWindow", "Направление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_prepaid_volume.setText(QtGui.QApplication.translate("MainWindow", "Объём", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_radius_traffic_reset_prepaidtraffic.setText(QtGui.QApplication.translate("MainWindow", "Cбрасывать в конце расчётного периода предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_traffic_tarification_settings.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_direction.setText(QtGui.QApplication.translate("MainWindow", "Направление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_tarification_step.setText(QtGui.QApplication.translate("MainWindow", "Единица тарификации, кб.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_traffic_rounding.setText(QtGui.QApplication.translate("MainWindow", "Способ округления", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_radius_traffic), QtGui.QApplication.translate("MainWindow", "Radius трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.add_time_cost_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_time_cost_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_time_prepaid.setTitle(QtGui.QApplication.translate("MainWindow", "Предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_time_label.setText(QtGui.QApplication.translate("MainWindow", "Предоплачено, с", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_time_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Сбрасывать в конце расчётного периода предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_radius_time_tarification_settings.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры тарификации", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_time_rounding.setText(QtGui.QApplication.translate("MainWindow", "Способ округления", None, QtGui.QApplication.UnicodeUTF8))
        self.label_radius_time_tarification_step.setText(QtGui.QApplication.translate("MainWindow", "Период тарификации, сек.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_radius_time), QtGui.QApplication.translate("MainWindow", "Radius время", None, QtGui.QApplication.UnicodeUTF8))
        self.add_onetime_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_onetime_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QtGui.QApplication.translate("MainWindow", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.del_periodical_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_periodical_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("MainWindow", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.add_limit_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_limit_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QtGui.QApplication.translate("MainWindow", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.add_addonservice_button.setText(QtGui.QApplication.translate("MainWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_addonservice_button.setText(QtGui.QApplication.translate("MainWindow", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefresh.setText(QtGui.QApplication.translate("MainWindow", "Обновить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_vpn_guest_ippool.setToolTip(QtGui.QApplication.translate("MainWindow", "IPv4 пул адреса из которого будут выдаваться абонентам, если их баланс будет <=0 или они будут заблокированы.", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_vpn_guest_ippool.setWhatsThis(QtGui.QApplication.translate("MainWindow", "IPv4 пул адреса из которого будут выдаваться абонентам, если их баланс будет <=0 или они будут заблокированы.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_guest_ippool.setText(QtGui.QApplication.translate("MainWindow", "Гостевой VPN пул", None, QtGui.QApplication.UnicodeUTF8))


    def tabordering(self):
        self.setTabOrder(self.tabWidget, self.tarif_name_edit)
        self.setTabOrder(self.tarif_name_edit, self.sp_groupbox)
        self.setTabOrder(self.sp_groupbox, self.tarif_cost_edit)
        self.setTabOrder(self.tarif_cost_edit, self.require_tarif_cost_edit)
        self.setTabOrder(self.require_tarif_cost_edit, self.reset_tarif_cost_edit)
        self.setTabOrder(self.reset_tarif_cost_edit, self.transmit_service_checkbox)
        self.setTabOrder(self.transmit_service_checkbox, self.time_access_service_checkbox)
        self.setTabOrder(self.time_access_service_checkbox, self.radius_traffic_access_service_checkbox)
        self.setTabOrder(self.radius_traffic_access_service_checkbox, self.onetime_services_checkbox)
        self.setTabOrder(self.onetime_services_checkbox, self.periodical_services_checkbox)
        self.setTabOrder(self.periodical_services_checkbox, self.limites_checkbox)
        self.setTabOrder(self.limites_checkbox, self.checkBox_addon_services)
        self.setTabOrder(self.checkBox_addon_services, self.checkBox_ip_telephony)
        self.setTabOrder(self.checkBox_ip_telephony, self.sp_name_edit)
        self.setTabOrder(self.sp_name_edit, self.comboBox_contracttemplate)
        self.setTabOrder(self.comboBox_contracttemplate, self.toolButton)
        self.setTabOrder(self.toolButton, self.lineEdit_sessioncount)
        self.setTabOrder(self.lineEdit_sessioncount, self.access_time_edit)
        self.setTabOrder(self.access_time_edit, self.access_type_edit)
        self.setTabOrder(self.access_type_edit, self.checkBox_ipn_actions)
        self.setTabOrder(self.checkBox_ipn_actions, self.comboBox_vpn_ippool)
        self.setTabOrder(self.comboBox_vpn_ippool, self.checkBox_allow_expresscards_activation)
        self.setTabOrder(self.checkBox_allow_expresscards_activation, self.checkBox_allow_moneytransfer)
        self.setTabOrder(self.checkBox_allow_moneytransfer, self.groupBox_allowuserblock)
        self.setTabOrder(self.groupBox_allowuserblock, self.lineEdit_userblock_cost)
        self.setTabOrder(self.lineEdit_userblock_cost, self.lineEdit_userblock_minballance)
        self.setTabOrder(self.lineEdit_userblock_minballance, self.spinBox_max_block_days)
        self.setTabOrder(self.spinBox_max_block_days, self.tarif_description_edit)
        self.setTabOrder(self.tarif_description_edit, self.tarif_status_edit)
        self.setTabOrder(self.tarif_status_edit, self.speed_max_in_edit)
        self.setTabOrder(self.speed_max_in_edit, self.speed_max_out_edit)
        self.setTabOrder(self.speed_max_out_edit, self.speed_min_in_edit)
        self.setTabOrder(self.speed_min_in_edit, self.speed_min_out_edit)
        self.setTabOrder(self.speed_min_out_edit, self.speed_burst_in_edit)
        self.setTabOrder(self.speed_burst_in_edit, self.speed_burst_out_edit)
        self.setTabOrder(self.speed_burst_out_edit, self.speed_burst_treshold_in_edit)
        self.setTabOrder(self.speed_burst_treshold_in_edit, self.speed_burst_treshold_out_edit)
        self.setTabOrder(self.speed_burst_treshold_out_edit, self.speed_burst_time_in_edit)
        self.setTabOrder(self.speed_burst_time_in_edit, self.speed_burst_time_out_edit)
        self.setTabOrder(self.speed_burst_time_out_edit, self.speed_priority_edit)
        self.setTabOrder(self.speed_priority_edit, self.add_speed_button)
        self.setTabOrder(self.add_speed_button, self.del_speed_button)
        self.setTabOrder(self.del_speed_button, self.speed_table)
        self.setTabOrder(self.speed_table, self.add_traffic_cost_button)
        self.setTabOrder(self.add_traffic_cost_button, self.del_traffic_cost_button)
        self.setTabOrder(self.del_traffic_cost_button, self.trafficcost_tableWidget)
        self.setTabOrder(self.trafficcost_tableWidget, self.add_prepaid_traffic_button)
        self.setTabOrder(self.add_prepaid_traffic_button, self.del_prepaid_traffic_button)
        self.setTabOrder(self.del_prepaid_traffic_button, self.prepaid_tableWidget)
        self.setTabOrder(self.prepaid_tableWidget, self.reset_traffic_edit)
        self.setTabOrder(self.reset_traffic_edit, self.add_radius_traffic_cost_button)
        self.setTabOrder(self.add_radius_traffic_cost_button, self.del_radius_traffic_cost_button)
        self.setTabOrder(self.del_radius_traffic_cost_button, self.tableWidget_radius_traffic_trafficcost)
        self.setTabOrder(self.tableWidget_radius_traffic_trafficcost, self.comboBox_radius_traffic_prepaid_direction)
        self.setTabOrder(self.comboBox_radius_traffic_prepaid_direction, self.spinBox_radius_traffic_prepaid_volume)
        self.setTabOrder(self.spinBox_radius_traffic_prepaid_volume, self.checkBox_radius_traffic_reset_prepaidtraffic)
        self.setTabOrder(self.checkBox_radius_traffic_reset_prepaidtraffic, self.comboBox_radius_traffic_direction)
        self.setTabOrder(self.comboBox_radius_traffic_direction, self.spinBox_radius_traffic_tarification_step)
        self.setTabOrder(self.spinBox_radius_traffic_tarification_step, self.comboBox_radius_traffic_rounding)
        self.setTabOrder(self.comboBox_radius_traffic_rounding, self.add_time_cost_button)
        self.setTabOrder(self.add_time_cost_button, self.del_time_cost_button)
        self.setTabOrder(self.del_time_cost_button, self.timeaccess_table)
        self.setTabOrder(self.timeaccess_table, self.prepaid_time_edit)
        self.setTabOrder(self.prepaid_time_edit, self.reset_time_checkbox)
        self.setTabOrder(self.reset_time_checkbox, self.comboBox_radius_time_rounding)
        self.setTabOrder(self.comboBox_radius_time_rounding, self.spinBox_radius_time_tarification_step)
        self.setTabOrder(self.spinBox_radius_time_tarification_step, self.add_onetime_button)
        self.setTabOrder(self.add_onetime_button, self.del_onetime_button)
        self.setTabOrder(self.del_onetime_button, self.onetime_tableWidget)
        self.setTabOrder(self.onetime_tableWidget, self.add_periodical_button)
        self.setTabOrder(self.add_periodical_button, self.del_periodical_button)
        self.setTabOrder(self.del_periodical_button, self.periodical_tableWidget)
        self.setTabOrder(self.periodical_tableWidget, self.add_limit_button)
        self.setTabOrder(self.add_limit_button, self.del_limit_button)
        self.setTabOrder(self.del_limit_button, self.limit_tableWidget)
        self.setTabOrder(self.limit_tableWidget, self.add_addonservice_button)
        self.setTabOrder(self.add_addonservice_button, self.del_addonservice_button)
        self.setTabOrder(self.del_addonservice_button, self.tableWidget_addonservices)


    def format_tables(self):
        self.speed_table=tableFormat(self.speed_table)
        self.speed_table.clear()
        columns=[u'#',u'Время', u'MAX', u'MIN', u'Burst', u'Burst Treshold', u'Burst Time', u'Priority']
        
        makeHeaders(columns, self.speed_table) 
        
        self.timeaccess_table=tableFormat(self.timeaccess_table)
        self.timeaccess_table.clear()

        columns=[u'#', u'Время', u'Цена за минуту']
        
        makeHeaders(columns, self.timeaccess_table)     
        self.trafficcost_tableWidget = tableFormat(self.trafficcost_tableWidget)
        self.trafficcost_tableWidget.clear()
        columns=[u'#', u'От МБ', u'До МБ', u'Группа трафика', u'Время', u'Цена за МБ']
        
        makeHeaders(columns, self.trafficcost_tableWidget)
        self.trafficcost_tableWidget.setColumnHidden(1, True)
        self.trafficcost_tableWidget.setColumnHidden(2, True)    
        
        self.prepaid_tableWidget = tableFormat(self.prepaid_tableWidget)
        self.prepaid_tableWidget.clear()
        columns=[u'#', u'Группа',  u'МБ']
        
        makeHeaders(columns, self.prepaid_tableWidget)        
        
        self.onetime_tableWidget = tableFormat(self.onetime_tableWidget)
        self.onetime_tableWidget.clear()

        columns=[u'#', u'Название', u'Стоимость']
        
        makeHeaders(columns, self.onetime_tableWidget)
        self.periodical_tableWidget = tableFormat(self.periodical_tableWidget)
        self.periodical_tableWidget.clear()
        columns=[u'#', u'Название', u'Период', u"Начало списаний", u'Способ снятия', u'Стоимость', u"Условие", u"Отключить услугу с"]
        
        makeHeaders(columns, self.periodical_tableWidget)
        self.limit_tableWidget = tableFormat(self.limit_tableWidget)
        
        self.limit_tableWidget.clear()

        columns=[u'#', u'Название', u'За последний', u'Период', u'Группа', u'МБ',u"Действие", u"Скорость"]
        
        makeHeaders(columns, self.limit_tableWidget)
        columns=[u'#', u'Название', u"Доступно для", u'Количество активаций', u'За период времени']
        
        self.table = tableFormat(self.tableWidget_addonservices)
        
        makeHeaders(columns, self.tableWidget_addonservices)
        self.tableWidget_radius_traffic_trafficcost = tableFormat(self.tableWidget_radius_traffic_trafficcost)
        columns=['#',u'Объём', u'Период тарификации', u'Цена за МБ.(после достижения объёма)']
        makeHeaders(columns, self.tableWidget_radius_traffic_trafficcost)    


    def contracttemplate(self):
        id = self.comboBox_contracttemplate.itemData(self.comboBox_contracttemplate.currentIndex()).toInt()[0]
        model=None
        if id>0:
            model = self.connection.get_model(id, "billservice_contracttemplate")
        child = ContractTemplateEdit(connection=self.connection,model=model)
        
        if child.exec_()==1:
            self.refreshContractTemplate()
        
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
        #if self.model is not None:
        #    if value==2 and self.connection.get("SELECT count(*) as accounts FROM billservice_account WHERE ipn_ip_address='0.0.0.0' and get_tarif(id)=%s" % self.model.id).accounts>0:
        #        self.checkBox_ipn_actions.setChecked(0)
        #        QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Вы не можете выбрать эту опцию, так как не у всех у пользователей \nданного тарифного плана указан IPN IP адрес."))
        pass
        
                 
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
        #if id!=-1:
            #self.connection.iddelete("DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=%d" % id)
            #self.connection.delete("DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=%d" % id)
            #self.connection.iddelete(id, "billservice_traffictransmitnodes")
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
        #if id!=-1:
        #    self.connection.iddelete(id, "billservice_trafficlimit")
        self.limit_tableWidget.removeRow(current_row)

    def addOneTimeRow(self):
        current_row = self.onetime_tableWidget.rowCount()
        self.onetime_tableWidget.insertRow(current_row)
    
    def delOneTimeRow(self):
        current_row = self.onetime_tableWidget.currentRow()     
        id = self.getIdFromtable(self.onetime_tableWidget, current_row)
        
        #if id!=-1:
        #    self.connection.iddelete(id, "billservice_onetimeservice")

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
        
        #if id!=-1:
         #   self.connection.iddelete(id ,"billservice_radiustrafficnode")
            #TimeAccessNode.objects.get(id=id).delete()
    
        self.tableWidget_radius_traffic_trafficcost.removeRow(current_row)

        
    def delTimeAccessRow(self):
        current_row = self.timeaccess_table.currentRow()   
        id = self.getIdFromtable(self.timeaccess_table, current_row)
        
       # if id!=-1:
        #    self.connection.iddelete(id ,"billservice_timeaccessnode")
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
        
        #if id!=-1:
            #d = Object()
            #d.prepaidtraffic_id = id
            #self.connection.delete(d, "billservice_prepaidtraffic_traffic_class")
        #    self.connection.iddelete(id, "billservice_prepaidtraffic")
            #PrepaidTraffic.objects.get(id=id).delete()
     
        self.prepaid_tableWidget.removeRow(current_row)

    def addSpeedRow(self):
        current_row = self.speed_table.rowCount()
        self.speed_table.insertRow(current_row)
    
    def delSpeedRow(self):
        current_row = self.speed_table.currentRow()
        id = self.getIdFromtable(self.speed_table, current_row)
        
        #if id!=-1:
         #   self.connection.iddelete(id, "billservice_timespeed")
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
        
        #if id!=-1:
            #self.connection.iddelete(id, "billservice_periodicalservice")
        #    self.connection.sql("UPDATE billservice_periodicalservice SET deleted=True, deactivated=now() WHERE id=%s" % id, return_response=False)

        self.periodical_tableWidget.removeRow(current_row)

         
    def addAddonServiceRow(self):
        current_row = self.tableWidget_addonservices.rowCount()
        self.tableWidget_addonservices.insertRow(current_row)
        
        
    def delAddonServiceRow(self):
        current_row = self.tableWidget_addonservices.currentRow()
        id = self.getIdFromtable(self.tableWidget_addonservices, current_row)
        
        #if id!=-1:
            #self.connection.iddelete(id, "billservice_addonservicetarif")
  
        self.tableWidget_addonservices.removeRow(current_row)
        
    #-----------------------------
    def onAccessTypeChange(self, *args):
        if args[0] == "IPN":
            if self.checkBox_ipn_actions.isEnabled():
                self.ipn_for_vpn_state = self.checkBox_ipn_actions.checkState()
                self.checkBox_ipn_actions.setChecked(True)
                self.checkBox_ipn_actions.setDisabled(True)
                self.comboBox_vpn_ippool.setCurrentIndex(0)
                self.comboBox_vpn_ippool.setDisabled(True)
        elif args[0] == "HotSpot":
            self.ipn_for_vpn_state = self.checkBox_ipn_actions.checkState()
            self.checkBox_ipn_actions.setChecked(False)
            self.checkBox_ipn_actions.setDisabled(True)
            self.comboBox_vpn_ippool.setDisabled(False)
        elif args[0] == "DHCP":
            self.comboBox_vpn_ippool.setDisabled(False)
        else:
            self.comboBox_vpn_ippool.setDisabled(False)
            if not self.checkBox_ipn_actions.isEnabled():
                self.checkBox_ipn_actions.setEnabled(True)
                self.checkBox_ipn_actions.setCheckState(self.ipn_for_vpn_state)

           
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
                group = self.connection.get_groups(child.selected_group, fields=['id', 'name'])
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
                
            timeperidos = self.connection.get_timeperiods()
            child = ComboBoxDialog(items = timeperidos, selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.speed_table, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)

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
                group = self.connection.get_groups(id=child.selected_group, fields=['id', 'name'])
                self.addrow(self.limit_tableWidget, group.name, y,x, id=child.selected_group)

                    
        if x==3:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_settlementperiods(fields=['id', 'name']), selected_item = default_text )
            self.connection.commit()
            if child.exec_()==1:
                self.addrow(self.limit_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)

        if x==1:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QtGui.QInputDialog.getText(self,u"Введите название", u"Название:", QtGui.QLineEdit.Normal, default_text)        
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
            child = ComboBoxDialog(items=self.connection.get_timeperiods(fields=['id', 'name']), selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.timeaccess_table, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==2:
            item = self.timeaccess_table.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость", default_text,-99999999,99999999,2)        
           
            self.timeaccess_table.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                
                                     
    def radiusTrafficEdit(self,y,x):
        if x==1:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Объём(МБ):", u"Введите объём трафика за расчётный период", default_text,-99999999,99999999,2)        
           
            self.tableWidget_radius_traffic_trafficcost.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
        
        if x==2:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_timeperiods(), selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.tableWidget_radius_traffic_trafficcost, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==3:
            item = self.tableWidget_radius_traffic_trafficcost.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите цену", default_text,-99999999,99999999,2)        
           
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
                group = self.connection.get_groups(id=child.selected_group, fields=['id', 'name'])
                self.addrow(self.trafficcost_tableWidget, group.name, y,x, id=child.selected_group)
                if child.selected_group>0:
                    #self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                    self.trafficcost_tableWidget.resizeRowsToContents()
                    
                
        if x==4:
            self.trafficcost_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=self.connection.get_timeperiods(), selected_item = default_text )
            if child.exec_()==1:
                #self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))
                #print "selected_id", child.selected_id
                

                self.addrow(self.trafficcost_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)
                
        if x==5:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0

            text = QtGui.QInputDialog.getDouble(self, u"Цена за МБ:", u"Введите цену", default_text, -1000000,1000000,3)      

            self.trafficcost_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode("%.3f" % float(text[0]))))

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
                
            child = ComboBoxDialog(items=self.connection.get_settlementperiods(), selected_item = default_text )
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
            child = ComboBoxDialog(items=self.connection.get_addonservices(), selected_item = default_text )

            if child.exec_()==1:
                self.addrow(self.tableWidget_addonservices, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  

        if x==2:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text = item.id
            except:
                default_text=u""
            child = ComboBoxDialog(items=addonservice_activation_types, selected_item = default_text )

            if child.exec_()==1:
                self.addrow(self.tableWidget_addonservices, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  


        if x==3:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getInteger(self, u"Количество активаций:", u"Количество активаций", default_text)        
           
            #self.tableWidget_addonservices.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
            self.addrow(self.tableWidget_addonservices, text[0], y, x, id=unicode(text[0]))
            
        if x==4:
            item = self.tableWidget_addonservices.item(y,x)
            try:
                default_text = item.id
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.get_settlementperiods(), selected_item = default_text )
            
            if child.exec_()==1:
                self.addrow(self.tableWidget_addonservices, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)  
            
    
    def getIdFromtable(self, tablewidget, row=0):
        tmp=tablewidget.item(row, 0)
        if tmp is not None:
            return int(tmp.text())
        return 0
        
    def refreshContractTemplate(self):
        self.comboBox_contracttemplate.clear()
        items = self.connection.get_contracttemplates()

        self.comboBox_contracttemplate.addItem(unicode(u"--Без шаблона/Добавить шаблон--"))
        self.comboBox_contracttemplate.setItemData(0, QtCore.QVariant(None))
        i=1
        for item in items:
            self.comboBox_contracttemplate.addItem(unicode(item.template))
            self.comboBox_contracttemplate.setItemData(i, QtCore.QVariant(item.id))
            if self.model:
                if self.model.contracttemplate==item.id:
                    self.comboBox_contracttemplate.setCurrentIndex(i)            
            i+=1
    
    def refreshVPNPool(self):
        self.comboBox_vpn_ippool.clear()
        items = self.connection.get_ippools(type=0)

        self.comboBox_vpn_ippool.addItem(unicode(u"--Без пула--"))
        self.comboBox_vpn_ippool.setItemData(0, QtCore.QVariant(None))
        self.comboBox_vpn_guest_ippool.addItem(unicode(u"--Без пула--"))
        self.comboBox_vpn_guest_ippool.setItemData(0, QtCore.QVariant(None))
        i=1
        for item in items:
            self.comboBox_vpn_ippool.addItem(unicode(item.name))
            self.comboBox_vpn_ippool.setItemData(i, QtCore.QVariant(item.id))
            self.comboBox_vpn_guest_ippool.addItem(unicode(item.name),QtCore.QVariant(item.id))
                        
            if self.model:
                if self.model.vpn_ippool==item.id:
                    self.comboBox_vpn_ippool.setCurrentIndex(i)    
                if self.model.vpn_guest_ippool==item.id:
                    self.comboBox_vpn_guest_ippool.setCurrentIndex(i)    
            i+=1   
            
    def fixtures(self):
        
        if self.model:
            if not self.model.settlement_period:
                #print "self.model.settlement_period_id", self.model.settlement_period_id
                settlement_period=self.connection.get_settlementperiods(self.model.settlement_period)

        settlement_periods = self.connection.get_settlementperiods()
        i=0
        self.sp_name_edit.clear()
        for item in settlement_periods:
            self.sp_name_edit.addItem(item.name, QtCore.QVariant(item.id))
            if not self.model:continue
            if self.model.settlement_period_id==item.id:
                    self.sp_name_edit.setCurrentIndex(i)

            i+=1
            
        self.tarif_cost_edit.setText(unicode('0'))



        access_types = ["PPTP", "PPPOE", "IPN", "HotSpot", 'HotSpotIp+Mac', 'HotSpotIp+Password','HotSpotMac','HotSpotMac+Password','lISG', "DHCP"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = self.connection.get_timeperiods()
        
        access_parameters = None
        if self.model:
            access_parameters = self.connection.get_accessparameters(self.model.access_parameters)
        i=0
        self.access_time_edit.clear()
        for item in access_time:
            self.access_time_edit.addItem(item.name, QtCore.QVariant(item.id))
            if access_parameters:
                if access_parameters.access_time==item.id:
                        self.access_time_edit.setCurrentIndex(i)

            i+=1
            


        self.refreshContractTemplate()
        self.refreshVPNPool()    
        systemgroups = [] #self.connection.get_models("billservice_systemgroup")
        

        self.lineEdit_sessioncount.setText(unicode(access_parameters.sessionscount))
        
        
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
        self.lineEdit_userblock_cost.setText(unicode(0))        
        self.lineEdit_userblock_minballance.setText(unicode(0))    
        if self.model:

            try:
                if self.model.systemgroup:
                    self.comboBox_system_group.setCurrentIndex(self.comboBox_system_group.findData(QtCore.QVariant(self.model.systemgroup)))
            except Exception, e:
                print e

            self.groupBox_allowuserblock.setChecked(self.model.allow_userblock or False)
            self.lineEdit_userblock_minballance.setText(unicode(self.model.userblock_require_balance or 0) )
            self.lineEdit_userblock_cost.setText(unicode(self.model.userblock_cost or 0))
            self.spinBox_max_block_days.setValue(self.model.userblock_max_days or 0)
            self.checkBox_allow_moneytransfer.setChecked(self.model.allow_ballance_transfer or False)
            self.require_tarif_cost_edit.setCheckState(self.model.require_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.tarif_status_edit.setCheckState(self.model.active == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.checkBox_allow_expresscards_activation.setChecked(bool(self.model.allow_express_pay))
            self.tarif_name_edit.setText(self.model.name)
            self.tarif_cost_edit.setText(unicode(self.model.cost))
            self.tarif_description_edit.setText(self.model.description)
            self.reset_tarif_cost_edit.setCheckState(self.model.reset_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.ps_null_ballance_checkout_edit.setCheckState(self.model.ps_null_ballance_checkout == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            
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

            #self.speed_table.clear()
            speeds = self.connection.get_timespeeds(access_parameters = access_parameters.id)
            #speeds = self.model.access_parameters.access_speed.all()
            self.speed_table.setRowCount(len(speeds))
            i=0
            for speed in speeds:
                self.addrow(self.speed_table, speed.id,i, 0, id=speed.id)
                self.addrow(self.speed_table, speed.time,i, 1, id=speed.time_id)
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
            if self.model.time_access_service:
                self.time_access_service_checkbox.setChecked(True)
                time_access_service = self.connection.get_timeaccessservices(id=self.model.time_access_service)
                self.prepaid_time_edit.setValue(time_access_service.prepaid_time)
                self.spinBox_radius_time_tarification_step.setValue(time_access_service.tarification_step)
                self.comboBox_radius_time_rounding.setCurrentIndex(self.comboBox_radius_time_rounding.findData(QtCore.QVariant(time_access_service.rounding)))
                self.reset_time_checkbox.setCheckState(time_access_service.reset_time == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                #nodes = self.model.time_access_service.time_access_nodes.all()
                nodes = self.connection.get_timeaccessservices_nodes( service_id=self.model.time_access_service_id)
                
                self.timeaccess_table.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.timeaccess_table, node.id,i, 0, id=node.id)
                    self.addrow(self.timeaccess_table, node.time_period,i, 1, 'combobox', node.time_period_id)
                    self.addrow(self.timeaccess_table, node.cost,i, 2)
                    i+=1                
            self.timeaccess_table.setColumnHidden(0, True)

            if self.model.radius_traffic_transmit_service:
                self.radius_traffic_access_service_checkbox.setChecked(True)
                radius_traffic_transmit_service = self.connection.get_radiustrafficservices(id = self.model.radius_traffic_transmit_service)
                self.spinBox_radius_traffic_prepaid_volume.setValue(int(float(radius_traffic_transmit_service.prepaid_value)/(1024*1024)))
                self.comboBox_radius_traffic_prepaid_direction.setCurrentIndex(self.comboBox_radius_traffic_prepaid_direction.findData(QtCore.QVariant(radius_traffic_transmit_service.prepaid_direction)))
                self.spinBox_radius_traffic_tarification_step.setValue(radius_traffic_transmit_service.tarification_step)
                self.comboBox_radius_traffic_direction.setCurrentIndex(self.comboBox_radius_traffic_direction.findData(QtCore.QVariant(radius_traffic_transmit_service.direction)))
                self.comboBox_radius_traffic_rounding.setCurrentIndex(self.comboBox_radius_traffic_rounding.findData(QtCore.QVariant(radius_traffic_transmit_service.rounding)))
                
                #self.checkBox_radius_traffic_reset_prepaidtraffic.setValue(rad.prepaid_time)
                self.checkBox_radius_traffic_reset_prepaidtraffic.setCheckState(radius_traffic_transmit_service.reset_prepaid_traffic == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                #nodes = self.model.time_access_service.time_access_nodes.all()
                
                nodes = self.connection.get_radiustrafficservices_nodes(service_id=self.model.radius_traffic_transmit_service_id)

                self.tableWidget_radius_traffic_trafficcost.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.id,i, 0, id=node.id)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.value,i, 1)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, node.timeperiod,i, 2, 'combobox', node.timeperiod_id)
                    self.addrow(self.tableWidget_radius_traffic_trafficcost, "%.3f" % float(node.cost),i, 3)
                    i+=1                
                self.tableWidget_radius_traffic_trafficcost.setColumnHidden(0, True)
                        
            #PeriodicalService
            periodical_services = self.connection.get_periodicalservices(tarif_id=self.model.id, deleted=False, normal_fields=True)
            

            #print "len(periodical_services)", len(periodical_services)
            if len(periodical_services)>0:
                self.periodical_services_checkbox.setChecked(True)
                nodes = periodical_services
                self.periodical_tableWidget.setRowCount(len(nodes))
                i=0
                
                for node in nodes:
                    self.addrow(self.periodical_tableWidget, node.id,i, 0, id=node.id)
                    self.addrow(self.periodical_tableWidget, node.name,i, 1)
                    self.addrow(self.periodical_tableWidget, node.settlement_period,i, 2, 'combobox', node.settlement_period_id)
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
            onetime_services = self.connection.get_onetimeservices(tarif_id=self.model.id)
            if len(onetime_services)>0:
                self.onetime_services_checkbox.setChecked(True)
                nodes = onetime_services
                self.onetime_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.onetime_tableWidget, node.id,i, 0, id=node.id)
                    self.addrow(self.onetime_tableWidget, node.name,i, 1)
                    self.addrow(self.onetime_tableWidget, node.cost,i, 2)
                    i+=1   
            self.onetime_tableWidget.setColumnHidden(0, True)
            
            #Limites
            traffic_limites = self.connection.get_trafficlimites(tarif_id=self.model.id, normal_fields=True)
             
            
            if len(traffic_limites)>0:

                self.limites_checkbox.setChecked(True)
                nodes = traffic_limites
                self.limit_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    speedmodel = self.connection.get_speedlimites(limit_id=node.id, normal_fields=False)
                    self.connection.commit()
                    self.addrow(self.limit_tableWidget, node.id,i, 0, id=node.id)
                    self.addrow(self.limit_tableWidget, node.name,i, 1)
                    self.addrow(self.limit_tableWidget, node.mode,i, 2, item_type='checkbox')
                    self.addrow(self.limit_tableWidget, node.settlement_period,i, 3, item_type='combobox', id=node.settlement_period_id)
                    self.addrow(self.limit_tableWidget, node.group,i, 4, id=node.group_id)
                    #self.limit_tableWidget.setItem(i,4, CustomWidget(parent=self.limit_tableWidget, models=traffic_classes))
                    self.addrow(self.limit_tableWidget, unicode(node.size/(1048576)),i, 5)
                    self.addrow(self.limit_tableWidget, la_list[node.action],i, 6, id = node.action)
                    if len(speedmodel)>0:

                        self.addrow(self.limit_tableWidget, u"%s/%s %s/%s %s/%s %s/%s %s %s/%s" % (speedmodel[0].max_tx, speedmodel[0].max_rx, speedmodel[0].burst_tx, speedmodel[0].burst_rx, speedmodel[0].burst_treshold_tx, speedmodel[0].burst_treshold_rx, speedmodel[0].burst_time_tx, speedmodel[0].burst_time_rx, speedmodel[0].priority, speedmodel[0].min_tx, speedmodel[0].min_rx),i, 7)
                        self.limit_tableWidget.item(i, 7).model = speedmodel[0]

                    i+=1
                    self.limit_tableWidget.resizeColumnsToContents()
                    self.limit_tableWidget.resizeRowsToContents()
            self.limit_tableWidget.setColumnHidden(0, True)
            
            
            #billservice_addonservicetarif
            #AddonServices
            addon_services = self.connection.get_addonservicetariff(tarif_id= self.model.id)
             
            self.connection.commit()
            if len(addon_services)>0:

                self.checkBox_addon_services.setChecked(True)
                nodes = addon_services
                self.tableWidget_addonservices.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    
                    self.addrow(self.tableWidget_addonservices, node.id,i, 0, id=node.id)
                    self.addrow(self.tableWidget_addonservices, node.service,i, 1, id=node.service_id)
                    self.addrow(self.tableWidget_addonservices, addonservice_activation_types[node.type].name,i, 2, id=node.type)
                    self.addrow(self.tableWidget_addonservices, node.activation_count if node.activation_count!=0  else 'unlimited',i, 3, id = node.activation_count)
                    self.addrow(self.tableWidget_addonservices, node.activation_count_period,i, 4, id= node.activation_count_period_id)
                    
                    i+=1
                    self.tableWidget_addonservices.resizeColumnsToContents()
                    self.tableWidget_addonservices.resizeRowsToContents()
            self.tableWidget_addonservices.setColumnHidden(0, True)
                        
            
            #print "self.model.traffic_transmit_service_id=", self.model.traffic_transmit_service_id 
            #Prepaid Traffic
            if self.model.traffic_transmit_service:
                self.transmit_service_checkbox.setChecked(True)
                prepaid_traffic = self.connection.get_prepaidtraffic(service_id= self.model.traffic_transmit_service)
                #print 'self.model.traffic_transmit_service_id', self.model.traffic_transmit_service_id
                if len(prepaid_traffic)>0:
                    nodes = prepaid_traffic
                    #self.model.traffic_transmit_service.prepaid_traffic.all()
                    #print nodes
                    self.prepaid_tableWidget.setRowCount(len(nodes))
                    i=0
                    for node in nodes:
              
                        self.addrow(self.prepaid_tableWidget, node.id,i, 0, id=node.id)
                        self.addrow(self.prepaid_tableWidget, node.group,i, 1, id=node.group_id)
                        #self.prepaid_tableWidget.setItem(i,1, CustomWidget(parent=self.prepaid_tableWidget, models=traffic_classes))

                        #self.addrow(self.prepaid_tableWidget, node.in_direction, i, 2, item_type='checkbox')
                        #self.addrow(self.prepaid_tableWidget, node.out_direction, i, 3, item_type='checkbox')
                        #self.addrow(self.prepaid_tableWidget, node.transit_direction, i, 4, item_type='checkbox')
                        
                        self.addrow(self.prepaid_tableWidget, float(node.size)/(1048576),i, 2)
                        i+=1       
                    
                    self.prepaid_tableWidget.resizeRowsToContents() 
                         
                self.prepaid_tableWidget.setColumnHidden(0, True)
                
                
                traffic_transmit_nodes = self.connection.get_traffictransmitnodes(service_id = self.model.traffic_transmit_service, normal_fields = True)
                #print "traffic_transmit_nodes=", traffic_transmit_nodes
                #print "traffic_transmit_service_id=", self.model.traffic_transmit_service_id
               
                if len(traffic_transmit_nodes)>0:
                    traffic_transmit_service = self.connection.get_traffictransmitservices(id = self.model.traffic_transmit_service)
                    self.reset_traffic_edit.setCheckState(traffic_transmit_service.reset_traffic == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                    nodes = traffic_transmit_nodes
                    self.trafficcost_tableWidget.setRowCount(len(nodes))
                    i = 0
                    for node in nodes:
                        self.addrow(self.trafficcost_tableWidget, node.id, i, 0, id=node.id)
                        #self.addrow(self.trafficcost_tableWidget, node.edge_value/(1024*1024), i, 1)
                        #self.addrow(self.trafficcost_tableWidget, node.edge_end, i, 2)
                        self.addrow(self.trafficcost_tableWidget, node.group, i, 3, id=node.group_id)
                        self.addrow(self.trafficcost_tableWidget, node.timeperiod, i, 4, id=node.timeperiod_id)
                        #self.trafficcost_tableWidget.setItem(i,4, CustomWidget(parent=self.trafficcost_tableWidget, models=time_nodes))
                        self.addrow(self.trafficcost_tableWidget, "%.3f" % float(node.cost), i, 5)
                        i+=1
                        
                    self.trafficcost_tableWidget.resizeRowsToContents()
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                    self.trafficcost_tableWidget.setColumnHidden(0, True)
            if access_parameters.access_type == 'IPN':
                self.access_type_edit.setDisabled(True)
                self.checkBox_ipn_actions.setDisabled(True)
            elif access_parameters.access_type == 'HotSpot':
                self.access_type_edit.setDisabled(True)
                self.checkBox_ipn_actions.setDisabled(True)
                self.checkBox_ipn_actions.setChecked(False)
            elif access_parameters.access_type == 'lISG':
                self.access_type_edit.setDisabled(True)
                self.checkBox_ipn_actions.setDisabled(False)
            else:
                self.access_type_edit.removeItem(3)
                self.access_type_edit.removeItem(2)
            self.access_type_edit.setCurrentIndex(self.access_type_edit.findText(access_parameters.access_type, QtCore.Qt.MatchCaseSensitive))
            #self.access_time_edit.setCurrentIndex(self.access_time_edit.findText(access_parameters.access_time, QtCore.Qt.MatchCaseSensitive))
            self.checkBox_ipn_actions.setChecked(access_parameters.ipn_for_vpn)
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
            model = self.model #copy.deepcopy(self.model)
            access_parameters = self.connection.get_accessparameters(self.model.access_parameters)
        else:
            model=AttrDict()
            access_parameters = AttrDict()
            previous_ipn_for_vpn_state = False
            
        if unicode(self.tarif_name_edit.text())=="":
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не указали название тарифного плана")
            return

        if unicode(self.access_time_edit.currentText())=="":
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не выбрали разрешённый период доступа")
            return

        if (unicode(self.access_time_edit.currentText()) == 'IPN') and self.checkBox_ipn_actions.checkState()==2:
            QtGui.QMessageBox.warning(self, u"Ошибка", u"'Производить IPN действия' может быть выбрано только для VPN планов")
            return

#===============================================================================
#        if  self.sp_name_edit.currentText() and not (self.prepaid_tableWidget.rowCount()>0 or self.reset_traffic_edit.isChecked()):
#            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного трафика необходимо указать расчётный период")
#            return
# 
#        if  self.sp_name_edit.currentText() and not (self.spinBox_radius_traffic_prepaid_volume.value()!=0 or self.checkBox_radius_traffic_reset_prepaidtraffic.isChecked()==True):
#            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного RADIUS трафика необходимо указать расчётный период")
#            return
# 
#        if  self.sp_name_edit.currentText() and not (self.reset_time_checkbox.isChecked()==True or self.prepaid_time_edit.value()!=0):
#            QtGui.QMessageBox.warning(self, u"Ошибка", u"Для начисления и сброса предоплаченного времени необходимо указать расчётный период")
#            return
#===============================================================================
        
        try:
            
            model.name = unicode(self.tarif_name_edit.text())
            
            model.description = unicode(self.tarif_description_edit.toPlainText())
            
            #model.ps_null_ballance_checkout = self.ps_null_ballance_checkout_edit.checkState()==2
            
            model.active = self.tarif_status_edit.checkState()==2
            model.allow_express_pay = self.checkBox_allow_expresscards_activation.checkState()==2
            model.contracttemplate = self.comboBox_contracttemplate.itemData(self.comboBox_contracttemplate.currentIndex()).toInt()[0] if self.comboBox_contracttemplate.itemData(self.comboBox_contracttemplate.currentIndex()).toInt()[0] else None
            model.vpn_ippool = self.comboBox_vpn_ippool.itemData(self.comboBox_vpn_ippool.currentIndex()).toInt()[0] if self.comboBox_vpn_ippool.itemData(self.comboBox_vpn_ippool.currentIndex()).toInt()[0] else None
            model.vpn_guest_ippool = self.comboBox_vpn_guest_ippool.itemData(self.comboBox_vpn_guest_ippool.currentIndex()).toInt()[0] if self.comboBox_vpn_guest_ippool.itemData(self.comboBox_vpn_guest_ippool.currentIndex()).toInt()[0] else None
            access_parameters.access_type = unicode(self.access_type_edit.currentText())
            access_parameters.access_time = self.access_time_edit.itemData(self.access_time_edit.currentIndex()).toInt()[0] or None
            access_parameters.max_limit = u"%s/%s" % (self.speed_max_in_edit.text() or 0, self.speed_max_out_edit.text() or 0)
            access_parameters.min_limit = u"%s/%s" % (self.speed_min_in_edit.text() or 0, self.speed_min_out_edit.text() or 0)
            access_parameters.burst_limit = u"%s/%s" % (self.speed_burst_in_edit.text() or 0, self.speed_burst_out_edit.text() or 0)
            access_parameters.burst_treshold = u"%s/%s" % (self.speed_burst_treshold_in_edit.text() or 0, self.speed_burst_treshold_out_edit.text() or 0)
            access_parameters.burst_time = u"%s/%s" % (self.speed_burst_time_in_edit.text() or 0, self.speed_burst_time_out_edit.text() or 0)
            access_parameters.priority = unicode(self.speed_priority_edit.text()) or 8
            access_parameters.ipn_for_vpn = self.checkBox_ipn_actions.checkState()==2
            access_parameters.sessionscount = unicode(self.lineEdit_sessioncount.text())
            
            model.allow_userblock = self.groupBox_allowuserblock.isChecked()
            if model.allow_userblock:
                try:
                    model.userblock_require_balance = unicode(self.lineEdit_userblock_minballance.text()) or 0
                except Exception, e:
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"В поле минимальный баланс для блокировки может быть только целым или дробным числом")
    #                print 1
                    self.connection.rollback()
                    return
                try:  
                    model.userblock_cost = float(unicode(self.lineEdit_userblock_cost.text())) or 0
                except Exception, e:
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"В поле 'Стоимость блокировки' может быть только целым или дробным числом")
    #                print 1
                    self.connection.rollback()
                    return

                model.userblock_max_days=self.spinBox_max_block_days.value() or 0

            model.allow_ballance_transfer = self.checkBox_allow_moneytransfer.isChecked()
            
            if check_speed([access_parameters.max_limit, access_parameters.burst_limit, access_parameters.burst_treshold, access_parameters.burst_time, access_parameters.priority, access_parameters.min_limit])==False:
                QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка в настройках скорости")
#                print 1
                self.connection.rollback()
                return              

            #model.access_parameters_id=self.connection.save(access_parameters, "billservice_accessparameters")
            
            #gr_id = self.comboBox_system_group.itemData(self.comboBox_system_group.currentIndex()).toInt()[0]
            
            self.connection.commit()
            #Таблица скоростей
            
            speeds = []
            for i in xrange(0, self.speed_table.rowCount()):
                id = self.getIdFromtable(self.speed_table, i)

                speed = AttrDict()
                if id:
                    speed.id=id
                #speed.access_parameters_id=model.access_parameters_id
    
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
                
                speed.time = self.speed_table.item(i,1).id
                #try:
                if check_speed([speed.max_limit, speed.burst_limit, speed.burst_treshold, speed.burst_time, speed.priority, speed.min_limit])==False:
                    QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка в настройках скорости")
                    #print 1
                    self.connection.rollback()
                    return    
                #except:
                #    print "speed compare error"
                speeds.append(speed)
            
            #Период
            model.settlement_period = self.sp_name_edit.itemData(self.sp_name_edit.currentIndex()).toInt()[0]
            

            model.cost = unicode(self.tarif_cost_edit.text()) or 0
            model.reset_tarif_cost = self.reset_tarif_cost_edit.checkState()==2
            model.require_tarif_cost = self.require_tarif_cost_edit.checkState()==2


            #Доступ по времени
            timeaccessnodes = []
            time_access_service = None
            if self.time_access_service_checkbox.checkState()==2 and (unicode(self.prepaid_time_edit.text()) or self.timeaccess_table.rowCount()>0):
                
                time_access_service=AttrDict()
                if 'time_access_service' in self.model:
                    time_access_service.id = self.model.time_access_service_id

                #print 1
                time_access_service.reset_time = self.reset_time_checkbox.checkState()==2
                time_access_service.prepaid_time = unicode(self.prepaid_time_edit.text())
                time_access_service.rounding = self.comboBox_radius_time_rounding.itemData(self.comboBox_radius_time_rounding.currentIndex()).toInt()[0]
                time_access_service.tarification_step = unicode(self.spinBox_radius_time_tarification_step.value())


                
                #model.time_access_service_id = self.connection.save(time_access_service, 'billservice_timeaccessservice')
                
                for i in xrange(0, self.timeaccess_table.rowCount()):
                    #print "pre save"
                    if self.timeaccess_table.item(i,1)==None or self.timeaccess_table.item(i,2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки оплаты за время")
                        self.connection.rollback()
                        return

                        
                    #print "post save"
                    id = self.getIdFromtable(self.timeaccess_table, i)
                    time_access_node = AttrDict()
                    if id:
                        time_access_node.id = id
                    
                    time_access_node.time_period = self.timeaccess_table.item(i,1).id
                    time_access_node.cost = unicode(self.timeaccess_table.item(i,2).text())
                    timeaccessnodes.append(time_access_node)
            
            elif self.time_access_service_checkbox.checkState()==0 and "time_access_service" in model:
                    model.time_access_service = None

                    
            #RADIUS траффик
            radiustrafficnodes = []
            radius_traffic_service = None
            if self.radius_traffic_access_service_checkbox.checkState()==2:
                radius_traffic_service=AttrDict()
                if model.radius_traffic_transmit_service:
                    radius_traffic_service.id = self.model.radius_traffic_transmit_service_id
               
                #print 1
                radius_traffic_service.reset_prepaid_traffic = self.checkBox_radius_traffic_reset_prepaidtraffic.checkState()==2
                radius_traffic_service.prepaid_value = unicode(self.spinBox_radius_traffic_prepaid_volume.value()*1024*1024)
                radius_traffic_service.direction = self.comboBox_radius_traffic_direction.itemData(self.comboBox_radius_traffic_direction.currentIndex()).toInt()[0]
                radius_traffic_service.prepaid_direction = self.comboBox_radius_traffic_prepaid_direction.itemData(self.comboBox_radius_traffic_prepaid_direction.currentIndex()).toInt()[0]
                radius_traffic_service.rounding = self.comboBox_radius_traffic_rounding.itemData(self.comboBox_radius_traffic_rounding.currentIndex()).toInt()[0]
                radius_traffic_service.tarification_step = unicode(self.spinBox_radius_traffic_tarification_step.value())
                #model.radius_traffic_transmit_service_id = self.connection.save(radius_traffic_service, 'billservice_radiustraffic')
                
                for i in xrange(0, self.tableWidget_radius_traffic_trafficcost.rowCount()):
                    #print "pre save"
                    if self.tableWidget_radius_traffic_trafficcost.item(i,1)==None or self.tableWidget_radius_traffic_trafficcost.item(i,2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки оплаты за radius трафик")
                        self.connection.rollback()
                        return
                    radius_traffic_node = AttrDict()
                    #print "post save"
                    id = self.getIdFromtable(self.tableWidget_radius_traffic_trafficcost, i)
                    if id:
                        radius_traffic_node.id = id

                    radius_traffic_node.value = unicode(self.tableWidget_radius_traffic_trafficcost.item(i,1).text())
                    radius_traffic_node.timeperiod = self.tableWidget_radius_traffic_trafficcost.item(i,2).id
                    radius_traffic_node.cost = unicode(self.tableWidget_radius_traffic_trafficcost.item(i,3).text())
                    radiustrafficnodes.append(radius_traffic_node)
            
            elif self.radius_traffic_access_service_checkbox.checkState()==0 and "radius_traffic_transmit_service" in model:
                    model.radius_traffic_transmit_service=None

            
            #Разовые услуги
            
            onetimeservices = []
            onetime_service = None
            if self.onetime_tableWidget.rowCount()>0 and self.onetime_services_checkbox.checkState()==2:
                #onetimeservices = self.connection.sql("SELECT * FROM billservice_tariff_onetime_services WHERE tariff_id=%d" % model.id)
                for i in xrange(0, self.onetime_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.onetime_tableWidget, i)
                    onetime_service = AttrDict()
                    if id:
                        onetime_service.id = id

                    onetime_service.name=unicode(self.onetime_tableWidget.item(i, 1).text())
                    onetime_service.cost=unicode(self.onetime_tableWidget.item(i, 2).text())
                    onetime_service.created = datetime.datetime.now() .strftime(strftimeFormat)
                    onetimeservices.append(onetime_service)
                    
                           

            #Периодические услуги
            periodicalservices = []
            if self.periodical_tableWidget.rowCount()>0 and self.periodical_services_checkbox.checkState()==2:
                for i in xrange(0, self.periodical_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.periodical_tableWidget, i)
                    
                    if self.periodical_tableWidget.item(i, 1)==None or self.periodical_tableWidget.item(i, 2)==None or self.periodical_tableWidget.item(i, 3)==None or self.periodical_tableWidget.item(i, 4)==None or self.periodical_tableWidget.item(i, 6)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки периодических услуг")
                        self.connection.rollback()
                        return
                    periodical_service = AttrDict()
                    if id:
                        periodical_service.id = id

                    [u'#', u'Название', u'Период', u"Начало списаний", u'Способ снятия', u'Стоимость', u"Условие", u"Отключить услугу с"]

                    periodical_service.name=unicode(self.periodical_tableWidget.item(i, 1).text())
                    periodical_service.settlement_period = unicode(self.periodical_tableWidget.item(i, 2).id)
                    periodical_service.cash_method = unicode(self.periodical_tableWidget.item(i, 4).text())
                    periodical_service.cost=unicode(self.periodical_tableWidget.item(i, 5).text())
                    periodical_service.condition = self.periodical_tableWidget.item(i,6).selected_id
                    periodical_service.created = self.periodical_tableWidget.item(i,3).created
                    periodical_service.deactivated = self.periodical_tableWidget.item(i,7).deactivated
                    
                    periodicalservices.append(periodical_service) 
                      

                

            #Лимиты
            limites = []
            if self.limit_tableWidget.rowCount()>0 and self.limites_checkbox.checkState()==2:
                for i in xrange(0, self.limit_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.limit_tableWidget, i)
                    #print self.limit_tableWidget.item(i, 1), self.limit_tableWidget.item(i, 3), self.limit_tableWidget.item(i, 8), self.limit_tableWidget.cellWidget(i, 4)
                    if self.limit_tableWidget.item(i, 6)==None or (self.limit_tableWidget.item(i, 6).id==1 and self.limit_tableWidget.item(i, 7)==None) or self.limit_tableWidget.item(i, 1)==None or self.limit_tableWidget.item(i, 3)==None or self.limit_tableWidget.item(i, 5)==None or self.limit_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки лимитов")
                        self.connection.rollback()
                        return
                   
                    limit = AttrDict()
                    
                    if id:                        
                        limit.id = id

                    limit.name=unicode(self.limit_tableWidget.item(i, 1).text())
                    limit.settlement_period = self.limit_tableWidget.item(i, 3).id
                    limit.mode = self.limit_tableWidget.cellWidget(i,2).checkState()==2
                    limit.size=unicode(int(float(unicode(self.limit_tableWidget.item(i, 5).text()))*1048576))
                    limit.group = self.limit_tableWidget.item(i, 4).id
                    limit.action = self.limit_tableWidget.item(i, 6).id
                    
                    
                    #limit.in_direction = self.limit_tableWidget.cellWidget(i,5).checkState()==2
                    #limit.out_direction = self.limit_tableWidget.cellWidget(i,6).checkState()==2
                    #limit.transit_direction = self.limit_tableWidget.cellWidget(i,7).checkState()==2
                    speedlimit_model = AttrDict()
                    
                    try:
                        speedlimit_model = self.limit_tableWidget.item(i, 7).model
                        """
                        if limit.action==1: 
                            speedlimit_model.limit_id = limit.id
                            self.connection.save(speedlimit_model, "billservice_speedlimit")
                        elif limit.action==0:
                            self.connection.iddelete(speedlimit_model, "billservice_speedlimit")
                        """
                    except Exception, e:
                        pass
                    limites.append((limit,speedlimit_model))


            #Подключаемые услуги
            addonservices = []
            if self.tableWidget_addonservices.rowCount()>0 and self.checkBox_addon_services.checkState()==2:
                for i in xrange(0, self.tableWidget_addonservices.rowCount()):
                    id = self.getIdFromtable(self.tableWidget_addonservices, i)
                    
                    if self.tableWidget_addonservices.item(i, 1)==None and (self.tableWidget_addonservices.item(i, 4)!=None and self.tableWidget_addonservices.item(i, 2) in [None, ]):
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки подключаемых услуг")
                        self.connection.rollback()
                        return
                    addon_service = AttrDict()
                    if id:
                        addon_service.id = id

                    addon_service.service=unicode(self.tableWidget_addonservices.item(i, 1).id)
                    addon_service.type=unicode(self.tableWidget_addonservices.item(i, 2).id)
                    if self.tableWidget_addonservices.item(i, 3):
                        addon_service.activation_count = unicode(self.tableWidget_addonservices.item(i, 3).id)
                    else:
                        addon_service.activation_count = 0
                    if self.tableWidget_addonservices.item(i, 4):
                        addon_service.activation_count_period_id = unicode(self.tableWidget_addonservices.item(i, 4).id)
                    else:
                        addon_service.activation_count_period_id = None

                    
                    addonservices.append(addon_service) 
                      

                                
            #Доступ по трафику 
            traffictransmitnodes = []
            prepaidtrafficnodes = []
            traffic_transmit_service = None
            if self.transmit_service_checkbox.checkState()==2:
                traffic_transmit_service = AttrDict()
                if 'traffic_transmit_service_id' in model and model.traffic_transmit_service_id:
                    traffic_transmit_service.id =  self.model.traffic_transmit_service_id

                
                #traffic_transmit_service.period_check='SP_START'
                traffic_transmit_service.reset_traffic=self.reset_traffic_edit.checkState()==2
            
     
                for i in xrange(0, self.trafficcost_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.trafficcost_tableWidget, i)
                    
                    if  self.trafficcost_tableWidget.item(i, 3)==None or self.trafficcost_tableWidget.item(i, 4)==None or self.trafficcost_tableWidget.item(i, 5)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для оплаты за трафик")
                        self.connection.rollback()
                        return
                    transmit_node = AttrDict()
                                                   
                    if id:
                        transmit_node.id = id


                    #transmit_node.edge_value =float(self.trafficcost_tableWidget.item(i,1).text() or 0)*(1024*1024)
                    #transmit_node.edge_end = float(self.trafficcost_tableWidget.item(i,2).text() or 0)
                    transmit_node.group = self.trafficcost_tableWidget.item(i,3).id

                    transmit_node.cost = unicode(self.trafficcost_tableWidget.item(i,5).text())
                    
                    
                    #transmit_node.id = self.connection.save(transmit_node, "billservice_traffictransmitnodes")
                    
                    transmit_node.timeperiod = self.trafficcost_tableWidget.item(i,4).id
                   


                    traffictransmitnodes.append(transmit_node)

                #Предоплаченный трафик
                for i in xrange(self.prepaid_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.prepaid_tableWidget, i)
                    
                    if self.prepaid_tableWidget.item(i, 1)==None or self.prepaid_tableWidget.item(i, 2)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для предоплаченного трафика")
                        self.connection.rollback()
                        return
                    
                    prepaid_node = AttrDict()
                    
                    if id:
                        prepaid_node.id = id

                    if 'id' in traffic_transmit_service:
                        prepaid_node.traffic_transmit_service = traffic_transmit_service.id
                    prepaid_node.group = self.prepaid_tableWidget.item(i,1).id
                    prepaid_node.size = unicode(int(float(self.prepaid_tableWidget.item(i,2).text())*1048576))

                    prepaidtrafficnodes.append(prepaid_node)


    
            elif (self.transmit_service_checkbox.checkState()==0) and "radius_traffic_transmit_service" in model:
                model.traffic_transmit_service=None


                
                            
        
            
            result=self.connection.tariff_save(data = {'model': model, 
                                                 'access_parameters':access_parameters, 
                                                 'speeds': speeds, 
                                                 'periodicalservices': periodicalservices, 
                                                 'traffic_transmit_service': traffic_transmit_service, 
                                                 'traffictransmitnodes': traffictransmitnodes, 
                                                 'prepaidtrafficnodes': prepaidtrafficnodes, 
                                                 'radiustrafficnodes': radiustrafficnodes, 
                                                 'radius_traffic_service': radius_traffic_service, 
                                                 'time_access_service': time_access_service,
                                                 'timeaccessnodes': timeaccessnodes,
                                                 'limites':limites, 
                                                 'onetimeservices': onetimeservices,
                                                 'addonservices': addonservices})
            
            self.model = self.connection.get_tariffs(id=result.tariff_id)
            self.model=model
            self.connection.commit()
            
            
        except Exception, e:
            print e
            traceback.print_exc()
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка сохранения тарифного плана\nВозможно тарифный план с таким именем уже существует или существовал раньше.")
            return
        
        self.parent.refreshTree()
        #QtGui.QDialog.accept(self)
             
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
        #QtGui.QDialog.reject(self)      
        

            

class AccountsMdiEbs(ebsTableView_n_TreeWindow):
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
        self.tb.setText(u"Информация")
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
                 ("messageDialogAction", "Сообщения", "images/messages.png", self.messageDialogForm), \
                 
                 ("actionEnableSession", "Включить на сервере доступа", "images/add.png", self.accountEnable), \
                 ("actionDisableSession", "Отключить на сервере доступа", "images/del.png", self.accountDisable), \
                 ("actionAddAccount", "Добавить на сервер доступа", "images/add.png", self.accountAdd), \
                 ("actionDeleteAccount", "Удалить с сервера доступа", "images/del.png", self.accountDelete), \
                 ("editTarifAction", "Редактировать", "images/edit.png", self.editTarif),\
                 ("editAccountAction", "Редактировать", "images/configure.png", self.editframe),\
                 ("connectionAgreementAction", "Договор на подключение", "images/Contract-icon.png", self.printAgreement),\
                 ("actionChangeTarif", "Сменить тарифный план", "images/tarif_change.png", self.changeTariff),\
                 ("actionSetSuspendedPeriod", "Отключить списание периодических услуг", "images/Lock-icon.png", self.suspended_period),\
                 ("actionLimitInfo", "Остаток трафика по лимитам", "images/traffic_limit.png", self.limit_info),\
                 ("actionPrepaidTrafficInfo", "Остаток предоплаченного трафика", "", self.prepaidtraffic_info),\
                 ("actionPrepaidRadiusTrafficInfo", "Остаток предоплаченного RADIUS трафика", "", self.radiusprepaidtraffic_info),\
                 ("actionPrepaidRadiusTimeInfo", "Остаток предоплаченного RADIUS времени ", "", self.radiusprepaidtime_info),\
                 ("actionSettlementPeriodInfo", "Информация по расчётным периодам", "images/sp.png", self.settlementperiod_info),\
                 ("rrdAccountTrafficInfo", "График использования канала аккаунтом", "images/bandwidth.png", self.rrdtraffic_info),\
                 ("radiusauth_logInfo", "Логи RADIUS авторизаций", "images/easytag.png", self.radiusauth_log),\
                 ("actionRadiusAttrs", "RADIUS атрибуты", "images/configure.png", self.radius_attrs),\
                 ("actionBalanceLog", "История изменения баланса", "images/money.png", self.balance_log),\
                 ("actionAccountFilter", "Поиск аккаунтов", "images/search_accounts.png", self.accountFilter),\
                 ("actionReports", "Отчёты и документы", "images/moneybook.png", self.reportForm),\
                 
                ]
                


        objDict = {self.treeWidget :["editTarifAction", "addTarifAction", "delTarifAction", "separator","actionRadiusAttrs",], \
                   self.tableWidget:["transactionAction", "addAction", "editAccountAction",  "delAction", "messageDialogAction", "rrdAccountTrafficInfo","radiusauth_logInfo", "transactionReportAction", "actionBalanceLog", "actionPrepaidTrafficInfo", "actionPrepaidRadiusTrafficInfo", "actionPrepaidRadiusTimeInfo", "actionChangeTarif"], \
                   self.toolBar    :["addTarifAction", "delTarifAction", "separator", "actionAccountFilter", "addAction", "delAction", "separator", "transactionAction", "transactionReportAction", "messageDialogAction""separator","actionRadiusAttrs",],\
                   self.toolBar2   :["actionChangeTarif", "actionSetSuspendedPeriod", "connectionAgreementAction", 'separator',  'radiusauth_logInfo', "actionBalanceLog"],\
                   self.menu   :[ 'actionSettlementPeriodInfo', 'separator', "separator", "actionLimitInfo", "separator", "actionPrepaidTrafficInfo", 'actionPrepaidRadiusTrafficInfo', 'actionPrepaidRadiusTimeInfo',"rrdAccountTrafficInfo"],\
                   self.reports_menu :["actionReports",],
                  }
        self.actionCreator(actList, objDict)
        
    def ebsPostInit(self, initargs):
        
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar2.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar2.setIconSize(QtCore.QSize(18,18))
        
        self.tableWidget.doubleClicked.connect(self.editframe) 
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
        self.refreshTree()
        self.refresh()
        
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
        #print accounts
        window = ReportMainWindow(template_id=template_id, accounts=accounts, connection = self.connection)
        self.parent.workspace.addWindow(window)
        window.show()
    
    def rrdtraffic_info(self):
        ids = self.get_selected_accounts()
        if ids:
            id=ids[0]
        window = RrdReportMainWindow(item_id=id, type='account', connection=self.connection)
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
        child = TarifWindow(connection=self.connection, parent=self)
        self.parent.workspace.addWindow(child)
        child.show()
        return
        #tarifframe = TarifFrame(connection=self.connection)
        #if tarifframe.exec_() == 1:
        #    #import datetime
        #    #print datetime.datetime.now()
        #    self.refreshTree()
        #    self.refresh()
        
    def get_selected_accounts(self):
        ids = []
        
        model = self.tableWidget.model()
        for index in self.tableWidget.selectionModel().selection().indexes():
            if index.column()!=0: continue
            ids.append(model.currentIdByIndex(index))
            

        return ids
    
    def changeTariff(self):
        tarif_id = None
        ids = self.get_selected_accounts()
        account=None
        #print "ids", ids
        if len(ids)==1:
            child=AddAccountTarif(connection=self.connection, account=account, get_info = True)
        else:
            child=AddAccountTarif(connection=self.connection, get_info = False)
        if child.exec_()==1:
            tarif_id = child.comboBox_tarif.itemData(child.comboBox_tarif.currentIndex()).toInt()[0]
            date = child.dateTimeEdit_start.currentDate()
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

    def radiusprepaidtime_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="radiusprepaidtime", account_id=id)
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
        ids=self.get_selected_accounts()    
                
        #print ids
        if not ids: return
        child=SuspendedPeriodForm()

        if child.exec_()==1:
            for id in ids:
                model = AttrDict()
                model.account = id
                model.start_date = child.start_date
                model.end_date = child.end_date
                self.connection.suspendedperiod_save(model)
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
                    tarif = self.connection.get("SELECT id FROM billservice_tariff WHERE name='%s'" % unicode(child.comboBox.currentText()))
    
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
                    self.connection.tariff_delete(tarif_id)
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
        tarif_id=self.getTarifId()
        if tarif_id<0: return
        model = self.connection.get_tariffs(tarif_id, normal_fields=False)
        
        #tarifframe = TarifFrame(connection=self.connection, model=model)
        child = TarifWindow(connection=self.connection, model=model, parent=self)
        self.parent.workspace.addWindow(child)
        child.show()
        return            
    
    def addframe(self):
        if self.getTarifId() in [-1000, -2000]: return
        tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
        self.connection.commit()
        #self.connection.flush()
        id = self.getTarifId()

        ipn_for_vpn=False
            
        #child = AddAccountFrame(connection=self.connection, tarif_id=id, ttype=tarif_type, ipn_for_vpn=ipn_for_vpn)
        child = AccountWindow(connection=self.connection, tarif_id=id, ttype=tarif_type, ipn_for_vpn=ipn_for_vpn, parent=self)
        self.parent.workspace.addWindow(child)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        child.show()
        return
        #self.connection.commit()
        #child = AddAccountFrame(connection=self.connection)


    def makeTransation(self):
        id = self.getSelectedId()
        account = self.connection.get_account(id, fields=['id'])
        child = TransactionForm(connection=self.connection, account = account)
        if child.exec_()==1:
            self.refresh()
       
    def prepaidReport(self):
        pass                                
            
    def transactionReport(self):
        id = self.getSelectedId()
        account = self.connection.get_account(id, fields=['id', 'username'])
        tr = TransactionsReport(connection=self.connection, account = account)
        self.parent.workspace.addWindow(tr)
        tr.show()
            
    
    def getSelectedId(self):
        index = self.tableWidget.selectionModel().currentIndex()
        
        return self.tableWidget.model().currentIdByIndex(index)


    def pass_(self):
        pass
    
    def delete(self):
        
        ids = self.get_selected_accounts()
        if not ids:return
        if QtGui.QMessageBox.question(self, u"Удалить аккаунты?" , u"Вы уверены, что хотите удалить выбранных пользователей из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.No:
            return

        for id in ids:
            if id>0:
                self.connection.accountActions(id, None, 'delete')
                self.connection.account_delete(id)
                self.connection.commit()
                self.refresh()


    @connlogin
    def editframe(self, *args, **kwargs):
        #print self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        id=self.getSelectedId()
        #print "id", id
        #print id
        if id == 0:
            return

        model = self.connection.get_account(id=id)

        if self.getTarifId()!=-3000:
            res = self.connection.account_ipn_for_vpn(model.id)
            if res.status==True:
                ipn_for_vpn = res.result
            else:
                return 
        else:
            ipn_for_vpn=False
            
        
        tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
        #addf = AddAccountFrame(connection=self.connection,tarif_id=self.getTarifId(), ttype=tarif_type, model=model, ipn_for_vpn=ipn_for_vpn)
        child = AccountWindow(connection=self.connection,tarif_id=self.getTarifId(), ttype=tarif_type, model=model, ipn_for_vpn=ipn_for_vpn, parent=self)
        
        self.parent.workspace.addWindow(child)
        #self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        child.show()
        return
        

    def addrow(self, value, x, y, id=None, color=None, enabled=True, ctext=None, setdata=False, organization=None):
        headerItem = QtGui.QTableWidgetItem()

        if value==None:
            value=''
        if type(value)==bool:
            value = u"Да" if value else u"Нет"
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
            if not organization:
                
                if enabled==True:
                    headerItem.setIcon(QtGui.QIcon("images/user.png"))
                else:
                    headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
            else:
                if enabled==True:
                    headerItem.setIcon(QtGui.QIcon("images/organization.png"))
                else:
                    headerItem.setIcon(QtGui.QIcon("images/organization_inactive.png"))
                                    
        #if setdata:
            #headerItem.setData(39, QtCore.QVariant(value))
        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))     
        elif isinstance(value,datetime.datetime):
            #.strftime(self.strftimeFormat)   
            #headerItem.setData(QtCore.Qt.DisplayRole, QtCore.QString(unicode(value.strftime(strftimeFormat))))         
            headerItem.setData(QtCore.Qt.DisplayRole, QtCore.QDateTime(value))
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
        tariffs = self.connection.gettariffs()
        #self.connection.commit()
        self.tableWidget.setColumnHidden(0, True)
        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -2000
        item.tarif_type = 'all'
        item.setText(0, u"Результаты поиска")
        item.setIcon(0,QtGui.QIcon("images/kfind.png"))        
        self.filter_item = item
        
        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -3000
        item.tarif_type = 'all'
        item.setText(0, u"Без тарифа")
        item.setIcon(0,QtGui.QIcon("images/new_users.png"))   
        
        self.tariffarchive_item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        self.tariffarchive_item.id = -10000
        self.tariffarchive_item.tarif_type = 'all'
        self.tariffarchive_item.setText(0, u"Архив тарифов")
        self.tariffarchive_item.setIcon(0,QtGui.QIcon("images/new_users.png"))   
        
        self.accountsarhive_item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        self.accountsarhive_item.id = -12000
        self.accountsarhive_item.tarif_type = 'all'
        self.accountsarhive_item.setText(0, u"Архив аккаунтов")
        self.accountsarhive_item.setIcon(0,QtGui.QIcon("images/new_users.png"))   

        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -4000
        item.tarif_type = 'all'
        item.setText(0, u"Физ. лица")
        item.setIcon(0,QtGui.QIcon("images/new_users.png"))   

        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
        item.id = -5000
        item.tarif_type = 'all'
        item.setText(0, u"Юр. лица")
        item.setIcon(0,QtGui.QIcon("images/new_users.png"))   
        
        for tarif in tariffs:
            if tarif.deleted:
                item = QtGui.QTreeWidgetItem(self.tariffarchive_item)
            else:
                item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
            item.id = tarif.id
            item.tarif_type = tarif.access_type
            item.setText(0, u"%s %s" % (tarif.access_type, tarif.name))
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
        
    def format_array(self, array):
        if type(array)==list:
            array=str(array)
        array=array.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('"', '').replace('\'', '')
        
        return str(array)
    
    def refresh(self, item=None, k=''):
        if item and not self.last_click:
            self.last_click = QtCore.QTime.currentTime()
            return
        now = QtCore.QTime.currentTime()
        if item and ((now.second() + now.msec()) - (1000*self.last_click.second()+self.last_click.msec())  )<500:
            #print "doubleclick"
            #print ((1000*now.second() + now.msec()) - (1000*self.last_click.second()+self.last_click.msec()) )
            self.last_click = None
            return
        else:
            #print "singleclick"       
            pass 
            
        
        self.tableWidget.setSortingEnabled(False)
        self.statusBar().showMessage(u"Ожидание ответа")
        self.treeWidget.dropEvent=self.treeWidgetDropEvent


        
        #print item
        if item:
            id=item.id
            if id==-1000 or id==-2000 or id==-4000 or id==-5000 or id==-12000:
                self.addAction.setDisabled(True)
                self.delAction.setDisabled(True)
                
            else:
                self.addAction.setDisabled(False)
                self.delAction.setDisabled(False)
        else:
            try:
                id=self.getTarifId()
                if id==-1000 or id==-2000 or id==-4000 or id==-5000 or id==-12000:
                    self.addAction.setDisabled(True)
                    self.delAction.setDisabled(True)
                    
                else:
                    self.addAction.setDisabled(False)
                    self.delAction.setDisabled(False)
            except:
                return
        


        #print "sql=", self.sql, id    
        #self.tableWidget.clearContents()  
        #self.tableWidget.setRowCount(0)
        #import json

        if id==-2000 :

            #accounts = self.connection.get_accounts_for_tilter(self.sql)
            accounts = self.connection.accountsfilter(self.sql)
            #AccountsFilterThread, AccountsRefreshThread
            #self.genericThread = AccountsFilterThread(self.connection, self.sql)
            #self.connect(self.genericThread, QtCore.SIGNAL("accountsRefresh(QVariant)"), self.fix)
            #self.genericThread.start()            
            #self.sql=''
        elif id!=-2000:
            #print "account for tarif", id
            #print "id===", id
            accounts = self.connection.accountsfortariff(id)
            #self.genericThread = AccountsRefreshThread(self.connection, self.getTarifId())
            #self.connect(self.genericThread, QtCore.SIGNAL("accountsRefresh(QVariant)"), self.fix)
            #self.genericThread.start()              
        else:
            return
        
        
        if id==-1000 or id==-2000 or id==-4000 or id==-5000 or id==-12000:
            #self.sql=''
            columns=[u'#', u'Аккаунт', u"Договор",u'Тарифный план', u'Баланс', u"Кредит", u'ФИО',  u'Адрес', u"VPN IP", u"IPN IP", u"MAC", u'Блокировка по балансу', u'Блокировка по лимитам' ,  u'Сессия активна',  u"Конец пакета", u'Создан',  u"Комментарий"]
            model = MyTableModel(datain = accounts, columns = columns)
            model.int_columns = ['id', 'username', 'contract',  'tariff_name', 'ballance', 'credit', 'fullname',  'address',  'vpn_ips', 'ipn_ips', 'ipn_macs', 'balance_blocked', 'disabled_by_limit', 'account_online', "sp_end", 'created',  'comment']
        else:
            columns=[u'#', u'Аккаунт',  u"Договор", u'Баланс', u"Кредит", u'ФИО', u'Адрес', u"VPN IP", u"IPN IP", u"MAC", u'Блокировка по балансу', u'Блокировка по лимитам' ,  u'Сессия активна',  u"Конец пакета", u'Создан',  u"Комментарий"]
            
            model = MyTableModel(datain = accounts, columns = columns)
            model.int_columns = ['id', 'username', 'contract', 'ballance', 'credit', 'fullname',  'address',  'vpn_ips', 'ipn_ips', 'ipn_macs', 'balance_blocked', 'disabled_by_limit', 'account_online',  "sp_end", 'created', 'comment']
        
        self.tableWidget.setModel(model)
        model.setIntColumns()

        id=self.getTarifId()
        #accounts=accounts.toList()
        #print accounts
        #self.tableWidget.setRowCount(len(accounts))
        HeaderUtil.getHeader("%s%s" % (self.setname,self.getTreeId()<0), self.tableWidget)
        #HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.delNodeLocalAction()
        #self.tablewidget.setShowGrid(False)
        self.tableWidget.setSortingEnabled(True)
        m_ballance = 0
        disabled_accounts = 0        
        for item in accounts:
            m_ballance+=float(item.ballance)
            if item.status!=1:
                disabled_accounts+=1
        self.statusBar().showMessage(u'Учётных записей:%s. Средний баланс: %.4f. Общий баланс: %.4f. Неактивно: %s' % (len(accounts), m_ballance/(1 if len(accounts)==0 else len(accounts)), m_ballance, disabled_accounts))
        return

        now = datetime.datetime.now()
        i=0
        for a in accounts:    
            
            #print dir(a)
            self.addrow(i, i,0, id=a.id, enabled=a.status, ctext=str(i+1), setdata=True)
            self.addrow(a.username, i,1, enabled=a.status)
            self.addrow(a.contract, i,2, enabled=a.status)
            #print "status", a
            disabled_accounts += 1 if a.status<>1 else 0
            if id==-1000 or id==-2000 or id==-4000 or id==-5000 or id==-12000:
                self.addrow(a.tariff, i,3, enabled=a.status, organization='')
                self.addrow(float("%.2f" % float(a.ballance or 0)), i,4, color="red", enabled=a.status)
                self.addrow(float(a.credit or 0), i,5, enabled=a.status)
                self.addrow(a.org_name if a.org_id else a.fullname, i,6, enabled=a.status)
                self.addrow(u"%s %s" % (a.address or '', u"кв %s" % a.room if a.room else ""), i,7, enabled=a.status)
                self.addrow(self.format_array(a.vpn_ips), i,8, enabled=a.status)
                self.addrow(self.format_array(a.ipn_ips), i,9, enabled=a.status)
                self.addrow(self.format_array(a.ipn_macs), i,10, enabled=a.status)
                #self.addrow(a.nas_name,i,7, enabled=a.status)
                #self.addrow(a.vpn_ip_address, i,7, enabled=a.status)
                #self.addrow(a.ipn_ip_address, i,8, enabled=a.status)
                #self.addrow(a.ipn_mac_address, i,9, enabled=a.status)
                self.addrow(a.suspended, i,11, enabled=a.status)
                #self.addrow(a.balance_blocked, i,11, enabled=a.status)
                #self.tableWidget.setCellWidget(i,11,simpleTableImageWidget(balance_blocked=a.balance_blocked, trafic_limit=a.disabled_by_limit, ipn_status=False, ipn_added=False, online_status=a.online_status))
                self.addrow(a.balance_blocked, i,12, enabled=a.status)
                self.addrow(a.disabled_by_limit, i,13, enabled=a.status)
                self.addrow(a.account_online, i,14, enabled=a.status)
                

                self.addrow(a.created, i,15, enabled=a.status)
                self.addrow(a.comment, i,16, enabled=a.status)
                #self.addrow(a.created, i,11, enabled=a.status)
            else:
                #self.addrow("%.2f" % a.ballance, i,2, color="red", enabled=a.status)
                self.addrow(float("%.2f" % float(a.ballance or 0)), i,3, color="red", enabled=a.status)
                self.addrow(float(a.credit or 0), i,4, enabled=a.status)
                self.addrow(a.org_name if a.org_id else a.fullname, i,5, enabled=a.status)
                self.addrow(u"%s %s" % (a.address or '', u"кв %s" % a.room if a.room else ""), i,6, enabled=a.status)
                self.addrow(self.format_array(a.vpn_ips), i,7, enabled=a.status)
                self.addrow(self.format_array(a.ipn_ips), i,8, enabled=a.status)
                self.addrow(self.format_array(a.ipn_macs), i,9, enabled=a.status)
                self.addrow(a.balance_blocked, i,10, enabled=a.status)
                self.addrow(a.disabled_by_limit, i,11, enabled=a.status)
                self.addrow(a.account_online, i,12, enabled=a.status)
                self.addrow(a.created, i,13, enabled=a.status)
                self.addrow(a.comment, i,14, enabled=a.status)
                #self.addrow(a.created, i,11, enabled=a.status)
                
            m_ballance += float(a.ballance or 0)
            #self.tableWidget.setRowHeight(i, 17)

            if self.selected_account:
                if self.selected_account.id == a.id:
                    self.tableWidget.setRangeSelected(QtGui.QTableWidgetSelectionRange(i,0,i,13), True)
            i+=1
            
        self.statusBar().showMessage(u'Учётных записей:%s. Средний баланс: %.4f. Общий баланс: %.4f. Неактивно: %s' % (len(accounts), m_ballance/(1 if len(accounts)==0 else len(accounts)), m_ballance, disabled_accounts))
        self.tableWidget.setColumnHidden(0, False)
        HeaderUtil.getHeader("%s%s" % (self.setname,self.getTreeId()<0), self.tableWidget)
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
        
    def printAgreement(self):
       

        models_id=self.get_selected_accounts()
        if len(models_id)!=1:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пакетная печать договоров невоможна. Выберите один аккаунт."))
            return
        model_id=models_id[0]
        
        operator = self.connection.get_operator()
        child = TemplateSelect(connection = self.connection)
        if child.exec_():
            template_id = child.id
        else:
            return
        template = self.connection.get_templates(template_id)
        templ = Template(template.body, input_encoding='utf-8')
        
        account = self.connection.get_account(model_id)
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
        

    def addNodeLocalAction(self):
        super(AccountsMdiEbs, self).addNodeLocalAction([self.addAction,self.delTarifAction, self.actionRadiusAttrs])
        
    def delNodeLocalAction(self):
        super(AccountsMdiEbs, self).delNodeLocalAction([self.delAction, self.actionChangeTarif, self.transactionAction,self.transactionReportAction, self.messageDialogAction,self.connectionAgreementAction,self.actionSetSuspendedPeriod,self.actionLimitInfo,self.actionPrepaidTrafficInfo,self.actionPrepaidRadiusTrafficInfo,self.actionPrepaidRadiusTimeInfo,self.actionSettlementPeriodInfo,self.rrdAccountTrafficInfo,self.radiusauth_logInfo, self.actionBalanceLog])
        
