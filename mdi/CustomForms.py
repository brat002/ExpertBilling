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