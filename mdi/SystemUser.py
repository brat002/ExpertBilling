#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui


from helpers import tableFormat
from helpers import Object as Object
   
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

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

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Изменить пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("Dialog", "Пароль:", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_password_label.setText(QtGui.QApplication.translate("Dialog", "Повторите:", None, QtGui.QApplication.UnicodeUTF8))


class SystemUserFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(SystemUserFrame, self).__init__()
        
        self.connection = connection
        self.model = model
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,344,122).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(109,90,161,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")

        self.username_edit = QtGui.QLineEdit(self)
        self.username_edit.setGeometry(QtCore.QRect(110,9,230,20))
        self.username_edit.setObjectName("username_edit")

        self.username_label = QtGui.QLabel(self)
        self.username_label.setGeometry(QtCore.QRect(11,9,97,20))
        self.username_label.setObjectName("username_label")

        self.comment_label = QtGui.QLabel(self)
        self.comment_label.setGeometry(QtCore.QRect(11,36,93,20))
        self.comment_label.setObjectName("comment_label")

        self.status_checkBox = QtGui.QCheckBox(self)
        self.status_checkBox.setGeometry(QtCore.QRect(110,60,131,21))
        self.status_checkBox.setObjectName("status_checkBox")

        self.password_pushButton = QtGui.QPushButton(self)
        self.password_pushButton.setGeometry(QtCore.QRect(0,90,93,25))
        self.password_pushButton.setFlat(False)
        self.password_pushButton.setObjectName("password_pushButton")

        self.comment_edit = QtGui.QLineEdit(self)
        self.comment_edit.setGeometry(QtCore.QRect(110,36,230,20))
        self.comment_edit.setObjectName("comment_edit")

        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.username_label.setText(QtGui.QApplication.translate("Dialog", "Имя пользователя:", None, QtGui.QApplication.UnicodeUTF8))
        self.comment_label.setText(QtGui.QApplication.translate("Dialog", "Комментарий:", None, QtGui.QApplication.UnicodeUTF8))
        self.status_checkBox.setText(QtGui.QApplication.translate("Dialog", "Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.password_pushButton.setText(QtGui.QApplication.translate("Dialog", "Новый пароль", None, QtGui.QApplication.UnicodeUTF8))

        

        

    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:
            model=self.model
        else:
            print 'New nas'
            model=Object()


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

    def fixtures(self):

        if self.model:
            self.username_edit.setText(unicode(self.model.username))
            self.comment_edit.setText(unicode(self.model.description))
            self.status_checkBox.setCheckState(self.model.status == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )





class SystemUserChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(SystemUserChild, self).__init__()
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(0,0,634,365).size()).expandedTo(self.minimumSizeHint()))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setDockNestingEnabled(False)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks|QtGui.QMainWindow.AnimatedDocks)

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
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.addUserAction = QtGui.QAction(self)
        self.addUserAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addUserAction.setObjectName("addUserAction")

        self.delUserAction = QtGui.QAction(self)
        self.delUserAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delUserAction.setObjectName("delUserAction")
        self.toolBar.addAction(self.addUserAction)
        self.toolBar.addAction(self.delUserAction)
        
        self.connect(self.addUserAction, QtCore.SIGNAL("triggered()"), self.addframe)
        self.retranslateUi()
        self.refresh()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Системные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("MainWindow", "id", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Created", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "Last Login", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        headerItem5.setText(QtGui.QApplication.translate("MainWindow", "Last IP", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem5)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Системные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.addUserAction.setText(QtGui.QApplication.translate("MainWindow", "addUser", None, QtGui.QApplication.UnicodeUTF8))
        self.delUserAction.setText(QtGui.QApplication.translate("MainWindow", "delUserAction", None, QtGui.QApplication.UnicodeUTF8))

    def addframe(self):
        addf = SystemUserFrame(connection=self.connection)
        #addf.show()
        addf.exec_()
        self.refresh()

    def configure(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=self.connection.get("SELECT * FROM nas_nas WHERE id=%d" % self.getSelectedId())
        except:
            return
        import Pyro.core

        if self.connection.configureNAS(str(model.ipaddress), str(model.login), str(model.password), str(model.confstring)):
            QtGui.QMessageBox.warning(self, u"Ok", unicode(u"Настройка сервера доступа прошла удачно."))
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка во время конфигурирования."))



    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def delete(self):
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить сервер доступа?" , u"Все связанные с сервером доступа аккаунты \n и вся статистика будут удалены. Вы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                self.connection.delete("DELETE FROM nas_nas WHERE id=%d" % self.getSelectedId())
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
        self.refresh()


    def editframe(self):
        try:
            model=self.connection.get("SELECT * FROM nas_nas WHERE id=%d" % self.getSelectedId())
        except:
            model=None

        addf = AddNasFrame(connection=self.connection, model=model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):

        #nasses=Nas.objects.all().order_by('id')
        users=self.connection.sql("SELECT * FROM billservice_systemuser ORDER BY id")
        #self.tableWidget.setRowCount(nasses.count())
        self.tableWidget.setRowCount(len(users))
        i=0
        for user in users:
            self.addrow(user.id, i,0)
            self.addrow(user.username, i,1)
            self.addrow(user.status, i,2)
            self.addrow(user.created, i,3)
            self.addrow(user.last_login, i,4)
            self.addrow(user.last_ip, i,5)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

            
        self.tableWidget.resizeColumnsToContents()

    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delAction.setDisabled(True)
            self.configureAction.setDisabled(True)
        else:
            self.delAction.setDisabled(False)
            self.configureAction.setDisabled(False)
            