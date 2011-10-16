#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import setFirstActive
from helpers import HeaderUtil, SplitterUtil
from ebsWindow import ebsTable_n_TreeWindow
from IPy import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class NetworksImportDialog(QtGui.QDialog):
    def __init__(self, class_id, connection):
        super(NetworksImportDialog, self).__init__()
        self.setObjectName("NetworksImportDialog")
        self.connection = connection
        self.connection.commit()
        self.class_id = class_id
        
        self.resize(467, 543)
        
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.toolButton = QtGui.QToolButton(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/folder1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 2)
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 2, 0, 1, 3)
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)
        self.plainTextEdit = QtGui.QPlainTextEdit(self)
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 150))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 4, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.toolButton, QtCore.SIGNAL("clicked()"), self.importNetworks)
        #QtCore.QMetaObject.connectSlotsByName()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Импорт списка сетей", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Путь к файлу(формат: Имя сети|Сеть)", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Импортируемые сетиисточники)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Связаные сети(получатели)", None, QtGui.QApplication.UnicodeUTF8))
        self.plainTextEdit.setPlainText("0.0.0.0/0")
        
        columns = [u'Импортировать', u"Название сети", u"Сеть"]
        makeHeaders(columns, self.tableWidget)
        
    def detect_delimeter(self, line):
		if line.rfind('|')!=-1:
			return "|"
		elif line.rfind(',')!=-1:
			return ","
		elif line.rfind(';')!=-1:
			return ';'
		else:
			return ' '
			
    def importNetworks(self):
        
        fileName = str(QtGui.QFileDialog.getOpenFileName(self,
                                          u"Выберите файл со списком сетей", unicode(self.lineEdit.text()), "TXT Files (*.txt)"))
        if fileName=="":
            return
		
        try:
			fileName=fileName.decode('mbcs')
        except Exception, e:
            print e
			
        self.lineEdit.setText(fileName)
        f = open(fileName, "r")
        
        self.tableWidget.clearContents()
        filedata = f.readlines()
        f.close()
        i=0
        for info in filedata:
            try:
                delimeter=self.detect_delimeter(info)
                print delimeter
                line = info.strip().split(delimeter)
                if not line: continue
                if len(line)==1:
                    name, net = line[0], line[0]
                elif len(line)==2:
                    name, net = line[0:2]
                else:
                    continue
                self.tableWidget.insertRow(i)
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Указанный файл имеет неправильный формат(Имя сети|Адрес сети).\n %s" % info))
                return 
            #print name, net
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Checked)
            self.tableWidget.setItem(i, 0,item)
            item = QtGui.QTableWidgetItem()
            item.setText(unicode(name).strip())
            self.tableWidget.setItem(i, 1,item)
            
            item = QtGui.QTableWidgetItem()
            item.setText(unicode(net).strip())
            self.tableWidget.setItem(i, 2,item)

            i+=1
        self.tableWidget.resizeColumnsToContents()
        
    def accept(self):
        nodes = self.connection.get_class_nodes(self.class_id)
        self.connection.commit()
        nodes = [(s.src_ip, s.dst_ip) for s in nodes]
        
        local_nets_text = unicode(self.plainTextEdit.toPlainText()).strip()
        
        local_nets = local_nets_text.split("\n")
        print "local_nets", local_nets
        print 'nodes', nodes
        for l in local_nets:
            try:
                IP("%s" % (l))
            except:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность указания сети %s" % l))
                return
                
        
        n = self.tableWidget.rowCount()
        
        for x in xrange(n):
            if self.tableWidget.item(x, 0).checkState()==QtCore.Qt.Unchecked: continue
            net_name = unicode(self.tableWidget.item(x, 1).text())
            net = unicode(self.tableWidget.item(x, 2).text())
            nn = "%s" % net_name
            for l in local_nets:
                if (net, l) not in nodes: 
                    #self.connection.create_class_node(class_id, name, src_net, dst_net)
                    print 'input', (net, l)
                    self.connection.create_class_node(class_id=self.class_id, name=nn, direction='INPUT', src_net=net, dst_net=l)
                if (l, net) not in nodes:
                    #Создать ноду
                    print "output", (l, net)
                    self.connection.create_class_node(class_id=self.class_id, name = nn, direction='OUTPUT', src_net=l, dst_net=net)
                self.connection.commit()
                
        QtGui.QDialog.accept(self)
        
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
        #self.store_edit.setDisabled(True)
        
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
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Класс трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры класса", None, QtGui.QApplication.UnicodeUTF8))
        self.color_edit.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setText(QtGui.QApplication.translate("Dialog", "Хранить сырую статистику", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setText(QtGui.QApplication.translate("Dialog", "Пометить и продолжить", None, QtGui.QApplication.UnicodeUTF8))
        self.color_label.setText(QtGui.QApplication.translate("Dialog", "Цвет класса", None, QtGui.QApplication.UnicodeUTF8))
        self.name_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Название класса.", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setWhatsThis(QtGui.QApplication.translate("Dialog", "Опция позволяет сохранять всю СЫРУЮ статистику в таблице billservice_rawnetflowstream базы данных.\nНе используйте эту опцию, если не уверены, зачем это вам нужно.", None, QtGui.QApplication.UnicodeUTF8))
        self.store_edit.setToolTip(QtGui.QApplication.translate("Dialog", "Опция позволяет сохранять всю сырую статистику в таблице billservice_rawnetflowstream базы данных.\nНе используйте эту опцию, если не уверены, зачем это вам нужно.", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setWhatsThis(QtGui.QApplication.translate("Dialog", "Пометить попавшую под одно из правил этого класса статистику и продолжить сравнивать с другими направлениями.\nДанная опция позволяет выделить из статистики, пападающей под обширные правила, отдельные записи и произвести по ним начисления трафика или использовать в определении квот.", None, QtGui.QApplication.UnicodeUTF8))
        self.passthrough_checkBox.setToolTip(QtGui.QApplication.translate("Dialog", "Пометить попавшую под одно из правил этого класса статистику и продолжить сравнивать с другими направлениями.\nДанная опция позволяет выделить из статистики, пападающей под обширные правила, отдельные записи и произвести по ним начисления трафика или использовать в определении квот.", None, QtGui.QApplication.UnicodeUTF8))
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
            
            #self.store_edit.checkState()==2
        
    def accept(self):
        if unicode(self.name_edit.text())=="":
            QtGui.QMessageBox.warning(self, u"Внимание!", unicode(u"Не указано название класса"))
            return
            
        if self.model:
            model=self.model
        else:
            #print 'New class'
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
            self.connection.save(model,"nas_trafficclass")
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

    
        
        self.resize(443, 327)

        self.gridLayout_3 = QtGui.QGridLayout(self)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.name_label = QtGui.QLabel(self)
        self.name_label.setObjectName(_fromUtf8("name_label"))
        self.gridLayout_3.addWidget(self.name_label, 0, 0, 1, 1)
        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setObjectName(_fromUtf8("name_edit"))
        self.gridLayout_3.addWidget(self.name_edit, 0, 1, 1, 2)
        self.group_label = QtGui.QLabel(self)
        self.group_label.setObjectName(_fromUtf8("group_label"))
        self.gridLayout_3.addWidget(self.group_label, 1, 0, 1, 1)
        self.group_edit = QtGui.QComboBox(self)
        self.group_edit.setObjectName(_fromUtf8("group_edit"))
        self.gridLayout_3.addWidget(self.group_edit, 1, 1, 1, 2)
        self.protocol_label = QtGui.QLabel(self)
        self.protocol_label.setObjectName(_fromUtf8("protocol_label"))
        self.gridLayout_3.addWidget(self.protocol_label, 2, 0, 1, 1)
        self.protocol_edit = QtGui.QComboBox(self)
        self.protocol_edit.setObjectName(_fromUtf8("protocol_edit"))
        self.gridLayout_3.addWidget(self.protocol_edit, 2, 1, 1, 2)
        self.groupBox_src = QtGui.QGroupBox(self)
        self.groupBox_src.setObjectName(_fromUtf8("groupBox_src"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_src)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.src_ip_label = QtGui.QLabel(self.groupBox_src)
        self.src_ip_label.setObjectName(_fromUtf8("src_ip_label"))
        self.gridLayout.addWidget(self.src_ip_label, 0, 0, 1, 1)
        self.src_ip_edit = QtGui.QLineEdit(self.groupBox_src)
        self.src_ip_edit.setObjectName(_fromUtf8("src_ip_edit"))
        self.gridLayout.addWidget(self.src_ip_edit, 0, 1, 1, 2)
        self.src_port_label = QtGui.QLabel(self.groupBox_src)
        self.src_port_label.setObjectName(_fromUtf8("src_port_label"))
        self.gridLayout.addWidget(self.src_port_label, 1, 0, 1, 1)
        self.src_port_edit = QtGui.QLineEdit(self.groupBox_src)
        self.src_port_edit.setObjectName(_fromUtf8("src_port_edit"))
        self.gridLayout.addWidget(self.src_port_edit, 1, 1, 1, 2)
        self.label_snmp_in = QtGui.QLabel(self.groupBox_src)
        self.label_snmp_in.setObjectName(_fromUtf8("label_snmp_in"))
        self.gridLayout.addWidget(self.label_snmp_in, 2, 0, 1, 2)
        self.spinBox_3 = QtGui.QSpinBox(self.groupBox_src)
        self.spinBox_3.setObjectName(_fromUtf8("spinBox_3"))
        self.gridLayout.addWidget(self.spinBox_3, 2, 2, 1, 1)
        self.label_src_as = QtGui.QLabel(self.groupBox_src)
        self.label_src_as.setObjectName(_fromUtf8("label_src_as"))
        self.gridLayout.addWidget(self.label_src_as, 3, 0, 1, 1)
        self.lineEdit_src_as = QtGui.QLineEdit(self.groupBox_src)
        self.lineEdit_src_as.setObjectName(_fromUtf8("lineEdit_src_as"))
        self.gridLayout.addWidget(self.lineEdit_src_as, 3, 1, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_src, 3, 0, 1, 2)
        self.groupBox_dst = QtGui.QGroupBox(self)
        self.groupBox_dst.setObjectName(_fromUtf8("groupBox_dst"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_dst)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.dst_ip_label = QtGui.QLabel(self.groupBox_dst)
        self.dst_ip_label.setObjectName(_fromUtf8("dst_ip_label"))
        self.gridLayout_2.addWidget(self.dst_ip_label, 0, 0, 1, 1)
        self.dst_ip_edit = QtGui.QLineEdit(self.groupBox_dst)
        self.dst_ip_edit.setInputMask(_fromUtf8(""))
        self.dst_ip_edit.setObjectName(_fromUtf8("dst_ip_edit"))
        self.gridLayout_2.addWidget(self.dst_ip_edit, 0, 1, 1, 2)
        self.dst_port_label = QtGui.QLabel(self.groupBox_dst)
        self.dst_port_label.setObjectName(_fromUtf8("dst_port_label"))
        self.gridLayout_2.addWidget(self.dst_port_label, 1, 0, 1, 1)
        self.dst_port_edit = QtGui.QLineEdit(self.groupBox_dst)
        self.dst_port_edit.setObjectName(_fromUtf8("dst_port_edit"))
        self.gridLayout_2.addWidget(self.dst_port_edit, 1, 1, 1, 2)
        self.label_snmp_out = QtGui.QLabel(self.groupBox_dst)
        self.label_snmp_out.setObjectName(_fromUtf8("label_snmp_out"))
        self.gridLayout_2.addWidget(self.label_snmp_out, 2, 0, 1, 2)
        self.spinBox_snmp_out = QtGui.QSpinBox(self.groupBox_dst)
        self.spinBox_snmp_out.setObjectName(_fromUtf8("spinBox_snmp_out"))
        self.gridLayout_2.addWidget(self.spinBox_snmp_out, 2, 2, 1, 1)
        self.labes_dst_as = QtGui.QLabel(self.groupBox_dst)
        self.labes_dst_as.setObjectName(_fromUtf8("labes_dst_as"))
        self.gridLayout_2.addWidget(self.labes_dst_as, 3, 0, 1, 1)
        self.lineEdit_dst_as = QtGui.QLineEdit(self.groupBox_dst)
        self.lineEdit_dst_as.setInputMask(_fromUtf8(""))
        self.lineEdit_dst_as.setObjectName(_fromUtf8("lineEdit_dst_as"))
        self.gridLayout_2.addWidget(self.lineEdit_dst_as, 3, 1, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_dst, 3, 2, 1, 1)
        self.next_hop_label = QtGui.QLabel(self)
        self.next_hop_label.setObjectName(_fromUtf8("next_hop_label"))
        self.gridLayout_3.addWidget(self.next_hop_label, 4, 0, 1, 1)
        self.next_hop_edit = QtGui.QLineEdit(self)
        self.next_hop_edit.setInputMask(_fromUtf8(""))
        self.next_hop_edit.setObjectName(_fromUtf8("next_hop_edit"))
        self.gridLayout_3.addWidget(self.next_hop_edit, 4, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 5, 1, 1, 2)
        
        
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/[0-9][0-9]?)?\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.setTabOrder(self.name_edit, self.group_edit)
        self.setTabOrder(self.group_edit, self.protocol_edit)
        self.setTabOrder(self.protocol_edit, self.src_ip_edit)
        self.setTabOrder(self.src_ip_edit, self.src_port_edit)
        self.setTabOrder(self.src_port_edit, self.spinBox_3)
        self.setTabOrder(self.spinBox_3, self.lineEdit_src_as)
        self.setTabOrder(self.lineEdit_src_as, self.dst_ip_edit)
        self.setTabOrder(self.dst_ip_edit, self.dst_port_edit)
        self.setTabOrder(self.dst_port_edit, self.spinBox_snmp_out)
        self.setTabOrder(self.spinBox_snmp_out, self.lineEdit_dst_as)
        self.setTabOrder(self.lineEdit_dst_as, self.next_hop_edit)
        self.setTabOrder(self.next_hop_edit, self.buttonBox)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры ноды", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.group_label.setText(QtGui.QApplication.translate("Dialog", "Направление", None, QtGui.QApplication.UnicodeUTF8))
        self.protocol_label.setText(QtGui.QApplication.translate("Dialog", "Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_src.setTitle(QtGui.QApplication.translate("Dialog", "Сеть источника", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_label.setText(QtGui.QApplication.translate("Dialog", "Src net", None, QtGui.QApplication.UnicodeUTF8))
        self.src_port_label.setText(QtGui.QApplication.translate("Dialog", "Src port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_snmp_in.setText(QtGui.QApplication.translate("Dialog", "In SNMP  interface index", None, QtGui.QApplication.UnicodeUTF8))
        self.label_src_as.setText(QtGui.QApplication.translate("Dialog", "Src AS", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_dst.setTitle(QtGui.QApplication.translate("Dialog", "Сеть получателя", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_ip_label.setText(QtGui.QApplication.translate("Dialog", "Dst net", None, QtGui.QApplication.UnicodeUTF8))
        self.dst_port_label.setText(QtGui.QApplication.translate("Dialog", "Dst port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_snmp_out.setText(QtGui.QApplication.translate("Dialog", "Out SNMP interface index", None, QtGui.QApplication.UnicodeUTF8))
        self.labes_dst_as.setText(QtGui.QApplication.translate("Dialog", "Dst AS", None, QtGui.QApplication.UnicodeUTF8))
        self.next_hop_label.setText(QtGui.QApplication.translate("Dialog", "Next Hop", None, QtGui.QApplication.UnicodeUTF8))
        self.src_ip_edit.setValidator(self.ipValidator)
        self.dst_ip_edit.setValidator(self.ipValidator)
        self.next_hop_edit.setValidator(self.ipValidator)
        
        
        for protocol in self.protocols:
            #print protocol
            self.protocol_edit.addItem(QtGui.QApplication.translate("Dialog", protocol, None, QtGui.QApplication.UnicodeUTF8))

        self.group_edit.addItem("INPUT")
        self.group_edit.addItem("OUTPUT")

    def fixtures(self):
        
        if self.model:
            
            self.name_edit.setText(unicode(self.model.name))
            self.group_edit.setCurrentIndex(self.group_edit.findText(self.model.direction, QtCore.Qt.MatchCaseSensitive))
            #self.
            self.src_ip_edit.setText(unicode(self.model.src_ip))
            #self.src_mask_edit.setText(unicode(self.model.src_mask))
            self.src_port_edit.setText(unicode(self.model.src_port or 0))
            self.dst_ip_edit.setText(unicode(self.model.dst_ip))
            #self.dst_mask_edit.setText(unicode(self.model.dst_mask))
            self.dst_port_edit.setText(unicode(self.model.dst_port or 0))
            #self.protocol_edit.setCurrentIndex(self.protocol_edit.findText(self.protocols[self.model.protocol], QtCore.Qt.MatchCaseSensitive)),
            self.next_hop_edit.setText(unicode(self.model.next_hop))
            self.spinBox_3.setValue(self.model.in_index)
            self.spinBox_snmp_out.setValue(self.model.out_index)
            self.lineEdit_src_as.setText(unicode(self.model.src_as or 0))
            self.lineEdit_dst_as.setText(unicode(self.model.dst_as or 0))
        else:
            default=u'0.0.0.0/0'
            self.src_ip_edit.setText(default)
            #self.src_mask_edit.setText(default)            
            self.dst_ip_edit.setText(default)
            #self.dst_mask_edit.setText(default)
            self.lineEdit_src_as.setText(unicode(0))
            self.lineEdit_dst_as.setText(unicode(0))
            self.next_hop_edit.setText('0.0.0.0')  
        self.connection.commit()                                     


    def accept(self):
        
        if self.model:
            model = self.model
        else:
            model = Object()
            
        model.name = unicode(self.name_edit.text())
        model.direction = unicode(self.group_edit.currentText())
        
        model.protocol = self.protocols[unicode(self.protocol_edit.currentText())]
        
        src_ip = unicode(self.src_ip_edit.text())
        if src_ip:
            #print src_ip
            #print self.ipValidator.validate(src_ip, 0)
            #if self.ipValidator.validate(src_ip, 0)[0] != QtGui.QValidator.Acceptable:
            #    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите правильный Src IP."))
            #    return
            pass
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
            #if self.ipValidator.validate(dst_ip, 0)[0]  != QtGui.QValidator.Acceptable:
            #    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность DST IP."))
            #    return
            pass
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
        
        model.in_index = self.spinBox_3.value()
        model.out_index = self.spinBox_snmp_out.value()
        
        try:
            model.src_as = int(unicode(self.lineEdit_src_as.text()))
            model.dst_as = int(unicode(self.lineEdit_dst_as.text()))
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Src AS и Dst AS должны быть целыми положительными числами или 0."))
            return
        
        if next_hop:
            #if self.ipValidator.validate(next_hop, 0)[0]  != QtGui.QValidator.Acceptable:
            #    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте правильность Next Hop."))
            #    return
            pass
        else:
            next_hop = '0.0.0.0'
        
        model.next_hop = next_hop
        self.model=model
        QtGui.QDialog.accept(self)



class ClassChildEbs(ebsTable_n_TreeWindow):
    def __init__(self, connection):
        columns  = ['#', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'In index', 'Out index', 'Next Hop']
        initargs = {"setname":"class_frame", "objname":"ClassChildEbs", "winsize":(0,0,795,597), "wintitle":"Пользователи", "tablecolumns":columns, "spltsize":(0,0,200,521), "treeheader":"Классы", "menubarsize":(0,0,800,21), "tbiconsize":(18,18)}
        
        super(ClassChildEbs, self).__init__(connection, initargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.protocols={'0':'-all-',  '37':'ddp', '98':'encap', 
                        '3':'ggp',    '47':'gre', '20':'hmp', 
                        '1':'icmp',   '38':'idpr-cmtp', 
                        '2':'igmp',   '94':'ipip','89':'ospf',
                        '4':'ipencap','17':'udp', '27':'rdp',      
                        '6':'tcp'}
        
    def ebsInterInit(self, initargs):
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        self.refreshTree = self.refresh_list
        self.getClassId = self.getTreeId
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editClass)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refreshTable)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.delNodeLocalAction)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editNode)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)

        actList=[("addClassAction", "Добавить класс", "images/folder_add.png", self.addClass), \
                 ("delClassAction", "Удалить класс", "images/folder_delete.png", self.delClass), \
                 ("editClassAction", "Edit class", "images/open.png", self.editClass), \
                 ("addClassNodeAction", "Добавить подкласс", "images/add.png", self.addNode), \
                 ("delClassNodeAction", "Удалить подкласс", "images/del.png", self.delNode), \
                 ("editClassNodeAction", "Редактировать", "images/open.png", self.editNode), \
                 ("importClassNodesAction", "Импорт сетей", "images/open.png", self.importNodes), \
                 ("upClassAction", "Повысить", "images/up.png", self.upClass), \
                 ("downClassAction", "Понизить", "images/down.png", self.downClass)
                ]


        objDict = {self.treeWidget :["editClassAction", "addClassAction", "delClassAction"], \
                   self.tableWidget:["editClassNodeAction", "addClassNodeAction", "delClassNodeAction"], \
                   self.toolBar    :["addClassAction", "delClassAction", "separator","upClassAction", "downClassAction", "separator", "addClassNodeAction", "delClassNodeAction", "separator", "importClassNodesAction"]
                  }
        self.actionCreator(actList, objDict)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
    def ebsPostInit(self, initargs):        

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.connectTree()
        self.delNodeLocalAction()
        self.addNodeLocalAction()
        self.restoreWindow()
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.refresh_list()
        
    def retranslateUI(self, initargs):
        super(ClassChildEbs, self).retranslateUI(initargs)
    def addClass(self):
        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        child=ClassEdit(connection=self.connection)
        if child.exec_()==1:
            self.refresh_list()
        
    
    def editClass(self, *args, **kwargs):
        
        try:
            model=self.connection.get_model(self.treeWidget.currentItem().id, "nas_trafficclass")
        except Exception, e:
            print e
        
        child=ClassEdit(connection=self.connection, model=model)
        
        if child.exec_()==1:
            self.refresh_list()
            
    def delClass(self):
        
        model = self.connection.get_model(self.getClassId(), "nas_trafficclass")
        
        if id>0 and QtGui.QMessageBox.question(self, u"Удалить класс трафика?" , u"Удалить класс трафика?\nВместе с ним будут удалены все его составляющие.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            try:
                
                #self.connection.delete("DELETE FROM nas_trafficnode WHERE traffic_class_id=%d" % model.id)
                self.connection.iddelete(model.id, "nas_trafficclass")
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
            
        #print "item_swap_id=", item_swap_id
        
        model1 = self.connection.get_model(item_changed_id, "nas_trafficclass")
        model2 = self.connection.get_model(item_swap_id, "nas_trafficclass")
        #print model1.name, model2.name
        a=model1.weight+0
        b=model2.weight+0
        #print "a,b", a,b, model1.id, model2.id
        model1.weight=1000001
        try:
            
            self.connection.save(model1,"nas_trafficclass")
            
            model2.weight=a
            model1.weight=b
            
            self.connection.save(model2,"nas_trafficclass")
            
            self.connection.save(model1,"nas_trafficclass")
            
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
        #print "index, self.treeWidget.topLevelItemCount()", index, self.treeWidget.topLevelItemCount()
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
        classes=self.connection.sql(" SELECT id,name,color,passthrough FROM nas_trafficclass ORDER BY weight ASC;")
        self.connection.commit()
        for clas in classes:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.id = clas.id
            item.setText(0, clas.name)
            item.setIcon(0,QtGui.QIcon("images/folder.png"))
            item.setBackgroundColor(0, QtGui.QColor(clas.color))
            if clas.passthrough==True:
                item.setIcon(0, QtGui.QIcon("images/down.png"))
            
        if curItem != -1:
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(curItem))
        

    def importNodes(self):
        id = self.getClassId()
        if id>0:
            child = NetworksImportDialog(id, connection=self.connection)
        if child.exec_()==1:
            self.refreshTable()

    def addNode(self):

        try:
            model=self.connection.get_model(self.getClassId(), "nas_trafficclass")
        except Exception, e:
            print e

        child=ClassNodeFrame(connection = self.connection)
        if child.exec_()==1:
            child.model.traffic_class_id=model.id
            try:
                self.connection.save(child.model,"nas_trafficnode")
                self.connection.commit()
            except Exception, e:
                print e
                self.connection.rollback()
            
            self.refreshTable()
        
    def delNode(self):
        ids = self.get_selected_nodes()
        print ids
        if not ids:return
        if QtGui.QMessageBox.question(self, u"Удалить составляющие?" , u"Вы уверены, что хотите удалить составляющие этого класса?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.No:
            return

        for id in ids:
            if id>0:
                try:
                    self.connection.iddelete(id, "nas_trafficnode")
                except Exception, e:
                    print e
                    self.connection.rollback()
                     
                self.connection.commit()
        self.refreshTable()
                
        
    def editNode(self):
        try:
            model=self.connection.get_model(self.getSelectedId(), "nas_trafficnode")
        except Exception, e:
            print e
            #return
        
        
        child=ClassNodeFrame(connection=self.connection, model=model)
        if child.exec_()==1:
            try:
                self.connection.save(child.model,"nas_trafficnode")
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
        self.tableWidget.setColumnHidden(0, False)
        #print text
        #model = self.connection.get_model(class_id, "nas_trafficclass", fields=[''])
        nodes = self.connection.get_models(table="nas_trafficnode", where={'traffic_class_id':class_id})
        self.connection.commit()
        self.tableWidget.setRowCount(len(nodes))        
        i=0        
        #['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src mask', 'Src Port', 'Dst IP', 'Dst Mask', 'Dst Port', 'Next Hop']
        protocols={'0':'all',  '37':'ddp', '98':'encap', 
                        '3':'ggp',    '47':'gre', '20':'hmp', 
                        '1':'icmp',   '38':'idpr-cmtp', 
                        '2':'igmp',   '94':'ipip','89':'ospf',
                        '4':'ipencap','17':'udp', '27':'rdp',      
                        '6':'tcp'}
        ['#', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'In index', 'Out index', 'Next Hop']
        for node in nodes:

            self.addrow(i, i,0, id=node.id)
            self.addrow(node.name, i,1)
            self.addrow(node.direction, i,2)
            self.addrow(protocols.get("%s" % node.protocol,""), i,3)
            self.addrow(node.src_ip, i,4)
            self.addrow(node.src_port, i,5)
            
            self.addrow(node.dst_ip, i,6)
            self.addrow(node.dst_port, i,7)
            
            self.addrow(node.in_index, i,8)
            self.addrow(node.out_index, i,9)
            self.addrow(node.next_hop, i,10)
            #self.tableWidget.setRowHeight(i, 17)
            i+=1
        
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        
    
    def addrow(self, value, x, y, id=None):
        if value==None:
            value=""
        headerItem = QtGui.QTableWidgetItem()
        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))        
        else:            
            headerItem.setData(0, QtCore.QVariant(value))    
                    
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tc.png"))
        
        if y==0:
            headerItem.id = id
            
        self.tableWidget.setItem(x,y,headerItem)
          
    def addNodeLocalAction(self):
        super(ClassChildEbs, self).addNodeLocalAction([self.addClassNodeAction, self.delClassAction, self.upClassAction, self.downClassAction])
        
    def delNodeLocalAction(self):
        #super(ClassChildEbs, self).delNodeLocalAction([self.delClassNodeAction])
        pass
        
    def get_selected_nodes(self):
        ids = []
        for r in self.tableWidget.selectedItems():
            if r.column()==0:
                ids.append(r.id)
        return ids
    
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
