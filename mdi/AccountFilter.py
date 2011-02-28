#-*-coding:utf-8 -*-

from PyQt4 import QtCore, QtGui

class AccountFilterDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(AccountFilterDialog, self).__init__()
        self.connection=connection
        self.sql=''
        self.result_dict={}
        self.conditions = ['','<','<=','=','>=', '>']
        self.setObjectName("AccountFilterDialog")
        self.resize(796, 367)
        self.gridLayout_4 = QtGui.QGridLayout(self)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox_account = QtGui.QGroupBox(self)
        self.groupBox_account.setObjectName("groupBox_account")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_account)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_agreement = QtGui.QLabel(self.groupBox_account)
        self.label_agreement.setObjectName("label_agreement")
        self.gridLayout_3.addWidget(self.label_agreement, 0, 0, 1, 1)
        self.label_subaccount = QtGui.QLabel(self.groupBox_account)
        self.label_subaccount.setObjectName("label_subaccount")
        self.gridLayout_3.addWidget(self.label_subaccount, 1, 0, 1, 1)
        self.label_balance = QtGui.QLabel(self.groupBox_account)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_3.addWidget(self.label_balance, 2, 0, 1, 1)
        self.lineEdit_agreement = QtGui.QLineEdit(self.groupBox_account)
        self.lineEdit_agreement.setObjectName("lineEdit_agreement")
        self.gridLayout_3.addWidget(self.lineEdit_agreement, 0, 1, 1, 2)
        self.lineEdit_subaccount = QtGui.QLineEdit(self.groupBox_account)
        self.lineEdit_subaccount.setObjectName("lineEdit_subaccount")
        self.gridLayout_3.addWidget(self.lineEdit_subaccount, 1, 1, 1, 2)
        self.label_account = QtGui.QLabel(self.groupBox_account)
        self.label_account.setObjectName("label_account")
        self.gridLayout_3.addWidget(self.label_account, 0, 3, 1, 1)
        self.label_manager = QtGui.QLabel(self.groupBox_account)
        self.label_manager.setObjectName("label_manager")
        self.gridLayout_3.addWidget(self.label_manager, 1, 3, 1, 1)
        self.label_tarif = QtGui.QLabel(self.groupBox_account)
        self.label_tarif.setObjectName("label_tarif")
        self.gridLayout_3.addWidget(self.label_tarif, 0, 6, 1, 1)
        self.comboBox_tarif = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_tarif.setMinimumSize(QtCore.QSize(180, 0))
        self.comboBox_tarif.setEditable(True)
        self.comboBox_tarif.setMaxVisibleItems(30)
        self.comboBox_tarif.setObjectName("comboBox_tarif")
        self.gridLayout_3.addWidget(self.comboBox_tarif, 0, 8, 1, 1)
        self.label_status = QtGui.QLabel(self.groupBox_account)
        self.label_status.setObjectName("label_status")
        self.gridLayout_3.addWidget(self.label_status, 1, 6, 1, 1)
        self.comboBox_status = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_status.setEditable(True)
        self.comboBox_status.setObjectName("comboBox_status")
        self.gridLayout_3.addWidget(self.comboBox_status, 1, 8, 1, 1)
        self.comboBox_balance_condition = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_balance_condition.setObjectName("comboBox_balance_condition")
        self.gridLayout_3.addWidget(self.comboBox_balance_condition, 2, 1, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_account)
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.gridLayout_3.addWidget(self.lineEdit_balance, 2, 2, 1, 1)
        self.label_credit = QtGui.QLabel(self.groupBox_account)
        self.label_credit.setObjectName("label_credit")
        self.gridLayout_3.addWidget(self.label_credit, 2, 3, 1, 1)
        self.comboBox_credit_condition = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_credit_condition.setObjectName("comboBox_credit_condition")
        self.gridLayout_3.addWidget(self.comboBox_credit_condition, 2, 4, 1, 1)
        self.lineEdit_credit = QtGui.QLineEdit(self.groupBox_account)
        self.lineEdit_credit.setObjectName("lineEdit_credit")
        self.gridLayout_3.addWidget(self.lineEdit_credit, 2, 5, 1, 1)
        self.comboBox_manager = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_manager.setEditable(True)
        self.comboBox_manager.setObjectName("comboBox_manager")
        self.gridLayout_3.addWidget(self.comboBox_manager, 1, 4, 1, 2)
        self.lineEdit_account = QtGui.QLineEdit(self.groupBox_account)
        self.lineEdit_account.setObjectName("lineEdit_account")
        self.gridLayout_3.addWidget(self.lineEdit_account, 0, 4, 1, 2)
        self.label_ur_name = QtGui.QLabel(self.groupBox_account)
        self.label_ur_name.setObjectName("label_ur_name")
        self.gridLayout_3.addWidget(self.label_ur_name, 2, 6, 1, 1)
        self.comboBox_ur_name = QtGui.QComboBox(self.groupBox_account)
        self.comboBox_ur_name.setEditable(True)
        self.comboBox_ur_name.setFrame(True)
        self.comboBox_ur_name.setObjectName("comboBox_ur_name")
        self.gridLayout_3.addWidget(self.comboBox_ur_name, 2, 8, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_account, 0, 0, 1, 2)
        self.groupBox_address = QtGui.QGroupBox(self)
        self.groupBox_address.setObjectName("groupBox_address")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_address)
        self.gridLayout.setObjectName("gridLayout")
        self.label_city = QtGui.QLabel(self.groupBox_address)
        self.label_city.setObjectName("label_city")
        self.gridLayout.addWidget(self.label_city, 0, 0, 1, 1)
        self.comboBox_city = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_city.setEditable(True)
        self.comboBox_city.setObjectName("comboBox_city")
        self.gridLayout.addWidget(self.comboBox_city, 0, 1, 1, 2)
        self.label_street = QtGui.QLabel(self.groupBox_address)
        self.label_street.setObjectName("label_street")
        self.gridLayout.addWidget(self.label_street, 1, 0, 1, 1)
        self.comboBox_street = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_street.setEditable(True)
        self.comboBox_street.setObjectName("comboBox_street")
        self.gridLayout.addWidget(self.comboBox_street, 1, 1, 1, 2)
        self.comboBox_house = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_house.setEditable(True)
        self.comboBox_house.setObjectName("comboBox_house")
        self.gridLayout.addWidget(self.comboBox_house, 2, 1, 1, 2)
        self.label_bulk = QtGui.QLabel(self.groupBox_address)
        self.label_bulk.setObjectName("label_bulk")
        self.gridLayout.addWidget(self.label_bulk, 3, 0, 1, 1)
        self.comboBox_bulk = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_bulk.setEditable(True)
        self.comboBox_bulk.setObjectName("comboBox_bulk")
        self.gridLayout.addWidget(self.comboBox_bulk, 3, 1, 1, 2)
        self.label_stage = QtGui.QLabel(self.groupBox_address)
        self.label_stage.setObjectName("label_stage")
        self.gridLayout.addWidget(self.label_stage, 4, 0, 1, 1)
        self.comboBox_stage = QtGui.QComboBox(self.groupBox_address)
        self.comboBox_stage.setEditable(True)
        self.comboBox_stage.setObjectName("comboBox_stage")
        self.gridLayout.addWidget(self.comboBox_stage, 4, 1, 1, 2)
        self.label_house = QtGui.QLabel(self.groupBox_address)
        self.label_house.setObjectName("label_house")
        self.gridLayout.addWidget(self.label_house, 2, 0, 1, 1)
        self.lineEdit_room = QtGui.QLineEdit(self.groupBox_address)
        self.lineEdit_room.setObjectName("lineEdit_room")
        self.gridLayout.addWidget(self.lineEdit_room, 5, 1, 1, 1)
        self.label_room = QtGui.QLabel(self.groupBox_address)
        self.label_room.setObjectName("label_room")
        self.gridLayout.addWidget(self.label_room, 5, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_address, 1, 0, 1, 1)
        self.groupBox_network_parameters = QtGui.QGroupBox(self)
        self.groupBox_network_parameters.setObjectName("groupBox_network_parameters")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_network_parameters)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_nas = QtGui.QLabel(self.groupBox_network_parameters)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_2.addWidget(self.label_nas, 0, 0, 1, 2)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_network_parameters)
        self.comboBox_nas.setEditable(True)
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout_2.addWidget(self.comboBox_nas, 0, 2, 1, 1)
        self.label_switch = QtGui.QLabel(self.groupBox_network_parameters)
        self.label_switch.setObjectName("label_switch")
        self.gridLayout_2.addWidget(self.label_switch, 1, 0, 1, 1)
        self.comboBox_switch = QtGui.QComboBox(self.groupBox_network_parameters)
        self.comboBox_switch.setEditable(True)
        self.comboBox_switch.setObjectName("comboBox_switch")
        self.gridLayout_2.addWidget(self.comboBox_switch, 1, 2, 1, 1)
        self.label_vpn_ip = QtGui.QLabel(self.groupBox_network_parameters)
        self.label_vpn_ip.setObjectName("label_vpn_ip")
        self.gridLayout_2.addWidget(self.label_vpn_ip, 3, 0, 1, 1)
        self.lineEdit_vpn_ip = QtGui.QLineEdit(self.groupBox_network_parameters)
        self.lineEdit_vpn_ip.setObjectName("lineEdit_vpn_ip")
        self.gridLayout_2.addWidget(self.lineEdit_vpn_ip, 3, 2, 1, 1)
        self.label_ipn_ip = QtGui.QLabel(self.groupBox_network_parameters)
        self.label_ipn_ip.setObjectName("label_ipn_ip")
        self.gridLayout_2.addWidget(self.label_ipn_ip, 4, 0, 1, 1)
        self.lineEdit_ipn_ip = QtGui.QLineEdit(self.groupBox_network_parameters)
        self.lineEdit_ipn_ip.setObjectName("lineEdit_ipn_ip")
        self.gridLayout_2.addWidget(self.lineEdit_ipn_ip, 4, 2, 1, 1)
        self.lineEdit_port = QtGui.QLineEdit(self.groupBox_network_parameters)
        self.lineEdit_port.setObjectName("lineEdit_port")
        self.gridLayout_2.addWidget(self.lineEdit_port, 2, 2, 1, 1)
        self.label_port = QtGui.QLabel(self.groupBox_network_parameters)
        self.label_port.setObjectName("label_port")
        self.gridLayout_2.addWidget(self.label_port, 2, 0, 1, 1)
        self.checkBox_ipn_enabled = QtGui.QCheckBox(self.groupBox_network_parameters)
        
        self.checkBox_ipn_enabled.setDisabled(True)
        self.checkBox_ipn_enabled.setObjectName("checkBox_ipn_enabled")
        self.gridLayout_2.addWidget(self.checkBox_ipn_enabled, 5, 2, 1, 1)
        self.checkBox_ipn_added = QtGui.QCheckBox(self.groupBox_network_parameters)
        self.checkBox_ipn_added.setObjectName("checkBox_ipn_added")
        self.checkBox_ipn_added.setDisabled(True)
        self.gridLayout_2.addWidget(self.checkBox_ipn_added, 6, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_network_parameters, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_4.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.fixtures()
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        self.connect(self.comboBox_city, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_street)
        self.connect(self.comboBox_street, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_house)
        self.connect(self.comboBox_balance_condition, QtCore.SIGNAL("currentIndexChanged(int)"), self.balance_condition)
        self.connect(self.comboBox_credit_condition, QtCore.SIGNAL("currentIndexChanged(int)"), self.credit_condition)

        self.setTabOrder(self.lineEdit_agreement, self.lineEdit_account)
        self.setTabOrder(self.lineEdit_account, self.comboBox_tarif)
        self.setTabOrder(self.comboBox_tarif, self.lineEdit_subaccount)
        self.setTabOrder(self.lineEdit_subaccount, self.comboBox_manager)
        self.setTabOrder(self.comboBox_manager, self.comboBox_status)
        self.setTabOrder(self.comboBox_status, self.comboBox_balance_condition)
        self.setTabOrder(self.comboBox_balance_condition, self.lineEdit_balance)
        self.setTabOrder(self.lineEdit_balance, self.comboBox_credit_condition)
        self.setTabOrder(self.comboBox_credit_condition, self.lineEdit_credit)
        self.setTabOrder(self.lineEdit_credit, self.comboBox_ur_name)
        self.setTabOrder(self.comboBox_ur_name, self.comboBox_city)
        self.setTabOrder(self.comboBox_city, self.comboBox_street)
        self.setTabOrder(self.comboBox_street, self.comboBox_house)
        self.setTabOrder(self.comboBox_house, self.comboBox_bulk)
        self.setTabOrder(self.comboBox_bulk, self.comboBox_stage)
        self.setTabOrder(self.comboBox_stage, self.lineEdit_room)
        self.setTabOrder(self.lineEdit_room, self.comboBox_nas)
        self.setTabOrder(self.comboBox_nas, self.comboBox_switch)
        self.setTabOrder(self.comboBox_switch, self.lineEdit_port)
        self.setTabOrder(self.lineEdit_port, self.lineEdit_vpn_ip)
        self.setTabOrder(self.lineEdit_vpn_ip, self.lineEdit_ipn_ip)
        self.setTabOrder(self.lineEdit_ipn_ip, self.checkBox_ipn_enabled)
        self.setTabOrder(self.checkBox_ipn_enabled, self.checkBox_ipn_added)
        self.setTabOrder(self.checkBox_ipn_added, self.buttonBox)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Поиск абонентов", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_account.setTitle(QtGui.QApplication.translate("Dialog", "Параметры аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement.setText(QtGui.QApplication.translate("Dialog", "Номер договора", None, QtGui.QApplication.UnicodeUTF8))
        self.label_subaccount.setText(QtGui.QApplication.translate("Dialog", "Имя субаккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("Dialog", "Баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_account.setText(QtGui.QApplication.translate("Dialog", "Имя аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.label_manager.setText(QtGui.QApplication.translate("Dialog", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.label_tarif.setText(QtGui.QApplication.translate("Dialog", "Тариф", None, QtGui.QApplication.UnicodeUTF8))
        self.label_status.setText(QtGui.QApplication.translate("Dialog", "Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("Dialog", "Кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ur_name.setText(QtGui.QApplication.translate("Dialog", "Юрлицо", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_address.setTitle(QtGui.QApplication.translate("Dialog", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("Dialog", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_street.setText(QtGui.QApplication.translate("Dialog", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bulk.setText(QtGui.QApplication.translate("Dialog", "Подъезд", None, QtGui.QApplication.UnicodeUTF8))
        self.label_stage.setText(QtGui.QApplication.translate("Dialog", "Этаж", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house.setText(QtGui.QApplication.translate("Dialog", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_room.setText(QtGui.QApplication.translate("Dialog", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_network_parameters.setTitle(QtGui.QApplication.translate("Dialog", "Сетевые параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_switch.setText(QtGui.QApplication.translate("Dialog", "Комутатор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_ip.setText(QtGui.QApplication.translate("Dialog", "VPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_ip.setText(QtGui.QApplication.translate("Dialog", "IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_port.setText(QtGui.QApplication.translate("Dialog", "Номер порта", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ipn_enabled.setText(QtGui.QApplication.translate("Dialog", "Активен на сервере доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_ipn_added.setText(QtGui.QApplication.translate("Dialog", "Добавлен на сервер доступа", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        items=self.connection.sql("SELECT id, name FROM nas_nas ORDER BY name;")
        self.connection.commit()
        self.comboBox_nas.addItem(u"---Любой---", QtCore.QVariant(0))
        self.comboBox_switch.addItem(u"---Любой---", QtCore.QVariant(0))
        for item in items:
            self.comboBox_nas.addItem(item.name, QtCore.QVariant(item.id))
            self.comboBox_switch.addItem(item.name, QtCore.QVariant(item.id))



        items=self.connection.sql("SELECT id, name FROM billservice_tariff ORDER BY name;")
        self.connection.commit()
        self.comboBox_tarif.addItem(u"---Любой---", QtCore.QVariant(0))
        for item in items:
            self.comboBox_tarif.addItem(item.name, QtCore.QVariant(item.id))

        items=self.connection.sql("SELECT id, username FROM billservice_systemuser ORDER BY username;")
        self.connection.commit()
        self.comboBox_manager.addItem(u"---Любой---", QtCore.QVariant(0))
        for item in items:
            self.comboBox_manager.addItem(item.username, QtCore.QVariant(item.id))


        items=self.connection.sql("SELECT id, name FROM billservice_organization ORDER BY name;")
        self.connection.commit()
        self.comboBox_ur_name.addItem(u"---Любой---", QtCore.QVariant(0))
        for item in items:
            self.comboBox_ur_name.addItem(item.name, QtCore.QVariant(item.id))

        items=self.connection.sql("SELECT id, name FROM billservice_city ORDER BY name;")
        self.connection.commit()
        self.comboBox_city.addItem(u"---Любой---", QtCore.QVariant(0))
        for item in items:
            self.comboBox_city.addItem(item.name, QtCore.QVariant(item.id))

        self.comboBox_status.addItem(u"---Любой---")
        self.comboBox_status.setItemData(0, QtCore.QVariant(0))
        self.comboBox_status.addItem(u"Активен")
        self.comboBox_status.setItemData(1, QtCore.QVariant(1))
        self.comboBox_status.addItem(u"Неактивен, не списывать периодические услуги")
        self.comboBox_status.setItemData(2, QtCore.QVariant(2))
        self.comboBox_status.addItem(u"Неактивен, списывать периодические услуги")
        self.comboBox_status.setItemData(3, QtCore.QVariant(3))
        
        for item in self.conditions:
            self.comboBox_balance_condition.addItem(item)
            self.comboBox_credit_condition.addItem(item)
        
        self.balance_condition()
        self.credit_condition()
            
    def accept(self):
        r=[]
        r.append(('acc.contract','=',unicode(self.lineEdit_agreement.text())))
        r.append(('acc.username', ' LIKE ',unicode(self.lineEdit_account.text())))
        r.append(('subacc.username', ' LIKE ',unicode(self.lineEdit_subaccount.text())))
        
        r.append(('subacc.ipn_ip_address::text',' LIKE ',unicode(self.lineEdit_ipn_ip.text())))
        r.append(('subacc.vpn_ip_address::text', ' LIKE ',unicode(self.lineEdit_vpn_ip.text())))
        
        r.append(('acc.entrance', ' = ',unicode(self.comboBox_bulk.currentText())))
        r.append(('acc.row', ' = ',unicode(self.comboBox_stage.currentText())))
        r.append(('acc.room', ' = ',unicode(self.lineEdit_room.text())))
        r.append(('subacc.switch_port', ' = ',unicode(self.lineEdit_port.text())))
        nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
        if nas_id!=0:
            r.append(('subacc.nas_id', ' = ',nas_id))

        switch_id = self.comboBox_switch.itemData(self.comboBox_switch.currentIndex()).toInt()[0]
        if switch_id!=0:
            r.append(('subacc.switch_id', ' = ',switch_id))

        tarif_id = self.comboBox_tarif.itemData(self.comboBox_tarif.currentIndex()).toInt()[0]
        if tarif_id!=0:
            r.append(('get_tarif(acc.id)', ' = ',tarif_id))
        
        manager_id = self.comboBox_manager.itemData(self.comboBox_manager.currentIndex()).toInt()[0]
        if manager_id!=0:
            r.append(('acc.systemuser_id', ' = ',manager_id))
            
        organization_id = self.comboBox_ur_name.itemData(self.comboBox_ur_name.currentIndex()).toInt()[0]
        if organization_id!=0:
            r.append(('(SELECT id FROM billservice_organization WHERE account_id=acc.id)', ' = ',organization_id))
                                
        if self.lineEdit_balance.text() and self.comboBox_balance_condition.currentText()!='':
            balance_condition=unicode(self.comboBox_balance_condition.currentText())
            r.append(('acc.ballance',balance_condition, str(self.lineEdit_balance.text() or '')))

        if self.lineEdit_credit.text() and self.comboBox_credit_condition.currentText()!='':
            credit_condition=unicode(self.comboBox_credit_condition.currentText())
            r.append(('acc.credit',credit_condition, str(self.lineEdit_credit.text() or '')))
            
        status = self.comboBox_status.itemData(self.comboBox_status.currentIndex()).toInt()[0]
        if status!=0:
            r.append(('acc.status', ' = ',status))
        
        city = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if city!=0:
            r.append(('acc.city_id', ' = ',city))

        street = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if street!=0:
            r.append(('acc.street_id', ' = ',city))
        
        house = self.comboBox_house.itemData(self.comboBox_house.currentIndex()).toInt()[0]
        if house!=0:
            r.append(('acc.house_id', ' = ',city))
                                    
        f = lambda l: True if l[2]!='' else False
        
        res = filter(f,r)
        
        s= " AND ".join([" %s %s '%s' " % (x[0],x[1],x[2]) if type(x[2])==unicode else " %s %s %s " % (x[0],x[1],x[2])  for x in res])
        #print s
        self.sql=s
        QtGui.QDialog.accept(self)
        
    def refresh_combo_street(self):
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if not city_id: return
        streets = self.connection.sql("SELECT id, name FROM billservice_street WHERE city_id=%s ORDER BY name ASC;" % city_id)
        self.connection.commit()
        self.comboBox_street.clear()
        self.comboBox_house.clear()
        self.comboBox_street.addItem(u'---Любая---', QtCore.QVariant(0))
        i=0
        for street in streets:
            self.comboBox_street.addItem(street.name, QtCore.QVariant(street.id))

            i+=1

    def refresh_combo_house(self):
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if not street_id: return        
        items = self.connection.sql("SELECT id, name FROM billservice_house WHERE street_id=%s ORDER BY name ASC;" % street_id)
        self.connection.commit()
        self.comboBox_house.clear()
        self.comboBox_house.addItem(u"---Любой---", QtCore.QVariant(0))
        i=0
        for item in items:
            self.comboBox_house.addItem(item.name, QtCore.QVariant(item.id))

            i+=1
            
    def balance_condition(self):
        if self.comboBox_balance_condition.currentText():
            self.lineEdit_balance.setDisabled(False)
            self.lineEdit_balance.setFocus(True)
        else:
            self.lineEdit_balance.setDisabled(True)

    def credit_condition(self):
        if self.comboBox_credit_condition.currentText():
            self.lineEdit_credit.setDisabled(False)
            self.lineEdit_credit.setFocus(True)
        else:
            self.lineEdit_credit.setDisabled(True)

    