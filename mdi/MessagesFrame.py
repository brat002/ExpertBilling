#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil

class MessageDialog(QtGui.QDialog):
    def __init__(self, accounts=[], model=None,connection=None):
        super(MessageDialog, self).__init__()
        self.accounts = accounts
        self.model = model
        self.connection = connection
        self.setObjectName("MessageDialog")
        self.resize(716, 287)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 9, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtGui.QTextEdit(self)
        self.textEdit.setAutoFormatting(QtGui.QTextEdit.AutoNone)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBox_public = QtGui.QCheckBox(self.groupBox)
        self.checkBox_public.setObjectName("checkBox_public")
        self.gridLayout_2.addWidget(self.checkBox_public, 0, 1, 1, 1)
        self.checkBox_private = QtGui.QCheckBox(self.groupBox)
        self.checkBox_private.setObjectName("checkBox_private")
        self.gridLayout_2.addWidget(self.checkBox_private, 1, 1, 1, 1)
        self.checkBox_agent = QtGui.QCheckBox(self.groupBox)
        self.checkBox_agent.setObjectName("checkBox_agent")
        self.gridLayout_2.addWidget(self.checkBox_agent, 2, 1, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.spinBox = QtGui.QSpinBox(self.groupBox_2)
        self.spinBox.setMaximum(99999999)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_3.addWidget(self.spinBox, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 2, 1)


        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Сообщение", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры сообщения", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_public.setText(QtGui.QApplication.translate("Dialog", "Опубликовать в публичной части веб-кабинета(всем)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_private.setText(QtGui.QApplication.translate("Dialog", "Опубликовать в приватной части веб-кабинета", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_agent.setText(QtGui.QApplication.translate("Dialog", "Отправить через EBS Agent", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Параметры отображения", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Срок жизни(минут)", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def fixtures(self):
        if self.model:
            self.textEdit.setPlainText(self.model.body)
            #print self.model.public
            self.checkBox_public.setChecked(self.model.public)
            self.checkBox_private.setChecked(self.model.private)
            self.checkBox_agent.setChecked(self.model.agent)
            self.buttonBox.setDisabled(True)
        if self.accounts:
            accounts = self.connection.sql("SELECT username FROM billservice_account WHERE id in %s ORDER BY username ASC" % str(self.accounts).replace("[","(").replace("]",")"))
            self.connection.commit()
            for account in accounts:
                item = QtGui.QListWidgetItem(unicode(account.username))
                self.listWidget.addItem(item)
        elif self.model:
            accounts = self.connection.sql("SELECT username FROM billservice_account WHERE id in (SELECT account_id FROM billservice_accountviewednews WHERE news_id=%s)" % self.model.id)
            self.connection.commit()
            for account in accounts:
                item = QtGui.QListWidgetItem(unicode(account.username))
                self.listWidget.addItem(item)
        
            
    def accept(self):
        body = self.textEdit.toPlainText()
        #print body
        
        if not body:
            QtGui.QDialog.accept(self)
            return

        if self.checkBox_agent.isChecked()==False and self.checkBox_public.isChecked()==False and self.checkBox_private.isChecked()==False:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Выберите хотя бы один способ получения сообщения абонентами."))
            return
        
        if self.model:
            news_model = self.model
        else:
            news_model = Object()
            
        news_model.body = unicode(body)
        if self.spinBox.value():
            news_model.age = datetime.datetime.now()+datetime.timedelta(minutes=self.spinBox.value())
        news_model.created = "now()"
        if self.checkBox_public.isChecked()==True or (self.accounts and (self.checkBox_public.isChecked() or self.checkBox_private.isChecked())):
            news_model.id = self.connection.save(news_model, "billservice_news")
            
        if self.checkBox_public.isChecked()==True:
            news_model.public = True
            self.connection.save(news_model, "billservice_news")
        
        #if self.checkBox_agent.isChecked():
        #    news_model.id=self.connection.save(news_model, "billservice_news")
            
        if not self.model  and (self.checkBox_private.isChecked() or self.checkBox_agent.isChecked()):
            if self.checkBox_private.isChecked()==True: 
                news_model.private = True
            if self.checkBox_agent.isChecked()==True:
                news_model.agent = True
            news_model.id=self.connection.save(news_model, "billservice_news")
            if self.model:
                QtGui.QDialog.accept(self)
            if self.accounts:
                account_model = Object()
                account_model.news_id = news_model.id
                account_model.viewed = False
                for account in self.accounts:
                    account_model.account_id = account
                    self.connection.save(account_model, "billservice_accountviewednews")
                    self.connection.commit()
            else:
                self.connection.createAccountViewedNews(news_model.id)
        elif not self.accounts and (self.checkBox_private.isChecked() or self.checkBox_agent.isChecked()):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Это сообщение будет помечено только как публичное. Для посылки приватных сообщений воспользуйтесь этой опцией из окна Пользователи и тарифы"))
        QtGui.QDialog.accept(self)




class MessagesEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['Id', u'Дата', u'Публичное', u'Приватное', u'Агент', u'Текст']
        initargs = {"setname":"messages_frame", "objname":"MessagesEbs", "winsize":(0,0,827,476), "wintitle":"Сообщения абонентам", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(MessagesEbs, self).__init__(connection, initargs)
        
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
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_message)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.add_message),("editAction", "Просмотреть", "images/open.png", self.edit_message), ("delAction", "Удалить", "images/del.png", self.del_message)]
        objDict = {self.tableWidget:["addAction", "editAction", "delAction"], self.toolBar:["addAction", "editAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(MessagesEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add_message(self):
        child=MessageDialog(connection=self.connection)
        child.exec_()
        self.refresh()

    def del_message(self):
        id=self.getSelectedId()
        if id>0:
            try:
                #self.connection.sql("UPDATE billservice_settlementperiod SET deleted=TRUE WHERE id=%d" % id, False)
                self.connection.iddelete(id, "billservice_news")
                self.connection.commit()
                self.refresh()
            except Exception, e:
                print e
                self.connection.rollback()
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit_message(self):
        id=self.getSelectedId()
        try:
            model=self.connection.get_model(id, "billservice_news")
        except:
            return

        self.connection.commit()
        child=MessageDialog(connection=self.connection, model=model)
        child.exec_()

        self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/sp.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        self.statusBar().showMessage(u"Идёт получение данных")
        #self.tableWidget.setSortingEnabled(False)
        messages = self.connection.get_messages()

        self.connection.commit()
        self.tableWidget.setRowCount(len(messages))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for message in messages:
            self.addrow(message.id, i,0)
            self.addrow(message.created.strftime(self.strftimeFormat), i,1)
            self.addrow(message.public, i,2)
            self.addrow(message.private, i,3)
            self.addrow(message.agent, i,4)        
            self.addrow(message.body[0:100], i,5)         
            #self.addrow(period.length, i,5)
            #self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        #self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
    def delNodeLocalAction(self):
        super(MessagesEbs, self).delNodeLocalAction([self.delAction])

