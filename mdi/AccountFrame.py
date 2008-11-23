#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui

import Pyro.core
import traceback
from ebsWindow import ebsTable_n_TreeWindow
from db import Object as Object
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil, SplitterUtil
from types import BooleanType
import copy

from randgen import nameGen, GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import CheckBoxDialog, ComboBoxDialog, SpeedEditDialog , TransactionForm
import time
from Reports import TransactionsReportEbs as TransactionsReport

from helpers import tableFormat
from helpers import transaction, makeHeaders
from helpers import Worker
from CustomForms import tableImageWidget
from CustomForms import CustomWidget

strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

                                           
        
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
        tarifs=self.connection.sql("SELECT id, name FROM billservice_tariff WHERE (active=TRUE) AND (get_tariff_type(id)='%s');" % self.ttype)
        self.connection.commit()
        for tarif in tarifs:
            self.tarif_edit.addItem(tarif.name, QtCore.QVariant(tarif.id))
        now=datetime.datetime.now()
        print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
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
        self.limit_tableWidget = tableFormat(self.limit_tableWidget, no_vsection_size=True)
        self.periodical_tableWidget = tableFormat(self.periodical_tableWidget)
        self.onetime_tableWidget = tableFormat(self.onetime_tableWidget)
        self.prepaid_tableWidget = tableFormat(self.prepaid_tableWidget, no_vsection_size=True)
        self.trafficcost_tableWidget = tableFormat(self.trafficcost_tableWidget, no_vsection_size=True)
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
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("Dialog", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("Dialog", "Фиксированный расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_type_edit.setText(QtGui.QApplication.translate("Dialog", "Начать при активации у пользователя данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("Dialog", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("Dialog", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
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
        self.checkBoxAllowExpressPay.setText(QtGui.QApplication.translate("Dialog", "Разрешить активацию карт экспресс-оплаты", None, QtGui.QApplication.UnicodeUTF8))
        
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
        columns=[u'Id', u'От МБ', u'До МБ', u'Направления', u'Вх', u'Исх', u'Время', u'Цена за МБ']
        
        makeHeaders(columns, self.trafficcost_tableWidget)
        self.trafficcost_tableWidget.setColumnHidden(1, True)     
        self.trafficcost_tableWidget.setColumnHidden(2, True)

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

        columns=[u'Id', u'Название', u'За последний', u'Период', u'Направления', u'Вх', u'Исх', u'МБ']
        
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
            item.id=id
            widget.setItem(x, y, item)


            
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
            #self.connection.iddelete("DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=%d" % id)
            #self.connection.delete("DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=%d" % id)
            self.connection.iddelete(id, "billservice_traffictransmitnodes")
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
        
        self.addrow(self.prepaid_tableWidget, True, current_row, 2, item_type='checkbox')
        self.addrow(self.prepaid_tableWidget, True, current_row, 3, item_type='checkbox')
        #self.addrow(self.prepaid_tableWidget, True, current_row, 4, item_type='checkbox')
    
    def delPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.currentRow()  
        id = self.getIdFromtable(self.prepaid_tableWidget, current_row)
        
        if id!=-1:
            d = Object()
            d.prepaidtraffic_id = id
            self.connection.delete(d, "billservice_prepaidtraffic_traffic_class")
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
        self.periodical_tableWidget.insertRow(self.periodical_tableWidget.rowCount())
    
    def delPeriodicalRow(self):
        current_row = self.periodical_tableWidget.currentRow()
        id = self.getIdFromtable(self.periodical_tableWidget, current_row)
        
        if id!=-1:
            self.connection.iddelete(id, "billservice_periodicalservice")
  
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
            
            child = CheckBoxDialog(all_items=self.connection.get_models("nas_trafficclass"), selected_items = models)
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
            try:
                models = self.limit_tableWidget.item(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=self.connection.get_models("nas_trafficclass"), selected_items = models)
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
            child = ComboBoxDialog(items=self.connection.get_models("billservice_settlementperiod"), selected_item = default_text )
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

        if x==3:
            try:
                models = self.trafficcost_tableWidget.item(y,x).models
            except Exception, e:
                print e
                models = []
            #print models
            child = CheckBoxDialog(all_items=self.connection.get_models("nas_trafficclass"), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setItem(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                self.trafficcost_tableWidget.resizeColumnsToContents()
                self.trafficcost_tableWidget.resizeRowsToContents()
                    
                
        if x==6:
            try:
                models = self.trafficcost_tableWidget.item(y,x).models
            except:
                models = []
            child = CheckBoxDialog(all_items=self.connection.get_models("billservice_timeperiod"), selected_items = models)
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




        access_types = ["PPTP", "PPPOE", "IPN"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = self.connection.get_models("billservice_timeperiod")
        
        for at in access_time:
            self.access_time_edit.addItem(unicode(at.name))


        
        if self.model:
            if not self.model.isnull('settlement_period_id'):
                self.sp_name_edit.setCurrentIndex(self.sp_name_edit.findText(settlement_period.name, QtCore.Qt.MatchCaseSensitive))
                
            self.tarif_status_edit.setCheckState(self.model.active == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.checkBoxAllowExpressPay.setChecked(bool(self.model.allow_express_pay))
            self.tarif_name_edit.setText(self.model.name)
            self.tarif_cost_edit.setText(unicode(self.model.cost))
            self.tarif_description_edit.setText(self.model.description)
            self.reset_tarif_cost_edit.setCheckState(self.model.reset_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.ps_null_ballance_checkout_edit.setCheckState(self.model.ps_null_ballance_checkout == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
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
            traffic_limites = self.connection.sql(""" SELECT trafficlimit.*, settlementperiod.name as settlement_period_name, settlementperiod.id as settlementperiod_id FROM billservice_trafficlimit as trafficlimit
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id=trafficlimit.settlement_period_id
            WHERE trafficlimit.tarif_id=%d
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
                    self.addrow(self.limit_tableWidget, node.settlement_period_name,i, 3, item_type='combobox', id=node.settlementperiod_id)
                    self.limit_tableWidget.setItem(i,4, CustomWidget(parent=self.limit_tableWidget, models=traffic_classes))
                    self.addrow(self.limit_tableWidget, unicode(node.size/(1024000)),i, 7)
                    
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
                        
                        self.addrow(self.prepaid_tableWidget, float(node.size)/(1024000),i, 4)
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
        self.trafficcost_tableWidget.resizeRowsToContents()
        self.trafficcost_tableWidget.resizeColumnsToContents()
        self.connection.commit()
        
        #self.trafficcost_tableWidget.resizeRowsToContents()

    def get_speed(self, speed):
        
        speed_in, speed_out = speed.split("/")
        if speed_in.endswith(u"k"):
            speed_in = int(speed_in[0:-1])*1024
        elif speed_in.endswith(u"M"):
            speed_in = int(speed_in[0:-1])*1024000
        else:
            speed_in=int(speed_in)
        
        if speed_out.endswith(u"k"):
            speed_out = int(speed_out[0:-1])*1024
        elif speed_out.endswith(u"M"):
            speed_out = int(speed_out[0:-1])*1024000
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
            QtGui.QMessageBox.warning(self, u"Ошибка", u"'Производить IPN действия' может быть указано только для VPN планов")
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
            

            model.access_parameters_id=self.connection.save(access_parameters, "billservice_accessparameters")
            
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
                self.connection.save(speed, "billservice_timespeed")
            
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
                    
                    if self.periodical_tableWidget.item(i, 1)==None or self.periodical_tableWidget.item(i, 2)==None or self.periodical_tableWidget.item(i, 3)==None or self.periodical_tableWidget.item(i, 4)==None:
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
                    
                    self.connection.save(periodical_service, "billservice_periodicalservice")    
                      
            elif self.periodical_services_checkbox.checkState()==0:
                    self.connection.iddelete(model.id, "billservice_periodicalservice") 
                
    
            #Лимиты
            if self.limit_tableWidget.rowCount()>0 and self.limites_checkbox.checkState()==2:
                for i in xrange(0, self.limit_tableWidget.rowCount()):
                    #print 2
                    id = self.getIdFromtable(self.limit_tableWidget, i)
                    #print self.limit_tableWidget.item(i, 1), self.limit_tableWidget.item(i, 3), self.limit_tableWidget.item(i, 8), self.limit_tableWidget.cellWidget(i, 4)
                    if (self.limit_tableWidget.cellWidget(i, 5).checkState()==self.limit_tableWidget.cellWidget(i, 6).checkState()==0) or self.limit_tableWidget.item(i, 1)==None or self.limit_tableWidget.item(i, 3)==None or self.limit_tableWidget.item(i, 7)==None or self.limit_tableWidget.item(i, 4)==None:
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
                        
                        limit = self.connection.get_model(id, "billservice_trafficlimit")
                    else:
                        limit = Object()
                    
                    limit.tarif_id = model.id
                    limit.name=unicode(self.limit_tableWidget.item(i, 1).text())
                    limit.settlement_period_id = self.limit_tableWidget.item(i, 3).id
                    limit.mode = self.limit_tableWidget.cellWidget(i,2).checkState()==2
                    limit.size=unicode(float(unicode(self.limit_tableWidget.item(i, 7).text()))*1024000)
    
                    limit.in_direction = self.limit_tableWidget.cellWidget(i,5).checkState()==2
                    limit.out_direction = self.limit_tableWidget.cellWidget(i,6).checkState()==2
                    #limit.transit_direction = self.limit_tableWidget.cellWidget(i,7).checkState()==2
                    
                    limit.id = self.connection.save(limit, "billservice_trafficlimit")
                    

                    
                    #print 'limit_id=', limit.id
                    
                    traffic_classes_for_limit = self.connection.sql("""SELECT class.* FROM nas_trafficclass as class
                    JOIN billservice_trafficlimit_traffic_class as tc ON tc.trafficclass_id = class.id
                    WHERE tc.trafficlimit_id=%d
                    """ % limit.id)
                    if traffic_classes_for_limit==None:
                        traffic_classes_for_limit=[]
                        
                    traffic_classes_for_limit= [x.id for x in traffic_classes_for_limit]
                    for cl in traffic_class_models:
                        if cl not in traffic_classes_for_limit:
                            tc = Object()
                            tc.trafficlimit_id = limit.id
                            tc.trafficclass_id = cl
                            self.connection.save(tc, "billservice_trafficlimit_traffic_class")
    
                    for cl in traffic_classes_for_limit:
                        if cl not in traffic_class_models:
                            d = Object()
                            d.trafficlimit_id = limit.id
                            d.trafficclass_id = cl
                            self.connection.delete(d, "billservice_trafficlimit_traffic_class")

            elif self.limites_checkbox.checkState()==0:
                d = Object()
                d.tarif_id = model.id
                self.connection.delete(d, "billservice_trafficlimit")

                                
            #Доступ по трафику 
            if self.trafficcost_tableWidget.rowCount()>0 and self.transmit_service_checkbox.checkState()==2:
                if not model.isnull('traffic_transmit_service_id'):
                    #print "'traffic_transmit_service'1"
                    traffic_transmit_service = self.connection.get_model(self.model.traffic_transmit_service_id, "billservice_traffictransmitservice")
                else:
                    #print 'traffic_transmit_service2'
                    traffic_transmit_service = Object()
                
                traffic_transmit_service.period_check='SP_START'
                traffic_transmit_service.reset_traffic=self.reset_traffic_edit.checkState()==2
                traffic_transmit_service.id = self.connection.save(traffic_transmit_service, "billservice_traffictransmitservice")
                
                    
     
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
                        transmit_node = self.connection.get_model(id, "billservice_traffictransmitnodes")
                    else:
                        transmit_node = Object()
                    
                    
                    transmit_node.traffic_transmit_service_id = traffic_transmit_service.id
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
                    
                    transmit_node.id = self.connection.save(transmit_node, "billservice_traffictransmitnodes")
                    
                        
                    traffic_classes_for_node = self.connection.sql("""SELECT trafficclass.* FROM nas_trafficclass as trafficclass 
                    
                    JOIN billservice_traffictransmitnodes_traffic_class as tc ON tc.trafficclass_id =  trafficclass.id
                    WHERE tc.traffictransmitnodes_id=%d""" % transmit_node.id)
                    
                    traffic_classes = [x.id for x in traffic_classes_for_node]
                    for cl in traffic_class_models:
                        if cl not in traffic_classes:
                            tc = Object()
                            tc.traffictransmitnodes_id = transmit_node.id
                            tc.trafficclass_id = cl
                            self.connection.save(tc, "billservice_traffictransmitnodes_traffic_class")
    
                    for cl in traffic_classes:
                        if cl not in traffic_class_models:
                            d = Object()
                            d.traffictransmitnodes_id = transmit_node.id
                            d.trafficclass_id = cl
                            self.connection.delete(d, "billservice_traffictransmitnodes_traffic_class")

                            
                    time_period_models = [x.id for x in self.trafficcost_tableWidget.item(i, 6).models]
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
                    
                    if self.prepaid_tableWidget.item(i, 1)==None or self.prepaid_tableWidget.item(i, 4)==None:
                        QtGui.QMessageBox.warning(self, u"Ошибка", u"Неверно указаны настройки для предоплаченного трафика")
                        self.connection.rollback()
                        return
                    elif self.prepaid_tableWidget.item(i, 1)!=None:
                        if self.prepaid_tableWidget.item(i, 1)==[]:
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
                    prepaid_node.in_direction = self.prepaid_tableWidget.cellWidget(i,2).checkState()==2
                    prepaid_node.out_direction = self.prepaid_tableWidget.cellWidget(i,3).checkState()==2
                    #prepaid_node.transit_direction = self.prepaid_tableWidget.cellWidget(i,4).checkState()==2
                    prepaid_node.size = unicode(float(self.prepaid_tableWidget.item(i,4).text())*1024000)


                    traffic_class_models = [x.id for x in self.prepaid_tableWidget.item(i, 1).models]
                    if len(traffic_class_models)==0:
                        return

                    prepaid_node.id = self.connection.save(prepaid_node,"billservice_prepaidtraffic")

                    traffic_classes_for_node = self.connection.sql("""SELECT trafficclass.* FROM nas_trafficclass as trafficclass 

                    JOIN billservice_prepaidtraffic_traffic_class as tc ON tc.trafficclass_id = trafficclass.id
                    WHERE tc.prepaidtraffic_id=%s""" % prepaid_node.id)

                    if traffic_classes_for_node==None:
                        traffic_classes_for_node=[]
                    traffic_classes_for_node = [x.id for x in traffic_classes_for_node]

                    for cl in traffic_class_models:
                        if cl not in traffic_classes_for_node:
                            tc = Object()
                            tc.prepaidtraffic_id = prepaid_node.id
                            tc.trafficclass_id = cl
                            self.connection.save(tc, "billservice_prepaidtraffic_traffic_class")

                    if traffic_classes_for_node==None:
                        traffic_classes_for_node=[]
                           
                    for cl in traffic_classes_for_node:
                        if cl not in traffic_class_models:
                            d = Object()
                            d.prepaidtraffic_id = prepaid_node.id
                            d.trafficclass_id = cl
                            self.connection.delete(d, "billservice_prepaidtraffic_traffic_class")

    
            elif (self.transmit_service_checkbox.checkState()==0 or self.trafficcost_tableWidget.rowCount()==0) and not model.isnull("traffic_transmit_service_id"):
                model.traffic_transmit_service_id=None
                self.connection.iddelete(model.traffic_transmit_service_id, "billservice_traffictransmitservice" )
                
                
                            
        
            
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
            
            
class AddAccountFrame(QtGui.QDialog):
    def __init__(self, connection,tarif_id, ttype, model=None, ipn_for_vpn=False):
        super(AddAccountFrame, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection
        self.ipn_for_vpn = ipn_for_vpn
        self.tarif_id = tarif_id

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

        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.ip_settings_groupBox)
        self.lineEdit_ipn_ip_address.setGeometry(QtCore.QRect(131,47,110,21))
        self.lineEdit_ipn_ip_address.setObjectName("lineEdit_ipn_ip_address")

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
        self.ipn_ip_address_label.setBuddy(self.lineEdit_ipn_ip_address)
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
        self.setTabOrder(self.assign_ipn_ip_from_dhcp_edit,self.lineEdit_ipn_ip_address)
        self.setTabOrder(self.lineEdit_ipn_ip_address,self.netmask_edit)
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
        self.dhcpActions()
        
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
        #self.ipn_mac_address_edit.setInputMask(QtGui.QApplication.translate("Dialog", ">HH:HH:HH:HH:HH:HH;0", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_ip_address_label_2.setText(QtGui.QApplication.translate("Dialog", "Маска подсети", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_ip_address_label.setText(QtGui.QApplication.translate("Dialog", "VPN Адрес", None, QtGui.QApplication.UnicodeUTF8))
        #self.netmask_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Индивидуальные настройки скорости для VPN", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]\n"
        "Примеры:\n"
        "128k  - rx-rate=128000, tx-rate=128000 (no bursts)\n"
        "64k/128M - rx-rate=64000, tx-rate=128000000\n"
        "64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s\n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s\n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]\n"
        "Примеры:\n"
        "128k  - rx-rate=128000, tx-rate=128000 (no bursts)\n"
        "64k/128M - rx-rate=64000, tx-rate=128000000\n"
        "64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s\n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s\n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_label.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Индивидуальные настройки скорости для IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setToolTip(QtGui.QApplication.translate("Dialog", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]\n"
        "Примеры:\n"
        "128k  - rx-rate=128000, tx-rate=128000 (no bursts)\n"
        "64k/128M - rx-rate=64000, tx-rate=128000000\n"
        "64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s\n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s\n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_speed_lineEdit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Формат:rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]\n"
        "Примеры:\n"
        "128k  - rx-rate=128000, tx-rate=128000 (no bursts)\n"
        "64k/128M - rx-rate=64000, tx-rate=128000000\n"
        "64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s\n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s\n"
        "", None, QtGui.QApplication.UnicodeUTF8))

        self.ipn_mac_address_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Укажите MAC адрес клиента, если хотите сделать к нему привязку аккаунта.\nПараметр обязателен, если вы выбрали опцию DHCP.", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_mac_address_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Укажите MAC адрес клиента, если хотите сделать к нему привязку аккаунта.\nПараметр обязателен, если вы выбрали опцию DHCP. Указывайте, если хотите привязать авторизацию аккаунта к этому адресу для PPPOE/IPN тарифных планов.", None, QtGui.QApplication.UnicodeUTF8))

        self.netmask_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Укажите сетевую маску, которую должен получить клиент по DHCP вместе с адресом.", None, QtGui.QApplication.UnicodeUTF8))
        self.netmask_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Укажите сетевую маску, которую должен получить клиент по DHCP вместе с адресом.", None, QtGui.QApplication.UnicodeUTF8))

        self.lineEdit_ipn_ip_address.setWhatsThis(QtGui.QApplication.translate("Dialog", "IP адрес клиента в сети.", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ipn_ip_address.setToolTip(QtGui.QApplication.translate("Dialog", "IP адрес клиента в сети. Указывайте, если хотите привязать авторизацию аккаунта к этому адресу для PPTP/IPN тарифных планов.", None, QtGui.QApplication.UnicodeUTF8))

        
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
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)
        
        self.lineEdit_ipn_ip_address.setValidator(self.ipValidator)
        self.vpn_ip_address_edit.setValidator(self.ipValidator)
        self.netmask_edit.setValidator(self.ipValidator)
        self.ipn_mac_address_edit.setValidator(self.macValidator)
        
        self.accounttarif_table.clear()
        self.accounttarif_table.setColumnCount(4)
        columns=[u'#', u'Тарифный план', u'Дата']


        makeHeaders(columns, self.accounttarif_table)
        
    def dhcpActions(self, newstate=0):
        
        if self.assign_ipn_ip_from_dhcp_edit.checkState()==2:
            self.netmask_edit.setDisabled(False)
            self.netmask_edit.setText("")
        elif self.assign_ipn_ip_from_dhcp_edit.checkState()==0:
            self.netmask_edit.setDisabled(True)
            self.netmask_edit.setText("")
            
            

    def getSelectedId(self):
        return int(self.accounttarif_table.item(self.accounttarif_table.currentRow(), 0).text())

    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection,ttype=self.ttype, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def del_accounttarif(self):
        i=self.getSelectedId()
        model = self.connection.get_model(i, "billservice_accounttarif")
        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_accounttarif")
            self.accountTarifRefresh()

    def edit_accounttarif(self):
        i=self.getSelectedId()
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
                #model = self.connection.get_model(self.model.id, "billservice_account")
                
                
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
                model.ipn_added = False
                model.disabled_by_limit = False
                
            model.username = unicode(self.username_edit.text())
            #print 1
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
            if self.lineEdit_ipn_ip_address.text():
                #print self.ipValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)
                if self.ipValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите IPN IP до конца."))
                    return
                try:
                    ipn_address_account_id = self.connection.get("SELECT id FROM billservice_account WHERE ipn_ip_address='%s'" % unicode(self.lineEdit_ipn_ip_address.text())).id
                    if ipn_address_account_id!=model.id:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
                        self.connection.rollback()
                        return  
                                          
                except Exception, ex:
                    print ex
                model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text())
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
                    vpn_address_account_id = self.connection.get("SELECT id FROM billservice_account WHERE vpn_ip_address='%s'" % unicode(self.vpn_ip_address_edit.text())).id
                    print "vpn_address_account_id", vpn_address_account_id
                    if vpn_address_account_id!=model.id:
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
    
            if self.ipn_mac_address_edit.text().isEmpty()==False:
                if self.macValidator.validate(self.ipn_mac_address_edit.text(), 0)[0]  == QtGui.QValidator.Acceptable:
                    cnt = self.connection.get("SELECT count(*) as cnt FROM billservice_account WHERE ipn_mac_address='%s' and id<>%s" % (unicode(self.ipn_mac_address_edit.text()).upper(), model.id)).cnt
                    if cnt>0 :
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
                        self.connection.rollback()
                        return
                    model.ipn_mac_address = unicode(self.ipn_mac_address_edit.text()).upper()
                else:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте MAC адрес."))
                    self.connection.rollback()
                    return
            else:
                model.ipn_mac_address=""
                
            model.nas_id = self.nas_comboBox.itemData(self.nas_comboBox.currentIndex()).toInt()[0]
    
            model.ballance = unicode(self.balance_edit.text()) or 0
            model.credit = unicode(self.credit_edit.text())
    
            model.assign_ipn_ip_from_dhcp = self.assign_ipn_ip_from_dhcp_edit.checkState() == QtCore.Qt.Checked
            model.suspended = self.suspended_edit.checkState() == QtCore.Qt.Checked
            model.status = self.status_edit.checkState() == QtCore.Qt.Checked
            
            if model.ipn_ip_address=="0.0.0.0" and self.ipn_for_vpn==True:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Для работы на этом тарифном плане у пользователя должен быть указан IPN IP."))
                return
            self.connection.rollback()
            if self.model:
                if model.ipn_ip_address!=self.model.ipn_ip_address:
                    """
                    Если изменили IPN IP адрес-значит нужно добавить новый адрес в лист доступа
                    """
                    model.ipn_status=False
                self.connection.save(model, "billservice_account")
            else:
                #print 123
                model.id=self.connection.save(model, "billservice_account")
                #print 321
                #Создаём AccounTarif
                #print 1111
                accounttarif = Object()
                accounttarif.account_id=model.id
                accounttarif.tarif_id=self.tarif_id
                accounttarif.datetime = datetime.datetime.now()
                self.connection.save(accounttarif,"billservice_accounttarif")
            self.connection.commit()
            
            #print "model.ipn_mac_address", model.ipn_mac_address
            
            

                #self.connection.rollback()
                #return
            #self.connection.commit()
            #self.model=model
        except Exception, e:
            import Pyro
            print ''.join(Pyro.util.getPyroTraceback(e))
            import sys, traceback
            traceback.print_exc()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при сохранении."))
            self.connection.rollback()
            return 
        QtGui.QDialog.accept(self)

    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)

    def fixtures(self):
        pools = []

        nasses = self.connection.get_models("nas_nas")
        self.connection.commit()
        i=0
        for nas in nasses:
            self.nas_comboBox.addItem(nas.name)
            self.nas_comboBox.setItemData(i, QtCore.QVariant(nas.id))
            if self.model:
                if nas.id==self.model.nas_id:
                    self.nas_comboBox.setCurrentIndex(i)
            
            i+=1
        
        if not self.model:
            self.add_accounttarif_toolButton.setDisabled(True)
            self.del_accounttarif_toolButton.setDisabled(True)
            self.balance_edit.setText(u"0")
            self.credit_edit.setText(u"0")

        if self.model:
            self.username_edit.setText(unicode(self.model.username))

            #self.nas_comboBox.setCurrentIndex(self.nas_comboBox.findText(self.model.nas_name, QtCore.Qt.MatchCaseSensitive))


            self.password_edit.setText(unicode(self.model.password))
            self.fullname_lineEdit.setText(unicode(self.model.fullname))
            self.email_lineEdit.setText(unicode(self.model.email))
            self.address_lineEdit.setText(unicode(self.model.address))
            self.netmask_edit.setText(unicode(self.model.netmask))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
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
                #self.accounttarif_table.setRowHeight(i, 17)
                self.accounttarif_table.setColumnHidden(0, True)
                i+=1
            #self.tabWidget.resizeColumnsToContents()
            self.connection.commit()



    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        headerItem.setText(unicode(value))
        self.accounttarif_table.setItem(x,y,headerItem)


        

class AccountWindow(QtGui.QMainWindow):
    def __init__(self, connection, tarif_id, ttype, model=None, ipn_for_vpn=False):
        super(AccountWindow, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection
        self.ipn_for_vpn = ipn_for_vpn
        self.tarif_id = tarif_id
        self.organization = None
        
        self.setObjectName("AccountWindow")
        self.resize(848, 628)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_general = QtGui.QWidget()
        self.tab_general.setObjectName("tab_general")
        self.groupBox_account_data = QtGui.QGroupBox(self.tab_general)
        self.groupBox_account_data.setGeometry(QtCore.QRect(9, 9, 381, 86))
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
        self.lineEdit_username.setMinimumSize(QtCore.QSize(0, 22))
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
        self.lineEdit_password.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout_3.addWidget(self.lineEdit_password, 1, 1, 1, 1)
        self.toolButton_generate_password = QtGui.QToolButton(self.groupBox_account_data)
        self.toolButton_generate_password.setObjectName("toolButton_generate_password")
        self.gridLayout_3.addWidget(self.toolButton_generate_password, 1, 2, 1, 1)
        self.groupBox_agreement = QtGui.QGroupBox(self.tab_general)
        self.groupBox_agreement.setGeometry(QtCore.QRect(396, 10, 421, 86))
        self.groupBox_agreement.setMinimumSize(QtCore.QSize(391, 86))
        self.groupBox_agreement.setMaximumSize(QtCore.QSize(3910, 84))
        self.groupBox_agreement.setObjectName("groupBox_agreement")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_agreement)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_agreement_date = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_date.setObjectName("label_agreement_date")
        self.gridLayout_4.addWidget(self.label_agreement_date, 0, 0, 1, 1)
        self.lineEdit_agreement_date = QtGui.QLineEdit(self.groupBox_agreement)
        self.lineEdit_agreement_date.setEnabled(False)
        self.lineEdit_agreement_date.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_agreement_date.setObjectName("lineEdit_agreement_date")
        self.gridLayout_4.addWidget(self.lineEdit_agreement_date, 0, 1, 1, 1)
        self.label_agreement_num = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_num.setObjectName("label_agreement_num")
        self.gridLayout_4.addWidget(self.label_agreement_num, 1, 0, 1, 1)
        self.lineEdit_agreement_num = QtGui.QLineEdit(self.groupBox_agreement)
        self.lineEdit_agreement_num.setEnabled(False)
        self.lineEdit_agreement_num.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_agreement_num.setObjectName("lineEdit_agreement_num")
        self.gridLayout_4.addWidget(self.lineEdit_agreement_num, 1, 1, 1, 1)
        self.toolButton_agreement_print = QtGui.QToolButton(self.groupBox_agreement)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_agreement_print.setIcon(icon)
        self.toolButton_agreement_print.setObjectName("toolButton_agreement_print")
        self.gridLayout_4.addWidget(self.toolButton_agreement_print, 1, 2, 1, 1)
        self.groupBox_account_info = QtGui.QGroupBox(self.tab_general)
        self.groupBox_account_info.setGeometry(QtCore.QRect(9, 101, 381, 226))
        self.groupBox_account_info.setMinimumSize(QtCore.QSize(381, 211))
        self.groupBox_account_info.setMaximumSize(QtCore.QSize(381, 16381))
        self.groupBox_account_info.setObjectName("groupBox_account_info")
        self.gridLayout_8 = QtGui.QGridLayout(self.groupBox_account_info)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_name = QtGui.QLabel(self.groupBox_account_info)
        self.label_name.setObjectName("label_name")
        self.gridLayout_8.addWidget(self.label_name, 0, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_name.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout_8.addWidget(self.lineEdit_name, 0, 1, 1, 1)
        self.label_address = QtGui.QLabel(self.groupBox_account_info)
        self.label_address.setObjectName("label_address")
        self.gridLayout_8.addWidget(self.label_address, 1, 0, 1, 1)
        self.lineEdit_email = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_email.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_email.setObjectName("lineEdit_email")
        self.gridLayout_8.addWidget(self.lineEdit_email, 1, 1, 1, 1)
        self.label_phone_h = QtGui.QLabel(self.groupBox_account_info)
        self.label_phone_h.setObjectName("label_phone_h")
        self.gridLayout_8.addWidget(self.label_phone_h, 2, 0, 1, 1)
        self.lineEdit_phone_h = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_phone_h.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_phone_h.setObjectName("lineEdit_phone_h")
        self.gridLayout_8.addWidget(self.lineEdit_phone_h, 2, 1, 1, 1)
        self.label_passport_n = QtGui.QLabel(self.groupBox_account_info)
        self.label_passport_n.setObjectName("label_passport_n")
        self.gridLayout_8.addWidget(self.label_passport_n, 4, 0, 1, 1)
        self.lineEdit_passport_n = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_passport_n.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_passport_n.setObjectName("lineEdit_passport_n")
        self.gridLayout_8.addWidget(self.lineEdit_passport_n, 4, 1, 1, 1)
        self.label_passport_give = QtGui.QLabel(self.groupBox_account_info)
        self.label_passport_give.setObjectName("label_passport_give")
        self.gridLayout_8.addWidget(self.label_passport_give, 5, 0, 1, 1)
        self.lineEdit_passport_given = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_passport_given.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_passport_given.setObjectName("lineEdit_passport_given")
        self.gridLayout_8.addWidget(self.lineEdit_passport_given, 5, 1, 1, 1)
        self.label_passport_date = QtGui.QLabel(self.groupBox_account_info)
        self.label_passport_date.setObjectName("label_passport_date")
        self.gridLayout_8.addWidget(self.label_passport_date, 6, 0, 1, 1)
        self.dateEdit_passport_date = QtGui.QDateEdit(self.groupBox_account_info)
        self.dateEdit_passport_date.setMinimumSize(QtCore.QSize(0, 22))
        self.dateEdit_passport_date.setObjectName("dateEdit_passport_date")
        self.gridLayout_8.addWidget(self.dateEdit_passport_date, 6, 1, 1, 1)
        self.lineEdit_phone_m = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_phone_m.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_phone_m.setObjectName("lineEdit_phone_m")
        self.gridLayout_8.addWidget(self.lineEdit_phone_m, 3, 1, 1, 1)
        self.label_phone_m = QtGui.QLabel(self.groupBox_account_info)
        self.label_phone_m.setObjectName("label_phone_m")
        self.gridLayout_8.addWidget(self.label_phone_m, 3, 0, 1, 1)
        self.groupBox_urdata = QtGui.QGroupBox(self.tab_general)
        self.groupBox_urdata.setGeometry(QtCore.QRect(396, 101, 421, 261))
        self.groupBox_urdata.setMinimumSize(QtCore.QSize(391, 241))
        self.groupBox_urdata.setMaximumSize(QtCore.QSize(16381, 261))
        self.groupBox_urdata.setCheckable(True)
        self.groupBox_urdata.setChecked(False)
        self.groupBox_urdata.setObjectName("groupBox_urdata")
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_urdata)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_organization = QtGui.QLabel(self.groupBox_urdata)
        self.label_organization.setObjectName("label_organization")
        self.gridLayout_7.addWidget(self.label_organization, 0, 0, 1, 1)
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_organization.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.gridLayout_7.addWidget(self.lineEdit_organization, 0, 1, 1, 4)
        self.label_bank = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank.setObjectName("label_bank")
        self.gridLayout_7.addWidget(self.label_bank, 10, 0, 1, 1)
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.gridLayout_7.addWidget(self.lineEdit_bank, 10, 1, 1, 1)
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_uraddress.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.gridLayout_7.addWidget(self.lineEdit_uraddress, 3, 1, 1, 4)
        self.label_uraddress = QtGui.QLabel(self.groupBox_urdata)
        self.label_uraddress.setObjectName("label_uraddress")
        self.gridLayout_7.addWidget(self.label_uraddress, 3, 0, 1, 1)
        self.lineEdit_urphone = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_urphone.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_urphone.setObjectName("lineEdit_urphone")
        self.gridLayout_7.addWidget(self.lineEdit_urphone, 4, 1, 1, 4)
        self.label_urphone = QtGui.QLabel(self.groupBox_urdata)
        self.label_urphone.setObjectName("label_urphone")
        self.gridLayout_7.addWidget(self.label_urphone, 4, 0, 1, 1)
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_fax.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.gridLayout_7.addWidget(self.lineEdit_fax, 5, 1, 1, 4)
        self.label_fax = QtGui.QLabel(self.groupBox_urdata)
        self.label_fax.setObjectName("label_fax")
        self.gridLayout_7.addWidget(self.label_fax, 5, 0, 1, 1)
        self.label_bank_code = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank_code.setObjectName("label_bank_code")
        self.gridLayout_7.addWidget(self.label_bank_code, 10, 3, 1, 1)
        self.lineEdit_bank_code = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank_code.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_bank_code.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_bank_code.setObjectName("lineEdit_bank_code")
        self.gridLayout_7.addWidget(self.lineEdit_bank_code, 10, 4, 1, 1)
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_rs.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.gridLayout_7.addWidget(self.lineEdit_rs, 11, 1, 1, 4)
        self.label_rs = QtGui.QLabel(self.groupBox_urdata)
        self.label_rs.setObjectName("label_rs")
        self.gridLayout_7.addWidget(self.label_rs, 11, 0, 1, 1)
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_unp.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.gridLayout_7.addWidget(self.lineEdit_unp, 1, 1, 1, 4)
        self.label_unp = QtGui.QLabel(self.groupBox_urdata)
        self.label_unp.setObjectName("label_unp")
        self.gridLayout_7.addWidget(self.label_unp, 1, 0, 1, 1)
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_okpo.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.gridLayout_7.addWidget(self.lineEdit_okpo, 2, 1, 1, 4)
        self.label_okpo = QtGui.QLabel(self.groupBox_urdata)
        self.label_okpo.setObjectName("label_okpo")
        self.gridLayout_7.addWidget(self.label_okpo, 2, 0, 1, 1)
        self.groupBox_address = QtGui.QGroupBox(self.tab_general)
        self.groupBox_address.setGeometry(QtCore.QRect(9, 330, 381, 211))
        self.groupBox_address.setMinimumSize(QtCore.QSize(381, 181))
        self.groupBox_address.setMaximumSize(QtCore.QSize(381, 211))
        self.groupBox_address.setObjectName("groupBox_address")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_address)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_city = QtGui.QLabel(self.groupBox_address)
        self.label_city.setObjectName("label_city")
        self.gridLayout_2.addWidget(self.label_city, 0, 0, 1, 1)
        self.lineEdit_city = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_city.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_city.setObjectName("lineEdit_city")
        self.gridLayout_2.addWidget(self.lineEdit_city, 0, 1, 1, 1)
        self.label_region = QtGui.QLabel(self.groupBox_address)
        self.label_region.setObjectName("label_region")
        self.gridLayout_2.addWidget(self.label_region, 1, 0, 1, 1)
        self.lineEdit_region = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_region.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_region.setObjectName("lineEdit_region")
        self.gridLayout_2.addWidget(self.lineEdit_region, 1, 1, 1, 3)
        self.label_street = QtGui.QLabel(self.groupBox_address)
        self.label_street.setObjectName("label_street")
        self.gridLayout_2.addWidget(self.label_street, 2, 0, 1, 1)
        self.lineEdit_street = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_street.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_street.setObjectName("lineEdit_street")
        self.gridLayout_2.addWidget(self.lineEdit_street, 2, 1, 1, 3)
        self.label_house = QtGui.QLabel(self.groupBox_address)
        self.label_house.setObjectName("label_house")
        self.gridLayout_2.addWidget(self.label_house, 3, 0, 1, 1)
        self.lineEdit_house = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_house.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_house.setObjectName("lineEdit_house")
        self.gridLayout_2.addWidget(self.lineEdit_house, 3, 1, 1, 1)
        self.label_house_bulk = QtGui.QLabel(self.groupBox_address)
        self.label_house_bulk.setObjectName("label_house_bulk")
        self.gridLayout_2.addWidget(self.label_house_bulk, 3, 2, 1, 1)
        self.lineEdit_house_bulk = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_house_bulk.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_house_bulk.setObjectName("lineEdit_house_bulk")
        self.gridLayout_2.addWidget(self.lineEdit_house_bulk, 3, 3, 1, 1)
        self.label_room = QtGui.QLabel(self.groupBox_address)
        self.label_room.setObjectName("label_room")
        self.gridLayout_2.addWidget(self.label_room, 5, 0, 1, 1)
        self.lineEdit_room = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_room.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_room.setObjectName("lineEdit_room")
        self.gridLayout_2.addWidget(self.lineEdit_room, 5, 1, 1, 3)
        self.label_20 = QtGui.QLabel(self.groupBox_address)
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 0, 2, 1, 1)
        self.lineEdit_postcode = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_postcode.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_postcode.setObjectName("lineEdit_postcode")
        self.gridLayout_2.addWidget(self.lineEdit_postcode, 0, 3, 1, 1)
        self.lineEdit_entrance = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_entrance.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_entrance.setObjectName("lineEdit_entrance")
        self.gridLayout_2.addWidget(self.lineEdit_entrance, 4, 1, 1, 3)
        self.label_entrance = QtGui.QLabel(self.groupBox_address)
        self.label_entrance.setObjectName("label_entrance")
        self.gridLayout_2.addWidget(self.label_entrance, 4, 0, 1, 1)
        self.groupBox_balance_info = QtGui.QGroupBox(self.tab_general)
        self.groupBox_balance_info.setGeometry(QtCore.QRect(396, 370, 421, 111))
        self.groupBox_balance_info.setMinimumSize(QtCore.QSize(391, 0))
        self.groupBox_balance_info.setMaximumSize(QtCore.QSize(3910, 1656465))
        self.groupBox_balance_info.setObjectName("groupBox_balance_info")
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_balance_info)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_balance = QtGui.QLabel(self.groupBox_balance_info)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_9.addWidget(self.label_balance, 0, 0, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_balance.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.lineEdit_balance.setDisabled(True)
        self.gridLayout_9.addWidget(self.lineEdit_balance, 0, 1, 1, 1)
        self.label_credit = QtGui.QLabel(self.groupBox_balance_info)
        self.label_credit.setObjectName("label_credit")
        self.gridLayout_9.addWidget(self.label_credit, 1, 0, 1, 1)
        self.lineEdit_credit = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_credit.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_credit.setObjectName("lineEdit_credit")
        self.gridLayout_9.addWidget(self.lineEdit_credit, 1, 1, 1, 1)
        self.checkBox_credit = QtGui.QCheckBox(self.groupBox_balance_info)
        self.checkBox_credit.setEnabled(False)
        self.checkBox_credit.setObjectName("checkBox_credit")
        self.gridLayout_9.addWidget(self.checkBox_credit, 2, 0, 1, 2)
        self.groupBox_status = QtGui.QGroupBox(self.tab_general)
        self.groupBox_status.setGeometry(QtCore.QRect(396, 490, 421, 51))
        self.groupBox_status.setMaximumSize(QtCore.QSize(16777215, 51))
        self.groupBox_status.setObjectName("groupBox_status")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_status)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox_active = QtGui.QCheckBox(self.groupBox_status)
        self.checkBox_active.setObjectName("checkBox_active")
        self.horizontalLayout.addWidget(self.checkBox_active)
        self.checkBox_suspended = QtGui.QCheckBox(self.groupBox_status)
        self.checkBox_suspended.setObjectName("checkBox_suspended")
        self.horizontalLayout.addWidget(self.checkBox_suspended)
        self.tabWidget.addTab(self.tab_general, "")
        self.tab_network_settings = QtGui.QWidget()
        self.tab_network_settings.setObjectName("tab_network_settings")
        self.gridLayout_17 = QtGui.QGridLayout(self.tab_network_settings)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.groupBox_nas = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_nas.setMinimumSize(QtCore.QSize(0, 51))
        self.groupBox_nas.setMaximumSize(QtCore.QSize(791, 51))
        self.groupBox_nas.setObjectName("groupBox_nas")
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_nas)
        self.comboBox_nas.setGeometry(QtCore.QRect(190, 20, 401, 22))
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.label_nas = QtGui.QLabel(self.groupBox_nas)
        self.label_nas.setGeometry(QtCore.QRect(10, 20, 171, 21))
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_17.addWidget(self.groupBox_nas, 0, 0, 1, 1)
        self.groupBox_dublicate_actions = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_dublicate_actions.setEnabled(False)
        self.groupBox_dublicate_actions.setMinimumSize(QtCore.QSize(191, 0))
        self.groupBox_dublicate_actions.setMaximumSize(QtCore.QSize(191, 481))
        self.groupBox_dublicate_actions.setObjectName("groupBox_dublicate_actions")
        self.gridLayout_12 = QtGui.QGridLayout(self.groupBox_dublicate_actions)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.listWidget_nasses = QtGui.QListWidget(self.groupBox_dublicate_actions)
        self.listWidget_nasses.setEnabled(False)
        self.listWidget_nasses.setObjectName("listWidget_nasses")
        self.gridLayout_12.addWidget(self.listWidget_nasses, 0, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_dublicate_actions, 0, 1, 4, 1)
        self.groupBox_ipn = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_ipn.setMinimumSize(QtCore.QSize(591, 0))
        self.groupBox_ipn.setMaximumSize(QtCore.QSize(597000, 151))
        self.groupBox_ipn.setObjectName("groupBox_ipn")
        self.gridLayout_15 = QtGui.QGridLayout(self.groupBox_ipn)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.label_ipn_ip_address = QtGui.QLabel(self.groupBox_ipn)
        self.label_ipn_ip_address.setObjectName("label_ipn_ip_address")
        self.gridLayout_15.addWidget(self.label_ipn_ip_address, 0, 0, 1, 1)
        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_ipn_ip_address.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_ipn_ip_address.setObjectName("lineEdit_ipn_ip_address")
        self.gridLayout_15.addWidget(self.lineEdit_ipn_ip_address, 0, 1, 1, 1)
        self.toolButton_get_ipn_from_pool = QtGui.QToolButton(self.groupBox_ipn)
        self.toolButton_get_ipn_from_pool.setEnabled(False)
        self.toolButton_get_ipn_from_pool.setObjectName("toolButton_get_ipn_from_pool")
        self.gridLayout_15.addWidget(self.toolButton_get_ipn_from_pool, 0, 2, 1, 1)
        self.comboBox_ipn_pool = QtGui.QComboBox(self.groupBox_ipn)
        self.comboBox_ipn_pool.setEnabled(False)
        self.comboBox_ipn_pool.setMinimumSize(QtCore.QSize(250, 22))
        self.comboBox_ipn_pool.setObjectName("comboBox_ipn_pool")
        self.gridLayout_15.addWidget(self.comboBox_ipn_pool, 0, 3, 1, 1)
        self.label_ipn_ip_mask = QtGui.QLabel(self.groupBox_ipn)
        self.label_ipn_ip_mask.setObjectName("label_ipn_ip_mask")
        self.gridLayout_15.addWidget(self.label_ipn_ip_mask, 1, 0, 1, 1)
        self.lineEdit_ipn_ip_mask = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_ipn_ip_mask.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_ipn_ip_mask.setObjectName("lineEdit_ipn_ip_mask")
        self.gridLayout_15.addWidget(self.lineEdit_ipn_ip_mask, 1, 1, 1, 1)
        self.label_ipn_mac_address = QtGui.QLabel(self.groupBox_ipn)
        self.label_ipn_mac_address.setObjectName("label_ipn_mac_address")
        self.gridLayout_15.addWidget(self.label_ipn_mac_address, 2, 0, 1, 1)
        self.lineEdit_ipn_mac_address = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_ipn_mac_address.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_ipn_mac_address.setObjectName("lineEdit_ipn_mac_address")
        self.gridLayout_15.addWidget(self.lineEdit_ipn_mac_address, 2, 1, 1, 1)
        self.lineEdit_vlan = QtGui.QLineEdit(self.groupBox_ipn)
        self.lineEdit_vlan.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_vlan.setObjectName("lineEdit_vlan")
        self.gridLayout_15.addWidget(self.lineEdit_vlan, 1, 3, 1, 1)
        self.label_vlan = QtGui.QLabel(self.groupBox_ipn)
        self.label_vlan.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_vlan.setObjectName("label_vlan")
        self.gridLayout_15.addWidget(self.label_vlan, 1, 2, 1, 1)
        self.checkBox_assign_ipn_ip_from_dhcp = QtGui.QCheckBox(self.groupBox_ipn)
        self.checkBox_assign_ipn_ip_from_dhcp.setObjectName("checkBox_assign_ipn_ip_from_dhcp")
        self.gridLayout_15.addWidget(self.checkBox_assign_ipn_ip_from_dhcp, 2, 3, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_ipn, 1, 0, 1, 1)
        self.groupBox_vpn = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_vpn.setMinimumSize(QtCore.QSize(0, 51))
        self.groupBox_vpn.setMaximumSize(QtCore.QSize(16777215, 51))
        self.groupBox_vpn.setObjectName("groupBox_vpn")
        self.comboBox_vpn_pool = QtGui.QComboBox(self.groupBox_vpn)
        self.comboBox_vpn_pool.setEnabled(False)
        self.comboBox_vpn_pool.setGeometry(QtCore.QRect(350, 20, 250, 22))
        self.comboBox_vpn_pool.setMinimumSize(QtCore.QSize(250, 22))
        self.comboBox_vpn_pool.setObjectName("comboBox_vpn_pool")
        self.lineEdit_vpn_ip_address = QtGui.QLineEdit(self.groupBox_vpn)
        self.lineEdit_vpn_ip_address.setGeometry(QtCore.QRect(110, 20, 131, 22))
        self.lineEdit_vpn_ip_address.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_vpn_ip_address.setFrame(True)
        self.lineEdit_vpn_ip_address.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit_vpn_ip_address.setObjectName("lineEdit_vpn_ip_address")
        self.label_vpn_ip_address = QtGui.QLabel(self.groupBox_vpn)
        self.label_vpn_ip_address.setGeometry(QtCore.QRect(10, 20, 71, 20))
        self.label_vpn_ip_address.setObjectName("label_vpn_ip_address")
        self.toolButton_get_vpn_from_pool = QtGui.QToolButton(self.groupBox_vpn)
        self.toolButton_get_vpn_from_pool.setEnabled(False)
        self.toolButton_get_vpn_from_pool.setGeometry(QtCore.QRect(250, 20, 91, 20))
        self.toolButton_get_vpn_from_pool.setObjectName("toolButton_get_vpn_from_pool")
        self.gridLayout_17.addWidget(self.groupBox_vpn, 2, 0, 1, 1)
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
        self.checkBox_assign_dhcp_null = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_assign_dhcp_null.setObjectName("checkBox_assign_dhcp_null")
        self.gridLayout_16.addWidget(self.checkBox_assign_dhcp_null, 2, 0, 1, 1)
        self.checkBox_assign_dhcp_block = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_assign_dhcp_block.setObjectName("checkBox_assign_dhcp_block")
        self.gridLayout_16.addWidget(self.checkBox_assign_dhcp_block, 3, 0, 1, 1)
        self.checkBox_allow_vpn_null = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_vpn_null.setObjectName("checkBox_allow_vpn_null")
        self.gridLayout_16.addWidget(self.checkBox_allow_vpn_null, 4, 0, 1, 1)
        self.checkBox_allow_vpn_block = QtGui.QCheckBox(self.groupBox_accessparameters)
        self.checkBox_allow_vpn_block.setObjectName("checkBox_allow_vpn_block")
        self.gridLayout_16.addWidget(self.checkBox_allow_vpn_block, 5, 0, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_accessparameters, 3, 0, 1, 1)
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
        self.gridLayout_17.addWidget(self.groupBox_vpn_speed, 4, 0, 1, 2)
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
        self.gridLayout_17.addWidget(self.groupBox_ipn_speed, 5, 0, 1, 2)
        self.tabWidget.addTab(self.tab_network_settings, "")
        self.tab_suspended = QtGui.QWidget()
        self.tab_suspended.setObjectName("tab_suspended")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_suspended)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.tableWidget_suspended = QtGui.QTableWidget(self.tab_suspended)
        self.tableWidget_suspended.setObjectName("tableWidget_suspended")
        self.tableWidget_suspended = tableFormat(self.tableWidget_suspended)
        
        self.gridLayout_5.addWidget(self.tableWidget_suspended, 0, 0, 1, 1)
        #self.tabWidget.addTab(self.tab_suspended, "")
        self.tab_downtime = QtGui.QWidget()
        self.tab_downtime.setObjectName("tab_downtime")
        self.gridLayout_13 = QtGui.QGridLayout(self.tab_downtime)
        self.gridLayout_13.setObjectName("gridLayout_13")
        
        self.tableWidget_downtime = QtGui.QTableWidget(self.tab_downtime)
        self.tableWidget_downtime.setObjectName("tableWidget_downtime")
        self.tableWidget_downtime = tableFormat(self.tableWidget_downtime)

        self.gridLayout_13.addWidget(self.tableWidget_downtime, 0, 0, 1, 1)
        #self.tabWidget.addTab(self.tab_downtime, "")
        self.tab_tarifs = QtGui.QWidget()
        self.tab_tarifs.setObjectName("tab_tarifs")
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_tarifs)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.tableWidget_accounttarif = QtGui.QTableWidget(self.tab_tarifs)
        self.tableWidget_accounttarif.setObjectName("tableWidget_accounttarif")
        self.tableWidget_accounttarif = tableFormat(self.tableWidget_accounttarif)
        
        self.gridLayout_6.addWidget(self.tableWidget_accounttarif, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_tarifs, "")
        self.tab_documents = QtGui.QWidget()
        self.tab_documents.setObjectName("tab_documents")
        self.gridLayout_18 = QtGui.QGridLayout(self.tab_documents)
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.tableWidget_documents = QtGui.QTableWidget(self.tab_documents)
        self.tableWidget_documents.setObjectName("tableWidget_documents")
        self.tableWidget_documents = tableFormat(self.tableWidget_documents)

        self.gridLayout_18.addWidget(self.tableWidget_documents, 0, 0, 1, 1)
        #self.tabWidget.addTab(self.tab_documents, "")
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


        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        
        self.connect(self.toolButton_generate_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_generate_password,QtCore.SIGNAL("clicked()"),self.generate_password)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        self.connect(self.checkBox_assign_ipn_ip_from_dhcp, QtCore.SIGNAL("stateChanged(int)"), self.dhcpActions)
        self.connect(self.tableWidget_accounttarif, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)
        
        self.connect(self.actionAdd, QtCore.SIGNAL("triggered()"), self.add_accounttarif)
        self.connect(self.actionDel, QtCore.SIGNAL("triggered()"), self.del_accounttarif)
        
        self.fixtures()
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
        self.groupBox_account_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о пользователе", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("MainWindow", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_address.setText(QtGui.QApplication.translate("MainWindow", "Email", None, QtGui.QApplication.UnicodeUTF8))
        self.label_phone_h.setText(QtGui.QApplication.translate("MainWindow", "Телефон дом.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport_n.setText(QtGui.QApplication.translate("MainWindow", "Паспорт №", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport_give.setText(QtGui.QApplication.translate("MainWindow", "Кем выдан", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport_date.setText(QtGui.QApplication.translate("MainWindow", "Когда выдан", None, QtGui.QApplication.UnicodeUTF8))
        self.label_phone_m.setText(QtGui.QApplication.translate("MainWindow", "Телефон моб.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_urdata.setTitle(QtGui.QApplication.translate("MainWindow", "Юридическое лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("MainWindow", "Расчётный счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("MainWindow", "Банк, код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_urphone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_address.setTitle(QtGui.QApplication.translate("MainWindow", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_region.setText(QtGui.QApplication.translate("MainWindow", "Район", None, QtGui.QApplication.UnicodeUTF8))
        self.label_street.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house.setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house_bulk.setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
        self.label_room.setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("MainWindow", "Индекс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_entrance.setText(QtGui.QApplication.translate("MainWindow", "Подъезд", None, QtGui.QApplication.UnicodeUTF8))
        #self.groupBox_manager.setTitle(QtGui.QApplication.translate("MainWindow", "Работа с клиентом", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_manager.setText(QtGui.QApplication.translate("MainWindow", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_balance_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("MainWindow", "Текущий баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("MainWindow", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_credit.setText(QtGui.QApplication.translate("MainWindow", "Работать в кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_general), QtGui.QApplication.translate("MainWindow", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_nas.setTitle(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("MainWindow", "Идентификатор сервера доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ipn.setTitle(QtGui.QApplication.translate("MainWindow", "IPN IP Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_ip_address.setText(QtGui.QApplication.translate("MainWindow", "Текущий IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank_code.setText(QtGui.QApplication.translate("MainWindow", "Код", None, QtGui.QApplication.UnicodeUTF8))
        
        self.toolButton_get_ipn_from_pool.setText(QtGui.QApplication.translate("MainWindow", "Выдать из пула", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_ip_mask.setText(QtGui.QApplication.translate("MainWindow", "Маска подсети", None, QtGui.QApplication.UnicodeUTF8))
        
        self.label_ipn_mac_address.setText(QtGui.QApplication.translate("MainWindow", "Аппаратный адрес", None, QtGui.QApplication.UnicodeUTF8))
        
        self.label_vlan.setText(QtGui.QApplication.translate("MainWindow", "VLAN ID", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_assign_ipn_ip_from_dhcp.setText(QtGui.QApplication.translate("MainWindow", "Выдавать IP адрес с помощью DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_dublicate_actions.setTitle(QtGui.QApplication.translate("MainWindow", "Дублировать IPN действия на", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_vpn.setTitle(QtGui.QApplication.translate("MainWindow", "VPN IP Адрес", None, QtGui.QApplication.UnicodeUTF8))

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

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_downtime), QtGui.QApplication.translate("MainWindow", "Периоды простоя", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tarifs), QtGui.QApplication.translate("MainWindow", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_documents), QtGui.QApplication.translate("MainWindow", "Документы", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setText(QtGui.QApplication.translate("MainWindow", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDel.setText(QtGui.QApplication.translate("MainWindow", "del", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_status.setTitle(QtGui.QApplication.translate("MainWindow", "Статус аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_active.setText(QtGui.QApplication.translate("MainWindow", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_suspended.setText(QtGui.QApplication.translate("MainWindow", "Отключить ПУ", None, QtGui.QApplication.UnicodeUTF8))
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)
        
        self.lineEdit_ipn_ip_address.setValidator(self.ipValidator)
        self.lineEdit_vpn_ip_address.setValidator(self.ipValidator)
        self.lineEdit_ipn_ip_mask.setValidator(self.ipValidator)
        self.lineEdit_ipn_mac_address.setValidator(self.macValidator)
        
        self.tableWidget_accounttarif.clear()

        columns = ["#", u"С",u"По"]
        makeHeaders(columns, self.tableWidget_suspended)
        
        columns=[u'#', u'Тарифный план', u'Дата']

        makeHeaders(columns, self.tableWidget_accounttarif)

        columns = ["#", u"С", u"По", u"Списано"]
        makeHeaders(columns, self.tableWidget_downtime)
                
        columns = ["#", u'Тип документа', u"Дата", u"Подписан", u"Отослан по E-mail"]
        makeHeaders(columns, self.tableWidget_documents)
        
        #self.tabWidget.removeTab(self.tab_documents)
        #self.tabWidget.removeTab(self.tab_downtime)
        #self.tabWidget.removeTab(self.tab_suspended)
        
        
    def generate_login(self):
        self.lineEdit_username.setText(nameGen())

    def generate_password(self):
        self.lineEdit_password.setText(GenPasswd2())
        
    def dhcpActions(self, newstate=0):
        
        if self.checkBox_assign_ipn_ip_from_dhcp.checkState()==2:
            self.lineEdit_ipn_ip_mask.setDisabled(False)
            self.lineEdit_ipn_ip_mask.setText("")
        elif self.checkBox_assign_ipn_ip_from_dhcp.checkState()==0:
            self.lineEdit_ipn_ip_mask.setDisabled(True)
            self.lineEdit_ipn_ip_mask.setText("")
            
    def fixtures(self):


        pools = []

        nasses = self.connection.get_models("nas_nas")
        self.connection.commit()
        i=0
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name)
            self.comboBox_nas.setItemData(i, QtCore.QVariant(nas.id))
            if self.model:
                if nas.id==self.model.nas_id:
                    self.comboBox_nas.setCurrentIndex(i)
            
            i+=1
        
        if not self.model:
            #self.add_accounttarif_toolButton.setDisabled(True)
            #self.del_accounttarif_toolButton.setDisabled(True)
            self.lineEdit_balance.setText(u"0")
            self.lineEdit_credit.setText(u"0")

        if self.model:
            self.lineEdit_agreement_num.setText("%s" % self.model.id)
            self.lineEdit_agreement_date.setText(unicode(self.model.created.strftime(strftimeFormat)))
            
            self.checkBox_suspended.setChecked(self.model.suspended)
            self.checkBox_active.setChecked(self.model.status)

            self.lineEdit_username.setText(unicode(self.model.username))
            self.lineEdit_password.setText(unicode(self.model.password))
            
            
            self.lineEdit_name.setText(unicode(self.model.fullname))
            
            
            self.lineEdit_email.setText(unicode(self.model.email))
            
            #self.address_lineEdit.setText(unicode(self.model.address))
            self.lineEdit_city.setText(unicode(self.model.city))
            self.lineEdit_postcode.setText(unicode(self.model.postcode))
            self.lineEdit_region.setText(unicode(self.model.region))
            self.lineEdit_street.setText(unicode(self.model.street))
            self.lineEdit_house.setText(unicode(self.model.house))
            self.lineEdit_house_bulk.setText(unicode(self.model.house_bulk))
            self.lineEdit_entrance.setText(unicode(self.model.entrance))
            self.lineEdit_room.setText(unicode(self.model.room))
            
            #passport
            self.lineEdit_passport_n.setText(u"%s" % self.model.passport)
            self.lineEdit_passport_given.setText(u"%s" % self.model.passport_given)
            try:
                self.dateEdit_passport_date.setDate(QtCore.QDate(self.model.passport_date.year,self.model.passport_date.month, self.model.passport_date.day))
            except:
                print "passport date error"
            
            self.lineEdit_ipn_ip_mask.setText(unicode(self.model.netmask))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
            self.lineEdit_vpn_ip_address.setText(unicode(self.model.vpn_ip_address))
            self.lineEdit_vlan.setText(unicode(self.model.vlan))
            
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
                self.groupBox_urdata.setChecked(False)
            self.accountTarifRefresh()

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
                model.created = datetime.datetime.now()
                #model.user_id=1
                model.ipn_status = False
                model.ipn_added = False
                model.disabled_by_limit = False
                
            model.username = unicode(self.lineEdit_username.text())
            #print 1
            model.password = unicode(self.lineEdit_password.text())
            model.fullname = unicode(self.lineEdit_name.text())
            model.email = unicode(self.lineEdit_email.text())
            
            model.fullname = unicode(self.lineEdit_name.text())
            
            model.city = unicode(self.lineEdit_city.text())
            model.postcode = unicode(self.lineEdit_postcode.text())
            
            model.region = unicode(self.lineEdit_region.text())
            model.street = unicode(self.lineEdit_street.text())
            model.house = unicode(self.lineEdit_house.text())
            model.house_bulk = unicode(self.lineEdit_house_bulk.text())
            model.entrance = unicode(self.lineEdit_entrance.text())
            model.room = unicode(self.lineEdit_room.text())
            
            #passport
            passport = unicode(self.lineEdit_passport_n.text())
            passport_given = unicode(self.lineEdit_passport_given.text())
            passport_date = self.dateEdit_passport_date.date().toPyDate()
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
                
            elif self.ttype == 'IPN':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь создан на IPN тарифном плане. \n IPN IP должен быть введён до конца."))
                return
            else:
                model.ipn_ip_address = '0.0.0.0'
                

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
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь создан на VPN тарифном плане. \n VPN IP должен быть введён до конца."))
                return
            else:
                model.vpn_ip_address = '0.0.0.0'
              
            model.netmask = '0.0.0.0'
            if self.lineEdit_ipn_ip_mask.isEnabled():
                if self.lineEdit_ipn_ip_mask.text():
                    if self.ipValidator.validate(self.lineEdit_ipn_ip_mask.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Маска указана неверно."))
                        self.connection.rollback()
                        return
                    model.netmask = unicode(self.lineEdit_ipn_ip_mask.text())
                
                
            #model.netmask = unicode(self.netmask_edit.text())
            if ((model.ipn_ip_address == '0.0.0.0') and (model.vpn_ip_address == '0.0.0.0')):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Должен быть введён хотя бы один из адресов"))
                self.connection.rollback()
                return
    
            if self.lineEdit_ipn_mac_address.text().isEmpty()==False:
                if self.macValidator.validate(self.ipn_mac_address_edit.text(), 0)[0]  == QtGui.QValidator.Acceptable:
                    cnt = self.connection.get("SELECT count(*) as cnt FROM billservice_account WHERE ipn_mac_address='%s' and id<>%s" % (unicode(self.lineEdit_ipn_mac_address.text()).upper(), model.id)).cnt
                    if cnt>0 :
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
                        self.connection.rollback()
                        return
                    model.ipn_mac_address = unicode(self.lineEdit_ipn_mac_address.text()).upper()
                else:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте MAC адрес."))
                    self.connection.rollback()
                    return
            else:
                model.ipn_mac_address=""
                
            model.nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
            model.vlan = unicode(self.lineEdit_vlan.text()) or 0
            
            model.ballance = unicode(self.lineEdit_balance.text()) or 0
            model.credit = unicode(self.lineEdit_credit.text()) or 0
    
            model.assign_ipn_ip_from_dhcp = self.checkBox_assign_ipn_ip_from_dhcp.isChecked()
            model.suspended = self.checkBox_suspended.isChecked()
            model.status = self.checkBox_active.isChecked()
            
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
                accounttarif.datetime = datetime.datetime.now()
                self.connection.save(accounttarif,"billservice_accounttarif")

            if self.groupBox_urdata.isChecked():
                if unicode(self.lineEdit_organization.text())=="" or unicode(self.lineEdit_bank.text())=="":
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указаны реквизиты юридического лица."))
                    return
                if self.organization:
                    org = self.organization
                    bank = self.connection.get_model(org.bank_id, "billservice_bankdata")
                else:
                    org = Object()
                    bank = Object()
                
                bank.bank = unicode(self.lineEdit_bank.text())
                bank.bankcode = unicode(self.lineEdit_bank_code.text())
                bank.rs = self.lineEdit_rs.text()
                bank.currency = ''
                bank.id = self.connection.save(bank, "billservice_bankdata")
                
                org.name = unicode(self.lineEdit_organization.text())
                org.uraddress = unicode(self.lineEdit_uraddress.text())
                org.phone = unicode(self.lineEdit_urphone.text())
                org.fax = unicode(self.lineEdit_fax.text())
                org.okpo = unicode(self.lineEdit_okpo.text())
                org.unp = unicode(self.lineEdit_unp.text())
                org.account_id = model.id
                org.bank_id = bank.id
                self.connection.save(org, "billservice_organization")
                print "save org.data"
            else:
                if self.organization:
                    self.connection.iddelete(self.organization.id, "billservice_organization")    
            
            
            self.connection.commit()
            
            self.model = model
            self.emit(QtCore.SIGNAL("refresh()"))
        except Exception, e:
            import sys, traceback
            traceback.print_exc()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при сохранении."))
            self.connection.rollback()
            return
        
    def accountTarifRefresh(self):
        if self.model:
            ac=self.connection.sql("""SELECT accounttarif.*, tarif.name as tarif_name FROM billservice_accounttarif as accounttarif 
            JOIN billservice_tariff as tarif ON tarif.id=accounttarif.tarif_id
            WHERE account_id=%d ORDER BY datetime ASC""" % self.model.id)
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



    def addrow(self, widget, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if y==0:
            headerItem.id=value
        headerItem.setText(unicode(value))
        widget.setItem(x,y,headerItem)
        
    
    def getSelectedId(self, table):
        return int(table.item(table.currentRow(), 0).text())

    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection,ttype=self.ttype, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def del_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)
        model = self.connection.get_model(i, "billservice_accounttarif")
        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_accounttarif")
            self.accountTarifRefresh()

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
    
class AccountsMdiEbs(ebsTable_n_TreeWindow):
    def __init__(self, connection, parent, selected_account=None):
        columns=[u'id', u'Имя пользователя', u'Баланс', u'Кредит', u'Имя', u'E-mail', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u"MAC адрес", u'Без ПУ', u'', u'Превышен лимит', u"Дата создания"]
        initargs = {"setname":"account_frame", "objname":"AccountEbsMDI", "winsize":(0,0,1100,600), "wintitle":"Пользователи", "tablecolumns":columns, "spltsize":(0,0,391,411), "treeheader":"Тарифы", "tbiconsize":(18,18)}
        self.parent = parent
        self.thread = Worker()
        self.selected_account = selected_account
        super(AccountsMdiEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tarif_treeWidget = self.treeWidget
        
    def ebsPostInit(self, initargs):
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemClicked(QTableWidgetItem *)"), self.delNodeLocalAction)
        self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.refreshTree)

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
                 ("editTarifAction", "Редактировать", "images/edit.png", self.editTarif)\
                 ("editAccountAction", "Редактировать", "images/configure.png", self.editframe)\
                ]
        

        objDict = {self.treeWidget:["editTarifAction", "addTarifAction", "delAction", "configureAction"], \
                   self.tableWidget:["editAction", "addAction", "delAction", "configureAction"], \
                   self.toolBar:["addAction", "delAction", "configureAction"]\
                  }
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
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar.addAction(self.addTarifAction)
        self.toolBar.addAction(self.delTarifAction)
        self.toolBar.addSeparator()        
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.transactionAction)
        self.toolBar.addAction(self.transactionReportAction)
        self.actionCreator(actList, objDict)
        self.delNodeLocalAction()
        
class AccountsMdiChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection, parent, selected_account=None):
        bhdr = HeaderUtil.getBinaryHeader("account_frame_header")
        self.splname = "account_frame_splitter"
        bspltr = SplitterUtil.getBinarySplitter(self.splname)
        super(AccountsMdiChild, self).__init__()
        self.parent = parent
        self.connection = connection
        self.thread = Worker()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
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
        self.tableWidget = tableFormat(self.tableWidget)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        #self.tableWidget.horizontalScrollBar().hide()
        columns=[u'id', u'Имя пользователя', u'Баланс', u'Кредит', u'Имя', u'E-mail', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u"MAC адрес", u'Статус', u"Дата подключения"]
        #self.tableWidget.setColumnCount(len(columns))
        
        makeHeaders(columns, self.tableWidget)
            
        
        tree_header = self.tarif_treeWidget.headerItem()
        hght = self.tableWidget.horizontalHeader().maximumHeight()
        sz = QtCore.QSize()
        sz.setHeight(hght)
        #sz.setWidth(self.width()*0.7 / 5)
        tree_header.setSizeHint(0,sz)
        #sz.setWidth(self.width()*0.3 / 5)
        #tree_header.setSizeHint(1,sz)
        tree_header.setText(0,QtGui.QApplication.translate("MainWindow", "Тарифы", None, QtGui.QApplication.UnicodeUTF8))
        #tree_header.setText(1,QtGui.QApplication.translate("MainWindow", "Тип", None, QtGui.QApplication.UnicodeUTF8))

        self.setCentralWidget(self.splitter)
        
        self.splitter.setSizes([self.width() / 5, self.width() - (self.width() / 5)])


        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        
        #self.toolBar.setMaximumHeight(24)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)


        self.addAction = QtGui.QAction(u"Добавить аккаунт", self)
        self.addAction.setIcon(QtGui.QIcon("images/add.png"))
        
        self.delAction = QtGui.QAction(u"Удалить аккаунт",self)
        self.delAction.setIcon(QtGui.QIcon("images/del.png"))

        self.addTarifAction = QtGui.QAction(u"Добавить тариф",self)
        self.addTarifAction.setIcon(QtGui.QIcon("images/folder_add.png"))
        
        self.delTarifAction = QtGui.QAction(u"Удалить тариф",self)
        self.delTarifAction.setIcon(QtGui.QIcon("images/folder_delete.png"))
        
        self.transactionAction = QtGui.QAction(u'Пополнить счёт', self)
        self.transactionAction.setIcon(QtGui.QIcon("images/pay.png"))

        self.transactionReportAction = QtGui.QAction(u'История платежей',self)
        self.transactionReportAction.setIcon(QtGui.QIcon("images/moneybook.png"))

        self.actionDisableSession = QtGui.QAction(u'Отключить на сервере доступа',self)
        self.actionDisableSession.setIcon(QtGui.QIcon("images/del.png"))

        self.actionEnableSession = QtGui.QAction(u'Включить на сервере доступа',self)
        self.actionEnableSession.setIcon(QtGui.QIcon("images/add.png"))

        self.actionAddAccount = QtGui.QAction(u'Добавить на сервер доступа',self)
        self.actionAddAccount.setIcon(QtGui.QIcon("images/add.png"))

        self.actionDeleteAccount = QtGui.QAction(u'Удалить с сервера доступа',self)
        self.actionDeleteAccount.setIcon(QtGui.QIcon("images/del.png"))
        
        self.editTarifAction = QtGui.QAction(u"Редактировать",self)
        self.editTarifAction.setIcon(QtGui.QIcon("images/edit.png"))
        self.editTarifAction.setObjectName("editTarifAction")
        
        self.editAccountAction = QtGui.QAction(u"Редактировать",self)
        self.editAccountAction.setIcon(QtGui.QIcon("images/edit.png"))
        self.editAccountAction.setObjectName("editAccountAction")

        self.prepaidTrafficTailsAction = QtGui.QAction(u"Остаток предоплаченного трафика",self)
        self.prepaidTrafficTailsAction.setObjectName("prepaidTrafficTailsAction")

        self.connectionAgreementAction = QtGui.QAction(u"Договор на подключение",self)
        self.connectionAgreementAction.setObjectName("connectionAgreementAction")

        #self.invoiceAction = QtGui.QAction(u"Счёт-фактура",self)
        #self.invoiceAction.setObjectName("invoiceAction")
        
        self.actOfProvidedServices = QtGui.QAction(u"Акт выполненных работ", self)
        

        self.separatorAction = QtGui.QAction(self)
        self.separatorAction.setSeparator(True)
                
        self.tb = QtGui.QToolButton(self)
        self.tb.setIcon(QtGui.QIcon("images/documents.png"))
        self.tb.setText(u"Документы")
        self.tb.setPopupMode(QtGui.QToolButton.InstantPopup)
        menu = QtGui.QMenu(self.tb)
        menu.addAction(self.prepaidTrafficTailsAction)
        menu.addAction(self.get_separator())
        menu.addAction(self.connectionAgreementAction)
        menu.addAction(self.get_separator())
        menu.addAction(self.actOfProvidedServices)
        self.tb.setMenu(menu)
        self.tb.setDisabled(True)

        
        self.tarif_treeWidget.addAction(self.addTarifAction)
        self.tarif_treeWidget.addAction(self.delTarifAction)
        self.tarif_treeWidget.addAction(self.editTarifAction)
        
        self.tableWidget.addAction(self.transactionAction)
        self.tableWidget.addAction(self.get_separator())
        self.tableWidget.addAction(self.addAction)
        self.tableWidget.addAction(self.delAction)
        self.tableWidget.addAction(self.editAccountAction)
        self.tableWidget.addAction(self.get_separator())
        
        
        self.tableWidget.addAction(self.actionEnableSession)
        self.tableWidget.addAction(self.actionDisableSession)
        self.tableWidget.addAction(self.get_separator())
                        
        self.tableWidget.addAction(self.actionAddAccount)
        self.tableWidget.addAction(self.actionDeleteAccount)
        
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar.addAction(self.addTarifAction)
        self.toolBar.addAction(self.delTarifAction)
        self.toolBar.addSeparator()        
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.transactionAction)
        self.toolBar.addAction(self.transactionReportAction)
        
        self.toolBar.addWidget(self.tb)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.resize(1100,600)


        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.splitter, QtCore.SIGNAL("splitterMoved(int,int)"), self.saveSplitter)        
        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        
        self.connect(self.addTarifAction, QtCore.SIGNAL("triggered()"), self.addTarif)
        self.connect(self.delTarifAction, QtCore.SIGNAL("triggered()"), self.delTarif)
        
        self.connect(self.prepaidTrafficTailsAction, QtCore.SIGNAL("triggered()"), self.prepaidReport)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("itemClicked(QTableWidgetItem *)"), self.delNodeLocalAction)
        self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.refreshTree)
 
        self.connect(self.transactionAction, QtCore.SIGNAL("triggered()"), self.makeTransation)
        self.connect(self.transactionReportAction, QtCore.SIGNAL("triggered()"), self.transactionReport) 
        self.connect(self.actionDisableSession, QtCore.SIGNAL("triggered()"), self.accountDisable)
        self.connect(self.actionEnableSession, QtCore.SIGNAL("triggered()"), self.accountEnable)
        self.connect(self.actionAddAccount, QtCore.SIGNAL("triggered()"), self.accountAdd)
        self.connect(self.actionDeleteAccount, QtCore.SIGNAL("triggered()"), self.accountDelete)
        self.connect(self.editTarifAction, QtCore.SIGNAL("triggered()"), self.editTarif)
        self.connect(self.editAccountAction, QtCore.SIGNAL("triggered()"), self.editframe)
        
        #self.connect(self, QtCore.SIGNAL("closed()"), self.saveGeometry)
        
        self.connectTree()
        
        
        self.retranslateUi()
        self.refreshTree()
        setFirstActive(self.tarif_treeWidget)
        HeaderUtil.nullifySaved("account_frame_header")
        SplitterUtil.nullifySaved(self.splname)
        #self.tableWidget.resizeColumnsToContents()
        
        self.refresh()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("account_frame_header", bhdr)
            HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        if not bspltr.isEmpty():
            SplitterUtil.setBinarySplitter(self.splname, bspltr)
            SplitterUtil.getSplitter(self.splname, self.splitter)
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        self.restoreWindow()
        #self.thread.go(interval=60) #Нельзя,т.к. будут происходить коммиты когда редактируется тарифный план
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        
    def get_separator(self):
        sep=QtGui.QAction(self)
        sep.setSeparator(True)
        return sep
        
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
        #self.editTarifAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        #self.editAccountAction.setText(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))


    def addTarif(self):
        #print connection
        tarifframe = TarifFrame(connection=self.connection)
        if tarifframe.exec_() == 1:
            #import datetime
            #print datetime.datetime.now()
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
                tarif_type = str(self.tarif_treeWidget.currentItem().tarif_type) 
                tarifs = self.connection.sql("SELECT id, name FROM billservice_tariff WHERE (id <> %d) AND (active=TRUE) AND (get_tariff_type(id)='%s');" % (tarif_id, tarif_type))
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
                        self.connection.iddelete(tarif_id, "billservice_tariff")
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
            
        #print num

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
        
        if child.exec_()==1 and id is not None:
            #time.sleep(5)
            self.connection.commit()
            self.refresh()

    def makeTransation(self):
        id = self.getSelectedId()
        account = self.connection.get_model(id, "billservice_account")
        child = TransactionForm(connection=self.connection, account = account)
        if child.exec_()==1:
            tr = transaction(account_id=account.id, type_id = "MANUAL_TRANSACTION", approved = True, description = "", summ=child.result, bill=unicode(child.payed_document_edit.text()))
            try:
                
                self.connection.transaction(tr)
                self.connection.commit()
            except Exception, e:
                print "omg traf exception", e
                self.connection.rollback()
            
            #Если будем переделывать - здесь нужно списывать со счёта пользователя указанную сумму денег.
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
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTarifId(self):
        return self.tarif_treeWidget.currentItem().id

    def delete(self):
        id=self.getSelectedId()
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить пользователя из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
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
        
        #addf.show()
        if addf.exec_()==1:
            self.connection.iddelete(id, "billservice_accountipnspeed")
            self.connection.commit()
            self.refresh()

    def addrow(self, value, x, y, color=None, enabled=True):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if float(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
        
        if not enabled:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        
            
        if y==1:
            if enabled==True:
                headerItem.setIcon(QtGui.QIcon("images/user.png"))
            else:
                headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
            

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
                item.setDisabled(True)
            
        self.connectTree()
        if curItem != -1:
            self.tarif_treeWidget.setCurrentItem(self.tarif_treeWidget.topLevelItem(curItem))
        
            
    def refresh(self, item=None, k=''):
        #self.tableWidget.setSortingEnabled(False)
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
        #tarif = self.connection.foselect("billservice_tariff", id)
        
        #self.connection.commit()
        accounts = self.connection.get_accounts_for_tarif(self.getTarifId())
        self.connection.commit()
        #self.connection.commit()
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
            self.addrow(a.ipn_mac_address, i,9, enabled=a.status)
            #self.addrow(a.suspended, i,10, enabled=a.status)
            #self.addrow(a.balance_blocked, i,11, enabled=a.status)
            self.tableWidget.setCellWidget(i,10,tableImageWidget(nops= not a.suspended, balance_blocked=a.balance_blocked, trafic_limit=a.disabled_by_limit, ipn_status=a.ipn_status, ipn_added=a.ipn_added))
            #self.addrow(a.disabled_by_limit,i,12, enabled=a.status)
            self.addrow(a.created.strftime(self.strftimeFormat), i,11, enabled=a.status)
            
            #self.tableWidget.setRowHeight(i, 17)
            
            if self.selected_account:
                if self.selected_account.id == a.id:
                    self.tableWidget.setRangeSelected(QtGui.QTableWidgetSelectionRange(i,0,i,12), True)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.delNodeLocalAction()
        #self.tableWidget.setSortingEnabled(True)
        

    def accountEnable(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'enable'):
            QtGui.QMessageBox.information(self, u"Ok", unicode(u"Аккаунт включён на сервере доступа."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))


    def accountAdd(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'create'):
            QtGui.QMessageBox.information(self, u"Ok", unicode(u"Аккаунт добавлен на сервер доступа."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа недоступен, настроен неправильно или у пользователя не указан IP адрес."))

    def accountDelete(self):
        id=self.getSelectedId()
        if (id==0) and (QtGui.QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить аккаунт? \n После удаления станет недоступна статистика и информация о проводках.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.No):
            return

        if self.connection.accountActions(id, 'delete'):
            QtGui.QMessageBox.information(self, u"Ok", unicode(u"Аккаунт удалёг с сервера доступа."))
            
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа недоступен, настроен неправильно или у пользователя не указан IP адрес."))


    def accountDisable(self):
        id=self.getSelectedId()
        if id==0:
            return

        if self.connection.accountActions(id, 'disable'):
            QtGui.QMessageBox.information(self, u"Ok", unicode(u"Аккаунт удалён с сервера доступа."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
    
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("account_frame_header", self.tableWidget)
    def saveSplitter(self, *args):
        SplitterUtil.saveSplitter(self.splname, self.splitter)
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
            
    def restoreWindow(self):
        #print 'restore geometry'
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        #print val
        self.restoreGeometry(val)
        
    def closeEvent(self, event):
        #self.thread.terminate()
        #print "Close Window"
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()
    #---------------------------
