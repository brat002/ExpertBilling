#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import Account, Tariff, AccountTarif, SettlementPeriod, TimePeriod
from nas.models import IPAddressPool, Nas, TrafficClass
from django.db import transaction
from randgen import nameGen, GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import CheckBoxDialog, ComboBoxDialog, SpeedEditDialog

class CashType(object):
    def __init__(self, name):
        self.name=name
        
cash_types = [CashType("AT_START"), CashType("AT_END"), CashType("GRADUAL")]

class CustomWidget(QtGui.QLabel):
    def __init__(self, parent, models):
        QtGui.QLabel.__init__(self, parent)
        self.models=models

        labels={}
        for x in models:
            label = QtGui.QLabel(self)
            label.setText(unicode(x.name))
            labels[x]=label
            
        layout = QtGui.QVBoxLayout(self)
        for key in labels:
            #print key
            layout.addWidget(labels[key])
        self.setLayout(layout)
        #self.setGeometry(QtCore.QRect(0,0,691,411))
        #self.setMinimumHeight(15*len(models))
        

class AddAccountTarif(QtGui.QDialog):
    def __init__(self, account, model=None):
        super(AddAccountTarif, self).__init__()
        self.model=model
        self.account=account

        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()).expandedTo(self.minimumSizeHint()))

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
        tarif=Tariff.objects.get(name=unicode(self.tarif_edit.currentText()))
        date=self.date_edit.dateTime().toPyDateTime()

        if self.model:
            self.model.tarif=tarif
            self.model.datetime=date
            self.model.save()
        else:
            model=AccountTarif.objects.create(account=self.account, tarif=tarif, datetime=date)

        QDialog.accept(self)


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
        tarifs=Tariff.objects.all()
        for tarif in tarifs:
            self.tarif_edit.addItem(tarif.name)
        now=datetime.datetime.now()

        if self.model:
            self.tarif_edit.setCurrentIndex(self.tarif_edit.findText(self.model.tarif.name, QtCore.Qt.MatchCaseSensitive))

            now = QtCore.QDateTime()

            now.setTime_t((mktime(self.model.datetime.timetuple())))
        self.date_edit.setDateTime(now)

class TarifFrame(QtGui.QDialog):
    def __init__(self, model=None):
        super(TarifFrame, self).__init__()
        
        self.model=model
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,623,630).size()).expandedTo(self.minimumSizeHint()))

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
        self.sp_groupbox.setGeometry(QtCore.QRect(10,60,481,161))
        self.sp_groupbox.setObjectName("sp_groupbox")

        self.sp_type_edit = QtGui.QCheckBox(self.sp_groupbox)
        self.sp_type_edit.setGeometry(QtCore.QRect(11,20,466,19))
        self.sp_type_edit.setObjectName("sp_type_edit")

        self.sp_name_label = QtGui.QLabel(self.sp_groupbox)
        self.sp_name_label.setGeometry(QtCore.QRect(10,50,71,21))
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

        self.ps_null_ballance_checkout_edit = QtGui.QCheckBox(self.tab_1)
        self.ps_null_ballance_checkout_edit.setGeometry(QtCore.QRect(10,230,451,30))
        self.ps_null_ballance_checkout_edit.setObjectName("ps_null_ballance_checkout_edit")

        self.access_type_edit = QtGui.QComboBox(self.tab_1)
        self.access_type_edit.setGeometry(QtCore.QRect(150,260,241,21))
        self.access_type_edit.setObjectName("access_type_edit")

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
        self.tabWidget.addTab(self.tab_1,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.speed_access_groupBox = QtGui.QGroupBox(self.tab_2)
        self.speed_access_groupBox.setGeometry(QtCore.QRect(10,10,598,245))
        self.speed_access_groupBox.setObjectName("speed_access_groupBox")

        self.speed_priority_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_priority_edit.setGeometry(QtCore.QRect(110,210,331,21))
        self.speed_priority_edit.setObjectName("speed_priority_edit")

        self.speed_max_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_max_out_edit.setGeometry(QtCore.QRect(276,45,161,21))
        self.speed_max_out_edit.setObjectName("speed_max_out_edit")

        self.speed_burst_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_out_edit.setGeometry(QtCore.QRect(276,111,164,21))
        self.speed_burst_out_edit.setObjectName("speed_burst_out_edit")

        self.speed_burst_time_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_time_out_edit.setGeometry(QtCore.QRect(276,177,164,21))
        self.speed_burst_time_out_edit.setObjectName("speed_burst_time_out_edit")

        self.speed_min_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_in_edit.setGeometry(QtCore.QRect(109,78,161,21))
        self.speed_min_in_edit.setObjectName("speed_min_in_edit")

        self.speed_burst_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_burst_label.setGeometry(QtCore.QRect(11,111,89,21))
        self.speed_burst_label.setObjectName("speed_burst_label")

        self.speed_burst_treshold_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_out_edit.setGeometry(QtCore.QRect(276,144,164,21))
        self.speed_burst_treshold_out_edit.setObjectName("speed_burst_treshold_out_edit")

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
        self.speed_burst_time_in_edit.setObjectName("speed_burst_time_in_edit")

        self.speed_burst_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_in_edit.setGeometry(QtCore.QRect(109,111,161,21))
        self.speed_burst_in_edit.setObjectName("speed_burst_in_edit")

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
        self.speed_max_in_edit.setObjectName("speed_max_in_edit")

        self.speed_min_label = QtGui.QLabel(self.speed_access_groupBox)
        self.speed_min_label.setGeometry(QtCore.QRect(11,78,89,21))
        self.speed_min_label.setObjectName("speed_min_label")

        self.speed_min_out_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_min_out_edit.setGeometry(QtCore.QRect(276,78,164,21))
        self.speed_min_out_edit.setObjectName("speed_min_out_edit")

        self.speed_burst_treshold_in_edit = QtGui.QLineEdit(self.speed_access_groupBox)
        self.speed_burst_treshold_in_edit.setGeometry(QtCore.QRect(109,144,161,21))
        self.speed_burst_treshold_in_edit.setObjectName("speed_burst_treshold_in_edit")

        self.speed_table = QtGui.QTableWidget(self.tab_2)
        self.speed_table.setGeometry(QtCore.QRect(9,290,595,239))
        self.speed_table.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.speed_table.setFrameShape(QtGui.QFrame.Panel)
        self.speed_table.setFrameShadow(QtGui.QFrame.Sunken)
        self.speed_table.setAlternatingRowColors(True)
        self.speed_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.speed_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.speed_table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.speed_table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.speed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.speed_table.setGridStyle(QtCore.Qt.DotLine)
        self.speed_table.setSortingEnabled(False)
        self.speed_table.setObjectName("speed_table")

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
        self.tabWidget.addTab(self.tab_2,"")

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
        self.timeaccess_table.setFrameShape(QtGui.QFrame.Panel)
        self.timeaccess_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.timeaccess_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.timeaccess_table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.timeaccess_table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.timeaccess_table.setGridStyle(QtCore.Qt.DotLine)
        self.timeaccess_table.setObjectName("timeaccess_table")

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
        self.tabWidget.addTab(self.tab_3,"")

        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.reset_traffic_edit = QtGui.QCheckBox(self.tab_4)
        self.reset_traffic_edit.setGeometry(QtCore.QRect(12,498,398,19))
        self.reset_traffic_edit.setObjectName("reset_traffic_edit")

        self.trafficcost_tableWidget = QtGui.QTableWidget(self.tab_4)
        self.trafficcost_tableWidget.setGeometry(QtCore.QRect(8,60,601,247))
        self.trafficcost_tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.trafficcost_tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        #self.trafficcost_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.trafficcost_tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.trafficcost_tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.trafficcost_tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.trafficcost_tableWidget.setObjectName("trafficcost_tableWidget")

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
        self.prepaid_tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.prepaid_tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.prepaid_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.prepaid_tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.prepaid_tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.prepaid_tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.prepaid_tableWidget.setObjectName("prepaid_tableWidget")

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
        self.tabWidget.addTab(self.tab_4,"")

        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName("tab_6")

        self.onetime_tableWidget = QtGui.QTableWidget(self.tab_6)
        self.onetime_tableWidget.setGeometry(QtCore.QRect(10,40,597,486))
        self.onetime_tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.onetime_tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.onetime_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.onetime_tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.onetime_tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.onetime_tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.onetime_tableWidget.setObjectName("onetime_tableWidget")

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
        self.periodical_tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.periodical_tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.periodical_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.periodical_tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.periodical_tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.periodical_tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.periodical_tableWidget.setObjectName("periodical_tableWidget")

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
        self.limit_tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.limit_tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.limit_tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.limit_tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.limit_tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.limit_tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.limit_tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.limit_tableWidget.setObjectName("limit_tableWidget")

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

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
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
        self.fixtures()

        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_description_label.setText(QtGui.QApplication.translate("Dialog", "Описание тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_status_edit.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_groupbox.setTitle(QtGui.QApplication.translate("Dialog", "Расчётный период", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_type_edit.setText(QtGui.QApplication.translate("Dialog", "Начать при активации у пользователя данного тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_cost_label.setText(QtGui.QApplication.translate("Dialog", "Стоимость пакета", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_tarif_cost_edit.setText(QtGui.QApplication.translate("Dialog", "Производить доснятие суммы до стоимости тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.ps_null_ballance_checkout_edit.setText(QtGui.QApplication.translate("Dialog", "Производить снятие денег при нулевом баллансе пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.access_type_label.setText(QtGui.QApplication.translate("Dialog", "Способ доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.access_time_label.setText(QtGui.QApplication.translate("Dialog", "Время доступа", None, QtGui.QApplication.UnicodeUTF8))
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
        self.speed_table.setColumnCount(8)
        self.speed_table.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("Dialog", "Time", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("Dialog", "BURST", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(4,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        headerItem5.setText(QtGui.QApplication.translate("Dialog", "Burst Tr", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(5,headerItem5)

        headerItem6 = QtGui.QTableWidgetItem()
        headerItem6.setText(QtGui.QApplication.translate("Dialog", "Burst time", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(6,headerItem6)

        headerItem7 = QtGui.QTableWidgetItem()
        headerItem7.setText(QtGui.QApplication.translate("Dialog", "Priority", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_table.setHorizontalHeaderItem(7,headerItem7)
        self.del_speed_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_speed_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_time_label.setText(QtGui.QApplication.translate("Dialog", "Предоплачено, с", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_time_checkbox.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце расчётного периода предоплаченное время", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.clear()
        self.timeaccess_table.setColumnCount(3)
        self.timeaccess_table.setRowCount(0)

        headerItem8 = QtGui.QTableWidgetItem()
        headerItem8.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.setHorizontalHeaderItem(0,headerItem8)

        headerItem9 = QtGui.QTableWidgetItem()
        headerItem9.setText(QtGui.QApplication.translate("Dialog", "Время", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.setHorizontalHeaderItem(1,headerItem9)

        headerItem10 = QtGui.QTableWidgetItem()
        headerItem10.setText(QtGui.QApplication.translate("Dialog", "Цена", None, QtGui.QApplication.UnicodeUTF8))
        self.timeaccess_table.setHorizontalHeaderItem(2,headerItem10)
        self.del_timecost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_timecost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Оплата за время", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_traffic_edit.setText(QtGui.QApplication.translate("Dialog", "Сбрасывать в конце периода предоплаченый трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.clear()
        self.trafficcost_tableWidget.setColumnCount(9)
        self.trafficcost_tableWidget.setRowCount(0)

        headerItem16 = QtGui.QTableWidgetItem()
        headerItem16.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(0,headerItem16)

        headerItem17 = QtGui.QTableWidgetItem()
        headerItem17.setText(QtGui.QApplication.translate("Dialog", "От МБ", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(1,headerItem17)

        headerItem18 = QtGui.QTableWidgetItem()
        headerItem18.setText(QtGui.QApplication.translate("Dialog", "До МБ", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(2,headerItem18)

        headerItem19 = QtGui.QTableWidgetItem()
        headerItem19.setText(QtGui.QApplication.translate("Dialog", "Класс трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(3,headerItem19)

        headerItem20 = QtGui.QTableWidgetItem()
        headerItem20.setText(QtGui.QApplication.translate("Dialog", "Вх", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(4,headerItem20)

        headerItem21 = QtGui.QTableWidgetItem()
        headerItem21.setText(QtGui.QApplication.translate("Dialog", "Исх", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(5,headerItem21)

        headerItem22 = QtGui.QTableWidgetItem()
        headerItem22.setText(QtGui.QApplication.translate("Dialog", "Тр", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(6,headerItem22)

        headerItem23 = QtGui.QTableWidgetItem()
        headerItem23.setText(QtGui.QApplication.translate("Dialog", "Время", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(7,headerItem23)

        headerItem24 = QtGui.QTableWidgetItem()
        headerItem24.setText(QtGui.QApplication.translate("Dialog", "Цена", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficcost_tableWidget.setHorizontalHeaderItem(8,headerItem24)

        self.trafficcost_label.setText(QtGui.QApplication.translate("Dialog", "Цена за МБ трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.del_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_traffic_cost_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_tableWidget.clear()
        self.prepaid_tableWidget.setColumnCount(3)
        self.prepaid_tableWidget.setRowCount(0)

        headerItem25 = QtGui.QTableWidgetItem()
        headerItem25.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_tableWidget.setHorizontalHeaderItem(0,headerItem25)

        headerItem26 = QtGui.QTableWidgetItem()
        headerItem26.setText(QtGui.QApplication.translate("Dialog", "Класс трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_tableWidget.setHorizontalHeaderItem(1,headerItem26)

        headerItem27 = QtGui.QTableWidgetItem()
        headerItem27.setText(QtGui.QApplication.translate("Dialog", "Размер", None, QtGui.QApplication.UnicodeUTF8))
        self.prepaid_tableWidget.setHorizontalHeaderItem(2,headerItem27)
        self.prepaid_traffic_cost_label.setText(QtGui.QApplication.translate("Dialog", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.del_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_prepaid_traffic_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("Dialog", "Оплата за трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_tableWidget.clear()
        self.onetime_tableWidget.setColumnCount(3)
        self.onetime_tableWidget.setRowCount(0)

        headerItem28 = QtGui.QTableWidgetItem()
        headerItem28.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_tableWidget.setHorizontalHeaderItem(0,headerItem28)

        headerItem29 = QtGui.QTableWidgetItem()
        headerItem29.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_tableWidget.setHorizontalHeaderItem(1,headerItem29)

        headerItem30 = QtGui.QTableWidgetItem()
        headerItem30.setText(QtGui.QApplication.translate("Dialog", "Стоимость", None, QtGui.QApplication.UnicodeUTF8))
        self.onetime_tableWidget.setHorizontalHeaderItem(2,headerItem30)
        self.del_onetime_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_onetime_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QtGui.QApplication.translate("Dialog", "Разовые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.clear()
        self.periodical_tableWidget.setColumnCount(5)
        self.periodical_tableWidget.setRowCount(0)

        headerItem31 = QtGui.QTableWidgetItem()
        headerItem31.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.setHorizontalHeaderItem(0,headerItem31)

        headerItem32 = QtGui.QTableWidgetItem()
        headerItem32.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.setHorizontalHeaderItem(1,headerItem32)

        headerItem33 = QtGui.QTableWidgetItem()
        headerItem33.setText(QtGui.QApplication.translate("Dialog", "Период", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.setHorizontalHeaderItem(2,headerItem33)

        headerItem34 = QtGui.QTableWidgetItem()
        headerItem34.setText(QtGui.QApplication.translate("Dialog", "Стоимость", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.setHorizontalHeaderItem(4,headerItem34)

        headerItem35 = QtGui.QTableWidgetItem()
        headerItem35.setText(QtGui.QApplication.translate("Dialog", "Способ снятия", None, QtGui.QApplication.UnicodeUTF8))
        self.periodical_tableWidget.setHorizontalHeaderItem(3,headerItem35)
        
        self.del_periodical_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_periodical_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("Dialog", "Периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.clear()
        self.limit_tableWidget.setColumnCount(6)
        self.limit_tableWidget.setRowCount(0)

        headerItem36 = QtGui.QTableWidgetItem()
        headerItem36.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(0,headerItem36)

        headerItem37 = QtGui.QTableWidgetItem()
        headerItem37.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(1,headerItem37)

        headerItem38 = QtGui.QTableWidgetItem()
        headerItem38.setText(QtGui.QApplication.translate("Dialog", "За поледний", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(2,headerItem38)

        headerItem39 = QtGui.QTableWidgetItem()
        headerItem39.setText(QtGui.QApplication.translate("Dialog", "Период", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(3,headerItem39)

        headerItem40 = QtGui.QTableWidgetItem()
        headerItem40.setText(QtGui.QApplication.translate("Dialog", "Классы трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(4,headerItem40)
        
        headerItem50 = QtGui.QTableWidgetItem()
        headerItem50.setText(QtGui.QApplication.translate("Dialog", "Объём", None, QtGui.QApplication.UnicodeUTF8))
        self.limit_tableWidget.setHorizontalHeaderItem(5,headerItem50)
        
        self.del_limit_button.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.add_limit_button.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QtGui.QApplication.translate("Dialog", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        
    def addrow(self, widget, value, x, y, item_type=None):
        if value==None:
            value=''
        if not item_type:
            item_type = QtGui.QTableWidgetItem()
            item_type.setText(unicode(value))
            widget.setItem(x, y, item_type)
        
        if item_type=='checkbox':
            item_type = QtGui.QCheckBox()
            #widget.setItem(x, y, item_type)
            item_type.setCheckState(value == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            widget.setCellWidget(x,y, item_type)
            
    def timeAccessRowEdit(self):
        pass
 
#-----------------------------Добавление строк в таблицы       
    def addTrafficCostRow(self):
        current_row = self.trafficcost_tableWidget.currentRow()+1
        self.trafficcost_tableWidget.insertRow(current_row)
        self.addrow(self.trafficcost_tableWidget, True, current_row, 4, item_type='checkbox')
        self.addrow(self.trafficcost_tableWidget, True, current_row, 5, item_type='checkbox')
        self.addrow(self.trafficcost_tableWidget, True, current_row, 6, item_type='checkbox')
    
    def delTrafficCostRow(self):
        current_row = self.trafficcost_tableWidget.currentRow()
        
        self.trafficcost_tableWidget.removeRow(current_row)
        
        
    def addLimitRow(self):
        current_row = self.limit_tableWidget.rowCount()
        self.limit_tableWidget.insertRow(current_row)
        self.addrow(self.limit_tableWidget, True, current_row, 2, item_type='checkbox')

    
    def delLimitRow(self):
        current_row = self.limit_tableWidget.currentRow()
        
        self.limit_tableWidget.removeRow(current_row)

    def addOneTimeRow(self):
        current_row = self.onetime_tableWidget.rowCount()
        self.onetime_tableWidget.insertRow(current_row)
    
    def delOneTimeRow(self):
        current_row = self.onetime_tableWidget.currentRow()        
        self.onetime_tableWidget.removeRow(current_row)

    def addTimeAccessRow(self):
        current_row = self.timeaccess_table.rowCount()
        self.timeaccess_table.insertRow(current_row)
    
    def delTimeAccessRow(self):
        current_row = self.timeaccess_table.currentRow()        
        self.timeaccess_table.removeRow(current_row)

    def addPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.rowCount()
        self.prepaid_tableWidget.insertRow(current_row)
    
    def delPrepaidTrafficRow(self):
        current_row = self.prepaid_tableWidget.currentRow()        
        self.prepaid_tableWidget.removeRow(current_row)

    def addSpeedRow(self):
        current_row = self.speed_table.rowCount()
        self.speed_table.insertRow(current_row)
    
    def delSpeedRow(self):
        current_row = self.speed_table.currentRow()        
        self.speed_table.removeRow(current_row)

                
#-----------------------------

#-----------------------------Обработка редактирования таблиц
    def prepaidTrafficEdit(self,y,x):
        if x==1:
            try:
                models = self.prepaid_tableWidget.cellWidget(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=TrafficClass.objects.all(), selected_items = models)
            if child.exec_()==1:
                self.prepaid_tableWidget.setCellWidget(y,x, CustomWidget(parent=self.prepaid_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    self.prepaid_tableWidget.setRowHeight(y, len(child.selected_items)*25)
        
        if x==2:
            item = self.prepaid_tableWidget.item(y,x)
            try:
                default_text=int(item.text())
            except:
                default_text=0
            
            text = QInputDialog.getInteger(self, u"Объём:", u"Введите количество предоплаченных мегабайт", default_text)        
           
            self.prepaid_tableWidget.setItem(y,x, QTableWidgetItem(unicode(text[0])))
 
 
    def speedEdit(self,y,x):
        if x==1:
            item = self.speed_table.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=TimePeriod.objects.all(), selected_item = default_text )
            if child.exec_()==1:
                self.speed_table.setItem(y,x, QTableWidgetItem(child.comboBox.currentText()))
        if x in (2, 3,4,5,6):
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
                self.speed_table.setItem(y,x, QTableWidgetItem(child.resultstring))
            
        if x==7:
            item = self.speed_table.item(y,x)
            try:
                default_text=int(item.text())
            except:
                default_text=0
            
            text = QInputDialog.getInteger(self, u"Приоритет", u"Введите приоритет от 1 до 8", default_text)        
           
            self.speed_table.setItem(y,x, QTableWidgetItem(unicode(text[0])))


    def limitClassEdit(self,y,x):
        if x==4:
            try:
                models = self.limit_tableWidget.cellWidget(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=TrafficClass.objects.all(), selected_items = models)
            if child.exec_()==1:
                self.limit_tableWidget.setCellWidget(y,x, CustomWidget(parent=self.limit_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    self.limit_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    
        if x==3:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=SettlementPeriod.objects.all(), selected_item = default_text )
            if child.exec_()==1:
                self.limit_tableWidget.setItem(y,x, QTableWidgetItem(child.comboBox.currentText()))

        if x==1:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QInputDialog.getText(self,u"Введите название название", u"Название:", QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[2]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            
            self.limit_tableWidget.setItem(y,x, QTableWidgetItem(text[0]))
             
        if x==5:
            item = self.limit_tableWidget.item(y,x)
            try:
                default_text=int(item.text())
            except:
                default_text=0
            
            text = QInputDialog.getInteger(self, u"Размер:", u"Введите размер лимита в МБ, после которого произойдёт отключение", default_text)        
           
            self.limit_tableWidget.setItem(y,x, QTableWidgetItem(unicode(text[0])))
                
    def oneTimeServicesEdit(self,y,x):
        if x==1:
            item = self.onetime_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QInputDialog.getText(self,u"Введите название название", u"Название:", QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[2]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            
            self.onetime_tableWidget.setItem(y,x, QTableWidgetItem(text[0]))        

        if x==2:
            item = self.onetime_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость разовой услуги", default_text)        
           
            self.onetime_tableWidget.setItem(y,x, QTableWidgetItem(unicode(text[0])))
                

    def timeAccessServiceEdit(self,y,x):
        if x==1:
            item = self.timeaccess_table.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
            child = ComboBoxDialog(items=TimePeriod.objects.all(), selected_item = default_text )
            if child.exec_()==1:
                self.timeaccess_table.setItem(y,x, QTableWidgetItem(child.comboBox.currentText()))    

        if x==2:
            item = self.timeaccess_table.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0.00
            
            text = QInputDialog.getDouble(self, u"Стоимость:", u"Введите стоимость", default_text)        
           
            self.timeaccess_table.setItem(y,x, QTableWidgetItem(unicode(text[0])))
                
                                     
   
    def trafficCostCellEdit(self,y,x):
        
        #Редактируем класс тарфика

        if x==3:
            try:
                models = self.trafficcost_tableWidget.cellWidget(y,x).models
            except:
                models = []
            
            child = CheckBoxDialog(all_items=TrafficClass.objects.all(), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setCellWidget(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    self.trafficcost_tableWidget.setRowHeight(y, len(child.selected_items)*25)
                    
                
        if x==7:
            try:
                models = self.trafficcost_tableWidget.cellWidget(y,x).models
            except:
                models = []
            child = CheckBoxDialog(all_items=TimePeriod.objects.all(), selected_items = models)
            if child.exec_()==1:
                self.trafficcost_tableWidget.setCellWidget(y,x, CustomWidget(parent=self.trafficcost_tableWidget, models=child.selected_items))
                if len(child.selected_items)>0:
                    self.trafficcost_tableWidget.setRowHeight(y, len(child.selected_items)*25)    

        if x==8:
            item = self.trafficcost_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QInputDialog.getDouble(self, u"Цена за МБ:", u"Введите цену", default_text)        
           
            self.trafficcost_tableWidget.setItem(y,x, QTableWidgetItem(unicode(text[0])))
            


    def periodicalServicesEdit(self,y,x):
        
                  
        if x==2:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=SettlementPeriod.objects.all(), selected_item = default_text )
            if child.exec_()==1:
                self.periodical_tableWidget.setItem(y,x, QTableWidgetItem(child.comboBox.currentText()))

        if x==1:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=item.text()
            except:
                default_text=u""
            
            text = QInputDialog.getText(self,u"Введите название", u"Название:", QLineEdit.Normal, default_text)        
            if text[0].isEmpty()==True and text[2]:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
                return
            
            self.periodical_tableWidget.setItem(y,x, QTableWidgetItem(text[0]))

        if x==3:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text = item.text()
            except:
                default_text=u""
                
            child = ComboBoxDialog(items=cash_types, selected_item = default_text )
            if child.exec_()==1:
                self.periodical_tableWidget.setItem(y,x, QTableWidgetItem(child.comboBox.currentText()))
             
        if x==4:
            item = self.periodical_tableWidget.item(y,x)
            try:
                default_text=float(item.text())
            except:
                default_text=0
            
            text = QInputDialog.getDouble(self, u"Цена:", u"Введите цену", default_text)        
           
            self.periodical_tableWidget.setItem(y,x, QTableWidgetItem(unicode(text[0])))


#----------------------------

    def getCurrentIdFromtable(self, tablewidget):
        return int(tablewidget.item(tablewidget.currentRow(), 0).text())
    
    def fixtures(self):
        settlement_periods = SettlementPeriod.objects.all()
        for sp in settlement_periods:
            self.sp_name_edit.addItem(sp.name)
            
        access_types = ["PPTP", "PPPOE", "IPN"]
        for access_type in access_types:
            self.access_type_edit.addItem(access_type)
        
        access_time = TimePeriod.objects.all()
        
        for at in access_time:
            self.access_time_edit.addItem(unicode(at.name))

        if self.model:
            self.tarif_name_edit.setText(self.model.name)
            self.tarif_cost_edit.setText(unicode(self.model.cost))
            self.tarif_description_edit.setText(self.model.description)
            self.reset_tarif_cost_edit.setCheckState(self.model.reset_tarif_cost == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.ps_null_ballance_checkout_edit.setCheckState(self.model.ps_null_ballance_checkout == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            #Speed default parameters
            try:
                max_limit_in, max_limit_out = self.model.access_parameters.max_limit.split("/")
            except:
                max_limit_in, max_limit_out = "",""
            
            self.speed_max_in_edit.setText(max_limit_in)
            self.speed_max_out_edit.setText(max_limit_out)
            
            try:
                min_limit_in, min_limit_out = self.model.access_parameters.min_limit.split("/")
            except:
                min_limit_in, min_limit_out = "",""

            self.speed_min_in_edit.setText(min_limit_in)
            self.speed_min_out_edit.setText(min_limit_out)

            try:
                burst_limit_in, burst_limit_out = self.model.access_parameters.burst_limit.split("/")
            except:
                burst_limit_in, burst_limit_out = "",""

            self.speed_burst_in_edit.setText(burst_limit_in)
            self.speed_burst_out_edit.setText(burst_limit_out)

            try:
                burst_treshold_in, burst_treshold_out = self.model.access_parameters.burst_treshold.split("/")
            except:
                burst_treshold_in, burst_treshold_out = "",""

            self.speed_burst_treshold_in_edit.setText(burst_treshold_in)
            self.speed_burst_treshold_out_edit.setText(burst_treshold_out)

            try:
                burst_time_in, burst_time_out = self.model.access_parameters.burst_time.split("/")
            except:
                burst_time_in, burst_time_out = "",""

            self.speed_burst_time_in_edit.setText(burst_time_in)
            self.speed_burst_time_out_edit.setText(burst_time_out)


            self.speed_priority_edit.setText(unicode(self.model.access_parameters.priority))   
            
            #self.speed_table.clear()
            speeds = self.model.access_parameters.access_speed.all()
            self.speed_table.setRowCount(speeds.count())
            i=0
            for speed in speeds:
                self.addrow(self.speed_table, speed.id,i, 0)
                self.addrow(self.speed_table, speed.time.name,i, 1)
                self.addrow(self.speed_table, speed.max_limit,i, 2)
                self.addrow(self.speed_table, speed.min_limit,i, 3)
                self.addrow(self.speed_table, speed.burst_limit,i, 4)
                self.addrow(self.speed_table, speed.burst_treshold,i, 5)
                self.addrow(self.speed_table, speed.burst_time,i, 6)
                self.addrow(self.speed_table, u"%s" % speed.priority, i, 7)
                i+=1
                
            #OneTimeService
            if self.model.time_access_service:
                self.prepaid_time_edit.setValue(self.model.time_access_service.prepaid_time)
                self.reset_time_checkbox.setCheckState(self.model.time_access_service.reset_time == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
                nodes = self.model.time_access_service.time_access_nodes.all()
                self.timeaccess_table.setRowCount(nodes.count())
                i=0
                for node in nodes:
                    self.addrow(self.timeaccess_table, node.id,i, 0)
                    self.addrow(self.timeaccess_table, node.time_period,i, 1)
                    self.addrow(self.timeaccess_table, node.cost,i, 2)
                    i+=1                
                   
            #PeriodicalService
            if self.model.periodical_services.all().count()>0:
                nodes = self.model.periodical_services.all()
                self.periodical_tableWidget.setRowCount(nodes.count())
                i=0
                for node in nodes:
                    self.addrow(self.periodical_tableWidget, node.id,i, 0)
                    self.addrow(self.periodical_tableWidget, node.name,i, 1)
                    self.addrow(self.periodical_tableWidget, node.settlement_period.name,i, 2)
                    self.addrow(self.periodical_tableWidget, node.cash_method, i, 3)
                    self.addrow(self.periodical_tableWidget, node.cost,i, 4)
                    i+=1                   

            #Onetime Service
            if self.model.onetime_services.all().count()>0:
                nodes = self.model.onetime_services.all()
                self.onetime_tableWidget.setRowCount(nodes.count())
                i=0
                for node in nodes:
                    self.addrow(self.onetime_tableWidget, node.id,i, 0)
                    self.addrow(self.onetime_tableWidget, node.name,i, 1)
                    self.addrow(self.onetime_tableWidget, node.cost,i, 2)
                    i+=1   
                    
            #Limites
            if self.model.traffic_limit.all().count()>0:
                nodes = self.model.traffic_limit.all()
                self.limit_tableWidget.setRowCount(nodes.count())
                i=0
                for node in nodes:
                    classes = [clas for clas in node.traffic_class.all()]
                    self.addrow(self.limit_tableWidget, node.id,i, 0)
                    self.addrow(self.limit_tableWidget, node.name,i, 1)
                    self.addrow(self.limit_tableWidget, node.mode,i, 2, item_type='checkbox')
                    self.addrow(self.limit_tableWidget, node.settlement_period.name,i, 3)
                    self.limit_tableWidget.setCellWidget(0,4, CustomWidget(parent=self.limit_tableWidget, models=classes))
                    self.addrow(self.limit_tableWidget, node.size,i, 5)
                    
                    self.limit_tableWidget.setRowHeight(i, len(classes)*22) 
                    i+=1
                    
            #Prepaid Traffic
            if self.model.traffic_transmit_service:
                if self.model.traffic_transmit_service.prepaid_traffic.all().count()>0:
                    nodes = self.model.traffic_transmit_service.prepaid_traffic.all()
                    self.prepaid_tableWidget.setRowCount(nodes.count())
                    i=0
                    for node in nodes:
                        classes = [clas for clas in node.traffic_class.all()]
                        self.addrow(self.prepaid_tableWidget, node.id,i, 0)
                        self.prepaid_tableWidget.setCellWidget(0,1, CustomWidget(parent=self.prepaid_tableWidget, models=classes))
                        self.addrow(self.prepaid_tableWidget, node.size,i, 2)
                               
                        self.prepaid_tableWidget.setRowHeight(i, len(classes)*22) 
                        i+=1 
                
                if self.model.traffic_transmit_service.traffic_transmit_nodes.all().count()>0:
                    nodes = self.model.traffic_transmit_service.traffic_transmit_nodes.all()
                    self.trafficcost_tableWidget.setRowCount(nodes.count())
                    i = 0
                    for node in nodes:
                        tableWidget = QtGui.QTableWidget()
                        classes = [clas for clas in node.traffic_class.all()]
                        
                        time_periods = [tp for tp in node.time_nodes.all()]
                        
                        self.addrow(self.trafficcost_tableWidget, node.id, i, 0)
                        self.addrow(self.trafficcost_tableWidget, node.edge_start, i, 1)
                        self.addrow(self.trafficcost_tableWidget, node.edge_end, i, 2)
                        #self.addrow(self.trafficcost_tableWidget, classes, i, 3)
                        self.trafficcost_tableWidget.setCellWidget(0,3, CustomWidget(parent=self.trafficcost_tableWidget, models=classes))
                        self.addrow(self.trafficcost_tableWidget, node.in_direction, i, 4, item_type='checkbox')
                        self.addrow(self.trafficcost_tableWidget, node.out_direction, i, 5, item_type='checkbox')
                        self.addrow(self.trafficcost_tableWidget, node.transit_direction, i, 6, item_type='checkbox')
                        self.trafficcost_tableWidget.setCellWidget(0,7, CustomWidget(parent=self.trafficcost_tableWidget, models=time_periods))
                        self.addrow(self.trafficcost_tableWidget, node.cost, i, 8)
                        self.trafficcost_tableWidget.setRowHeight(i, len(classes)*22)
                        
                    self.trafficcost_tableWidget.resizeColumnsToContents()
                        
                        
                    
                    
class AddAccountFrame(QtGui.QDialog):
    def __init__(self, model=None):
        super(AddAccountFrame, self).__init__()
        self.model=model

        self.resize(QtCore.QSize(QtCore.QRect(0,0,427,476).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(70,440,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)


        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0,10,421,421))


        self.tab = QtGui.QWidget()

        self.address_label = QtGui.QLabel(self.tab)
        self.address_label.setGeometry(QtCore.QRect(10,230,44,21))


        self.address_edit = QtGui.QTextEdit(self.tab)
        self.address_edit.setGeometry(QtCore.QRect(58,240,333,111))


        self.status_edit = QtGui.QCheckBox(self.tab)
        self.status_edit.setGeometry(QtCore.QRect(10,370,70,19))


        self.suspended_edit = QtGui.QCheckBox(self.tab)
        self.suspended_edit.setGeometry(QtCore.QRect(10,210,345,19))


        self.widget = QtGui.QWidget(self.tab)
        self.widget.setGeometry(QtCore.QRect(10,148,325,61))


        self.gridlayout = QtGui.QGridLayout(self.widget)


        self.ballance_label = QtGui.QLabel(self.widget)

        self.gridlayout.addWidget(self.ballance_label,0,0,1,1)

        self.ballance_edit = QtGui.QLineEdit(self.widget)

        self.gridlayout.addWidget(self.ballance_edit,0,1,1,1)

        self.credit_label = QtGui.QLabel(self.widget)

        self.gridlayout.addWidget(self.credit_label,1,0,1,1)

        self.credit_edit = QtGui.QLineEdit(self.widget)

        self.gridlayout.addWidget(self.credit_edit,1,1,1,1)

        self.widget1 = QtGui.QWidget(self.tab)
        self.widget1.setGeometry(QtCore.QRect(11,7,391,141))


        self.gridlayout1 = QtGui.QGridLayout(self.widget1)


        self.username_label = QtGui.QLabel(self.widget1)

        self.gridlayout1.addWidget(self.username_label,0,0,1,1)

        self.username_edit = QtGui.QLineEdit(self.widget1)

        self.gridlayout1.addWidget(self.username_edit,0,1,1,1)

        self.generate_login_toolButton = QtGui.QToolButton(self.widget1)

        self.gridlayout1.addWidget(self.generate_login_toolButton,0,2,1,1)

        self.password_label = QtGui.QLabel(self.widget1)

        self.gridlayout1.addWidget(self.password_label,1,0,1,1)

        self.password_edit = QtGui.QLineEdit(self.widget1)

        self.gridlayout1.addWidget(self.password_edit,1,1,1,1)

        self.generate_password_toolButton = QtGui.QToolButton(self.widget1)

        self.gridlayout1.addWidget(self.generate_password_toolButton,1,2,1,1)

        self.firstname_label = QtGui.QLabel(self.widget1)

        self.gridlayout1.addWidget(self.firstname_label,2,0,1,1)

        self.firstname_edit = QtGui.QLineEdit(self.widget1)

        self.gridlayout1.addWidget(self.firstname_edit,2,1,1,2)

        self.lastname_label = QtGui.QLabel(self.widget1)

        self.gridlayout1.addWidget(self.lastname_label,3,0,1,1)

        self.lastname_edit = QtGui.QLineEdit(self.widget1)

        self.gridlayout1.addWidget(self.lastname_edit,3,1,1,2)
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()


        self.ip_settings_groupBox = QtGui.QGroupBox(self.tab_2)
        self.ip_settings_groupBox.setGeometry(QtCore.QRect(10,40,391,341))


        self.widget2 = QtGui.QWidget(self.ip_settings_groupBox)
        self.widget2.setGeometry(QtCore.QRect(20,20,352,231))


        self.gridlayout2 = QtGui.QGridLayout(self.widget2)


        self.assign_ipn_ip_from_dhcp_edit = QtGui.QCheckBox(self.widget2)

        self.gridlayout2.addWidget(self.assign_ipn_ip_from_dhcp_edit,0,0,1,2)

        self.ipn_dhcp_pool_label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.ipn_dhcp_pool_label,1,0,1,1)

        self.ipn_dhcp_pool_edit = QtGui.QComboBox(self.widget2)

        self.gridlayout2.addWidget(self.ipn_dhcp_pool_edit,1,1,1,2)

        self.assign_ipn_address_toolButton = QtGui.QToolButton(self.widget2)

        self.gridlayout2.addWidget(self.assign_ipn_address_toolButton,1,3,1,1)

        self.ipn_ip_address_label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.ipn_ip_address_label,2,0,1,1)

        self.ipn_ip_address_edit = QtGui.QLineEdit(self.widget2)

        self.gridlayout2.addWidget(self.ipn_ip_address_edit,2,1,1,1)

        self.ipn_mac_address_label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.ipn_mac_address_label,3,0,1,1)

        self.ipn_mac_address_edit = QtGui.QLineEdit(self.widget2)

        self.gridlayout2.addWidget(self.ipn_mac_address_edit,3,1,1,1)

        self.get_mac_address_toolButton = QtGui.QToolButton(self.widget2)
        self.get_mac_address_toolButton.hide()

        self.gridlayout2.addWidget(self.get_mac_address_toolButton,3,2,1,2)

        self.assign_vpn_ip_from_dhcp_edit = QtGui.QCheckBox(self.widget2)

        self.gridlayout2.addWidget(self.assign_vpn_ip_from_dhcp_edit,4,0,1,2)

        self.vpn_dhcp_pool_label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.vpn_dhcp_pool_label,5,0,1,1)

        self.vpn_dhcp_pool_edit = QtGui.QComboBox(self.widget2)

        self.gridlayout2.addWidget(self.vpn_dhcp_pool_edit,5,1,1,2)

        self.assign_vpn_address_toolButton = QtGui.QToolButton(self.widget2)

        self.gridlayout2.addWidget(self.assign_vpn_address_toolButton,5,3,1,1)

        self.vpn_ip_address_label = QtGui.QLabel(self.widget2)

        self.gridlayout2.addWidget(self.vpn_ip_address_label,6,0,1,1)

        self.vpn_ip_address_edit = QtGui.QLineEdit(self.widget2)

        self.gridlayout2.addWidget(self.vpn_ip_address_edit,6,1,1,1)

        self.splitter = QtGui.QSplitter(self.tab_2)
        self.splitter.setGeometry(QtCore.QRect(10,10,281,20))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)


        self.label_2 = QtGui.QLabel(self.splitter)


        self.nas_edit = QtGui.QComboBox(self.splitter)

        self.tabWidget.addTab(self.tab_2,"")

        self.tab_3 = QtGui.QWidget()


        self.accounttarif_table = QtGui.QTableWidget(self.tab_3)
        self.accounttarif_table.setGeometry(QtCore.QRect(0,90,411,291))
        vh = self.accounttarif_table.verticalHeader()
        vh.setVisible(False)

        hh = self.accounttarif_table.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        hh.setClickable(False)
        hh.ResizeMode(QtGui.QHeaderView.Stretch)



        self.add_accounttarif_toolButton = QtGui.QToolButton(self.tab_3)
        self.add_accounttarif_toolButton.setGeometry(QtCore.QRect(0,70,25,20))


        self.del_accounttarif_toolButton = QtGui.QToolButton(self.tab_3)
        self.del_accounttarif_toolButton.setGeometry(QtCore.QRect(30,70,25,20))


        self.label_3 = QtGui.QLabel(self.tab_3)
        self.label_3.setGeometry(QtCore.QRect(100,10,311,42))

        self.tabWidget.addTab(self.tab_3,"")
        
        self.address_label.setBuddy(self.address_edit)
        self.ballance_label.setBuddy(self.ballance_edit)
        self.credit_label.setBuddy(self.credit_edit)
        self.username_label.setBuddy(self.username_edit)
        self.password_label.setBuddy(self.password_edit)
        self.firstname_label.setBuddy(self.firstname_edit)
        self.lastname_label.setBuddy(self.lastname_edit)
        self.ipn_dhcp_pool_label.setBuddy(self.ipn_dhcp_pool_edit)
        self.ipn_ip_address_label.setBuddy(self.ipn_ip_address_edit)
        self.ipn_mac_address_label.setBuddy(self.ipn_mac_address_edit)
        self.vpn_dhcp_pool_label.setBuddy(self.vpn_dhcp_pool_edit)
        self.vpn_ip_address_label.setBuddy(self.vpn_ip_address_edit)
        self.label_2.setBuddy(self.nas_edit)

        self.retranslateUi()
        #self.tabWidget.setCurrentIndex(1)
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.generate_login_toolButton,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.generate_password_toolButton,QtCore.SIGNAL("clicked()"),self.generate_password)

        self.connect(self.add_accounttarif_toolButton,QtCore.SIGNAL("clicked()"),self.add_accounttarif)
        self.connect(self.del_accounttarif_toolButton,QtCore.SIGNAL("clicked()"),self.del_accounttarif)

        self.connect(self.accounttarif_table, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)




        self.setTabOrder(self.buttonBox,self.tabWidget)
        self.setTabOrder(self.tabWidget,self.username_edit)
        self.setTabOrder(self.username_edit,self.generate_login_toolButton)
        self.setTabOrder(self.generate_login_toolButton,self.password_edit)
        self.setTabOrder(self.password_edit,self.generate_password_toolButton)
        self.setTabOrder(self.generate_password_toolButton,self.firstname_label)
        self.setTabOrder(self.firstname_label,self.lastname_edit)
        self.setTabOrder(self.lastname_edit,self.ballance_edit)
        self.setTabOrder(self.ballance_edit,self.credit_edit)
        self.setTabOrder(self.credit_edit,self.suspended_edit)
        self.setTabOrder(self.suspended_edit,self.address_edit)
        self.setTabOrder(self.address_edit,self.status_edit)
        self.setTabOrder(self.status_edit,self.nas_edit)
        self.setTabOrder(self.nas_edit,self.assign_ipn_ip_from_dhcp_edit)
        self.setTabOrder(self.assign_ipn_ip_from_dhcp_edit,self.ipn_dhcp_pool_edit)
        self.setTabOrder(self.ipn_dhcp_pool_edit,self.assign_ipn_address_toolButton)
        self.setTabOrder(self.assign_ipn_address_toolButton,self.ipn_ip_address_edit)
        self.setTabOrder(self.ipn_ip_address_edit,self.ipn_mac_address_edit)
        self.setTabOrder(self.ipn_mac_address_edit,self.get_mac_address_toolButton)
        self.setTabOrder(self.get_mac_address_toolButton,self.assign_vpn_ip_from_dhcp_edit)
        self.setTabOrder(self.assign_vpn_ip_from_dhcp_edit,self.vpn_dhcp_pool_edit)
        self.setTabOrder(self.vpn_dhcp_pool_edit,self.assign_vpn_address_toolButton)
        self.setTabOrder(self.assign_vpn_address_toolButton,self.vpn_ip_address_edit)
        self.setTabOrder(self.vpn_ip_address_edit,self.add_accounttarif_toolButton)
        self.setTabOrder(self.add_accounttarif_toolButton,self.del_accounttarif_toolButton)
        self.setTabOrder(self.del_accounttarif_toolButton,self.accounttarif_table)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


        self.accounttarif_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.accounttarif_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.accounttarif_table.setSelectionMode(QTableWidget.SingleSelection)

    def getSelectedId(self):
        return int(self.accounttarif_table.item(self.accounttarif_table.currentRow(), 0).text())

    def add_accounttarif(self):

        child=AddAccountTarif(self.model)
        child.exec_()
        self.accountTarifRefresh()

    def del_accounttarif(self):
        i=self.getSelectedId()
        try:
            model=AccountTarif.objects.get(id=i)
        except:
            return

        if model.datetime<datetime.datetime.now():
            QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            model.delete()
        self.accountTarifRefresh()

    def edit_accounttarif(self):
        i=self.getSelectedId()
        try:
            model=AccountTarif.objects.get(id=i)
        except:
            return

        if model.datetime<datetime.datetime.now():
            QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        child=AddAccountTarif(account=self.model, model=model)
        child.exec_()
        self.accountTarifRefresh()




    def generate_login(self):
        self.username_edit.setText(nameGen())

    def generate_password(self):
        self.password_edit.setText(GenPasswd2())

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.address_label.setText(QtGui.QApplication.translate("Dialog", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.status_edit.setText(QtGui.QApplication.translate("Dialog", "Включен", None, QtGui.QApplication.UnicodeUTF8))
        self.suspended_edit.setText(QtGui.QApplication.translate("Dialog", "Не производить списывание денег по периодическим услугам", None, QtGui.QApplication.UnicodeUTF8))
        self.ballance_label.setText(QtGui.QApplication.translate("Dialog", "Текущий балланс", None, QtGui.QApplication.UnicodeUTF8))
        self.credit_label.setText(QtGui.QApplication.translate("Dialog", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.username_label.setText(QtGui.QApplication.translate("Dialog", "<b>Логин</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.generate_login_toolButton.setText(QtGui.QApplication.translate("Dialog", "Сгенерировать", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("Dialog", "<b>Пароль</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.generate_password_toolButton.setText(QtGui.QApplication.translate("Dialog", "Сгенерировать", None, QtGui.QApplication.UnicodeUTF8))
        self.firstname_label.setText(QtGui.QApplication.translate("Dialog", "<b>Имя</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.lastname_label.setText(QtGui.QApplication.translate("Dialog", "<b>Фамилия</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Аккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.ip_settings_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "IP Адреса", None, QtGui.QApplication.UnicodeUTF8))
        self.assign_ipn_ip_from_dhcp_edit.setText(QtGui.QApplication.translate("Dialog", "Выдавать IP адрес с помощью DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_dhcp_pool_label.setText(QtGui.QApplication.translate("Dialog", "DHCP пул", None, QtGui.QApplication.UnicodeUTF8))
        self.assign_ipn_address_toolButton.setText(QtGui.QApplication.translate("Dialog", "Назначить адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_ip_address_label.setText(QtGui.QApplication.translate("Dialog", "Текущий IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_ip_address_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_mac_address_label.setText(QtGui.QApplication.translate("Dialog", "Аппаратный адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.ipn_mac_address_edit.setInputMask(QtGui.QApplication.translate("Dialog", "00:00:00:00:00:00;0", None, QtGui.QApplication.UnicodeUTF8))
        self.get_mac_address_toolButton.setText(QtGui.QApplication.translate("Dialog", "Получить", None, QtGui.QApplication.UnicodeUTF8))
        self.assign_vpn_ip_from_dhcp_edit.setText(QtGui.QApplication.translate("Dialog", "Выдавать VPN адрес с помощью DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_dhcp_pool_label.setText(QtGui.QApplication.translate("Dialog", "DHCP пул", None, QtGui.QApplication.UnicodeUTF8))
        self.assign_vpn_address_toolButton.setText(QtGui.QApplication.translate("Dialog", "Назначить адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_ip_address_label.setText(QtGui.QApplication.translate("Dialog", "Текущий VPN адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.vpn_ip_address_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Настройки доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.clear()
        self.accounttarif_table.setColumnCount(4)


        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(0,headerItem)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("Dialog", "Тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(1,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("Dialog", "Дата ", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(2,headerItem1)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("Dialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(3,headerItem1)


        self.add_accounttarif_toolButton.setText(QtGui.QApplication.translate("Dialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.del_accounttarif_toolButton.setText(QtGui.QApplication.translate("Dialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Здесь вы можете просмотреть историю тарифных планов\n"
        " пользователя и создать задания для перехода на\n"
        " новые тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "История тарифных планов", None, QtGui.QApplication.UnicodeUTF8))


        self.fixtures()

    @transaction.commit_manually
    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:

            model=self.model
            if self.username_edit.text()!=model.username:
                if User.objects.filter(username=unicode(self.username_edit.text())).count()>0 or Account.objects.filter(username=unicode(self.username_edit.text())).count()>0:
                    QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                    return
            model.user.username=unicode(self.username_edit.text())
        else:
            print 'New account'
            if User.objects.filter(username=unicode(self.username_edit.text())).count()>0 or Account.objects.filter(username=unicode(self.username_edit.text())).count()>0:
                QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                return

            model=Account()
            model.user = User.objects.create(username=unicode(self.username_edit.text()), password=unicode(self.password_edit.text()))


        model.username = unicode(self.username_edit.text())

        model.password = unicode(self.password_edit.text())
        model.firstname = unicode(self.firstname_edit.text())
        model.lastname = unicode(self.lastname_edit.text())
        model.address = unicode(self.address_edit.toPlainText())


        if unicode(self.ipn_ip_address_edit.text())==u"...":
            value = None
        else:
            if (self.ipn_ip_address_edit.text()!=model.ipn_ip_address or model.ipn_ip_address==None) and  Account.objects.filter(ipn_ip_address=unicode(self.ipn_ip_address_edit.text())).count()>0:
               QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
               return
            value = unicode(self.ipn_ip_address_edit.text())

        model.ipn_ip_address = value


        if unicode(self.vpn_ip_address_edit.text()) == u'...':
            value = None
        else:
            if (model.vpn_ip_address!=self.vpn_ip_address_edit.text() or model.vpn_ip_address==None) and  Account.objects.filter(vpn_ip_address=unicode(self.vpn_ip_address_edit.text())).count()>0:
               QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой IP."))
               return
            value = unicode(self.vpn_ip_address_edit.text())

        model.vpn_ip_address = value


        if unicode(self.ipn_mac_address_edit.text()) == u'00:00:00:00:00:00':
            value = None
        else:
            if (model.ipn_mac_address!=self.ipn_mac_address_edit.text() and self.ipn_mac_address_edit.text()!= '00:00:00:00:00:00') and  Account.objects.filter(ipn_mac_address=unicode(self.ipn_mac_address_edit.text())).count()>0:
               QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC адрес."))
               return

            value = unicode(self.ipn_mac_address_edit.text())

        model.ipn_mac_address = value

        model.nas = Nas.objects.get(name=str(self.nas_edit.currentText()))

        model.ballance = unicode(self.ballance_edit.text())
        model.credit = unicode(self.credit_edit.text())

        model.assign_ipn_ip_from_dhcp = self.assign_ipn_ip_from_dhcp_edit.checkState() == 2
        model.assign_vpn_ip_from_dhcp = self.assign_vpn_ip_from_dhcp_edit.checkState() == 2
        model.suspended = self.suspended_edit.checkState() == 2
        model.status = self.status_edit.checkState() == 2

        try:
            model.save()
            transaction.commit()
        except Exception, e:
            transaction.rollback()
            return



        QDialog.accept(self)

    def fixtures(self):


        #users = User.objects.all()
        #for user in users:
        #    self.user_edit.addItem(user.username)

        pools = IPAddressPool.objects.all()

        for pool in pools:
            self.ipn_pool_edit.addItem(pool.name)
            self.vpn_pool_edit.addItem(pool.name)

        nasses = Nas.objects.all()
        for nas in nasses:
            self.nas_edit.addItem(nas.name)

        if self.model:
            self.username_edit.setText(unicode(self.model.username))

            self.nas_edit.setCurrentIndex(self.nas_edit.findText(self.model.nas.name, QtCore.Qt.MatchCaseSensitive))

            if self.model.vpn_pool:
                self.vpn_pool_edit.setCurrentIndex(self.vpn_pool_edit.findText(self.model.vpn_pool.name, QtCore.Qt.MatchFlags())[0])

            if self.model.ipn_pool:
                self.ipn_pool_edit.setCurrentIndex(self.ipn_pool_edit.findText(self.model.ipn_pool.name, QtCore.Qt.MatchFlags())[0])

            self.password_edit.setText(unicode(self.model.password))
            self.firstname_edit.setText(unicode(self.model.firstname))
            self.lastname_edit.setText(unicode(self.model.lastname))
            self.address_edit.setText(unicode(self.model.address))
            self.ipn_ip_address_edit.setText(unicode(self.model.ipn_ip_address))
            self.vpn_ip_address_edit.setText(unicode(self.model.vpn_ip_address))
            self.ipn_mac_address_edit.setText(unicode(self.model.ipn_mac_address))


            self.status_edit.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.suspended_edit.setCheckState(self.model.suspended == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )


            self.ballance_edit.setText(unicode(self.model.ballance))
            self.credit_edit.setText(unicode(self.model.credit))

            self.assign_ipn_ip_from_dhcp_edit.setCheckState(self.model.assign_ipn_ip_from_dhcp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.assign_vpn_ip_from_dhcp_edit.setCheckState(self.model.assign_vpn_ip_from_dhcp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.accountTarifRefresh()

    def accountTarifRefresh(self):
        if self.model:
            ac=AccountTarif.objects.filter(account=self.model).order_by('datetime')
            self.accounttarif_table.setRowCount(ac.count())
            i=0
            for a in ac:

                self.addrow(a.id, i,0)
                self.addrow(a.tarif.name, i,1)
                self.addrow(a.datetime.strftime("%d-%m-%Y %H:%M:%S"), i,2)
                self.accounttarif_table.setRowHeight(i, 17)
                self.accounttarif_table.setColumnHidden(0, True)
                i+=1
            #self.tabWidget.resizeColumnsToContents()


    def save(self):
        print 'Saved'

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        headerItem.setText(unicode(value))
        self.accounttarif_table.setItem(x,y,headerItem)



class AccountsMdiChild(QMainWindow):
    sequenceNumber = 1

    def __init__(self):
        super(AccountsMdiChild, self).__init__()

        self.setWindowTitle(u"Пользователи")
        
        self.centralwidget = QtGui.QWidget(self)
        
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0,0,691,411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        
        self.tarif_treeWidget = QtGui.QTreeWidget(self.splitter)
        self.tarif_treeWidget.setGeometry(QtCore.QRect(0,0,221,551))
        self.tarif_treeWidget.setMaximumSize(QtCore.QSize(150,16777215))
        self.tarif_treeWidget.setObjectName("tarif_treeWidget")
        self.tarif_treeWidget.headerItem().setText(0,"")
        
        tree_header = self.tarif_treeWidget.headerItem()
        tree_header.setHidden(True)


        self.tableWidget = QTableWidget(self.splitter)

        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        #self.tablewidget.setSortingEnabled(True)
        vh = self.tableWidget.verticalHeader()
        vh.setVisible(False)

        hh = self.tableWidget.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        #hh.setClickable(False)
        hh.ResizeMode(QtGui.QHeaderView.Stretch)
        #hh.setCascadingSectionResizes(True)
        hh.setMovable(True)
        hh.setOffset(200)


        columns=[u'id', u'Имя пользователя', u'Балланс', u'Кредит', u'Имя', u'Фамилия', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u'Без ПУ', u'Статус в системе', u""]
        
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)
        self.setCentralWidget(self.splitter)


        self.statusbar = QStatusBar(self)
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

        self.addTarifAction = QtGui.QAction(self)
        self.addTarifAction.setIcon(QtGui.QIcon("images/add.png"))
        
        self.delTarifAction = QtGui.QAction(self)
        self.delTarifAction.setIcon(QtGui.QIcon("images/del.png"))
        
        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addTarifAction)
        self.toolBar.addAction(self.delTarifAction)        

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.tableWidget.resizeColumnsToContents()
        self.resize(1100,600)



        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        
        self.connect(self.addTarifAction, QtCore.SIGNAL("triggered()"), self.addTarif)
        self.connect(self.delTarifAction, QtCore.SIGNAL("triggered()"), self.delTarif)
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        
        self.connect(self.tarif_treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
                     
        self.retranslateUi()
        self.refresh()
        self.refreshTree()
        
    def retranslateUi(self):
        self.tarif_treeWidget.clear()

#===============================================================================
#        item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
#        item.setText(0,QtGui.QApplication.translate("MainWindow", "Анлим 20", None, QtGui.QApplication.UnicodeUTF8))
# 
#        item1 = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
#        item1.setText(0,QtGui.QApplication.translate("MainWindow", "Анлим 15", None, QtGui.QApplication.UnicodeUTF8))
# 
#        item2 = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
#        item2.setText(0,QtGui.QApplication.translate("MainWindow", "Траффик 60", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================

    def addTarif(self):
        tarifframe = TarifFrame()
        tarifframe.exec_()
        self.refresh()
        
    
    def delTarif(self):
        pass
    
    def editTarif(self, item, num):
        model = Tariff.objects.get(name=unicode(item.text(0)))
        tarifframe = TarifFrame(model=model)
        tarifframe.exec_()
        self.refresh()
        #print num

    def addframe(self):

        model = None
        addf = AddAccountFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        id=self.getSelectedId()
        if id>0 and QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить пользователя из системы?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                model = Account.objects.get(id=self.getSelectedId())
                model.delete()
                model.user.delete()
            except Exception, e:
                print e
        self.refresh()


    def editframe(self):
        id=self.getSelectedId()
        if id == 0:
            return
        try:
            model = Account.objects.get(id=self.getSelectedId())
        except:
            model = None

        addf = AddAccountFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y, color=None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if int(value)<0:
                headerItem.setBackgroundColor(QColor(color))

        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)

    def refreshTree(self):
        self.tarif_treeWidget.clear()
        tariffs = Tariff.objects.all().order_by("id")
        for tarif in tariffs:
            item = QtGui.QTreeWidgetItem(self.tarif_treeWidget)
            item.setText(0, u"%s" % tarif.name)
            
    def refresh(self):

        accounts=Account.objects.all().order_by('id')
        self.tableWidget.setRowCount(accounts.count())
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for a in accounts:
            self.addrow(a.id, i,0)
            #self.addrow(a.user, i,1)
            self.addrow(a.username, i,1)
            self.addrow(a.ballance, i,2, color="red")
            self.addrow(a.credit, i,3)
            self.addrow(a.firstname, i,4)
            self.addrow(a.lastname, i,5)
            self.addrow(a.nas.name,i,6)
            self.addrow(a.vpn_ip_address, i,7)
            self.addrow(a.ipn_ip_address, i,8)
            self.addrow(a.suspended, i,9)
            self.addrow(a.status, i,10)
            self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)

            i+=1
        #self.tableWidget.resizeColumnsToContents()

    def newFile(self):
        self.isUntitled = True
        #self.curFile = self.tr("iplist").arg(MdiChild.sequenceNumber)
        #MdiChild.sequenceNumber += 1
        #self.setWindowTitle(self.curFile+"[*]")

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                        self.tr("Cannot read file %1:\n%2.")
                        .arg(fileName)
                        .arg(file.errorString()))
            return False

        instr = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPlainText(instr.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def save(self):
        if self.isUntitled:
            return self.saveAs()
        else:
            return self.saveFile(self.curFile)

    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),
                        self.curFile)
        if fileName.isEmpty:
            return False

        return self.saveFile(fileName)

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)

        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("Cannot write file %1:\n%2.")
                    .arg(fileName)
                    .arg(file.errorString()))
            return False

        outstr = QtCore.QTextStream(file)
        QtCore.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outstr << self.toPlainText()
        QtCore.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def userFriendlyCurrentFile(self):
        return self.strippedName(self.curFile)

    def currentFile(self):
        return self.curFile

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def documentWasModified(self):
        self.setWindowModified(self.document().isModified())

    def maybeSave(self):
        if self.document().isModified():
            ret = QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("'%1' has been modified.\n"\
                            "Do you want to save your changes?")
                    .arg(self.userFriendlyCurrentFile()),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
            if ret == QtGui.QMessageBox.Yes:
                return self.save()
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def setCurrentFile(self, fileName):
        self.curFile = QtCore.QFileInfo(fileName).canonicalFilePath()
        self.isUntitled = False
        self.document().setModified(False)
        self.setWindowModified(False)
        self.setWindowTitle(self.userFriendlyCurrentFile() + "[*]")

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

