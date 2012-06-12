#-*-coding=utf-8-*-
#import Pyro
from PyQt4 import QtCore, QtGui

from helpers import tableFormat

from ebsWindow import ebsTableWindow
from db import AttrDict
from helpers import makeHeaders, dateDelim
from time import mktime
from CustomForms import ComboBoxDialog, CardPreviewDialog
import datetime, calendar
from helpers import transaction, get_free_addreses_from_pool
from helpers import HeaderUtil, SplitterUtil
from helpers import write_cards, get_type
from customwidget import CustomDateTimeWidget
import os, datetime
from randgen import GenPasswd2
from random import randint
import string
from mako.template import Template
from mako.lookup import TemplateLookup
from helpers import transip
from decimal import Decimal
from helpers import GenericThread
templatedir = "templates/cards/"
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
class SaleCards(QtGui.QDialog):
    def __init__(self, connection, cards, model=None):
        bhdr = HeaderUtil.getBinaryHeader("sale_cards_frame_header")
        super(SaleCards, self).__init__()
        self.connection = connection
        self.connection.commit()
        self.cards = cards # list of cards id
        self.model = model
        self.connection.commit()
        self.nominalsumm = 0
        
        self.setObjectName("SaleCards")
        self.resize(672, 645)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20, 610, 641, 26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.comboBox_dealer = QtGui.QComboBox(self)
        self.comboBox_dealer.setGeometry(QtCore.QRect(60, 20, 601, 21))
        self.comboBox_dealer.setObjectName("comboBox_dealer")

        self.label_dealer = QtGui.QLabel(self)
        self.label_dealer.setGeometry(QtCore.QRect(11, 20, 51, 21))
        self.label_dealer.setObjectName("label_dealer")
        self.groupBox_cards_actions = QtGui.QGroupBox(self)
        self.groupBox_cards_actions.setGeometry(QtCore.QRect(10, 240, 651, 61))
        self.groupBox_cards_actions.setObjectName("groupBox_cards_actions")
        self.commandLinkButton_save = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_save.setGeometry(QtCore.QRect(10, 20, 201, 31))
        self.commandLinkButton_save.setObjectName("commandLinkButton_save")
        self.commandLinkButton_bill = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_bill.setGeometry(QtCore.QRect(220, 20, 201, 31))
        self.commandLinkButton_bill.setObjectName("commandLinkButton_bill")
        self.commandLinkButton_print = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_print.setGeometry(QtCore.QRect(430, 20, 201, 31))
        self.commandLinkButton_print.setObjectName("commandLinkButton_print")
        self.groupBox_dealer_info = QtGui.QGroupBox(self)
        self.groupBox_dealer_info.setGeometry(QtCore.QRect(10, 60, 321, 141))
        self.groupBox_dealer_info.setObjectName("groupBox_dealer_info")
        self.lineEdit_debet = QtGui.QLineEdit(self.groupBox_dealer_info)
        self.lineEdit_debet.setGeometry(QtCore.QRect(140, 20, 171, 20))
        self.lineEdit_debet.setObjectName("lineEdit_debet")
        self.spinBox_prepay = QtGui.QDoubleSpinBox(self.groupBox_dealer_info)
        self.spinBox_prepay.setGeometry(QtCore.QRect(140, 50, 81, 20))
        self.spinBox_prepay.setObjectName("spinBox_prepay")
        self.spinBox_prepay.setMaximum(100)
        self.spinBox_prepay.setDecimals(3)
        
        self.label_debet = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_debet.setGeometry(QtCore.QRect(11, 20, 119, 20))
        self.label_debet.setObjectName("label_debet")
        self.label_prepay_procs = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_prepay_procs.setGeometry(QtCore.QRect(11, 51, 119, 20))
        self.label_prepay_procs.setObjectName("label_prepay_procs")
        self.label_paydeffer = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_paydeffer.setGeometry(QtCore.QRect(11, 77, 119, 20))
        self.label_paydeffer.setObjectName("label_paydeffer")
        self.spinBox_paydeffer = QtGui.QSpinBox(self.groupBox_dealer_info)
        self.spinBox_paydeffer.setGeometry(QtCore.QRect(140, 80, 81, 20))
        self.spinBox_paydeffer.setObjectName("spinBox_paydeffer")
        self.spinBox_paydeffer.setMaximum(365)
        
        
        self.label_discount = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_discount.setGeometry(QtCore.QRect(10, 110, 61, 16))
        self.label_discount.setObjectName("label_discount")
        self.spinBox_discount = QtGui.QDoubleSpinBox(self.groupBox_dealer_info)
        self.spinBox_discount.setGeometry(QtCore.QRect(140, 110, 81, 20))
        self.spinBox_discount.setObjectName("spinBox_discount")
        self.spinBox_discount.setMaximum(100)
        self.spinBox_discount.setDecimals(3)
        
        self.groupBox_bill_info = QtGui.QGroupBox(self)
        self.groupBox_bill_info.setGeometry(QtCore.QRect(340, 60, 321, 141))
        self.groupBox_bill_info.setMinimumSize(QtCore.QSize(300, 0))
        self.groupBox_bill_info.setObjectName("groupBox_bill_info")
        self.label_discount_amount = QtGui.QLabel(self.groupBox_bill_info)
        self.label_discount_amount.setGeometry(QtCore.QRect(10, 80, 81, 20))
        self.label_discount_amount.setObjectName("label_discount_amount")
        self.lineEdit_discount_amount = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_discount_amount.setGeometry(QtCore.QRect(90, 80, 113, 20))
        self.lineEdit_discount_amount.setObjectName("lineEdit_discount_amount")
        self.lineEdit_amount = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_amount.setGeometry(QtCore.QRect(90, 50, 113, 20))
        self.lineEdit_amount.setObjectName("lineEdit_amount")
        self.label_amount = QtGui.QLabel(self.groupBox_bill_info)
        self.label_amount.setGeometry(QtCore.QRect(10, 50, 61, 16))
        self.label_amount.setObjectName("label_amount")
        self.lineEdit_count_cards = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_count_cards.setGeometry(QtCore.QRect(90, 20, 113, 20))
        self.lineEdit_count_cards.setObjectName("lineEdit_count_cards")
        self.label_count_carts = QtGui.QLabel(self.groupBox_bill_info)
        self.label_count_carts.setGeometry(QtCore.QRect(10, 20, 71, 20))
        self.label_count_carts.setObjectName("label_count_carts")
        self.lineEdit_for_pay = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_for_pay.setGeometry(QtCore.QRect(90, 110, 113, 20))
        self.lineEdit_for_pay.setObjectName("lineEdit_for_pay")
        self.label_for_pay = QtGui.QLabel(self.groupBox_bill_info)
        self.label_for_pay.setGeometry(QtCore.QRect(10, 110, 71, 16))
        self.label_for_pay.setObjectName("label_for_pay")
        self.label_pay = QtGui.QLabel(self)
        self.label_pay.setGeometry(QtCore.QRect(340, 210, 81, 21))
        self.label_pay.setObjectName("label_pay")
        self.lineEdit_pay = QtGui.QLineEdit(self)
        self.lineEdit_pay.setGeometry(QtCore.QRect(430, 210, 231, 21))
        self.lineEdit_pay.setObjectName("lineEdit_pay")
        self.lineEdit_pay.setValidator(QtGui.QDoubleValidator(self.lineEdit_pay))
        
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10, 310, 651, 291))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)

        self.retranslateUi()
        
        tableHeader = self.tableWidget.horizontalHeader()
        
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.spinBox_discount, QtCore.SIGNAL("valueChanged (double)"), self.recalculateAmount)
        QtCore.QObject.connect(self.spinBox_prepay, QtCore.SIGNAL("valueChanged (double)"), self.recalculateAmount)
        #QtCore.QObject.connect(self.lineEdit_pay, QtCore.SIGNAL("editingFinished ()"), self.recalculatePrepay)
        
        QtCore.QObject.connect(self.commandLinkButton_save, QtCore.SIGNAL("clicked()"), self.exportToXML)
        QtCore.QObject.connect(self.commandLinkButton_print, QtCore.SIGNAL("clicked()"), self.printCards)
        QtCore.QObject.connect(self.commandLinkButton_bill, QtCore.SIGNAL("clicked()"), self.print_invoice)
        
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        HeaderUtil.nullifySaved("sale_cards_frame_header")
        
        self.setTabOrder(self.comboBox_dealer, self.lineEdit_debet)
        self.setTabOrder(self.lineEdit_debet, self.spinBox_prepay)
        self.setTabOrder(self.spinBox_prepay, self.spinBox_paydeffer)
        self.setTabOrder(self.spinBox_paydeffer, self.spinBox_discount)
        self.setTabOrder(self.spinBox_discount, self.lineEdit_count_cards)
        self.setTabOrder(self.lineEdit_count_cards, self.lineEdit_amount)
        self.setTabOrder(self.lineEdit_amount, self.lineEdit_discount_amount)
        self.setTabOrder(self.lineEdit_discount_amount, self.lineEdit_for_pay)
        self.setTabOrder(self.lineEdit_for_pay, self.lineEdit_pay)
        self.setTabOrder(self.lineEdit_pay, self.commandLinkButton_save)
        self.setTabOrder(self.commandLinkButton_save, self.commandLinkButton_bill)
        self.setTabOrder(self.commandLinkButton_bill, self.commandLinkButton_print)
        self.setTabOrder(self.commandLinkButton_print, self.tableWidget)
        self.setTabOrder(self.tableWidget, self.buttonBox)
        self.refresh()
        self.fixtures()
        QtCore.QObject.connect(self.comboBox_dealer,QtCore.SIGNAL("currentIndexChanged(int)"),self.dealerInfo)
        self.comboBox_dealer.emit(QtCore.SIGNAL("currentIndexChanged(int)"), self.comboBox_dealer.currentIndex())
        self.setWidgetsDisabled()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("sale_cards_frame_header", bhdr)
            HeaderUtil.getHeader("sale_cards_frame_header", self.tableWidget)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Продажа карт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_dealer.setText(QtGui.QApplication.translate("Dialog", "Дилер", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_cards_actions.setTitle(QtGui.QApplication.translate("Dialog", "Действия с партией карточек", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_save.setText(QtGui.QApplication.translate("Dialog", "Сохранить в файл", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_bill.setText(QtGui.QApplication.translate("Dialog", "Выписать счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_print.setText(QtGui.QApplication.translate("Dialog", "Распечатать", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_dealer_info.setTitle(QtGui.QApplication.translate("Dialog", "Иформация о дилере", None, QtGui.QApplication.UnicodeUTF8))
        self.label_debet.setText(QtGui.QApplication.translate("Dialog", "Задолженность", None, QtGui.QApplication.UnicodeUTF8))
        self.label_prepay_procs.setText(QtGui.QApplication.translate("Dialog", "Размер предоплаты, %", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paydeffer.setText(QtGui.QApplication.translate("Dialog", "Отсрочка платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_discount.setText(QtGui.QApplication.translate("Dialog", "Скидка, %", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_bill_info.setTitle(QtGui.QApplication.translate("Dialog", "Платёжная информация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_discount_amount.setText(QtGui.QApplication.translate("Dialog", "Сумма скидки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_amount.setText(QtGui.QApplication.translate("Dialog", "На сумму", None, QtGui.QApplication.UnicodeUTF8))
        self.label_count_carts.setText(QtGui.QApplication.translate("Dialog", "Кол-вол карт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_for_pay.setText(QtGui.QApplication.translate("Dialog", "К оплате", None, QtGui.QApplication.UnicodeUTF8))
        self.label_pay.setText(QtGui.QApplication.translate("Dialog", "Сумма оплаты", None, QtGui.QApplication.UnicodeUTF8))

        columns = ["#",u"Серия",u"Номинал",u"PIN",u"Активировать с",u"Активировать по"]
        makeHeaders(columns, self.tableWidget)
        
        
    def exportToXML(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                  "Create XML File", "", "XML Files (*.xml)")
        if fileName=="":
            return
        #try:
        import codecs
        if True:
            
            f = codecs.open(fileName, "w", "utf-8")
            f.write("<xml>")
            for x in xrange(self.tableWidget.rowCount()):
                #card = unicode(self.tableWidget.item(x,0).text())
                card = self.connection.get_cards(id= unicode(self.tableWidget.item(x,0).text()))[0]
                self.connection.commit()
                print card.tarif_name
                f.write("<card>")
                f.write("<id>%s</id>" % card.id)
                #f.write(u"<tarif>"+unicode(card.tarif_name)+"</tarif>")
                f.write(u"<tarif>%s</tarif>" % card.tarif)
                f.write(u"<series>%s</series>" % card.series)
                f.write(u"<nominal>%s</nominal>" % card.nominal)
                f.write(u"<pin>%s</pin>" % card.pin)
                f.write(u"<login>%s</login>" % card.login)
                f.write(u"<template>%s</template>" % card.template)
                f.write(u"<nas>%s</nas>" % card.nas)
                f.write(u"<ip>%s</ip>" % card.ip)
                f.write(u"<date_start>%s</date_start>" % card.start_date)
                f.write(u"<date_end>%s</date_end>" % card.end_date)
                
                f.write("</card>")
            f.write("</xml>")
            f.close()
            QtGui.QMessageBox.information(self, u"Файл успешно сохранён", unicode(u"Операция произведена успешно."))
        #except Exception, e:
        #    print e
        #    QtGui.QMessageBox.warning(self, u"Ошибка‹", unicode(u"Ошибка при сохранении."))
            
    def printCards(self):
        
        if len(self.cards)>0:
            crd = "(" + ",".join(self.cards) + ")"
        else:
            crd = "(0)" 
        
        cards = self.connection.get_notsold_cards(self.cards)
        templates = self.connection.get_templates()
        t={}
        #print templates
        for templ in templates:
            #print templ.id
            t['%s' % templ.id] = templ.body
            
        self.connection.commit()
        
        data="""
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        </head>
        <body>
        """; 
        
        try:
            operator =self.connection.get_operator()
            
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
            return

        try:
            bank =self.connection.get_banks(id=operator.bank_id)
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
            return
        self.connection.commit()
        try:
            for card in cards:
                
                templ = Template(t["%s" % card.template_id], input_encoding='utf-8')
                data+=templ.render_unicode(connection=self.connection, card=card, operator = operator, bank=bank)
        except Exception, e:
                data=unicode(u""" <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                </head>
                <body style="text-align:center;">%s</body></html>""" % repr(e))
        self.connection.commit()
        
        data+="</body></html>"
        file= open('templates/cards/cards.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        a=CardPreviewDialog(url="templates/cards/cards.html")
        a.exec_()
        #print data
        
    def print_invoice(self):

        dealer_id = self.comboBox_dealer.itemData(self.comboBox_dealer.currentIndex()).toInt()[0]

        cards = self.connection.get_notsold_cards(self.cards)
        operator = self.connection.get_operator()
        
        dealer = self.connection.get_dealers(dealer_id)

        template = self.connection.get_templates(type_id=6)
        self.connection.commit()
        
        templ = Template(unicode(template.body), input_encoding='utf-8')
        
        try:
            data=templ.render_unicode(connection=self.connection, cards=cards, operator=operator, dealer=dealer, created=datetime.datetime.now().strftime(strftimeFormat), 
                                      cardcount=len(cards), sum_for_pay = unicode(self.lineEdit_for_pay.text()), discount = unicode(self.spinBox_discount.text()),
                                      discount_sum = unicode(self.lineEdit_discount_amount.text()), pay = unicode(self.lineEdit_pay.text()),
                                      paydeffer = (datetime.datetime.now()+datetime.timedelta(days=self.spinBox_paydeffer.value())).strftime(strftimeFormat))
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

        

    def recalculateAmount(self, t=None):
        #print "recal"
        discount = (float(self.spinBox_discount.value())/float(100.00))*float(self.nominalsumm)
        #print "discount", discount
        #print index, dealer.id


        prepay = self.spinBox_prepay.value()
        self.lineEdit_for_pay.setText(unicode((float(self.nominalsumm)-float(discount))))
        self.lineEdit_discount_amount.setText(unicode(discount))
        self.lineEdit_pay.setText(unicode((Decimal(str(self.nominalsumm))-Decimal(str(discount)))*(Decimal(str(prepay))/Decimal(100))))
    
    def recalculatePrepay(self):
        self.spinBox_prepay.setValue(Decimal(self.lineEdit_pay.text())/Decimal(self.lineEdit_for_pay.text())*100)
        
    def fixtures(self):
        self.lineEdit_count_cards.setText(unicode(len(self.cards)))
        dealers = self.connection.get_dealers()
        self.connection.commit()
        i=0
        for dealer in dealers:
            self.comboBox_dealer.addItem(unicode(u"%s, %s" % (dealer.organization, dealer.contactperson)))
            self.comboBox_dealer.setItemData(i, QtCore.QVariant(dealer.id))
            if self.model:
                if self.model.daler==dealer.id:
                    self.model_dealer = dealer
                    self.comboBox_dealer.setCurrentIndex(i)
                    self.comboBox_dealer.setDisabled(True)
            i+=1
            
    def dealerInfo(self, index):
        id = self.comboBox_dealer.itemData(index).toInt()[0]
        #print id
        dealer = self.connection.get_dealers(id=id)
        self.connection.commit()
        self.model_dealer = dealer
        self.spinBox_discount.setValue(float(dealer.discount))
        self.spinBox_paydeffer.setValue(float(dealer.paydeffer))
        self.spinBox_prepay.setValue(float(dealer.prepayment))
        self.recalculateAmount()
        #self.
        
    def accept(self):
        if self.model:
            return
    
        try:
            model = AttrDict()
            now = datetime.datetime.now()
            model.dealer = self.comboBox_dealer.itemData(self.comboBox_dealer.currentIndex()).toInt()[0]
            #model.pay = 
            model.sum_for_pay = unicode(self.lineEdit_for_pay.text())
            model.paydeffer = self.spinBox_paydeffer.value()
            model.discount = self.spinBox_discount.value()
            model.discount_sum = unicode(self.lineEdit_discount_amount.text())
            model.prepayment = unicode(self.spinBox_prepay.value())
            #model.created = now.strftime(strftimeFormat)
            
            #print model.save("billservice_salecard")
            res = None
            try:
                res = self.connection.salecards_save(model, cards=[self.tableWidget.item(x,0).text().toInt()[0] for x in xrange(self.tableWidget.rowCount())])
                self.connection.commit()
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"К сожалению, данные не могут быть сохранены."))
                return
            
            if float(unicode(self.lineEdit_pay.text()))>0:
                if QtGui.QMessageBox.question(self, u"Зачислить сумму на счёт?" , u'''Произвести запись оплаты за эту партию карт?''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                    pay = AttrDict()
                    pay.dealer = model.dealer
                    pay.salecard = model.id
                    pay.pay = unicode(self.lineEdit_pay.text() or 0)
                    pay.created = now
                    self.connection.add_dealerpay(pay)

    
                
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"К сожалению, произошла непредвиденная ошибка. Отмена продажи."))
            return 
       
        if res:
            QtGui.QDialog.accept(self)
            
    
    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        
        #print 'activated',activated
        if value == None:
            value = ""
            
        headerItem.setText(unicode(value))

    
        self.tableWidget.setItem(x,y,headerItem)
        
    def setWidgetsDisabled(self):
        self.lineEdit_amount.setDisabled(True)
        self.lineEdit_count_cards.setDisabled(True)
        self.lineEdit_debet.setDisabled(True)
        #self.spinBox_discount.setDisabled(True)
        self.lineEdit_discount_amount.setDisabled(True)
        self.lineEdit_for_pay.setDisabled(True)
        #self.spinBox_paydeffer.setDisabled(True)
        #self.spinBox_prepay.setDisabled(True)
        
    def refresh(self):

        cards = self.connection.get_notsold_cards(self.cards)
        self.connection.commit()
        self.tableWidget.setRowCount(len(cards))
        
        nominal = 0
        i=0
        for a in cards:
            
            self.addrow(a.id, i,0)
            self.addrow(a.series, i,1)
            self.addrow(a.nominal, i,2)
            self.addrow(a.pin, i,3)
            self.addrow(a.start_date.strftime(strftimeFormat), i,4)
            self.addrow(a.end_date.strftime(strftimeFormat), i,5)
            nominal += float(a.nominal)
            i+=1
            
        self.lineEdit_count_cards.setText(unicode(len(cards)))
        self.lineEdit_amount.setText(unicode(nominal))
        self.nominalsumm=nominal
        HeaderUtil.getHeader("sale_cards_frame_header", self.tableWidget)
        
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("cards_frame_header", self.tableWidget)
        
class AddCards(QtGui.QDialog):
    def __init__(self, connection,last_series=0):
        super(AddCards, self).__init__()
        
        self.connection = connection
        self.last_series=last_series
        self.connection.commit()
        self.op_model   = AttrDict()
        self.bank_model = AttrDict()
        self.resize(573, 475)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.params_groupBox = QtGui.QGroupBox(self.tab)
        self.params_groupBox.setObjectName("params_groupBox")
        self.gridLayout_3 = QtGui.QGridLayout(self.params_groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radioButton_access = QtGui.QRadioButton(self.params_groupBox)
        self.radioButton_access.setChecked(True)
        self.radioButton_access.setObjectName("radioButton_access")
        self.gridLayout_3.addWidget(self.radioButton_access, 0, 0, 1, 1)
        self.radioButton_prepaid = QtGui.QRadioButton(self.params_groupBox)
        self.radioButton_prepaid.setChecked(False)
        self.radioButton_prepaid.setObjectName("radioButton_prepaid")
        self.gridLayout_3.addWidget(self.radioButton_prepaid, 1, 0, 1, 6)
        self.series_label = QtGui.QLabel(self.params_groupBox)
        self.series_label.setObjectName("series_label")
        self.gridLayout_3.addWidget(self.series_label, 4, 0, 1, 1)
        self.series_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.series_spinBox.setMaximum(999999999)
        self.series_spinBox.setObjectName("series_spinBox")
        self.gridLayout_3.addWidget(self.series_spinBox, 4, 1, 1, 4)
        self.nominal_label = QtGui.QLabel(self.params_groupBox)
        self.nominal_label.setObjectName("nominal_label")
        self.gridLayout_3.addWidget(self.nominal_label, 5, 0, 1, 1)
        self.spinBox_nominal = QtGui.QSpinBox(self.params_groupBox)
        self.spinBox_nominal.setFrame(True)
        self.spinBox_nominal.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.spinBox_nominal.setAccelerated(True)
        self.spinBox_nominal.setMaximum(999999999)
        self.spinBox_nominal.setObjectName("spinBox_nominal")
        self.gridLayout_3.addWidget(self.spinBox_nominal, 5, 1, 1, 4)
        self.count_label = QtGui.QLabel(self.params_groupBox)
        self.count_label.setObjectName("count_label")
        self.gridLayout_3.addWidget(self.count_label, 6, 0, 1, 1)
        self.count_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.count_spinBox.setFrame(True)
        self.count_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.count_spinBox.setAccelerated(True)
        self.count_spinBox.setMaximum(999999999)
        self.count_spinBox.setObjectName("count_spinBox")
        self.gridLayout_3.addWidget(self.count_spinBox, 6, 1, 1, 4)
        self.label_tarif = QtGui.QLabel(self.params_groupBox)
        self.label_tarif.setObjectName("label_tarif")
        self.gridLayout_3.addWidget(self.label_tarif, 7, 0, 1, 1)
        self.comboBox_tarif = QtGui.QComboBox(self.params_groupBox)
        self.comboBox_tarif.setObjectName("comboBox_tarif")
        self.gridLayout_3.addWidget(self.comboBox_tarif, 7, 1, 1, 4)
        self.label_nas = QtGui.QLabel(self.params_groupBox)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_3.addWidget(self.label_nas, 8, 0, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.params_groupBox)
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout_3.addWidget(self.comboBox_nas, 8, 1, 1, 4)
        self.label_ippool = QtGui.QLabel(self.params_groupBox)
        self.label_ippool.setObjectName("label_ippool")
        self.gridLayout_3.addWidget(self.label_ippool, 9, 0, 1, 1)
        self.comboBox_ippool = QtGui.QComboBox(self.params_groupBox)
        self.comboBox_ippool.setObjectName("comboBox_ippool")
        self.gridLayout_3.addWidget(self.comboBox_ippool, 9, 1, 1, 4)
        self.label_login = QtGui.QLabel(self.params_groupBox)
        self.label_login.setObjectName("label_login")
        self.gridLayout_3.addWidget(self.label_login, 10, 0, 1, 1)
        self.spinBox_login_from = QtGui.QSpinBox(self.params_groupBox)
        self.spinBox_login_from.setMaximum(32)
        self.spinBox_login_from.setProperty("value", 5)
        self.spinBox_login_from.setObjectName("spinBox_login_from")
        self.gridLayout_3.addWidget(self.spinBox_login_from, 10, 2, 1, 1)
        self.l_checkBox_login = QtGui.QCheckBox(self.params_groupBox)
        self.l_checkBox_login.setChecked(True)
        self.l_checkBox_login.setObjectName("l_checkBox_login")
        self.gridLayout_3.addWidget(self.l_checkBox_login, 11, 1, 1, 2)
        self.numbers_checkBox_login = QtGui.QCheckBox(self.params_groupBox)
        self.numbers_checkBox_login.setChecked(True)
        self.numbers_checkBox_login.setObjectName("numbers_checkBox_login")
        self.gridLayout_3.addWidget(self.numbers_checkBox_login, 11, 3, 1, 2)
        self.pin_label = QtGui.QLabel(self.params_groupBox)
        self.pin_label.setObjectName("pin_label")
        self.gridLayout_3.addWidget(self.pin_label, 12, 0, 1, 1)
        self.pin_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.pin_spinBox.setMaximum(32)
        self.pin_spinBox.setObjectName("pin_spinBox")
        self.gridLayout_3.addWidget(self.pin_spinBox, 12, 1, 1, 4)
        self.l_checkBox_pin = QtGui.QCheckBox(self.params_groupBox)
        self.l_checkBox_pin.setChecked(True)
        self.l_checkBox_pin.setObjectName("l_checkBox_pin")
        self.gridLayout_3.addWidget(self.l_checkBox_pin, 13, 1, 1, 2)
        self.numbers_checkBox_pin = QtGui.QCheckBox(self.params_groupBox)
        self.numbers_checkBox_pin.setChecked(True)
        self.numbers_checkBox_pin.setObjectName("numbers_checkBox_pin")
        self.gridLayout_3.addWidget(self.numbers_checkBox_pin, 13, 3, 1, 1)
        self.radioButton_hotspot = QtGui.QRadioButton(self.params_groupBox)
        self.radioButton_hotspot.setObjectName("radioButton_hotspot")
        self.gridLayout_3.addWidget(self.radioButton_hotspot, 2, 0, 1, 1)
        self.label_login_from = QtGui.QLabel(self.params_groupBox)
        self.label_login_from.setObjectName("label_login_from")
        self.gridLayout_3.addWidget(self.label_login_from, 10, 1, 1, 1)
        self.label_login_to = QtGui.QLabel(self.params_groupBox)
        self.label_login_to.setObjectName("label_login_to")
        self.gridLayout_3.addWidget(self.label_login_to, 10, 3, 1, 1)
        self.spinBox_login_to = QtGui.QSpinBox(self.params_groupBox)
        self.spinBox_login_to.setProperty("value", 7)
        self.spinBox_login_to.setObjectName("spinBox_login_to")
        self.gridLayout_3.addWidget(self.spinBox_login_to, 10, 4, 1, 1)
        self.radioButton_phone = QtGui.QRadioButton(self.params_groupBox)
        self.radioButton_phone.setObjectName("radioButton_phone")
        self.gridLayout_3.addWidget(self.radioButton_phone, 3, 0, 1, 2)
        self.gridLayout_2.addWidget(self.params_groupBox, 0, 0, 3, 1)
        self.period_groupBox = QtGui.QGroupBox(self.tab)
        self.period_groupBox.setObjectName("period_groupBox")
        self.gridLayout_4 = QtGui.QGridLayout(self.period_groupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.start_label = QtGui.QLabel(self.period_groupBox)
        self.start_label.setObjectName("start_label")
        self.gridLayout_4.addWidget(self.start_label, 0, 0, 1, 1)
        self.start_dateTimeEdit = CustomDateTimeWidget()
        self.start_dateTimeEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2011, 1, 1), QtCore.QTime(0, 0, 0)))
        self.start_dateTimeEdit.setCalendarPopup(True)
        self.start_dateTimeEdit.setObjectName("start_dateTimeEdit")
        self.gridLayout_4.addWidget(self.start_dateTimeEdit, 0, 1, 1, 1)
        self.end_label = QtGui.QLabel(self.period_groupBox)
        self.end_label.setObjectName("end_label")
        self.gridLayout_4.addWidget(self.end_label, 1, 0, 1, 1)
        self.end_dateTimeEdit = CustomDateTimeWidget()
        self.end_dateTimeEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2012, 1, 1), QtCore.QTime(0, 0, 0)))
        self.end_dateTimeEdit.setCalendarPopup(True)
        self.end_dateTimeEdit.setObjectName("end_dateTimeEdit")
        self.gridLayout_4.addWidget(self.end_dateTimeEdit, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.period_groupBox, 0, 1, 1, 1)
        self.groupBox_template = QtGui.QGroupBox(self.tab)
        self.groupBox_template.setObjectName("groupBox_template")
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_template)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.comboBox_templates = QtGui.QComboBox(self.groupBox_template)
        self.comboBox_templates.setFrame(True)
        self.comboBox_templates.setObjectName("comboBox_templates")
        self.gridLayout_5.addWidget(self.comboBox_templates, 0, 0, 1, 2)
        self.toolButton_preview = QtGui.QToolButton(self.groupBox_template)
        self.toolButton_preview.setObjectName("toolButton_preview")
        self.gridLayout_5.addWidget(self.toolButton_preview, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_template, 1, 1, 1, 1)
        self.groupBox_info = QtGui.QGroupBox(self.tab)
        self.groupBox_info.setObjectName("groupBox_info")
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_info)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.textBrowser = QtGui.QTextBrowser(self.groupBox_info)
        self.textBrowser.setEnabled(True)
        self.textBrowser.setFrameShape(QtGui.QFrame.Box)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setAcceptRichText(False)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textBrowser.setOpenLinks(False)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_6.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_info, 2, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)


        
        self.spinBox_login_from.setValue(5)
        self.spinBox_login_to.setValue(7)
        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.toolButton_preview,QtCore.SIGNAL("clicked()"),self.preView)
        self.connect(self.radioButton_access, QtCore.SIGNAL("clicked()"), self.check_card_type)
        self.connect(self.radioButton_prepaid, QtCore.SIGNAL("clicked()"), self.check_card_type)
        self.connect(self.radioButton_hotspot, QtCore.SIGNAL("clicked()"), self.check_card_type)
        self.connect(self.radioButton_phone, QtCore.SIGNAL("clicked()"), self.check_card_type)
        self.fixtures()
        self.check_card_type()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры серии", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры генерации карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_access.setText(QtGui.QApplication.translate("Dialog", "VPN Карты доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_prepaid.setText(QtGui.QApplication.translate("Dialog", "Карты предоплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.series_label.setText(QtGui.QApplication.translate("Dialog", "Серия", None, QtGui.QApplication.UnicodeUTF8))
        self.nominal_label.setText(QtGui.QApplication.translate("Dialog", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.count_label.setText(QtGui.QApplication.translate("Dialog", "Количество", None, QtGui.QApplication.UnicodeUTF8))
        self.label_tarif.setText(QtGui.QApplication.translate("Dialog", "Тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ippool.setText(QtGui.QApplication.translate("Dialog", "IP пул", None, QtGui.QApplication.UnicodeUTF8))
        self.label_login.setText(QtGui.QApplication.translate("Dialog", "Длина логина", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_login_from.setProperty("text", QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.l_checkBox_login.setText(QtGui.QApplication.translate("Dialog", "a-Z", None, QtGui.QApplication.UnicodeUTF8))
        self.numbers_checkBox_login.setText(QtGui.QApplication.translate("Dialog", "0-9", None, QtGui.QApplication.UnicodeUTF8))
        self.pin_label.setText(QtGui.QApplication.translate("Dialog", "Длина пина", None, QtGui.QApplication.UnicodeUTF8))
        self.pin_spinBox.setProperty("text", QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.l_checkBox_pin.setText(QtGui.QApplication.translate("Dialog", "a-Z", None, QtGui.QApplication.UnicodeUTF8))
        self.numbers_checkBox_pin.setText(QtGui.QApplication.translate("Dialog", "0-9", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_hotspot.setText(QtGui.QApplication.translate("Dialog", "HotSpot карты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_login_from.setText(QtGui.QApplication.translate("Dialog", "от", None, QtGui.QApplication.UnicodeUTF8))
        self.label_login_to.setText(QtGui.QApplication.translate("Dialog", "до", None, QtGui.QApplication.UnicodeUTF8))
        self.period_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Период действия", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_template.setTitle(QtGui.QApplication.translate("Dialog", "Шаблон для печати", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_preview.setText(QtGui.QApplication.translate("Dialog", "Предросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_info.setTitle(QtGui.QApplication.translate("Dialog", "Информация", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">При создании карт доступа, убедитесь что в выбранном пуле присутствует достаточное количество свободных IP адресов.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_phone.setText(QtGui.QApplication.translate("Dialog", "Телефонные карты", None, QtGui.QApplication.UnicodeUTF8))

    def check_card_type(self):
        if self.radioButton_access.isChecked()==True:
            self.comboBox_tarif.setDisabled(False)
            self.spinBox_login_from.setDisabled(False)
            self.spinBox_login_to.setDisabled(False)
            self.comboBox_ippool.setDisabled(False)
            self.comboBox_nas.setDisabled(False)
            self.l_checkBox_login.setDisabled(False)
            self.numbers_checkBox_login.setDisabled(False)
        
        if self.radioButton_prepaid.isChecked()==True:
            self.comboBox_tarif.setDisabled(True)
            self.spinBox_login_from.setDisabled(True)
            self.spinBox_login_to.setDisabled(True)
            self.comboBox_ippool.setDisabled(True)
            self.comboBox_nas.setDisabled(True)
            self.l_checkBox_login.setDisabled(True)
            self.numbers_checkBox_login.setDisabled(True)

        if self.radioButton_hotspot.isChecked()==True or self.radioButton_phone.isChecked()==True :
            self.comboBox_tarif.setDisabled(False)
            self.spinBox_login_from.setDisabled(False)
            self.spinBox_login_to.setDisabled(False)
            self.comboBox_ippool.setDisabled(False)
            self.comboBox_nas.setDisabled(True)
            self.l_checkBox_login.setDisabled(False)
            self.numbers_checkBox_login.setDisabled(False)


            
    def accept(self):
        """
        понаставить проверок
        """
        #try:
        if self.l_checkBox_pin.checkState()==0 and self.numbers_checkBox_pin.checkState()==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не выбрали состав PIN-кода"))
            return
        
        if self.spinBox_nominal.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан номинал"))
            return
        
        if self.count_spinBox.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано количество генерируемых карточек"))
            return
        
        if self.pin_spinBox.text().toInt()[0]==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана длина PIN-кода"))
            return     
        
        if (self.radioButton_access.isChecked() or self.radioButton_hotspot.isChecked() ) and (self.spinBox_login_to.value()<self.spinBox_login_from.value() or self.spinBox_login_from.value()==0 or self.spinBox_login_to.value()==self.spinBox_login_from.value()):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность указания длины логина"))
            return     
            

######################33
        
        
        pin_mask = ''
        if self.l_checkBox_pin.checkState()==2:
            pin_mask+=string.letters
        if self.numbers_checkBox_pin.checkState()==2:
            pin_mask+=string.digits
        login_mask = ''
        if self.l_checkBox_login.checkState()==2:
            login_mask+=string.letters
        if self.numbers_checkBox_login.checkState()==2:
            login_mask+=string.digits
            
        dnow = datetime.datetime.now()
        if self.radioButton_access.isChecked() or self.radioButton_hotspot.isChecked()or self.radioButton_phone.isChecked():
            tarif_id = self.comboBox_tarif.itemData(self.comboBox_tarif.currentIndex()).toInt()[0]
            
        template_id = self.comboBox_templates.itemData(self.comboBox_templates.currentIndex()).toInt()[0]
        
        if self.radioButton_access.isChecked():
            nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0] or None
        pool_id=None
        if self.radioButton_access.isChecked() or self.radioButton_hotspot.isChecked():
            pool_id = self.comboBox_ippool.itemData(self.comboBox_ippool.currentIndex()).toInt()[0]
            #ips = get_free_addreses_from_pool(self.connection, self.comboBox_ippool.itemData(self.comboBox_ippool.currentIndex()).toInt()[0], self.count_spinBox.text().toInt()[0])
            
        cards_count=self.count_spinBox.value()
        i=0
        bad=0
        """
        типы карт
        0 - экспресс оплата
        1 - хотспот
        2- vpn доступ 
        """
        while i<cards_count:
            if bad>=1000:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Было сгенерировано только %s карт.\nРасширьте условия генерации для уменьшения количества дублирующихся логинов." % i))
                return   
            model = AttrDict()

            model.series = unicode(self.series_spinBox.text())
            model.pin = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=pin_mask)
            model.type = 0
            if self.radioButton_access.isChecked()==True:
                model.login = "%s%s" % (model.series, GenPasswd2(length=randint(self.spinBox_login_from.value(), self.spinBox_login_to.value())-1,chars=login_mask))
                model.tarif = tarif_id
                model.ippool = pool_id
                model.nas = nas_id
                model.type = 2
            if self.radioButton_hotspot.isChecked():
                model.login = "%s%s" % (model.series, GenPasswd2(length=randint(self.spinBox_login_from.value(), self.spinBox_login_to.value())-1,chars=login_mask))
                model.tarif = tarif_id
                model.type = 1
                model.ippool_id = pool_id or None
            if self.radioButton_phone.isChecked():
                model.login = "%s%s" % (model.series, GenPasswd2(length=randint(self.spinBox_login_from.value(), self.spinBox_login_to.value())-1,chars=login_mask))
                model.tarif = tarif_id
                model.type = 3
                
            model.nominal = unicode(self.spinBox_nominal.value())
            model.start_date = self.start_dateTimeEdit.currentDate()
            model.end_date = self.end_dateTimeEdit.currentDate()
            model.template = template_id
            
            model.created = dnow

            try:
                self.connection.cards_save(model)
                self.connection.commit()
                i+=1
            except:
                bad+=1
                print "found dublicates"
                
        
        #except Exception, ex:
        #    self.connection.rollback()
        #    print ex
        #    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Во время генерации карт возникла непредвиденная ошибка."))
        #    return

        QtGui.QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        #end=datetime.datetime.now()
        self.last_series = self.connection.get_next_cardseries()[0]
        self.series_spinBox.setValue(self.last_series)
        self.start_dateTimeEdit.setMinimumDate(start)
        self.end_dateTimeEdit.setMinimumDate(start)
        self.count_spinBox.setValue(100)
        self.pin_spinBox.setValue(10)
        #self.updateTemplates()
        

            
        tarifs = self.connection.get_tariffs(fields=['id', 'name'])
        #???TODOtarifs = self.connection.sql("SELECT id, name FROM billservice_tariff as tariff WHERE deleted=False and access_parameters_id not in (SELECT id FROM billservice_accessparameters WHERE access_type in ('IPN','lISG','DHCP'))")
        self.connection.commit()
        self.comboBox_tarif.clear()
        i=0
        #print tarifs
        for tarif in tarifs:
            self.comboBox_tarif.addItem(tarif.name)
            self.comboBox_tarif.setItemData(i, QtCore.QVariant(tarif.id))
            i+=1
            
        templates = self.connection.get_templates( type_id=7, fields=['id', 'name'])
        self.connection.commit()
        i=0
        for templ in templates:
            self.comboBox_templates.addItem(templ.name)
            self.comboBox_templates.setItemData(i, QtCore.QVariant(templ.id))
            i+=1

        pools = self.connection.get_ippools(fields=['id', 'name'])
        self.connection.commit()
        i=0
        self.comboBox_ippool.addItem('---',QtCore.QVariant(None))
        for pool in pools:
            self.comboBox_ippool.addItem(pool.name, QtCore.QVariant(pool.id))
            i+=1
            
        nasses = self.connection.get_nasses(fields=['id', 'name'])
        self.connection.commit()
        self.comboBox_nas.addItem(u"--Не указан--", QtCore.QVariant(None))
        i=1
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name)
            self.comboBox_nas.setItemData(i, QtCore.QVariant(nas.id))
            i+=1
            
    def preView(self):
        try:
            operator =self.connection.get_operator()
            
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
            return

        try:
            bank =self.connection.get_banks(operator.bank)
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
            return
        self.connection.commit()
        
        tmplt = self.comboBox_templates.itemData(self.comboBox_templates.currentIndex()).toInt()[0]
        if not tmplt:
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Вы не выбрали шаблон!")
            return
        pin_mask = ''
        if self.l_checkBox_pin.checkState()==2:
            pin_mask+=string.letters
        if self.numbers_checkBox_pin.checkState()==2:
            pin_mask+=string.digits
        login_mask = ''
        if self.l_checkBox_login.checkState()==2:
            login_mask+=string.letters
        if self.numbers_checkBox_login.checkState()==2:
            login_mask+=string.digits
        card = AttrDict()
        card.pin = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=pin_mask)
        card.login = GenPasswd2(length=self.spinBox_login_from.text().toInt()[0],chars=login_mask)
        card.nominal = unicode(self.spinBox_nominal.text())
        card.id = unicode("100")
        card.start_date = self.start_dateTimeEdit.currentDate()
        card.end_date = self.end_dateTimeEdit.currentDate()
        card.series = unicode(self.series_spinBox.value())
        card.tarif = unicode(self.comboBox_tarif.currentText())
        #operator=self.op_model.__dict__
        #bank = self.bank_model.__dict__
        
        data="""
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        </head>
        <body>
        """;
        #print "====", self.comboBox_templates.itemData(self.comboBox_templates.currentIndex()).toInt()[0]

        
        template = self.connection.get_templates(self.comboBox_templates.itemData(self.comboBox_templates.currentIndex()).toInt()[0], "billservice_template")
        #print template.body
        templ = Template(template.body, input_encoding='utf-8')
        try:
            data+=templ.render_unicode(connection=self.connection, card=card, operator=operator, bank=bank)
        except Exception, e:
            data=unicode(u""" <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body style="text-align:center;">%s</body></html>""" % repr(e))
        
        data+="</body></html>"
        file= open('templates/cards/cards.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        a=CardPreviewDialog(url="templates/cards/cards.html")
        a.exec_()        
        
    #def updateTemplates(self):
    #    self.comboBox_templates.addItems([unicode(tmplt) for tmplt in os.listdir(templatedir) if ((tmplt.find("_printandum_") == -1) and os.path.isfile(''.join((templatedir, '/',tmplt))))])

class CardsChildEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'Серия', u'Номинал', u'Тип', u'Пул', u'Логин', u'PIN',  u'Ext ID', u'Тариф', u'NAS', u"Продано", u"Активировано", u'Активировать c', u'Активировать по']
        initargs = {"setname":"cards_frame", "objname":"CardsFrameMDI", "winsize":(0,0,947, 619), "wintitle":"Система карт оплаты", "tablecolumns":columns}
        super(CardsChildEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setIconSize(QtCore.QSize(18, 18))
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.toolBar_filter = QtGui.QToolBar(self)
        self.toolBar_filter.setMovable(False)
        self.toolBar_filter.setAllowedAreas(QtCore.Qt.BottomToolBarArea)
        self.toolBar_filter.setFloatable(False)
        self.toolBar_filter.setObjectName("toolBar_filter")
        ###################### Filter
        self.comboBox_nominal = QtGui.QComboBox()        
        self.comboBox_nominal.setGeometry(QtCore.QRect(0,0,60,20))
        self.comboBox_nominal.setEditable(True)
        
        self.date_start = CustomDateTimeWidget()
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        #self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")
        #self.date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
 
        self.date_end = CustomDateTimeWidget()
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        #self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        #self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")
        #self.date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
 
        self.label_date_start = QtGui.QLabel()
        self.label_date_start.setMargin(10)
        self.label_date_start.setObjectName("date_start_label")
 
        self.label_date_end = QtGui.QLabel()
        self.label_date_end.setMargin(10)
        self.label_date_end.setObjectName("date_end_label")
        
        self.label_nominal = QtGui.QLabel()
        self.label_nominal.setMargin(10)        
        self.label_filter = QtGui.QLabel()
        self.label_filter.setMargin(10)
        
        self.checkBox_sold = QtGui.QCheckBox()
        self.checkBox_activated = QtGui.QCheckBox()        
        self.checkBox_filter = QtGui.QCheckBox()        
        self.pushButton_go = QtGui.QPushButton()
        
        self.toolBar_filter.addWidget(self.checkBox_filter)
        self.toolBar_filter.addWidget(self.label_nominal)
        self.toolBar_filter.addWidget(self.comboBox_nominal)
        self.toolBar_filter.addWidget(self.checkBox_sold)
        self.toolBar_filter.addWidget(self.checkBox_activated)
        self.toolBar_filter.addSeparator()
        self.toolBar_filter.addWidget(self.label_date_start)
        self.toolBar_filter.addWidget(self.date_start)
        self.toolBar_filter.addWidget(self.label_date_end)
        self.toolBar_filter.addWidget(self.date_end)
        self.toolBar_filter.addWidget(self.pushButton_go)
        #####################        
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_filter)
        self.insertToolBarBreak(self.toolBar_filter)

        actList=[("actionGenerate_Cards", "Сгенерировать", "images/add.png", self.generateCards), ("actionDelete_Cards", "Удалить карты", "images/del.png", self.deleteCards), ("actionEnable_Card", "Активна", "images/enable.png", self.enableCard), ("actionDisable_Card", "Неактивна", "images/disable.png", self.disableCard), ("actionSell_Card", "Продать", "images/dollar.png", self.saleCard), ("actionExportXml", "Выгрузить выделенные в xml", "images/fileexport.png", self.export_cards),  ("actionRefresh", "Обновить", "images/reload.png", self.refr)]
        objDict = {self.tableWidget:['actionRefresh', "actionDelete_Cards", "actionEnable_Card", "actionDisable_Card"], self.toolBar:['actionRefresh', "actionGenerate_Cards", "actionDelete_Cards", "actionEnable_Card", "actionDisable_Card", "actionSell_Card", "actionExportXml"]}
        self.actionCreator(actList, objDict)
        
    def ebsPostInit(self, initargs):
        self.connect(self.pushButton_go, QtCore.SIGNAL("clicked()"),  self.refr)
        self.connect(self.checkBox_filter, QtCore.SIGNAL("stateChanged(int)"), self.filterActions)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.fixtures()        
        self.filterActions()
        self.delNodeLocalAction()
        self.refr()
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("cards_date_start", QtCore.QVariant(QtCore.QDateTime(2009,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("cards_date_end", QtCore.QVariant(QtCore.QDateTime(2020,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex
            
    def retranslateUI(self, initargs):
        super(CardsChildEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_filter.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nominal.setText(QtGui.QApplication.translate("MainWindow", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_filter.setText(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_start.setText(QtGui.QApplication.translate("MainWindow", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_end.setText(QtGui.QApplication.translate("MainWindow", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_sold.setText(QtGui.QApplication.translate("MainWindow", "Проданные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_activated.setText(QtGui.QApplication.translate("MainWindow", "Активированные", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_go.setText(QtGui.QApplication.translate("MainWindow", "Фильтровать", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, True)
        
    def saleCard(self):
        
        items = self.tableWidget.selectedIndexes()
        cards = []
        for item in items:
            if item.column()>0:
                continue
            cards.append(unicode(self.tableWidget.item(item.row(), 0).text()))
        
        child = SaleCards(connection=self.connection, cards = cards)
        if child.exec_()==1:
            self.refr()
        
    def export_cards(self):
        ids=self.get_selected_ids(self.tableWidget)
        self.exportToXML(ids)

            
    def get_selected_ids(self, table):
        ids = []
        for r in table.selectedItems():
            if r.column()==0:
                if r.id:
                    ids.append(r.id)
        return ids
    
    def exportToXML(self, ids):
        fileName = str(QtGui.QFileDialog.getSaveFileName(self,
                                                  "Create XML File", "", "XML Files (*.xml)")).decode('mbcs')
        if fileName=="":
            return
        #try:
        import codecs
        if True:
            
            f = codecs.open(fileName, "w", "utf-8")
            f.write("<xml>")
            for x in ids:
                #card = unicode(self.tableWidget.item(x,0).text())
                card = self.connection.get_cards(id=x)
                self.connection.commit()
                #print x,card
                f.write("<card>")
                f.write("<id>%s</id>" % card.id)
                #f.write(u"<tarif>"+unicode(card.tarif_name)+"</tarif>")
                f.write(u"<tarif>%s</tarif>" % card.tarif)
                f.write(u"<series>%s</series>" % card.series)
                f.write(u"<nominal>%s</nominal>" % card.nominal)
                f.write(u"<pin>%s</pin>" % card.pin)
                f.write(u"<login>%s</login>" % card.login)
                f.write(u"<template>%s</template>" % card.template)
                f.write(u"<nas>%s</nas>" % card.nas)
                f.write(u"<ip>%s</ip>" % card.ip)
                f.write(u"<date_start>%s</date_start>" % card.start_date)
                f.write(u"<date_end>%s</date_end>" % card.end_date)
                
                f.write("</card>")
            f.write("</xml>")
            f.close()
            QtGui.QMessageBox.information(self, u"Файл успешно сохранён", unicode(u"Операция произведена успешно."))
            
    def fixtures(self):
        nominals = self.connection.get_cards_nominal()
        self.connection.commit()
        self.comboBox_nominal.clear()
        for nom in nominals:            
            self.comboBox_nominal.addItem(unicode(nom[0]))
            
    def filterActions(self):
        if self.checkBox_filter.checkState()==2:
            self.label_nominal.setDisabled(False)
            self.comboBox_nominal.setDisabled(False)
            self.label_date_start.setDisabled(False)
            self.date_start.setDisabled(False)
            self.label_date_end.setDisabled(False)
            self.date_end.setDisabled(False)
            self.checkBox_sold.setDisabled(False)
            self.checkBox_activated.setDisabled(False)
            self.pushButton_go.setDisabled(False)
        else:
            self.label_nominal.setDisabled(True)
            self.comboBox_nominal.setDisabled(True)
            self.label_date_start.setDisabled(True)
            self.date_start.setDisabled(True)
            self.label_date_end.setDisabled(True)
            self.date_end.setDisabled(True)
            self.checkBox_sold.setDisabled(True)
            self.checkBox_activated.setDisabled(True)
            self.pushButton_go.setDisabled(True)
            #self.refresh()
            
    def enableCard(self):
        ids = []
        for index in self.tableWidget.selectedIndexes():
            if index.column()>=1:
                continue
            ids.append(unicode(self.tableWidget.item(index.row(), 0).text()))

        self.connection.set_cardsstatus(ids, status=False)
        
        self.refr()
    
    def disableCard(self):
        ids = []
        for index in self.tableWidget.selectedIndexes():
            if index.column()>=1:
                continue
            ids.append(unicode(self.tableWidget.item(index.row(), 0).text()))

        self.connection.set_cardsstatus(ids, status=True)
        
        self.refr()
        
    def deleteCards(self):
        """
        """
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>=1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                self.connection.cards_delete(i)
            except Exception, e:
                pass  
            
        self.connection.commit()    
        self.refr()     

    def generateCards(self):

        #print model.id
        
        last_series = self.connection.get_next_cardseries()[0]
        
        print "last_series", last_series
        child=AddCards(connection=self.connection, last_series=last_series)
        if child.exec_()==1:
            self.refr()
            self.fixtures()
        
        
    def refresh(self):
        pass
    
    def refr(self, widget=None):
        
        self.statusBar().showMessage(u"Ожидание ответа")
        sql = """SELECT *,(SELECT name FROM billservice_ippool WHERE id=c.ippool_id) as pool_name FROM billservice_card as c"""
        if self.checkBox_filter.checkState()==2:
            start_date = self.date_start.currentDate()
            end_date = self.date_end.currentDate()
            sql+=" WHERE id>0"
            if unicode(self.comboBox_nominal.currentText())!="":
                sql+=" AND nominal = '%s'" % unicode(self.comboBox_nominal.currentText())
                
            if self.checkBox_activated.checkState() == 2:
                sql+=" AND activated>'%s' and activated<'%s'" % (start_date, end_date)
            
            if self.checkBox_sold.checkState() == 2:
                sql+=" OR sold>'%s' and sold<'%s'" % (start_date, end_date)
                
            if self.checkBox_sold.checkState() == 0 and self.checkBox_activated.checkState() == 0:
                sql+=" OR start_date>'%s' and end_date<'%s'" % (start_date, end_date)
        else:
            sql+=" WHERE sold is Null"
            
        sql += " ORDER BY id;"
            
        self.tableWidget.setSortingEnabled(False)

            
        self.tableWidget.clearContents()
        nodes=self.connection.sql(sql)
        #print nodes
        tariffs = self.connection.get_tariffs(fields=['id', 'name'])
        t={}
        for tar in tariffs:
            t['%s' % tar.id] = tar.name

        nasses = self.connection.get_nasses(fields=['id','name'])
        n = {}
        for nas in nasses:
            n['%s' % nas.id] = nas.name
            
        self.tableWidget.setRowCount(len(nodes))
        i=0        
        
        card_types=[u'Карта экспресс-оплаты',u'HotSpot карта',u'VPN карта доступа',u"Телефонные карты"]
        for node in nodes:
            self.addrow(node.id, i,0, status = node.disabled, activated=node.activated, id=node.id)
            self.addrow(node.series, i,1, status = node.disabled, activated=node.activated)
            self.addrow(node.nominal, i,2, status = node.disabled, activated=node.activated)
            self.addrow(card_types[node.type], i,3, status = node.disabled, activated=node.activated)
            self.addrow(node.pool_name, i,4, status = node.disabled, activated=node.activated)
            self.addrow(node.login, i,5, status = node.disabled, activated=node.activated)
            self.addrow(node.pin, i,6, status = node.disabled, activated=node.activated)
            self.addrow(node.ext_id, i,7, status = node.disabled, activated=node.activated)
            self.addrow(t.get("%s" % node.tarif_id), i,8, status = node.disabled, activated=node.activated)
            self.addrow(n.get("%s" % node.nas_id), i,9, status = node.disabled, activated=node.activated)
            
            self.addrow(node.sold, i,10, status = node.disabled, activated=node.activated)
            self.addrow(node.activated, i,11, status = node.disabled, activated=node.activated)
            self.addrow(node.start_date.strftime(self.strftimeFormat), i,12, status = node.disabled, activated=node.activated)
            self.addrow(node.end_date.strftime(self.strftimeFormat), i,13, status = node.disabled, activated=node.activated)
            i+=1
            
        self.statusBar().showMessage(u"Данные получены")
        self.tableWidget.setColumnHidden(0, False)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.delNodeLocalAction()
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("cards_date_start", QtCore.QVariant(self.date_start.currentDate()))
            settings.setValue("cards_date_end", QtCore.QVariant(self.date_end.currentDate()))
        except Exception, ex:
            print "Cards settings save error: ", ex        


    def addrow(self, value, x, y, status, activated, id=None):
        headerItem = QtGui.QTableWidgetItem()
        
        if value == None:
            value = ""
        
        headerItem.setText(unicode(value))
        
        if status==True:
            headerItem.setTextColor(QtGui.QColor('#FF0100'))
        
        if y==5:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        if activated == None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/ok.png"))
        elif activated!=None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/false.png"))
    
        if id:
            headerItem.id=id
        self.tableWidget.setItem(x,y,headerItem)
        

        
       
    def delNodeLocalAction(self):
        super(CardsChildEbs, self).delNodeLocalAction([self.actionDelete_Cards, self.actionEnable_Card, self.actionDisable_Card, self.actionSell_Card])

