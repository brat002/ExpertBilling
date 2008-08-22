#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders

class ClassEdit(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(ClassEdit, self).__init__()
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,346,106).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,346,106).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,346,106).size()))
        
        self.connection = connection
        self.connection.commit()
        self.model=model
        self.color=''

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(180,70,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setGeometry(QtCore.QRect(65,21,241,20))
        self.name_edit.setObjectName("name_edit")

        self.name_label = QtGui.QLabel(self)
        self.name_label.setGeometry(QtCore.QRect(11,21,48,20))
        self.name_label.setObjectName("name_label")

        self.color_edit = QtGui.QPushButton(self)
        self.color_edit.setGeometry(QtCore.QRect(310,20,25,20))
        self.color_edit.setObjectName("color_edit")

        self.store_edit = QtGui.QCheckBox(self)
        self.store_edit.setGeometry(QtCore.QRect(60,50,151,18))
        self.store_edit.setObjectName("store_edit")

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
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.color_edit.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setText(QtGui.QApplication.translate("Dialog", "Хранить всю статистику", None, QtGui.QApplication.UnicodeUTF8))
    
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
            
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,247,328).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,247,328).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,247,328).size()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(80,290,160,26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        
        self.buttonBox.setObjectName("buttonBox")

        self.layoutWidget = QtGui.QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(10,10,181,265))
        self.layoutWidget.setObjectName("layoutWidget")

        self.gridlayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridlayout.setObjectName("gridlayout")

        self.name_label = QtGui.QLabel(self.layoutWidget)
        self.name_label.setObjectName("name_label")
        self.gridlayout.addWidget(self.name_label,0,0,1,1)

        self.name_edit = QtGui.QLineEdit(self.layoutWidget)

        font = QtGui.QFont()
        font.setFamily("MS Reference Sans Serif")
        self.name_edit.setFont(font)
        self.name_edit.setObjectName("name_edit")
        self.gridlayout.addWidget(self.name_edit,0,1,1,2)

        self.group_label = QtGui.QLabel(self.layoutWidget)
        self.group_label.setObjectName("group_label")
        self.gridlayout.addWidget(self.group_label,1,0,1,1)

        self.direction_edit = QtGui.QComboBox(self.layoutWidget)
        self.direction_edit.setObjectName("direction_edit")
        self.gridlayout.addWidget(self.direction_edit,1,1,1,2)

        self.src_ip_label = QtGui.QLabel(self.layoutWidget)
        self.src_ip_label.setObjectName("src_ip_label")
        self.gridlayout.addWidget(self.src_ip_label,2,0,1,1)

        self.src_ip_edit = QtGui.QLineEdit(self.layoutWidget)

        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(8)
        self.src_ip_edit.setFont(font)
        self.src_ip_edit.setMaxLength(15)
        self.src_ip_edit.setFrame(True)
        self.src_ip_edit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.src_ip_edit.setObjectName("src_ip_edit")
        self.gridlayout.addWidget(self.src_ip_edit,2,1,1,2)

        self.src_mask_label = QtGui.QLabel(self.layoutWidget)
        self.src_mask_label.setObjectName("src_mask_label")
        self.gridlayout.addWidget(self.src_mask_label,3,0,1,1)

        self.src_mask_edit = QtGui.QLineEdit(self.layoutWidget)
        self.src_mask_edit.setObjectName("src_mask_edit")
        self.gridlayout.addWidget(self.src_mask_edit,3,1,1,2)

        self.dst_ip_label = QtGui.QLabel(self.layoutWidget)
        self.dst_ip_label.setObjectName("dst_ip_label")
        self.gridlayout.addWidget(self.dst_ip_label,4,0,1,1)

        self.dst_ip_edit = QtGui.QLineEdit(self.layoutWidget)
        self.dst_ip_edit.setObjectName("dst_ip_edit")
        self.gridlayout.addWidget(self.dst_ip_edit,4,1,1,2)

        self.dst_mask_label = QtGui.QLabel(self.layoutWidget)
        self.dst_mask_label.setObjectName("dst_mask_label")
        self.gridlayout.addWidget(self.dst_mask_label,5,0,1,1)

        self.dst_mask_edit = QtGui.QLineEdit(self.layoutWidget)
        self.dst_mask_edit.setObjectName("dst_mask_edit")
        self.gridlayout.addWidget(self.dst_mask_edit,5,1,1,2)

        self.protocol_label = QtGui.QLabel(self.layoutWidget)
        self.protocol_label.setObjectName("protocol_label")
        self.gridlayout.addWidget(self.protocol_label,6,0,1,1)

        self.protocol_edit = QtGui.QComboBox(self.layoutWidget)
        self.protocol_edit.setObjectName("protocol_edit")
        self.gridlayout.addWidget(self.protocol_edit,6,1,1,2)

        self.src_port_label = QtGui.QLabel(self.layoutWidget)
        self.src_port_label.setObjectName("src_port_label")
        self.gridlayout.addWidget(self.src_port_label,7,0,1,1)

        self.src_port_edit = QtGui.QLineEdit(self.layoutWidget)
        self.src_port_edit.setObjectName("src_port_edit")
        self.gridlayout.addWidget(self.src_port_edit,7,1,1,2)

        self.dst_port_label = QtGui.QLabel(self.layoutWidget)
        self.dst_port_label.setObjectName("dst_port_label")
        self.gridlayout.addWidget(self.dst_port_label,8,0,1,1)

        self.dst_port_edit = QtGui.QLineEdit(self.layoutWidget)
        self.dst_port_edit.setObjectName("dst_port_edit")
        self.gridlayout.addWidget(self.dst_port_edit,8,1,1,2)
        
        self.src_validator=QtGui.QIntValidator(self.src_port_edit)
        self.src_port_edit.setValidator(self.src_validator)
        
        self.dst_validator=QtGui.QIntValidator(self.dst_port_edit)
        self.dst_port_edit.setValidator(self.dst_validator)


        self.next_hop_label = QtGui.QLabel(self.layoutWidget)
        self.next_hop_label.setObjectName("next_hop_label")
        self.gridlayout.addWidget(self.next_hop_label,9,0,1,1)

        self.next_hop_edit = QtGui.QLineEdit(self.layoutWidget)
        self.next_hop_edit.setObjectName("next_hop_edit")
        self.gridlayout.addWidget(self.next_hop_edit,9,1,1,2)

        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.name_edit.setText(QtGui.QApplication.translate("Dialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.group_label.setText(QtGui.QApplication.translate("Dialog", "Group", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_label.setText(QtGui.QApplication.translate("Dialog", "Src IP", None, QtGui.QApplication.UnicodeUTF8))
        #self.src_ip_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        #self.src_ip_edit.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_edit.setValidator(self.ipValidator)
        #self.src_ip_edit.setText('0.0.0.0')
        self.src_mask_label.setText(QtGui.QApplication.translate("Dialog", "Src mask", None, QtGui.QApplication.UnicodeUTF8))
        #self.src_mask_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.src_mask_edit.setValidator(self.ipValidator)
        #self.src_mask_edit.setText('0.0.0.0')
        self.dst_ip_label.setText(QtGui.QApplication.translate("Dialog", "Dst-IP", None, QtGui.QApplication.UnicodeUTF8))
        #self.dst_ip_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_ip_edit.setValidator(self.ipValidator)
        #self.dst_ip_edit.setText('0.0.0.0')
        self.dst_mask_label.setText(QtGui.QApplication.translate("Dialog", "Dst mask", None, QtGui.QApplication.UnicodeUTF8))
        #self.dst_mask_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_mask_edit.setValidator(self.ipValidator)
        #self.dst_mask_edit.setText('0.0.0.0')
        self.protocol_label.setText(QtGui.QApplication.translate("Dialog", "Protocol", None, QtGui.QApplication.UnicodeUTF8))
        self.src_port_label.setText(QtGui.QApplication.translate("Dialog", "Src port", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_port_label.setText(QtGui.QApplication.translate("Dialog", "Dst port", None, QtGui.QApplication.UnicodeUTF8))
        self.next_hop_label.setText(QtGui.QApplication.translate("Dialog", "Next Hop", None, QtGui.QApplication.UnicodeUTF8))
        #self.next_hop_edit.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000;   ", None, QtGui.QApplication.UnicodeUTF8))
        self.next_hop_edit.setValidator(self.ipValidator)
        #self.next_hop_edit.setText('0.0.0.0')
        
        self.direction_edit.addItem(QtGui.QApplication.translate("Dialog", "INPUT", None, QtGui.QApplication.UnicodeUTF8))
        self.direction_edit.addItem(QtGui.QApplication.translate("Dialog", "OUTPUT", None, QtGui.QApplication.UnicodeUTF8))
        
        for protocol in self.protocols:
            #print protocol
            self.protocol_edit.addItem(QtGui.QApplication.translate("Dialog", protocol, None, QtGui.QApplication.UnicodeUTF8))


    def fixtures(self):
        
        if self.model:
            
            self.name_edit.setText(unicode(self.model.name))
            self.direction_edit.setCurrentIndex(self.direction_edit.findText(self.model.direction, QtCore.Qt.MatchCaseSensitive)),
            self.src_ip_edit.setText(unicode(self.model.src_ip))
            self.src_mask_edit.setText(unicode(self.model.src_mask))
            self.src_port_edit.setText(unicode(self.model.src_port or 0))
            self.dst_ip_edit.setText(unicode(self.model.dst_ip))
            self.dst_mask_edit.setText(unicode(self.model.dst_mask))
            self.dst_port_edit.setText(unicode(self.model.dst_port or 0))
            #self.protocol_edit.setCurrentIndex(self.protocol_edit.findText(self.protocols[self.model.protocol], QtCore.Qt.MatchCaseSensitive)),
            self.next_hop_edit.setText(unicode(self.model.next_hop))

                                       

            
    


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
            src_ip='0.0.0.0'
        
        model.src_ip = src_ip
            
        src_mask = unicode(self.src_mask_edit.text())
        
        if src_mask:
            if self.ipValidator.validate(src_mask, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите Src Mask до конца."))
                return
        else:
            src_mask= '0.0.0.0'
            
        model.src_mask = src_mask
            
        dst_ip = unicode(self.dst_ip_edit.text())
        if dst_ip:
            if self.ipValidator.validate(dst_ip, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите Dst Ip до конца."))
                return
        else:
            src_mask='0.0.0.0'
        model.dst_ip = dst_ip
        
        dst_mask = unicode(self.dst_mask_edit.text())
        if dst_mask:
            if self.ipValidator.validate(dst_mask, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите Dst Mask до конца."))
                return
        else:
            dst_mask='0.0.0.0'

        model.dst_mask = dst_mask
            
        src_port = unicode(self.src_port_edit.text())
           
        model.src_port = src_port or 0
        
        dst_port = unicode(self.dst_port_edit.text())

        model.dst_port = dst_port or 0
        
        next_hop = unicode(self.next_hop_edit.text())
        
        if next_hop:
            if self.ipValidator.validate(next_hop, 0)[0]  != QtGui.QValidator.Acceptable:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите Next Hop до конца."))
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
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,800,597).size()).expandedTo(self.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(157,1,16,519))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(0,0,2,2))
        self.widget.setObjectName("widget")

        self.hboxlayout = QtGui.QHBoxLayout(self.widget)
        self.hboxlayout.setObjectName("hboxlayout")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0,0,800,521))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.treeWidget.setColumnCount(2)
        tree_header = self.treeWidget.headerItem()
        tree_header.setHidden(True)
        
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        self.splitterHandle = self.splitter.createHandle()
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

        self.addClassAction = QtGui.QAction(self)
        self.addClassAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addClassAction.setObjectName("addClassAction")

        self.delClassAction = QtGui.QAction(self)
        self.delClassAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delClassAction.setObjectName("delClassAction")

        self.addClassNodeAction = QtGui.QAction(self)
        self.addClassNodeAction.setIcon(QtGui.QIcon("images/add.png"))
        self.addClassNodeAction.setObjectName("addClassNodeAction")

        self.delClassNodeAction = QtGui.QAction(self)
        self.delClassNodeAction.setIcon(QtGui.QIcon("images/del.png"))
        self.delClassNodeAction.setObjectName("delClassNodeAction")
        
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
        self.toolBar.addAction(self.addClassNodeAction)
        self.toolBar.addAction(self.delClassNodeAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.upClassAction)
        self.toolBar.addAction(self.downClassAction)
        
        
        self.retranslateUi()
        
        self.tableWidget.addAction(self.addClassNodeAction)
        self.tableWidget.addAction(self.delClassNodeAction)
        
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
        
        self.refresh_list()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.delNodeLocalAction()
        self.addNodeLocalAction()

    
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Направления трафика", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tableWidget.clear()        
        columns = ['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src mask', 'Src Port', 'Dst IP', 'Dst Mask', 'Dst Port', 'Next Hop']
        makeHeaders(columns, self.tableWidget)

        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassAction.setText(QtGui.QApplication.translate("MainWindow", "Add class", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Add Node", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class Node", None, QtGui.QApplication.UnicodeUTF8))


    def addClass(self):
        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        child=ClassEdit(connection=self.connection)
        if child.exec_()==1:
            self.refresh_list()
        
    
    def editClass(self, item, index):
        
        try:
            model=self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % item.id)
        except Exception, e:
            print e
        
        child=ClassEdit(connection=self.connection, model=model)
        
        if child.exec_()==1:
            self.refresh_list()
            
    def delClass(self):
        
        model = self.connection.get("SELECT * FROM nas_trafficclass WHERE id=%d" % self.getClassId())
        
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить класс трафика?" , u"Удалить класс трафика?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                
                self.connection.delete("DELETE FROM nas_trafficnode WHERE traffic_class_id=%d" % model.id)
                self.connection.delete("DELETE FROM nas_trafficclass WHERE id=%d" % model.id)
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()

            self.refresh_list()
        
        
    def savePosition(self, direction):
        item_changed_id = self.treeWidget.currentItem().id
        print "item_changed_id", item_changed_id 
        
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
        self.treeWidget.clear()
        classes=self.connection.sql(" SELECT * FROM nas_trafficclass ORDER BY weight ASC;")
        
        for clas in classes:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.id = clas.id
            item.setText(0, clas.name)
            
            item.setBackgroundColor(1, QtGui.QColor(clas.color))


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
            self.addrow(node.src_mask, i,5)
            self.addrow(node.src_port, i,6)
            
            self.addrow(node.dst_ip, i,7)
            self.addrow(node.dst_mask, i,8)
            self.addrow(node.dst_port, i,9)
            self.addrow(node.next_hop, i,10)
            self.tableWidget.setRowHeight(i, 17)
            self.tableWidget.setColumnHidden(0, True)

            i+=1
        self.tableWidget.resizeColumnsToContents()
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getClassId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y):
        if value==None:
            value=""
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)

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
                        

