#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import Account, Tariff, AccountTarif
from nas.models import IPAddressPool, Nas
from django.db import transaction
from randgen import nameGen, GenPasswd2
import datetime, time, calendar

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

            now.setTime_t(calendar.timegm(self.model.datetime.timetuple()))
        self.date_edit.setDateTime(now)


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
        self.accounttarif_table.setColumnCount(3)


        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("Dialog", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(0,headerItem)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("Dialog", "Тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(1,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("Dialog", "Дата ", None, QtGui.QApplication.UnicodeUTF8))
        self.accounttarif_table.setHorizontalHeaderItem(2,headerItem1)

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
                self.addrow(a.datetime, i,2)
                self.accounttarif_table.setRowHeight(i, 17)
                self.accounttarif_table.setColumnHidden(0, True)
                i+=1
            #self.accounttarif_table.resizeColumnsToContents()


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


        self.tableWidget = QTableWidget()

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


        columns=[u'id', u'Имя пользователя', u'Балланс', u'Кредит', u'Имя', u'Фамилия', u'Сервер доступа', u'VPN IP адрес', u'IPN IP адрес', u'Без ПУ', u'Статус в системе']
        i=0
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)
        self.setCentralWidget(self.tableWidget)


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

        self.toolBar.addAction(self.addAction)
        self.toolBar.addAction(self.delAction)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.tableWidget.resizeColumnsToContents()
        self.resize(1100,600)



        self.connect(self.addAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delAction, QtCore.SIGNAL("triggered()"), self.delete)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.refresh()


    def addframe(self):

        model=None
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
                model=Account.objects.get(id=self.getSelectedId())
                model.delete()
                model.user.delete()
            except Exception, e:
                print e
        self.refresh()


    def editframe(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=Account.objects.get(id=self.getSelectedId())
        except:
            model=None

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

