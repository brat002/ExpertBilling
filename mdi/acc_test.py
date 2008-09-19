
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
        self.accounttarif_table = tableFormat(self.accounttarif_table)





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


        self.accounttarif_table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.accounttarif_table.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.accounttarif_table.setSelectionMode(QtGui.QTableWidget.SingleSelection)