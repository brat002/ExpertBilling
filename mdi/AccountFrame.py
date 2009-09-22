#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui

import Pyro.core
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
from Reports import TransactionsReportEbs as TransactionsReport

from helpers import tableFormat, check_speed
from helpers import transaction, makeHeaders
from helpers import Worker
from CustomForms import tableImageWidget, IPAddressSelectForm
from CustomForms import CustomWidget, CardPreviewDialog, SuspendedPeriodForm, GroupsDialog, SpeedLimitDialog, InfoDialog, PSCreatedForm, AccountAddonServiceEdit
from mako.template import Template
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
import IPy

class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

limit_actions = [CashType(0, u"Заблокировать пользователя"), CashType(1,u"Изменить скорость")]

la_list = [u"Заблокировать пользователя", u"Изменить скорость"]

ps_conditions = [CashType(0, u"При любом балансе"), CashType(1,u"При положительном и нулевом балансе"), CashType(2,u"При отрицательном балансе")]
ps_list = [u"При любом балансе", u"При положительном и нулевом балансе", u"При отрицательном балансе"]
class AddAccountTarif(QtGui.QDialog):
    def __init__(self, connection, account=None, get_info=False, model=None):
        super(AddAccountTarif, self).__init__()
        self.model=model
        self.get_info = get_info
        self.account=account
        self.connection = connection
        self.connection.commit()

        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()))
                            
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(130,140,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.hint_label = QtGui.QLabel(self)
        self.hint_label.setGeometry(QtCore.QRect(10,10,371,31))
        self.hint_label.setObjectName("hint_label")

        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(10,40,281,101))
        self.widget.setObjectName("widget")

        self.gridlayout = QtGui.QGridLayout(self.widget)
        self.gridlayout.setObjectName("gridlayout")

        self.tarif_label = QtGui.QLabel(self.widget)
        self.tarif_label.setObjectName("tarif_label")
        self.gridlayout.addWidget(self.tarif_label,0,0,1,1)

        self.tarif_edit = QtGui.QComboBox(self.widget)
        self.tarif_edit.setMaxVisibleItems(10)
        self.tarif_edit.setObjectName("tarif_edit")
        self.gridlayout.addWidget(self.tarif_edit,0,1,1,1)

        self.date_label = QtGui.QLabel(self.widget)
        self.date_label.setObjectName("date_label")
        self.gridlayout.addWidget(self.date_label,1,0,1,1)

        self.date_edit = QtGui.QDateTimeEdit(self.widget)
        self.date_edit.setFrame(True)
        self.date_edit.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_edit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setObjectName("date_edit")
        self.date_edit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridlayout.addWidget(self.date_edit,1,1,1,1)


        self.retranslateUi()
        self.fixtures()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)

    def accept(self):
        if self.get_info==False:
            date=self.date_edit.dateTime().toPyDateTime()
            if self.model:
                model=self.model
                model.datetime = date
            else:
                model = Object()
                model.account_id = self.account.id
                model.tarif_id =self.tarif_edit.itemData(self.tarif_edit.currentIndex()).toInt()[0]
                model.datetime = date
                
                #AccountTarif.objects.create(account=self.account, tarif=tarif, datetime=date)
            try:
                self.connection.save(model,"billservice_accounttarif")
                self.connection.commit()
            except Exception, e:
                print e
                self.conection.rollback()
        QtGui.QDialog.accept(self)


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование плана", None, QtGui.QApplication.UnicodeUTF8))
        self.hint_label.setText(QtGui.QApplication.translate("Dialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Выберите тарифный план и время, </span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\">когда должен быть осуществлён переход</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_label.setText(QtGui.QApplication.translate("Dialog", "Тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.date_label.setText(QtGui.QApplication.translate("Dialog", "Дата и время", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        tarifs=self.connection.sql("SELECT id, name FROM billservice_tariff WHERE deleted IS NOT TRUE ORDER BY name;")
        self.connection.commit()
        for tarif in tarifs:
            self.tarif_edit.addItem(tarif.name, QtCore.QVariant(tarif.id))
        now=datetime.datetime.now()
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            self.tarif_edit.setCurrentIndex(self.tarif_edit.findData(self.model.tarif_id))

            now = QtCore.QDateTime()

            now.setTime_t((mktime(self.model.datetime.timetuple())))
        self.date_edit.setDateTime(now)

    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)
        
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

        self.sp_type_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.sp_type_edit.setGeometry(QtCore.QRect(11,20,466,19))
        self.sp_type_edit.setObjectName("sp_type_edit")

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
        self.components_groupBox.setGeometry(QtCore.QRect(420,60,184,179))
        self.components_groupBox.setObjectName("components_groupBox")

        self.widget = QtGui.QWidget(self.components_groupBox)
        self.widget.setGeometry(QtCore.QRect(11,20,168,131))
        self.widget.setObjectName("widget")

        self.vboxlayout = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.transmit_service_checkbox = QtGui.QCheckBox(self.widget)
        self.transmit_service_checkbox.setObjectName("transmit_service_checkbox")
        self.vboxlayout.addWidget(self.transmit_service_checkbox)

        self.time_access_service_checkbox = QtGui.QCheckBox(self.widget)
        self.time_access_service_checkbox.setObjectName("time_access_service_checkbox")
        self.vboxlayout.addWidget(self.time_access_service_checkbox)

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
        

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.prepaid_time_label = QtGui.QLabel(self.tab_3)
        self.prepaid_time_label.setGeometry(QtCore.QRect(10,10,121,16))
        self.prepaid_time_label.setObjectName("prepaid_time_label")

        self.reset_time_checkbox = QtGui.QCheckBox(self.tab_3)
        self.reset_time_checkbox.setGeometry(QtCore.QRect(10,40,361,19))
        self.reset_time_checkbox.setObjectName("reset_time_checkbox")

        self.timeaccess_table = QtGui.QTableWidget(self.tab_3)
        self.timeaccess_table.setGeometry(QtCore.QRect(10,90,595,436))
        #----------------
        #self.timeaccess_table = tableFormat(self.timeaccess_table)
        #----------------

        self.timeaccess_panel = QtGui.QFrame(self.tab_3)
        self.timeaccess_panel.setGeometry(QtCore.QRect(10,60,596,27))
        self.timeaccess_panel.setFrameShape(QtGui.QFrame.Box)
        self.timeaccess_panel.setFrameShadow(QtGui.QFrame.Raised)
        self.timeaccess_panel.setObjectName("timeaccess_panel")

        self.del_timecost_button = QtGui.QToolButton(self.timeaccess_panel)
        self.del_timecost_button.setGeometry(QtCore.QRect(40,3,25,20))
        self.del_timecost_button.setObjectName("del_timecost_button")

        self.add_timecost_button = QtGui.QToolButton(self.timeaccess_panel)
        self.add_timecost_button.setGeometry(QtCore.QRect(6,3,24,20))
        self.add_timecost_button.setObjectName("add_timecost_button")

        self.prepaid_time_edit = QtGui.QSpinBox(self.tab_3)
        self.prepaid_time_edit.setGeometry(QtCore.QRect(130,10,221,21))
        self.prepaid_time_edit.setObjectName("prepaid_time_edit")
        


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
        self.tabWidget.addTab(self.tab_3,"")
        

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
        
        QtCore.QObject.connect(self.periodical_tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.periodicalServicesEdit)
        
        
        QtCore.QObject.connect(self.speed_table, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.speedEdit)
        
        QtCore.QObject.connect(self.tableWidget_addonservices, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.addonserviceEdit)
        
        QtCore.QObject.connect(self.add_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.addTrafficCostRow)
        QtCore.QObject.connect(self.del_traffic_cost_button, QtCore.SIGNAL("clicked()"), self.delTrafficCostRow)

        QtCore.QObject.connect(self.add_limit_button, QtCore.SIGNAL("clicked()"), self.addLimitRow)
        QtCore.QObject.connect(self.del_limit_button, QtCore.SIGNAL("clicked()"), self.delLimitRow)       

        QtCore.QObject.connect(self.add_onetime_button, QtCore.SIGNAL("clicked()"), self.addOneTimeRow)
        QtCore.QObject.connect(self.del_onetime_button, QtCore.SIGNAL("clicked()"), self.delOneTimeRow)        
        
        QtCore.QObject.connect(self.add_timecost_button, QtCore.SIGNAL("clicked()"), self.addTimeAccessRow)
        QtCore.QObject.connect(self.del_timecost_button, QtCore.SIGNAL("clicked()"), self.delTimeAccessRow)


        QtCore.QObject.connect(self.add_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.addPrepaidTrafficRow)
        QtCore.QObject.connect(self.del_prepaid_traffic_button, QtCore.SIGNAL("clicked()"), self.delPrepaidTrafficRow)        
        
        QtCore.QObject.connect(self.add_speed_button, QtCore.SIGNAL("clicked()"), self.addSpeedRow)
        QtCore.QObject.connect(self.del_speed_button, QtCore.SIGNAL("clicked()"), self.delSpeedRow)   
        
        QtCore.QObject.connect(self.add_periodical_button, QtCore.SIGNAL("clicked()"), self.addPeriodicalRow)
        QtCore.QObject.connect(self.del_periodical_button, QtCore.SIGNAL("clicked()"), self.delPeriodicalRow)   

        QtCore.QObject.connect(self.add_addonservice_button, QtCore.SIGNAL("clicked()"), self.addAddonServiceRow)
        QtCore.QObject.connect(self.del_addonservice_button, QtCore.SIGNAL("clicked()"), self.delAddonServiceRow)   
        
        QtCore.QObject.connect(self.sp_type_edit, QtCore.SIGNAL("stateChanged(int)"), self.filterSettlementPeriods)
        
        QtCore.QObject.connect(self.transmit_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.transmitTabActivityActions)
        
        QtCore.QObject.connect(self.time_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.timeaccessTabActivityActions)
        
        QtCore.QObject.connect(self.onetime_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.onetimeTabActivityActions)
        
        QtCore.QObject.connect(self.periodical_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.periodicalServicesTabActivityActions)
        
        QtCore.QObject.connect(self.limites_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.limitTabActivityActions)
        QtCore.QObject.connect(self.checkBox_addon_services, QtCore.SIGNAL("stateChanged(int)"), self.addonservicesTabActivityActions)
        QtCore.QObject.connect(self.ipn_for_vpn, QtCore.SIGNAL("stateChanged(int)"), self.ipn_for_vpnActions)

        QtCore.QObject.connect(self.sp_name_edit, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.spChangedActions)
#-----------------------        
        self.setTabOrder(self.tabWidget,self.sp_type_edit)
        self.setTabOrder(self.sp_type_edit,self.ps_null_ballance_checkout_edit)
        self.setTabOrder(self.ps_null_ballance_checkout_edit,self.reset_tarif_cost_edit)
        self.setTabOrder(self.reset_tarif_cost_edit,self.tarif_description_edit)
        self.setTabOrder(self.tarif_description_edit,self.tarif_status_edit)
        self.setTabOrder(self.tarif_status_edit,self.speed_max_in_edit)
        self.setTabOrder(self.speed_max_in_edit,self.speed_max_out_edit)
        self.setTabOrder(self.speed_max_out_edit,self.speed_min_in_edit)
        self.setTabOrder(self.speed_min_in_edit,self.speed_min_out_edit)
        self.setTabOrder(self.speed_min_out_edit,self.speed_burst_in_edit)
        self.setTabOrder(self.speed_burst_in_edit,self.speed_burst_out_edit)
        self.setTabOrder(self.speed_burst_out_edit,self.speed_burst_treshold_in_edit)
        self.setTabOrder(self.speed_burst_treshold_in_edit,self.speed_burst_treshold_out_edit)
        self.setTabOrder(self.speed_burst_treshold_out_edit,self.speed_burst_time_in_edit)
        self.setTabOrder(self.speed_burst_time_in_edit,self.speed_burst_time_out_edit)
        self.setTabOrder(self.speed_burst_time_out_edit,self.add_speed_button)
        self.setTabOrder(self.add_speed_button,self.del_speed_button)
        self.setTabOrder(self.del_speed_button,self.speed_table)
        self.setTabOrder(self.speed_table,self.reset_time_checkbox)
        self.setTabOrder(self.reset_time_checkbox,self.add_timecost_button)
        self.setTabOrder(self.add_timecost_button,self.del_timecost_button)
        self.setTabOrder(self.del_timecost_button,self.timeaccess_table)
        self.setTabOrder(self.timeaccess_table,self.reset_traffic_edit)
        self.setTabOrder(self.reset_traffic_edit,self.add_traffic_cost_button)
        self.setTabOrder(self.add_traffic_cost_button,self.del_traffic_cost_button)
        self.setTabOrder(self.del_traffic_cost_button,self.trafficcost_tableWidget)
        self.setTabOrder(self.trafficcost_tableWidget,self.add_prepaid_traffic_button)
        self.setTabOrder(self.add_prepaid_traffic_button,self.del_prepaid_traffic_button)
        self.setTabOrder(self.del_prepaid_traffic_button,self.prepaid_tableWidget)
        self.setTabOrder(self.prepaid_tableWidget,self.add_periodical_button)
        self.setTabOrder(self.add_periodical_button,self.del_periodical_button)
        self.setTabOrder(self.del_periodical_button,self.periodical_tableWidget)
        self.setTabOrder(self.periodical_tableWidget,self.onetime_tableWidget)
        self.setTabOrder(self.onetime_tableWidget,self.add_onetime_button)
        self.setTabOrder(self.add_onetime_button,self.del_onetime_button)
        self.setTabOrder(self.del_onetime_button,self.limit_tableWidget)
        self.setTabOrder(self.limit_tableWidget,self.del_limit_button)
        self.setTabOrder(self.del_limit_button,self.add_limit_button)
        self.setTabOrder(self.add_limit_button,self.buttonBox)  
        

        
    def retranslateUi(self):
        if self.model:
            self.setWindowTitle(u"Настройки тарифного плана %s" % self.model.name)
        else:
            self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки нового тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("Dialog", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("Dialog", "Фиксированный расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_type_edit.setText(QtGui.QApplication.translate("Dialog", "Начать при активации у пользователя данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("Dialog", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("Dialog", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        
        self.require_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Требовать наличия всей суммы", None, QtGui.QApplication.UnicodeUTF8))
        self.ps_null_ballance_checkout_edit.setText(QtGui.QApplication.translate("Dialog", "Производить снятие денег при нулевом балансе пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setText(QtGui.QApplication.translate("Dialog", "Способ доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setText(QtGui.QApplication.translate("Dialog", "Время доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Набор компонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_for_vpn.setText(QtGui.QApplication.translate("Dialog", "Производить IPN действия", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setText(QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_addon_services.setText(QtGui.QApplication.translate("Dialog", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
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

        columns=[u'#', u'Время', u'Цена']
        
        makeHeaders(columns, self.timeaccess_table)     
        
        self.del_timecost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_timecost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_traffic_edit.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце периода предоплаченый трафик", None, QtGui.QApplication.UnicodeUTF8))
        
        self.trafficcost_tableWidget.clear()
        columns=[u'#', u'От МБ', u'До МБ', u'Группа', u'Время', u'Цена за МБ']
        
        makeHeaders(columns, self.trafficcost_tableWidget)
        self.trafficcost_tableWidget.setColumnHidden(1, True)     
        self.trafficcost_tableWidget.setColumnHidden(2, True)

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
        columns=[u'#', u'Название', u'Период', u'Способ снятия', u'Стоимость', u"Условие", u"Начало списаний"]
        
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
        self.addrow(self.periodical_tableWidget, ps_list[0], current_row, 5)
        self.addrow(self.periodical_tableWidget, '', current_row, 6)
        #if QtGui.QMessageBox.question(self, u"Внимание!!!" , 
        #                                    u'''Вы хотите, чтобы по новой периодической услуге были поизведены списания с начала текущего расчётного периода?''', \
        #                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.No:
        #    self.periodical_tableWidget.item(current_row,5).created='now()'
        #else:
        #    self.periodical_tableWidget.item(current_row,5).created=None
        self.periodical_tableWidget.item(current_row,5).selected_id=0
        
        
    def delPeriodicalRow(self):
        current_row = self.periodical_tableWidget.currentRow()
        id = self.getIdFromtable(self.periodical_tableWidget, current_row)
        
        if id!=-1:
            self.connection.iddelete(id, "billservice_periodicalservice")
  
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

    #---------Local Logic
    def filterSettlementPeriods(self):
        
        self.sp_name_edit.clear()
        self.sp_name_edit.addItem("")
        if self.sp_type_edit.checkState()==2:         
            settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=True")
            ast=True
        else:
            ast=False
            settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=False")
            
        for sp in settlement_periods:
            self.sp_name_edit.addItem(sp.name)
            
        try:
            if self.model.settlement_period and self.model.settlement_period.autostart==ast:
                self.sp_name_edit.setCurrentIndex(self.sp_name_edit.findText(self.model.settlement_period.name, QtCore.Qt.MatchCaseSensitive))
        except:
            pass
            
    #------------------tab actions         
    def timeaccessTabActivityActions(self):
        if self.time_access_service_checkbox.checkState()!=2:
            self.tab_3.setDisabled(True)
            #self.tab_3.hide()
            #self.tabWidget.removeTab(3)
        else:
            self.tab_3.setDisabled(False)
            #self.tab_3.sho
            #self.tabWidget.insertTab(3, self.tab_3,"")
            #self.retranslateUi()
               
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
            
            text = QtGui.QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость", default_text)        
           
            self.timeaccess_table.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                
                                     
   
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
        
                  
        if x==2:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=self.connection.get_models("billservice_settlementperiod"), selected_item = default_text )
            if child.exec_()==1:
                #self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))
                print "selected_id", child.selected_id
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

        if x==3:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=cash_types, selected_item = default_text )
            if child.exec_()==1:
                self.addrow(self.periodical_tableWidget, child.comboBox.currentText(), y, x, 'combobox', child.selected_id)
             
        if x==4:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Цена:", u"Введите цену", default_text)        
           
            self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))


        if x==5:
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


        if x==6:
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
                if settlement_period.autostart==True:
                    
                    self.sp_type_edit.setChecked(True)
                        
                    settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=True")
                
                else:
                    settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=False")
                
            else:
                self.sp_groupbox.setChecked(False)
                settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=False")
        else:
            self.sp_groupbox.setChecked(False)
            settlement_periods = self.connection.sql("SELECT * FROM billservice_settlementperiod WHERE autostart=False")
        

        
        
        for sp in settlement_periods:
            self.sp_name_edit.addItem(sp.name)
            
        #print settlement_period.name




        access_types = ["PPTP", "PPPOE", "IPN", "HotSpot"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = self.connection.get_models("billservice_timeperiod")
        
        for at in access_time:
            self.access_time_edit.addItem(unicode(at.name))


        
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                self.sp_name_edit.setCurrentIndex(self.sp_name_edit.findText(settlement_period.name, QtCore.Qt.MatchCaseSensitive))
                
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
                    self.addrow(self.periodical_tableWidget, node.cash_method, i, 3)
                    self.addrow(self.periodical_tableWidget, node.cost,i, 4)
                    self.addrow(self.periodical_tableWidget, ps_list[node.condition],i, 5)
                    self.periodical_tableWidget.item(i, 5).selected_id = node.condition
                    if node.created:
                        self.addrow(self.periodical_tableWidget, node.created.strftime(strftimeFormat),i, 6)
                    else:
                        self.addrow(self.periodical_tableWidget, u"С начала расчётного периода",i, 6)
                    self.periodical_tableWidget.item(i, 6).created = node.created
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
                WHERE traffictransmitnodes.traffic_transmit_service_id=%d ORDER BY edge_start ASC
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
                        self.addrow(self.trafficcost_tableWidget, node.edge_start, i, 1)
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
        self.limitTabActivityActions()
        self.addonservicesTabActivityActions()
        self.trafficcost_tableWidget.resizeRowsToContents()
        self.trafficcost_tableWidget.resizeColumnsToContents()
        self.connection.commit()
        
        #self.trafficcost_tableWidget.resizeRowsToContents()

    def accept(self):
        #import datetime
        #print datetime.datetime.now()
        #self.connection.command("BEGIN;")
        if self.model:
            model=copy.deepcopy(self.model)
            access_parameters = Object()
            access_parameters.id=self.model.access_parameters_id
            access_parameters = self.connection.get(access_parameters.get("billservice_accessparameters"))
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
                    print 1
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



                
            if self.time_access_service_checkbox.checkState()==2 and self.timeaccess_table.rowCount()>0:

                    
                if not model.isnull('time_access_service_id'):
                    time_access_service = self.connection.get_model(self.model.time_access_service_id, "billservice_timeaccessservice" )
                else:
                    time_access_service=Object()
                #print 1
                time_access_service.reset_time = self.reset_time_checkbox.checkState()==2
                time_access_service.prepaid_time = unicode(self.prepaid_time_edit.text())
                
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
                    
                    periodical_service.tarif_id = model.id
                    periodical_service.name=unicode(self.periodical_tableWidget.item(i, 1).text())
                    periodical_service.settlement_period_id = unicode(self.periodical_tableWidget.item(i, 2).id)
                    periodical_service.cash_method = unicode(self.periodical_tableWidget.item(i, 3).text())
                    periodical_service.cost=unicode(self.periodical_tableWidget.item(i, 4).text())
                    periodical_service.condition = self.periodical_tableWidget.item(i,5).selected_id
                    periodical_service.created = self.periodical_tableWidget.item(i,6).created
                    
                    self.connection.save(periodical_service, "billservice_periodicalservice")    
                      
            elif self.periodical_services_checkbox.checkState()==0:
                    self.connection.iddelete(model.id, "billservice_periodicalservice") 
                

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
                        print e



            elif self.limites_checkbox.checkState()==0:
                d = Object()
                d.tarif_id = model.id
                self.connection.delete(d, "billservice_trafficlimit")

            #Подключаемые услуги
            if self.tableWidget_addonservices.rowCount()>0 and self.checkBox_addon_services.checkState()==2:
                for i in xrange(0, self.tableWidget_addonservices.rowCount()):
                    #print 2
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
                    self.connection.iddelete(model.id, "billservice_addonservicetarif") 
                    
                                
            #Доступ по трафику 
            if self.trafficcost_tableWidget.rowCount()>0 and self.transmit_service_checkbox.checkState()==2:
                if not model.isnull('traffic_transmit_service_id'):
                    #print "'traffic_transmit_service'1"
                    traffic_transmit_service = self.connection.get_model(self.model.traffic_transmit_service_id, "billservice_traffictransmitservice")
                else:
                    #print 'traffic_transmit_service2'
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
                    transmit_node.edge_start = unicode(self.trafficcost_tableWidget.item(i,1).text() or 0)
                    transmit_node.edge_end = unicode(self.trafficcost_tableWidget.item(i,2).text() or 0)
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


    
            elif (self.transmit_service_checkbox.checkState()==0 or self.trafficcost_tableWidget.rowCount()==0) and not model.isnull("traffic_transmit_service_id"):
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
            return self.connection.accountActions(x, "create")
        elif prev==True and now==False:
            return self.connection.accountActions(x, "delete")
            
    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)        
            
            
class AccountWindow(QtGui.QMainWindow):
    def __init__(self, connection, tarif_id, ttype, model=None, ipn_for_vpn=False):
        super(AccountWindow, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection
        self.ipn_for_vpn = ipn_for_vpn
        self.tarif_id = tarif_id
        self.organization = None
        self.bank = None
        
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
        self.gridLayout_13 = QtGui.QGridLayout(self.tab_general)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.groupBox_account_data = QtGui.QGroupBox(self.tab_general)
        self.groupBox_account_data.setMinimumSize(QtCore.QSize(381, 82))
        self.groupBox_account_data.setMaximumSize(QtCore.QSize(381, 86))
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
        self.gridLayout_13.addWidget(self.groupBox_account_data, 0, 0, 2, 2)
        self.groupBox_agreement = QtGui.QGroupBox(self.tab_general)
        self.groupBox_agreement.setMinimumSize(QtCore.QSize(391, 86))
        self.groupBox_agreement.setMaximumSize(QtCore.QSize(3910, 84))
        self.groupBox_agreement.setObjectName("groupBox_agreement")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_agreement)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_agreement_date = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_date.setObjectName("label_agreement_date")
        self.gridLayout_4.addWidget(self.label_agreement_date, 0, 0, 1, 1)
        #
        #self.lineEdit_agreement_date = QtGui.QLineEdit(self.groupBox_agreement)
        #self.lineEdit_agreement_date.setEnabled(False)
        #self.lineEdit_agreement_date.setMinimumSize(QtCore.QSize(0, 20))
        #self.lineEdit_agreement_date.setObjectName("lineEdit_agreement_date")
        #self.gridLayout_4.addWidget(self.lineEdit_agreement_date, 0, 1, 1, 1)
        #
        self.dateTimeEdit_agreement_date = QtGui.QDateTimeEdit(self.groupBox_agreement)
        self.dateTimeEdit_agreement_date.setMinimumSize(QtCore.QSize(0, 20))
        
        self.gridLayout_4.addWidget(self.dateTimeEdit_agreement_date, 0, 1, 1, 1)
        self.label_agreement_num = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_num.setObjectName("label_agreement_num")
        self.gridLayout_4.addWidget(self.label_agreement_num, 1, 0, 1, 1)
        self.lineEdit_agreement_num = QtGui.QLineEdit(self.groupBox_agreement)
        self.lineEdit_agreement_num.setEnabled(False)
        self.lineEdit_agreement_num.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_agreement_num.setObjectName("lineEdit_agreement_num")
        self.gridLayout_4.addWidget(self.lineEdit_agreement_num, 1, 1, 1, 1)
        self.toolButton_agreement_print = QtGui.QToolButton(self.groupBox_agreement)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_agreement_print.setIcon(icon)
        self.toolButton_agreement_print.setObjectName("toolButton_agreement_print")
        self.gridLayout_4.addWidget(self.toolButton_agreement_print, 1, 2, 1, 1)
        self.gridLayout_13.addWidget(self.groupBox_agreement, 0, 2, 2, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_general)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_19 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.plainTextEdit_comment = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit_comment.setObjectName("plainTextEdit_comment")
        self.gridLayout_19.addWidget(self.plainTextEdit_comment, 0, 0, 1, 1)
        self.gridLayout_13.addWidget(self.groupBox, 6, 2, 2, 1)
        self.groupBox_status = QtGui.QGroupBox(self.tab_general)
        self.groupBox_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_status.setObjectName("groupBox_status")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_status)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_status = QtGui.QComboBox(self.groupBox_status)
        self.comboBox_status.setObjectName("comboBox_status")
        self.horizontalLayout.addWidget(self.comboBox_status)
        self.gridLayout_13.addWidget(self.groupBox_status, 7, 0, 1, 2)
        self.tableWidget = QtGui.QTableWidget(self.tab_general)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setObjectName("AccountWindow-account_info")

        self.gridLayout_13.addWidget(self.tableWidget, 2, 0, 2, 3)
        self.groupBox_balance_info = QtGui.QGroupBox(self.tab_general)
        self.groupBox_balance_info.setMinimumSize(QtCore.QSize(391, 0))
        self.groupBox_balance_info.setMaximumSize(QtCore.QSize(3910, 1656465))
        self.groupBox_balance_info.setObjectName("groupBox_balance_info")
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_balance_info)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_balance = QtGui.QLabel(self.groupBox_balance_info)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_9.addWidget(self.label_balance, 0, 0, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_balance.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.lineEdit_balance.setDisabled(True)
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
        self.gridLayout_13.addWidget(self.groupBox_balance_info, 6, 0, 1, 1)
        self.tabWidget.addTab(self.tab_general, "")
        
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
        self.gridLayout_17.addWidget(self.groupBox_nas, 0, 0, 1, 1)
        self.groupBox_ipn = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_ipn.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_ipn.setMaximumSize(QtCore.QSize(597000, 151))
        self.groupBox_ipn.setObjectName("groupBox_ipn")
        self.gridLayout_15 = QtGui.QGridLayout(self.groupBox_ipn)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.label_ipn_ip_address = QtGui.QLabel(self.groupBox_ipn)
        self.label_ipn_ip_address.setObjectName("label_ipn_ip_address")
        self.gridLayout_15.addWidget(self.label_ipn_ip_address, 0, 0, 1, 1)
        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_ipn_ip_address.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_ipn_ip_address.setObjectName("lineEdit_ipn_ip_address")
        self.gridLayout_15.addWidget(self.lineEdit_ipn_ip_address, 0, 1, 1, 1)
        self.toolButton_get_ipn_from_pool = QtGui.QToolButton(self.groupBox_ipn)
        
        self.toolButton_get_ipn_from_pool.setObjectName("toolButton_get_ipn_from_pool")
        self.gridLayout_15.addWidget(self.toolButton_get_ipn_from_pool, 0, 2, 1, 1)
        self.comboBox_ipn_pool = QtGui.QComboBox(self.groupBox_ipn)

        self.comboBox_ipn_pool.setMinimumSize(QtCore.QSize(150, 20))
        self.comboBox_ipn_pool.setObjectName("comboBox_ipn_pool")
        self.gridLayout_15.addWidget(self.comboBox_ipn_pool, 0, 3, 1, 1)
        self.label_ipn_mac_address = QtGui.QLabel(self.groupBox_ipn)
        self.label_ipn_mac_address.setObjectName("label_ipn_mac_address")
        self.gridLayout_15.addWidget(self.label_ipn_mac_address, 2, 0, 1, 1)
        self.lineEdit_ipn_mac_address = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_ipn_mac_address.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_ipn_mac_address.setObjectName("lineEdit_ipn_mac_address")
        self.gridLayout_15.addWidget(self.lineEdit_ipn_mac_address, 2, 1, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_ipn, 1, 0, 1, 1)
        self.groupBox_vpn = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_vpn.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_vpn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_vpn.setObjectName("groupBox_vpn")
        self.gridLayout_20 = QtGui.QGridLayout(self.groupBox_vpn)
        self.gridLayout_20.setObjectName("gridLayout_20")
        self.label_vpn_ip_address = QtGui.QLabel(self.groupBox_vpn)
        self.label_vpn_ip_address.setObjectName("label_vpn_ip_address")
        self.gridLayout_20.addWidget(self.label_vpn_ip_address, 0, 0, 1, 1)
        self.lineEdit_vpn_ip_address = QtGui.QLineEdit(self.groupBox_vpn)
        self.lineEdit_vpn_ip_address.setMinimumSize(QtCore.QSize(170, 20))
        self.lineEdit_vpn_ip_address.setObjectName("lineEdit_vpn_ip_address")
        self.gridLayout_20.addWidget(self.lineEdit_vpn_ip_address, 0, 2, 1, 1)
        self.toolButton_get_vpn_from_pool = QtGui.QToolButton(self.groupBox_vpn)

        self.toolButton_get_vpn_from_pool.setObjectName("toolButton_get_vpn_from_pool")
        self.gridLayout_20.addWidget(self.toolButton_get_vpn_from_pool, 0, 3, 1, 1)
        self.comboBox_vpn_pool = QtGui.QComboBox(self.groupBox_vpn)

        self.comboBox_vpn_pool.setMinimumSize(QtCore.QSize(150, 20))
        self.comboBox_vpn_pool.setObjectName("comboBox_vpn_pool")
        self.gridLayout_20.addWidget(self.comboBox_vpn_pool, 0, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_20.addItem(spacerItem, 0, 1, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_vpn, 2, 0, 1, 1)
        self.groupBox_accessparameters = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_accessparameters.setObjectName("groupBox_accessparameters")
        self.gridLayout_16 = QtGui.QGridLayout(self.groupBox_accessparameters)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.checkBox_allow_webcab = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_webcab.setObjectName("checkBox_allow_webcab")
        self.checkBox_allow_webcab.setChecked(True)
        
        self.gridLayout_16.addWidget(self.checkBox_allow_webcab, 3, 0, 1, 1)
        self.checkBox_allow_expresscards = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_expresscards.setObjectName("checkBox_allow_expresscards")
        self.checkBox_allow_expresscards.setChecked(True)
        self.gridLayout_16.addWidget(self.checkBox_allow_expresscards, 4, 0, 1, 1)
        self.checkBox_assign_dhcp_null = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_assign_dhcp_null.setObjectName("checkBox_assign_dhcp_null")
        self.gridLayout_16.addWidget(self.checkBox_assign_dhcp_null, 5, 0, 1, 1)
        self.checkBox_assign_dhcp_block = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_assign_dhcp_block.setObjectName("checkBox_assign_dhcp_block")
        self.gridLayout_16.addWidget(self.checkBox_assign_dhcp_block, 6, 0, 1, 1)
        self.checkBox_allow_vpn_null = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_vpn_null.setObjectName("checkBox_allow_vpn_null")
        self.gridLayout_16.addWidget(self.checkBox_allow_vpn_null, 7, 0, 1, 1)
        self.checkBox_allow_vpn_block = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_vpn_block.setObjectName("checkBox_allow_vpn_block")
        self.gridLayout_16.addWidget(self.checkBox_allow_vpn_block, 8, 0, 1, 1)
        self.checkBox_associate_pptp_ipn_ip = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_associate_pptp_ipn_ip.setObjectName("checkBox_associate_pptp_ipn_ip")
        self.gridLayout_16.addWidget(self.checkBox_associate_pptp_ipn_ip, 1, 0, 1, 1)
        self.checkBox_associate_pppoe_mac = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_associate_pppoe_mac.setObjectName("checkBox_associate_pppoe_mac")
        self.gridLayout_16.addWidget(self.checkBox_associate_pppoe_mac, 2, 0, 1, 1)
        self.checkBox_assign_ipn_ip_from_dhcp = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_assign_ipn_ip_from_dhcp.setObjectName("checkBox_assign_ipn_ip_from_dhcp")
        self.gridLayout_16.addWidget(self.checkBox_assign_ipn_ip_from_dhcp, 0, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_accessparameters, 3, 0, 1, 2)
        self.groupBox_vpn_speed = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_vpn_speed.setMinimumSize(QtCore.QSize(0, 56))
        self.groupBox_vpn_speed.setCheckable(True)
        self.groupBox_vpn_speed.setChecked(False)
        self.groupBox_vpn_speed.setObjectName("groupBox_vpn_speed")
        self.gridLayout_11 = QtGui.QGridLayout(self.groupBox_vpn_speed)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.vpn_speed_lineEdit = QtGui.QLineEdit(self.groupBox_vpn_speed)
        self.vpn_speed_lineEdit.setObjectName("vpn_speed_lineEdit")
        self.gridLayout_11.addWidget(self.vpn_speed_lineEdit, 0, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_vpn_speed, 4, 0, 1, 3)
        self.groupBox_ipn_speed = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_ipn_speed.setMinimumSize(QtCore.QSize(0, 56))
        self.groupBox_ipn_speed.setCheckable(True)
        self.groupBox_ipn_speed.setChecked(False)
        self.groupBox_ipn_speed.setObjectName("groupBox_ipn_speed")
        self.gridLayout_10 = QtGui.QGridLayout(self.groupBox_ipn_speed)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.ipn_speed_lineEdit = QtGui.QLineEdit(self.groupBox_ipn_speed)
        self.ipn_speed_lineEdit.setObjectName("ipn_speed_lineEdit")
        self.gridLayout_10.addWidget(self.ipn_speed_lineEdit, 0, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_ipn_speed, 5, 0, 1, 3)
        self.groupBox_8021_x = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_8021_x.setEnabled(True)
        self.groupBox_8021_x.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox_8021_x.setMaximumSize(QtCore.QSize(191, 16500))
        self.groupBox_8021_x.setFlat(False)
        self.groupBox_8021_x.setCheckable(True)
        self.groupBox_8021_x.setChecked(False)
        self.groupBox_8021_x.setObjectName("groupBox_8021_x")
        self.gridLayout_12 = QtGui.QGridLayout(self.groupBox_8021_x)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.lineEdit_8021x_port = QtGui.QLineEdit(self.groupBox_8021_x)
        self.lineEdit_8021x_port.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_8021x_port.setObjectName("lineEdit_8021x_port")
        self.gridLayout_12.addWidget(self.lineEdit_8021x_port, 1, 1, 1, 1)
        self.comboBox_8021x_nas = QtGui.QComboBox(self.groupBox_8021_x)
        self.comboBox_8021x_nas.setMinimumSize(QtCore.QSize(0, 20))
        self.comboBox_8021x_nas.setObjectName("comboBox_8021x_nas")
        self.gridLayout_12.addWidget(self.comboBox_8021x_nas, 0, 1, 1, 1)
        self.label_8021x_port = QtGui.QLabel(self.groupBox_8021_x)
        self.label_8021x_port.setObjectName("label_8021x_port")
        self.gridLayout_12.addWidget(self.label_8021x_port, 1, 0, 1, 1)
        self.label_8021x_nas = QtGui.QLabel(self.groupBox_8021_x)
        self.label_8021x_nas.setObjectName("label_8021x_nas")
        self.gridLayout_12.addWidget(self.label_8021x_nas, 0, 0, 1, 1)
        self.radioButton_8021x_port_auth = QtGui.QRadioButton(self.groupBox_8021_x)
        self.radioButton_8021x_port_auth.setObjectName("radioButton_8021x_port_auth")
        self.gridLayout_12.addWidget(self.radioButton_8021x_port_auth, 3, 0, 1, 2)
        self.radioButton_8021x_login_auth = QtGui.QRadioButton(self.groupBox_8021_x)
        self.radioButton_8021x_login_auth.setChecked(True)
        self.radioButton_8021x_login_auth.setObjectName("radioButton_8021x_login_auth")
        self.gridLayout_12.addWidget(self.radioButton_8021x_login_auth, 2, 0, 1, 2)
        self.lineEdit_vlan_accept = QtGui.QLineEdit(self.groupBox_8021_x)
        self.lineEdit_vlan_accept.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_vlan_accept.setObjectName("lineEdit_vlan_accept")
        self.gridLayout_12.addWidget(self.lineEdit_vlan_accept, 4, 1, 1, 1)
        self.label_vlan_accept = QtGui.QLabel(self.groupBox_8021_x)
        self.label_vlan_accept.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_vlan_accept.setObjectName("label_vlan_accept")
        self.gridLayout_12.addWidget(self.label_vlan_accept, 4, 0, 1, 1)
        self.lineEdit_vlan_reject = QtGui.QLineEdit(self.groupBox_8021_x)
        
        self.lineEdit_vlan_reject.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_vlan_reject.setObjectName("lineEdit_vlan_reject")
        self.gridLayout_12.addWidget(self.lineEdit_vlan_reject, 5, 1, 1, 1)
        self.label_vlan_reject = QtGui.QLabel(self.groupBox_8021_x)
        self.label_vlan_reject.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_vlan_reject.setObjectName("label_vlan_reject")
        self.gridLayout_12.addWidget(self.label_vlan_reject, 5, 0, 1, 1)
        self.checkBox_8021x_simpleauth = QtGui.QCheckBox(self.groupBox_8021_x)
        self.checkBox_8021x_simpleauth.setObjectName("checkBox_8021x_simpleauth")
        self.gridLayout_12.addWidget(self.checkBox_8021x_simpleauth, 6, 0, 1, 2)
        self.gridLayout_17.addWidget(self.groupBox_8021_x, 0, 1, 3, 1)
        self.tabWidget.addTab(self.tab_network_settings, "")
        self.tab_suspended = QtGui.QWidget()
        self.tab_suspended.setObjectName("tab_suspended")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_suspended)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.tableWidget_suspended = QtGui.QTableWidget(self.tab_suspended)
        self.tableWidget_suspended.setObjectName("tableWidget_suspended")
        self.gridLayout_5.addWidget(self.tableWidget_suspended, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_suspended, "")
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
        #self.label_name.setBuddy(self.lineEdit_name)
        #self.label_balance.setBuddy(self.lineEdit_balance)
        ##self.label_credit.setBuddy(self.lineEdit_credit)
        #self.label_ipn_ip_address.setBuddy(self.lineEdit_ipn_ip_address)
        #self.label_ipn_mac_address.setBuddy(self.lineEdit_ipn_mac_address)

        self.retranslateUi()
        HeaderUtil.nullifySaved(self.tableWidget.objectName())
        self.firsttime = True
        
        self.tabWidget.setCurrentIndex(0)
        
        QtCore.QMetaObject.connectSlotsByName(self)

        
        self.connect(self.toolButton_generate_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_generate_password,QtCore.SIGNAL("clicked()"),self.generate_password)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        self.connect(self.checkBox_assign_ipn_ip_from_dhcp, QtCore.SIGNAL("stateChanged(int)"), self.dhcpActions)
        self.connect(self.tableWidget_accounttarif, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)
        self.connect(self.tableWidget_addonservice, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.editAccountInfo)
        
        self.connect(self.actionAdd, QtCore.SIGNAL("triggered()"), self.add_action)
        self.connect(self.actionDel, QtCore.SIGNAL("triggered()"), self.del_action)
        self.connect(self.toolButton_agreement_print, QtCore.SIGNAL("clicked()"), self.printAgreement)
        
        self.connect(self.toolButton_get_ipn_from_pool,QtCore.SIGNAL("clicked()"),self.get_ipn_from_pool)
        self.connect(self.toolButton_get_vpn_from_pool,QtCore.SIGNAL("clicked()"),self.get_vpn_from_pool)
        
        self.fixtures()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.tableWidget.objectName(), bhdr)
            HeaderUtil.getHeader(self.tableWidget.objectName(), self.tableWidget)
        else: self.firsttime = False
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        self.dhcpActions()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Профиль аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_account_data.setTitle(QtGui.QApplication.translate("MainWindow", "Учётные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_login.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.label_password.setText(QtGui.QApplication.translate("MainWindow", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_password.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_agreement.setTitle(QtGui.QApplication.translate("MainWindow", "Договор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_date.setText(QtGui.QApplication.translate("MainWindow", "Дата подключения", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_num.setText(QtGui.QApplication.translate("MainWindow", "Номер договора", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================
#        self.groupBox_account_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о пользователе", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_name.setText(QtGui.QApplication.translate("MainWindow", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_address.setText(QtGui.QApplication.translate("MainWindow", "Email", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_phone_h.setText(QtGui.QApplication.translate("MainWindow", "Телефон дом.", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_passport_n.setText(QtGui.QApplication.translate("MainWindow", "Паспорт №", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_passport_give.setText(QtGui.QApplication.translate("MainWindow", "Кем выдан", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_passport_date.setText(QtGui.QApplication.translate("MainWindow", "Когда выдан", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_phone_m.setText(QtGui.QApplication.translate("MainWindow", "Телефон моб.", None, QtGui.QApplication.UnicodeUTF8))
#        self.groupBox_urdata.setTitle(QtGui.QApplication.translate("MainWindow", "Юридическое лицо", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_organization.setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_rs.setText(QtGui.QApplication.translate("MainWindow", "Расчётный счёт", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_okpo.setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_unp.setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_bank.setText(QtGui.QApplication.translate("MainWindow", "Банк, код банка", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_uraddress.setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_urphone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_fax.setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
#        self.groupBox_address.setTitle(QtGui.QApplication.translate("MainWindow", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_city.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_region.setText(QtGui.QApplication.translate("MainWindow", "Район", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_street.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_house.setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_house_bulk.setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_room.setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_20.setText(QtGui.QApplication.translate("MainWindow", "Индекс", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_entrance.setText(QtGui.QApplication.translate("MainWindow", "Подъезд", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================
        #self.groupBox_manager.setTitle(QtGui.QApplication.translate("MainWindow", "Работа с клиентом", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_manager.setText(QtGui.QApplication.translate("MainWindow", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_balance_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("MainWindow", "Текущий баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("MainWindow", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_credit.setText(QtGui.QApplication.translate("MainWindow", "Работать в кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_general), QtGui.QApplication.translate("MainWindow", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_nas.setTitle(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("MainWindow", "Основной сервера доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ipn.setTitle(QtGui.QApplication.translate("MainWindow", "IPN IP Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_ip_address.setText(QtGui.QApplication.translate("MainWindow", "Текущий IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_bank_code.setText(QtGui.QApplication.translate("MainWindow", "Код", None, QtGui.QApplication.UnicodeUTF8))
        
        
        #---------
        
#===============================================================================
#        self.tableWidget.item(0, 0).setText(QtGui.QApplication.translate("MainWindow", "Контактное лицо", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(1, 0).setText(QtGui.QApplication.translate("MainWindow", "Тел. Контактного лица", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(2, 0).setText(QtGui.QApplication.translate("MainWindow", "ФИО абонента", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(3, 0).setText(QtGui.QApplication.translate("MainWindow", "e-mail", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(4, 0).setText(QtGui.QApplication.translate("MainWindow", "Телефон дом.", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(5, 0).setText(QtGui.QApplication.translate("MainWindow", "Телефон моб.", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(6, 0).setText(QtGui.QApplication.translate("MainWindow", "Паспорт №", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(7, 0).setText(QtGui.QApplication.translate("MainWindow", "Кем выдан", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(8, 0).setText(QtGui.QApplication.translate("MainWindow", "Когда выдан", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(9, 0).setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(10, 0).setText(QtGui.QApplication.translate("MainWindow", "Индекс", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(11, 0).setText(QtGui.QApplication.translate("MainWindow", "Район", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(12, 0).setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(13, 0).setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(14, 0).setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(15, 0).setText(QtGui.QApplication.translate("MainWindow", "Подъезд", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(16, 0).setText(QtGui.QApplication.translate("MainWindow", "Этаж", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(17, 0).setText(QtGui.QApplication.translate("MainWindow", "Направление от лифта", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(18, 0).setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(19, 0).setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(20, 0).setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(21, 0).setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(22, 0).setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(23, 0).setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
#        self.tableWidget.item(24, 0).setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================
        
        self.tableWidget.setColumnHidden(0, False)
        columns = [u"Название", u"Значение"]
        makeHeaders(columns, self.tableWidget)
        #self.tableWidget.
        
        self.tableInfo=[
            #['ur', u'Юридическое лицо','checkbox'],
            ['contactperson', u'Контактное лицо',''],
            ['contactperson_phone', u'Тел. Контактного лица',''],
            ['fullname', u'ФИО абонента',''],
            ['email',u'e-mail',''],
            ['phone_h',u'Телефон дом.',''],
            ['phone_m',u'Телефон моб.',''],
            ['passport',u'Паспорт №',''],
            ['passport_given',u'Кем выдан',''],
            ['passport_date',u'Когда выдан',''],
            ['city', u'Город',''],
            ['postcode',u'Индекс',''],
            ['region',u'Район',''],
            ['street',u'Улица',''],
            ['house',u'Дом',''],
            ['house_bulk',u'Корпус',''],
            ['entrance',u'Подъезд',''],
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
                self.addrow(self.tableWidget, '', i, 1, widget_type = item[2])
            i+=1
            

        #self.tableWidget.resizeColumnsToContents()
        #------------
        self.toolButton_get_ipn_from_pool.setText(QtGui.QApplication.translate("MainWindow", "Выдать из пула", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_ipn_ip_mask.setText(QtGui.QApplication.translate("MainWindow", "Маска подсети", None, QtGui.QApplication.UnicodeUTF8))
        
        self.label_ipn_mac_address.setText(QtGui.QApplication.translate("MainWindow", "Аппаратный адрес", None, QtGui.QApplication.UnicodeUTF8))
        
        #self.label_vlan.setText(QtGui.QApplication.translate("MainWindow", "VLAN ID", None, QtGui.QApplication.UnicodeUTF8))
        
        self.checkBox_assign_ipn_ip_from_dhcp.setText(QtGui.QApplication.translate("MainWindow", "Выдавать IP адрес с помощью DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_8021_x.setTitle(QtGui.QApplication.translate("MainWindow", "802.1x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8021x_port.setText(QtGui.QApplication.translate("MainWindow", "Порт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8021x_nas.setText(QtGui.QApplication.translate("MainWindow", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_8021x_port_auth.setText(QtGui.QApplication.translate("MainWindow", "Авторизация по MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_8021x_login_auth.setText(QtGui.QApplication.translate("MainWindow", "Авторизация по логину", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vlan_accept.setText(QtGui.QApplication.translate("MainWindow", "VLAN Accept", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vlan_reject.setText(QtGui.QApplication.translate("MainWindow", "VLAN Reject", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_8021x_simpleauth.setToolTip(QtGui.QApplication.translate("MainWindow", "Авторизация без применения правил и параметров тарифного плана(разрешённое время работы)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_8021x_simpleauth.setText(QtGui.QApplication.translate("MainWindow", "Простая авторизация", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_contactperson.setText(QtGui.QApplication.translate("MainWindow", "Контактное лицо", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_contactphone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_vpn.setTitle(QtGui.QApplication.translate("MainWindow", "VPN IP Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pptp_ipn_ip.setText(QtGui.QApplication.translate("MainWindow", "Привязать PPTP авторизацию к IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pppoe_mac.setText(QtGui.QApplication.translate("MainWindow", "Привязать PPPOE авторизацию к MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ip_address.setText(QtGui.QApplication.translate("MainWindow", "VPN IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_get_vpn_from_pool.setText(QtGui.QApplication.translate("MainWindow", "Выдать из пула", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_accessparameters.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_webcab.setText(QtGui.QApplication.translate("MainWindow", "Разрешить пользоваться веб-кабинетом", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_expresscards.setText(QtGui.QApplication.translate("MainWindow", "Разрешить активировать карты экспресс-оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_assign_dhcp_null.setText(QtGui.QApplication.translate("MainWindow", "Выдавать адрес по DHCP при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_assign_dhcp_block.setText(QtGui.QApplication.translate("MainWindow", "Выдавать адрес по DHCP, если клиент неактивен, заблокирован или находится в режиме простоя", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_null.setText(QtGui.QApplication.translate("MainWindow", "Разрешить PPTP/PPPOE авторизацию при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_block.setText(QtGui.QApplication.translate("MainWindow", "Разрешить PPTP/PPPOE авторизацию, если клиент неактивен, заблокирован или находится в режиме простоя", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_vpn_speed.setTitle(QtGui.QApplication.translate("MainWindow", "Индивидуальные настройки скорости для VPN", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ipn_speed.setTitle(QtGui.QApplication.translate("MainWindow", "Индивидуальные настройки скорости для IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_network_settings), QtGui.QApplication.translate("MainWindow", "Сетевые параметры", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_suspended), QtGui.QApplication.translate("MainWindow", "Не списывать ПУ", None, QtGui.QApplication.UnicodeUTF8))

        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_downtime), QtGui.QApplication.translate("MainWindow", "Периоды простоя", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tarifs), QtGui.QApplication.translate("MainWindow", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addonservice), QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_documents), QtGui.QApplication.translate("MainWindow", "Документы", None, QtGui.QApplication.UnicodeUTF8))
        #self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDel.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_status.setTitle(QtGui.QApplication.translate("MainWindow", "Статус аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        #self.checkBox_active.setText(QtGui.QApplication.translate("MainWindow", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        #self.checkBox_suspended.setText(QtGui.QApplication.translate("MainWindow", "Отключить ПУ", None, QtGui.QApplication.UnicodeUTF8))
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)
        
        self.lineEdit_ipn_ip_address.setValidator(self.ipValidator)
        self.lineEdit_vpn_ip_address.setValidator(self.ipValidator)
        #self.lineEdit_ipn_ip_mask.setValidator(self.ipValidator)
        self.lineEdit_ipn_mac_address.setValidator(self.macValidator)
        
        self.tableWidget_accounttarif.clear()

        columns = ["#", u"С",u"По"]
        self.tableWidget_suspended = tableFormat(self.tableWidget_suspended)
        makeHeaders(columns, self.tableWidget_suspended)
        
        columns=[u'#', u'Тарифный план', u'Дата']
        self.tableWidget_accounttarif = tableFormat(self.tableWidget_accounttarif)
        makeHeaders(columns, self.tableWidget_accounttarif)


        columns=[u'#', u'Название услуги', u'Дата активации', u'Дата окончания', u'Активирована на сервере доступа', u"Временная блокировка"]
        self.tableWidget_addonservice = tableFormat(self.tableWidget_addonservice)
        makeHeaders(columns, self.tableWidget_addonservice)
        
        #columns = ["#", u"С", u"По", u"Списано"]
        #makeHeaders(columns, self.tableWidget_downtime)
                
        #columns = ["#", u'Тип документа', u"Дата", u"Подписан", u"Отослан по E-mail"]
        #makeHeaders(columns, self.tableWidget_documents)
        
        #self.tabWidget.removeTab(self.tab_documents)
        #self.tabWidget.removeTab(self.tab_downtime)
        #self.tabWidget.removeTab(self.tab_suspended)
        self.comboBox_status.addItem(u"Активен")
        self.comboBox_status.setItemData(0, QtCore.QVariant(1))
        self.comboBox_status.addItem(u"Неактивен, не списывать периодические услуги")
        self.comboBox_status.setItemData(1, QtCore.QVariant(2))
        self.comboBox_status.addItem(u"Неактивен, списывать периодические услуги")
        self.comboBox_status.setItemData(2, QtCore.QVariant(3))
        

    def saveHeader(self, *args):

        HeaderUtil.saveHeader(self.tableWidget.objectName(), self.tableWidget)
            
    def printAgreement(self):
       
        tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id = get_tarif(%s)" % self.model.id)
        operator = self.connection.get("SELECT * FROM billservice_operator LIMIT 1")
        if self.groupBox_urdata.isChecked()==True:
            template = self.connection.get("SELECT * FROM billservice_template WHERE type_id=2")
            try:
                data=templ.render_unicode(account=self.model, tarif=tarif, operator=operator, organization = self.organization, bank=self.bank, created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=u"Error %s" % str(e)
            templ = Template(template.body, input_encoding='utf-8')
        else:
            template = self.connection.get("SELECT * FROM billservice_template WHERE type_id=1")
            templ = Template(template.body, input_encoding='utf-8')
            
            try:
                data=templ.render_unicode(account=self.model, tarif=tarif, created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=u"Error %s" % str(e)
            self.connection.commit()
            file= open('templates/tmp/temp.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            a=CardPreviewDialog(url="templates/tmp/temp.html")
            a.exec_()
       
       
           
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
            
  
    def generate_login(self):
        self.lineEdit_username.setText(nameGen())

    def generate_password(self):
        self.lineEdit_password.setText(GenPasswd2())
        
    def dhcpActions(self, newstate=0):
        pass
    
    def fixtures(self):


        pools = []

        nasses = self.connection.get_models("nas_nas")
        self.connection.commit()
        i=0
        self.comboBox_nas.clear()
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name)
            self.comboBox_8021x_nas.addItem(nas.name)
            self.comboBox_nas.setItemData(i, QtCore.QVariant(nas.id))
            self.comboBox_8021x_nas.setItemData(i, QtCore.QVariant(nas.id))
            if self.model:
                if nas.id==self.model.nas_id:
                    self.comboBox_nas.setCurrentIndex(i)
            
            i+=1
        if self.model:
            if self.model.isnull('vpn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.vpn_ipinuse_id)[0]
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
            
            i+=1

        if self.model:
            if self.model.isnull('ipn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.ipn_ipinuse_id)[0]
            
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
            i+=1

                  
        if not self.model:
            self.actionAdd.setDisabled(True)
            self.actionDel.setDisabled(True)
            self.toolButton_agreement_print.setDisabled(True)
            self.lineEdit_balance.setText(u"0")
            self.lineEdit_credit.setText(u"0")

        self.dateTimeEdit_agreement_date.setDateTime(datetime.datetime.now())
        if self.model:
            self.lineEdit_agreement_num.setText("%s" % self.model.id)
            #self.lineEdit_agreement_date.setText(unicode(self.model.created.strftime(strftimeFormat)))
            self.dateTimeEdit_agreement_date.setDateTime(self.model.created)
            self.dateTimeEdit_agreement_date.setDisabled(True)
            #model.status = self.comboBox_status.itemData(self.comboBox.currentIndex()).toInt()[0]
            #print dir(self.model)
            self.comboBox_status.setCurrentIndex(self.model.status-1)
            #self.checkBox_suspended.setChecked(self.model.suspended)
            #self.checkBox_active.setChecked(self.model.status)

            self.lineEdit_username.setText(unicode(self.model.username))
            self.lineEdit_password.setText(unicode(self.model.password))
            
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, unicode(self.model.__dict__.get(self.tableInfo[i][0],'')), i,1)


            #self.tableWidget.resizeColumnsToContents()
#===============================================================================
#            self.lineEdit_name.setText(unicode(self.model.fullname))
#            
#            
#            self.lineEdit_email.setText(unicode(self.model.email))
#            
#            self.lineEdit_contactperson.setText(unicode(self.model.contactperson))
#            self.lineEdit_contactphone.setText(unicode(self.model.contactperson_phone))
#            self.lineEdit_city.setText(unicode(self.model.city))
#            self.lineEdit_postcode.setText(unicode(self.model.postcode))
#            self.lineEdit_region.setText(unicode(self.model.region))
#            self.lineEdit_street.setText(unicode(self.model.street))
#            self.lineEdit_house.setText(unicode(self.model.house))
#            self.lineEdit_house_bulk.setText(unicode(self.model.house_bulk))
#            self.lineEdit_entrance.setText(unicode(self.model.entrance))
#            self.lineEdit_room.setText(unicode(self.model.room))
#            self.lineEdit_phone_h.setText(unicode(self.model.phone_h))
#            self.lineEdit_phone_m.setText(unicode(self.model.phone_m))
#===============================================================================

            self.plainTextEdit_comment.setPlainText(unicode(self.model.comment))
            
#===============================================================================
#            #passport
#            self.lineEdit_passport_n.setText(u"%s" % self.model.passport)
#            self.lineEdit_passport_given.setText(u"%s" % self.model.passport_given)
#            try:
#                self.dateEdit_passport_date.setDate(QtCore.QDate(self.model.passport_date.year,self.model.passport_date.month, self.model.passport_date.day))
#            except:
#                print "passport date error"
#===============================================================================
            
            #self.lineEdit_ipn_ip_mask.setText(unicode(self.model.netmask))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
            self.lineEdit_vpn_ip_address.setText(unicode(self.model.vpn_ip_address))
            #self.lineEdit_vlan.setText(unicode(self.model.vlan))
            
            if self.model.ipn_mac_address==None or self.model.ipn_mac_address=="":
                self.checkBox_assign_ipn_ip_from_dhcp.setCheckState(QtCore.Qt.Checked)
                
            else:
                self.lineEdit_ipn_mac_address.setText(unicode(self.model.ipn_mac_address))

            #print "self.model.status", self.model.status
            #self.status_edit.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.suspended_edit.setCheckState(self.model.suspended == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            self.checkBox_assign_ipn_ip_from_dhcp.setCheckState(self.model.assign_ipn_ip_from_dhcp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            self.lineEdit_balance.setText(unicode(self.model.ballance))
            self.lineEdit_credit.setText(unicode(self.model.credit))
            
            if self.model.vpn_speed!="" and self.model.vpn_speed!=None:
                self.groupBox_vpn_speed.setChecked(True)
                self.vpn_speed_lineEdit.setText(self.model.vpn_speed)
            else:
                self.groupBox_vpn_speed.setChecked(False)
                
            if self.model.ipn_speed!="" and self.model.ipn_speed!=None:
                self.groupBox_ipn_speed.setChecked(True)
                self.ipn_speed_lineEdit.setText(self.model.ipn_speed)
            else:
                self.groupBox_ipn_speed.setChecked(False)
            
            self.checkBox_allow_webcab.setChecked(self.model.allow_webcab or False)
            self.checkBox_allow_expresscards.setChecked(self.model.allow_expresscards or False)
            self.checkBox_assign_dhcp_null.setChecked(self.model.assign_dhcp_null or False)
            self.checkBox_assign_dhcp_block.setChecked(self.model.assign_dhcp_block or False)
            self.checkBox_allow_vpn_null.setChecked(self.model.allow_vpn_null or False)
            self.checkBox_allow_vpn_block.setChecked(self.model.allow_vpn_block or False)
            self.checkBox_associate_pptp_ipn_ip.setChecked(self.model.associate_pptp_ipn_ip  or False)
            self.checkBox_associate_pppoe_mac.setChecked(self.model.associate_pppoe_mac  or False)
            
            
            
            
            x8021 = self.connection.sql("SELECT * FROM billservice_x8021 WHERE account_id = %s" % self.model.id)
            
            if x8021:
                x8021 = x8021[0]
                self.groupBox_8021_x.setEnabled(True)
                for x in xrange(self.comboBox_8021x_nas.count()):
                    if self.comboBox_8021x_nas.itemData(x).toInt()[0]==x8021.nas_id:
                        self.comboBox_8021x_nas.setCurrentIndex(x)
                self.lineEdit_8021x_port.setText(unicode(x8021.port  or ""))
                self.lineEdit_vlan_accept.setText(unicode(x8021.vlan_accept  or ""))
                self.lineEdit_vlan_reject.setText(unicode(x8021.vlan_reject  or ""))
                self.radioButton_8021x_login_auth.setChecked(x8021.typeauth == "BY_LOGIN")
                self.groupBox_8021_x.setChecked(True)
            organization = self.connection.get_models("billservice_organization", where={'account_id':self.model.id})
            self.connection.commit()
            if organization!=[]:
                
                org = organization[0]
                self.organization = org
                self.groupBox_urdata.setChecked(True)
                self.lineEdit_organization.setText(unicode(org.name))
                self.lineEdit_uraddress.setText(unicode(org.uraddress))
                self.lineEdit_urphone.setText(unicode(org.phone))
                self.lineEdit_fax.setText(unicode(org.fax))
                self.lineEdit_okpo.setText(unicode(org.okpo))
                self.lineEdit_unp.setText(unicode(org.unp))
                
                #print "bank_id",org.bank_id
                bank = self.connection.get_model(org.bank_id, "billservice_bankdata")
                self.connection.commit()
                if bank:
                    self.lineEdit_bank.setText(unicode(bank.bank))
                    self.lineEdit_bank_code.setText(unicode(bank.bankcode))
                    self.lineEdit_rs.setText(unicode(bank.rs))
            
            else:
                #self.groupBox_urdata.setChecked(False)
                pass
            self.accountTarifRefresh()
            self.suspendedPeriodRefresh()
            self.accountAddonServiceRefresh()
        else:
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, '', i,1)

    def accept(self):
        """
        понаставить проверок
        """
        try:
            
            if self.model:
                model=self.model
            else:
                print 'New account'
                if self.connection.get("SELECT count(*) as count FROM billservice_account WHERE username='%s'" % unicode(self.lineEdit_username.text())).count > 0:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                    self.connection.rollback()
                    return

                model=Object()
                model.created = self.dateTimeEdit_agreement_date.dateTime().toPyDateTime()
                #model.user_id=1
                model.ipn_status = False
                model.ipn_added = False
                model.disabled_by_limit = False
                model.vpn_ipinuse_id = None
                model.ipn_ipinuse_id = None
                
                
            model.username = unicode(self.lineEdit_username.text())
            if model.username=='':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не указали имя пользователя."))
                return 
            #print 1
            model.password = unicode(self.lineEdit_password.text())
#===============================================================================
#            model.fullname = unicode(self.lineEdit_name.text())
#            model.email = unicode(self.lineEdit_email.text())
#            
#            model.fullname = unicode(self.lineEdit_name.text())
#            
#            model.city = unicode(self.lineEdit_city.text())
#            model.postcode = unicode(self.lineEdit_postcode.text())
#            
#            model.region = unicode(self.lineEdit_region.text())
#            model.street = unicode(self.lineEdit_street.text())
#            model.house = unicode(self.lineEdit_house.text())
#            model.house_bulk = unicode(self.lineEdit_house_bulk.text())
#            model.entrance = unicode(self.lineEdit_entrance.text())
#            model.room = unicode(self.lineEdit_room.text())
#            model.phone_h = unicode(self.lineEdit_phone_h.text())
#            model.phone_m = unicode(self.lineEdit_phone_m.text())
#            #passport
#            model.passport = unicode(self.lineEdit_passport_n.text())
#            model.passport_given = unicode(self.lineEdit_passport_given.text())
#            model.passport_date = self.dateEdit_passport_date.date().toPyDate()
#           
#            model.contactperson = unicode(self.lineEdit_contactperson.text())
#            model.contactperson_phone = unicode(self.lineEdit_contactphone.text())
#===============================================================================
            model.status = self.comboBox_status.itemData(self.comboBox_status.currentIndex()).toInt()[0]
            for i in xrange(self.tableWidget.rowCount()):
                model.__dict__[self.tableInfo[i][0]] = unicode(self.tableWidget.item(i,1).text()) 
                #self.tableWidget.item(i,1).setText(unicode(self.model.__dict__.get(self.tableInfo[i][0])))
                
            #print "passport_date", self.model.passport_date
            #dateTime().toPyDateTime()
            
            if self.groupBox_vpn_speed.isChecked()==True and self.vpn_speed_lineEdit.text()!="":
                model.vpn_speed = unicode(self.vpn_speed_lineEdit.text())
            else:
                model.vpn_speed = ""

            if self.groupBox_ipn_speed.isChecked()==True and self.ipn_speed_lineEdit.text()!="":
                model.ipn_speed = unicode(self.ipn_speed_lineEdit.text())
            else:
                model.ipn_speed = ""

            if self.lineEdit_ipn_ip_address.text():
                if self.ipValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка в IPN IP."))
                    return
                try:
                    ipn_address_account_id = self.connection.get("SELECT id FROM billservice_account WHERE ipn_ip_address='%s'" % unicode(self.lineEdit_ipn_ip_address.text())).id
                    if ipn_address_account_id!=model.id:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
                        self.connection.rollback()
                        return  
                                          
                except Exception, ex:
                    pass
                model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text())
                
            elif self.ttype in ['IPN', 'HotSpot']:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте IPN IP."))
                return
            else:
                model.ipn_ip_address = u'0.0.0.0'
            
                    
            if self.lineEdit_vpn_ip_address.text():
                if self.ipValidator.validate(self.lineEdit_vpn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка в VPN IP."))
                    return
                try:
                    vpn_address_account_id = self.connection.get("SELECT id FROM billservice_account WHERE vpn_ip_address='%s'" % unicode(self.lineEdit_vpn_ip_address.text())).id
                    #print "vpn_address_account_id", vpn_address_account_id
                    if vpn_address_account_id!=model.id:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
                        self.connection.rollback()
                        return    
                          
                except Exception, ex:
                    pass
                
                model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text())
            elif self.ttype == 'VPN':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте заполнение VPN IP."))
                return
            else:
                model.vpn_ip_address = u'0.0.0.0'
                



#===============================================================================
#            model.netmask = '0.0.0.0'
#            if self.lineEdit_ipn_ip_mask.isEnabled():
#                if self.lineEdit_ipn_ip_mask.text():
#                    if self.ipValidator.validate(self.lineEdit_ipn_ip_mask.text(), 0)[0]  != QtGui.QValidator.Acceptable:
#                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Маска указана неверно."))
#                        self.connection.rollback()
#                        return
#                    model.netmask = unicode(self.lineEdit_ipn_ip_mask.text())
#===============================================================================


            #model.netmask = unicode(self.netmask_edit.text())
            if ((model.ipn_ip_address == '0.0.0.0') and (model.vpn_ip_address == '0.0.0.0')):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Должен быть введён хотя бы один из адресов"))
                self.connection.rollback()
                return

            if self.lineEdit_ipn_mac_address.text().isEmpty()==False:
                if self.macValidator.validate(self.lineEdit_ipn_mac_address.text(), 0)[0]  == QtGui.QValidator.Acceptable:
                    try:
                        id = self.connection.get("SELECT id FROM billservice_account WHERE ipn_mac_address='%s'" % unicode(self.lineEdit_ipn_mac_address.text()).upper()).id
                        if id!=model.id :
                            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
                            self.connection.rollback()
                            return
                    except:
                        pass
                    model.ipn_mac_address = unicode(self.lineEdit_ipn_mac_address.text()).upper()
                else:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте MAC адрес."))
                    self.connection.rollback()
                    return
            else:
                model.ipn_mac_address=u""

            model.nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
            #model.vlan = unicode(self.lineEdit_vlan.text()) or 0

            model.ballance = unicode(self.lineEdit_balance.text()) or 0
            model.credit = unicode(self.lineEdit_credit.text()) or 0

            model.assign_ipn_ip_from_dhcp = self.checkBox_assign_ipn_ip_from_dhcp.isChecked()
            #model.suspended = self.checkBox_suspended.isChecked()
            #model.status = self.checkBox_active.isChecked()

            if model.ipn_ip_address=="0.0.0.0" and self.ipn_for_vpn==True:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Для работы на этом тарифном плане у пользователя должен быть указан IPN IP."))
                self.connection.rollback()
                return



            model.allow_webcab = self.checkBox_allow_webcab.checkState() == QtCore.Qt.Checked
            model.allow_expresscards = self.checkBox_allow_expresscards.checkState() == QtCore.Qt.Checked
            model.assign_dhcp_null = self.checkBox_assign_dhcp_null.checkState() == QtCore.Qt.Checked
            model.assign_dhcp_block = self.checkBox_assign_dhcp_block.checkState() == QtCore.Qt.Checked
            model.allow_vpn_null = self.checkBox_allow_vpn_null.checkState() == QtCore.Qt.Checked
            model.allow_vpn_block = self.checkBox_allow_vpn_block.checkState() == QtCore.Qt.Checked
            model.associate_pptp_ipn_ip = self.checkBox_associate_pptp_ipn_ip.checkState() == QtCore.Qt.Checked
            model.associate_pppoe_mac = self.checkBox_associate_pppoe_mac.checkState() == QtCore.Qt.Checked
            model.comment = unicode(self.plainTextEdit_comment.toPlainText())

            if self.model:
                if model.ipn_ip_address!=self.model.ipn_ip_address:
                    """
                    Если изменили IPN IP адрес-значит нужно добавить новый адрес в лист доступа
                    """
                    model.ipn_status=False
                model.id = self.connection.save(model, "billservice_account")
            else:
                #print 123
                model.id=self.connection.save(model, "billservice_account")
                accounttarif = Object()
                accounttarif.account_id=model.id
                accounttarif.tarif_id=self.tarif_id
                accounttarif.datetime = "now()"
                self.connection.save(accounttarif,"billservice_accounttarif")

#            if self.groupBox_urdata.isChecked():
#                if unicode(self.lineEdit_organization.text())=="" or unicode(self.lineEdit_bank.text())=="":
#                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указаны реквизиты юридического лица."))
#                    return
#                if self.organization:
#                    org = self.organization
#                    bank = self.connection.get_model(org.bank_id, "billservice_bankdata")
#                else:
#                    org = Object()
#                    bank = Object()
#                
#                bank.bank = unicode(self.lineEdit_bank.text())
#                bank.bankcode = unicode(self.lineEdit_bank_code.text())
#                bank.rs = self.lineEdit_rs.text()
#                bank.currency = ''
#                bank.id = self.connection.save(bank, "billservice_bankdata")
#                self.bank = bank
#                
#                org.name = unicode(self.lineEdit_organization.text())
#                org.uraddress = unicode(self.lineEdit_uraddress.text())
#                org.phone = unicode(self.lineEdit_urphone.text())
#                org.fax = unicode(self.lineEdit_fax.text())
#                org.okpo = unicode(self.lineEdit_okpo.text())
#                org.unp = unicode(self.lineEdit_unp.text())
#                org.account_id = model.id
#                org.bank_id = bank.id
#                org.id = self.connection.save(org, "billservice_organization")
#                self.organization = org
#                #print "save org.data"
#            else:
#                if self.organization:
#                    self.connection.iddelete(self.organization.id, "billservice_organization")    
            
 
             #Операции с пулом    
            try:
                if model.isnull('ipn_ipinuse_id')==False and model.ipn_ip_address=='0.0.0.0':
                    old_ipn = model.ipn_ipinuse_id
                    model.ipn_ipinuse_id = None
                    self.connection.save(model, "billservice_account")
                    self.connection.iddelete(old_ipn, "billservice_ipinuse")
                
                if model.ipn_ip_address!='0.0.0.0':
                    if model.isnull('ipn_ipinuse_id')==False:
                        ipn_ip_model = self.connection.get_model(model.ipn_ipinuse_id, "billservice_ipinuse")
                    elif model.isnull('ipn_ipinuse_id')==True:
                        ipn_ip_model = Object()
                
                    pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
                    
                    if pool_id!=0:
                        pool = self.connection.get_model(pool_id, "billservice_ippool")
                        start_ip = IPy.IP(pool.start_ip).int()
                        end_ip = IPy.IP(pool.end_ip).int()
                        ip = IPy.IP(unicode(self.lineEdit_ipn_ip_address.text())).int()

                        if ip < start_ip or ip>end_ip: raise Exception
                        
                        ipn_ip_model.pool_id = pool_id
                        
                        ipn_ip_model.ip = unicode(self.lineEdit_ipn_ip_address.text())
                        ipn_ip_model.datetime = "now()"
                        ipn_ip_model.id = self.connection.save(ipn_ip_model, "billservice_ipinuse")
                        model.ipn_ipinuse_id = ipn_ip_model.id
                    else:
                        model.ipn_ipinuse_id = None
                
                    self.connection.save(model, "billservice_account")
            except Exception:
                print e
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте настройки IPN IP адресов. Возможно выбранный IP адрес уже используется в пуле или не принадлежит выбранному пулу."))
                self.connection.rollback()
                return 

             #Операции с пулом    
            try:
                if model.isnull('vpn_ipinuse_id')==False and model.vpn_ip_address=='0.0.0.0':
                    old_vpn = model.vpn_ipinuse_id
                    model.vpn_ipinuse_id = None
                    self.connection.save(model, "billservice_account")
                    self.connection.iddelete(old_vpn, "billservice_ipinuse")
                
                if model.vpn_ip_address!='0.0.0.0':
                    if model.isnull('vpn_ipinuse_id')==False:
                        vpn_ip_model = self.connection.get_model(model.vpn_ipinuse_id, "billservice_ipinuse")
                    elif model.isnull('vpn_ipinuse_id')==True:
                        vpn_ip_model = Object()
                
                    pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
                    if pool_id!=0:
                        pool = self.connection.get_model(pool_id, "billservice_ippool")
                        start_ip = IPy.IP(pool.start_ip).int()
                        end_ip = IPy.IP(pool.end_ip).int()
                        ip = IPy.IP(unicode(self.lineEdit_vpn_ip_address.text())).int()

                        if ip < start_ip or ip>end_ip: raise Exception
                        
                        #ipn_ip_model.pool_id = pool_id
                        vpn_ip_model.pool_id = pool_id
                        vpn_ip_model.ip = unicode(self.lineEdit_vpn_ip_address.text())
                        vpn_ip_model.datetime = "now()"
                        vpn_ip_model.id = self.connection.save(vpn_ip_model, "billservice_ipinuse")
                        model.vpn_ipinuse_id = vpn_ip_model.id
                    else:
                        model.vpn_ipinuse_id = None
                
                    self.connection.save(model, "billservice_account")
            except:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте настройки VPN IP адресов. Возможно выбранный IP адрес уже используется в пуле или не принадлежит выбранному пулу."))
                    self.connection.rollback()
                    return 
                
            #Проверка статуса             

#===============================================================================
#            if not model.isnull("id"):
#                try:
#                    speriod = self.connection.sql("SELECT * FROM billservice_suspendedperiod WHERE end_date is Null and account_id=%s ORDER BY start_date ASC LIMIT 1" % self.model.id)[0]
#                except:
#                    speriod = None
#                    
#                if speriod:
#                    if model.status in [1, 3]:
#                        speriod.end_date="now()"
#                        self.connection.save(speriod, "billservice_suspendedperiod")
#                            
#                if not speriod and not model.isnull("status"):
#                    if model.status==2:
#                        speriod = Object()
#                        speriod.start_date = "now()"
#                        speriod.account_id = model.id
#                        
#                        self.connection.save(speriod, "billservice_suspendedperiod")
#===============================================================================
                    
            if not model.isnull("id"):
                x8021 = self.connection.sql("SELECT * FROM billservice_x8021 WHERE account_id = %s" % model.id)
            else:
                x8021 = None
                
            if self.groupBox_8021_x.isChecked():
                if x8021:
                    x8021_model = x8021[0]
                else:
                    x8021_model = Object()
                x8021_model.account_id = model.id
                x8021_model.nas_id = self.comboBox_8021x_nas.itemData(self.comboBox_8021x_nas.currentIndex()).toInt()[0]
                x8021_model.port = unicode(self.lineEdit_8021x_port.text()) or None
                x8021_model.typeauth = "BY_LOGIN" if self.radioButton_8021x_login_auth.isChecked() else "BY_MAC"
                x8021_model.vlan_accept = unicode(self.lineEdit_vlan_accept.text()) or None
                x8021_model.vlan_reject = unicode(self.lineEdit_vlan_reject.text()) or None
                x8021_model.simpleauth = self.checkBox_8021x_simpleauth.isChecked()
                self.connection.save(x8021_model, "billservice_x8021")
            else:
                self.connection.command("DELETE FROM billservice_x8021 WHERE account_id=%s" % model.id)
                    
            #x8021 = self.connection.get
            self.connection.commit()
            self.model = model
            self.fixtures()
            self.emit(QtCore.SIGNAL("refresh()"))
        except Exception, e:
            import traceback
            traceback.print_exc()
            if isinstance(e, psycopg2.InternalError) and e.args[0].startswith('Amount'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Достигнуто максимальное число пользователей. \n" + e.args[0]))
            else:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при сохранении."))
            self.connection.rollback()
            return
        
    def accountTarifRefresh(self):
        if self.model:
            ac=self.connection.sql("""SELECT accounttarif.*, tarif.name as tarif_name FROM billservice_accounttarif as accounttarif 
            JOIN billservice_tariff as tarif ON tarif.id=accounttarif.tarif_id
            WHERE account_id=%d AND tarif.deleted IS NOT TRUE ORDER BY datetime ASC""" % self.model.id)
            self.tableWidget_accounttarif.setRowCount(len(ac))
            i=0
            #print ac
            for a in ac:

                self.addrow(self.tableWidget_accounttarif, a.id, i,0)
                self.addrow(self.tableWidget_accounttarif, a.tarif_name, i,1)
                self.addrow(self.tableWidget_accounttarif, a.datetime.strftime(strftimeFormat), i,2)
                i+=1

            self.tableWidget_accounttarif.setColumnHidden(0, True)
            self.connection.commit()
    
    def editAccountInfo(self, item):
        if item.column()==1:
            self.tableWidget.editItem(item)
            
    def suspendedPeriodRefresh(self):
        if self.model:
            sp = self.connection.get_models("billservice_suspendedperiod", where={'account_id':self.model.id})
            self.connection.commit()
            self.tableWidget_suspended.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_suspended, a.id, i, 0)
                self.addrow(self.tableWidget_suspended, a.start_date.strftime(strftimeFormat), i, 1)
                try:
                    self.addrow(self.tableWidget_suspended, a.end_date.strftime(strftimeFormat), i, 2)
                except:
                    self.addrow(self.tableWidget_suspended, u"Не закончен", i, 2)
                i+=1
            self.tableWidget_suspended.setColumnHidden(0, True)
      
      
    def accountAddonServiceRefresh(self):
        if self.model:
            sp = self.connection.sql("""
            SELECT accadd.*, adds.name as addonservice_name, adds.id as addonservice_id FROM billservice_accountaddonservice as accadd
            JOIN billservice_addonservice as adds ON adds.id=accadd.service_id
            WHERE account_id=%s ORDER BY id DESC
            """ % self.model.id)
            self.connection.commit()
            self.tableWidget_addonservice.clearContents()
            self.tableWidget_addonservice.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_addonservice, a.id, i, 0)
                self.addrow(self.tableWidget_addonservice, a.addonservice_name, i, 1)
                self.addrow(self.tableWidget_addonservice, a.activated.strftime(strftimeFormat), i, 2)
                try:
                    self.addrow(self.tableWidget_addonservice, a.deactivated.strftime(strftimeFormat), i, 3)
                except:
                    self.addrow(self.tableWidget_addonservice, u"Не закончен", i, 3)
                self.addrow(self.tableWidget_addonservice, a.action_status, i, 4)
                try:
                    self.addrow(self.tableWidget_addonservice, a.temporary_blocked.strftime(strftimeFormat), i, 5)
                except:
                    pass
                i+=1
            self.tableWidget_addonservice.setColumnHidden(0, True)
            self.tableWidget_addonservice.resizeColumnsToContents()
                  
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

    def add_action(self):
        if self.tabWidget.currentIndex()==3:
            self.add_accounttarif()
        elif self.tabWidget.currentIndex()==2:
            self.add_suspendedperiod()
        elif self.tabWidget.currentIndex()==4:
            self.addAddonService()
    
    def del_action(self):
        if self.tabWidget.currentIndex()==3:
            self.del_accounttarif()
        elif self.tabWidget.currentIndex()==2:
            self.del_suspendedperiod()
                
    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        child = AccountAddonServiceEdit(connection=self.connection, account_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        try:
            model = self.connection.get_model(i, "billservice_accountaddonservice")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountAddonServiceEdit(connection=self.connection, model=model, account_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def del_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)
        try:
            model = self.connection.get_model(i, "billservice_accounttarif")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        
        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_accounttarif")
            self.accountTarifRefresh()

    def add_suspendedperiod(self):
        child=SuspendedPeriodForm()

        if child.exec_()==1:
            model = Object()
            model.account_id = self.model.id
            model.start_date = child.start_date
            model.end_date = child.end_date
            self.connection.save(model, "billservice_suspendedperiod")
            self.connection.commit()
            self.suspendedPeriodRefresh()

    def del_suspendedperiod(self):
        i=self.getSelectedId(self.tableWidget_suspended)
        ###

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_suspendedperiod")
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


class AccountsMdiEbs(ebsTable_n_TreeWindow):
    def __init__(self, connection, parent, selected_account=None):
        columns=[u'#', u'Имя пользователя', u'Баланс', u'Кредит', u'Имя', u'E-mail', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u"MAC адрес", u'', u"Дата создания"]
        initargs = {"setname":"account_frame", "objname":"AccountEbsMDI", "winsize":(0,0,1100,600), "wintitle":"Пользователи", "tablecolumns":columns, "spltsize":(0,0,391,411), "treeheader":"Тарифы", "tbiconsize":(18,18)}
        self.parent = parent
        self.selected_account = selected_account
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
        self.menu = QtGui.QMenu(self.tb)
        
        
        #self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.refreshTree)

        actList=[("addAction", "Добавить аккаунт", "images/add.png", self.addframe), \
                 ("delAction", "Удалить аккаунт", "images/del.png", self.delete), \
                 ("addTarifAction", "Добавить тариф", "images/folder_add.png", self.addTarif), \
                 ("delTarifAction", "Удалить тариф", "images/folder_delete.png", self.delTarif), \
                 ("transactionAction", "Пополнить счёт", "images/pay.png", self.makeTransation), \
                 ("transactionReportAction", "История платежей", "images/moneybook.png", self.transactionReport), \
                 ("actionEnableSession", "Включить на сервере доступа", "images/add.png", self.accountEnable), \
                 ("actionDisableSession", "Отключить на сервере доступа", "images/del.png", self.accountDisable), \
                 ("actionAddAccount", "Добавить на сервер доступа", "images/add.png", self.accountAdd), \
                 ("actionDeleteAccount", "Удалить с сервера доступа", "images/del.png", self.accountDelete), \
                 ("editTarifAction", "Редактировать", "images/edit.png", self.editTarif),\
                 ("editAccountAction", "Редактировать", "images/configure.png", self.editframe),\
                 ("connectionAgreementAction", "Договор на подключение", "", self.pass_),\
                 ("actionChangeTarif", "Сменить тарифный план", "", self.changeTariff),\
                 ("actionSetSuspendedPeriod", "Отключить списание периодических услуг", "", self.suspended_period),\
                 ("actionLimitInfo", "Остаток трафика по лимитам", "", self.limit_info),\
                 ("actionPrepaidTrafficInfo", "Остаток предоплаченного трафика", "", self.prepaidtraffic_info),\
                 ("actionRadiusAttrs", "Дополнительные RADIUS атрибуты", "images/configure.png", self.radius_attrs),\
                ]



        objDict = {self.treeWidget :["editTarifAction", "addTarifAction", "delTarifAction"], \
                   self.tableWidget:["editAccountAction", "addAction", "delAction", "transactionAction", "actionEnableSession", "actionDisableSession", "actionAddAccount", "actionDeleteAccount"], \
                   self.toolBar    :["addTarifAction", "delTarifAction", "separator", "actionRadiusAttrs", "addAction", "delAction", "separator", "transactionAction", "transactionReportAction"],\
                   self.menu       :["connectionAgreementAction", "separator", "actionChangeTarif", "separator", "actionSetSuspendedPeriod", "separator", "actionLimitInfo", "separator", "actionPrepaidTrafficInfo"],\
                  }
        self.actionCreator(actList, objDict)
        
    def ebsPostInit(self, initargs):
        
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.tb.setMenu(self.menu)
        #self.tb.setDisabled(True)
        self.toolBar.addWidget(self.tb)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.editRow = self.editTarif
        #self.connectTree()
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        self.restoreWindow()
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #
        self.treeWidget.setAcceptDrops(True)
        self.treeWidget.setDragEnabled(True)
        self.treeWidget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        
    def retranslateUI(self, initargs):
        super(AccountsMdiEbs, self).retranslateUI(initargs)
        self.tableWidget.setColumnHidden(0, False)
        
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

        ids = self.get_selected_accounts()
        child=AddAccountTarif(connection=self.connection, account=None, get_info = True)
        if child.exec_()==1:
            tarif_id = child.tarif_edit.itemData(child.tarif_edit.currentIndex()).toInt()[0]
            date = child.date_edit.dateTime().toPyDateTime()
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
                self.connection.accountActions(id, 'delete')
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
        WHERE tarif.id=%s""" % self.getTarifId()).ipn_for_vpn
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
                                
        if not enabled:
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
        self.tableWidget.setSortingEnabled(False)
        self.statusBar().showMessage(u"Ожидание ответа")
        self.treeWidget.dropEvent=self.treeWidgetDropEvent


        
        #print item
        if item:
            id=item.id
        else:
            try:
                id=self.getTarifId()
            except:
                return

        accounts = self.connection.get_accounts_for_tarif(self.getTarifId())
        #print self.getTarifId()
        self.connection.commit()
        #self.connection.commit()
        #print accounts

        #print "after acc"
        self.tableWidget.setRowCount(len(accounts))
        
        m_ballance = 0
        
        i=0
        for a in accounts:            
            self.addrow(a.id, i,0, id=a.id, enabled=a.status, ctext=str(i+1), setdata=True)
            self.addrow(a.username, i,1, enabled=a.status)
            #self.addrow("%.2f" % a.ballance, i,2, color="red", enabled=a.status)
            self.addrow("%.02f" % float(a.ballance), i,2, color="red", enabled=a.status)
            self.addrow(float(a.credit), i,3, enabled=a.status)
            self.addrow(a.fullname, i,4, enabled=a.status)
            self.addrow(a.email, i,5, enabled=a.status)
            self.addrow(a.nas_name,i,6, enabled=a.status)
            self.addrow(a.vpn_ip_address, i,7, enabled=a.status)
            self.addrow(a.ipn_ip_address, i,8, enabled=a.status)
            self.addrow(a.ipn_mac_address, i,9, enabled=a.status)
            #self.addrow(a.suspended, i,10, enabled=a.status)
            #self.addrow(a.balance_blocked, i,11, enabled=a.status)
            self.tableWidget.setCellWidget(i,10,tableImageWidget(balance_blocked=a.balance_blocked, trafic_limit=a.disabled_by_limit, ipn_status=a.ipn_status, ipn_added=a.ipn_added))
            #self.addrow(a.disabled_by_limit,i,12, enabled=a.status)
            self.addrow(a.created.strftime(self.strftimeFormat), i,11, enabled=a.status)
            #self.addrow(a.created, i,11, enabled=a.status)
            m_ballance += float(a.ballance)
            #self.tableWidget.setRowHeight(i, 17)
            
            if self.selected_account:
                if self.selected_account.id == a.id:
                    self.tableWidget.setRangeSelected(QtGui.QTableWidgetSelectionRange(i,0,i,12), True)
            i+=1
            
        self.statusBar().showMessage(u'Учётных записей:%s. Средний баланс: %s' % (len(accounts), m_ballance/(1 if len(accounts)==0 else len(accounts))))
        self.tableWidget.setColumnHidden(0, False)
        #HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.delNodeLocalAction()
        #self.tablewidget.setShowGrid(False)
        self.tableWidget.setSortingEnabled(True)
        

    def accountEnable(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, 'enable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        


    def accountAdd(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, 'create'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        
    def accountDelete(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, 'delete'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()

    def accountDisable(self):
        ids = self.get_selected_accounts()
        if not ids:return
        
        for id in ids:
            if not self.connection.accountActions(id, 'disable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        self.refresh()
        
    
    def addNodeLocalAction(self):
        super(AccountsMdiEbs, self).addNodeLocalAction([self.addAction,self.delTarifAction])
        
    def delNodeLocalAction(self):
        super(AccountsMdiEbs, self).delNodeLocalAction([self.delAction,self.transactionAction,self.transactionReportAction])
        
