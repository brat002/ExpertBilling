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

class AccountHardwareDialog(QtGui.QDialog):
    def __init__(self,connection, account_model=None, model=None):
        super(AccountHardwareDialog, self).__init__()
        self.connection=connection
        self.model=model
        self.account_model=account_model
        self.setObjectName(_fromUtf8("AccountHardwareDialog"))
        self.resize(658, 393)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_model = QtGui.QLabel(self.groupBox)
        self.label_model.setObjectName(_fromUtf8("label_model"))
        self.gridLayout_2.addWidget(self.label_model, 3, 0, 1, 1)
        self.comboBox_model = QtGui.QComboBox(self.groupBox)
        self.comboBox_model.setObjectName(_fromUtf8("comboBox_model"))
        self.gridLayout_2.addWidget(self.comboBox_model, 3, 1, 1, 1)
        self.label_datetime_transfer_date = QtGui.QLabel(self.groupBox)
        self.label_datetime_transfer_date.setObjectName(_fromUtf8("label_datetime_transfer_date"))
        self.gridLayout_2.addWidget(self.label_datetime_transfer_date, 5, 0, 1, 1)
        self.dateTimeEdit_transfer_date = CustomDateTimeWidget()
        self.dateTimeEdit_transfer_date.setObjectName(_fromUtf8("dateTimeEdit_transfer_date"))
        self.gridLayout_2.addWidget(self.dateTimeEdit_transfer_date, 5, 1, 1, 1)
        self.checkBox_return = QtGui.QCheckBox(self.groupBox)
        self.checkBox_return.setObjectName(_fromUtf8("checkBox_return"))
        self.gridLayout_2.addWidget(self.checkBox_return, 6, 1, 1, 1)
        self.label_return_date = QtGui.QLabel(self.groupBox)
        self.label_return_date.setObjectName(_fromUtf8("label_return_date"))
        self.gridLayout_2.addWidget(self.label_return_date, 7, 0, 1, 1)
        self.dateTimeEdit_return_date = CustomDateTimeWidget()
        self.dateTimeEdit_return_date.setObjectName(_fromUtf8("dateTimeEdit_return_date"))
        self.gridLayout_2.addWidget(self.dateTimeEdit_return_date, 7, 1, 1, 1)
        self.comboBox_manufacturer = QtGui.QComboBox(self.groupBox)
        self.comboBox_manufacturer.setObjectName(_fromUtf8("comboBox_manufacturer"))
        self.gridLayout_2.addWidget(self.comboBox_manufacturer, 0, 1, 1, 1)
        self.label_manufacturer = QtGui.QLabel(self.groupBox)
        self.label_manufacturer.setObjectName(_fromUtf8("label_manufacturer"))
        self.gridLayout_2.addWidget(self.label_manufacturer, 0, 0, 1, 1)
        self.comboBox_hardwaretype = QtGui.QComboBox(self.groupBox)
        self.comboBox_hardwaretype.setObjectName(_fromUtf8("comboBox_hardwaretype"))
        self.gridLayout_2.addWidget(self.comboBox_hardwaretype, 2, 1, 1, 1)
        self.comboBox_hardware = QtGui.QComboBox(self.groupBox)
        self.comboBox_hardware.setObjectName(_fromUtf8("comboBox_hardware"))
        self.gridLayout_2.addWidget(self.comboBox_hardware, 4, 1, 1, 1)
        self.label_hardware = QtGui.QLabel(self.groupBox)
        self.label_hardware.setObjectName(_fromUtf8("label_hardware"))
        self.gridLayout_2.addWidget(self.label_hardware, 4, 0, 1, 1)
        self.label_comment = QtGui.QLabel(self.groupBox)
        self.label_comment.setObjectName(_fromUtf8("label_comment"))
        self.gridLayout_2.addWidget(self.label_comment, 8, 0, 1, 1)
        self.label_hardwaretype = QtGui.QLabel(self.groupBox)
        self.label_hardwaretype.setObjectName(_fromUtf8("label_hardwaretype"))
        self.gridLayout_2.addWidget(self.label_hardwaretype, 2, 0, 1, 1)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout_2.addWidget(self.plainTextEdit, 8, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        
        self.connect(self.comboBox_manufacturer, QtCore.SIGNAL("currentIndexChanged(int)"), self.set_hardwaretype)
        self.connect(self.comboBox_hardwaretype, QtCore.SIGNAL("currentIndexChanged(int)"), self.set_model)
        self.connect(self.comboBox_model, QtCore.SIGNAL("currentIndexChanged(int)"), self.set_hardware)
        self.connect(self.checkBox_return, QtCore.SIGNAL("stateChanged(int)"), self.returned_check)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.setTabOrder(self.comboBox_manufacturer, self.comboBox_hardwaretype)
        self.setTabOrder(self.comboBox_hardwaretype, self.comboBox_model)
        self.setTabOrder(self.comboBox_model, self.comboBox_hardware)
        self.setTabOrder(self.comboBox_hardware, self.dateTimeEdit_transfer_date)
        self.setTabOrder(self.dateTimeEdit_transfer_date, self.checkBox_return)
        self.setTabOrder(self.checkBox_return, self.dateTimeEdit_return_date)
        self.setTabOrder(self.dateTimeEdit_return_date, self.plainTextEdit)
        self.setTabOrder(self.plainTextEdit, self.buttonBox)


        self.fixtures()
        self.returned_check()
        

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("AccountHardwareDialog", "Выдача оборудования на руки", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("AccountHardwareDialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.label_model.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Модель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_datetime_transfer_date.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Дата выдачи", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_transfer_date.setDisplayFormat(QtGui.QApplication.translate("AccountHardwareDialog", "dd.MM.yy H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_return.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Оборудование возвращено", None, QtGui.QApplication.UnicodeUTF8))
        self.label_return_date.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Дата возврата", None, QtGui.QApplication.UnicodeUTF8))
        self.label_manufacturer.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Производитель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_hardware.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Серийный номер", None, QtGui.QApplication.UnicodeUTF8))
        self.label_comment.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_hardwaretype.setText(QtGui.QApplication.translate("AccountHardwareDialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))


    def set_hardwaretype(self,index):
        id=self.comboBox_manufacturer.itemData(index).toInt()[0]
        items = self.connection.get_models("billservice_hardwaretype", order={'name':'ASC'}, fields=['id', 'name'])
        self.connection.commit()
        self.comboBox_hardwaretype.clear()
        i=0
        for item in items:
            self.comboBox_hardwaretype.addItem(item.name, QtCore.QVariant(item.id))
            i+=1   

        hardwaretype_id=self.comboBox_hardwaretype.itemData(0).toInt()[0]
        if hardwaretype_id:
            items = self.connection.get_models("billservice_model", order={'name':'ASC'}, fields=['id', 'name'], where={'manufacturer_id':id, 'hardwaretype_id':hardwaretype_id})
            self.connection.commit()
            self.comboBox_model.clear()
            i=0
            for item in items:
                self.comboBox_model.addItem(item.name, QtCore.QVariant(item.id))
                i+=1   
            
    def set_model(self, index):
        id=self.comboBox_hardwaretype.itemData(index).toInt()[0]
        manufacturer_id=self.comboBox_manufacturer.itemData(self.comboBox_manufacturer.currentIndex()).toInt()[0]
        items = self.connection.get_models("billservice_model", order={'name':'ASC'}, fields=['id', 'name'], where={'manufacturer_id':manufacturer_id, 'hardwaretype_id':id})
        self.connection.commit()
        self.comboBox_model.clear()
        i=0
        for item in items:
            self.comboBox_model.addItem(item.name, QtCore.QVariant(item.id))
            i+=1  
            
            
    def set_hardware(self, index):
        id=self.comboBox_model.itemData(index).toInt()[0]
        items = self.connection.get_models("billservice_hardware", order={'sn':'ASC'}, fields=['id', 'name', 'sn'], where={'model_id':id})
        self.connection.commit()
        self.comboBox_hardware.clear()
        i=0
        for item in items:
            self.comboBox_hardware.addItem(u"%s %s" % (item.name, item.sn), QtCore.QVariant(item.id))
            i+=1     
          
    def returned_check(self):
        self.dateTimeEdit_return_date.setDisabled(True)
        if self.model:
            if self.checkBox_return.isChecked():
                self.dateTimeEdit_return_date.setDisabled(False)
                       
    def fixtures(self):
        hw=None
        if self.model:
            hw=self.connection.get("""
            SELECT hw.id as hardware_id,model.id as model_id,hwtype.id as hwtype_id,m.id as manufacturer_id 
            FROM billservice_accounthardware as ahw 
            JOIN billservice_hardware as hw ON ahw.hardware_id=hw.id
            JOIN billservice_model as model ON model.id=hw.model_id
            JOIN billservice_hardwaretype as hwtype ON hwtype.id=model.hardwaretype_id
            JOIN billservice_manufacturer as m ON m.id=model.manufacturer_id
            WHERE ahw.id=%s        
            """ % self.model.id)     
               
        items = self.connection.get_models("billservice_manufacturer", order={'name':'ASC'}, fields=['id', 'name'])
        self.connection.commit()
        self.comboBox_model.clear()
        i=0
        for item in items:
            self.comboBox_manufacturer.addItem(item.name, QtCore.QVariant(item.id))
            if hw:
                if hw.manufacturer_id==item.id:
                    self.comboBox_model.setCurrentIndex(i)
            i+=1    

        if self.model:
            items = self.connection.get_models("billservice_hardwaretype", order={'name':'ASC'}, fields=['id', 'name'])
            self.connection.commit()
            self.comboBox_hardwaretype.clear()
            i=0
            for item in items:
                self.comboBox_hardwaretype.addItem(item.name, QtCore.QVariant(item.id))
                if hw:
                    if hw.hwtype_id==item.id:
                        self.comboBox_hardwaretype.setCurrentIndex(i)
                i+=1    
                
            items = self.connection.get_models("billservice_model", order={'name':'ASC'}, fields=['id', 'name'])
            self.connection.commit()
            self.comboBox_model.clear()
            i=0
            for item in items:
                self.comboBox_model.addItem(item.name, QtCore.QVariant(item.id))
                if hw:
                    if hw.model_id==item.id:
                        self.comboBox_model.setCurrentIndex(i)
                i+=1   
                
            items = self.connection.get_models("billservice_hardware", order={'name':'ASC'}, fields=['id', 'name', 'sn'])
            self.connection.commit()
            self.comboBox_hardware.clear()
            i=0
            for item in items:
                self.comboBox_hardware.addItem(u"%s %s" % (item.name,item.sn), QtCore.QVariant(item.id))
                if hw:
                    if hw.hardware_id==item.id:
                        self.comboBox_hardware.setCurrentIndex(i)
                i+=1 
                
            self.dateTimeEdit_transfer_date.setDateTime(self.model.datetime)
            
            self.checkBox_return.setChecked(True if self.model.returned else False)
            if self.model.returned:
                self.dateTimeEdit_return_date.setDateTime(self.model.returned)
                
            self.plainTextEdit.setPlainText(unicode(self.model.comment)) 
            
            
            
    def accept(self):
        if self.model:
            model=self.model
        else:
            model = Object()
            model.account_id=self.account_model
        model.hardware_id=self.comboBox_hardware.itemData(self.comboBox_hardware.currentIndex()).toInt()[0]
        if not model.hardware_id:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы должны выбрать оборудование, передаваемое аккаунту."))
            return
        model.datetime = self.dateTimeEdit_transfer_date.toPyDateTime()
        if self.checkBox_return.isChecked():
            model.returned = self.dateTimeEdit_return_date.toPyDateTime()
        else:
            model.returned=None
        model.comment=unicode(self.plainTextEdit.toPlainText())
        
        try:
            self.connection.save(model, "billservice_accounthardware")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Произошла ошибка записи данных."))
            return               
        QtGui.QDialog.accept(self)
            
class HardwareDialog(QtGui.QDialog):
    def __init__(self,connection, model=None):
        super(HardwareDialog, self).__init__()
        self.setObjectName(_fromUtf8("HardwareDialog"))
        self.connection=connection
        self.model=model
        self.resize(580, 271)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_model = QtGui.QLabel(self.groupBox)
        self.label_model.setObjectName(_fromUtf8("label_model"))
        self.gridLayout.addWidget(self.label_model, 0, 0, 1, 1)
        self.comboBox_model = QtGui.QComboBox(self.groupBox)
        self.comboBox_model.setObjectName(_fromUtf8("comboBox_model"))
        self.gridLayout.addWidget(self.comboBox_model, 0, 1, 1, 1)
        self.label_name = QtGui.QLabel(self.groupBox)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout.addWidget(self.label_name, 1, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.gridLayout.addWidget(self.lineEdit_name, 1, 1, 1, 1)
        self.label_sn = QtGui.QLabel(self.groupBox)
        self.label_sn.setObjectName(_fromUtf8("label_sn"))
        self.gridLayout.addWidget(self.label_sn, 2, 0, 1, 1)
        self.lineEdit_sn = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_sn.setObjectName(_fromUtf8("lineEdit_sn"))
        self.gridLayout.addWidget(self.lineEdit_sn, 2, 1, 1, 1)
        self.label_ipaddress = QtGui.QLabel(self.groupBox)
        self.label_ipaddress.setObjectName(_fromUtf8("label_ipaddress"))
        self.gridLayout.addWidget(self.label_ipaddress, 3, 0, 1, 1)
        self.lineEdit_ipaddress = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_ipaddress.setObjectName(_fromUtf8("lineEdit_ipaddress"))
        self.gridLayout.addWidget(self.lineEdit_ipaddress, 3, 1, 1, 1)
        self.label_macaddress = QtGui.QLabel(self.groupBox)
        self.label_macaddress.setObjectName(_fromUtf8("label_macaddress"))
        self.gridLayout.addWidget(self.label_macaddress, 4, 0, 1, 1)
        self.lineEdit_macaddress = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_macaddress.setObjectName(_fromUtf8("lineEdit_macaddress"))
        self.gridLayout.addWidget(self.lineEdit_macaddress, 4, 1, 1, 1)
        self.label_comment = QtGui.QLabel(self.groupBox)
        self.label_comment.setObjectName(_fromUtf8("label_comment"))
        self.gridLayout.addWidget(self.label_comment, 5, 0, 1, 1)
        self.lineEdit_comment = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_comment.setObjectName(_fromUtf8("lineEdit_comment"))
        self.gridLayout.addWidget(self.lineEdit_comment, 5, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.comboBox_model, self.lineEdit_name)
        self.setTabOrder(self.lineEdit_name, self.lineEdit_sn)
        self.setTabOrder(self.lineEdit_sn, self.lineEdit_ipaddress)
        self.setTabOrder(self.lineEdit_ipaddress, self.lineEdit_macaddress)
        self.setTabOrder(self.lineEdit_macaddress, self.lineEdit_comment)
        self.setTabOrder(self.lineEdit_comment, self.buttonBox)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("HardwareDialog", "Параметры оборудования", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("HardwareDialog", "Параметры оборудования", None, QtGui.QApplication.UnicodeUTF8))
        self.label_model.setText(QtGui.QApplication.translate("HardwareDialog", "Производитель/модель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("HardwareDialog", "Название/назначение", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sn.setText(QtGui.QApplication.translate("HardwareDialog", "Серийный номер", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipaddress.setText(QtGui.QApplication.translate("HardwareDialog", "IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_macaddress.setText(QtGui.QApplication.translate("HardwareDialog", "MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_comment.setText(QtGui.QApplication.translate("HardwareDialog", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        items = self.connection.sql("SELECT model.id, model.name as model_name, (SELECT name FROM billservice_manufacturer WHERE id=model.manufacturer_id) as manufacturer FROM billservice_model as model ORDER BY manufacturer, model_name")
        self.connection.commit()
        self.comboBox_model.clear()
        i=0
        for item in items:
            self.comboBox_model.addItem(u"%s/%s" % (item.manufacturer, item.model_name), QtCore.QVariant(item.id))
            if self.model:
                if self.model.model_id==item.id:
                    self.comboBox_model.setCurrentIndex(i)
            i+=1    
    
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            self.lineEdit_comment.setText(unicode(self.model.comment))
            self.lineEdit_sn.setText(unicode(self.model.sn))
            self.lineEdit_ipaddress.setText(unicode(self.model.ipaddress))
            self.lineEdit_macaddress.setText(unicode(self.model.macaddress))
            
    def accept(self):
        if self.model:
            model=self.model
        else:
            model=Object()
            
        model.model_id=self.comboBox_model.itemData(self.comboBox_model.currentIndex()).toInt()[0]
        model.name=unicode(self.lineEdit_name.text())
        model.sn=unicode(self.lineEdit_sn.text())
        model.ipaddress=unicode(self.lineEdit_ipaddress.text())
        model.macaddress=unicode(self.lineEdit_macaddress.text())
        model.comment=unicode(self.lineEdit_comment.text())
        
        try:
            self.connection.save(model, "billservice_hardware")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()        
        QtGui.QDialog.accept(self)
    

class ModelEditDialog(QtGui.QDialog):
    def __init__(self,connection, model=None):
        super(ModelEditDialog, self).__init__()
        self.model=model
        self.connection=connection
        self.setObjectName(_fromUtf8("ModelDialog"))
        self.resize(469, 163)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_manufacturer = QtGui.QLabel(self.groupBox)
        self.label_manufacturer.setObjectName(_fromUtf8("label_manufacturer"))
        self.gridLayout_2.addWidget(self.label_manufacturer, 0, 0, 1, 1)
        self.comboBox_manufacturer = QtGui.QComboBox(self.groupBox)
        self.comboBox_manufacturer.setObjectName(_fromUtf8("comboBox_manufacturer"))
        self.gridLayout_2.addWidget(self.comboBox_manufacturer, 0, 1, 1, 1)
        self.label_name = QtGui.QLabel(self.groupBox)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout_2.addWidget(self.label_name, 2, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.gridLayout_2.addWidget(self.lineEdit_name, 2, 1, 1, 1)
        self.label_hardwaretype = QtGui.QLabel(self.groupBox)
        self.label_hardwaretype.setObjectName(_fromUtf8("label_hardwaretype"))
        self.gridLayout_2.addWidget(self.label_hardwaretype, 1, 0, 1, 1)
        self.comboBox_hardwaretype = QtGui.QComboBox(self.groupBox)
        self.comboBox_hardwaretype.setObjectName(_fromUtf8("comboBox_hardwaretype"))
        self.gridLayout_2.addWidget(self.comboBox_hardwaretype, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("ModelDialog", "Параметры модели", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ModelDialog", "Параметры модели", None, QtGui.QApplication.UnicodeUTF8))
        self.label_manufacturer.setText(QtGui.QApplication.translate("ModelDialog", "Производитель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("ModelDialog", "Модель", None, QtGui.QApplication.UnicodeUTF8))
        self.label_hardwaretype.setText(QtGui.QApplication.translate("ModelDialog", "Тип оборудования", None, QtGui.QApplication.UnicodeUTF8))



    def fixtures(self):
        items = self.connection.get_models("billservice_manufacturer", order={'name':'ASC'})
        self.connection.commit()
        self.comboBox_manufacturer.clear()
        i=0
        for item in items:
            self.comboBox_manufacturer.addItem(item.name, QtCore.QVariant(item.id))
            if self.model:
                if self.model.manufacturer_id==item.id:
                    self.comboBox_manufacturer.setCurrentIndex(i)
            i+=1        

        items = self.connection.get_models("billservice_hardwaretype", order={'name':'ASC'})
        self.connection.commit()
        self.comboBox_hardwaretype.clear()
        i=0
        for item in items:
            self.comboBox_hardwaretype.addItem(item.name, QtCore.QVariant(item.id))
            if self.model:
                if self.model.hardwaretype_id==item.id:
                    self.comboBox_hardwaretype.setCurrentIndex(i)
            i+=1      
            
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            
    def accept(self):
        if self.model:
            model=self.model
        else:
            model=Object()
        
        model.manufacturer_id=self.comboBox_manufacturer.itemData(self.comboBox_manufacturer.currentIndex()).toInt()[0]
        model.hardwaretype_id=self.comboBox_hardwaretype.itemData(self.comboBox_hardwaretype.currentIndex()).toInt()[0]
        model.name = unicode(self.lineEdit_name.text())
        try:
            self.connection.save(model, "billservice_model")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        QtGui.QDialog.accept(self)

class HardwareManufacturerEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'Производитель', ]
        initargs = {"setname":"HardwareManufacturerEbs_window", "objname":"HardwareManufacturerEbs", "winsize":(0,0,827,476), "wintitle":"Производители оборудования", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(HardwareManufacturerEbs, self).__init__(connection, initargs)
        
        
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

        actList=[("addAction", "Добавить", "images/add.png", self.add_window), ("editAction", "Редактировать", "images/open.png", self.edit_window), ("delAction", "Удалить", "images/del.png", self.del_window)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(HardwareManufacturerEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_window(self):
        text=QtGui.QInputDialog.getText(self, u'Введите название производителя', u'Название', text="")
        #child.exec_()
        if text[1] and not text[0].isEmpty():
            model = Object()
            model.name=unicode(text[0])
            self.connection.save(model, "billservice_manufacturer") 
            self.connection.commit()
            self.refresh()
            

    def del_window(self):

        id=self.getSelectedId()
        if id>0:
            if self.connection.get_models("billservice_hardware", where={"manufacturer_id":id}, fields=['id']):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Этот производитель назначен оборудованию. Удаление невозможно!")
                self.connection.commit()
                return
            elif QtGui.QMessageBox.question(self, u"Удалить производителя?" , u"Действие необратимо.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_manufacturer")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_window(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "billservice_manufacturer")
            text=QtGui.QInputDialog.getText(self, u'Введите название производителя', u'Название', text=unicode(model.name))
            #child.exec_()
            if text[1] and not text[0].isEmpty():
                model.name=unicode(text[0])
                self.connection.save(model, "billservice_manufacturer") 
                self.connection.commit()
                self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/modem.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        items = self.connection.get_models("billservice_manufacturer", order={'name':'ASC'})
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.name, i,1)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(HardwareManufacturerEbs, self).delNodeLocalAction([self.delAction])

class HardwareTypeEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'Тип оборудования', ]
        initargs = {"setname":"HardwareTypeEbs_window", "objname":"HardwareTypeEbs", "winsize":(0,0,827,476), "wintitle":"Типы оборудования", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(HardwareTypeEbs, self).__init__(connection, initargs)
        
        
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

        actList=[("addAction", "Добавить", "images/add.png", self.add_window), ("editAction", "Редактировать", "images/open.png", self.edit_window), ("delAction", "Удалить", "images/del.png", self.del_window)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(HardwareTypeEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_window(self):
        text=QtGui.QInputDialog.getText(self, u'Введите тип оборудования', u'Название', text="")
        #child.exec_()
        if text[1] and not text[0].isEmpty():
            model = Object()
            model.name=unicode(text[0])
            self.connection.save(model, "billservice_hardwaretype") 
            self.refresh()
            

    def del_window(self):

        id=self.getSelectedId()
        if id>0:
            if self.connection.get_models("billservice_model", where={"hardwaretype_id":id}, fields=['id']):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Этот тип назначен оборудованию. Удаление невозможно!")
                self.connection.commit()
                return
            elif QtGui.QMessageBox.question(self, u"Удалить тип?" , u"Действие необратимо.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_hardwaretype")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_window(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "billservice_hardwaretype")
            text=QtGui.QInputDialog.getText(self, u'Введите тип оборудования', u'Название', text=unicode(model.name))
            #child.exec_()
            if text[1] and not text[0].isEmpty():
                model.name=unicode(text[0])
                self.connection.save(model, "billservice_hardwaretype") 
                self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/modem.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        items = self.connection.get_models("billservice_hardwaretype", order={'name':'ASC'})
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.name, i,1)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(HardwareTypeEbs, self).delNodeLocalAction([self.delAction])
        
class ModelWindowEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'Производитель', u'Тип оборудования', u'Модель', ]
        initargs = {"setname":"ModelWindowEbs_window", "objname":"ModelWindowEbs", "winsize":(0,0,827,476), "wintitle":"Модели оборудования", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(ModelWindowEbs, self).__init__(connection, initargs)
        
        
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

        actList=[("addAction", "Добавить", "images/add.png", self.add_window), ("editAction", "Редактировать", "images/open.png", self.edit_window), ("delAction", "Удалить", "images/del.png", self.del_window)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(ModelWindowEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_window(self):

        child=ModelEditDialog(connection=self.connection)
        if child.exec_()==1:
            self.refresh()
            

    def del_window(self):

        id=self.getSelectedId()
        if id>0:
            if self.connection.get_models("billservice_hardware", where={"model_id":id}, fields=['id']):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Эта модель назначена оборудованию. Удаление невозможно!")
                self.connection.commit()
                return
            elif QtGui.QMessageBox.question(self, u"Удалить модель?" , u"Действие необратимо.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_model")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_window(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "billservice_model")
            child=ModelEditDialog(connection=self.connection, model=model)
            if child.exec_()==1:
                self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/modem.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        items = self.connection.sql("""SELECT model.id, model.name,(SELECT name FROM billservice_manufacturer WHERE id=model.manufacturer_id) as manufacturer,(SELECT name FROM billservice_hardwaretype WHERE id=model.hardwaretype_id) as hardwaretype FROM billservice_model as model ORDER BY name""")
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.manufacturer, i,1)
            self.addrow(item.hardwaretype, i,2)
            self.addrow(item.name, i,3)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(ModelWindowEbs, self).delNodeLocalAction([self.delAction])


class HardwareWindowEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['#', u'Производитель', u'Тип оборудования', u'Модель', u'Название', u's/n','uIP',  u'MAC', u'Комментарий']
        initargs = {"setname":"HardwareWindowEbs_window_", "objname":"HardwareWindowEbs_", "winsize":(0,0,827,476), "wintitle":"Подотчётное оборудование", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(HardwareWindowEbs, self).__init__(connection, initargs)
        
        
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

        actList=[("addAction", "Добавить", "images/add.png", self.add_window), ("editAction", "Редактировать", "images/open.png", self.edit_window), ("delAction", "Удалить", "images/del.png", self.del_window)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(HardwareWindowEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_window(self):

        child=HardwareDialog(connection=self.connection)
        if child.exec_()==1:
            self.refresh()
            

    def del_window(self):

        id=self.getSelectedId()
        if id>0:
            if self.connection.get_models("billservice_accounthardware", where={"hardware_id":id}, fields=['id']):
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Это оборудование было выдано абонентам. Удаление невозможно!")
                self.connection.commit()
                return
            elif QtGui.QMessageBox.question(self, u"Удалить оборудование?" , u"Действие необратимо.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                    self.connection.iddelete(id, "billservice_hardware")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_window(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "billservice_hardware")
            child=HardwareDialog(connection=self.connection, model=model)
            if child.exec_()==1:
                self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/modem.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        ['#', u'Производитель', u'Тип оборудования', u'Модель', u'Название/Назначение',u'IP', u'MAC', u'Комментарий']
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setSortingEnabled(False)
        items = self.connection.sql("""
        SELECT hw.id, hw.name,hw.comment as comment, hw.ipaddress,hw.macaddress, hw.sn, model.name as model_name, hwtype.name as hardwaretype, m.name as manufacturer
        FROM billservice_hardware as hw
        JOIN billservice_model as model ON model.id=hw.model_id
        JOIN billservice_hardwaretype as hwtype ON hwtype.id=model.hardwaretype_id
        JOIN billservice_manufacturer as m ON m.id=model.manufacturer_id 
        ORDER BY hw.name""")
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.manufacturer, i,1)
            self.addrow(item.hardwaretype, i,2)
            self.addrow(item.model_name, i,3)
            self.addrow(item.name, i,4)
            self.addrow(item.sn, i,5)
            self.addrow(item.ipaddress, i,6)
            self.addrow(item.macaddress, i,7)
            self.addrow(item.comment, i,8)
            i+=1
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(HardwareWindowEbs, self).delNodeLocalAction([self.delAction])
        