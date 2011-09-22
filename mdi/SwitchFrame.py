#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil
from customwidget import CustomDateTimeWidget



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class SwitchMainWindow(QtGui.QMainWindow):
    def __init__(self, parent, connection, model=None):
        super(SwitchMainWindow, self).__init__()
        self.connection=connection
        self.model=model
        self.parent_window=parent
        self.setObjectName(_fromUtf8("SwitchMainWindow"))

        self.resize(659, 644)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_7 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout = QtGui.QGridLayout(self.tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_device = QtGui.QGroupBox(self.tab)
        self.groupBox_device.setObjectName(_fromUtf8("groupBox_device"))
        self.gridLayout_8 = QtGui.QGridLayout(self.groupBox_device)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.label_manufacturer = QtGui.QLabel(self.groupBox_device)
        self.label_manufacturer.setObjectName(_fromUtf8("label_manufacturer"))
        self.gridLayout_8.addWidget(self.label_manufacturer, 0, 0, 1, 1)
        self.lineEdit_manufacturer = QtGui.QLineEdit(self.groupBox_device)
        self.lineEdit_manufacturer.setObjectName(_fromUtf8("lineEdit_manufacturer"))
        self.gridLayout_8.addWidget(self.lineEdit_manufacturer, 0, 1, 1, 1)
        self.label_model = QtGui.QLabel(self.groupBox_device)
        self.label_model.setObjectName(_fromUtf8("label_model"))
        self.gridLayout_8.addWidget(self.label_model, 1, 0, 1, 1)
        self.lineEdit_model = QtGui.QLineEdit(self.groupBox_device)
        self.lineEdit_model.setObjectName(_fromUtf8("lineEdit_model"))
        self.gridLayout_8.addWidget(self.lineEdit_model, 1, 1, 1, 1)
        self.label_sn = QtGui.QLabel(self.groupBox_device)
        self.label_sn.setObjectName(_fromUtf8("label_sn"))
        self.gridLayout_8.addWidget(self.label_sn, 2, 0, 1, 1)
        self.lineEdit_sn = QtGui.QLineEdit(self.groupBox_device)
        self.lineEdit_sn.setObjectName(_fromUtf8("lineEdit_sn"))
        self.gridLayout_8.addWidget(self.lineEdit_sn, 2, 1, 1, 1)
        self.lineEdit_comment = QtGui.QLineEdit(self.groupBox_device)
        self.lineEdit_comment.setObjectName(_fromUtf8("lineEdit_comment"))
        self.gridLayout_8.addWidget(self.lineEdit_comment, 3, 1, 1, 1)
        self.label_comment = QtGui.QLabel(self.groupBox_device)
        self.label_comment.setObjectName(_fromUtf8("label_comment"))
        self.gridLayout_8.addWidget(self.label_comment, 3, 0, 1, 1)
        self.spinBox_ports_num = QtGui.QSpinBox(self.groupBox_device)
        self.spinBox_ports_num.setObjectName(_fromUtf8("spinBox_ports_num"))
        self.gridLayout_8.addWidget(self.spinBox_ports_num, 4, 1, 1, 1)
        self.label_ports_num = QtGui.QLabel(self.groupBox_device)
        self.label_ports_num.setObjectName(_fromUtf8("label_ports_num"))
        self.gridLayout_8.addWidget(self.label_ports_num, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_device, 0, 0, 1, 3)
        self.groupBox_management = QtGui.QGroupBox(self.tab)
        self.groupBox_management.setObjectName(_fromUtf8("groupBox_management"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_management)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_management_method = QtGui.QLabel(self.groupBox_management)
        self.label_management_method.setObjectName(_fromUtf8("label_management_method"))
        self.gridLayout_3.addWidget(self.label_management_method, 0, 0, 1, 1)
        self.comboBox_management_method = QtGui.QComboBox(self.groupBox_management)
        self.comboBox_management_method.setObjectName(_fromUtf8("comboBox_management_method"))
        self.gridLayout_3.addWidget(self.comboBox_management_method, 0, 1, 1, 1)
        self.label_username = QtGui.QLabel(self.groupBox_management)
        self.label_username.setObjectName(_fromUtf8("label_username"))
        self.gridLayout_3.addWidget(self.label_username, 1, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox_management)
        self.lineEdit_username.setObjectName(_fromUtf8("lineEdit_username"))
        self.gridLayout_3.addWidget(self.lineEdit_username, 1, 1, 1, 1)
        self.label_password = QtGui.QLabel(self.groupBox_management)
        self.label_password.setObjectName(_fromUtf8("label_password"))
        self.gridLayout_3.addWidget(self.label_password, 2, 0, 1, 1)
        self.lineEdit_password = QtGui.QLineEdit(self.groupBox_management)
        self.lineEdit_password.setObjectName(_fromUtf8("lineEdit_password"))
        self.gridLayout_3.addWidget(self.lineEdit_password, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_management, 2, 2, 1, 1)
        self.groupBox_snmp_support = QtGui.QGroupBox(self.tab)
        self.groupBox_snmp_support.setCheckable(True)
        self.groupBox_snmp_support.setObjectName(_fromUtf8("groupBox_snmp_support"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_snmp_support)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_community = QtGui.QLabel(self.groupBox_snmp_support)
        self.label_community.setObjectName(_fromUtf8("label_community"))
        self.gridLayout_4.addWidget(self.label_community, 2, 0, 1, 1)
        self.lineEdit_community = QtGui.QLineEdit(self.groupBox_snmp_support)
        self.lineEdit_community.setObjectName(_fromUtf8("lineEdit_community"))
        self.gridLayout_4.addWidget(self.lineEdit_community, 2, 1, 1, 1)
        self.comboBox_version = QtGui.QComboBox(self.groupBox_snmp_support)
        self.comboBox_version.setObjectName(_fromUtf8("comboBox_version"))
        self.gridLayout_4.addWidget(self.comboBox_version, 1, 1, 1, 1)
        self.label_version = QtGui.QLabel(self.groupBox_snmp_support)
        self.label_version.setObjectName(_fromUtf8("label_version"))
        self.gridLayout_4.addWidget(self.label_version, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_snmp_support, 4, 2, 1, 1)
        self.groupBox_address = QtGui.QGroupBox(self.tab)
        self.groupBox_address.setObjectName(_fromUtf8("groupBox_address"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_address)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_city_2 = QtGui.QLabel(self.groupBox_address)
        self.label_city_2.setObjectName(_fromUtf8("label_city_2"))
        self.gridLayout_6.addWidget(self.label_city_2, 2, 0, 1, 1)
        self.comboBox_street = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_street.setObjectName(_fromUtf8("comboBox_street"))
        self.gridLayout_6.addWidget(self.comboBox_street, 2, 1, 1, 1)
        self.label_city_3 = QtGui.QLabel(self.groupBox_address)
        self.label_city_3.setObjectName(_fromUtf8("label_city_3"))
        self.gridLayout_6.addWidget(self.label_city_3, 3, 0, 1, 1)
        self.comboBox_house = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_house.setObjectName(_fromUtf8("comboBox_house"))
        self.gridLayout_6.addWidget(self.comboBox_house, 3, 1, 1, 1)
        self.label_place = QtGui.QLabel(self.groupBox_address)
        self.label_place.setObjectName(_fromUtf8("label_place"))
        self.gridLayout_6.addWidget(self.label_place, 4, 0, 1, 1)
        self.lineEdit_place = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_place.setObjectName(_fromUtf8("lineEdit_place"))
        self.gridLayout_6.addWidget(self.lineEdit_place, 4, 1, 1, 1)
        self.comboBox_city = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_city.setObjectName(_fromUtf8("comboBox_city"))
        self.gridLayout_6.addWidget(self.comboBox_city, 1, 1, 1, 1)
        self.label_city = QtGui.QLabel(self.groupBox_address)
        self.label_city.setObjectName(_fromUtf8("label_city"))
        self.gridLayout_6.addWidget(self.label_city, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_address, 1, 0, 1, 3)
        self.groupBox_option82 = QtGui.QGroupBox(self.tab)
        self.groupBox_option82.setCheckable(True)
        self.groupBox_option82.setObjectName(_fromUtf8("groupBox_option82"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_option82)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_option82_auth_type = QtGui.QLabel(self.groupBox_option82)
        self.label_option82_auth_type.setObjectName(_fromUtf8("label_option82_auth_type"))
        self.gridLayout_5.addWidget(self.label_option82_auth_type, 0, 0, 1, 1)
        self.comboBox_option82_auth_type = QtGui.QComboBox(self.groupBox_option82)
        self.comboBox_option82_auth_type.setObjectName(_fromUtf8("comboBox_option82_auth_type"))
        self.gridLayout_5.addWidget(self.comboBox_option82_auth_type, 0, 1, 1, 1)
        self.comboBox_option82_template = QtGui.QComboBox(self.groupBox_option82)
        self.comboBox_option82_template.setObjectName(_fromUtf8("comboBox_option82_template"))
        self.gridLayout_5.addWidget(self.comboBox_option82_template, 1, 1, 1, 1)
        self.label_option82_template = QtGui.QLabel(self.groupBox_option82)
        self.label_option82_template.setObjectName(_fromUtf8("label_option82_template"))
        self.gridLayout_5.addWidget(self.label_option82_template, 1, 0, 1, 1)
        self.label_remote_id = QtGui.QLabel(self.groupBox_option82)
        self.label_remote_id.setObjectName(_fromUtf8("label_remote_id"))
        self.gridLayout_5.addWidget(self.label_remote_id, 2, 0, 1, 1)
        self.lineEdit_remote_id = QtGui.QLineEdit(self.groupBox_option82)
        self.lineEdit_remote_id.setObjectName(_fromUtf8("lineEdit_remote_id"))
        self.gridLayout_5.addWidget(self.lineEdit_remote_id, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_option82, 4, 1, 1, 1)
        self.groupBox_network_identify = QtGui.QGroupBox(self.tab)
        self.groupBox_network_identify.setObjectName(_fromUtf8("groupBox_network_identify"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_network_identify)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_ipaddress = QtGui.QLabel(self.groupBox_network_identify)
        self.label_ipaddress.setObjectName(_fromUtf8("label_ipaddress"))
        self.gridLayout_2.addWidget(self.label_ipaddress, 0, 0, 1, 1)
        self.lineEdit_ipaddress = QtGui.QLineEdit(self.groupBox_network_identify)
        self.lineEdit_ipaddress.setObjectName(_fromUtf8("lineEdit_ipaddress"))
        self.gridLayout_2.addWidget(self.lineEdit_ipaddress, 0, 2, 1, 1)
        self.label_macaddress = QtGui.QLabel(self.groupBox_network_identify)
        self.label_macaddress.setObjectName(_fromUtf8("label_macaddress"))
        self.gridLayout_2.addWidget(self.label_macaddress, 1, 0, 1, 2)
        self.lineEdit_macaddress = QtGui.QLineEdit(self.groupBox_network_identify)
        self.lineEdit_macaddress.setObjectName(_fromUtf8("lineEdit_macaddress"))
        self.gridLayout_2.addWidget(self.lineEdit_macaddress, 1, 2, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox_network_identify)
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.gridLayout_2.addWidget(self.lineEdit_name, 2, 2, 1, 1)
        self.label_name = QtGui.QLabel(self.groupBox_network_identify)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout_2.addWidget(self.label_name, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_network_identify, 2, 1, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_10 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.groupBox_ports_management = QtGui.QGroupBox(self.tab_2)
        self.groupBox_ports_management.setObjectName(_fromUtf8("groupBox_ports_management"))
        self.gridLayout_11 = QtGui.QGridLayout(self.groupBox_ports_management)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.label_enable_port_command = QtGui.QLabel(self.groupBox_ports_management)
        self.label_enable_port_command.setObjectName(_fromUtf8("label_enable_port_command"))
        self.gridLayout_11.addWidget(self.label_enable_port_command, 0, 0, 1, 1)
        self.lineEdit_enable_port_command = QtGui.QLineEdit(self.groupBox_ports_management)
        self.lineEdit_enable_port_command.setObjectName(_fromUtf8("lineEdit_enable_port_command"))
        self.gridLayout_11.addWidget(self.lineEdit_enable_port_command, 0, 1, 1, 1)
        self.label_disable_port_command = QtGui.QLabel(self.groupBox_ports_management)
        self.label_disable_port_command.setObjectName(_fromUtf8("label_disable_port_command"))
        self.gridLayout_11.addWidget(self.label_disable_port_command, 1, 0, 1, 1)
        self.lineEdit_disable_port_command = QtGui.QLineEdit(self.groupBox_ports_management)
        self.lineEdit_disable_port_command.setObjectName(_fromUtf8("lineEdit_disable_port_command"))
        self.gridLayout_11.addWidget(self.lineEdit_disable_port_command, 1, 1, 1, 1)
        self.gridLayout_10.addWidget(self.groupBox_ports_management, 0, 0, 1, 1)
        self.groupBox_ports_status = QtGui.QGroupBox(self.tab_2)
        self.groupBox_ports_status.setObjectName(_fromUtf8("groupBox_ports_status"))
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_ports_status)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.tableWidget = QtGui.QTableWidget(self.groupBox_ports_status)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget-switch_prop"))
        self.tableWidget=tableFormat(self.tableWidget)

        self.gridLayout_9.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_10.addWidget(self.groupBox_ports_status, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout_7.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.actionSave = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave.setObjectName("actionSave")
        self.toolBar.addAction(self.actionSave)
        
        self.actionRefreshTable = QtGui.QAction(self)
        self.actionRefreshTable = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/reload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefreshTable.setIcon(icon1)
        self.actionRefreshTable.setObjectName("actionRefreshTable")
        self.toolBar.addAction(self.actionRefreshTable)
        
        
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.tabWidget, self.lineEdit_manufacturer)
        self.setTabOrder(self.lineEdit_manufacturer, self.lineEdit_model)
        self.setTabOrder(self.lineEdit_model, self.lineEdit_sn)
        self.setTabOrder(self.lineEdit_sn, self.lineEdit_comment)
        self.setTabOrder(self.lineEdit_comment, self.spinBox_ports_num)
        self.setTabOrder(self.spinBox_ports_num, self.comboBox_city)
        self.setTabOrder(self.comboBox_city, self.comboBox_street)
        self.setTabOrder(self.comboBox_street, self.comboBox_house)
        self.setTabOrder(self.comboBox_house, self.lineEdit_place)
        self.setTabOrder(self.lineEdit_place, self.lineEdit_ipaddress)
        self.setTabOrder(self.lineEdit_ipaddress, self.lineEdit_macaddress)
        self.setTabOrder(self.lineEdit_macaddress, self.lineEdit_name)
        self.setTabOrder(self.lineEdit_name, self.comboBox_management_method)
        self.setTabOrder(self.comboBox_management_method, self.lineEdit_username)
        self.setTabOrder(self.lineEdit_username, self.lineEdit_password)
        self.setTabOrder(self.lineEdit_password, self.groupBox_option82)
        self.setTabOrder(self.groupBox_option82, self.comboBox_option82_auth_type)
        self.setTabOrder(self.comboBox_option82_auth_type, self.comboBox_option82_template)
        self.setTabOrder(self.comboBox_option82_template, self.lineEdit_remote_id)
        self.setTabOrder(self.lineEdit_remote_id, self.groupBox_snmp_support)
        self.setTabOrder(self.groupBox_snmp_support, self.comboBox_version)
        self.setTabOrder(self.comboBox_version, self.lineEdit_community)
        self.setTabOrder(self.lineEdit_community, self.lineEdit_enable_port_command)
        self.setTabOrder(self.lineEdit_enable_port_command, self.lineEdit_disable_port_command)
        self.setTabOrder(self.lineEdit_disable_port_command, self.tableWidget)
        
        
        bhdr = HeaderUtil.getBinaryHeader(self.tableWidget.objectName())
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.tableWidget.objectName(), bhdr)
            HeaderUtil.getHeader(self.tableWidget.objectName(), self.tableWidget)
        else:
            
            HeaderUtil.nullifySaved(self.tableWidget.objectName())
        self.fixtures()
        self.connect(self.comboBox_city, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_street)
        self.connect(self.comboBox_street, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_house)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        self.connect(self.actionRefreshTable, QtCore.SIGNAL("triggered()"),  self.fill_ports)
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("SwitchMainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_device.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Данные о устройстве", None, QtGui.QApplication.UnicodeUTF8))
        self.label_manufacturer.setText(QtGui.QApplication.translate("SwitchMainWindow", "Производитель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_model.setText(QtGui.QApplication.translate("SwitchMainWindow", "Модель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sn.setText(QtGui.QApplication.translate("SwitchMainWindow", "Серийный номер", None, QtGui.QApplication.UnicodeUTF8))
        self.label_comment.setText(QtGui.QApplication.translate("SwitchMainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ports_num.setText(QtGui.QApplication.translate("SwitchMainWindow", "Количество портов", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_management.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Управление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_management_method.setText(QtGui.QApplication.translate("SwitchMainWindow", "Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("SwitchMainWindow", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.label_password.setText(QtGui.QApplication.translate("SwitchMainWindow", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_snmp_support.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Поддержка snmp", None, QtGui.QApplication.UnicodeUTF8))
        self.label_community.setText(QtGui.QApplication.translate("SwitchMainWindow", "Комьюнити", None, QtGui.QApplication.UnicodeUTF8))
        self.label_version.setText(QtGui.QApplication.translate("SwitchMainWindow", "Версия", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_address.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Адрес установки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city_2.setText(QtGui.QApplication.translate("SwitchMainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city_3.setText(QtGui.QApplication.translate("SwitchMainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_place.setText(QtGui.QApplication.translate("SwitchMainWindow", "Место установки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("SwitchMainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_option82.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Опция 82", None, QtGui.QApplication.UnicodeUTF8))
        self.label_option82_auth_type.setText(QtGui.QApplication.translate("SwitchMainWindow", "Способ авторизации", None, QtGui.QApplication.UnicodeUTF8))
        self.label_option82_template.setText(QtGui.QApplication.translate("SwitchMainWindow", "Шаблон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_remote_id.setText(QtGui.QApplication.translate("SwitchMainWindow", "Remote-ID", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_network_identify.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Сетевая идентификация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipaddress.setText(QtGui.QApplication.translate("SwitchMainWindow", "IP адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_macaddress.setText(QtGui.QApplication.translate("SwitchMainWindow", "MAC адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("SwitchMainWindow", "Идентификатор", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("SwitchMainWindow", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ports_management.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Telnet/SSH команды управления портом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_enable_port_command.setText(QtGui.QApplication.translate("SwitchMainWindow", "Включить порт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_disable_port_command.setText(QtGui.QApplication.translate("SwitchMainWindow", "Отключить порт", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ports_status.setTitle(QtGui.QApplication.translate("SwitchMainWindow", "Параметры портов", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("SwitchMainWindow", "Управление", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("SwitchMainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setToolTip(u"Сохранить изменения")
        self.actionRefreshTable.setToolTip(u"Получить состояние портов с коммутаторе")
        columns = [u"Порт", u"Скорость", u"Включен", u"Аплинк", u"Защита", u"Битый"]
        makeHeaders(columns, self.tableWidget)

    def saveHeader(self, *args):

        HeaderUtil.saveHeader(self.tableWidget.objectName(), self.tableWidget)
        
    def refresh_combo_street(self):
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if city_id==0:
            self.comboBox_street.clear()
        if not city_id: return
        streets = self.connection.sql("SELECT id, name FROM billservice_street WHERE city_id=%s ORDER BY name ASC;" % city_id)
        self.connection.commit()
        self.comboBox_street.clear()
        self.comboBox_house.clear()
        i=0
        for street in streets:
            self.comboBox_street.addItem(street.name, QtCore.QVariant(street.id))
            if self.model:
                if self.model.street_id==street.id:
                    self.comboBox_street.setCurrentIndex(i)
            i+=1

    def refresh_combo_house(self):
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if not street_id: return        
        items = self.connection.sql("SELECT id, name FROM billservice_house WHERE street_id=%s ORDER BY name ASC;" % street_id)
        self.connection.commit()
        self.comboBox_house.clear()
        i=0
        for item in items:
            self.comboBox_house.addItem(item.name, QtCore.QVariant(item.id))
            if self.model:
                if self.model.house_id==item.id:
                    self.comboBox_house.setCurrentIndex(i)
            i+=1
    def addrow(self, value, x, y, checked=None):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        #if y==1:
        #    headerItem.setIcon(QtGui.QIcon("images/switch.png"))
        if checked==True:
            headerItem.setCheckState(QtCore.Qt.Checked)
        elif checked==False:
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        self.tableWidget.setItem(x,y,headerItem)
        
    def fill_ports(self):
        ports_count = self.spinBox_ports_num.value()
        if ports_count==0: return
        print ports_count
        self.tableWidget.setRowCount(ports_count)
        port_speed=['']*ports_count
        if self.model.snmp_support:
            try:
                disabled_ports, port_speed = self.connection.get_ports_status(self.model.id)
            except Exception, e:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Невозможно получить информацию о портах коммутатора. Неверно настоен или не настроен протокол SNMP."))
                disabled_ports = self.model.disabled_ports.split(',')
        else:
            disabled_ports = self.model.disabled_ports.split(',')
        uplink_ports = self.model.uplink_ports.split(',')
        protected_ports = self.model.protected_ports.split(',')
        broken_ports = self.model.broken_ports.split(',')
        for i in xrange(0,ports_count):
            self.addrow(i+1, i, 0)
            self.addrow(port_speed[i], i, 1)
            self.addrow(u'Включен', i, 2, checked=str(i+1) not in disabled_ports)
            self.addrow(u'Аплинк', i, 3, checked=str(i+1) in uplink_ports)
            self.addrow(u'Защита', i, 4, checked=str(i+1) in protected_ports)
            self.addrow(u'Битый', i, 5, checked=str(i+1) in broken_ports)
        
        
        
    def fixtures(self):
        cities = self.connection.sql("SELECT id, name FROM billservice_city ORDER BY name ASC;")
        self.connection.commit()
        self.comboBox_city.clear()
        self.comboBox_city.addItem(u'-Не указан-', QtCore.QVariant(0))
        i=1
        for city in cities:
            self.comboBox_city.addItem(city.name, QtCore.QVariant(city.id))
            if self.model:
                if self.model.city_id==city.id:
                    self.comboBox_city.setCurrentIndex(i)
            i+=1

        self.comboBox_management_method.clear()
        methods=((u"Не управлять",0),(u"SSH",1),(u"SNMP",1),(u"Telnet",2),(u"localhost",3),)
        i=0
        for name, value in methods:
            self.comboBox_management_method.addItem(name, QtCore.QVariant(value))
            if self.model:
                if self.model.management_method==value:
                    self.comboBox_management_method.setCurrentIndex(i)
            i+=1
            

        self.comboBox_version.clear()
        methods=((u"v1",0),(u"v2c",1),)
        i=0
        for name, value in methods:
            self.comboBox_version.addItem(name, QtCore.QVariant(value))
            if self.model:
                if self.model.snmp_version==value:
                    self.comboBox_version.setCurrentIndex(i)
            i+=1

        self.comboBox_option82_auth_type.clear()
        methods=((u"Порт",0),(u"Порт+MAC",1),(u"MAC",2),)
        i=0
        for name, value in methods:
            self.comboBox_option82_auth_type.addItem(name, QtCore.QVariant(value))
            if self.model:
                if self.model.option82_auth_type==value:
                    self.comboBox_option82_auth_type.setCurrentIndex(i)
            i+=1

        self.comboBox_option82_template.clear()
        methods=((u"dlink-32xx",'dlink-32xx'),)
        i=0
        for name, value in methods:
            self.comboBox_option82_template.addItem(name, QtCore.QVariant(value))
            if self.model:
                if self.model.option82_template==value:
                    self.comboBox_option82_template.setCurrentIndex(i)
            i+=1
        self.actionRefreshTable.setDisabled(True)    
        if self.model:
            
            self.refresh_combo_street()
            self.refresh_combo_house()
            self.lineEdit_manufacturer.setText(unicode(self.model.manufacturer))
            self.lineEdit_model.setText(unicode(self.model.model))
            self.lineEdit_comment.setText(unicode(self.model.comment))
            self.lineEdit_name.setText(u"%s" % self.model.name)
            self.lineEdit_manufacturer.setText(u"%s" % self.model.manufacturer)
            self.lineEdit_model.setText(u"%s" % self.model.model)
            self.lineEdit_sn.setText(u"%s" % self.model.sn)
            self.lineEdit_comment.setText(u"%s" % self.model.comment)
            self.lineEdit_place.setText(u"%s" % self.model.place)
            self.lineEdit_community.setText(u"%s" % self.model.snmp_community)
            self.lineEdit_ipaddress.setText(u"%s" % self.model.ipaddress)
            self.lineEdit_macaddress.setText(u"%s" % self.model.macaddress)
            self.lineEdit_username.setText(u"%s" % self.model.username)
            self.lineEdit_password.setText(u"%s" % self.model.password)
            self.lineEdit_remote_id.setText(u"%s" % self.model.remote_id)
            
            self.groupBox_option82.setChecked(self.model.option82)
            self.groupBox_snmp_support.setChecked(self.model.snmp_support)
            self.spinBox_ports_num.setValue(self.model.ports_count)
            
            self.lineEdit_enable_port_command.setText(self.model.enable_port)
            self.lineEdit_disable_port_command.setText(self.model.disable_port)
            
            if self.model.snmp_support:
                self.actionRefreshTable.setDisabled(False)    
            self.fill_ports()
        
    def accept(self):
        if self.model:
            model=self.model
        else:
            model=Object()

        model.name= u"%s" % self.lineEdit_name.text()
        model.manufacturer= u"%s" % self.lineEdit_manufacturer.text()
        model.model= u"%s" % self.lineEdit_model.text()
        model.sn= u"%s" % self.lineEdit_sn.text()
        model.comment= u"%s" % self.lineEdit_comment.text()
        model.place = u"%s" % self.lineEdit_place.text()
        model.snmp_community = u"%s" % self.lineEdit_community.text()
        model.ipaddress =  u"%s" % self.lineEdit_ipaddress.text() or "0.0.0.0"
        model.macaddress =  u"%s" % self.lineEdit_macaddress.text()
        model.username = u"%s" % self.lineEdit_username.text()
        model.password = u"%s" % self.lineEdit_password.text()
        model.enable_port = u"%s" % self.lineEdit_enable_port_command.text() 
        model.disable_port = u"%s" % self.lineEdit_disable_port_command.text()
        model.remote_id = u"%s" % self.lineEdit_remote_id.text()
        
        model.city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0] or None
        model.street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0] or None
        model.house_id = self.comboBox_house.itemData(self.comboBox_house.currentIndex()).toInt()[0] or None
        model.ports_count = self.spinBox_ports_num.value()
        model.management_method = self.comboBox_management_method.itemData(self.comboBox_management_method.currentIndex()).toInt()[0] or None
        model.option82_auth_type = self.comboBox_option82_auth_type.itemData(self.comboBox_option82_auth_type.currentIndex()).toInt()[0] or None
        model.snmp_version = self.comboBox_version.itemData(self.comboBox_version.currentIndex()).toInt()[0] or None
        model.option82_template = unicode(self.comboBox_option82_template.itemData(self.comboBox_option82_template.currentIndex()).toString()[0]) or ''
        
        model.snmp_support = self.groupBox_snmp_support.isChecked()
        
        model.option82 = self.groupBox_option82.isChecked()
        
        disabled_ports=[]
        uplink_ports=[]
        protected_ports=[]
        broken_ports=[]
        for i in xrange(self.tableWidget.rowCount()):
            if self.tableWidget.item(i,2).checkState()==QtCore.Qt.Unchecked:
                disabled_ports.append(i+1)
            if self.tableWidget.item(i,3).checkState()==QtCore.Qt.Checked:
                uplink_ports.append(i+1)
            if self.tableWidget.item(i,4).checkState()==QtCore.Qt.Checked:
                protected_ports.append(i+1)
            if self.tableWidget.item(i,5).checkState()==QtCore.Qt.Checked:
                broken_ports.append(i+1)
                
        print disabled_ports, uplink_ports,protected_ports,broken_ports
        model.disabled_ports=','.join(map(str,disabled_ports))
        model.uplink_ports=','.join(map(str,uplink_ports))
        model.protected_ports=','.join(map(str,protected_ports))
        model.broken_ports=','.join(map(str,broken_ports))
        try:
            self.model=model
            self.model.id=self.connection.save(model, "nas_switch")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        self.parent_window.refresh()



class SwitchEbs(ebsTableWindow):
    def __init__(self, parent, connection):
        columns=['#', u'Производитель', u'Идентификатор', u'Модель', u'IP', u'Место установки', u"Количество портов"]
        initargs = {"setname":"switch_window", "objname":"SwitchEbs", "winsize":(0,0,827,476), "wintitle":"Коммутаторы", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(SwitchEbs, self).__init__(connection, initargs)
        self.parent=parent
        
    def ebsInterInit(self, initargs):
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,827,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def ebsPostInit(self, initargs):
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_window)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.add_window), ("editAction", "Настройки", "images/open.png", self.edit_window), ("delAction", "Удалить", "images/del.png", self.del_window)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(SwitchEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_window(self):
        child=SwitchMainWindow(parent=self,connection=self.connection)
        #child.exec_()
        self.parent.workspace.addWindow(child)
        child.show()
        #self.refresh()

    def del_window(self):
        '''id=self.getSelectedId()

        if id>0 and QtGui.QMessageBox.question(self, u"Удалить расчётный период?" , u"Все связанные тарифные планы и вся статистика будут удалены.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.delete("DELETE FROM billservice_settlementperiod WHERE id=%d" % id)

        self.refresh()'''
        id=self.getSelectedId()
        if id>0:
            if self.connection.get_models("billservice_tariff", where={"settlement_period_id":id}):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Данный период используется в тарифных планах, удаление невозможно!!")
                return
            elif QtGui.QMessageBox.question(self, u"Удалить расчётный период?" , u"Все связанные тарифные планы и вся статистика будут удалены.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_settlementperiod")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_window(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "nas_switch")
            child=SwitchMainWindow(parent=self,connection=self.connection, model=model)
            #child.exec_()
            self.parent.workspace.addWindow(child)
            child.show()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/switch.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        items = self.connection.sql("SELECT id,manufacturer,model,name,ipaddress,ports_count,((SELECT name FROM billservice_street WHERE id=switch.street_id)||', ' ||(SELECT name FROM billservice_house WHERE id=switch.house_id)||' '||switch.place) as switch_place FROM nas_switch as switch", return_response=True)
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.manufacturer, i,1)
            self.addrow(item.model, i,2)
            self.addrow(item.name, i,3)
            self.addrow(item.ipaddress, i,4)
            self.addrow(item.switch_place, i,5)
            self.addrow(item.ports_count, i,6)
           
            
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(SwitchEbs, self).delNodeLocalAction([self.delAction])

