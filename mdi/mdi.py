#-*-coding=utf-8*-

############################################################################
#
#  Copyright (C) 2004-2005 Trolltech AS. All rights reserved.
#
#  This file is part of the example classes of the Qt Toolkit.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  self file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
#
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact the
#  sales department at sales@trolltech.com.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################################

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *



import mdi_rc
#-*-coding=utf-8-*-

import os, sys

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from django.contrib.auth.models import User
from billservice.models import Account
from nas.models import IPAddressPool

#class MdiChild(QtGui.QTextEdit):

class AddNFFrame(QtGui.QDialog):
    def __init__(self, model=None):
        super(AddNFFrame, self).__init__()
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
        self.ballance_edit = QLineEdit('')
        self.credit_edit = QLineEdit('')
        self.disabled_by_limit_edit = QCheckBox()
        self.assign_ip_from_dhcp_edit = QCheckBox()

        self.button_add = QPushButton('Save')

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


        grid.addWidget(self.button_add,19,1)

        #layout = QVBoxLayout()

        self.setLayout(grid)

        #self.connect(self.button_add,  QtCore.SIGNAL("clicked()"), self.save)
        self.connect(self.button_add, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))

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

class MdiChild(QtGui.QDialog):
    sequenceNumber = 1

    def __init__(self):
        super(MdiChild, self).__init__()

        self.button = QPushButton('Refresh')
        self.button_add = QPushButton('Add')
        self.button_edit = QPushButton('Edit')
        self.countedit = QLineEdit("0")
        self.listWidget = QListWidget()
        self.tablewidget = QTableWidget()

        self.tablewidget.setAlternatingRowColors(True)
        self.tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablewidget.setSelectionMode(QTableWidget.SingleSelection)

        columns=(u'Id', u'Аккаунт владельца', u'Имя пользователя', u'Балланс', u'Кредит', u'Имя', u'Фамилия', u'VPN IP адрес', u'IPN IP адрес', u'Усыплён', u'Статус')
        i=0
        self.tablewidget.setColumnCount(len(columns))
        for column in columns:
            headerItem = QtGui.QTableWidgetItem()
            headerItem.setText(column)
            self.tablewidget.setHorizontalHeaderItem(i,headerItem)
            i+=1




        layout = QVBoxLayout()
        layout.addWidget(self.countedit)
        layout.addWidget(self.button)
        layout.addWidget(self.button_add)
        layout.addWidget(self.button_edit)
        layout.addWidget(self.tablewidget)
        self.setLayout(layout)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True


        self.connect(self.button, QtCore.SIGNAL("clicked()"), self.refresh)
        self.connect(self.button_add, QtCore.SIGNAL("clicked()"), self.addframe)
        self.connect(self.button_edit, QtCore.SIGNAL("clicked()"), self.editframe)

    def addframe(self):

        model=None
        addf = AddNFFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def editframe(self):
        print self.tablewidget.item(self.tablewidget.currentRow(), 0).text()
        try:
            model=Account.objects.get(id=int(self.tablewidget.item(self.tablewidget.currentRow(), 0).text()))
        except:
            model=None

        addf = AddNFFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tablewidget.setItem(x,y,headerItem)

    def refresh(self):
        cnt = int(self.countedit.text())

        accounts=Account.objects.all().order_by('id')[0:cnt]
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for a in accounts:
            self.tablewidget.setRowCount(i+1)
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


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.workspace = QtGui.QWorkspace()
        self.setCentralWidget(self.workspace)

        self.connect(self.workspace, QtCore.SIGNAL("windowActivated(QWidget *)"), self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle(self.tr("MDI"))

    def closeEvent(self, event):
        self.workspace.closeAllWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def newFile(self):
        child = self.createMdiChild()
        child.newFile()
        child.show()

    def open(self):
        #fileName = QtGui.QFileDialog.getOpenFileName(self)
        #if not fileName.isEmpty():
        existing = self.findMdiChild('iplist')
        print existing
        if existing:
            child=self.workspace.setActiveWindow(existing)
        #        return
        else:
            child = self.createMdiChild()

        #    if child.loadFile(fileName):
        #self.statusBar().showMessage(self.tr("File loaded"), 2000)
        nf=NetFlowStream.objects.all()[0:200]
        i=0
        for a in nf:
            child.tablewidget.setRowCount(i+1)
            child.listWidget.addItem(str(a.src_addr))
            child.browser.append(str(a.src_addr))
            headerItem = QtGui.QTableWidgetItem()
            headerItem1 = QtGui.QTableWidgetItem()

            headerItem.setText(QtGui.QApplication.translate("MainWindow", a.src_addr, None, QtGui.QApplication.UnicodeUTF8))
            headerItem1.setText(QtGui.QApplication.translate("MainWindow", a.dst_addr, None, QtGui.QApplication.UnicodeUTF8))
            child.tablewidget.setItem(i,0,headerItem)
            child.tablewidget.setItem(i,1,headerItem1)
            i+=1
        child.show()


    def save(self):
        if self.activeMdiChild().save():
            self.statusBar().showMessage(self.tr("File saved"), 2000)

    def saveAs(self):
        if self.activeMdiChild().saveAs():
            self.statusBar().showMessage(self.tr("File saved"), 2000)

    def cut(self):
        self.activeMdiChild().cut()

    def copy(self):
        self.activeMdiChild().copy()

    def paste(self):
        self.activeMdiChild().paste()

    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About MDI"),
            self.tr("The <b>MDI</b> example demonstrates how to write multiple "
                    "document interface applications using Qt."))

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.saveAct.setEnabled(hasMdiChild)
        self.saveAsAct.setEnabled(hasMdiChild)
        self.pasteAct.setEnabled(hasMdiChild)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.arrangeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()

        self.separatorAct.setVisible(len(windows) != 0)

        i = 0

        for child in windows:
            if i < 9:
                text = self.tr("&%1 %2").arg(i + 1).arg(child.userFriendlyCurrentFile())
            else:
                text = self.tr("%1 %2").arg(i + 1).arg(child.userFriendlyFile())

            i += 1

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)

    def createMdiChild(self):
        child = MdiChild()
        self.workspace.addWindow(child)
        self.connect(child, QtCore.SIGNAL("copyAvailable(bool)"),
                     self.cutAct.setEnabled)
        self.connect(child, QtCore.SIGNAL("copyAvailable(bool)"),
                     self.copyAct.setEnabled)
        return child

    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon(":/images/new.png"),
                            self.tr("&New"), self)
        self.newAct.setShortcut(self.tr("Ctrl+N"))
        self.newAct.setStatusTip(self.tr("Create a new file"))
        self.connect(self.newAct, QtCore.SIGNAL("triggered()"), self.newFile)

        self.openAct = QtGui.QAction(QtGui.QIcon(":/images/open.png"),
                        self.tr("&Open..."), self)
        self.openAct.setShortcut(self.tr("Ctrl+O"))
        self.openAct.setStatusTip(self.tr("Open an existing file"))
        self.connect(self.openAct, QtCore.SIGNAL("triggered()"), self.open)

        self.saveAct = QtGui.QAction(QtGui.QIcon(":/images/save.png"),
                        self.tr("&Save"), self)
        self.saveAct.setShortcut(self.tr("Ctrl+S"))
        self.saveAct.setStatusTip(self.tr("Save the document to disk"))
        self.connect(self.saveAct, QtCore.SIGNAL("triggered()"), self.save)

        self.saveAsAct = QtGui.QAction(self.tr("Save &As..."), self)
        self.saveAsAct.setStatusTip(self.tr("Save the document under a new name"))
        self.connect(self.saveAsAct, QtCore.SIGNAL("triggered()"), self.saveAs)

        self.exitAct = QtGui.QAction(self.tr("E&xit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(self.tr("Exit the application"))
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)

        self.cutAct = QtGui.QAction(QtGui.QIcon(":/images/cut.png"),
                        self.tr("Cu&t"), self)
        self.cutAct.setShortcut(self.tr("Ctrl+X"))
        self.cutAct.setStatusTip(self.tr("Cut the current selection's "
                                         "contents to the clipboard"))
        self.connect(self.cutAct, QtCore.SIGNAL("triggered()"), self.cut)

        self.copyAct = QtGui.QAction(QtGui.QIcon(":/images/copy.png"),
                        self.tr("&Copy"), self)
        self.copyAct.setShortcut(self.tr("Ctrl+C"))
        self.copyAct.setStatusTip(self.tr("Copy the current selection's "
                                          "contents to the clipboard"))
        self.connect(self.copyAct, QtCore.SIGNAL("triggered()"), self.copy)

        self.pasteAct = QtGui.QAction(QtGui.QIcon(":/images/paste.png"),
                        self.tr("&Paste"), self)
        self.pasteAct.setShortcut(self.tr("Ctrl+V"))
        self.pasteAct.setStatusTip(self.tr("Paste the clipboard's contents "
                                           "into the current selection"))
        self.connect(self.pasteAct, QtCore.SIGNAL("triggered()"), self.paste)

        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"), self.about)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                     QtGui.qApp, QtCore.SLOT("aboutQt()"))

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)

        self.windowMenu = self.menuBar().addMenu(self.tr("&Window"))
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar(self.tr("File"))
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar(self.tr("Edit"))
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def readSettings(self):
        settings = QtCore.QSettings("Trolltech", "MDI Example")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Trolltech", "MDI Example")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))

    def activeMdiChild(self):
        return self.workspace.activeWindow()

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.workspace.windowList():
            if window.currentFile() == canonicalFilePath:
                return window
        return None


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
