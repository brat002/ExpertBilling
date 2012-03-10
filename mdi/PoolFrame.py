#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

import IPy
from helpers import tableFormat
from db import AttrDict
from helpers import makeHeaders
from helpers import HeaderUtil

from ebsWindow import ebsTableWindow, ebsTabs_n_TablesWindow

poolt_types=['IPv4 VPN', 'IPv4 IPN', 'IPv6 VPN', 'IPv6 IPN']

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class AddPoolFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(AddPoolFrame, self).__init__()
        self.model = model
        #print "model=", model
        self.connection = connection
        self.setObjectName("AddPoolFrame")
        self.resize(463, 197)
        self.setSizeGripEnabled(False)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox_pool = QtGui.QGroupBox(self)
        self.groupBox_pool.setObjectName(_fromUtf8("groupBox_pool"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_pool)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox_pool)
        self.lineEdit_name.setMaximumSize(QtCore.QSize(16777215, 20))
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.gridLayout.addWidget(self.lineEdit_name, 0, 2, 1, 1)
        self.label_type = QtGui.QLabel(self.groupBox_pool)
        self.label_type.setObjectName(_fromUtf8("label_type"))
        self.gridLayout.addWidget(self.label_type, 0, 3, 1, 1)
        self.comboBox_type = QtGui.QComboBox(self.groupBox_pool)
        self.comboBox_type.setMinimumSize(QtCore.QSize(71, 0))
        self.comboBox_type.setObjectName(_fromUtf8("comboBox_type"))
        self.gridLayout.addWidget(self.comboBox_type, 0, 4, 1, 1)
        self.comboBox_next_pool_id = QtGui.QComboBox(self.groupBox_pool)
        self.comboBox_next_pool_id.setObjectName(_fromUtf8("comboBox_next_pool_id"))
        self.gridLayout.addWidget(self.comboBox_next_pool_id, 7, 2, 1, 1)
        self.label_from = QtGui.QLabel(self.groupBox_pool)
        self.label_from.setObjectName(_fromUtf8("label_from"))
        self.gridLayout.addWidget(self.label_from, 1, 0, 1, 1)
        self.lineEdit_end_ip = QtGui.QLineEdit(self.groupBox_pool)
        self.lineEdit_end_ip.setMinimumSize(QtCore.QSize(131, 0))
        self.lineEdit_end_ip.setMaximumSize(QtCore.QSize(16777215, 20))
        self.lineEdit_end_ip.setObjectName(_fromUtf8("lineEdit_end_ip"))
        self.gridLayout.addWidget(self.lineEdit_end_ip, 2, 2, 1, 1)
        self.label_to = QtGui.QLabel(self.groupBox_pool)
        self.label_to.setObjectName(_fromUtf8("label_to"))
        self.gridLayout.addWidget(self.label_to, 2, 0, 1, 1)
        self.lineEdit_start_ip = QtGui.QLineEdit(self.groupBox_pool)
        self.lineEdit_start_ip.setMaximumSize(QtCore.QSize(16777215, 20))
        self.lineEdit_start_ip.setObjectName(_fromUtf8("lineEdit_start_ip"))
        self.gridLayout.addWidget(self.lineEdit_start_ip, 1, 2, 1, 1)
        self.label_name = QtGui.QLabel(self.groupBox_pool)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout.addWidget(self.label_name, 0, 0, 1, 1)
        self.label_next_pool_id = QtGui.QLabel(self.groupBox_pool)
        self.label_next_pool_id.setObjectName(_fromUtf8("label_next_pool_id"))
        self.gridLayout.addWidget(self.label_next_pool_id, 7, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_pool, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 2, 1, 1, 1)
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        
        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setTabOrder(self.lineEdit_name, self.comboBox_type)
        self.setTabOrder(self.comboBox_type, self.lineEdit_end_ip)
        self.setTabOrder(self.lineEdit_end_ip, self.lineEdit_start_ip)
        self.setTabOrder(self.lineEdit_start_ip, self.comboBox_next_pool_id)
        self.setTabOrder(self.comboBox_next_pool_id, self.buttonBox)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки пула", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_pool.setTitle(QtGui.QApplication.translate("Dialog", "Настройки пула", None, QtGui.QApplication.UnicodeUTF8))
        self.label_type.setText(QtGui.QApplication.translate("Dialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_type.setItemText(0, QtGui.QApplication.translate("Dialog", "VPN", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_type.setItemText(1, QtGui.QApplication.translate("Dialog", "IPN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_from.setText(QtGui.QApplication.translate("Dialog", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.label_to.setText(QtGui.QApplication.translate("Dialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.label_next_pool_id.setText(QtGui.QApplication.translate("Dialog", "Следующий пул", None, QtGui.QApplication.UnicodeUTF8))

        #self.lineEdit_start_ip.setValidator(self.ipValidator)
        #self.lineEdit_end_ip.setValidator(self.ipValidator)

    def fixtures(self):
        self.comboBox_type.addItem("IPv4 VPN")
        self.comboBox_type.setItemData(0, QtCore.QVariant(0))
        self.comboBox_type.addItem("IPv4 IPN")
        self.comboBox_type.setItemData(1, QtCore.QVariant(1))
        self.comboBox_type.addItem("IPv6 VPN")
        self.comboBox_type.setItemData(2, QtCore.QVariant(2))
        self.comboBox_type.addItem("IPv6 IPN")
        self.comboBox_type.setItemData(3, QtCore.QVariant(3))

        items = self.connection.get_ippools(fields=['id','name'])
        self.connection.commit()
        i=0
        self.comboBox_next_pool_id.clear()
        self.comboBox_next_pool_id.addItem("---")
        self.comboBox_next_pool_id.setItemData(i, QtCore.QVariant(0))
        for item in items:
            if self.model and item.id==self.model.id:continue
            
            self.comboBox_next_pool_id.addItem(item.name)
            self.comboBox_next_pool_id.setItemData(i+1, QtCore.QVariant(item.id))
            if self.model:
                if item.id==self.model.next_ippool:
                    self.comboBox_next_pool_id.setCurrentIndex(i+1)
            
            i+=1

        
        if self.model:
            self.lineEdit_name.setText(self.model.name)
            self.lineEdit_start_ip.setText(self.model.start_ip)
            self.lineEdit_end_ip.setText(self.model.end_ip)
            

            self.comboBox_type.setCurrentIndex(self.model.type)

            
    def accept(self):
        if self.model:
            model = self.model
        else:
            model = AttrDict()
            
        
        model.name = unicode(self.lineEdit_name.text())
        model.type = self.comboBox_type.itemData(self.comboBox_type.currentIndex()).toInt()[0]
        
        model.start_ip = unicode(self.lineEdit_start_ip.text())
        model.end_ip = unicode(self.lineEdit_end_ip.text())

        if len(model.name)==0:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не указади название пула"))
            return

            
            
        try:
            IPy.IP(str(model.start_ip))
            IPy.IP(str(model.end_ip))
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Некорректный IP адрес."))
            return
            
            
        
        if IPy.IP(str(model.end_ip))<=IPy.IP(str(model.start_ip)):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Конечный IP адрес должен быть больше первого и не равен ему"))
            return
        
        pools = self.connection.get_ippools()
        self.connection.commit()
        for pool in pools:
            if 'id' in model:
                if model.id==pool.id:continue
            if not (IPy.IP(pool.end_ip)<IPy.IP(model.start_ip) or (IPy.IP(model.end_ip)<IPy.IP(pool.start_ip))):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Новый диапазон уже входит в пул адресов %s" % pool.name))
                return
        
        model.next_ippool_id = self.comboBox_next_pool_id.itemData(self.comboBox_next_pool_id.currentIndex()).toInt()[0]         
        try:
            self.connection.ippool_save(model)
            self.connection.commit()
        except:
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Непредвиденная ошибка", unicode(u"Данные не были сохранены."))
            return 
        QtGui.QDialog.accept(self)



class PoolEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u"#", u"Название", u"Тип", u"Start IP", u"End IP", u"Количество адресов", u"Использовано", u"Осталось", u'% использования']
        initargs = {"setname":"pool_frame_header", "objname":"PoolEbsMDI", "winsize":(0,0,750,400), "wintitle":"Пулы адресов", "tablecolumns":columns}
        super(PoolEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))      
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        
    def ebsPostInit(self, initargs):
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addAction", "Добавить", "images/add.png", self.addframe), ("editAction", "Настройки", "images/open.png", self.editframe), ("delAction", "Удалить", "images/del.png", self.delete)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        self.tableWidget = tableFormat(self.tableWidget)
        
    def retranslateUI(self, initargs):
        super(PoolEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        

    
    def addframe(self):
        addf = AddPoolFrame(self.connection)
        if addf.exec_()==1:
            self.refresh()


    def delete(self):
        id=self.getSelectedId()
        if (QtGui.QMessageBox.question(self, u"Удалить пул?" , u'''Внимание! Во избежание удаления пользовательских аккаунтов, удостоверьтесь, что пользователи не используют IP адреса из этого пула.''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
            self.connection.ippool_delete(id)
            self.connection.commit()
            self.refresh()
    
        
    def editframe(self):
        try:
            model=self.connection.get_ippools(self.getSelectedId())
        except:
            model=None

        addf = AddPoolFrame(connection=self.connection, model=model)
        if addf.exec_()==1:
            self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/nas.png"))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.clearContents()
        pools = self.connection.sql("SELECT ippool.*, (SELECT count(*) FROM billservice_ipinuse as ipinuse WHERE ipinuse.pool_id=ippool.id and ipinuse.disabled is Null) as count_used FROM billservice_ippool as ippool ORDER BY ippool.name ASC")
        self.connection.commit()
        self.tableWidget.setRowCount(len(pools))
        i=0
        for pool in pools:
            self.addrow(pool.id, i,0)
            self.addrow(pool.name, i,1)
            self.addrow(poolt_types[pool.type], i,2)
            self.addrow(pool.start_ip, i,3)
            self.addrow(pool.end_ip, i,4)
            self.addrow(IPy.IP(pool.end_ip).int()+1- IPy.IP(pool.start_ip).int(), i,5)
            self.addrow(pool.count_used, i,6)
            self.addrow(IPy.IP(pool.end_ip).int()+1- IPy.IP(pool.start_ip).int()-pool.count_used, i,7)
            try:
                proc= "%.3f" % (float(pool.count_used)/float(IPy.IP(pool.end_ip).int()+1- IPy.IP(pool.start_ip).int())*100)
                self.addrow(proc, i,8)
            except:
                self.addrow(0, i,8)
            
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader(self.setname, self.tableWidget)
        #self.delNodeLocalAction()
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")

    def delNodeLocalAction(self):
        super(PoolEbs, self).delNodeLocalAction([self.delAction])
        
