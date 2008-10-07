#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import setFirstActive
from helpers import HeaderUtil
from IPy import *

class ClassEdit(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(ClassEdit, self).__init__()
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,329,186).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,329,186).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,329,186).size()))
        
        self.connection = connection
        self.connection.commit()
        self.model=model
        self.color=''


        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(160,150,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.params_groupBox = QtGui.QGroupBox(self)
        self.params_groupBox.setGeometry(QtCore.QRect(10,10,311,131))
        self.params_groupBox.setObjectName("params_groupBox")

        self.name_edit = QtGui.QLineEdit(self.params_groupBox)
        self.name_edit.setGeometry(QtCore.QRect(60,20,241,20))
        self.name_edit.setObjectName("name_edit")

        self.color_edit = QtGui.QToolButton(self.params_groupBox)
        self.color_edit.setGeometry(QtCore.QRect(164,50,131,20))
        self.color_edit.setArrowType(QtCore.Qt.NoArrow)
        self.color_edit.setObjectName("color_edit")

        self.name_label = QtGui.QLabel(self.params_groupBox)
        self.name_label.setGeometry(QtCore.QRect(6,20,48,20))
        self.name_label.setObjectName("name_label")

        self.store_edit = QtGui.QCheckBox(self.params_groupBox)
        self.store_edit.setGeometry(QtCore.QRect(60,80,271,18))
        self.store_edit.setObjectName("store_edit")

        self.passthrough_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.passthrough_checkBox.setGeometry(QtCore.QRect(60,100,271,19))
        self.passthrough_checkBox.setObjectName("passthrough_checkBox")

        self.color_label = QtGui.QLabel(self.params_groupBox)
        self.color_label.setGeometry(QtCore.QRect(60,50,101,21))
        self.color_label.setObjectName("color_label")


        self.retranslateUi()
        
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.connect(self.color_edit, QtCore.SIGNAL("clicked()"), self.setColor)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        self.setTabOrder(self.name_edit,self.color_edit)
        self.setTabOrder(self.color_edit,self.store_edit)
        self.setTabOrder(self.store_edit,self.buttonBox)
        
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Направление трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры направления", None, QtGui.QApplication.UnicodeUTF8))
        self.color_edit.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setText(QtGui.QApplication.translate("Dialog", "Хранить сырую статистику", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setText(QtGui.QApplication.translate("Dialog", "Пометить и продолжить", None, QtGui.QApplication.UnicodeUTF8))
        self.color_label.setText(QtGui.QApplication.translate("Dialog", "Цвет направления", None, QtGui.QApplication.UnicodeUTF8))
        self.name_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Название группы направлений.", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Опция позволяет сохранять всю сырую статистику в таблице billservice_rawnetflowstream базы данных.\nНе используйте эту опцию, если не уверены, зачем это вам нужно.", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Опция позволяет сохранять всю сырую статистику в таблице billservice_rawnetflowstream базы данных.\nНе используйте эту опцию, если не уверены, зачем это вам нужно.", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Пометить попавшую под одно из правил этого направления статистику и продолжить сравнивать с другими направлениями.\nДанная опция позволяет выделить из статистики, пападающей под обширные правила, отдельные записи и произвести по ним начисления трафика или использовать в определении лимитов.", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setToolTip(QtGui.QApplication.translate("Dialog", "Пометить попавшую под одно из правил этого направления статистику и продолжить сравнивать с другими направлениями.\nДанная опция позволяет выделить из статистики, пападающей под обширные правила, отдельные записи и произвести по ним начисления трафика или использовать в определении лимитов.", None, QtGui.QApplication.UnicodeUTF8))
        self.color_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Цвет направления.", None, QtGui.QApplication.UnicodeUTF8))
    def setColor(self):    
        color = QtGui.QColorDialog.getColor(QtCore.Qt.green, self)
        if color.isValid(): 
            #self.color_edit.setText(color.name())
            self.color_edit.setStyleSheet("QWidget { background-color: %s }" % color.name())
            self.color = unicode(color.name())
            #self.color_edit.setPalette(QtGui.QPalette(color))
            
    def fixtures(self):
        if self.model:
            self.name_edit.setText(self.model.name)
            self.color=unicode(self.model.color)
            self.color_edit.setStyleSheet("QWidget { background-color: %s }" % self.color)
            self.store_edit.setCheckState(self.model.store == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            self.passthrough_checkBox.setCheckState(self.model.passthrough == True and QtCore.Qt.Checked or QtCore.Qt.Unchecked )
            
            #self.store_editself.pptp_edit.checkState()==2
        
    def accept(self):
        if self.model:
            model=self.model
        else:
            print 'New class'
            model=Object()
            try:
                maxweight = self.connection.get("SELECT MAX(weight) as weight FROM nas_trafficclass;").weight+1
            except Exception, e:
                maxweight = 0
            model.weight = maxweight
            
        model.name=unicode(self.name_edit.text())
            
        model.color=self.color
           
        model.store=self.store_edit.checkState()==2
        model.passthrough = self.passthrough_checkBox.checkState()==2
        #model.save()
        try:
            self.connection.create(model.save("nas_trafficclass"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        QtGui.QDialog.accept(self)
        

class ClassNodeFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(ClassNodeFrame, self).__init__()
        self.model=model
        self.connection = connection
        self.connection.commit()
        
        self.protocols={'':0,
           'ddp':37,
           'encap':98, 
           'ggp':3, 
           'gre':47, 
           'hmp':20, 
           'icmp':1, 
           'idpr-cmtp':38, 
           'igmp':2, 
           'ipencap':4, 
           'ipip':94,  
           'ospf':89, 
           'rdp':27, 
           'tcp':6, 
           'udp':17
           }

    
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,221,356).size()).expandedTo(self.minimumSizeHint()))

        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,221,356).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,221,356).size()))        
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(50,320,160,26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10,100,201,81))
        self.groupBox.setObjectName("groupBox")

        self.src_port_edit = QtGui.QLineEdit(self.groupBox)
        self.src_port_edit.setGeometry(QtCore.QRect(60,50,127,20))
        self.src_port_edit.setObjectName("src_port_edit")

        self.src_port_label = QtGui.QLabel(self.groupBox)
        self.src_port_label.setGeometry(QtCore.QRect(10,50,46,20))
        self.src_port_label.setObjectName("src_port_label")

        self.src_ip_label = QtGui.QLabel(self.groupBox)
        self.src_ip_label.setGeometry(QtCore.QRect(11,20,46,20))
        self.src_ip_label.setObjectName("src_ip_label")

        self.src_ip_edit = QtGui.QLineEdit(self.groupBox)
        self.src_ip_edit.setGeometry(QtCore.QRect(60,20,127,20))

        self.src_ip_edit.setMaxLength(32767)
        self.src_ip_edit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.src_ip_edit.setObjectName("src_ip_edit")

        self.groupBox_2 = QtGui.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(10,190,201,80))
        self.groupBox_2.setObjectName("groupBox_2")

        self.dst_port_edit = QtGui.QLineEdit(self.groupBox_2)
        self.dst_port_edit.setGeometry(QtCore.QRect(60,50,127,20))
        self.dst_port_edit.setObjectName("dst_port_edit")

        self.dst_ip_label = QtGui.QLabel(self.groupBox_2)
        self.dst_ip_label.setGeometry(QtCore.QRect(8,20,46,20))
        self.dst_ip_label.setObjectName("dst_ip_label")

        self.dst_ip_edit = QtGui.QLineEdit(self.groupBox_2)
        self.dst_ip_edit.setGeometry(QtCore.QRect(60,20,127,20))
        self.dst_ip_edit.setObjectName("dst_ip_edit")

        self.dst_port_label = QtGui.QLabel(self.groupBox_2)
        self.dst_port_label.setGeometry(QtCore.QRect(8,50,46,20))
        self.dst_port_label.setObjectName("dst_port_label")

        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setGeometry(QtCore.QRect(70,10,131,20))
        self.name_edit.setObjectName("name_edit")

        self.next_hop_label = QtGui.QLabel(self)
        self.next_hop_label.setGeometry(QtCore.QRect(18,280,46,20))
        self.next_hop_label.setObjectName("next_hop_label")

        self.next_hop_edit = QtGui.QLineEdit(self)
        self.next_hop_edit.setGeometry(QtCore.QRect(70,280,127,20))
        self.next_hop_edit.setObjectName("next_hop_edit")

        self.name_label = QtGui.QLabel(self)
        self.name_label.setGeometry(QtCore.QRect(10,10,61,22))
        self.name_label.setObjectName("name_label")

        self.protocol_label = QtGui.QLabel(self)
        self.protocol_label.setGeometry(QtCore.QRect(10,70,61,20))
        self.protocol_label.setObjectName("protocol_label")

        self.group_label = QtGui.QLabel(self)
        self.group_label.setGeometry(QtCore.QRect(10,40,61,20))
        self.group_label.setObjectName("group_label")

        self.protocol_edit = QtGui.QComboBox(self)
        self.protocol_edit.setGeometry(QtCore.QRect(70,70,131,20))
        self.protocol_edit.setObjectName("protocol_edit")

        self.direction_edit = QtGui.QComboBox(self)
        self.direction_edit.setGeometry(QtCore.QRect(70,40,131,20))
        self.direction_edit.setObjectName("group_edit")
        
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/[0-9][0-9]?)?\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.setTabOrder(self.direction_edit,self.protocol_edit)
        self.setTabOrder(self.protocol_edit,self.src_ip_edit)
        self.setTabOrder(self.src_ip_edit,self.src_port_edit)
        self.setTabOrder(self.src_port_edit,self.dst_ip_edit)
        self.setTabOrder(self.dst_ip_edit,self.dst_port_edit)
        self.setTabOrder(self.dst_port_edit,self.next_hop_edit)
        self.setTabOrder(self.next_hop_edit,self.buttonBox)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Сеть источника", None, QtGui.QApplication.UnicodeUTF8))
        self.src_port_label.setText(QtGui.QApplication.translate("Dialog", "Src port", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_label.setText(QtGui.QApplication.translate("Dialog", "Src net", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Сеть получателя", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_ip_label.setText(QtGui.QApplication.translate("Dialog", "Dst net", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_port_label.setText(QtGui.QApplication.translate("Dialog", "Dst port", None, QtGui.QApplication.UnicodeUTF8))
        self.next_hop_label.setText(QtGui.QApplication.translate("Dialog", "Next Hop", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.protocol_label.setText(QtGui.QApplication.translate("Dialog", "Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.group_label.setText(QtGui.QApplication.translate("Dialog", "Группа", None, QtGui.QApplication.UnicodeUTF8))
        
        self.direction_edit.addItem(QtGui.QApplication.translate("Dialog", "INPUT", None, QtGui.QApplication.UnicodeUTF8))
        self.direction_edit.addItem(QtGui.QApplication.translate("Dialog", "OUTPUT", None, QtGui.QApplication.UnicodeUTF8))
        #Help Hints
        self.name_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Название поднаправления.", None, QtGui.QApplication.UnicodeUTF8))
        self.direction_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Описываемое направление трафика (Вх/Исх).", None, QtGui.QApplication.UnicodeUTF8))
        self.protocol_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Выберите протокол из списка.", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "IP/Сеть источника трафика.\n Примеры:\n192.168.1.0/24 - сеть 192.168.1.1-192.168.1.254\n192.168.1.1/32 - один IP адрес\n0.0.0.0/0 все IP адреса", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_ip_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "IP/Сеть получателя трафика.\n Примеры:\n192.168.1.0/24 - сеть 192.168.1.1-192.168.1.254\n192.168.1.1/32 - один IP адрес\n0.0.0.0/0 все IP адреса", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_port_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Порт получателя. Имеет смысл указывать только, если протокол TCP/UDP", None, QtGui.QApplication.UnicodeUTF8))        
        self.src_port_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Порт источника. Имеет смысл указывать только, если протокол TCP/UDP", None, QtGui.QApplication.UnicodeUTF8))
        self.next_hop_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Next Hop", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_edit.setValidator(self.ipValidator)
        self.dst_ip_edit.setValidator(self.ipValidator)
        self.next_hop_edit.setValidator(self.ipValidator)
        
        
        for protocol in self.protocols:
            #print protocol
            self.protocol_edit.addItem(QtGui.QApplication.translate("Dialog", protocol, None, QtGui.QApplication.UnicodeUTF8))


    def fixtures(self):
        
        if self.model:
            
            self.name_edit.setText(unicode(self.model.name))
            self.direction_edit.setCurrentIndex(self.direction_edit.findText(self.model.direction, QtCore.Qt.MatchCaseSensitive)),
            self.src_ip_edit.setText(unicode(self.model.src_ip))
            #self.src_mask_edit.setText(unicode(self.model.src_mask))
            self.src_port_edit.setText(unicode(self.model.src_port or 0))
            self.dst_ip_edit.setText(unicode(self.model.dst_ip))
            #self.dst_mask_edit.setText(unicode(self.model.dst_mask))
            self.dst_port_edit.setText(unicode(self.model.dst_port or 0))
            #self.protocol_edit.setCurrentIndex(self.protocol_edit.findText(self.protocols[self.model.protocol], QtCore.Qt.MatchCaseSensitive)),
            self.next_hop_edit.setText(unicode(self.model.next_hop))
        else:
            default=u'0.0.0.0'
            self.src_ip_edit.setText(default)
            #self.src_mask_edit.setText(default)            
            self.dst_ip_edit.setText(default)
            #self.dst_mask_edit.setText(default)
            self.next_hop_edit.setText(default)                                       


    def accept(self):
        
        if self.model:
            model = self.model
        else:
            model = Object()
            
        model.name = unicode(self.name_edit.text())
        model.direction = unicode(self.direction_edit.currentText())
        
        model.protocol = self.protocols[unicode(self.protocol_edit.currentText())]
        
        src_ip = unicode(self.src_ip_edit.text())
        if src_ip:
            print src_ip
            print self.ipValidator.validate(src_ip, 0)
            if self.ipValidator.validate(src_ip, 0)[0] != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите Src IP до конца."))
                return
        else:
            src_ip='0.0.0.0/0'
        
        model.src_ip = src_ip
            

        try:
            IP("%s" % (model.src_ip))
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Неправильное сочетание SRC IP/Mask."))
            return

        
        dst_ip = unicode(self.dst_ip_edit.text())
        if dst_ip:
            if self.ipValidator.validate(dst_ip, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность DST IP."))
                return
        else:
            src_mask='0.0.0.0/0'
        model.dst_ip = dst_ip
        
        try:
            IP("%s" % (model.dst_ip))
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Неправильное сочетание DST IP/Mask."))
            return
                    
        src_port = unicode(self.src_port_edit.text())
           
        model.src_port = src_port or 0
        
        dst_port = unicode(self.dst_port_edit.text())

        model.dst_port = dst_port or 0
        
        next_hop = unicode(self.next_hop_edit.text())
        
        if next_hop:
            if self.ipValidator.validate(next_hop, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность Next Hop."))
                return
        else:
            next_hop = '0.0.0.0'
        
        model.next_hop = next_hop
        self.model=model
        QtGui.QDialog.accept(self)


class ClassChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        super(ClassChild, self).__init__()
        self.connection = connection
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.protocols={'0':'-all-',
           '37':'ddp',
           '98':'encap', 
           '3':'ggp', 
           '47':'gre', 
           '20':'hmp', 
           '1':'icmp', 
           '38':'idpr-cmtp', 
           '2':'igmp', 
           '4':'ipencap', 
           '94':'ipip',  
           '89':'ospf', 
           '27':'rdp', 
           '6':'tcp', 
           '17':'udp'
           }
        self.setObjectName("ClassMDI")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,795,597).size()).expandedTo(self.minimumSizeHint()))

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setGeometry(QtCore.QRect(0,0,200,521))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.treeWidget.setColumnCount(2)

        self.treeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        tree_header = self.treeWidget.headerItem()
        hght = self.tableWidget.horizontalHeader().maximumHeight()
        sz = QtCore.QSize()
        sz.setHeight(hght)
        tree_header.setSizeHint(0,sz)
        tree_header.setSizeHint(1,sz)
        tree_header.setText(0,QtGui.QApplication.translate("MainWindow", "Направления", None, QtGui.QApplication.UnicodeUTF8))
        tree_header.setText(1,QtGui.QApplication.translate("MainWindow", "Цвет", None, QtGui.QApplication.UnicodeUTF8))
        wwidth =  self.width()
        self.splitter.setSizes([wwidth / 5, wwidth - (wwidth / 5)])
        #self.splitter.moveSplitter(150, 0)
        
        self.setCentralWidget(self.splitter)
        #self.setCentralWidget(self.splitterHandle)

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,800,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.addClassAction = QtGui.QAction(self)
        self.addClassAction.setIcon(QtGui.QIcon("images/folder_add.png"))
        self.addClassAction.setObjectName("addClassAction")

        self.delClassAction = QtGui.QAction(self)
        self.delClassAction.setIcon(QtGui.QIcon("images/folder_delete.png"))
        self.delClassAction.setObjectName("delClassAction")
        self.editClassAction = QtGui.QAction(self)
        self.editClassAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editClassAction.setObjectName("editClassAction")

        self.addClassNodeAction = QtGui.QAction(self)
        self.addClassNodeAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addClassNodeAction.setObjectName("addClassNodeAction")

        self.delClassNodeAction = QtGui.QAction(self)
        self.delClassNodeAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delClassNodeAction.setObjectName("delClassNodeAction")
        
        self.editClassNodeAction = QtGui.QAction(self)
        self.editClassNodeAction.setIcon(QtGui.QIcon("images/open.png"))
        self.editClassNodeAction.setObjectName("editClassNodeAction")
        
        #Up Class
        self.upClassAction = QtGui.QAction(self)
        self.upClassAction.setIcon(QtGui.QIcon("images/up.png"))
        self.upClassAction.setObjectName("delClassNodeAction")
               
        #Down Class
        self.downClassAction = QtGui.QAction(self)
        self.downClassAction.setIcon(QtGui.QIcon("images/down.png"))
        self.downClassAction.setObjectName("delClassNodeAction")
        
        self.toolBar.addAction(self.addClassAction)
        self.toolBar.addAction(self.delClassAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.upClassAction)
        self.toolBar.addAction(self.downClassAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.addClassNodeAction)
        self.toolBar.addAction(self.delClassNodeAction)

        
        
        self.retranslateUi()
        
        self.treeWidget.addAction(self.editClassAction)
        self.treeWidget.addAction(self.addClassAction)
        self.treeWidget.addAction(self.delClassAction)

        
        self.tableWidget.addAction(self.editClassNodeAction)
        self.tableWidget.addAction(self.addClassNodeAction)
        self.tableWidget.addAction(self.delClassNodeAction)
        
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.addClassAction, QtCore.SIGNAL("triggered()"), self.addClass)
        self.connect(self.delClassAction, QtCore.SIGNAL("triggered()"), self.delClass)
        
        self.connect(self.upClassAction, QtCore.SIGNAL("triggered()"), self.upClass)
        self.connect(self.downClassAction, QtCore.SIGNAL("triggered()"), self.downClass)

        self.connect(self.addClassNodeAction, QtCore.SIGNAL("triggered()"), self.addNode)
        self.connect(self.delClassNodeAction, QtCore.SIGNAL("triggered()"), self.delNode)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editClass)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refreshTable)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        
        
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        self.connect(self.editClassAction, QtCore.SIGNAL("triggered()"), self.editClass)
        self.connect(self.editClassNodeAction, QtCore.SIGNAL("triggered()"), self.editNode)
        self.refresh_list()
        try:
            setFirstActive(self.treeWidget)
            HeaderUtil.nullifySaved("class_frame_header")
            self.refreshTable()
        except Exception, ex:
            print "Error in setting first element active: ",ex
            
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.delNodeLocalAction()
        self.addNodeLocalAction()

    
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Направления трафика", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tableWidget.clear()        
        columns = ['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Next Hop']
        makeHeaders(columns, self.tableWidget)

        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassAction.setText(QtGui.QApplication.translate("MainWindow", "Add class", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Add Node", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class Node", None, QtGui.QApplication.UnicodeUTF8))
        self.editClassAction.setText(QtGui.QApplication.translate("MainWindow", "Edit Class", None, QtGui.QApplication.UnicodeUTF8))
        self.editClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Edit Node", None, QtGui.QApplication.UnicodeUTF8))
        
        

    def addClass(self):
        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        child=ClassEdit(connection=self.connection)
        if child.exec_()==1:
            self.refresh_list()
        
    
    def editClass(self, *args, **kwargs):
        
        try:
            model=self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % self.treeWidget.currentItem().id)
        except Exception, e:
            print e
        
        child=ClassEdit(connection=self.connection, model=model)
        
        if child.exec_()==1:
            self.refresh_list()
            
    def delClass(self):
        
        model = self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % self.getClassId())
        
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить класс трафика?" , u"Удалить класс трафика?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                
                #self.connection.delete("DELETE FROM nas_trafficnode WHERE traffic_class_id=%d" % model.id)
                self.connection.delete("DELETE FROM nas_trafficclass WHERE id=%d" % model.id)
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()

            self.refresh_list()
            
            try:
                setFirstActive(self.treeWidget)
                self.refreshTable()
            except Exception, ex:
                print ex
        
        
    def savePosition(self, direction):
        item_changed_id = self.treeWidget.currentItem().id
        #print "item_changed_id", item_changed_id 
        
        if direction == u"up":
            item_swap_id = self.treeWidget.topLevelItem(self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())+1).id
        elif direction == u"down":
            item_swap_id = self.treeWidget.topLevelItem(self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())-1).id
            
        print "item_swap_id=", item_swap_id
        
        model1 = self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % item_changed_id)
        model2 = self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % item_swap_id)
        print model1.name, model2.name
        a=model1.weight+0
        b=model2.weight+0
        print "a,b", a,b, model1.id, model2.id
        model1.weight=1000001
        try:
            
            self.connection.create(model1.save("nas_trafficclass"))
            
            model2.weight=a
            model1.weight=b
            
            self.connection.create(model2.save("nas_trafficclass"))
            
            self.connection.create(model1.save("nas_trafficclass"))
            
            #self.connection.create(model2.save("nas_trafficclass"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        
        #self.refresh_list()
            

    
    def upClass(self):
        index=self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())
        if index==0:
            return
        item = self.treeWidget.takeTopLevelItem(index)
        self.treeWidget.insertTopLevelItem(index-1,item)
        self.treeWidget.setCurrentItem(item)
        self.savePosition(direction=u"up")
        #pass
    


    def downClass(self):
        index=self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())
        print "index, self.treeWidget.topLevelItemCount()", index, self.treeWidget.topLevelItemCount()
        if index==self.treeWidget.topLevelItemCount()-1:
            return
        
        item = self.treeWidget.takeTopLevelItem(index)
        self.treeWidget.insertTopLevelItem(index+1,item)
        self.treeWidget.setCurrentItem(item)
        self.savePosition(direction=u"down")
        
    def refresh_list(self):
        curItem = -1
        try:
            curItem = self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem())
        except Exception, ex:
            print ex
        self.treeWidget.clear()
        classes=self.connection.sql(" SELECT * FROM nas_trafficclass ORDER BY weight ASC;")
        
        for clas in classes:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.id = clas.id
            item.setText(0, clas.name)
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            item.setBackgroundColor(1, QtGui.QColor(clas.color))
            if clas.passthrough==True:
                item.setIcon(1, QtGui.QIcon("images/down.png"))
            
        if curItem != -1:
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(curItem))


    def addNode(self):

        try:
            model=self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % self.getClassId())
        except Exception, e:
            print e

        child=ClassNodeFrame(connection = self.connection)
        if child.exec_()==1:
            child.model.traffic_class_id=model.id
            try:
                self.connection.create(child.model.save("nas_trafficnode"))
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
            
            self.refreshTable()
        
    def delNode(self):
        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                self.connection.delete("DELETE FROM nas_trafficnode WHERE id=%d" % self.getSelectedId())
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
            self.refreshTable()
        
    def editNode(self):
        try:
            model=self.connection.get("SELECT * FROM nas_trafficnode WHERE id=%d" % self.getSelectedId())
        except Exception, e:
            print e
            #return
        
        
        child=ClassNodeFrame(connection=self.connection, model=model)
        if child.exec_()==1:
            try:
                self.connection.create(child.model.save("nas_trafficnode"))
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
            self.refreshTable()
        
    def refreshTable(self, widget=None):
        self.tableWidget.setSortingEnabled(False)
        if not widget:
            class_id=self.getClassId()
        else:
            class_id=widget.id
        self.tableWidget.clearContents()
        #print text
        model = self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % class_id)
        nodes = self.connection.sql("SELECT * FROM nas_trafficnode WHERE traffic_class_id=%d ORDER BY id" % model.id)

        self.tableWidget.setRowCount(len(nodes))
        
        i=0        
        #['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src mask', 'Src Port', 'Dst IP', 'Dst Mask', 'Dst Port', 'Next Hop']
        for node in nodes:

            self.addrow(node.id, i,0)
            self.addrow(node.name, i,1)
            self.addrow(node.direction, i,2)
            self.addrow(node.protocol, i,3)
            self.addrow(node.src_ip, i,4)
            self.addrow(node.src_port, i,5)
            
            self.addrow(node.dst_ip, i,6)
            self.addrow(node.dst_port, i,7)
            self.addrow(node.next_hop, i,8)
            #self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)

            i+=1
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader("class_frame_header", self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getClassId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y):
        if value==None:
            value=""
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tc.png"))
            
        self.tableWidget.setItem(x,y,headerItem)
    def saveHeader(self, *args):
        HeaderUtil.saveHeader("class_frame_header", self.tableWidget)

    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delClassNodeAction.setDisabled(True)
        else:
            self.delClassNodeAction.setDisabled(False)


    def addNodeLocalAction(self):
        if self.treeWidget.currentItem() is None:
            self.addClassNodeAction.setDisabled(True)
            self.delClassAction.setDisabled(True)
            self.upClassAction.setDisabled(True)
            self.downClassAction.setDisabled(True)
        else:
            self.addClassNodeAction.setDisabled(False)
            self.delClassAction.setDisabled(False)
            self.upClassAction.setDisabled(False)
            self.downClassAction.setDisabled(False)
                        

