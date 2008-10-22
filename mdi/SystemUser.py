#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

#restrict by ip adresses

from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil
from helpers import dateDelim


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
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пароль должен быть длиной как минимум 3 и не содержать спецефических символов."))
                return
            if self.password_lineEdit.text() == self.repeat_password_lineEdit.text():
                self.password = QtCore.QCryptographicHash.hash(self.password_lineEdit.text().toUtf8(), QtCore.QCryptographicHash.Md5)
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
       
        self.resize(QtCore.QSize(QtCore.QRect(0,0,369,182).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(200,150,161,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")

        self.password_pushButton = QtGui.QPushButton(self)
        self.password_pushButton.setGeometry(QtCore.QRect(10,150,93,25))
        self.password_pushButton.setFlat(False)
        self.password_pushButton.setObjectName("password_pushButton")

        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10,10,351,131))
        self.groupBox.setObjectName("groupBox")

        self.hosts_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.hosts_lineEdit.setGeometry(QtCore.QRect(110,50,231,20))
        self.hosts_lineEdit.setObjectName("hosts_lineEdit")

        self.username_edit = QtGui.QLineEdit(self.groupBox)
        self.username_edit.setGeometry(QtCore.QRect(110,20,230,20))
        self.username_edit.setObjectName("username_edit")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10,50,101,20))
        self.label.setObjectName("label")

        self.username_label = QtGui.QLabel(self.groupBox)
        self.username_label.setGeometry(QtCore.QRect(11,20,97,21))
        self.username_label.setObjectName("username_label")

        self.comment_label = QtGui.QLabel(self.groupBox)
        self.comment_label.setGeometry(QtCore.QRect(11,80,93,21))
        self.comment_label.setObjectName("comment_label")

        self.comment_edit = QtGui.QLineEdit(self.groupBox)
        self.comment_edit.setGeometry(QtCore.QRect(110,80,230,20))
        self.comment_edit.setObjectName("comment_edit")

        self.status_checkBox = QtGui.QCheckBox(self.groupBox)
        self.status_checkBox.setGeometry(QtCore.QRect(110,110,131,16))
        self.status_checkBox.setObjectName("status_checkBox")
        
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
        self.status_checkBox.setText(QtGui.QApplication.translate("Dialog", "Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.password_pushButton.setText(QtGui.QApplication.translate("Dialog", "Новый пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Разрешённые IP:", None, QtGui.QApplication.UnicodeUTF8))        

    def setPassword(self):
        child = PasswordEditFrame()
        
        if child.exec_()==1:
            if child.password:
                self.password = unicode(child.password.toHex())
                
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
        else:
            print 'New nas'
            model=Object()
            model.password=self.password
            
            
        if self.username_edit.text():
            model.host = unicode(self.check_ips(str(self.hosts_lineEdit.text())))
            model.username = unicode(self.username_edit.text())
            model.description = unicode(self.comment_edit.text())
            model.status = self.status_checkBox.checkState()==2
            try:
                self.connection.create(model.save(table="billservice_systemuser"))
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
    
            QtGui.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите необходимые данные"))
            return

    def fixtures(self):

        if self.model:
            self.username_edit.setText(unicode(self.model.username))
            self.comment_edit.setText(unicode(self.model.description))
            self.status_checkBox.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.hosts_lineEdit.setText(unicode(self.model.host))
        else:
            self.hosts_lineEdit.setText(u'0.0.0.0/0')





class SystemUserChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        self.setname = "users_frame_header"
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        super(SystemUserChild, self).__init__()
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(0,0,634,365).size()).expandedTo(self.minimumSizeHint()))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setDockNestingEnabled(False)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks|QtGui.QMainWindow.AnimatedDocks)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(0,0,631,311))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.setCentralWidget(self.tableWidget)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.editUserAction = QtGui.QAction(self)
        self.editUserAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editUserAction.setObjectName("openUserAction")

        self.addUserAction = QtGui.QAction(self)
        self.addUserAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addUserAction.setObjectName("addUserAction")

        self.delUserAction = QtGui.QAction(self)
        self.delUserAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delUserAction.setObjectName("delUserAction")
        self.toolBar.addAction(self.addUserAction)
        self.toolBar.addAction(self.delUserAction)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.addAction(self.editUserAction)
        self.tableWidget.addAction(self.addUserAction)
        self.tableWidget.addAction(self.delUserAction)

        self.connect(self.addUserAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.connect(self.delUserAction, QtCore.SIGNAL("triggered()"), self.delete)
        self.connect(self.editUserAction, QtCore.SIGNAL("triggered()"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.retranslateUi()
        HeaderUtil.nullifySaved(self.setname)
        self.refresh()
        if not bhdr.isEmpty():
                HeaderUtil.setBinaryHeader(self.setname, bhdr)
                HeaderUtil.getHeader(self.setname, self.tableWidget)
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Системные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tableWidget.clear()
        columns=[u"id", u"Имя", u"Статус", u"Создан", u'Последний вход', u'Последний IP', u'Разрешённые адреса']
        makeHeaders(columns, self.tableWidget)


        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Системные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.addUserAction.setText(QtGui.QApplication.translate("MainWindow", "addUser", None, QtGui.QApplication.UnicodeUTF8))
        self.delUserAction.setText(QtGui.QApplication.translate("MainWindow", "delUserAction", None, QtGui.QApplication.UnicodeUTF8))
        self.editUserAction.setText(QtGui.QApplication.translate("MainWindow", "Редактировать", None, QtGui.QApplication.UnicodeUTF8))

    def addframe(self):
        addf = SystemUserFrame(connection=self.connection)
        #addf.show()
        if addf.exec_()==1:
            self.refresh()


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить пользователя?" , u"Вы уверены, что хотите удалить пользователя?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                #self.connection.delete("DELETE FROM billservice_systemuser WHERE id=%d" % self.getSelectedId())
                self.connection.iddelete("billservice_systemuser", self.getSelectedId())
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
        self.refresh()


    def editframe(self):
        try:
            model=self.connection.get("SELECT * FROM billservice_systemuser WHERE id=%d" % self.getSelectedId())
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
            headerItem.setIcon(QtGui.QIcon("images/user.png"))
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        self.tableWidget.setSortingEnabled(False)
        #nasses=Nas.objects.all().order_by('id')
        #users=self.connection.sql("SELECT * FROM billservice_systemuser ORDER BY id")
        users = self.connection.foselect("billservice_systemuser")
        #self.tableWidget.setRowCount(nasses.count())
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

            
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname, self.tableWidget)
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.configureAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.configureAction.setDisabled(False)
            