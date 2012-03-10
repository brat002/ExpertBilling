#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

import IPy
from helpers import tableFormat
from db import AttrDict
from helpers import makeHeaders
from helpers import HeaderUtil

from ebsWindow import ebsTableWindow

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class AddressEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u""]
        initargs = {"setname":"address_frame_header", "objname":"AddressEbs", "winsize":(0,0,750,400), "wintitle":"Пулы адресов", "tablecolumns":columns}
        super(AddressEbs, self).__init__(connection, initargs)
        
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

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.listWidget_city = QtGui.QListWidget(self.centralwidget)
        self.listWidget_city.setObjectName(_fromUtf8("listWidget_city"))
        self.gridLayout.addWidget(self.listWidget_city, 1, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.listWidget_street = QtGui.QListWidget(self.centralwidget)
        self.listWidget_street.setObjectName(_fromUtf8("listWidget_street"))
        self.gridLayout_2.addWidget(self.listWidget_street, 2, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.listWidget_house = QtGui.QListWidget(self.centralwidget)
        self.listWidget_house.setObjectName(_fromUtf8("listWidget_house"))
        self.gridLayout_3.addWidget(self.listWidget_house, 1, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_3)
        self.gridLayout_4.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        
        #self.city_ce = QtGui.QGraphicsColorizeEffect()
        #self.street_ce = QtGui.QGraphicsColorizeEffect()
        #self.house_ce = QtGui.QGraphicsColorizeEffect()
        
        #self.city_ce.setEnabled(True)
        #self.street_ce.setEnabled(True)
        #self.house_ce.setEnabled(True)
        #self.listWidget_city.setGraphicsEffect(self.city_ce)
        #self.listWidget_street.setGraphicsEffect(self.street_ce)
        #self.listWidget_house.setGraphicsEffect(self.house_ce)
        self.listWidget_city.setFocus()
        
    def ebsPostInit(self, initargs):
        #self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        #self.connect(self.tableWidget, QtCore.SIGNAL("cellClicked(int, int)"), self.delNodeLocalAction)
        
        actList=[("addAction", "Добавить", "images/add.png", self.addframe), ("delAction", "Удалить", "images/del.png", self.delete)]
        objDict = {self.tableWidget:["editAction", "addAction", "delAction"], self.toolBar:["addAction", "delAction"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        self.connect(self.listWidget_city, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.refresh_street)
        self.connect(self.listWidget_street, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.refresh_house)
        #self.tableWidget = tableFormat(self.tableWidget)
        self.connect(self.listWidget_city, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.city_clicked)
        self.connect(self.listWidget_street, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.street_clicked)
        self.connect(self.listWidget_house, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.house_clicked)
        
        self.connect(self.listWidget_city, QtCore.SIGNAL("itemPressed(QListWidgetItem *)"), self.city_click)
        self.connect(self.listWidget_street, QtCore.SIGNAL("itemPressed(QListWidgetItem *)"), self.street_click)
        self.connect(self.listWidget_house, QtCore.SIGNAL("itemPressed(QListWidgetItem *)"), self.house_click)
                
        self.toolBar_find.setHidden(True)
        
    def retranslateUI(self, initargs):
        super(AddressEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Номер дома", None, QtGui.QApplication.UnicodeUTF8))
        
    
    def city_click(self):
        self.listWidget_city.setStyleSheet("background-color: rgb(174, 218, 255);")
        self.listWidget_street.setStyleSheet("")
        self.listWidget_house.setStyleSheet("")
    def street_click(self):
        self.listWidget_city.setStyleSheet('')
        self.listWidget_street.setStyleSheet("background-color: rgb(174, 218, 255);")
        self.listWidget_house.setStyleSheet("")
       
    def house_click(self):
        self.listWidget_city.setStyleSheet('')
        self.listWidget_street.setStyleSheet("")
        self.listWidget_house.setStyleSheet("background-color: rgb(174, 218, 255);")
                
    def city_clicked(self, item):
        id = item.id
        default_text = item.text()
        text = QtGui.QInputDialog.getText(self,u"Введите название города", u"Название города:", QtGui.QLineEdit.Normal, default_text)      
        
        if text[0].isEmpty()==True:
            #QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return            
        
        model = AttrDict()
        model.id = id
        model.name = unicode(text[0])
        self.connection.city_save(model)
        self.refresh_city()
        print "city"
        #ce.setEnabled(False)
    def street_clicked(self, item):
        id = item.id
        default_text = item.text()
        text = QtGui.QInputDialog.getText(self,u"Введите название улицы", u"Название улицы:", QtGui.QLineEdit.Normal, default_text)      
        
        if text[0].isEmpty()==True:
            #QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return            
        
        model = AttrDict()
        model.id = id
        model.street = item.city
        model.name = unicode(text[0])
        self.connection.street_save(model)
        self.refresh_street()
        print "street"
        #ce.setEnabled(False)
    def house_clicked(self, item):
        id = item.id
        default_text = item.text()
        text = QtGui.QInputDialog.getText(self,u"Введите номер дома", u"Номер дома:", QtGui.QLineEdit.Normal, default_text)      
        
        if text[0].isEmpty()==True:
            #QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return            
        
        model = AttrDict()
        model.id = id
        model.street = item.street
        model.name = unicode(text[0])
        self.connection.house_save(model)
        self.refresh_street()
        print "house"
                #ce.setEnabled(False)                
    
    def addframe(self):
        print "addfr"
        #addf = AddPoolFrame(self.connection)
        #if addf.exec_()==1:
        #    self.refresh()
        selected_listwidget = None
        parent = None
        type=None
        if self.listWidget_city.hasFocus():
            selected_listwidget = self.listWidget_city
            type=1
        elif self.listWidget_street.hasFocus():
            selected_listwidget = self.listWidget_street
            parent = self.listWidget_city.currentItem().id
            type=2
        elif self.listWidget_house.hasFocus():
            selected_listwidget = self.listWidget_house
            parent = self.listWidget_street.currentItem().id
            type=3
        else:
            QtGui.QMessageBox.warning(self, unicode(u"Подсказка"), unicode(u"Кликните по полю, куда хотите добавить запись."))
            return
        
        #print "yupe", type, selected_listwidget
        #if not selected_listwidget: print 123;return
        default_text = ""
        print 123
        if type==1:
            text = QtGui.QInputDialog.getText(self,u"Введите название города", u"Название:", QtGui.QLineEdit.Normal, default_text)        
        if type==2:
            text = QtGui.QInputDialog.getText(self,u"Введите название улицы", u"Название:", QtGui.QLineEdit.Normal, default_text)        
        if type==3:
            text = QtGui.QInputDialog.getText(self,u"Введите номер дома", u"Название:", QtGui.QLineEdit.Normal, default_text)        
        
        if text[0].isEmpty()==True:
            #QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode(u"Введено пустое название."))
            return            
        
        model = AttrDict()
        model.name = unicode(text[0])
        if type==1:

            self.connection.city_save(model)

            self.refresh_city()
            
        if type==2:
            model.city=parent

            self.connection.street_save(model)

            self.refresh_street()
            
        if type==3:
            model.street=parent

            self.connection.house_save(model)
 
            self.refresh_house()
                        
    def delete(self):
        
        selected_listwidget = None
        parent = None
        type=None
        if self.listWidget_city.hasFocus():
            selected_listwidget = self.listWidget_city
            type=1
        elif self.listWidget_street.hasFocus():
            selected_listwidget = self.listWidget_street
            parent = self.listWidget_city.currentItem().id
            type=2
        elif self.listWidget_house.hasFocus():
            selected_listwidget = self.listWidget_house
            parent = self.listWidget_street.currentItem().id
            type=3
        id = selected_listwidget.currentItem().id    
        if (QtGui.QMessageBox.question(self, u"Удалить адрес?" , u'''Внимание! Во избежание удаления пользовательских аккаунтов, удостоверьтесь, что пользователи не используют удаляемые адреса.''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
            if type==1:
                self.connection.city_delete(id)
                self.refresh_city()
            if type==2:
                self.connection.street_delete(id)
                self.refresh_street()
            if type==3:
                self.connection.house_delete(id)
                self.refresh_house()


            
            

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/nas.png"))
        self.tableWidget.setItem(x,y,headerItem)


    def refresh(self):
        self.refresh_city()
    
    def refresh_city(self):
        
    
        self.listWidget_city.clear()
        self.listWidget_street.clear()
        self.listWidget_house.clear()
        
        
        cities = self.connection.get_cities()
        self.connection.commit()
        #self.tableWidget.setRowCount(len(pools))

        for city in cities:
            item =QtGui.QListWidgetItem( unicode(city.name))
            item.id = city.id
            self.listWidget_city.addItem(item)
            #self.delNodeLocalAction()
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.setSortingEnabled(True)
    
    def refresh_street(self):
        self.listWidget_street.clear()
        self.listWidget_house.clear()
        #ce = QtGui.QGraphicsColorizeEffect()
        #self.listWidget_city.setGraphicsEffect(ce)
        #ce.setEnabled(False)
        
        try:
            city_id = self.listWidget_city.currentItem().id
        except:
            return
        streets = self.connection.get_streets(city_id= city_id)
        self.connection.commit()
        #self.tableWidget.setRowCount(len(pools))

        for street in streets:
            item =QtGui.QListWidgetItem( unicode(street.name))
            item.id = street.id
            item.city=city_id
            self.listWidget_street.addItem(item)    

    def refresh_house(self):
        
    
        self.listWidget_house.clear()
        
        try:
            street_id = self.listWidget_street.currentItem().id
        except:
            return
        houses = self.connection.get_houses(street_id = street_id)
        self.connection.commit()
        #self.tableWidget.setRowCount(len(pools))

        for house in houses:
            item =QtGui.QListWidgetItem( unicode(house.name))
            item.id = house.id
            item.street=street_id
            self.listWidget_house.addItem(item)
            
    def delNodeLocalAction(self):
        pass
    #    super(PoolEbs, self).delNodeLocalAction([self.delAction])
        
