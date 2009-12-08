#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

#restrict by ip adresses

from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil
from helpers import dateDelim
from ebsWindow import ebsTableWindow



class GroupSelectDialog(QtGui.QDialog):
    def __init__(self, selected_ids, connection):
        super(GroupSelectDialog, self).__init__()
        self.selected_ids = selected_ids
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
        self.commandLinkButton = QtGui.QCommandLinkButton(self)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.gridLayout_2.addWidget(self.commandLinkButton, 1, 0, 1, 1)
        self.commandLinkButton_2 = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.gridLayout_2.addWidget(self.commandLinkButton_2, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Список пользователей в группе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Группы", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("Dialog", "Добавить новую группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setDescription(QtGui.QApplication.translate("Dialog", "Удалить группу", None, QtGui.QApplication.UnicodeUTF8))
        
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
            if self.passValidator.validate(self.password_lineEdit.text(), 0)[0]  != QtGui.QValidator.Acceptable:
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
       
        self.resize(379, 194)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.username_label = QtGui.QLabel(self.groupBox)
        self.username_label.setObjectName("username_label")
        self.gridLayout_2.addWidget(self.username_label, 0, 0, 1, 1)
        self.username_edit = QtGui.QLineEdit(self.groupBox)
        self.username_edit.setMinimumSize(QtCore.QSize(0, 21))
        self.username_edit.setObjectName("username_edit")
        self.gridLayout_2.addWidget(self.username_edit, 0, 1, 1, 2)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.hosts_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.hosts_lineEdit.setMinimumSize(QtCore.QSize(0, 21))
        self.hosts_lineEdit.setObjectName("hosts_lineEdit")
        self.gridLayout_2.addWidget(self.hosts_lineEdit, 1, 1, 1, 2)
        self.comment_label = QtGui.QLabel(self.groupBox)
        self.comment_label.setObjectName("comment_label")
        self.gridLayout_2.addWidget(self.comment_label, 2, 0, 1, 1)
        self.comment_edit = QtGui.QLineEdit(self.groupBox)
        self.comment_edit.setMinimumSize(QtCore.QSize(0, 21))
        self.comment_edit.setObjectName("comment_edit")
        self.gridLayout_2.addWidget(self.comment_edit, 2, 1, 1, 2)
        self.label_role = QtGui.QLabel(self.groupBox)
        self.label_role.setObjectName("label_role")
        self.gridLayout_2.addWidget(self.label_role, 3, 0, 1, 1)
        self.comboBox_role = QtGui.QComboBox(self.groupBox)
        self.comboBox_role.setMinimumSize(QtCore.QSize(0, 21))
        self.comboBox_role.setObjectName("comboBox_role")

        self.gridLayout_2.addWidget(self.comboBox_role, 3, 1, 1, 1)
        self.status_checkBox = QtGui.QCheckBox(self.groupBox)
        self.status_checkBox.setObjectName("status_checkBox")
        self.gridLayout_2.addWidget(self.status_checkBox, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.password_pushButton = QtGui.QPushButton(self)
        self.password_pushButton.setFlat(False)
        self.password_pushButton.setObjectName("password_pushButton")
        self.gridLayout.addWidget(self.password_pushButton, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        
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
        self.username_label.setText(QtGui.QApplication.translate("Dialog", "Логин:", None, QtGui.QApplication.UnicodeUTF8))
        self.comment_label.setText(QtGui.QApplication.translate("Dialog", "Комментарий:", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox.setText(QtGui.QApplication.translate("Dialog", "Разрешён вход", None, QtGui.QApplication.UnicodeUTF8))
        self.password_pushButton.setText(QtGui.QApplication.translate("Dialog", "Новый пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Разрешённые IP:", None, QtGui.QApplication.UnicodeUTF8))     
        self.label_role.setText(QtGui.QApplication.translate("Dialog", "Роль", None, QtGui.QApplication.UnicodeUTF8))   
        self.hosts_lineEdit.setValidator(self.ipValidator)
        
    def setPassword(self):
        child = PasswordEditFrame()
        
        if child.exec_()==1:
            if child.password:
                self.password = unicode(child.password.toHex())
                self.text_password = child.text_password
                
    def check_ips(self, ipsstr):
        ips = ipsstr.split(', ')

        added = []
        for ipstr in ips:
            ipstr_ok = True
            for ip in ipstr.split('-'):                
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
            
        if self.username_edit.text():
            model.host = unicode(self.check_ips(str(self.hosts_lineEdit.text())))
            model.username = unicode(self.username_edit.text())
            model.description = unicode(self.comment_edit.text())
            model.status = self.status_checkBox.checkState()==2
            model.role = self.comboBox_role.currentIndex()
            
            try:
                self.connection.save(model, "billservice_systemuser")
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
    
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
        else:
            self.hosts_lineEdit.setText(u'0.0.0.0/0')





class SystemEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u"id", u"Имя", u"Статус", u"Создан", u'Последний вход', u'Последний IP', u'Разрешённые адреса']
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
        #self.tableWidget.setSortingEnabled(False)
        users = self.connection.get_models("billservice_systemuser")
        self.connection.commit()
        self.tableWidget.setRowCount(len(users))
        i=0
        for user in users:
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
            self.tableWidget.setRowHeight(i, 14)
            i+=1            
            
        self.tableWidget.setColumnHidden(0, True)
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        
        #self.tableWidget.setSortingEnabled(True)
    
        
