#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import Account
from nas.models import IPAddressPool

class AddAccountFrame(QtGui.QDialog):
    def __init__(self, model=None):
        super(AddAccountFrame, self).__init__()
        self.model=model

        self.account_label = QLabel(u'Имя пользователя')
        self.password_label = QLabel(u'Пароль')
        self.vpn_ip_label = QLabel(u'VPN IP адрес')

        user_label = QLabel(u'Имя пользователя')
        username_label = QLabel(u'Аккаунт')
        password_label = QLabel(u'Пароль')
        firstname_label = QLabel(u'Имя')
        lastname_label = QLabel(u'Фамилия')
        address_label = QLabel(u'Адрес')
        vpn_pool_label = QLabel(u'Имя VPN пула')
        vpn_ip_address_label = QLabel(u'VPN IP адрес пользователя')
        ipn_pool_label = QLabel(u'Имя IPN пула')
        ipn_ip_address_label = QLabel(u'IP адрес пльзователя')
        ipn_mac_address_label = QLabel(u'MAC адрес')
        ipn_status_label = QLabel(u'Статус на сервере доступа')
        status_label = QLabel(u'Статус пользователя в системе')
        suspended_label = QLabel(u'Не списывать деньги по периодичесим слугам')
        created_label = QLabel(u'Дата создания')
        ballance_label = QLabel(u'Текущий балланс')
        credit_label = QLabel(u'Максимальный кредит')
        disabled_by_limit_label = QLabel(u'Отключен за превышение лимита')
        assign_ip_from_dhcp_label = QLabel(u'Назначить IP адрес через DHCP')

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setGeometry(QtCore.QRect(30,240,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)


        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))


        self.user_edit = QComboBox()
        self.username_edit = QLineEdit('')
        self.password_edit = QLineEdit('')
        self.password_edit.EchoMode(2)
        self.firstname_edit = QLineEdit('')
        self.lastname_edit = QLineEdit('')
        self.address_edit = QTextEdit()
        self.vpn_pool_edit = QComboBox()
        self.vpn_ip_address_edit = QLineEdit('')
        self.ipn_pool_edit = QComboBox()
        self.ipn_ip_address_edit = QLineEdit('')
        self.ipn_mac_address_edit = QLineEdit('')
        self.ipn_status_edit = QCheckBox()
        self.status_edit = QCheckBox()
        self.suspended_edit = QCheckBox()
        self.created_edit = QDateTimeEdit()
        self.created_edit.setCalendarPopup(True)
        self.ballance_edit = QLineEdit('0')
        self.credit_edit = QLineEdit('0')
        self.disabled_by_limit_edit = QCheckBox()
        self.assign_ip_from_dhcp_edit = QCheckBox()

        #self.button_add = QPushButton('Save')

        user_label.setBuddy(self.user_edit)
        username_label.setBuddy(self.username_edit)
        password_label.setBuddy(self.password_edit)
        firstname_label.setBuddy(self.firstname_edit)
        lastname_label.setBuddy(self.lastname_edit)
        address_label.setBuddy(self.address_edit)
        vpn_pool_label.setBuddy(self.vpn_pool_edit)
        vpn_ip_address_label.setBuddy(self.vpn_ip_address_edit)
        ipn_pool_label.setBuddy(self.ipn_pool_edit)
        ipn_ip_address_label.setBuddy(self.ipn_ip_address_edit)
        ipn_mac_address_label.setBuddy(self.ipn_mac_address_edit)
        ipn_status_label.setBuddy(self.ipn_status_edit)
        status_label.setBuddy(self.status_edit)
        suspended_label.setBuddy(self.suspended_edit)
        created_label.setBuddy(self.created_edit)
        ballance_label.setBuddy(self.ballance_edit)
        credit_label.setBuddy(self.credit_edit)
        disabled_by_limit_label.setBuddy(self.disabled_by_limit_edit)
        assign_ip_from_dhcp_label.setBuddy(self.assign_ip_from_dhcp_edit)


        grid = QGridLayout()

        grid.addWidget(user_label,0,0)
        grid.addWidget(username_label,1,0)
        grid.addWidget(password_label,2,0)
        grid.addWidget(firstname_label,3,0)
        grid.addWidget(lastname_label,4,0)
        grid.addWidget(address_label,5,0)
        grid.addWidget(vpn_pool_label,6,0)
        grid.addWidget(vpn_ip_address_label,7,0)
        grid.addWidget(ipn_pool_label,8,0)
        grid.addWidget(ipn_ip_address_label,9,0)
        grid.addWidget(ipn_mac_address_label,10,0)
        grid.addWidget(ipn_status_label,11,0)
        grid.addWidget(status_label,12,0)
        grid.addWidget(suspended_label,13,0)
        grid.addWidget(created_label,14,0)
        grid.addWidget(ballance_label,15,0)
        grid.addWidget(credit_label,16,0)
        grid.addWidget(disabled_by_limit_label,17,0)
        grid.addWidget(assign_ip_from_dhcp_label,18,0)

        grid.addWidget(self.user_edit,0,1)
        grid.addWidget(self.username_edit,1,1)
        grid.addWidget(self.password_edit,2,1)
        grid.addWidget(self.firstname_edit,3,1)
        grid.addWidget(self.lastname_edit,4,1)
        grid.addWidget(self.address_edit,5,1)
        grid.addWidget(self.vpn_pool_edit,6,1)
        grid.addWidget(self.vpn_ip_address_edit,7,1)
        grid.addWidget(self.ipn_pool_edit,8,1)
        grid.addWidget(self.ipn_ip_address_edit,9,1)
        grid.addWidget(self.ipn_mac_address_edit,10,1)
        grid.addWidget(self.ipn_status_edit,11,1)
        grid.addWidget(self.status_edit,12,1)
        grid.addWidget(self.suspended_edit,13,1)
        grid.addWidget(self.created_edit,14,1)
        grid.addWidget(self.ballance_edit,15,1)
        grid.addWidget(self.credit_edit,16,1)
        grid.addWidget(self.disabled_by_limit_edit,17,1)
        grid.addWidget(self.assign_ip_from_dhcp_edit,18,1)


        #grid.addWidget(self.button_add,19,1)
        grid.addWidget(self.buttonBox,19,0,2,2)

        #layout = QVBoxLayout()

        self.setLayout(grid)

        #self.connect(self.button_add,  QtCore.SIGNAL("clicked()"), self.save)
        #self.connect(self.button_add, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))


        self.fixtures()

    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:
            model=self.model
        else:
            print 'account'
            model=Account()
        model.user = User.objects.get(username=unicode(self.user_edit.currentText()))

        model.username = unicode(self.username_edit.text())



        #if self.model.vpn_pool:
        #    self.vpn_pool_edit.setCurrentItem(self.vpn_pool_edit.findItems(self.model.vpn_pool.name, QtCore.Qt.MatchFlags())[0])

        #if self.model.ipn_pool:
        #    self.ipn_pool_edit.setCurrentItem(self.ipn_pool_edit.findItems(self.model.ipn_pool.name, QtCore.Qt.MatchFlags())[0])

        model.password = unicode(self.password_edit.text())
        model.firstname = unicode(self.firstname_edit.text())
        model.lastname = unicode(self.lastname_edit.text())
        model.address = unicode(self.address_edit.toPlainText())


        if unicode(self.ipn_ip_address_edit.text())=='None' or unicode(self.ipn_ip_address_edit.text())==u"":
            value = None
        else:
            value = unicode(self.ipn_ip_address_edit.text())

        model.ipn_ip_address = value
        print 'ipn ok'

        if unicode(self.vpn_ip_address_edit.text())=='None' or unicode(self.vpn_ip_address_edit.text())==u'':
            value = None
        else:
            value = unicode(self.vpn_ip_address_edit.text())

        model.vpn_ip_address = value
        print 'vpn ok'

        if unicode(self.ipn_mac_address_edit.text())=='None' or unicode(self.ipn_mac_address_edit.text())==u'':
            value = None
        else:
            value = unicode(self.ipn_mac_address_edit.text())

        model.ipn_mac_address = unicode(self.ipn_mac_address_edit.text())

        #self.model.ipn_status = self.ipn_status_edit.checkStateSet()
        #self.model.status = self.status_edit.checkStateSet()
        #self.model.suspended = self.suspended_edit.checkStateSet()

        #self.created_edit.setDateTime(QDateTimeEdit.dateTimeFromText(self.model.created))

        model.ballance = unicode(self.ballance_edit.text())
        model.credit = unicode(self.credit_edit.text())
        #print self.disabled_by_limit_edit.checkStateSet()
        #self.model.disabled_by_limit = self.disabled_by_limit_edit.checkStateSet()
        #self.model.assign_ip_from_dhcp = self.assign_ip_from_dhcp_edit.checkStateSet()
        try:
            model.save()
        except Exception, e:
            print e
            return



        QDialog.accept(self)

    def fixtures(self):


        users = User.objects.all()
        for user in users:
            self.user_edit.addItem(user.username)

        pools = IPAddressPool.objects.all()

        for pool in pools:
            self.ipn_pool_edit.addItem(pool.name)
            self.vpn_pool_edit.addItem(pool.name)

        if self.model:
            self.username_edit.setText(unicode(self.model.username))

            self.user_edit.setCurrentIndex(self.user_edit.findText(self.model.user.username, QtCore.Qt.MatchCaseSensitive))

            if self.model.vpn_pool:
                self.vpn_pool_edit.setCurrentIndex(self.vpn_pool_edit.findText(self.model.vpn_pool.name, QtCore.Qt.MatchFlags())[0])

            if self.model.ipn_pool:
                self.ipn_pool_edit.setCurrentIndex(self.ipn_pool_edit.findText(self.model.ipn_pool.name, QtCore.Qt.MatchFlags())[0])

            self.password_edit.setText(unicode(self.model.password))
            self.firstname_edit.setText(unicode(self.model.firstname))
            self.lastname_edit.setText(unicode(self.model.lastname))
            self.address_edit.setText(unicode(self.model.address))
            self.ipn_ip_address_edit.setText(unicode(self.model.ipn_ip_address))
            self.vpn_ip_address_edit.setText(unicode(self.model.vpn_ip_address))
            self.ipn_mac_address_edit.setText(unicode(self.model.ipn_mac_address))

            self.ipn_status_edit.setTristate(self.model.ipn_status)
            self.status_edit.setTristate(self.model.status)
            self.suspended_edit.setTristate(self.model.suspended)
            self.created_edit.setDateTime(self.model.created)

            self.ballance_edit.setText(unicode(self.model.ballance))
            self.credit_edit.setText(unicode(self.model.credit))

            self.disabled_by_limit_edit.setTristate(self.model.disabled_by_limit)
            self.assign_ip_from_dhcp_edit.setTristate(self.model.assign_ip_from_dhcp)


    def save(self):
        print 'Saved'



class AccountsMdiChild(QtGui.QDialog):
    sequenceNumber = 1

    def __init__(self):
        super(AccountsMdiChild, self).__init__()

        self.button = QPushButton('Refresh')
        self.button_add = QPushButton('Add')
        self.button_edit = QPushButton('Edit')
        self.button_delete = QPushButton('Delete')
        self.countedit = QLineEdit("100")
        self.tablewidget = QTableWidget()

        self.tablewidget.setAlternatingRowColors(True)
        self.tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablewidget.setSelectionMode(QTableWidget.SingleSelection)
        #self.tablewidget.setSortingEnabled(True)


        columns=[u'Id', u'Аккаунт владельца', u'Имя пользователя', u'Балланс', u'Кредит', u'Имя', u'Фамилия', u'VPN IP адрес', u'IPN IP адрес', u'Усыплён', u'Статус в системе']
        i=0
        self.tablewidget.setColumnCount(len(columns))
        self.tablewidget.setHorizontalHeaderLabels(columns)




        #layout = QVBoxLayout()
        layout = QGridLayout()
        layout.addWidget(self.countedit,0,0)
        layout.addWidget(self.button,0,1)
        layout.addWidget(self.button_add,1,1)
        layout.addWidget(self.button_edit,1,2)
        layout.addWidget(self.button_delete,1,3)
        layout.addWidget(self.tablewidget,2,0,3,0)
        self.setLayout(layout)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.tablewidget.resizeColumnsToContents()
        self.resize(1100,600)
        self.setSizeGripEnabled(1)




        self.connect(self.button, QtCore.SIGNAL("clicked()"), self.refresh)
        self.connect(self.button_add, QtCore.SIGNAL("clicked()"), self.addframe)
        self.connect(self.button_edit, QtCore.SIGNAL("clicked()"), self.editframe)
        self.connect(self.button_delete, QtCore.SIGNAL("clicked()"), self.delete)
        self.connect(self.tablewidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)


    def addframe(self):

        model=None
        addf = AddAccountFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()
    def getSelectedId(self):
        return int(self.tablewidget.item(self.tablewidget.currentRow(), 0).text())

    def delete(self):
        id=self.getSelectedId()
        if id>0 and QMessageBox.question(self, u"Удалить аккаунт?" , u"Вы уверены, что хотите удалить пользователя из системы?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                model=Account.objects.get(id=self.getSelectedId()).delete()
            except Exception, e:
                print e
        self.refresh()


    def editframe(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=Account.objects.get(id=self.getSelectedId())
        except:
            model=None

        addf = AddAccountFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tablewidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)

    def refresh(self):
        cnt = int(self.countedit.text())

        accounts=Account.objects.all().order_by('id')[0:cnt]
        self.tablewidget.setRowCount(accounts.count())
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for a in accounts:
            self.addrow(a.id, i,0)
            self.addrow(a.user, i,1)
            self.addrow(a.username, i,2)
            self.addrow(a.ballance, i,3)
            self.addrow(a.credit, i,4)
            self.addrow(a.firstname, i,5)
            self.addrow(a.lastname, i,6)
            self.addrow(a.vpn_ip_address, i,7)
            self.addrow(a.ipn_ip_address, i,8)
            self.addrow(a.suspended, i,9)
            self.addrow(a.status, i,10)
            i+=1
        self.tablewidget.resizeColumnsToContents()

    def newFile(self):
        self.isUntitled = True
        #self.curFile = self.tr("iplist").arg(MdiChild.sequenceNumber)
        #MdiChild.sequenceNumber += 1
        #self.setWindowTitle(self.curFile+"[*]")

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                        self.tr("Cannot read file %1:\n%2.")
                        .arg(fileName)
                        .arg(file.errorString()))
            return False

        instr = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPlainText(instr.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def save(self):
        if self.isUntitled:
            return self.saveAs()
        else:
            return self.saveFile(self.curFile)

    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save As"),
                        self.curFile)
        if fileName.isEmpty:
            return False

        return self.saveFile(fileName)

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)

        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("Cannot write file %1:\n%2.")
                    .arg(fileName)
                    .arg(file.errorString()))
            return False

        outstr = QtCore.QTextStream(file)
        QtCore.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outstr << self.toPlainText()
        QtCore.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        return True

    def userFriendlyCurrentFile(self):
        return self.strippedName(self.curFile)

    def currentFile(self):
        return self.curFile

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def documentWasModified(self):
        self.setWindowModified(self.document().isModified())

    def maybeSave(self):
        if self.document().isModified():
            ret = QtGui.QMessageBox.warning(self, self.tr("MDI"),
                    self.tr("'%1' has been modified.\n"\
                            "Do you want to save your changes?")
                    .arg(self.userFriendlyCurrentFile()),
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                    QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
            if ret == QtGui.QMessageBox.Yes:
                return self.save()
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def setCurrentFile(self, fileName):
        self.curFile = QtCore.QFileInfo(fileName).canonicalFilePath()
        self.isUntitled = False
        self.document().setModified(False)
        self.setWindowModified(False)
        self.setWindowTitle(self.userFriendlyCurrentFile() + "[*]")

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

