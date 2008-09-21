#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui

import Pyro.core
import traceback
from helpers import Object as Object
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil
from types import BooleanType
import copy

#from django.contrib.auth.models import User

#from billservice.models import Account, AccountTarif,  Transaction, TransactionType,   Tariff, AccountTarif, SettlementPeriod, TimePeriod, AccessParameters, TimeSpeed, TimeAccessService, TimeAccessNode, OneTimeService, PeriodicalService, TrafficLimit, TrafficTransmitService, TrafficTransmitNodes, PrepaidTraffic
#from nas.models import IPAddressPool, Nas, TrafficClass
#from django.db import transaction
from randgen import nameGen, GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import CheckBoxDialog, ComboBoxDialog, SpeedEditDialog , TransactionForm

from Reports import TransactionsReport

from helpers import tableFormat

from helpers import transaction, makeHeaders

class CashType(object):
    def __init__(self, name):
        self.name=name
        
cash_types = [CashType("AT_START"), CashType("AT_END"), CashType("GRADUAL")]

class CustomWidget(QtGui.QTableWidgetItem):
    def __init__(self, parent, models, *args, **kwargs):
        super(CustomWidget, self).__init__()
        self.models=models
        label=""
        for model in models:
            label += "%s \n" % model.name
        
        self.setText(label[0:-2])
        

class AddAccountTarif(QtGui.QDialog):
    def __init__(self, connection,ttype, account=None, model=None):
        super(AddAccountTarif, self).__init__()
        self.model=model
        self.ttype = ttype
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
        self.gridlayout.addWidget(self.date_edit,1,1,1,1)


        self.retranslateUi()
        self.fixtures()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)

    def accept(self):
        tarif=self.connection.get("SELECT * FROM billservice_tariff WHERE id=%d" % self.tarif_edit.itemData(self.tarif_edit.currentIndex()).toInt()[0])
        date=self.date_edit.dateTime().toPyDateTime()
        if self.model:
            model=self.model
            model.datetime = date
        else:
            model = Object()
            model.account_id = self.account.id
            model.tarif_id =tarif.id 
            model.datetime = date
            
            #AccountTarif.objects.create(account=self.account, tarif=tarif, datetime=date)
        try:
            self.connection.create(model.save("billservice_accounttarif"))
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
        tarifs=self.connection.sql("SELECT id, name FROM billservice_tariff WHERE (active=TRUE) AND (get_tariff_type(id)='%s');" % self.ttype)
        for tarif in tarifs:
            self.tarif_edit.addItem(tarif.name, QtCore.QVariant(tarif.id))
        now=datetime.datetime.now()
        print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            self.tarif_edit.setCurrentIndex(self.tarif_edit.findData(self.model.tarif_id))

            now = QtCore.QDateTime()

            now.setTime_t((mktime(self.model.datetime.timetuple())))
        self.date_edit.setDateTime(now)

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

        self.tarif_description_edit = QtGui.QTextEdit(self.tab_1)
        self.tarif_description_edit.setGeometry(QtCore.QRect(11,350,597,142))
        self.tarif_description_edit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.NoTextInteraction|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.tarif_description_edit.setObjectName("tarif_description_edit")

        self.tarif_description_label = QtGui.QLabel(self.tab_1)
        self.tarif_description_label.setGeometry(QtCore.QRect(10,320,198,16))
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

        self.tarif_cost_edit = QtGui.QLineEdit(self.sp_groupbox)
        self.tarif_cost_edit.setGeometry(QtCore.QRect(139,80,241,21))
        self.tarif_cost_edit.setObjectName("tarif_cost_edit")
        self.tarif_cost_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9]+)([\.]?)([0-9]+)"), self))

        self.ps_null_ballance_checkout_edit = QtGui.QCheckBox(self.tab_1)
        self.ps_null_ballance_checkout_edit.setGeometry(QtCore.QRect(10,230,451,30))
        self.ps_null_ballance_checkout_edit.setObjectName("ps_null_ballance_checkout_edit")

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
        self.components_groupBox.setGeometry(QtCore.QRect(420,60,184,159))
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
        self.limit_tableWidget = tableFormat(self.limit_tableWidget)
        self.periodical_tableWidget = tableFormat(self.periodical_tableWidget)
        self.onetime_tableWidget = tableFormat(self.onetime_tableWidget)
        self.prepaid_tableWidget = tableFormat(self.prepaid_tableWidget)
        self.trafficcost_tableWidget = tableFormat(self.trafficcost_tableWidget)
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
        
        QtCore.QObject.connect(self.sp_type_edit, QtCore.SIGNAL("stateChanged(int)"), self.filterSettlementPeriods)
        
        QtCore.QObject.connect(self.transmit_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.transmitTabActivityActions)
        
        QtCore.QObject.connect(self.time_access_service_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.timeaccessTabActivityActions)
        
        QtCore.QObject.connect(self.onetime_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.onetimeTabActivityActions)
        
        QtCore.QObject.connect(self.periodical_services_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.periodicalServicesTabActivityActions)
        
        QtCore.QObject.connect(self.limites_checkbox, QtCore.SIGNAL("stateChanged(int)"), self.limitTabActivityActions)

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
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("Dialog", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("Dialog", "Фиксированный расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_type_edit.setText(QtGui.QApplication.translate("Dialog", "Начать при активации у пользователя данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("Dialog", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("Dialog", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.ps_null_ballance_checkout_edit.setText(QtGui.QApplication.translate("Dialog", "Производить снятие денег при нулевом баллансе пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setText(QtGui.QApplication.translate("Dialog", "Способ доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setText(QtGui.QApplication.translate("Dialog", "Время доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.components_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Набор компонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.transmit_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_for_vpn.setText(QtGui.QApplication.translate("Dialog", "Производить IPN действия", None, QtGui.QApplication.UnicodeUTF8))
        self.time_access_service_checkbox.setText(QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_services_checkbox.setText(QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limites_checkbox.setText(QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_access_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Настройки скорости по-умолчанию", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_label.setText(QtGui.QApplication.translate("Dialog", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_priority_label.setText(QtGui.QApplication.translate("Dialog", "Приоритет", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_time_label.setText(QtGui.QApplication.translate("Dialog", "Burst Time", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_burst_treshold_label.setText(QtGui.QApplication.translate("Dialog", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("Dialog", "OUT", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("Dialog", "IN", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_max_label.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_min_label.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        
        self.speed_table.clear()
        columns=[u'Id',u'Время', u'Макс', u'Гарант.', u'Пик', u'Средняя для пика', u'Время для пика', u'Приоритет']
        
        makeHeaders(columns, self.speed_table) 
        
        self.del_speed_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_speed_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_time_label.setText(QtGui.QApplication.translate("Dialog", "Предоплачено, с", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_time_checkbox.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце расчётного периода предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.clear()

        columns=[u'Id', u'Время', u'Цена']
        
        makeHeaders(columns, self.timeaccess_table)     
        
        self.del_timecost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_timecost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_traffic_edit.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце периода предоплаченый трафик", None, QtGui.QApplication.UnicodeUTF8))
        
        self.trafficcost_tableWidget.clear()
        columns=[u'Id', u'От МБ', u'До МБ', u'Направления', u'Вх', u'Исх', u'Время', u'Цена']
        
        makeHeaders(columns, self.trafficcost_tableWidget)      

        self.trafficcost_label.setText(QtGui.QApplication.translate("Dialog", "Цена за МБ трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.del_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        
        self.prepaid_tableWidget.clear()
        columns=[u'Id', u'Направления', u'Вх', u'Исх',  u'МБ']
        
        makeHeaders(columns, self.prepaid_tableWidget)                
                
        self.prepaid_traffic_cost_label.setText(QtGui.QApplication.translate("Dialog", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.del_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("Dialog", "Оплата за трафик", None, QtGui.QApplication.UnicodeUTF8))
        
        self.onetime_tableWidget.clear()

        columns=[u'Id', u'Название', u'Стоимость']
        
        makeHeaders(columns, self.onetime_tableWidget)
        
        self.del_onetime_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_onetime_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        
        self.periodical_tableWidget.clear()
        columns=[u'Id', u'Название', u'Период', u'Способ снятия', u'Стоимость']
        
        makeHeaders(columns, self.periodical_tableWidget)
        
        self.del_periodical_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_periodical_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.clear()

        columns=[u'Id', u'Название', u'За поледний', u'Период', u'Направления', u'Вх', u'Исх', u'МБ']
        
        makeHeaders(columns, self.limit_tableWidget)
        
        self.del_limit_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_limit_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        
        
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
            
    def addrow(self, widget, value, x, y, item_type=None):
        if value==None:
            value=''
            
        if not item_type:
            item = QtGui.QTableWidgetItem()
            item.setText(unicode(value))               
            widget.setItem(x, y, item)
            
        if item_type=='checkbox':
            item = QtGui.QCheckBox()

            item.setCheckState(value == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            widget.setCellWidget(x,y, item)

            

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
        self.addrow(self.trafficcost_tableWidget, True, current_row, 4, item_type='checkbox')
        self.addrow(self.trafficcost_tableWidget, True, current_row, 5, item_type='checkbox')
        #self.addrow(self.trafficcost_tableWidget, True, current_row, 6, item_type='checkbox')
        
    
    def delTrafficCostRow(self):
        current_row = self.trafficcost_tableWidget.currentRow()
        
        id = self.getIdFromtable(self.trafficcost_tableWidget, current_row)
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=%d" % id)
            self.connection.delete("DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=%d" % id)
            self.connection.delete("DELETE FROM billservice_traffictransmitnodes WHERE id=%d" % id)
        self.trafficcost_tableWidget.removeRow(current_row)
        
        
    def addLimitRow(self):
        current_row = self.limit_tableWidget.rowCount()
        self.limit_tableWidget.insertRow(current_row)
        self.addrow(self.limit_tableWidget, True, current_row, 2, item_type='checkbox')

        self.addrow(self.limit_tableWidget, True, current_row, 5, item_type='checkbox')
        self.addrow(self.limit_tableWidget, True, current_row, 6, item_type='checkbox')
        #self.addrow(self.limit_tableWidget, True, current_row, 7, item_type='checkbox')

    
    def delLimitRow(self):
        current_row = self.limit_tableWidget.currentRow()
        id = self.getIdFromtable(self.limit_tableWidget, current_row)
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_trafficlimit_traffic_class WHERE trafficlimit_id=%d" % id )
            self.connection.delete("DELETE FROM billservice_tariff_traffic_limit WHERE trafficlimit_id=%d" % id)
            self.connection.delete("DELETE FROM billservice_trafficlimit WHERE id=%d" % id)
        self.limit_tableWidget.removeRow(current_row)

    def addOneTimeRow(self):
        current_row = self.onetime_tableWidget.rowCount()
        self.onetime_tableWidget.insertRow(current_row)
    
    def delOneTimeRow(self):
        current_row = self.onetime_tableWidget.currentRow()     
        id = self.getIdFromtable(self.onetime_tableWidget, current_row)
        
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_tariff_onetime_services WHERE onetimeservice_id=%d and tariff_id=%d" % (id, self.model.id))
            self.connection.delete("DELETE FROM billservice_onetimeservice WHERE id=%d" % id)

        self.onetime_tableWidget.removeRow(current_row)

    def addTimeAccessRow(self):
        current_row = self.timeaccess_table.rowCount()
        self.timeaccess_table.insertRow(current_row)
    
    def delTimeAccessRow(self):
        current_row = self.timeaccess_table.currentRow()   
        id = self.getIdFromtable(self.timeaccess_table, current_row)
        
        if id!=-1:
            
            self.connection.delete("DELETE FROM billservice_timeaccessnode WHERE id=%d" % id)
            #TimeAccessNode.objects.get(id=id).delete()
    
        self.timeaccess_table.removeRow(current_row)

    def addPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.rowCount()
        self.prepaid_tableWidget.insertRow(current_row)
        
        self.addrow(self.prepaid_tableWidget, True, current_row, 2, item_type='checkbox')
        self.addrow(self.prepaid_tableWidget, True, current_row, 3, item_type='checkbox')
        #self.addrow(self.prepaid_tableWidget, True, current_row, 4, item_type='checkbox')
    
    def delPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.currentRow()  
        id = self.getIdFromtable(self.prepaid_tableWidget, current_row)
        
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_prepaidtraffic_traffic_class WHERE prepaidtraffic_id=%d" % id)
            self.connection.delete("DELETE FROM billservice_prepaidtraffic WHERE id=%d" % id)
            #PrepaidTraffic.objects.get(id=id).delete()
     
        self.prepaid_tableWidget.removeRow(current_row)

    def addSpeedRow(self):
        current_row = self.speed_table.rowCount()
        self.speed_table.insertRow(current_row)
    
    def delSpeedRow(self):
        current_row = self.speed_table.currentRow()
        id = self.getIdFromtable(self.speed_table, current_row)
        
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_timespeed WHERE id=%d" % id)
            #service.delete()    
        self.speed_table.removeRow(current_row)

                
    def addPeriodicalRow(self):
        self.periodical_tableWidget.insertRow(self.periodical_tableWidget.rowCount())
    
    def delPeriodicalRow(self):
        current_row = self.periodical_tableWidget.currentRow()
        id = self.getIdFromtable(self.periodical_tableWidget, current_row)
        
        if id!=-1:
            self.connection.delete("DELETE FROM billservice_tariff_periodical_services WHERE periodicalservice_id=%d" % id)
            self.connection.delete("DELETE FROM billservice_periodicalservice WHERE id=%d" % id)
            #service.tariff_set.remove(self.model)
            #service.delete()    
        self.periodical_tableWidget.removeRow(current_row)
        
    #-----------------------------
    def onAccessTypeChange(self, *args):
        if args[0] == "IPN":
            if self.ipn_for_vpn.isEnabled():
                self.ipn_for_vpn_state = self.ipn_for_vpn.checkState()
                self.ipn_for_vpn.setChecked(True)
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



#-----------------------------Обработка редактирования таблиц
    def prepaidTrafficEdit(self,y,x):
        if x==1:
            try:
                models = self.prepaid_tableWidget.item(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=self.connection.sql("SELECT * FROM nas_trafficclass ORDER BY name ASC"), selected_items = models)
            if child.exec_()==1:
                self.prepaid_tableWidget.setItem(y,x, CustomWidget(parent=self.prepaid_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    #self.prepaid_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.prepaid_tableWidget.resizeColumnsToContents()
                    self.prepaid_tableWidget.resizeRowsToContents()
        
        if x==4:
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
                
            child = ComboBoxDialog(items=self.connection.sql("SELECT * FROM billservice_timeperiod ORDER BY name ASC"), selected_item = default_text )
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
            
            text = QtGui.QInputDialog.getInteger(self, u"Приоритет", u"Введите приоритет от 1 до 8", default_text)        
           
            self.speed_table.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))


    def limitClassEdit(self,y,x):
        if x==4:
            try:
                models = self.limit_tableWidget.item(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=self.connection.sql("SELECT * FROM nas_trafficclass ORDER BY name ASC"), selected_items = models)
            if child.exec_()==1:
                self.limit_tableWidget.setItem(y,x, CustomWidget(parent=self.limit_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    #self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    self.limit_tableWidget.resizeColumnsToContents()
                    self.limit_tableWidget.resizeRowsToContents()
                    
        if x==3:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=self.connection.sql("SELECT * FROM billservice_settlementperiod ORDER BY name ASC"), selected_item = default_text )
            if child.exec_()==1:
                self.limit_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))

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
             
        if x==7:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getInteger(self, u"Размер:", u"Введите размер лимита в МБ, после которого произойдёт отключение", default_text)        
           
            self.limit_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))
                
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
            child = ComboBoxDialog(items=self.connection.sql("SELECT * FROM billservice_timeperiod ORDER BY name ASC"), selected_item = default_text )
            if child.exec_()==1:
                self.timeaccess_table.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))    

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

        if x==3:
            try:
                models = self.trafficcost_tableWidget.item(y,x).models
            except Exception, e:
                print e
                models = []
            #print models
            child = CheckBoxDialog(all_items=self.connection.sql("SELECT * FROM nas_trafficclass"), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setItem(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                self.trafficcost_tableWidget.resizeColumnsToContents()
                self.trafficcost_tableWidget.resizeRowsToContents()
                    
                
        if x==6:
            try:
                models = self.trafficcost_tableWidget.item(y,x).models
            except:
                models = []
            child = CheckBoxDialog(all_items=self.connection.sql("SELECT * FROM billservice_timeperiod ORDER BY name ASC"), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setItem(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                self.trafficcost_tableWidget.resizeColumnsToContents()
                self.trafficcost_tableWidget.resizeRowsToContents()

        if x==7:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Цена за МБ:", u"Введите цену", default_text)        
           
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
                
            child = ComboBoxDialog(items=self.connection.sql("SELECT * FROM billservice_settlementperiod ORDER BY name ASC"), selected_item = default_text )
            if child.exec_()==1:
                self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))

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
                self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(child.comboBox.currentText()))
             
        if x==4:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QtGui.QInputDialog.getDouble(self, u"Цена:", u"Введите цену", default_text)        
           
            self.periodical_tableWidget.setItem(y,x, QtGui.QTableWidgetItem(unicode(text[0])))


#----------------------------

    def getIdFromtable(self, tablewidget, row=0):
        tmp=tablewidget.item(row, 0)
        if tmp is not None:
            return int(tmp.text())
        return -1
        
    
    def fixtures(self):
        
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                #print "self.model.settlement_period_id", self.model.settlement_period_id
                settlement_period=self.connection.get("""SELECT * FROM billservice_settlementperiod WHERE id =%s""" % self.model.settlement_period_id)
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




        access_types = ["PPTP", "PPPOE", "IPN"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = self.connection.sql("SELECT * FROM billservice_timeperiod ORDER BY name ASC")
        
        for at in access_time:
            self.access_time_edit.addItem(unicode(at.name))


        
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                self.sp_name_edit.setCurrentIndex(self.sp_name_edit.findText(settlement_period.name, QtCore.Qt.MatchCaseSensitive))
                
            self.tarif_status_edit.setCheckState(self.model.active == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.tarif_name_edit.setText(self.model.name)
            self.tarif_cost_edit.setText(unicode(self.model.cost))
            self.tarif_description_edit.setText(self.model.description)
            self.reset_tarif_cost_edit.setCheckState(self.model.reset_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.ps_null_ballance_checkout_edit.setCheckState(self.model.ps_null_ballance_checkout == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            access_parameters = self.connection.get("SELECT * FROM billservice_accessparameters WHERE id=%d" % self.model.access_parameters_id)
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
                time_access_service = self.connection.get("SELECT * FROM billservice_timeaccessservice WHERE id=%d" % self.model.time_access_service_id)
                self.prepaid_time_edit.setValue(time_access_service.prepaid_time)
                self.reset_time_checkbox.setCheckState(time_access_service.reset_time == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                #nodes = self.model.time_access_service.time_access_nodes.all()
                nodes = self.connection.sql("""SELECT timeaccessnode.*, timeperiod.name as time_period_name FROM billservice_timeaccessnode as timeaccessnode  
                JOIN billservice_timeperiod as timeperiod ON timeperiod.id=timeaccessnode.time_period_id
                WHERE timeaccessnode.time_access_service_id=%d""" % self.model.time_access_service_id)
                self.timeaccess_table.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.timeaccess_table, node.id,i, 0)
                    self.addrow(self.timeaccess_table, node.time_period_name,i, 1)
                    self.addrow(self.timeaccess_table, node.cost,i, 2)
                    i+=1                
            self.timeaccess_table.setColumnHidden(0, True)
            
            #PeriodicalService
            periodical_services = self.connection.sql("""SELECT periodicalservice.*, settlementperiod.name as settlement_period_name
            FROM billservice_periodicalservice as periodicalservice
            JOIN billservice_tariff_periodical_services as tps ON tps.periodicalservice_id=periodicalservice.id
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id = periodicalservice.settlement_period_id
            WHERE tps.tariff_id = %d   
            """ % self.model.id)
            if len(periodical_services)>0:
                self.periodical_services_checkbox.setChecked(True)
                nodes = periodical_services
                self.periodical_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    self.addrow(self.periodical_tableWidget, node.id,i, 0)
                    self.addrow(self.periodical_tableWidget, node.name,i, 1)
                    self.addrow(self.periodical_tableWidget, node.settlement_period_name,i, 2)
                    self.addrow(self.periodical_tableWidget, node.cash_method, i, 3)
                    self.addrow(self.periodical_tableWidget, node.cost,i, 4)
                    i+=1                   
            self.periodical_tableWidget.setColumnHidden(0, True)
            
            #Onetime Service
            onetime_services = self.connection.sql("""SELECT onetimeservice.* FROM billservice_onetimeservice as onetimeservice
            JOIN billservice_tariff_onetime_services as ots ON ots.onetimeservice_id=onetimeservice.id
            WHERE ots.tariff_id=%d
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
            traffic_limites = self.connection.sql(""" SELECT trafficlimit.*, settlementperiod.name as settlement_period_name FROM billservice_trafficlimit as trafficlimit
            JOIN billservice_tariff_traffic_limit as ttl ON ttl.trafficlimit_id= trafficlimit.id
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id=trafficlimit.settlement_period_id
            WHERE ttl.tariff_id=%d
            """ % self.model.id)
             
            
            if len(traffic_limites)>0:

                self.limites_checkbox.setChecked(True)
                nodes = traffic_limites
                self.limit_tableWidget.setRowCount(len(nodes))
                i=0
                for node in nodes:
                    traffic_classes = self.connection.sql(""" 
                    SELECT trafficclass.* FROM nas_trafficclass as trafficclass
                    JOIN billservice_trafficlimit_traffic_class as ttc ON ttc.trafficclass_id=trafficclass.id
                    WHERE ttc.trafficlimit_id=%d
                    """ % node.id)
                
                    self.addrow(self.limit_tableWidget, node.id,i, 0)
                    self.addrow(self.limit_tableWidget, node.name,i, 1)
                    self.addrow(self.limit_tableWidget, node.mode,i, 2, item_type='checkbox')
                    self.addrow(self.limit_tableWidget, node.settlement_period_name,i, 3)
                    self.limit_tableWidget.setItem(i,4, CustomWidget(parent=self.limit_tableWidget, models=traffic_classes))
                    self.addrow(self.limit_tableWidget, unicode(int(unicode(node.size))/(1024*1024)),i, 7)
                    
                    self.addrow(self.limit_tableWidget, node.in_direction, i, 5, item_type='checkbox')
                    self.addrow(self.limit_tableWidget, node.out_direction, i, 6, item_type='checkbox')
                    #self.addrow(self.limit_tableWidget, node.transit_direction, i, 7, item_type='checkbox')                    
                    
                    i+=1
                    self.limit_tableWidget.resizeColumnsToContents()
                    self.limit_tableWidget.resizeRowsToContents()
            self.limit_tableWidget.setColumnHidden(0, True)
            
            #print "self.model.traffic_transmit_service_id=", self.model.traffic_transmit_service_id 
            #Prepaid Traffic
            if not self.model.isnull('traffic_transmit_service_id'):
                self.transmit_service_checkbox.setChecked(True)
                prepaid_traffic = self.connection.sql("""SELECT * FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=%d""" % self.model.traffic_transmit_service_id)
                #print 'self.model.traffic_transmit_service_id', self.model.traffic_transmit_service_id
                if len(prepaid_traffic)>0:
                    nodes = prepaid_traffic
                    #self.model.traffic_transmit_service.prepaid_traffic.all()
                    #print nodes
                    self.prepaid_tableWidget.setRowCount(len(nodes))
                    i=0
                    for node in nodes:
                        traffic_classes = self.connection.sql(""" 
                        SELECT trafficclass.* FROM nas_trafficclass as trafficclass
                        JOIN billservice_prepaidtraffic_traffic_class as ttc ON ttc.trafficclass_id=trafficclass.id
                        WHERE ttc.prepaidtraffic_id=%d
                        """ % node.id)
              
                        self.addrow(self.prepaid_tableWidget, node.id,i, 0)
                        self.prepaid_tableWidget.setItem(i,1, CustomWidget(parent=self.prepaid_tableWidget, models=traffic_classes))

                        self.addrow(self.prepaid_tableWidget, node.in_direction, i, 2, item_type='checkbox')
                        self.addrow(self.prepaid_tableWidget, node.out_direction, i, 3, item_type='checkbox')
                        #self.addrow(self.prepaid_tableWidget, node.transit_direction, i, 4, item_type='checkbox')
                        
                        self.addrow(self.prepaid_tableWidget, float(node.size)/(1024*1024),i, 4)
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
                    traffic_transmit_service = self.connection.get("SELECT * FROM billservice_traffictransmitservice WHERE id=%d" % self.model.traffic_transmit_service_id)
                    self.reset_traffic_edit.setCheckState(traffic_transmit_service.reset_traffic == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                    nodes = traffic_transmit_nodes
                    self.trafficcost_tableWidget.setRowCount(len(nodes))
                    i = 0
                    for node in nodes:
                        traffic_classes = self.connection.sql(""" 
                        SELECT trafficclass.* FROM nas_trafficclass as trafficclass
                        JOIN billservice_traffictransmitnodes_traffic_class as ttc ON ttc.trafficclass_id=trafficclass.id
                        WHERE ttc.traffictransmitnodes_id=%d
                        """ % node.id)           
              
                        
                        
                        time_nodes = self.connection.sql(""" 
                        SELECT timeperiod.* FROM billservice_timeperiod as timeperiod
                        JOIN billservice_traffictransmitnodes_time_nodes as tn ON tn.timeperiod_id=timeperiod.id
                        WHERE tn.traffictransmitnodes_id=%d  
                        """ % node.id)
                        
                        #print node.id
                        self.addrow(self.trafficcost_tableWidget, node.id, i, 0)
                        self.addrow(self.trafficcost_tableWidget, node.edge_start, i, 1)
                        self.addrow(self.trafficcost_tableWidget, node.edge_end, i, 2)
                        self.trafficcost_tableWidget.setItem(i,3, CustomWidget(parent=self.trafficcost_tableWidget, models=traffic_classes))
                        self.addrow(self.trafficcost_tableWidget, node.in_direction, i, 4, item_type='checkbox')
                        self.addrow(self.trafficcost_tableWidget, node.out_direction, i, 5, item_type='checkbox')
                        #self.addrow(self.trafficcost_tableWidget, node.transit_direction, i, 6, item_type='checkbox')
                        self.trafficcost_tableWidget.setItem(i,6, CustomWidget(parent=self.trafficcost_tableWidget, models=time_nodes))
                        self.addrow(self.trafficcost_tableWidget, node.cost, i, 7)
                        i+=1
                    self.trafficcost_tableWidget.resizeRowsToContents()
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                    self.trafficcost_tableWidget.setColumnHidden(0, True)
            if access_parameters.access_type == 'IPN':
                self.access_type_edit.setDisabled(True)
                self.ipn_for_vpn.setDisabled(True)
            else:
                self.access_type_edit.removeItem(2)
            self.access_type_edit.setCurrentIndex(self.access_type_edit.findText(access_parameters.access_type, QtCore.Qt.MatchCaseSensitive))
            self.access_time_edit.setCurrentIndex(self.access_time_edit.findText(access_parameters.time_name, QtCore.Qt.MatchCaseSensitive))
            self.ipn_for_vpn.setChecked(access_parameters.ipn_for_vpn)
        self.timeaccessTabActivityActions()
        self.transmitTabActivityActions()
        self.onetimeTabActivityActions()
        self.periodicalServicesTabActivityActions()
        self.limitTabActivityActions()

    def get_speed(self, speed):
        
        speed_in, speed_out = speed.split("/")
        if speed_in.endswith(u"k"):
            speed_in = int(speed_in[0:-1])*1024
        elif speed_in.endswith(u"M"):
            speed_in = int(speed_in[0:-1])*1024*1024
        else:
            speed_in=int(speed_in)
        
        if speed_out.endswith(u"k"):
            speed_out = int(speed_out[0:-1])*1024
        elif speed_out.endswith(u"M"):
            speed_out = int(speed_out[0:-1])*1024*1024
        else:
            speed_out=int(speed_out)
                       
        return speed_in, speed_out
    
    def compare_speeds(self, speed1, speed2):

        speed1_in, speed1_out = self.get_speed(unicode(speed1))
        speed2_in, speed2_out = self.get_speed(unicode(speed2))
        
        if speed1_in<speed2_in:
            return False

        if speed1_out<speed2_out:
            return False        
        return True
    


            
                
          
    #@transaction.commit_manually            
    def accept(self):
        #self.connection.command("BEGIN;")
        if self.model:
            model=copy.deepcopy(self.model)
            access_parameters = Object()
            access_parameters.id=self.model.access_parameters_id
            access_parameters = self.connection.get(access_parameters.get("billservice_accessparameters"))
        else:
            model=Object()
            access_parameters = Object()
            
            if unicode(self.tarif_name_edit.text())=="":
                QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не указали название тарифного плана")
                return
            if unicode(self.access_time_edit.currentText())=="":
                QtGui.QMessageBox.warning(self, u"Ошибка", u"Вы не выбрали разрешённый период доступа")
                return
            if (unicode(self.access_time_edit.currentText()) == 'IPN') and self.ipn_for_vpn.checkState()==2:
                QtGui.QMessageBox.warning(self, u"Ошибка", u"'Производить IPN действия' может быть указано только для VPN планов")
                return
        try:
            
            model.name = unicode(self.tarif_name_edit.text())
            
            model.description = unicode(self.tarif_description_edit.toPlainText())
            
            model.ps_null_ballance_checkout = self.ps_null_ballance_checkout_edit.checkState()==2
            
            model.active = self.tarif_status_edit.checkState()==2
            
            access_parameters.access_type = unicode(self.access_type_edit.currentText())
            access_parameters.access_time_id = self.connection.get("SELECT * FROM billservice_timeperiod WHERE name='%s'" % unicode(self.access_time_edit.currentText())).id
            access_parameters.max_limit = u"%s/%s" % (self.speed_max_in_edit.text() or 0, self.speed_max_out_edit.text() or 0)
            access_parameters.min_limit = u"%s/%s" % (self.speed_min_in_edit.text() or 0, self.speed_min_out_edit.text() or 0)
            access_parameters.burst_limit = u"%s/%s" % (self.speed_burst_in_edit.text() or 0, self.speed_burst_out_edit.text() or 0)
            access_parameters.burst_treshold = u"%s/%s" % (self.speed_burst_treshold_in_edit.text() or 0, self.speed_burst_treshold_out_edit.text() or 0)
            access_parameters.burst_time = u"%s/%s" % (self.speed_burst_time_in_edit.text() or 0, self.speed_burst_time_out_edit.text() or 0)
            access_parameters.priority = unicode(self.speed_priority_edit.text()) or 8
            access_parameters.ipn_for_vpn = self.ipn_for_vpn.checkState()==2
            access_parameters_id = self.connection.create(access_parameters.save("billservice_accessparameters"))
            
            if self.model:
                #Просто обновляем запись
                self.connection.create(access_parameters.save("billservice_accessparameters"))
            else:
                #Иначе создаём новую
                model.access_parameters_id=self.connection.create(access_parameters.save("billservice_accessparameters"))
            
            #Таблица скоростей
            
            for i in xrange(0, self.speed_table.rowCount()):
                id = self.getIdFromtable(self.speed_table, i)
                if id!=-1:
                    #Если такая запись уже есть
                    speed = self.connection.get("SELECT * FROM billservice_timespeed WHERE id=%d" % id)
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
                try:
                    if self.speed_table.item(i,3) and not self.compare_speeds(self.speed_table.item(i,2).text() or 0, self.speed_table.item(i,3).text() or 0):
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка при указании максимальной и гарантированной скорости")
                        #print 1
                        self.connection.rollback()
                        
                        return
    
                    if self.speed_table.item(i,4) and self.speed_table.item(i,5) and not self.compare_speeds(self.speed_table.item(i,4).text() or 0, self.speed_table.item(i,5).text() or 0):
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка при указании пиковой и средней скорости")
                        #print 2
                        self.connection.rollback()
                        
                        return
                except:
                    print "speed compare error"
                self.connection.create(speed.save("billservice_timespeed"))
            #model.save()
            
            #Период
            sp=unicode(self.sp_name_edit.currentText())
            if self.sp_groupbox.isChecked()==True and sp!='':
                model.settlement_period_id = self.connection.get( "SELECT * FROM billservice_settlementperiod WHERE name='%s'" % sp).id
                model.cost = unicode(self.tarif_cost_edit.text()) or 0
                model.reset_tarif_cost = self.reset_tarif_cost_edit.checkState()==2
                
            else:
                model.settlement_period_id=None
                model.reset_tarif_cost=False
                model.cost = 0

            model_id = self.connection.create(model.save("billservice_tariff"))
            if model_id==-1:
                #Если не создали новую сущность
                model_id = model.id
            else:
                model.id = model_id 

            #Доступ по времени
            if model.hasattr("time_access_service_id"):
                if not model.isnull('time_access_service_id'):
                    time_access_service = self.connection.get(" SELECT * FROM billservice_timeaccessservice WHERE id=%d" % self.model.time_access_service_id)
                else:
                    time_access_service=Object()
            else:
                time_access_service=Object()
                
            if self.time_access_service_checkbox.checkState()==2:
                if self.timeaccess_table.rowCount()>0:
                    
                    #print 1
                    time_access_service.name = ""
                    time_access_service.reset_time = self.reset_time_checkbox.checkState()==2
                    time_access_service.prepaid_time = unicode(self.prepaid_time_edit.text())
                    
                    if not model.isnull('time_access_service_id'):
                        self.connection.create(time_access_service.save("billservice_timeaccessservice"))
                        time_access_service_id = self.model.time_access_service_id
                    else:
                        model.time_access_service_id = self.connection.create(time_access_service.save("billservice_timeaccessservice"))
                        time_access_service_id = model.time_access_service_id
                    
                    for i in xrange(0, self.timeaccess_table.rowCount()):
                        #print "pre save"
                        if self.timeaccess_table.item(i,1)==None or self.timeaccess_table.item(i,2)==None:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки оплаты за время")
                            self.connection.rollback()
                            return
                        else:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"Сохранение настроек стоимости за время")
                            
                        #print "post save"
                        id = self.getIdFromtable(self.timeaccess_table, i)
                        if id!=-1:
                            time_access_node = self.connection.get("SELECT * FROM billservice_timeaccessnode WHERE id=%d" % id )
                        else:
                            time_access_node = Object()
                        
                        time_access_node.time_access_service_id=time_access_service_id
                        
                        time_access_node.time_period_id = self.connection.get("SELECT * FROM billservice_timeperiod WHERE name='%s'" % unicode(self.timeaccess_table.item(i,1).text())).id
                        time_access_node.cost = unicode(self.timeaccess_table.item(i,2).text())
                        self.connection.create(time_access_node.save("billservice_timeaccessnode"))
            
            elif self.time_access_service_checkbox.checkState()==0 and model.hasattr("time_access_service_id"):
                if  not model.isnull("time_access_service_id"):
                    #model.save()
                    self.connection.delete("DELETE FROM billservice_timeaccessnode WHERE time_access_service_id=%d" % self.model.time_access_service_id)
                    
                    time_access_service_id=model.time_access_service_id
                    model.time_access_service_id=None
                    self.connection.create(model.save("billservice_tariff"))
                    self.connection.delete("DELETE FROM billservice_timeaccessservice WHERE id=%d" % time_access_service_id)
                    
                    model.time_access_service_id = None
            
                else:
                    model.time_access_service_id = None
                    
            #Разовые услуги
            
            if self.onetime_tableWidget.rowCount()>0 and self.onetime_services_checkbox.checkState()==2:
                onetimeservices = self.connection.sql("SELECT * FROM billservice_tariff_onetime_services WHERE tariff_id=%d" % model_id)
                for i in xrange(0, self.onetime_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.onetime_tableWidget, i)
                    
                    if id!=-1:
                        onetime_service = self.connection.get("SELECT * FROM billservice_onetimeservice WHERE id=%d" % id)
                    else:
                        onetime_service = Object()
                    
                    onetime_service.name=unicode(self.onetime_tableWidget.item(i, 1).text())
                    onetime_service.cost=unicode(self.onetime_tableWidget.item(i, 2).text())
                    
                    onetime_service_id = self.connection.create(onetime_service.save("billservice_onetimeservice"))
                    
                    #Если это новая запись
                    if onetime_service_id>0:
                        self.connection.create("INSERT INTO billservice_tariff_onetime_services(tariff_id, onetimeservice_id) VALUES(%d, %d)" % (model.id, onetime_service_id))
                        #onetime_service.tariff_set.add(model)
            elif self.onetime_services_checkbox.checkState()==0:
                onetimeservices = self.connection.sql("SELECT * FROM billservice_tariff_onetime_services WHERE tariff_id=%d" % model_id)
                if len(onetimeservices)>0:
                    #сделать удаление самих сущностей
                    self.connection.delete("DELETE FROM billservice_tariff_onetime_services WHERE tarif_id=%d" % model_id)
                    for onetimeservice in onetimeservices:
                        self.connection.delete("DELETE FROM billservice_onetimeservice WHERE onetimeservice_id=%d" % onetimeservice.onetimeservice_id)
                                                   
            
            #Периодические услуги
            if self.periodical_tableWidget.rowCount()>0 and self.periodical_services_checkbox.checkState()==2:
                peridical_services = self.connection.sql("SELECT * FROM billservice_tariff_periodical_services WHERE tariff_id=%d" % model_id)
                for i in xrange(0, self.periodical_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.periodical_tableWidget, i)
                    
                    if self.periodical_tableWidget.item(i, 1)==None or self.periodical_tableWidget.item(i, 2)==None or self.periodical_tableWidget.item(i, 3)==None or self.periodical_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки периодических услуг")
                        self.connection.rollback()
                        return
                    
                    if id!=-1:
                        periodical_service = self.connection.get("SELECT * FROM billservice_periodicalservice WHERE id=%d" % id)
                    else:
                        periodical_service = Object()
                    
                    periodical_service.name=unicode(self.periodical_tableWidget.item(i, 1).text())
                    periodical_service.settlement_period_id = self.connection.get("SELECT * FROM billservice_settlementperiod WHERE name='%s'" % unicode(self.periodical_tableWidget.item(i, 2).text())).id
                    periodical_service.cash_method = unicode(self.periodical_tableWidget.item(i, 3).text())
                    periodical_service.cost=unicode(self.periodical_tableWidget.item(i, 4).text())
                    
                    periodical_service_id = self.connection.create(periodical_service.save("billservice_periodicalservice"))     
                      
                    #Если это новая запись
                    if periodical_service_id>0:      
                        self.connection.create("INSERT INTO billservice_tariff_periodical_services(tariff_id, periodicalservice_id) VALUES(%d, %d)" % (model.id, periodical_service_id))
            elif self.periodical_services_checkbox.checkState()==0:
                peridical_services = self.connection.sql("SELECT * FROM billservice_tariff_periodical_services WHERE tariff_id=%d" % model_id)
                if len(peridical_services)>0:
                    self.connection.delete("DELETE FROM billservice_tariff_periodical_services WHERE tariff_id=%d" % model_id) 
                    for periodical_service in periodical_services:
                        self.connection.delete("DELETE FROM billservice_tariff_periodical_services WHERE periodicalservice_id=%d" % periodical_service.periodicalservice_id)
                
    
            #Лимиты
            if self.limit_tableWidget.rowCount()>0 and self.limites_checkbox.checkState()==2:
                for i in xrange(0, self.limit_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.limit_tableWidget, i)
                    #print self.limit_tableWidget.item(i, 1), self.limit_tableWidget.item(i, 3), self.limit_tableWidget.item(i, 8), self.limit_tableWidget.cellWidget(i, 4)
                    if self.limit_tableWidget.item(i, 1)==None or self.limit_tableWidget.item(i, 3)==None or self.limit_tableWidget.item(i, 7)==None or self.limit_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки лимитов")
                        self.connection.rollback()
                        return
                    elif self.limit_tableWidget.item(i, 4)!=None:
                        if self.limit_tableWidget.item(i, 4)==[]:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"В настройках лимитов не указаны классы трафика")
                            self.connection.rollback()
                            return                            
                    
                    traffic_class_models = [x.id for x in self.limit_tableWidget.item(i, 4).models]
    
                    if len(traffic_class_models)==0:
                        return
                    
                    if id!=-1:
                        
                        limit = self.connection.get("SELECT * FROM billservice_trafficlimit WHERE id=%d" % id)
                    else:
                        limit = Object()
                    
                    limit.name=unicode(self.limit_tableWidget.item(i, 1).text())
                    limit.settlement_period_id = self.connection.get("SELECT * FROM billservice_settlementperiod WHERE name='%s'" % unicode(self.limit_tableWidget.item(i, 3).text())).id
                    limit.mode = self.limit_tableWidget.cellWidget(i,2).checkState()==2
                    limit.size=unicode(int(unicode(self.limit_tableWidget.item(i, 7).text()))*1024*1024)
    
                    limit.in_direction = self.limit_tableWidget.cellWidget(i,5).checkState()==2
                    limit.out_direction = self.limit_tableWidget.cellWidget(i,6).checkState()==2
                    #limit.transit_direction = self.limit_tableWidget.cellWidget(i,7).checkState()==2
                    
                    limit_id = self.connection.create(limit.save("billservice_trafficlimit"))
                    
                    if limit_id==-1:
                        limit_id=limit.id
                    
                    #print 'limit_id=', limit_id
                    
                    traffic_classes_for_limit = self.connection.sql("""SELECT class.* FROM nas_trafficclass as class
                    JOIN billservice_trafficlimit_traffic_class as tc ON tc.trafficclass_id = class.id
                    WHERE tc.trafficlimit_id=%d
                    """ % limit_id)
    
                    traffic_classes_for_limit= [x.id for x in traffic_classes_for_limit]
                    for cl in traffic_class_models:
                        if cl not in traffic_classes_for_limit:
                            self.connection.create("INSERT INTO billservice_trafficlimit_traffic_class(trafficlimit_id, trafficclass_id) VALUES(%d, %d)" % (limit_id, cl))
    
                    for cl in traffic_classes_for_limit:
                        if cl not in traffic_class_models:
                            self.connection.delete("DELETE FROM billservice_trafficlimit_traffic_class WHERE trafficlimit_id=%d and trafficclass_id=%d " % (limit_id, cl))
                                            
    #                limit.save()     
                      
                    #Если это новая запись
                    #print 'id', id
                    if id==-1:   
                        #print u"Сохраняем связь"   
                        self.connection.create("INSERT INTO billservice_tariff_traffic_limit(tariff_id, trafficlimit_id) VALUES (%d, %d);" % (model_id, limit_id)) 
                        #limit.tariff_set.add(model)
            elif self.limites_checkbox.checkState()==0:
                limites = self.connection.sql("SELECT * FROM billservice_tariff_traffic_limit WHERE tariff_id=%d" % model_id)
                if len(limites)>0:
                    for limit in limites:
                        self.connection.delete("DELETE FROM billservice_trafficlimit_traffic_class WHERE trafficlimit_id=%d" % limit.id)
                    self.connection.delete("DELETE FROM billservice_tariff_traffic_limit WHERE tariff_id=%d;" % model_id)
                                
            #Доступ по трафику 
            if self.trafficcost_tableWidget.rowCount()>0 and self.transmit_service_checkbox.checkState()==2:
                if not model.isnull('traffic_transmit_service_id'):
                    #print "'traffic_transmit_service'1"
                    traffic_transmit_service = self.connection.get("SELECT * FROM billservice_traffictransmitservice WHERE id=%d" % self.model.traffic_transmit_service_id)
                else:
                    #print 'traffic_transmit_service2'
                    traffic_transmit_service = Object()
                
                traffic_transmit_service.period_check='SP_START'
                traffic_transmit_service.reset_traffic=self.reset_traffic_edit.checkState()==2
                traffic_transmit_service_id = self.connection.create(traffic_transmit_service.save("billservice_traffictransmitservice"))
                
                if traffic_transmit_service_id==-1:
                    traffic_transmit_service_id = traffic_transmit_service.id
                    
     
                
                for i in xrange(0, self.trafficcost_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.trafficcost_tableWidget, i)
                    
                    if self.trafficcost_tableWidget.item(i, 1)==None or self.trafficcost_tableWidget.item(i, 2)==None or self.trafficcost_tableWidget.item(i, 3)==None or self.trafficcost_tableWidget.item(i, 6)==None or self.trafficcost_tableWidget.item(i, 7)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для оплаты за трафик")
                        self.connection.rollback()
                        return
                    elif self.trafficcost_tableWidget.item(i, 3)!=None:
                        if self.trafficcost_tableWidget.item(i, 3)==[]:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для оплаты за трафик")
                            self.connection.rollback()
                            return    
                    elif self.trafficcost_tableWidget.item(i, 6)!=None:
                        if self.trafficcost_tableWidget.item(i, 6)==[]:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для оплаты за трафик")
                            self.connection.rollback()
                            return
                                                   
                    if id!=-1:
                        transmit_node = self.connection.get("SELECT * FROM billservice_traffictransmitnodes WHERE id=%d" % id)
                    else:
                        transmit_node = Object()
                    
                    
                    transmit_node.traffic_transmit_service_id = traffic_transmit_service_id
                    transmit_node.edge_start = unicode(self.trafficcost_tableWidget.item(i,1).text() or 0)
                    transmit_node.edge_end = unicode(self.trafficcost_tableWidget.item(i,2).text() or 0)
                    transmit_node.in_direction = self.trafficcost_tableWidget.cellWidget(i,4).checkState()==2
                    transmit_node.out_direction = self.trafficcost_tableWidget.cellWidget(i,5).checkState()==2
                    #transmit_node.transit_direction = self.trafficcost_tableWidget.cellWidget(i,6).checkState()==2
                    transmit_node.cost = unicode(self.trafficcost_tableWidget.item(i,7).text())
                    
                    
                    
                    traffic_class_models = self.trafficcost_tableWidget.item(i, 3).models
                    
                    traffic_class_models = [x.id for x in traffic_class_models]
                    
                    if len(traffic_class_models)==0:
                        return
                    
                    transmit_node_id = self.connection.create(transmit_node.save("billservice_traffictransmitnodes"))
                    
                    if transmit_node_id==-1:
                        transmit_node_id=transmit_node.id
                        
                    traffic_classes_for_node = self.connection.sql("""SELECT trafficclass.* FROM nas_trafficclass as trafficclass 
                    
                    JOIN billservice_traffictransmitnodes_traffic_class as tc ON tc.trafficclass_id =  trafficclass.id
                    WHERE tc.traffictransmitnodes_id=%d""" % transmit_node_id)
                    
                    traffic_classes = [x.id for x in traffic_classes_for_node]
                    for cl in traffic_class_models:
                        #print (transmit_node_id, cl.id)
                        if cl not in traffic_classes:
                            #print cl, traffic_classes
                            self.connection.create("""INSERT INTO billservice_traffictransmitnodes_traffic_class(traffictransmitnodes_id, trafficclass_id) VALUES(%d, %d)""" % (transmit_node_id, cl))
                            #cl.traffictransmitnodes_set.add(transmit_node)
                            
                            #print "add"
    
                    for cl in traffic_classes:
                        if cl not in traffic_class_models:
                            self.connection.delete("DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=%d and trafficclass_id=%d" % (transmit_node_id, cl))
                            #cl.traffictransmitnodes_set.remove(transmit_node)
    #                        print "del"
                            
                    time_period_models = [x.id for x in self.trafficcost_tableWidget.item(i, 6).models]
                    if len(time_period_models)==0:
                        return
                    
                    time_periods_for_node = self.connection.sql("""SELECT timeperiod.* FROM billservice_timeperiod as timeperiod
                                                                JOIN billservice_traffictransmitnodes_time_nodes as tn ON tn.timeperiod_id=timeperiod.id
                                                                WHERE tn.traffictransmitnodes_id=%d
                                                                """ % transmit_node_id)
                    time_periods_for_node = [x.id for x in time_periods_for_node]
                    for cl in time_period_models:
                        if cl not in time_periods_for_node:
                            #cl.traffictransmitnodes_set.add(transmit_node)
                            self.connection.create("""INSERT INTO billservice_traffictransmitnodes_time_nodes(traffictransmitnodes_id, timeperiod_id) VALUES(%d, %d)""" % (transmit_node_id, cl))

                    for cl in time_periods_for_node:
                        if cl not in time_period_models:
                            #cl.traffictransmitnodes_set.remove(transmit_node)
                            self.connection.delete("DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=%d and timeperiod_id=%d" % (transmit_node_id, cl))

                    #transmit_node.save() 
                    #traffic_transmit_service.save()  

                model.traffic_transmit_service_id = traffic_transmit_service_id
                #self.model.save() 

                #Предоплаченный трафик
                for i in xrange(self.prepaid_tableWidget.rowCount()):
                    id = self.getIdFromtable(self.prepaid_tableWidget, i)
                    
                    if self.prepaid_tableWidget.item(i, 1)==None or self.prepaid_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для предоплаченного трафика")
                        self.connection.rollback()
                        return
                    elif self.prepaid_tableWidget.item(i, 1)!=None:
                        if self.prepaid_tableWidget.item(i, 1)==[]:
                            QtGui.QMessageBox.warning(self, u"Ошибка", u"В настройках лимитов не указаны классы трафика")
                            self.connection.rollback()
                            return    
                        
                    if id!=-1:
                        #print "prepaid_id=", id
                        prepaid_node = self.connection.get("SELECT * FROM billservice_prepaidtraffic WHERE id=%d" % id)
                    else:
                        prepaid_node = Object()

                    #print "i=", self.prepaid_tableWidget.item(i,2)

                    prepaid_node.traffic_transmit_service_id = traffic_transmit_service_id
                    prepaid_node.in_direction = self.prepaid_tableWidget.cellWidget(i,2).checkState()==2
                    prepaid_node.out_direction = self.prepaid_tableWidget.cellWidget(i,3).checkState()==2
                    #prepaid_node.transit_direction = self.prepaid_tableWidget.cellWidget(i,4).checkState()==2
                    prepaid_node.size = unicode(float(self.prepaid_tableWidget.item(i,4).text())*1024*1024)


                    traffic_class_models = [x.id for x in self.prepaid_tableWidget.item(i, 1).models]
                    if len(traffic_class_models)==0:
                        return

                    prepaid_node_id = self.connection.create(prepaid_node.save("billservice_prepaidtraffic"))
                    if prepaid_node_id==-1:
                        prepaid_node_id = prepaid_node.id 

                    traffic_classes_for_node = self.connection.sql("""SELECT trafficclass.* FROM nas_trafficclass as trafficclass 

                    JOIN billservice_prepaidtraffic_traffic_class as tc ON tc.trafficclass_id = trafficclass.id
                    WHERE tc.prepaidtraffic_id=%d""" % prepaid_node_id)

                    traffic_classes_for_node = [x.id for x in traffic_classes_for_node]

                    for cl in traffic_class_models:
                        if cl not in traffic_classes_for_node:
                            self.connection.create("INSERT INTO billservice_prepaidtraffic_traffic_class(prepaidtraffic_id, trafficclass_id) VALUES(%d,%d)" % (prepaid_node_id, cl))
                            #cl.prepaidtraffic_set.add(prepaid_node)
                            #print "add"
    
                    for cl in traffic_classes_for_node:
                        if cl not in traffic_class_models:
                            self.connection.delete("DELETE FROM billservice_prepaidtraffic_traffic_class WHERE prepaidtraffic_id=%d and trafficclass_id=%d " % (prepaid_node_id, cl))
                            #cl.prepaidtraffic_set.remove(prepaidt_node)
                            #print "del"
                            
                                                                    
                    #self.connection.create(prepaid_node.save("billservice_prepaidtraffic")) 
    
            elif (self.transmit_service_checkbox.checkState()==0 or self.trafficcost_tableWidget.rowCount()==0) and not model.isnull("traffic_transmit_service_id"):
                self.connection.delete("DELETE FROM billservice_traffictransmitservice WHERE id=%d" % model.traffic_transmit_service_id)
                model.traffic_transmit_service_id=None
                
                            
        
            
            self.connection.create(model.save("billservice_tariff"))
            self.connection.commit()
        
            #print True
            
        except Exception, e:
            print e
            traceback.print_exc()
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", u"Ошибка сохранения тарифного плана")
            return

        QtGui.QDialog.accept(self)
                    
class AddAccountFrame(QtGui.QDialog):
    def __init__(self, connection,ttype, model=None):
        super(AddAccountFrame, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection

        self.resize(QtCore.QSize(QtCore.QRect(0,0,340,435).size()).expandedTo(self.minimumSizeHint()))
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(80,400,251,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0,10,341,381))
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.status_edit = QtGui.QCheckBox(self.tab)
        self.status_edit.setGeometry(QtCore.QRect(10,330,70,19))
        self.status_edit.setObjectName("status_edit")

        self.suspended_edit = QtGui.QCheckBox(self.tab)
        self.suspended_edit.setGeometry(QtCore.QRect(10,310,301,19))
        self.suspended_edit.setObjectName("suspended_edit")

        self.account_data_groupBox = QtGui.QGroupBox(self.tab)
        self.account_data_groupBox.setGeometry(QtCore.QRect(10,10,291,81))
        self.account_data_groupBox.setObjectName("account_data_groupBox")

        self.generate_login_toolButton = QtGui.QToolButton(self.account_data_groupBox)
        self.generate_login_toolButton.setEnabled(True)
        self.generate_login_toolButton.setGeometry(QtCore.QRect(250,20,21,20))
        self.generate_login_toolButton.setObjectName("generate_login_toolButton")

        self.password_label = QtGui.QLabel(self.account_data_groupBox)
        self.password_label.setGeometry(QtCore.QRect(12,50,44,20))
        self.password_label.setObjectName("password_label")

        self.username_label = QtGui.QLabel(self.account_data_groupBox)
        self.username_label.setGeometry(QtCore.QRect(12,20,44,21))
        self.username_label.setObjectName("username_label")

        self.generate_password_toolButton = QtGui.QToolButton(self.account_data_groupBox)
        self.generate_password_toolButton.setGeometry(QtCore.QRect(250,50,21,20))
        self.generate_password_toolButton.setObjectName("generate_password_toolButton")

        self.password_edit = QtGui.QLineEdit(self.account_data_groupBox)
        self.password_edit.setGeometry(QtCore.QRect(60,50,181,20))
        self.password_edit.setObjectName("password_edit")

        self.username_edit = QtGui.QLineEdit(self.account_data_groupBox)
        self.username_edit.setGeometry(QtCore.QRect(60,20,181,20))
        self.username_edit.setObjectName("username_edit")

        self.account_info_groupBox = QtGui.QGroupBox(self.tab)
        self.account_info_groupBox.setGeometry(QtCore.QRect(10,100,291,111))
        self.account_info_groupBox.setObjectName("account_info_groupBox")

        self.email_lineEdit = QtGui.QLineEdit(self.account_info_groupBox)
        self.email_lineEdit.setGeometry(QtCore.QRect(60,80,211,21))
        self.email_lineEdit.setObjectName("email_lineEdit")

        self.address_label = QtGui.QLabel(self.account_info_groupBox)
        self.address_label.setGeometry(QtCore.QRect(10,80,44,21))
        self.address_label.setObjectName("address_label")

        self.address_lineEdit = QtGui.QLineEdit(self.account_info_groupBox)
        self.address_lineEdit.setGeometry(QtCore.QRect(60,50,211,21))
        self.address_lineEdit.setObjectName("address_lineEdit")

        self.fullname_label = QtGui.QLabel(self.account_info_groupBox)
        self.fullname_label.setGeometry(QtCore.QRect(10,20,44,20))
        self.fullname_label.setObjectName("fullname_label")

        self.fullname_lineEdit = QtGui.QLineEdit(self.account_info_groupBox)
        self.fullname_lineEdit.setGeometry(QtCore.QRect(60,20,211,21))
        self.fullname_lineEdit.setObjectName("fullname_lineEdit")

        self.lastname_edit = QtGui.QLabel(self.account_info_groupBox)
        self.lastname_edit.setGeometry(QtCore.QRect(10,50,44,20))
        self.lastname_edit.setObjectName("lastname_edit")

        self.ballance_info_groupBox = QtGui.QGroupBox(self.tab)
        self.ballance_info_groupBox.setGeometry(QtCore.QRect(10,220,291,80))
        self.ballance_info_groupBox.setObjectName("ballance_info_groupBox")

        self.balance_edit = QtGui.QLineEdit(self.ballance_info_groupBox)
        self.balance_edit.setGeometry(QtCore.QRect(130,20,138,21))
        self.balance_edit.setObjectName("balance_edit")

        self.credit_label = QtGui.QLabel(self.ballance_info_groupBox)
        self.credit_label.setGeometry(QtCore.QRect(9,50,115,21))
        self.credit_label.setObjectName("credit_label")

        self.ballance_label = QtGui.QLabel(self.ballance_info_groupBox)
        self.ballance_label.setGeometry(QtCore.QRect(9,20,115,21))
        self.ballance_label.setObjectName("ballance_label")

        self.credit_edit = QtGui.QLineEdit(self.ballance_info_groupBox)
        self.credit_edit.setGeometry(QtCore.QRect(130,50,138,21))
        self.credit_edit.setObjectName("credit_edit")
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.ip_settings_groupBox = QtGui.QGroupBox(self.tab_2)
        self.ip_settings_groupBox.setGeometry(QtCore.QRect(10,40,321,171))
        self.ip_settings_groupBox.setObjectName("ip_settings_groupBox")

        self.assign_ipn_ip_from_dhcp_edit = QtGui.QCheckBox(self.ip_settings_groupBox)
        self.assign_ipn_ip_from_dhcp_edit.setGeometry(QtCore.QRect(10,20,219,19))
        self.assign_ipn_ip_from_dhcp_edit.setObjectName("assign_ipn_ip_from_dhcp_edit")

        self.ipn_ip_address_label = QtGui.QLabel(self.ip_settings_groupBox)
        self.ipn_ip_address_label.setGeometry(QtCore.QRect(10,50,114,20))
        self.ipn_ip_address_label.setObjectName("ipn_ip_address_label")

        self.ipn_mac_address_label = QtGui.QLabel(self.ip_settings_groupBox)
        self.ipn_mac_address_label.setGeometry(QtCore.QRect(11,110,114,20))
        self.ipn_mac_address_label.setObjectName("ipn_mac_address_label")

        self.ipn_mac_address_edit = QtGui.QLineEdit(self.ip_settings_groupBox)
        self.ipn_mac_address_edit.setGeometry(QtCore.QRect(131,110,110,21))
        self.ipn_mac_address_edit.setObjectName("ipn_mac_address_edit")

        self.vpn_ip_address_label = QtGui.QLabel(self.ip_settings_groupBox)
        self.vpn_ip_address_label.setGeometry(QtCore.QRect(11,140,114,20))
        self.vpn_ip_address_label.setObjectName("vpn_ip_address_label")

        self.ipn_ip_address_edit = QtGui.QLineEdit(self.ip_settings_groupBox)
        self.ipn_ip_address_edit.setGeometry(QtCore.QRect(131,47,110,21))
        self.ipn_ip_address_edit.setObjectName("ipn_ip_address_edit")

        self.vpn_ip_address_edit = QtGui.QLineEdit(self.ip_settings_groupBox)
        self.vpn_ip_address_edit.setGeometry(QtCore.QRect(131,140,111,21))
        self.vpn_ip_address_edit.setFrame(True)
        self.vpn_ip_address_edit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.vpn_ip_address_edit.setObjectName("vpn_ip_address_edit")

        self.ipn_ip_address_label_2 = QtGui.QLabel(self.ip_settings_groupBox)
        self.ipn_ip_address_label_2.setGeometry(QtCore.QRect(10,81,114,20))
        self.ipn_ip_address_label_2.setObjectName("ipn_ip_address_label_2")

        self.netmask_edit = QtGui.QLineEdit(self.ip_settings_groupBox)
        self.netmask_edit.setGeometry(QtCore.QRect(130,80,110,21))
        self.netmask_edit.setFrame(True)
        self.netmask_edit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.netmask_edit.setObjectName("netmask_edit")

        self.vpn_speed_groupBox = QtGui.QGroupBox(self.tab_2)
        self.vpn_speed_groupBox.setGeometry(QtCore.QRect(10,220,321,51))
        self.vpn_speed_groupBox.setCheckable(True)
        self.vpn_speed_groupBox.setChecked(False)
        self.vpn_speed_groupBox.setObjectName("vpn_speed_groupBox")

        self.vpn_speed_lineEdit = QtGui.QLineEdit(self.vpn_speed_groupBox)
        self.vpn_speed_lineEdit.setGeometry(QtCore.QRect(10,20,301,20))
        self.vpn_speed_lineEdit.setObjectName("vpn_speed_lineEdit")

        self.nas_label = QtGui.QLabel(self.tab_2)
        self.nas_label.setGeometry(QtCore.QRect(10,10,101,20))
        self.nas_label.setObjectName("nas_label")

        self.nas_comboBox = QtGui.QComboBox(self.tab_2)
        self.nas_comboBox.setGeometry(QtCore.QRect(110,10,151,20))
        self.nas_comboBox.setObjectName("nas_comboBox")
        self.ipn_speed_groupBox = QtGui.QGroupBox(self.tab_2)
        self.ipn_speed_groupBox.setGeometry(QtCore.QRect(10,280,321,51))
        self.ipn_speed_groupBox.setCheckable(True)
        self.ipn_speed_groupBox.setChecked(False)
        self.ipn_speed_groupBox.setObjectName("ipn_speed_groupBox")

        self.ipn_speed_lineEdit = QtGui.QLineEdit(self.ipn_speed_groupBox)
        self.ipn_speed_lineEdit.setGeometry(QtCore.QRect(10,20,301,20))
        self.ipn_speed_lineEdit.setObjectName("ipn_speed_lineEdit")
        self.tabWidget.addTab(self.tab_2,"")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.accounttarif_table = QtGui.QTableWidget(self.tab_3)
        self.accounttarif_table.setGeometry(QtCore.QRect(0,90,331,261))
        self.accounttarif_table.setObjectName("accounttarif_table")
        

        self.add_accounttarif_toolButton = QtGui.QToolButton(self.tab_3)
        self.add_accounttarif_toolButton.setGeometry(QtCore.QRect(0,70,25,20))
        self.add_accounttarif_toolButton.setObjectName("add_accounttarif_toolButton")

        self.del_accounttarif_toolButton = QtGui.QToolButton(self.tab_3)
        self.del_accounttarif_toolButton.setGeometry(QtCore.QRect(30,70,25,20))
        self.del_accounttarif_toolButton.setObjectName("del_accounttarif_toolButton")

        self.label_3 = QtGui.QLabel(self.tab_3)
        self.label_3.setGeometry(QtCore.QRect(10,10,311,42))
        self.label_3.setObjectName("label_3")
        self.tabWidget.addTab(self.tab_3,"")
        self.password_label.setBuddy(self.password_edit)
        self.username_label.setBuddy(self.username_edit)
        self.address_label.setBuddy(self.email_lineEdit)
        self.fullname_label.setBuddy(self.fullname_lineEdit)
        self.lastname_edit.setBuddy(self.address_lineEdit)
        self.credit_label.setBuddy(self.credit_edit)
        self.ballance_label.setBuddy(self.balance_edit)
        self.ipn_ip_address_label.setBuddy(self.ipn_ip_address_edit)
        self.ipn_mac_address_label.setBuddy(self.ipn_mac_address_edit)
        self.vpn_ip_address_label.setBuddy(self.vpn_ip_address_edit)
        self.ipn_ip_address_label_2.setBuddy(self.netmask_edit)
        self.nas_label.setBuddy(self.nas_comboBox)
        self.setTabOrder(self.tabWidget,self.username_edit)
        self.setTabOrder(self.username_edit,self.generate_login_toolButton)
        self.setTabOrder(self.generate_login_toolButton,self.password_edit)
        self.setTabOrder(self.password_edit,self.generate_password_toolButton)
        self.setTabOrder(self.generate_password_toolButton,self.fullname_lineEdit)
        self.setTabOrder(self.fullname_lineEdit,self.address_lineEdit)
        self.setTabOrder(self.address_lineEdit,self.email_lineEdit)
        self.setTabOrder(self.email_lineEdit,self.balance_edit)
        self.setTabOrder(self.balance_edit,self.credit_edit)
        self.setTabOrder(self.credit_edit,self.suspended_edit)
        self.setTabOrder(self.suspended_edit,self.status_edit)
        self.setTabOrder(self.status_edit,self.nas_comboBox)
        self.setTabOrder(self.nas_comboBox,self.assign_ipn_ip_from_dhcp_edit)
        self.setTabOrder(self.assign_ipn_ip_from_dhcp_edit,self.ipn_ip_address_edit)
        self.setTabOrder(self.ipn_ip_address_edit,self.netmask_edit)
        self.setTabOrder(self.netmask_edit,self.ipn_mac_address_edit)
        self.setTabOrder(self.ipn_mac_address_edit,self.vpn_ip_address_edit)
        self.setTabOrder(self.vpn_ip_address_edit,self.vpn_speed_groupBox)
        self.setTabOrder(self.vpn_speed_groupBox,self.vpn_speed_lineEdit)
        self.setTabOrder(self.vpn_speed_lineEdit,self.ipn_speed_groupBox)
        self.setTabOrder(self.ipn_speed_groupBox,self.ipn_speed_lineEdit)
        self.setTabOrder(self.ipn_speed_lineEdit,self.add_accounttarif_toolButton)
        self.setTabOrder(self.add_accounttarif_toolButton,self.del_accounttarif_toolButton)
        self.setTabOrder(self.del_accounttarif_toolButton,self.accounttarif_table)
        self.setTabOrder(self.accounttarif_table,self.buttonBox)

        self.accounttarif_table = tableFormat(self.accounttarif_table)
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.generate_login_toolButton,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.generate_password_toolButton,QtCore.SIGNAL("clicked()"),self.generate_password)
        
        self.connect(self.assign_ipn_ip_from_dhcp_edit, QtCore.SIGNAL("stateChanged(int)"), self.dhcpActions)
        
        self.connect(self.add_accounttarif_toolButton,QtCore.SIGNAL("clicked()"),self.add_accounttarif)
        self.connect(self.del_accounttarif_toolButton,QtCore.SIGNAL("clicked()"),self.del_accounttarif)

        self.connect(self.accounttarif_table, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)
        
        self.retranslateUi()
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.suspended_edit.setText(QtGui.QApplication.translate("Dialog", "Не списывать деньги по периодическим услугам", None, QtGui.QApplication.UnicodeUTF8))
        self.account_data_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Учётные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.generate_login_toolButton.setText(QtGui.QApplication.translate("Dialog", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("Dialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.username_label.setText(QtGui.QApplication.translate("Dialog", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.generate_password_toolButton.setText(QtGui.QApplication.translate("Dialog", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.account_info_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Информация о пользователе", None, QtGui.QApplication.UnicodeUTF8))
        self.address_label.setText(QtGui.QApplication.translate("Dialog", "Email", None, QtGui.QApplication.UnicodeUTF8))
        self.fullname_label.setText(QtGui.QApplication.translate("Dialog", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.lastname_edit.setText(QtGui.QApplication.translate("Dialog", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ballance_info_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Платёжная информация", None, QtGui.QApplication.UnicodeUTF8))
        self.credit_label.setText(QtGui.QApplication.translate("Dialog", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.ballance_label.setText(QtGui.QApplication.translate("Dialog", "Текущий баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.ip_settings_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "IP Адреса", None, QtGui.QApplication.UnicodeUTF8))
        self.assign_ipn_ip_from_dhcp_edit.setText(QtGui.QApplication.translate("Dialog", "Выдавать IP адрес с помощью DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_ip_address_label.setText(QtGui.QApplication.translate("Dialog", "Текущий IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_mac_address_label.setText(QtGui.QApplication.translate("Dialog", "Аппаратный адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_mac_address_edit.setInputMask(QtGui.QApplication.translate("Dialog", ">HH:HH:HH:HH:HH:HH;0", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_ip_address_label_2.setText(QtGui.QApplication.translate("Dialog", "Маска подсети", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_ip_address_label.setText(QtGui.QApplication.translate("Dialog", "VPN Адрес", None, QtGui.QApplication.UnicodeUTF8))
        #self.netmask_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Индивидуальные настройки скорости для VPN", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_label.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Индивидуальные настройки скорости для IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Сетевые настройки", None, QtGui.QApplication.UnicodeUTF8))
        
        

        self.add_accounttarif_toolButton.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_accounttarif_toolButton.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Здесь вы можете просмотреть историю тарифных планов\n"
        " пользователя и создать задания для перехода на\n"
        " новые тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Здесь вы можете просмотреть историю тарифных планов\n"
        " пользователя и создать задания для перехода на\n"
        " новые тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))

        
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.ipn_ip_address_edit.setValidator(self.ipValidator)
        self.vpn_ip_address_edit.setValidator(self.ipValidator)
        self.netmask_edit.setValidator(self.ipValidator)
        
        self.accounttarif_table.clear()
        self.accounttarif_table.setColumnCount(4)
        columns=[u'#', u'Тарифный план', u'Дата']


        makeHeaders(columns, self.accounttarif_table)
        
    def dhcpActions(self, newstate):
        
        if newstate==2:
            self.netmask_edit.setDisabled(False)
        elif newstate==0:
            self.netmask_edit.setDisabled(True)
            
            

    def getSelectedId(self):
        return int(self.accounttarif_table.item(self.accounttarif_table.currentRow(), 0).text())

    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection,ttype=self.ttype, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def del_accounttarif(self):
        i=self.getSelectedId()
        model = self.connection.get("SELECT * FROM billservice_accounttarif WHERE id=%d" % i)
        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.delete("DELETE FROM billservice_accounttarif WHERE id=%d" % i)
            self.accountTarifRefresh()

    def edit_accounttarif(self):
        i=self.getSelectedId()
        try:
            model=self.connection.get("SELECT * FROM billservice_accounttarif WHERE id=%d" % i)
        except:
            return

        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        child=AddAccountTarif(connection=self.connection, ttype=self.ttype, model=model)
        if child.exec_()==1:
            self.accountTarifRefresh()




    def generate_login(self):
        self.username_edit.setText(nameGen())

    def generate_password(self):
        self.password_edit.setText(GenPasswd2())

    def accept(self):
        """
        понаставить проверок
        """
        self.connection.commit()
        try:
            
            if self.model:
                model=self.model
                model = self.connection.get("SELECT * FROM billservice_account WHERE id=%d" % self.model.id)
                
                
            else:
                print 'New account'
                if self.connection.get("SELECT count(*) as count FROM billservice_account WHERE username='%s'" % unicode(self.username_edit.text())).count > 0:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                    self.connection.rollback()
                    return
    
                model=Object()
                model.created = datetime.datetime.now()
    
                #model.user_id=1
                model.ipn_status = False
                model.disabled_by_limit = False
                
            model.username = unicode(self.username_edit.text())
    
            model.password = unicode(self.password_edit.text())
            model.fullname = unicode(self.fullname_lineEdit.text())
            model.email = unicode(self.email_lineEdit.text())
            model.address = unicode(self.address_lineEdit.text())
            
            #print "self.speed_groupBox.isChecked()=", self.speed_groupBox.isChecked()
            if self.vpn_speed_groupBox.isChecked()==True and self.vpn_speed_lineEdit.text()!="":
                #print "save vpn speed=True"
                model.vpn_speed = unicode(self.vpn_speed_lineEdit.text())
            else:
                model.vpn_speed = ""

            if self.ipn_speed_groupBox.isChecked()==True and self.ipn_speed_lineEdit.text()!="":
                #print "save ipn speed=True"
                model.ipn_speed = unicode(self.ipn_speed_lineEdit.text())
            else:
                model.ipn_speed = ""
            #убрать действие с чекбокса "получать адрес по дхцп"
            #проверка уникальности MAC создание/редактирование
            #classframe - validate ip's
            #while 1:
            if self.ipn_ip_address_edit.text():
                #print self.ipValidator.validate(self.ipn_ip_address_edit.text(), 0)
                if self.ipValidator.validate(self.ipn_ip_address_edit.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите IPN IP до конца."))
                    return
                try:
                    ipn_address_account = self.connection.get("SELECT * FROM billservice_account WHERE ipn_ip_address='%s'" % unicode(self.ipn_ip_address_edit.text()))
                    if ipn_address_account.id != model.id:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
                        self.connection.rollback()
                        return  
                                          
                except Exception, ex:
                    print ex
                model.ipn_ip_address = unicode(self.ipn_ip_address_edit.text())
            elif self.ttype == 'IPN':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь создан на IPN тарифном плане. \n IPN IP должен быть введён до конца."))
                return
            else:
                model.ipn_ip_address = '0.0.0.0'
                

            if self.vpn_ip_address_edit.text():
                if self.ipValidator.validate(self.vpn_ip_address_edit.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите VPN IP до конца."))
                    return
                try:
                    vpn_address_account = self.connection.get("SELECT * FROM billservice_account WHERE vpn_ip_address='%s'" % unicode(self.vpn_ip_address_edit.text()))
                    if vpn_address_account.id != model.id:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
                        self.connection.rollback()
                        return    
                          
                except Exception, ex:
                    print ex
                
                model.vpn_ip_address = unicode(self.vpn_ip_address_edit.text())
            elif self.ttype == 'VPN':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь создан на VPN тарифном плане. \n VPN IP должен быть введён до конца."))
                return
            else:
                model.vpn_ip_address = '0.0.0.0'
              
            model.netmask = '0.0.0.0'
            if self.netmask_edit.isEnabled():
                if self.netmask_edit.text():
                    if self.ipValidator.validate(self.netmask_edit.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Маска указана неверно."))
                        self.connection.rollback()
                        return
                    model.netmask = unicode(self.netmask_edit.text())
                
                
            #model.netmask = unicode(self.netmask_edit.text())
            if ((model.ipn_ip_address == '0.0.0.0') and (model.vpn_ip_address == '0.0.0.0')):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Должен быть введён хотя бы один из адресов"))
                self.connection.rollback()
                return
    

            if unicode(self.ipn_mac_address_edit.text()) != ':::::':
                try:
                    ipn_mac_address_account = self.connection.get("SELECT * FROM billservice_account WHERE ipn_mac_address='%s'" % unicode(self.ipn_mac_address_edit.text()))
                    if ipn_mac_address_account.id !=model.id :
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
                        self.connection.rollback()
                        return
                except Exception, ex:
                    print ex
                model.ipn_mac_address = unicode(self.ipn_mac_address_edit.text())
            else:
                model.ipn_mac_address = ''
                    
    
            
            model.nas_id = self.connection.get("SELECT id FROM nas_nas WHERE name='%s'" % str(self.nas_comboBox.currentText())).id
    
            model.ballance = unicode(self.balance_edit.text()) or 0
            model.credit = unicode(self.credit_edit.text())
    
            model.assign_ipn_ip_from_dhcp = self.assign_ipn_ip_from_dhcp_edit.checkState() == QtCore.Qt.Checked
            model.suspended = self.suspended_edit.checkState() == QtCore.Qt.Checked
            model.status = self.status_edit.checkState() == QtCore.Qt.Checked
            
            
            if self.model:
                self.connection.create(model.save("billservice_account"))
            else:
                
                model.id=self.connection.create(model.save("billservice_account"))
            #print "model.ipn_mac_address", model.ipn_mac_address
            
            
            if model.ipn_ip_address!="0.0.0.0":
                self.connection.accountActions(model.id, 'delete')
                if self.connection.accountActions(model.id, 'create'):
                    #self.connection.commit()
                    QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Пользователь успешно синхронизирован на сервере доступа."))
                else:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Для начала работы необходимо синхронизировать изменения на сервере доступа с помощью контекстного меню."))
                    #self.connection.rollback()
                #self.connection.commit()
                
            #self.connection.commit()
            self.model=model
        except Exception, e:
            print "!!!SAVE CREATE ERROR", e
            import sys, traceback
            traceback.print_exc()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при сохранении."))
            self.connection.rollback()
            return 
        QtGui.QDialog.accept(self)



    def fixtures(self):


        pools = []

        nasses = self.connection.sql("SELECT * FROM nas_nas")
        for nas in nasses:
            self.nas_comboBox.addItem(nas.name)
        
        if not self.model:
            self.add_accounttarif_toolButton.setDisabled(True)
            self.del_accounttarif_toolButton.setDisabled(True)
            self.balance_edit.setText(u"0")
            self.credit_edit.setText(u"0")

        if self.model:
            self.username_edit.setText(unicode(self.model.username))

            self.nas_comboBox.setCurrentIndex(self.nas_comboBox.findText(self.model.nas_name, QtCore.Qt.MatchCaseSensitive))


            self.password_edit.setText(unicode(self.model.password))
            self.fullname_lineEdit.setText(unicode(self.model.fullname))
            self.email_lineEdit.setText(unicode(self.model.email))
            self.address_lineEdit.setText(unicode(self.model.address))
            self.netmask_edit.setText(unicode(self.model.netmask))
            self.ipn_ip_address_edit.setText(unicode(self.model.ipn_ip_address))
            self.vpn_ip_address_edit.setText(unicode(self.model.vpn_ip_address))
        
            #print "self.model.ipn_mac_address", self.model.ipn_mac_address
            if self.model.ipn_mac_address==None or self.model.ipn_mac_address=="":
                #print "assign True"
                self.assign_ipn_ip_from_dhcp_edit.setCheckState(QtCore.Qt.Checked)
                
            else:
                self.ipn_mac_address_edit.setText(unicode(self.model.ipn_mac_address))

            #print "self.model.status", self.model.status
            self.status_edit.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.suspended_edit.setCheckState(self.model.suspended == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            self.assign_ipn_ip_from_dhcp_edit.setCheckState(self.model.assign_ipn_ip_from_dhcp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            self.balance_edit.setText(unicode(self.model.ballance))
            self.credit_edit.setText(unicode(self.model.credit))
            
            if self.model.vpn_speed!="" and self.model.vpn_speed!=None:
                self.vpn_speed_groupBox.setChecked(True)
                self.vpn_speed_lineEdit.setText(self.model.vpn_speed)
            else:
                self.vpn_speed_groupBox.setChecked(False)
                
            if self.model.ipn_speed!="" and self.model.ipn_speed!=None:
                self.ipn_speed_groupBox.setChecked(True)
                self.ipn_speed_lineEdit.setText(self.model.ipn_speed)
            else:
                self.ipn_speed_groupBox.setChecked(False)
                                
            #self.last_vpn_login_label.setText(u"Последний VPN вход: %s" % self.lastVPNEntrance())

            

            self.accountTarifRefresh()

    def accountTarifRefresh(self):
        if self.model:
            ac=self.connection.sql("""SELECT accounttarif.*, tarif.name as tarif_name FROM billservice_accounttarif as accounttarif 
            JOIN billservice_tariff as tarif ON tarif.id=accounttarif.tarif_id
            WHERE account_id=%d ORDER BY datetime ASC""" % self.model.id)
            self.accounttarif_table.setRowCount(len(ac))
            i=0
            #print ac
            for a in ac:

                self.addrow(a.id, i,0)
                self.addrow(a.tarif_name, i,1)
                self.addrow(a.datetime.strftime(self.strftimeFormat), i,2)
                self.accounttarif_table.setRowHeight(i, 17)
                self.accounttarif_table.setColumnHidden(0, True)
                i+=1
            #self.tabWidget.resizeColumnsToContents()



    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        headerItem.setText(unicode(value))
        self.accounttarif_table.setItem(x,y,headerItem)




class AccountsMdiChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection, parent, selected_account=None):
        super(AccountsMdiChild, self).__init__()
        self.parent = parent
        self.connection = connection
        self.setObjectName('AccountMDI')
        self.selected_account = selected_account 
        self.setWindowTitle(u"Пользователи")
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.centralwidget = QtGui.QWidget(self)
        
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0,0,391,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        
        
        self.tarif_treeWidget = QtGui.QTreeWidget(self.splitter)
        #self.tarif_treeWidget.setGeometry(QtCore.QRect(0,0,221,551))
        #self.tarif_treeWidget.setFixedSize(QtCore.QSize(150,551))
        self.tarif_treeWidget.setObjectName("tarif_treeWidget")
        #self.tarif_treeWidget.headerItem().setText(0,"")
        self.tarif_treeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        



        self.tableWidget = QtGui.QTableWidget(self.splitter)
        
        #self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget = tableFormat(self.tableWidget)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
  
        columns=[u'id', u'Имя пользователя', u'Балланс', u'Кредит', u'Имя', u'E-mail', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u'Без ПУ', u'', u'Превышен лимит', u"Дата создания"]
        #self.tableWidget.setColumnCount(len(columns))
        
        makeHeaders(columns, self.tableWidget)
            
        
        tree_header = self.tarif_treeWidget.headerItem()
        hght = self.tableWidget.horizontalHeader().maximumHeight()
        sz = QtCore.QSize()
        sz.setHeight(hght)
        tree_header.setSizeHint(0,sz)
        tree_header.setSizeHint(1,sz)
        tree_header.setText(0,QtGui.QApplication.translate("MainWindow", "Тарифы", None, QtGui.QApplication.UnicodeUTF8))
        tree_header.setText(1,QtGui.QApplication.translate("MainWindow", "Тип", None, QtGui.QApplication.UnicodeUTF8))

        self.setCentralWidget(self.splitter)
        
        self.splitter.setSizes([self.width() / 5, self.width() - (self.width() / 5)])


        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        #self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        
        #self.toolBar.setMaximumHeight(24)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)


        self.addAction = QtGui.QAction(u"Добавить пользователя", self)
        self.addAction.setIcon(QtGui.QIcon("images/user_add.png"))


        self.delAction = QtGui.QAction(u"Удалить пользователя",self)
        self.delAction.setIcon(QtGui.QIcon("images/user_delete.png"))

        self.addTarifAction = QtGui.QAction(u"Добавить тарифный план",self)
        self.addTarifAction.setIcon(QtGui.QIcon("images/folder_add.png"))
        
        self.delTarifAction = QtGui.QAction(u"Удалить тарифный план",self)
        self.delTarifAction.setIcon(QtGui.QIcon("images/folder_delete.png"))
        
        self.transactionAction = QtGui.QAction(u'Пополнить счёт', self)
        self.transactionAction.setIcon(QtGui.QIcon("images/add.png"))

        self.transactionReportAction = QtGui.QAction(u'Журнал проводок',self)
        self.transactionReportAction.setIcon(QtGui.QIcon("images/add.png"))

        self.actionDisableSession = QtGui.QAction(u'Отключить на сервере доступа',self)
        self.actionDisableSession.setIcon(QtGui.QIcon("images/del.png"))

        self.actionEnableSession = QtGui.QAction(u'Включить на сервере доступа',self)
        self.actionEnableSession.setIcon(QtGui.QIcon("images/add.png"))

        self.actionAddAccount = QtGui.QAction(u'Добавить на сервер доступа',self)
        self.actionAddAccount.setIcon(QtGui.QIcon("images/add.png"))

        self.actionDeleteAccount = QtGui.QAction(u'Удалить с сервера доступа',self)
        self.actionDeleteAccount.setIcon(QtGui.QIcon("images/del.png"))
        
        self.editTarifAction = QtGui.QAction(self)
        self.editTarifAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editTarifAction.setObjectName("editTarifAction")
        
        self.editAccountAction = QtGui.QAction(self)
        self.editAccountAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editAccountAction.setObjectName("editAccountAction")
                
        self.tarif_treeWidget.addAction(self.editTarifAction)
        self.tarif_treeWidget.addAction(self.addTarifAction)
        self.tarif_treeWidget.addAction(self.delTarifAction)
        
        self.tableWidget.addAction(self.editAccountAction)
        self.tableWidget.addAction(self.addAction)
        self.tableWidget.addAction(self.delAction)
        self.tableWidget.addAction(self.transactionAction)
        self.tableWidget.addAction(self.actionEnableSession)
        self.tableWidget.addAction(self.actionDisableSession)
                        
        self.tableWidget.addAction(self.actionAddAccount)
        self.tableWidget.addAction(self.actionDeleteAccount)
        
        self.toolBar.addAction(self.addTarifAction)
        self.toolBar.addAction(self.delTarifAction)
        self.toolBar.addSeparator()        
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.transactionAction)
        self.toolBar.addAction(self.transactionReportAction)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.tableWidget.resizeColumnsToContents()
        self.resize(1100,600)


        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        
        self.connect(self.addTarifAction, QtCore.SIGNAL("triggered()"), self.addTarif)
        self.connect(self.delTarifAction, QtCore.SIGNAL("triggered()"), self.delTarif)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("itemClicked(QTableWidgetItem *)"), self.delNodeLocalAction)
        

        
        
        self.connect(self.transactionAction, QtCore.SIGNAL("triggered()"), self.makeTransation)
        
        self.connect(self.transactionReportAction, QtCore.SIGNAL("triggered()"), self.transactionReport) 
        
        self.connect(self.actionDisableSession, QtCore.SIGNAL("triggered()"), self.accountDisable)
        
        self.connect(self.actionEnableSession, QtCore.SIGNAL("triggered()"), self.accountEnable)

        self.connect(self.actionAddAccount, QtCore.SIGNAL("triggered()"), self.accountAdd)
        
        self.connect(self.actionDeleteAccount, QtCore.SIGNAL("triggered()"), self.accountDelete)
        
        self.connect(self.editTarifAction, QtCore.SIGNAL("triggered()"), self.editTarif)
        self.connect(self.editAccountAction, QtCore.SIGNAL("triggered()"), self.editframe)
        self.connectTree()
        
        
        self.retranslateUi()
        self.refreshTree()
        setFirstActive(self.tarif_treeWidget)
        HeaderUtil.nullifySaved("account_frame_header")
        self.refresh()
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        
    def connectTree(self):
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh)
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh)
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh)
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    
           
    def disconnectTree(self):
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh)
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh)
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh)
        self.disconnect(self.tarif_treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    

    def retranslateUi(self):
        self.tarif_treeWidget.clear()
        self.editTarifAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.editAccountAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))


    def addTarif(self):
        #print connection
        tarifframe = TarifFrame(connection=self.connection)
        tarifframe.exec_()
        self.refreshTree()
        self.refresh()
        
    
    def delTarif(self):
        tarif_id = self.getTarifId()
        if tarif_id>0 and QtGui.QMessageBox.question(self, u"Удалить тарифный план?" , u"Вы уверены, что хотите удалить тарифный план?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            accounts=self.connection.sql("""SELECT account.id 
                    FROM billservice_account as account
                    JOIN billservice_accounttarif as accounttarif ON accounttarif.id=(SELECT id FROM billservice_accounttarif WHERE account_id=account.id AND datetime<now() ORDER BY datetime DESC LIMIT 1 )
                    WHERE accounttarif.tarif_id=%d ORDER BY account.username ASC""" % tarif_id)
            if len(accounts)>0:
                tarif_type = str(self.tarif_treeWidget.currentItem().text(1)) 
                tarifs = self.connection.sql("SELECT id, name FROM billservice_tariff WHERE (id <> %d) AND (active=TRUE) AND (get_tariff_type(id)='%s');" % (tarif_id, tarif_type))
                child = ComboBoxDialog(items = tarifs, title = u"Выберите тарифный план, куда нужно перенести пользователей")
                
                if child.exec_()==1:
                    tarif = self.connection.get("SELECT * FROM billservice_tariff WHERE name='%s'" % unicode(child.comboBox.currentText()))
    
                    try:    
                        for account in accounts:
                            self.connection.create("INSERT INTO billservice_accounttarif (account_id, tarif_id, datetime) VALUES(%d, %d, now())" % (account.id, tarif.id))
                    
                    
                        #self.connection.create("UPDATE billservice_tariff SET deleted = True WHERE id=%s" % tarif_id)
                        self.connection.iddelete("billservice_tariff", tarif_id)
                        self.connection.commit()
                    except Exception, e:
                        print e
                        self.connection.rollback()
                        return
            else:
                try:
                    #self.connection.create("UPDATE billservice_tariff SET deleted = True WHERE id=%s" % tarif_id)
                    self.connection.iddelete("billservice_tariff", tarif_id)
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
        model = self.connection.get("SELECT * FROM billservice_tariff WHERE id=%s" % self.getTarifId())
        
        tarifframe = TarifFrame(connection=self.connection, model=model)
        #self.parent.workspace.addWindow(tarifframe)
        if tarifframe.exec_()==1:
            self.refreshTree()
            self.refresh()
            
        #print num

    def addframe(self):
        tarif_type = str(self.tarif_treeWidget.currentItem().text(1)) 
        self.connection.commit()
        #self.connection.flush()
        child = AddAccountFrame(connection=self.connection, ttype=tarif_type)
        #self.connection.commit()
        #child = AddAccountFrame(connection=self.connection)
        id = self.getTarifId()
        if child.exec_()==1 and id is not None:
            accounttarif = Object()
            accounttarif.account_id=child.model.id
            accounttarif.tarif_id=id
            accounttarif.datetime = datetime.datetime.now()
            print self.connection.create(accounttarif.save("billservice_accounttarif"))
            self.connection.commit()
            #time.sleep(5)
            #self.connection.flush()
            self.refresh(k="zomgnewacc")

    def makeTransation(self):
        id = self.getSelectedId()
        account = self.connection.get("SELECT * FROM billservice_account WHERE id=%d" % id)
        child = TransactionForm(connection=self.connection, account = account)
        if child.exec_()==1:
            tr = transaction(account_id=account.id, type_id = "MANUAL_TRANSACTION", approved = True, description = "", summ=child.result, bill=unicode(child.payed_document_edit.text()))
            try:
                
                self.connection.create(tr)
                #toex = tr.split(';')
                #print 
                #self.connection.listexec(toex[0]+ ';')
                #self.connection.listexec(tr)
                #self.connection.create(tr)
                #self.connection.create(toex[0]+ ';')
                self.connection.commit()
            except Exception, e:
                print "omg traf exception", e
                self.connection.rollback()
            
            #Если будем переделывать - здесь нужно списывать со счёта пользователя указанную сумму денег.
            self.refresh()
                                       
            
    def transactionReport(self):
        id = self.getSelectedId()
        account = self.connection.get("SELECT * FROM billservice_account WHERE id=%d" % id)
        tr = TransactionsReport(connection=self.connection, account = account)
        self.parent.workspace.addWindow(tr)
        tr.show()
            
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTarifId(self):
        return self.tarif_treeWidget.currentItem().id

    def delete(self):
        id=self.getSelectedId()
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить пользователя из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.accountActions(id, 'delete')
            
            #self.connection.delete("DELETE FROM billservice_accounttarif WHERE account_id=%d" % id)
            #self.connection.delete("DELETE FROM billservice_account WHERE id=%d" % id)
            self.connection.iddelete("billservice_account", id)
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
            model = self.connection.get("""SELECT account.*, nas.name as nas_name 
            FROM billservice_account as account
            JOIN nas_nas as nas ON  nas.id = account.nas_id
            WHERE account.id=%d""" % id)
        except Exception, e:
            print e
            return
        #print 'model', model
        tarif_type = str(self.tarif_treeWidget.currentItem().text(1)) 
        addf = AddAccountFrame(connection=self.connection,ttype=tarif_type, model=model)
        #addf.show()
        if addf.exec_()==1:
            self.connection.commit()
            self.refresh()

    def addrow(self, value, x, y, color=None, enabled=True):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if int(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
        
        elif not enabled:
            headerItem.setTextColor(QtGui.QColor('#FF0100'))
        
        if type(value)==BooleanType and value==True:
            if y==10:
                headerItem.setIcon(QtGui.QIcon("images/money_false.png"))
                headerItem.setToolTip(u"На счету недостаточно средств для активации пользователя в этом расчётном периоде")
            else:
                headerItem.setIcon(QtGui.QIcon("images/ok.png"))
            value=u""
        elif type(value)==BooleanType and value==False:
            if y==10:
                headerItem.setIcon(QtGui.QIcon("images/money_true.png"))
                headerItem.setToolTip(u"На счету достаточно средств")
            else:
                headerItem.setIcon(QtGui.QIcon("images/false.png"))
            value=u""
            
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/user.png"))
            

        headerItem.setText(unicode(value))
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
        tariffs = self.connection.sql("SELECT id, name, active, get_tariff_type(id) AS ttype FROM billservice_tariff ORDER BY ttype, name;")

        self.tableWidget.setColumnHidden(0, True)
        for tarif in tariffs:
            item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
            item.id = tarif.id
            item.setText(0, u"%s" % tarif.name)
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            #tariff_type = self.connection.get("SELECT get_tariff_type(%d);" % tarif.id)
            item.setText(1, tarif.ttype)
            if not tarif.active:
                item.setDisabled(True)
            
        self.connectTree()
        if curItem != -1:
            self.tarif_treeWidget.setCurrentItem(self.tarif_treeWidget.topLevelItem(curItem))
        
            
    def refresh(self, item=None, k=''):
        self.tableWidget.setSortingEnabled(False)
        #print item
        if item:
            id=item.id
        else:
            try:
                id=self.getTarifId()
            except:
                return
            
        #print "tarif_id=",id
        #print k

        #self.connection.commit()
        tarif = self.connection.foselect("billservice_tariff", id)

        '''accounts=self.connection.sql("""SELECT account.*, nas_nas.name as nas_name FROM billservice_account as account
        JOIN nas_nas ON nas_nas.id=account.nas_id
        JOIN billservice_accounttarif as accounttarif ON accounttarif.id=(SELECT id FROM billservice_accounttarif WHERE account_id=account.id AND datetime<now() ORDER BY datetime DESC LIMIT 1 )
        WHERE (accounttarif.tarif_id=%d) ORDER BY account.username ASC""" % tarif.id)'''
        '''accounts = self.connection.sql("""SELECT account.*, nas_nas.name as nas_name FROM billservice_account as account
        JOIN nas_nas ON nas_nas.id=account.nas_id
        WHERE (account.id IN (SELECT account_id FROM billservice_accounttarif WHERE tarif_id=%d)) ORDER BY account.username ASC""" % tarif.id)'''
        '''SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name FROM billservice_account AS acc WHERE (acc.id IN (SELECT account_id FROM billservice_accounttarif WHERE tarif_id=1)) ORDER BY acc.username ASC;'''
        accounts = self.connection.sql("""SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name FROM billservice_account AS acc WHERE (%d IN (SELECT tarif_id FROM billservice_accounttarif WHERE account_id=acc.id)) ORDER BY acc.username ASC;""" % tarif.id)
        self.connection.commit()
        #print accounts

        #print "after acc"
        self.tableWidget.setRowCount(len(accounts))
        
        
        i=0
        for a in accounts:
            
            self.addrow(a.id, i,0, enabled=a.status)
            self.addrow(a.username, i,1, enabled=a.status)
            self.addrow(a.ballance, i,2, color="red", enabled=a.status)
            self.addrow(a.credit, i,3, enabled=a.status)
            self.addrow(a.fullname, i,4, enabled=a.status)
            self.addrow(a.email, i,5, enabled=a.status)
            self.addrow(a.nas_name,i,6, enabled=a.status)
            self.addrow(a.vpn_ip_address, i,7, enabled=a.status)
            self.addrow(a.ipn_ip_address, i,8, enabled=a.status)
            self.addrow(a.suspended, i,9, enabled=a.status)
            #self.addrow(a.status, i,10, enabled=a.status)
            self.addrow(a.balance_blocked, i,10, enabled=a.status)
            self.addrow(a.disabled_by_limit,i,11, enabled=a.status)
            self.addrow(a.created.strftime(self.strftimeFormat), i,12, enabled=a.status)
            
            #self.tableWidget.setRowHeight(i, 17)
            
            if self.selected_account:
                if self.selected_account.id == a.id:
                    self.tableWidget.setRangeSelected(QtGui.QTableWidgetSelectionRange(i,0,i,12), True)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.delNodeLocalAction()
        self.tableWidget.setSortingEnabled(True)

    def accountEnable(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'enable'):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))

    def accountAdd(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'create'):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))

    def accountDelete(self):
        id=self.getSelectedId()
        if (id==0) and (QtGui.QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить аккаунт? \n После удаления станет недоступна статистика и информация о проводках.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.No):
            return

        if self.connection.accountActions(id, 'delete'):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok."))
            
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа недоступен, настроен неправильно или у пользователя не указан IP адрес."))


    def accountDisable(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'disable'):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Ok."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
    
    def saveHeader(self, *args):
        HeaderUtil.saveHeader("account_frame_header", self.tableWidget)
#---------------Local actions
    def delNodeLocalAction(self):
        #print self.tableWidget.currentRow()
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.transactionAction.setDisabled(True)
            self.transactionReportAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.transactionAction.setDisabled(False)
            self.transactionReportAction.setDisabled(False)


    def addNodeLocalAction(self):
        #print self.tableWidget.currentRow()
        #print self.tarif_treeWidget.currentItem()
        if self.tarif_treeWidget.currentItem() is None:
            self.addAction.setDisabled(True)
            self.delTarifAction.setDisabled(True)
        else:
            self.addAction.setDisabled(False)
            self.delTarifAction.setDisabled(False)
            


#---------------------------
