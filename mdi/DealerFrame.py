#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil

class AddDealerFrame(QtGui.QMainWindow):
    def __init__(self, connection, model=None):
        super(AddDealerFrame, self).__init__()
        self.model = model
        self.bank_model = None
        self.connection = connection
        self.connection.commit()

        self.setObjectName("MainWindow")
        self.resize(915, 560)
        self.setMinimumSize(QtCore.QSize(915, 560))
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_info = QtGui.QWidget()
        self.tab_info.setObjectName("tab_info")
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_info)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.groupBox_contact = QtGui.QGroupBox(self.tab_info)
        self.groupBox_contact.setMinimumSize(QtCore.QSize(531, 321))
        self.groupBox_contact.setObjectName("groupBox_contact")
        self.lineEdit_postaddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_postaddress.setGeometry(QtCore.QRect(120, 229, 383, 20))
        self.lineEdit_postaddress.setObjectName("lineEdit_postaddress")
        self.label_organization = QtGui.QLabel(self.groupBox_contact)
        self.label_organization.setGeometry(QtCore.QRect(9, 20, 88, 20))
        self.label_organization.setObjectName("label_organization")
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_fax.setGeometry(QtCore.QRect(120, 199, 191, 20))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.lineEdit_phone = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_phone.setGeometry(QtCore.QRect(120, 169, 191, 20))
        self.lineEdit_phone.setObjectName("lineEdit_phone")
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_organization.setGeometry(QtCore.QRect(120, 20, 381, 20))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.label_director = QtGui.QLabel(self.groupBox_contact)
        self.label_director.setGeometry(QtCore.QRect(9, 139, 88, 20))
        self.label_director.setObjectName("label_director")
        self.label_postaddress = QtGui.QLabel(self.groupBox_contact)
        self.label_postaddress.setGeometry(QtCore.QRect(9, 229, 101, 20))
        self.label_postaddress.setObjectName("label_postaddress")
        self.label_contactperson = QtGui.QLabel(self.groupBox_contact)
        self.label_contactperson.setGeometry(QtCore.QRect(9, 109, 88, 20))
        self.label_contactperson.setObjectName("label_contactperson")
        self.lineEdit_director = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_director.setGeometry(QtCore.QRect(120, 139, 381, 20))
        self.lineEdit_director.setObjectName("lineEdit_director")
        self.label_phone = QtGui.QLabel(self.groupBox_contact)
        self.label_phone.setGeometry(QtCore.QRect(9, 169, 88, 20))
        self.label_phone.setObjectName("label_phone")
        self.lineEdit_contactperson = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_contactperson.setGeometry(QtCore.QRect(120, 109, 381, 20))
        self.lineEdit_contactperson.setObjectName("lineEdit_contactperson")
        self.label_fax = QtGui.QLabel(self.groupBox_contact)
        self.label_fax.setGeometry(QtCore.QRect(9, 199, 88, 20))
        self.label_fax.setObjectName("label_fax")
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_uraddress.setGeometry(QtCore.QRect(120, 259, 383, 20))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.label_uraddress = QtGui.QLabel(self.groupBox_contact)
        self.label_uraddress.setGeometry(QtCore.QRect(10, 259, 111, 20))
        self.label_uraddress.setObjectName("label_uraddress")
        self.lineEdit_email = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_email.setGeometry(QtCore.QRect(120, 289, 381, 20))
        self.lineEdit_email.setObjectName("lineEdit_email")
        self.label_email = QtGui.QLabel(self.groupBox_contact)
        self.label_email.setGeometry(QtCore.QRect(10, 290, 111, 20))
        self.label_email.setObjectName("label_email")
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_okpo.setGeometry(QtCore.QRect(120, 80, 191, 20))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_unp.setGeometry(QtCore.QRect(120, 50, 191, 20))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.label_unp = QtGui.QLabel(self.groupBox_contact)
        self.label_unp.setGeometry(QtCore.QRect(9, 50, 51, 20))
        self.label_unp.setObjectName("label_unp")
        self.label_okpo = QtGui.QLabel(self.groupBox_contact)
        self.label_okpo.setGeometry(QtCore.QRect(9, 80, 51, 20))
        self.label_okpo.setObjectName("label_okpo")
        self.gridLayout_6.addWidget(self.groupBox_contact, 0, 0, 2, 1)
        self.groupBox_billinfo = QtGui.QGroupBox(self.tab_info)
        self.groupBox_billinfo.setMinimumSize(QtCore.QSize(338, 291))
        self.groupBox_billinfo.setObjectName("groupBox_billinfo")
        self.label_last_sale_date = QtGui.QLabel(self.groupBox_billinfo)
        self.label_last_sale_date.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label_last_sale_date.setObjectName("label_last_sale_date")
        self.label_buy_cards_sum = QtGui.QLabel(self.groupBox_billinfo)
        self.label_buy_cards_sum.setGeometry(QtCore.QRect(10, 80, 171, 16))
        self.label_buy_cards_sum.setObjectName("label_buy_cards_sum")
        self.label_pay_sum = QtGui.QLabel(self.groupBox_billinfo)
        self.label_pay_sum.setGeometry(QtCore.QRect(10, 110, 171, 16))
        self.label_pay_sum.setObjectName("label_pay_sum")
        self.label_debet_sum = QtGui.QLabel(self.groupBox_billinfo)
        self.label_debet_sum.setGeometry(QtCore.QRect(10, 140, 171, 16))
        self.label_debet_sum.setObjectName("label_debet_sum")
        self.label_dealer_return = QtGui.QLabel(self.groupBox_billinfo)
        self.label_dealer_return.setGeometry(QtCore.QRect(10, 170, 171, 16))
        self.label_dealer_return.setObjectName("label_dealer_return")
        self.label_operator_return_without_discount = QtGui.QLabel(self.groupBox_billinfo)
        self.label_operator_return_without_discount.setGeometry(QtCore.QRect(10, 200, 171, 16))
        self.label_operator_return_without_discount.setObjectName("label_operator_return_without_discount")
        self.label_loss_for_discount = QtGui.QLabel(self.groupBox_billinfo)
        self.label_loss_for_discount.setGeometry(QtCore.QRect(10, 260, 171, 16))
        self.label_loss_for_discount.setObjectName("label_loss_for_discount")
        self.label_operator_return_with_discount = QtGui.QLabel(self.groupBox_billinfo)
        self.label_operator_return_with_discount.setGeometry(QtCore.QRect(10, 230, 171, 16))
        self.label_operator_return_with_discount.setObjectName("label_operator_return_with_discount")
        self.label_last_sale_date_z = QtGui.QLabel(self.groupBox_billinfo)
        self.label_last_sale_date_z.setGeometry(QtCore.QRect(190, 20, 141, 16))
        self.label_last_sale_date_z.setObjectName("label_last_sale_date_z")
        self.lineEdit_buy_cards_sum = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_buy_cards_sum.setGeometry(QtCore.QRect(190, 80, 141, 20))
        self.lineEdit_buy_cards_sum.setObjectName("lineEdit_buy_cards_sum")
        self.lineEdit_pay_sum = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_pay_sum.setGeometry(QtCore.QRect(190, 110, 141, 20))
        self.lineEdit_pay_sum.setObjectName("lineEdit_pay_sum")
        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_3.setGeometry(QtCore.QRect(190, 140, 141, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_debet_sum = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_debet_sum.setGeometry(QtCore.QRect(190, 140, 141, 20))
        self.lineEdit_debet_sum.setObjectName("lineEdit_debet_sum")
        self.lineEdit_operator_return_without_discount = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_operator_return_without_discount.setGeometry(QtCore.QRect(190, 200, 141, 20))
        self.lineEdit_operator_return_without_discount.setObjectName("lineEdit_operator_return_without_discount")
        self.lineEdit_operator_return_with_discount = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_operator_return_with_discount.setGeometry(QtCore.QRect(190, 230, 141, 20))
        self.lineEdit_operator_return_with_discount.setObjectName("lineEdit_operator_return_with_discount")
        self.lineEdit_loss_for_discount = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_loss_for_discount.setGeometry(QtCore.QRect(190, 260, 141, 20))
        self.lineEdit_loss_for_discount.setObjectName("lineEdit_loss_for_discount")
        self.label_buy_cards = QtGui.QLabel(self.groupBox_billinfo)
        self.label_buy_cards.setGeometry(QtCore.QRect(10, 50, 171, 16))
        self.label_buy_cards.setObjectName("label_buy_cards")
        self.lineEdit_buy_cards = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_buy_cards.setGeometry(QtCore.QRect(190, 50, 141, 20))
        self.lineEdit_buy_cards.setObjectName("lineEdit_buy_cards")
        self.lineEdit_dealer_return = QtGui.QLineEdit(self.groupBox_billinfo)
        self.lineEdit_dealer_return.setGeometry(QtCore.QRect(190, 170, 141, 20))
        self.lineEdit_dealer_return.setObjectName("lineEdit_dealer_return")
        self.gridLayout_6.addWidget(self.groupBox_billinfo, 0, 1, 1, 1)
        self.groupBox_billdata = QtGui.QGroupBox(self.tab_info)
        self.groupBox_billdata.setMinimumSize(QtCore.QSize(338, 151))
        self.groupBox_billdata.setObjectName("groupBox_billdata")
        self.spinBox_prepayment = QtGui.QSpinBox(self.groupBox_billdata)
        self.spinBox_prepayment.setGeometry(QtCore.QRect(150, 20, 91, 22))
        self.spinBox_prepayment.setMaximum(100)
        self.spinBox_prepayment.setObjectName("spinBox_prepayment")
        self.label_prepayment = QtGui.QLabel(self.groupBox_billdata)
        self.label_prepayment.setGeometry(QtCore.QRect(10, 20, 131, 21))
        self.label_prepayment.setObjectName("label_prepayment")
        self.label_paydeffer = QtGui.QLabel(self.groupBox_billdata)
        self.label_paydeffer.setGeometry(QtCore.QRect(10, 50, 131, 21))
        self.label_paydeffer.setObjectName("label_paydeffer")
        self.spinBox_paydeffer = QtGui.QSpinBox(self.groupBox_billdata)
        self.spinBox_paydeffer.setGeometry(QtCore.QRect(150, 50, 91, 22))
        self.spinBox_paydeffer.setMaximum(365)
        self.spinBox_paydeffer.setObjectName("spinBox_paydeffer")
        self.spinBox_discount = QtGui.QSpinBox(self.groupBox_billdata)
        self.spinBox_discount.setGeometry(QtCore.QRect(150, 80, 91, 22))
        self.spinBox_discount.setMaximum(100)
        self.spinBox_discount.setObjectName("spinBox_discount")
        self.label_discount = QtGui.QLabel(self.groupBox_billdata)
        self.label_discount.setGeometry(QtCore.QRect(10, 80, 91, 20))
        self.label_discount.setObjectName("label_discount")
        self.checkBox_always_sell_cards = QtGui.QCheckBox(self.groupBox_billdata)
        self.checkBox_always_sell_cards.setGeometry(QtCore.QRect(10, 110, 301, 31))
        self.checkBox_always_sell_cards.setObjectName("checkBox_always_sell_cards")
        self.gridLayout_6.addWidget(self.groupBox_billdata, 1, 1, 2, 1)
        self.groupBox_bankdata = QtGui.QGroupBox(self.tab_info)
        self.groupBox_bankdata.setMinimumSize(QtCore.QSize(531, 111))
        self.groupBox_bankdata.setObjectName("groupBox_bankdata")
        self.label_rs = QtGui.QLabel(self.groupBox_bankdata)
        self.label_rs.setGeometry(QtCore.QRect(10, 80, 51, 20))
        self.label_rs.setObjectName("label_rs")
        self.label_bank = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bank.setGeometry(QtCore.QRect(9, 20, 51, 20))
        self.label_bank.setObjectName("label_bank")
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_rs.setGeometry(QtCore.QRect(90, 80, 383, 20))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bank.setGeometry(QtCore.QRect(90, 20, 383, 20))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.lineEdit_bankcode = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bankcode.setGeometry(QtCore.QRect(90, 50, 151, 20))
        self.lineEdit_bankcode.setObjectName("lineEdit_bankcode")
        self.label_bankcode = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bankcode.setGeometry(QtCore.QRect(10, 50, 61, 16))
        self.label_bankcode.setObjectName("label_bankcode")
        self.gridLayout_6.addWidget(self.groupBox_bankdata, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_info, "")
        self.tab_not_activated = QtGui.QWidget()
        self.tab_not_activated.setObjectName("tab_not_activated")
        self.gridLayout_2 = QtGui.QGridLayout(self.tab_not_activated)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget_not_activated = QtGui.QTableWidget(self.tab_not_activated)
        self.tableWidget_not_activated.setObjectName("tableWidget_not_activated")
        self.tableWidget_not_activated = tableFormat(self.tableWidget_not_activated)
        

        self.gridLayout_2.addWidget(self.tableWidget_not_activated, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_not_activated, "")
        self.tab_activated = QtGui.QWidget()
        self.tab_activated.setObjectName("tab_activated")
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_activated)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableWidget_activated = QtGui.QTableWidget(self.tab_activated)
        self.tableWidget_activated.setObjectName("tableWidget_activated")
        self.tableWidget_activated = tableFormat(self.tableWidget_activated)


        self.gridLayout_3.addWidget(self.tableWidget_activated, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_activated, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSave = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon)
        self.actionSave.setObjectName("actionSave")
        self.returnCardsAction = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/return.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.returnCardsAction.setIcon(icon1)
        self.returnCardsAction.setObjectName("returnCardsAction")
        self.actionPrepareBill = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/moneybook.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPrepareBill.setIcon(icon2)
        self.actionPrepareBill.setObjectName("actionPrepareBill")
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionPrepareBill)
        self.toolBar.addAction(self.returnCardsAction)

        
        
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.lineEdit_organization, self.lineEdit_unp)
        self.setTabOrder(self.lineEdit_unp, self.lineEdit_okpo)
        self.setTabOrder(self.lineEdit_okpo, self.lineEdit_contactperson)
        self.setTabOrder(self.lineEdit_contactperson, self.lineEdit_director)
        self.setTabOrder(self.lineEdit_director, self.lineEdit_phone)
        self.setTabOrder(self.lineEdit_phone, self.lineEdit_fax)
        self.setTabOrder(self.lineEdit_fax, self.lineEdit_postaddress)
        self.setTabOrder(self.lineEdit_postaddress, self.lineEdit_uraddress)
        self.setTabOrder(self.lineEdit_uraddress, self.lineEdit_email)
        self.setTabOrder(self.lineEdit_email, self.lineEdit_bank)
        self.setTabOrder(self.lineEdit_bank, self.lineEdit_bankcode)
        self.setTabOrder(self.lineEdit_bankcode, self.lineEdit_rs)
        self.setTabOrder(self.lineEdit_rs, self.lineEdit_buy_cards)
        self.setTabOrder(self.lineEdit_buy_cards, self.lineEdit_buy_cards_sum)
        self.setTabOrder(self.lineEdit_buy_cards_sum, self.lineEdit_pay_sum)
        self.setTabOrder(self.lineEdit_pay_sum, self.lineEdit_dealer_return)
        self.setTabOrder(self.lineEdit_dealer_return, self.lineEdit_operator_return_without_discount)
        self.setTabOrder(self.lineEdit_operator_return_without_discount, self.lineEdit_operator_return_with_discount)
        self.setTabOrder(self.lineEdit_operator_return_with_discount, self.lineEdit_loss_for_discount)
        self.setTabOrder(self.lineEdit_loss_for_discount, self.spinBox_prepayment)
        self.setTabOrder(self.spinBox_prepayment, self.spinBox_paydeffer)
        self.setTabOrder(self.spinBox_paydeffer, self.spinBox_discount)
        self.setTabOrder(self.spinBox_discount, self.checkBox_always_sell_cards)
        self.setTabOrder(self.checkBox_always_sell_cards, self.lineEdit_3)
        #self.setTabOrder(self.lineEdit_3, self.comboBox)
        #self.setTabOrder(MainWindow.comboBox, self.tableWidget_not_activated)
        self.setTabOrder(self.tableWidget_not_activated, self.tableWidget_activated)
        self.setTabOrder(self.tableWidget_activated, self.lineEdit_debet_sum)
        self.setTabOrder(self.lineEdit_debet_sum, self.tabWidget)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.fixtures()
        #QtCore.QObject.connect(self.nas_comboBox,QtCore.SIGNAL("currentIndexChanged(int)"),self.refillActions)
        self.retranslateUi()
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Данные дилера", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_contact.setTitle(QtGui.QApplication.translate("MainWindow", "Контактные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_director.setText(QtGui.QApplication.translate("MainWindow", "ФИО директора", None, QtGui.QApplication.UnicodeUTF8))
        self.label_postaddress.setText(QtGui.QApplication.translate("MainWindow", "Почтовый адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contactperson.setText(QtGui.QApplication.translate("MainWindow", "Контактное лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_phone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_email.setText(QtGui.QApplication.translate("MainWindow", "E-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_billinfo.setTitle(QtGui.QApplication.translate("MainWindow", "Платёжная информация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_last_sale_date.setText(QtGui.QApplication.translate("MainWindow", "Последняя продажа карт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_buy_cards_sum.setText(QtGui.QApplication.translate("MainWindow", "На сумму", None, QtGui.QApplication.UnicodeUTF8))
        self.label_pay_sum.setText(QtGui.QApplication.translate("MainWindow", "Всего оплачено на сумму", None, QtGui.QApplication.UnicodeUTF8))
        self.label_debet_sum.setText(QtGui.QApplication.translate("MainWindow", "Задолженность составляет", None, QtGui.QApplication.UnicodeUTF8))
        self.label_dealer_return.setText(QtGui.QApplication.translate("MainWindow", "Прибыль дилера", None, QtGui.QApplication.UnicodeUTF8))
        self.label_operator_return_without_discount.setText(QtGui.QApplication.translate("MainWindow", "Прибыль оператора без скидки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_loss_for_discount.setText(QtGui.QApplication.translate("MainWindow", "Убыток по скидке", None, QtGui.QApplication.UnicodeUTF8))
        self.label_operator_return_with_discount.setText(QtGui.QApplication.translate("MainWindow", "Прибыль оператора со скидкой", None, QtGui.QApplication.UnicodeUTF8))
        self.label_last_sale_date_z.setText(QtGui.QApplication.translate("MainWindow", "date", None, QtGui.QApplication.UnicodeUTF8))
        self.label_buy_cards.setText(QtGui.QApplication.translate("MainWindow", "Приобретено карт", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_billdata.setTitle(QtGui.QApplication.translate("MainWindow", "Условия оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_prepayment.setText(QtGui.QApplication.translate("MainWindow", "Размер предоплаты в %", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paydeffer.setText(QtGui.QApplication.translate("MainWindow", "Отсрочка платежа, дней", None, QtGui.QApplication.UnicodeUTF8))
        self.label_discount.setText(QtGui.QApplication.translate("MainWindow", "Скидка в %", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_always_sell_cards.setText(QtGui.QApplication.translate("MainWindow", "Разрешить продажу новых карт в случае неоплаты\nпо отсрочке", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_bankdata.setTitle(QtGui.QApplication.translate("MainWindow", "Банковские реквизиты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("MainWindow", "Р/с", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("MainWindow", "Банк", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bankcode.setText(QtGui.QApplication.translate("MainWindow", "Код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_info), QtGui.QApplication.translate("MainWindow", "Данные о дилере", None, QtGui.QApplication.UnicodeUTF8))
        
        columns = ["#", u"Серия", u"PIN", u"Номинальная стоимость", u"Дата начала", u"Дата конца"]
        makeHeaders(columns, self.tableWidget_not_activated)
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_not_activated), QtGui.QApplication.translate("MainWindow", "Карточки в наличии", None, QtGui.QApplication.UnicodeUTF8))

        columns = ["#", u"Серия", u"PIN", u"Номинальная стоимость", u"Дата начала", u"Дата конца", u"Дата активации"]
        makeHeaders(columns, self.tableWidget_activated)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_activated), QtGui.QApplication.translate("MainWindow", "Активированные карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.returnCardsAction.setText(QtGui.QApplication.translate("MainWindow", "Вернуть карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrepareBill.setText(QtGui.QApplication.translate("MainWindow", "PrepareBill", None, QtGui.QApplication.UnicodeUTF8))
         
    
    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))
            
        if self.model:
            model=self.model
        else:
            print 'New dealer'
            model=Object()

        if unicode(self.lineEdit_contactperson.text())==u"" and unicode(self.lineEdit_organization.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано контактное лицо или организация"))
            return

        if self.bank_model:
            bank_model = self.bank_model
        else:
            bank_model = Object()
        
        bank_model.bank = unicode(self.lineEdit_bank.text())
        bank_model.bankcode = unicode(self.lineEdit_bankcode.text())
        bank_model.rs = unicode(self.lineEdit_rs.text())
        bank_model.currency = ""
        
        try:
            bank_id = self.connection.create(bank_model.save("billservice_bankdata"))
            """
            Защита от двойного обавления при создании записи
            """

            if bank_id==-1:
                bank_id = self.bank_model.id
            self.bank_model = bank_model
            self.bank_model.id = bank_id
            
        except Exception, e:
            print 1,e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка!",
                                u"Невозможно сохранить данные!")
            return

    
        model.organization = unicode(self.lineEdit_organization.text())
        model.unp = unicode(self.lineEdit_unp.text())
        model.okpo = unicode(self.lineEdit_okpo.text())
        model.contactperson = unicode(self.lineEdit_contactperson.text())
        model.director = unicode(self.lineEdit_director.text())
        model.phone = unicode(self.lineEdit_phone.text())
        model.fax = unicode(self.lineEdit_fax.text())
        model.postaddress = unicode(self.lineEdit_postaddress.text())
        model.uraddress = unicode(self.lineEdit_uraddress.text())
        model.email = unicode(self.lineEdit_email.text())
        model.prepayment = unicode(self.spinBox_prepayment.text())
        model.discount = unicode(self.spinBox_discount.text())
        model.paydeffer = unicode(self.spinBox_paydeffer.text())

        model.always_sell_cards = self.checkBox_always_sell_cards.checkState()==2
        model.bank_id = bank_id


        try:
            model_id = self.connection.create(model.save(table="billservice_dealer"))
            self.connection.commit()
            """
            Защита от двойного обавления при создании записи
            """
            if model_id==-1:
                model_id = self.model.id
            self.model = model
            self.model.id = model_id
        except Exception, e:
            print 2,e
            self.connection.rollback()
            
        self.model.id = model_id
        #QtGui.QDialog.accept(self)
        self.emit(QtCore.SIGNAL("refresh()"))
        #self.destroy()

    def fixtures(self):

        if self.model:
            self.bank_model = self.connection.foselect("billservice_bankdata", self.model.bank_id)
            
            self.lineEdit_organization.setText(unicode(self.model.organization))
            self.lineEdit_unp.setText(unicode(self.model.unp))
            self.lineEdit_okpo.setText(unicode(self.model.okpo))
            self.lineEdit_contactperson.setText(unicode(self.model.contactperson))
            self.lineEdit_director.setText(unicode(self.model.director))
            self.lineEdit_phone.setText(unicode(self.model.phone))
            self.lineEdit_fax.setText(unicode(self.model.fax))
            self.lineEdit_postaddress.setText(unicode(self.model.postaddress))
            self.lineEdit_uraddress.setText(unicode(self.model.uraddress))                                
            self.lineEdit_email.setText(unicode(self.model.email))
            
            self.spinBox_prepayment.setValue(self.model.prepayment)
            self.spinBox_discount.setValue(self.model.discount)
            self.spinBox_paydeffer.setValue(self.model.paydeffer)

            self.checkBox_always_sell_cards.setChecked(self.model.always_sell_cards)
            
            self.lineEdit_bank.setText(unicode(self.bank_model.bank))
            self.lineEdit_bankcode.setText(unicode(self.bank_model.bankcode))
            self.lineEdit_rs.setText(unicode(self.bank_model.rs))
            
            
            #self.pptp_checkBox.setCheckState(self.model.allow_pptp == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.pppoe_checkBox.setCheckState(self.model.allow_pppoe == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.ipn_checkBox.setCheckState(self.model.allow_ipn == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            #self.multilink_checkBox.setChecked(self.model.multilink)
        else:
            self.bank_model = Object()






class DealerMdiChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, parent, connection):
        bhdr = HeaderUtil.getBinaryHeader("dealer_frame_header")
        super(DealerMdiChild, self).__init__()
        #global connection
        self.connection=connection
        self.parent = parent
        self.setObjectName("DealerMDI")

        self.resize(936, 648)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_dealers = QtGui.QWidget()
        self.tab_dealers.setObjectName("tab_dealers")
        self.gridLayout_2 = QtGui.QGridLayout(self.tab_dealers)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget = QtGui.QTableWidget(self.tab_dealers)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        
        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_dealers, "")
        self.tab_sales = QtGui.QWidget()
        self.tab_sales.setObjectName("tab_sales")
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_sales)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableWidget_sales = QtGui.QTableWidget(self.tab_sales)
        self.tableWidget_sales.setObjectName("tableWidget_sales")
        self.tableWidget_sales = tableFormat(self.tableWidget_sales)
        
        self.gridLayout_3.addWidget(self.tableWidget_sales, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_sales, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.statusBar = QtGui.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)
        self.actionAddDealer = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAddDealer.setIcon(icon)
        self.actionAddDealer.setObjectName("actionAddDealer")
        self.actionDelDealer = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelDealer.setIcon(icon1)
        self.actionDelDealer.setObjectName("actionDelDealer")
        self.actionSales = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSales.setIcon(icon2)
        self.actionSales.setObjectName("actionSales")
        self.toolBar.addAction(self.actionAddDealer)
        self.toolBar.addAction(self.actionDelDealer)
        self.toolBar.addAction(self.actionSales)




        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.actionAddDealer, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        
        HeaderUtil.nullifySaved("dealer_frame_header")
        self.retranslateUi()
        self.refresh()
        self.tableWidget = tableFormat(self.tableWidget)
        
        if not bhdr.isEmpty():
                HeaderUtil.setBinaryHeader("dealer_frame_header", bhdr)
                HeaderUtil.getHeader("dealer_frame_header", self.tableWidget)
        
        #self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        #self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.delNodeLocalAction()
        #self.show()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Дилеры", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.clear()
        columns=[u"id", u"Организация", u"Контактное лицо", u"Продано", u"Активировано", u"Задолженность", u"Скидка", u"Отсрочка"]
        makeHeaders(columns, self.tableWidget)

        self.tableWidget_sales.clear()
        columns=[u"id", u"Дата", u"Количество", u"Сумма", u"Скидка", u"Отсрочка", u"Оплачено"]
        makeHeaders(columns, self.tableWidget_sales)
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_dealers), QtGui.QApplication.translate("MainWindow", "Дилеры", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sales), QtGui.QApplication.translate("MainWindow", "Запупки", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAddDealer.setText(QtGui.QApplication.translate("MainWindow", "AddDealer", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelDealer.setText(QtGui.QApplication.translate("MainWindow", "delDealer", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSales.setText(QtGui.QApplication.translate("MainWindow", "Sales", None, QtGui.QApplication.UnicodeUTF8))
        


    def addframe(self):
        
        model=None
        child = AddDealerFrame(connection=self.connection, model=model)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        self.parent.workspace.addWindow(child)

        child.show()
        #self.refresh()




    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        id=self.getSelectedId()
        if id>0:
            if self.connection.sql("""SELECT id FROM billservice_account WHERE (nas_id=%d)""" % id):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Пожалуйста, отцепите сначала всех пользователей от сервера!")
                return
            elif (QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u'''Все связанные с сервером доступа аккаунты \n и вся статистика будут удалены. \nВы уверены, что хотите это сделать?''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
                try:
                    #self.connection.sql("UPDATE nas_nas SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete("nas_nas", id)
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")
        


    def editframe(self):
        try:
            model=self.connection.foselect("billservice_dealer", self.getSelectedId())
        except:
            model=None

        child = AddDealerFrame(connection=self.connection, model=model)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        #addf.show()
        self.parent.workspace.addWindow(child)
        #addf.show()
        #if child.exec_()==1:
        #    self.refresh()
        child.show()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/nas.png"))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        self.tableWidget.setSortingEnabled(False)
        #nasses=Nas.objects.all().order_by('id')
        #nasses=self.connection.sql("SELECT * FROM nas_nas ORDER BY id")
        
        data = self.connection.foselect("billservice_dealer")
        #self.tableWidget.setRowCount(nasses.count())
        self.tableWidget.setRowCount(len(data))
        i=0
        [u"id", u"Организация", u"Контактное лицо", u"Продано", u"Активировано", u"Задолженность", u"Скидка", u"Отсрочка"]
        for d in data:
            self.addrow(d.id, i,0)
            self.addrow(d.organization, i,1)
            self.addrow(d.contactperson, i,2)
            self.addrow(d.contactperson, i,2)
            #self.addrow(nas.ipaddress, i,3)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader("dealer_frame_header", self.tableWidget)
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setSortingEnabled(True)

    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("dealer_frame_header", self.tableWidget)    
            
            
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.configureAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.configureAction.setDisabled(False)
            