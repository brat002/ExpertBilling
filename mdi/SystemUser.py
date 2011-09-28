#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

#restrict by ip adresses

from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil
from helpers import dateDelim
from ebsWindow import ebsTableWindow
from CustomForms import CustomWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class GroupSelectDialog(QtGui.QDialog):
    def __init__(self, systemuser_model=None, connection=None):
        super(GroupSelectDialog, self).__init__()
        
        self.systemuser_model = systemuser_model
        self.connection = connection
        self.setObjectName("GroupSelectDialog")
        self.resize(424, 335)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(self.groupBox)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.commandLinkButton_add = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_add.setObjectName("commandLinkButton_add")
        self.gridLayout_2.addWidget(self.commandLinkButton_add, 1, 0, 1, 1)
        self.commandLinkButton_del = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_del.setObjectName("commandLinkButton_del")
        self.gridLayout_2.addWidget(self.commandLinkButton_del, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.commandLinkButton_add, QtCore.SIGNAL("clicked()"), self.add)
        QtCore.QObject.connect(self.commandLinkButton_del, QtCore.SIGNAL("clicked()"), self.delete)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Список пользователей в группе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Группы", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setDescription(QtGui.QApplication.translate("Dialog", "Добавить новую группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setDescription(QtGui.QApplication.translate("Dialog", "Удалить группу", None, QtGui.QApplication.UnicodeUTF8))
        

    def add(self):
        text = QtGui.QInputDialog.getText(self,u"Введите название название", u"Название:", QtGui.QLineEdit.Normal, "")        
        if text[0].isEmpty()==True and text[1]:
            QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return
        model = Object()
        model.name = unicode(text[0])
        self.connection.save(model, "billservice_systemgroup")
        self.connection.commit()
        self.fixtures()
        
    def delete(self):
        
        item = self.listWidget.currentItem()
        
        if not item: return
        
        id = item.id
        self.connection.iddelete(id, "billservice_systemgroup")
        self.connection.commit()
        self.fixtures()


    def fixtures(self):
        self.listWidget.clear()
        self.connection.commit()
        groups = self.connection.get_models("billservice_systemgroup")
        self.connection.commit()
        
        self.selected_ids = self.connection.sql("SELECT id, systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s" % self.systemuser_model.id)
        self.connection.commit()
        self.selected_nodes = [x.id for x in self.selected_ids]
        self.selected_groups = [x.systemgroup_id for x in self.selected_ids]
        for group in groups:
            
            item = QtGui.QListWidgetItem(self.listWidget)
            item.setText(unicode(group.name))
            item.id = group.id
            if item.id in self.selected_groups:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.listWidget.addItem(item)

    def accept(self):
        selected_items = []
        
        for i in xrange(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState()==QtCore.Qt.Checked and item.id not in self.selected_groups:
                model = Object()
                model.systemuser_id = self.systemuser_model.id
                model.systemgroup_id = item.id
                self.connection.save(model, "billservice_systemuser_group")
                self.connection.commit()
            
            
            if item.checkState()==QtCore.Qt.Unchecked and item.id  in self.selected_groups:
                self.connection.command("DELETE FROM billservice_systemuser_group WHERE systemuser_id=%s and systemgroup_id=%s" % (self.systemuser_model.id, item.id,))
                self.connection.commit() 
        
        QtGui.QDialog.accept(self)
        
roles = [u"Администратор", u"Кассир", u"Веб-кабинет"]
class PasswordEditFrame(QtGui.QDialog):
    def __init__(self):
        super(PasswordEditFrame, self).__init__()
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,284,73).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(200,10,77,56))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.password_label = QtGui.QLabel(self)
        self.password_label.setGeometry(QtCore.QRect(10,10,46,21))
        self.password_label.setObjectName("password_label")

        self.repeat_password_label = QtGui.QLabel(self)
        self.repeat_password_label.setGeometry(QtCore.QRect(10,40,59,21))
        self.repeat_password_label.setObjectName("repeat_password_label")

        self.password_lineEdit = QtGui.QLineEdit(self)
        self.password_lineEdit.setGeometry(QtCore.QRect(80,10,113,20))
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName("password_lineEdit")

        self.repeat_password_lineEdit = QtGui.QLineEdit(self)
        self.repeat_password_lineEdit.setGeometry(QtCore.QRect(80,40,113,20))
        self.repeat_password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.repeat_password_lineEdit.setObjectName("repeat_password_lineEdit")
        self.password = ''
        self.passRx = QtCore.QRegExp(r"^\w{3,}")
        self.passValidator = QtGui.QRegExpValidator(self.passRx, self)
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Изменить пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("Dialog", "Пароль:", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_password_label.setText(QtGui.QApplication.translate("Dialog", "Повторите:", None, QtGui.QApplication.UnicodeUTF8))
        self.password_lineEdit.setValidator(self.passValidator)
        
    def accept(self):
        if self.password_lineEdit.text():
            if self.passValidator.validate(QtCore.QString(self.password_lineEdit.text()), 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пароль должен быть не менее 3-х символов."))
                return
            if self.password_lineEdit.text() == self.repeat_password_lineEdit.text():
                self.password = QtCore.QCryptographicHash.hash(self.password_lineEdit.text().toUtf8(), QtCore.QCryptographicHash.Md5)
                self.text_password = unicode(self.password_lineEdit.text())
                QtGui.QDialog.accept(self)
            else:
                QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введенные пароли не совпадают"))
                return
        else:
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите пароль"))
            return
            
      
class SystemUserFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(SystemUserFrame, self).__init__()
        self.setObjectName("SystemUserMDI")
        self.connection = connection
        self.connection.commit()
        self.model = model
        self.password = ''
       
        self.resize(514, 561)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.username_label = QtGui.QLabel(self.groupBox)
        self.username_label.setObjectName(_fromUtf8("username_label"))
        self.gridLayout.addWidget(self.username_label, 0, 0, 1, 1)
        self.username_edit = QtGui.QLineEdit(self.groupBox)
        self.username_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.username_edit.setObjectName(_fromUtf8("username_edit"))
        self.gridLayout.addWidget(self.username_edit, 0, 1, 1, 1)
        self.label_fullname = QtGui.QLabel(self.groupBox)
        self.label_fullname.setObjectName(_fromUtf8("label_fullname"))
        self.gridLayout.addWidget(self.label_fullname, 2, 0, 1, 1)
        self.lineEdit_fullname = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_fullname.setObjectName(_fromUtf8("lineEdit_fullname"))
        self.gridLayout.addWidget(self.lineEdit_fullname, 2, 1, 1, 1)
        self.label_address = QtGui.QLabel(self.groupBox)
        self.label_address.setObjectName(_fromUtf8("label_address"))
        self.gridLayout.addWidget(self.label_address, 3, 0, 1, 1)
        self.lineEdit_address = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_address.setObjectName(_fromUtf8("lineEdit_address"))
        self.gridLayout.addWidget(self.lineEdit_address, 3, 1, 1, 1)
        self.label_home_phone = QtGui.QLabel(self.groupBox)
        self.label_home_phone.setObjectName(_fromUtf8("label_home_phone"))
        self.gridLayout.addWidget(self.label_home_phone, 4, 0, 1, 1)
        self.lineEdit_home_phone = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_home_phone.setObjectName(_fromUtf8("lineEdit_home_phone"))
        self.gridLayout.addWidget(self.lineEdit_home_phone, 4, 1, 1, 1)
        self.label_mobile_phone = QtGui.QLabel(self.groupBox)
        self.label_mobile_phone.setObjectName(_fromUtf8("label_mobile_phone"))
        self.gridLayout.addWidget(self.label_mobile_phone, 5, 0, 1, 1)
        self.lineEdit_mobile_phone = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_mobile_phone.setObjectName(_fromUtf8("lineEdit_mobile_phone"))
        self.gridLayout.addWidget(self.lineEdit_mobile_phone, 5, 1, 1, 1)
        self.label_passport = QtGui.QLabel(self.groupBox)
        self.label_passport.setObjectName(_fromUtf8("label_passport"))
        self.gridLayout.addWidget(self.label_passport, 6, 0, 1, 1)
        self.lineEdit_passport = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_passport.setObjectName(_fromUtf8("lineEdit_passport"))
        self.gridLayout.addWidget(self.lineEdit_passport, 6, 1, 1, 1)
        self.label_passport_number = QtGui.QLabel(self.groupBox)
        self.label_passport_number.setObjectName(_fromUtf8("label_passport_number"))
        self.gridLayout.addWidget(self.label_passport_number, 9, 0, 1, 1)
        self.lineEdit_passport_number = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_passport_number.setObjectName(_fromUtf8("lineEdit_passport_number"))
        self.gridLayout.addWidget(self.lineEdit_passport_number, 9, 1, 1, 1)
        self.label_unp = QtGui.QLabel(self.groupBox)
        self.label_unp.setObjectName(_fromUtf8("label_unp"))
        self.gridLayout.addWidget(self.label_unp, 11, 0, 1, 1)
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_unp.setObjectName(_fromUtf8("lineEdit_unp"))
        self.gridLayout.addWidget(self.lineEdit_unp, 11, 1, 1, 1)
        self.label_job = QtGui.QLabel(self.groupBox)
        self.label_job.setObjectName(_fromUtf8("label_job"))
        self.gridLayout.addWidget(self.label_job, 1, 0, 1, 1)
        self.lineEdit_job = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_job.setObjectName(_fromUtf8("lineEdit_job"))
        self.gridLayout.addWidget(self.lineEdit_job, 1, 1, 1, 1)
        self.label_passport_detail = QtGui.QLabel(self.groupBox)
        self.label_passport_detail.setObjectName(_fromUtf8("label_passport_detail"))
        self.gridLayout.addWidget(self.label_passport_detail, 8, 0, 1, 1)
        self.lineEdit_passport_detail = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_passport_detail.setObjectName(_fromUtf8("lineEdit_passport_detail"))
        self.gridLayout.addWidget(self.lineEdit_passport_detail, 8, 1, 1, 1)
        self.label_email = QtGui.QLabel(self.groupBox)
        self.label_email.setObjectName(_fromUtf8("label_email"))
        self.gridLayout.addWidget(self.label_email, 12, 0, 1, 1)
        self.lineEdit_email = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_email.setObjectName(_fromUtf8("lineEdit_email"))
        self.gridLayout.addWidget(self.lineEdit_email, 12, 1, 1, 1)
        self.label_im = QtGui.QLabel(self.groupBox)
        self.label_im.setObjectName(_fromUtf8("label_im"))
        self.gridLayout.addWidget(self.label_im, 13, 0, 1, 1)
        self.lineEdit_im = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_im.setObjectName(_fromUtf8("lineEdit_im"))
        self.gridLayout.addWidget(self.lineEdit_im, 13, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 3)
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.hosts_lineEdit = QtGui.QLineEdit(self)
        self.hosts_lineEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.hosts_lineEdit.setObjectName(_fromUtf8("hosts_lineEdit"))
        self.gridLayout_2.addWidget(self.hosts_lineEdit, 1, 1, 1, 2)
        self.comment_label = QtGui.QLabel(self)
        self.comment_label.setObjectName(_fromUtf8("comment_label"))
        self.gridLayout_2.addWidget(self.comment_label, 2, 0, 1, 1)
        self.comment_edit = QtGui.QLineEdit(self)
        self.comment_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.comment_edit.setObjectName(_fromUtf8("comment_edit"))
        self.gridLayout_2.addWidget(self.comment_edit, 2, 1, 1, 2)
        self.label_role = QtGui.QLabel(self)
        self.label_role.setObjectName(_fromUtf8("label_role"))
        self.gridLayout_2.addWidget(self.label_role, 3, 0, 1, 1)
        self.comboBox_role = QtGui.QComboBox(self)
        self.comboBox_role.setMinimumSize(QtCore.QSize(0, 0))
        self.comboBox_role.setObjectName(_fromUtf8("comboBox_role"))
        self.gridLayout_2.addWidget(self.comboBox_role, 3, 1, 1, 1)
        self.status_checkBox = QtGui.QCheckBox(self)
        self.status_checkBox.setObjectName(_fromUtf8("status_checkBox"))
        self.gridLayout_2.addWidget(self.status_checkBox, 3, 2, 1, 1)
        self.password_pushButton = QtGui.QPushButton(self)
        self.password_pushButton.setFlat(False)
        self.password_pushButton.setObjectName(_fromUtf8("password_pushButton"))
        self.gridLayout_2.addWidget(self.password_pushButton, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 4, 1, 1, 1)

        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/[0-9][0-9]?)?\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)

        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)
        QtCore.QObject.connect(self.password_pushButton, QtCore.SIGNAL("clicked()"),self.setPassword)
        #QtCore.QObject.connect(self.hosts_pushButton, QtCore.SIGNAL("clicked()"), self.setHosts)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.username_label.setText(QtGui.QApplication.translate("Dialog", "Логин:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fullname.setText(QtGui.QApplication.translate("Dialog", "ФИО:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_address.setText(QtGui.QApplication.translate("Dialog", "Домашний адрес:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_home_phone.setText(QtGui.QApplication.translate("Dialog", "Домашний телефон:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_mobile_phone.setText(QtGui.QApplication.translate("Dialog", "Сотовый телефон:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport.setText(QtGui.QApplication.translate("Dialog", "Паспорт(серия, номер):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport_number.setText(QtGui.QApplication.translate("Dialog", "Личный номер:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("Dialog", "УНП:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_job.setText(QtGui.QApplication.translate("Dialog", "Должность:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_passport_detail.setText(QtGui.QApplication.translate("Dialog", "Где и когда выдан:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_email.setText(QtGui.QApplication.translate("Dialog", "e-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_im.setText(QtGui.QApplication.translate("Dialog", "ICQ/MSN/Skype", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Разрешённые IP:", None, QtGui.QApplication.UnicodeUTF8))
        self.comment_label.setText(QtGui.QApplication.translate("Dialog", "Комментарий:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_role.setText(QtGui.QApplication.translate("Dialog", "Роль", None, QtGui.QApplication.UnicodeUTF8))
        #self.comboBox_role.setItemText(0, QtGui.QApplication.translate("Dialog", "Администратор", None, QtGui.QApplication.UnicodeUTF8))
        #self.comboBox_role.setItemText(1, QtGui.QApplication.translate("Dialog", "Кассир", None, QtGui.QApplication.UnicodeUTF8))
        #self.comboBox_role.setItemText(2, QtGui.QApplication.translate("Dialog", "Веб-кабинет", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox.setText(QtGui.QApplication.translate("Dialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.password_pushButton.setText(QtGui.QApplication.translate("Dialog", "Новый пароль", None, QtGui.QApplication.UnicodeUTF8))
   
        
        self.hosts_lineEdit.setValidator(self.ipValidator)
        
    def setPassword(self):
        child = PasswordEditFrame()
        
        if child.exec_()==1:
            if child.password:
                self.password = unicode(child.password.toHex())
                self.text_password = child.text_password
                
    def check_ips(self, ipsstr):
        ips = ipsstr.split(',')

        added = []
        for ipstr in ips:
            ipstr_ok = True
            ipstr = ipstr.strip()
            for ip in ipstr.split('-'):    
                ip = QtCore.QString(ip)            
                ipstr_ok = ipstr_ok and (self.ipValidator.validate(ip, 0)[0]  == QtGui.QValidator.Acceptable)
            if ipstr_ok and (ipstr not in added):
                added.append(ipstr)
        return ', '.join(added)
        
    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))
        if self.model:
            model=self.model
            if self.password!='':
                model.password=self.password
                model.text_password = self.text_password
        else:
            #print 'New nas'
            model=Object()
            model.password=self.password
            model.text_password = self.text_password
            
        if not model.text_password:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пароль пользователя должен быть указан %s" % repr(e)))
            return
        if self.username_edit.text():
            model.host = unicode(self.check_ips(str(self.hosts_lineEdit.text()))) or "0.0.0.0/0"
            model.username = unicode(self.username_edit.text())
            model.description = unicode(self.comment_edit.text()) or ""
            model.status = self.status_checkBox.checkState()==2
            model.role = self.comboBox_role.currentIndex()

            model.email=unicode(self.lineEdit_email.text())
            model.job=unicode(self.lineEdit_job.text())
            model.fullname=unicode(self.lineEdit_fullname.text())
            model.address=unicode(self.lineEdit_address.text())
            model.home_phone=unicode(self.lineEdit_home_phone.text())
            model.mobile_phone=unicode(self.lineEdit_mobile_phone.text())
            model.passport=unicode(self.lineEdit_passport.text())
            model.passport_details=unicode(self.lineEdit_passport_detail.text())
            model.passport_number=unicode(self.lineEdit_passport_number.text())
            model.unp=unicode(self.lineEdit_unp.text())
            model.im = unicode(self.lineEdit_im.text())
                        
            try:
                self.connection.save(model, "billservice_systemuser")
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"При сохранении данных возникла ошибка %s" % repr(e)))
                return
    
            QtGui.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите необходимые данные"))
            return

    def fixtures(self):
        
        i=0
        for role in roles:
            self.comboBox_role.addItem(role)
            self.comboBox_role.setItemData(i, QtCore.QVariant(i))
            i+=1
            
        #print "current index", self.model.role
        if self.model:
            self.username_edit.setText(unicode(self.model.username))
            self.comment_edit.setText(unicode(self.model.description))
            self.status_checkBox.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.hosts_lineEdit.setText(unicode(self.model.host))
            self.comboBox_role.setCurrentIndex(int(self.model.role))
            self.lineEdit_email.setText(unicode(self.model.email))
            self.lineEdit_job.setText(unicode(self.model.job))
            self.lineEdit_fullname.setText(unicode(self.model.fullname))
            self.lineEdit_address.setText(unicode(self.model.address))
            self.lineEdit_home_phone.setText(unicode(self.model.home_phone))
            self.lineEdit_mobile_phone.setText(unicode(self.model.mobile_phone))
            self.lineEdit_passport.setText(unicode(self.model.passport))
            self.lineEdit_passport_detail.setText(unicode(self.model.passport_details))
            self.lineEdit_passport_number.setText(unicode(self.model.passport_number))
            self.lineEdit_unp.setText(unicode(self.model.unp))
            self.lineEdit_im.setText(unicode(self.model.im))
        else:
            self.hosts_lineEdit.setText(u'0.0.0.0/0')





class SystemEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u"id", u"Имя", u"Статус", u"Создан", u'Последний вход', u'Последний IP', u'Разрешённые адреса', u"Группы безопасности"]
        initargs = {"setname":"users_frame_header", "objname":"SystemEbsMDI", "winsize":(0,0,634,365), "wintitle":"Системные пользователи", "tablecolumns":columns, "tablesize":(0,0,631,311)}
        super(SystemEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setDockNestingEnabled(False)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks|QtGui.QMainWindow.AnimatedDocks)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def ebsPostInit(self, initargs):
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        actList=[("addAction", "Добавить", "images/add.png", self.addframe), ("editAction", "Настройки", "images/open.png", self.editframe), ("delAction", "Удалить", "images/del.png", self.delete)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)

        
    def retranslateUI(self, initargs):
        super(SystemEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Системные пользователи", None, QtGui.QApplication.UnicodeUTF8))
    
    def addframe(self):
        addf = SystemUserFrame(connection=self.connection)
        #addf.show()
        if addf.exec_()==1:
            self.refresh()
            
    def delete(self):
        id = self.getSelectedId()
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить пользователя?" , u"Вы уверены, что хотите удалить пользователя?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_systemuser WHERE id=%d" % self.getSelectedId())
                self.connection.iddelete(id, "billservice_systemuser")
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
        self.refresh()


    def editframe(self):
        


            
        try:
            model=self.connection.get_model(self.getSelectedId(), "billservice_systemuser")
        except:
            return

        if self.tableWidget.currentColumn()==7:
            child = GroupSelectDialog(systemuser_model=model, connection = self.connection)
            if child.exec_()==1:
                self.refresh()
            return            

        addf = SystemUserFrame(connection=self.connection, model=model)
        
        if addf.exec_()==1:
            self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if value == None:
            value = ''
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/system_administrators.png"))
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)

        
    def refresh(self):
        self.statusBar().showMessage(u"Идёт получение данных")
        #self.tableWidget.setSortingEnabled(False)
        users = self.connection.get_models("billservice_systemuser")
        self.connection.commit()
        self.tableWidget.setRowCount(len(users))
        i=0
        for user in users:
            groups = self.connection.sql("SELECT (SELECT name FROM billservice_systemgroup WHERE id=sg.systemgroup_id) as name FROM billservice_systemuser_group as sg WHERE systemuser_id=%s" % user.id)
            self.addrow(user.id, i,0)
            self.addrow(user.username, i,1)
            self.addrow(user.status, i,2)
            self.addrow(user.created, i,3)
            try:
                self.addrow(user.last_login.strftime(self.strftimeFormat), i,4)
            except:
                pass
            self.addrow(user.last_ip, i,5)
            self.addrow(user.host, i,6)
            if groups:
                self.tableWidget.setItem(i,7, CustomWidget(parent=self.tableWidget, models=groups))
            else:
                self.addrow(u"Группы не назначены", i,7)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1            
            
        self.tableWidget.setColumnHidden(0, True)
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.resizeRowsToContents()
        self.statusBar().showMessage(u"Готово")
        #self.tableWidget.setSortingEnabled(True)
    
        
