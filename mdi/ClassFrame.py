#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import mdi_rc

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'

from nas.models import TrafficClass, TrafficNode
from time import mktime
import datetime, calendar
NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

class ClassEdit(QtGui.QDialog):
    def __init__(self, model=None):
        super(ClassEdit, self).__init__()
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,346,106).size()).expandedTo(self.minimumSizeHint()))
        
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
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
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
        
            
        

class AddTimePeriod(QtGui.QDialog):
    def __init__(self, timemodel, nodemodel=None):
        super(AddTimePeriod, self).__init__()
        self.timemodel=timemodel
        self.nodemodel=nodemodel
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,278,198).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(110,160,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10,10,197,16))
        self.label.setObjectName("label")

        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(10,30,261,131))
        self.widget.setObjectName("widget")

        self.gridlayout = QtGui.QGridLayout(self.widget)
        self.gridlayout.setObjectName("gridlayout")

        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,0,0,1,1)

        self.name_edit = QtGui.QLineEdit(self.widget)
        self.name_edit.setObjectName("name_edit")
        self.gridlayout.addWidget(self.name_edit,0,1,1,1)

        self.start_label = QtGui.QLabel(self.widget)
        self.start_label.setObjectName("start_label")
        self.gridlayout.addWidget(self.start_label,1,0,1,1)

        self.start_date_edit = QtGui.QDateTimeEdit(self.widget)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setObjectName("start_date_edit")
        self.gridlayout.addWidget(self.start_date_edit,1,1,1,1)

        self.end_label = QtGui.QLabel(self.widget)
        self.end_label.setObjectName("end_label")
        self.gridlayout.addWidget(self.end_label,2,0,1,1)

        self.end_date_edit = QtGui.QDateTimeEdit(self.widget)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setObjectName("end_date_edit")
        self.gridlayout.addWidget(self.end_date_edit,2,1,1,1)

        self.repeat_label = QtGui.QLabel(self.widget)
        self.repeat_label.setObjectName("repeat_label")
        self.gridlayout.addWidget(self.repeat_label,3,0,1,1)

        self.repeat_edit = QtGui.QComboBox(self.widget)
        self.repeat_edit.setObjectName("repeat_edit")
        self.gridlayout.addWidget(self.repeat_edit,3,1,1,1)

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Период времени", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<b>Укажите временной промежуток</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Окончание", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_label.setText(QtGui.QApplication.translate("Dialog", "Повторять через", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Сутки", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Месяц", None, QtGui.QApplication.UnicodeUTF8))
        self.repeat_edit.addItem(QtGui.QApplication.translate("Dialog", "Год", None, QtGui.QApplication.UnicodeUTF8))


    def accept(self):
        """
        понаставить проверок
        """
        #QMessageBox.warning(self, u"Сохранение", unicode(u"Осталось написать сохранение :)"))

        if self.nodemodel:
            model=self.nodemodel
        else:
            print 'New sp'
            model=TimePeriodNode()
        
        model.name=unicode(self.name_edit.text())
        model.time_start=self.start_date_edit.dateTime().toPyDateTime()

        model.length=self.start_date_edit.dateTime().secsTo(self.end_date_edit.dateTime())
        print model.length
        
        model.repeat_after=unicode(self.repeat_edit.currentText())
        try:
            id=model.id
            model.save()
            #Если редактируем
            if not id:
                self.timemodel.time_period_nodes.add(model)
        except Exception, e:
            print e
            return



        QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        end=datetime.datetime.now()

        if self.nodemodel:
            self.name_edit.setText(unicode(self.nodemodel.name))
    
            start = QtCore.QDateTime()

            start.setTime_t(int(mktime(self.nodemodel.time_start.timetuple())))

            end = QtCore.QDateTime()
            end.setTime_t(int(mktime((self.nodemodel.time_start+datetime.timedelta(seconds=self.nodemodel.length)).timetuple())))

            self.repeat_edit.setCurrentIndex(self.repeat_edit.findText(self.nodemodel.repeat_after, QtCore.Qt.MatchCaseSensitive))
            
    

        self.start_date_edit.setDateTime(start)
        self.end_date_edit.setDateTime(end)

    def save(self):
        print 'Saved'


class ListWidget(QListWidget):
    def __init__(self, parent = None):
        QListWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        #event.setDropAction(QtCore.Qt.CopyAction)
        #event.acceptProposedAction()
        event.accept()

    def dropEvent(self, event):
        print "Drop"
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        print unicode(self.currentItem().text())


class ClassChild(QMainWindow):
    sequenceNumber = 1

    def __init__(self):
        super(ClassChild, self).__init__()
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,801,597).size()).expandedTo(self.minimumSizeHint()))

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
        self.splitter.setGeometry(QtCore.QRect(0,0,801,521))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.listWidget = QListWidget(self.splitter)
        self.listWidget.setMaximumSize(QtCore.QSize(220,16777215))
        #self.listWidget.setMouseTracking(True)
        #self.listWidget.setAcceptDrops(True)
        #self.listWidget.setDragEnabled(True)
        self.listWidget.setDropIndicatorShown(True)
        
        self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        
        self.listWidget.setFrameShape(QtGui.QFrame.Panel)
        self.listWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.listWidget.setObjectName("listWidget")

        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.tableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.tableWidget.setLineWidth(1)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        
        self.tableWidget.setObjectName("tableWidget")
        self.setCentralWidget(self.splitter)
        
        vh = self.tableWidget.verticalHeader()
        vh.setVisible(False)
        hh = self.tableWidget.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        #hh.setClickable(False)
        hh.ResizeMode(QtGui.QHeaderView.Stretch)
        hh.setMovable(True)
        hh.setMaximumHeight(18)
        

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0,0,801,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

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
        self.upClassAction.setIcon(QtGui.QIcon("images/add.png"))
        self.upClassAction.setObjectName("delClassNodeAction")
               
        #Down Class
        self.downClassAction = QtGui.QAction(self)
        self.downClassAction.setIcon(QtGui.QIcon("images/add.png"))
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
        self.connect(self.addClassAction, QtCore.SIGNAL("triggered()"), self.addClass)
        self.connect(self.delClassAction, QtCore.SIGNAL("triggered()"), self.delClass)
        
        self.connect(self.upClassAction, QtCore.SIGNAL("triggered()"), self.upClass)
        self.connect(self.downClassAction, QtCore.SIGNAL("triggered()"), self.downClass)
        
        self.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.editClass)
        self.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.refreshTable)
        self.refresh_list()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)


    
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("MainWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Group", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "Protocol", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Src-IP", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "Src-mask", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        
        headerItem5.setText(QtGui.QApplication.translate("MainWindow", "Dst-IP", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem5)

        headerItem6 = QtGui.QTableWidgetItem()
        
        headerItem6.setText(QtGui.QApplication.translate("MainWindow", "Dst-Mask", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(6,headerItem6)
        columns = ['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src mask', 'Src Port', 'Dst IP', 'Dst Mask', 'Dst Port', 'Next Hop']
        self.tableWidget.setColumnCount(len(columns))
        self.tableWidget.setHorizontalHeaderLabels(columns)
        self.tableWidget.setColumnHidden(0, True)

        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassAction.setText(QtGui.QApplication.translate("MainWindow", "Add class", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class", None, QtGui.QApplication.UnicodeUTF8))
        self.addClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Add Node", None, QtGui.QApplication.UnicodeUTF8))
        self.delClassNodeAction.setText(QtGui.QApplication.translate("MainWindow", "Delete Class Node", None, QtGui.QApplication.UnicodeUTF8))


    def addClass(self):
        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        child=ClassEdit()
        if child.exec_()==1:
            clc=TrafficClass.objects.all().order_by("-weight")[0]
            max_weight=clc.weight
            print "color=", child.color
            TrafficClass.objects.create(name=unicode(child.name_edit.text()), weight=max_weight+100, color=unicode(child.color), store=child.store_edit.checkState()==2)
            
        self.refresh_list()
        
    
    def editClass(self):
        name=self.getSelectedName()
        try:
            model=TrafficClass.objects.get(name=unicode(name))
        except:
            return
        
        child=ClassEdit(model=model)
        
        if child.exec_()==1:
            model.name=unicode(child.name_edit.text())
            
            model.color=child.color
            
            model.store=child.store_edit.checkState()==2
            model.save()
            
            
        self.refresh_list()
            
    def delClass(self):
        name=self.getSelectedName()
        try:
            model=TrafficClass.objects.get(name=unicode(name))
        except:
            return

        if id>0 and QMessageBox.question(self, u"Удалить класс трафика?" , u"Удалить класс трафика?\nВместе с ним будут удалены все его составляющие.", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            model.delete()

        self.refresh_list()
        
        
    def savePosition(self, direction):
        item_changed_name = unicode(self.listWidget.item(self.listWidget.currentRow()).text())
        if direction == u"up":
            item_swap_name = unicode(self.listWidget.item(self.listWidget.currentRow()+1).text())
        elif direction == u"down":
            item_swap_name = unicode(self.listWidget.item(self.listWidget.currentRow()-1).text())
            
        
        model1 = TrafficClass.objects.get(name = item_changed_name)
        model2 = TrafficClass.objects.get(name = item_swap_name)
        print model1.weight, model2.weight
        a=model1.weight+0
        b=model2.weight+0
        
        model1.weight=1000001
        model1.save()
        
        model2.weight=a
        model1.weight=b
        
        model2.save()
        
        model1.save()
        
        model2.save()
        
        print model1.weight, model2.weight
            

    
    def upClass(self):
        #self.listWidget.currentItem()
        row=self.listWidget.currentRow()
        item = self.listWidget.takeItem(row)
        self.listWidget.insertItem(row-1,item)
        self.listWidget.setCurrentItem(item)
        self.savePosition(direction=u"up")
        #pass
    
    def downClass(self):
        row=self.listWidget.currentRow()
        item = self.listWidget.takeItem(row)
        self.listWidget.insertItem(row+1,item)
        self.listWidget.setCurrentItem(item)
        self.savePosition(direction=u"down")
        
        
    def refresh_list(self):
        self.listWidget.clear()

        classes=TrafficClass.objects.all().order_by('-weight')
        
        for clas in classes:
            item = QtGui.QListWidgetItem(self.listWidget)
            item.setText(clas.name)
            item.setBackgroundColor(QColor(clas.color))
            self.listWidget.addItem(item)
            
            
        

    def editPeriod(self):
        name=unicode(self.getSelectedName())
        text = QInputDialog.getText(self,unicode(u"Введите название периода"), unicode(u"Название:"), QLineEdit.Normal,name);
        if text[0].isEmpty()==True and text[2]:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                    u"Введено пустое название.")
            return
        try:
            model=TimePeriod.objects.get(name=name)
            model.name=unicode(text[0])
            model.save()                
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка",
                        u"Введено недопустимое значение.")
            return
        self.refresh()

    def addNode(self):
        name=self.getSelectedName()
        try:
            model=TimePeriod.objects.get(name=unicode(name))
        except:
            return

        child=AddTimePeriod(timemodel=model)
        child.exec_()
        self.refreshTable()
        
    def delNode(self):
        id = self.getSelectedId()
        try:
            nodemodel = TimePeriodNode.objects.get(id=id)
        except:
            return
        if QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            nodemodel.delete()
            self.refreshTable()
        
    def editNode(self):
        id = self.getSelectedId()
        try:
            nodemodel = TimePeriodNode.objects.get(id=id)
        except:
            pass
        
        name=self.getSelectedName()
        try:
            model=TimePeriod.objects.get(name=unicode(name))
        except:
            return
        
        child=AddTimePeriod(timemodel=model, nodemodel=nodemodel)
        child.exec_()
        self.refreshTable()
        
    def refreshTable(self, widget=None):
        if not widget:
            text=unicode(self.getSelectedName())
        else:
            text=unicode(widget.text())
        self.tableWidget.clearContents()
        #print text
        model = TrafficClass.objects.get(name=text)
        nodes = TrafficNode.objects.filter(traffic_class = model).order_by("id")

        self.tableWidget.setRowCount(nodes.count())
        
        i=0        
        ['Id', 'Name', 'Direction', 'Protocol', 'Src IP', 'Src mask', 'Src Port', 'Dst IP', 'Dst Mask', 'Dst Port', 'Next Hop']
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
            #self.tableWidget.setColumnHidden(0, True)
# 
 
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.rowHeight(10)


        #child=AddSettlementPeriod(model=model)
        #child.exec_()

        #self.refresh()


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getSelectedName(self):
        return self.listWidget.currentItem().text()
    
    def editframe(self):
        id=self.getSelectedId()
        if id==0:
            return
        try:
            model=Nas.objects.get(id=self.getSelectedId())
        except:
            model=None

        addf = AddNasFrame(model)
        #addf.show()
        addf.exec_()
        self.refresh()

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)

    def refresh(self):
        self.timeperiod_list_edit.clear()

        periods=TimePeriod.objects.all().order_by('id')
        
        for period in periods:
            item = QtGui.QListWidgetItem(self.timeperiod_list_edit)
            item.setText(period.name)
            self.timeperiod_list_edit.addItem(item)
        
#===============================================================================
#        self.tableWidget.setRowCount(periods.count())
#        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
#        i=0
#        for period in periods:
#            self.addrow(period.id, i,0)
#            self.addrow(period.name, i,1)
#            self.addrow(period.autostart, i,2)
#            self.addrow(period.time_start, i,3)
#            self.addrow(period.length_in, i,4)
#            self.addrow(period.length, i,5)
#            self.tableWidget.setRowHeight(i, 17)
#            self.tableWidget.setColumnHidden(0, True)
# 
# 
#            i+=1
#        self.tableWidget.resizeColumnsToContents()
#        self.tableWidget.rowHeight(10)
#===============================================================================

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
        #if self.maybeSave():
        #    event.accept()
        #else:
        #    event.ignore()
        pass

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


