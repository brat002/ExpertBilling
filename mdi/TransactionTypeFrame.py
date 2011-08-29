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
    
class AddTransactionType(QtGui.QDialog):
    def __init__(self, connection,model=None):
        super(AddTransactionType, self).__init__()
        self.model=model
        self.connection=connection
        self.connection.commit()

        self.resize(541, 215)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox_payment_type = QtGui.QGroupBox(self)
        self.groupBox_payment_type.setObjectName(_fromUtf8("groupBox_payment_type"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_payment_type)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_name = QtGui.QLabel(self.groupBox_payment_type)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout.addWidget(self.label_name, 0, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox_payment_type)
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.gridLayout.addWidget(self.lineEdit_name, 0, 2, 1, 1)
        self.label_internal_name = QtGui.QLabel(self.groupBox_payment_type)
        self.label_internal_name.setObjectName(_fromUtf8("label_internal_name"))
        self.gridLayout.addWidget(self.label_internal_name, 1, 0, 1, 2)
        self.lineEdit_internal_name = QtGui.QLineEdit(self.groupBox_payment_type)
        self.lineEdit_internal_name.setObjectName(_fromUtf8("lineEdit_internal_name"))
        self.gridLayout.addWidget(self.lineEdit_internal_name, 1, 2, 1, 1)
        self.label_hint = QtGui.QLabel(self.groupBox_payment_type)
        self.label_hint.setObjectName(_fromUtf8("label_hint"))
        self.gridLayout.addWidget(self.label_hint, 2, 1, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox_payment_type, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("AddTransactionType", "Редактирование типа платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_payment_type.setTitle(QtGui.QApplication.translate("AddTransactionType", "Параметры типа платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("AddTransactionType", "Название платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_internal_name.setText(QtGui.QApplication.translate("AddTransactionType", "Внутреннее имя платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_hint.setText(QtGui.QApplication.translate("AddTransactionType", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Liberation Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Важно!!!</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Для внутреннего имени платежа используйте большие</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">латинские символы без пробелов и спецсимволов.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">К примеру SBERBANK_PAYMENT, CREDIT_PAYMENT и т.д.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))



    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.model:
            model=self.model
        else:
            #print 'New sp'
            model=Object()

        if unicode(self.lineEdit_name.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано название"))
            return
        else:
            model.name=unicode(self.lineEdit_name.text())

        if unicode(self.lineEdit_internal_name.text())==u"":
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано внутреннее название"))
            return
        else:
            model.internal_name=unicode(self.lineEdit_internal_name.text())

      

        try:
            self.connection.save(model,"billservice_transactiontype")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            return



        QtGui.QDialog.accept(self)

    def fixtures(self):
       
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            self.lineEdit_internal_name.setText(unicode(self.model.internal_name))




class TransactionTypeEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=['Id', u'Название', u'Внутреннее имя']
        initargs = {"setname":"trtype_period", "objname":"TransactionTypeEbs", "winsize":(0,0,827,476), "wintitle":"Типы платежей", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(TransactionTypeEbs, self).__init__(connection, initargs)
        
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
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.add), ("editAction", "Редактировать", "images/open.png", self.edit), ("delAction", "Удалить", "images/del.png", self.delete)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
    def retranslateUI(self, initargs):
        super(TransactionTypeEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

    def add(self):
        child=AddTransactionType(connection=self.connection)
        if child.exec_():
            self.refresh()

    def delete(self):
        id=self.getSelectedId()
        if id>0:
            model = self.connection.get_model(id, "billservice_transactiontype")
            if not model.is_deletable:
                QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Указанный тип платежа является внутрисистемным и не может быть удалён!")
                return
                
            if QtGui.QMessageBox.question(self, u"Удалить тип платежа" , u"Все связанные с этим типом платежа платежи будут удалены.\nВы уверены, что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                try:
                    self.connection.iddelete(id, "billservice_transactiontype")
                    self.connection.commit()
                    self.refresh()
                except Exception, e:
                    print e
                    self.connection.rollback()
                    QtGui.QMessageBox.warning(self, u"Предупреждение!", u"Удаление не было произведено!")


    def edit(self):
        id=self.getSelectedId()
        try:
            model=self.connection.get_model(id, "billservice_transactiontype")
        except:
            return

        self.connection.commit()
        child=AddTransactionType(connection=self.connection, model=model)
        if child.exec_():
            self.refresh()


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/moneybook.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def refresh(self):
        self.statusBar().showMessage(u"Идёт получение данных")
        #self.tableWidget.setSortingEnabled(False)
        items = self.connection.get_models("billservice_transactiontype", order={'name':'ASC'})
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow(item.id, i,0)
            self.addrow(item.name, i,1)
            self.addrow(item.internal_name, i,2)
            self.tableWidget.setColumnHidden(0, True)
            i+=1

        HeaderUtil.getHeader(self.setname, self.tableWidget)
        #self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
            
    def delNodeLocalAction(self):
        super(TransactionTypeEbs, self).delNodeLocalAction([self.delAction])

