#-*-coding=utf-8*-


from PyQt4 import QtCore, QtGui

class CheckBoxDialog(QtGui.QDialog):
    def __init__(self, all_items, selected_items, select_mode='checkbox'):
        super(CheckBoxDialog, self).__init__()
        self.all_items=all_items
        self.selected_items = selected_items
        self.select_mode = select_mode
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30,240,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(0,30,256,192))
        self.listWidget.setObjectName("listWidget")
        
  
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.listWidget)
        vbox.addWidget(self.buttonBox)
        
        self.setLayout(vbox)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        
    def fixtures(self):
       
        for ai in self.all_items:
            item = QtGui.QListWidgetItem(ai.name)
            if ai in self.selected_items:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setSelected(True)
            else:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Unchecked)
                
            self.listWidget.addItem(item)
            
    def accept(self):
        self.selected_items=[]
        for x in xrange(0,self.listWidget.count()):
            if self.listWidget.item(x).checkState()==QtCore.Qt.Checked:
                self.selected_items.append(self.all_items[x])
        
        print self.selected_items
        QtGui.QDialog.accept(self)        
        
            
class ComboBoxDialog(QtGui.QDialog):
    def __init__(self, items, selected_item=None):
        super(ComboBoxDialog, self).__init__()
        self.items = items
        self.selected_item = selected_item
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()).expandedTo(self.minimumSizeHint()))


        self.vboxlayout = QtGui.QVBoxLayout()


        self.comboBox = QtGui.QComboBox()

        self.vboxlayout.addWidget(self.comboBox)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)

        self.vboxlayout.addWidget(self.buttonBox)
        self.setLayout(self.vboxlayout)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Диалог выбора", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        i=0
        for item in self.items:
            self.comboBox.addItem(item.name)
            if unicode(item.name) == unicode(self.selected_item):
                self.comboBox.setCurrentIndex(i)
            i+=1
            
class SpeedEditDialog(QtGui.QDialog):
    def __init__(self, item, title):
        super(SpeedEditDialog, self).__init__()
        self.item = item
        self.title = title
        self.resultstring = ""
        self.resize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(120,95,171,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.speed_out_label = QtGui.QLabel(self)
        self.speed_out_label.setGeometry(QtCore.QRect(220,44,171,16))
        self.speed_out_label.setObjectName("speed_out_label")

        self.speed_in_label = QtGui.QLabel(self)
        self.speed_in_label.setGeometry(QtCore.QRect(20,44,171,16))
        self.speed_in_label.setObjectName("speed_in_label")

        self.in_postfix = QtGui.QComboBox(self)
        self.in_postfix.setGeometry(QtCore.QRect(140,60,69,21))
        self.in_postfix.setObjectName("in_postfix")
        self.in_postfix.addItem("")

        self.out_postfix = QtGui.QComboBox(self)
        self.out_postfix.setGeometry(QtCore.QRect(340,60,69,21))
        self.out_postfix.setObjectName("out_postfix")
        self.out_postfix.addItem("")

        self.description_label = QtGui.QLabel(self)
        self.description_label.setGeometry(QtCore.QRect(11,11,428,25))
        self.description_label.setObjectName("description_label")

        self.speed_in_edit = QtGui.QLineEdit(self)
        self.speed_in_edit.setGeometry(QtCore.QRect(20,60,113,21))
        self.speed_in_edit.setObjectName("speed_in_edit")

        self.speed_out_edit = QtGui.QLineEdit(self)
        self.speed_out_edit.setGeometry(QtCore.QRect(220,60,113,21))
        self.speed_out_edit.setObjectName("speed_out_edit")

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)

        self.setTabOrder(self.speed_in_edit,self.in_postfix)
        self.setTabOrder(self.in_postfix,self.speed_out_edit)
        self.setTabOrder(self.speed_out_edit,self.out_postfix)
        self.setTabOrder(self.out_postfix,self.buttonBox)

        self.fixtures()
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("Dialog", "Исходящий", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("Dialog", "Входящий", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.description_label.setText("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><span style=\" font-size:12pt; color:#000080;\">%s</span></p></body></html>" % self.title)
        
    def fixtures(self):
        if self.item=="" or self.item.rfind("/")==-1:
            return
        
        nodes = self.item.split("/")

        if nodes[0].endswith(u"k") or nodes[0].endswith(u"M"):
            self.in_postfix.setCurrentIndex(self.in_postfix.findText(nodes[0][-1], QtCore.Qt.MatchCaseSensitive))
            
            self.speed_in_edit.setText(nodes[0][0:-1])
        else:
            self.speed_in_edit.setText(nodes[0])
            
        if nodes[1].endswith(u"k") or nodes[1].endswith(u"M"):
            self.out_postfix.setCurrentIndex(self.in_postfix.findText(nodes[1][-1], QtCore.Qt.MatchCaseSensitive))
            self.speed_out_edit.setText(nodes[1][0:-1])
        else:
            self.speed_out_edit.setText(nodes[1])
            
            
    def accept(self): 
        if (self.speed_in_edit.text()=="" and self.in_postfix.currentText()=="") and (self.speed_out_edit.text()=="" and self.out_postfix.currentText()=="") :
            self.resultstring=""
        else:     
            self.resultstring = "%s%s/%s%s" % (self.speed_in_edit.text(), self.in_postfix.currentText(), self.speed_out_edit.text(), self.out_postfix.currentText())
        QtGui.QDialog.accept(self)
        