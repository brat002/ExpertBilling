#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui, QtWebKit

from helpers import tableFormat

from helpers import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from time import mktime
from CustomForms import ComboBoxDialog
import datetime, calendar
from helpers import transaction
from helpers import HeaderUtil, SplitterUtil
from helpers import write_cards
import os
from randgen import GenPasswd2
import string

templatedir = "cards"
class AddCards(QtGui.QDialog):
    def __init__(self, connection,last_series=0):
        super(AddCards, self).__init__()
        
        self.connection = connection
        self.last_series=last_series
        self.connection.commit()
        self.resize(337, 426)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.params_groupBox = QtGui.QGroupBox(self.tab)
        self.params_groupBox.setGeometry(QtCore.QRect(10, 10, 291, 171))
        self.params_groupBox.setObjectName("params_groupBox")
        self.nominal_lineEdit = QtGui.QLineEdit(self.params_groupBox)
        self.nominal_lineEdit.setGeometry(QtCore.QRect(110, 50, 171, 20))
        self.nominal_lineEdit.setObjectName("nominal_lineEdit")
        self.count_label = QtGui.QLabel(self.params_groupBox)
        self.count_label.setGeometry(QtCore.QRect(10, 80, 80, 21))
        self.count_label.setObjectName("count_label")
        self.pin_label = QtGui.QLabel(self.params_groupBox)
        self.pin_label.setGeometry(QtCore.QRect(10, 110, 59, 21))
        self.pin_label.setObjectName("pin_label")
        self.series_label = QtGui.QLabel(self.params_groupBox)
        self.series_label.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.series_label.setObjectName("series_label")
        self.nominal_label = QtGui.QLabel(self.params_groupBox)
        self.nominal_label.setGeometry(QtCore.QRect(10, 50, 46, 21))
        self.nominal_label.setObjectName("nominal_label")
        self.pin_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.pin_spinBox.setGeometry(QtCore.QRect(110, 110, 101, 21))
        self.pin_spinBox.setMaximum(32)
        self.pin_spinBox.setObjectName("pin_spinBox")
        self.l_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.l_checkBox.setGeometry(QtCore.QRect(110, 140, 91, 21))
        self.l_checkBox.setObjectName("l_checkBox")
        self.numbers_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.numbers_checkBox.setGeometry(QtCore.QRect(200, 140, 81, 21))
        self.numbers_checkBox.setObjectName("numbers_checkBox")
        self.count_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.count_spinBox.setGeometry(QtCore.QRect(110, 80, 171, 21))
        self.count_spinBox.setFrame(True)
        self.count_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.count_spinBox.setAccelerated(True)
        self.count_spinBox.setMaximum(999999999)
        self.count_spinBox.setObjectName("count_spinBox")
        self.series_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.series_spinBox.setGeometry(QtCore.QRect(110, 20, 171, 22))
        self.series_spinBox.setMaximum(999999999)
        self.series_spinBox.setObjectName("series_spinBox")
        self.period_groupBox = QtGui.QGroupBox(self.tab)
        self.period_groupBox.setGeometry(QtCore.QRect(10, 190, 291, 91))
        self.period_groupBox.setObjectName("period_groupBox")
        self.end_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.end_dateTimeEdit.setGeometry(QtCore.QRect(70, 50, 194, 22))
        self.end_dateTimeEdit.setCalendarPopup(True)
        self.end_dateTimeEdit.setObjectName("end_dateTimeEdit")
        self.start_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.start_dateTimeEdit.setGeometry(QtCore.QRect(70, 20, 194, 22))
        self.start_dateTimeEdit.setCalendarPopup(True)
        self.start_dateTimeEdit.setObjectName("start_dateTimeEdit")
        self.start_label = QtGui.QLabel(self.period_groupBox)
        self.start_label.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.start_label.setObjectName("start_label")
        self.end_label = QtGui.QLabel(self.period_groupBox)
        self.end_label.setGeometry(QtCore.QRect(10, 50, 46, 16))
        self.end_label.setObjectName("end_label")
        self.groupBox_template = QtGui.QGroupBox(self.tab)
        self.groupBox_template.setGeometry(QtCore.QRect(10, 290, 291, 51))
        self.groupBox_template.setObjectName("groupBox_template")
        self.comboBox_templates = QtGui.QComboBox(self.groupBox_template)
        self.comboBox_templates.setGeometry(QtCore.QRect(100, 20, 181, 22))
        self.comboBox_templates.setObjectName("comboBox_templates")
        self.toolButton_preview = QtGui.QToolButton(self.groupBox_template)
        self.toolButton_preview.setGeometry(QtCore.QRect(10, 20, 81, 20))
        self.toolButton_preview.setObjectName("toolButton_preview")
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.toolButton_preview,QtCore.SIGNAL("clicked()"),self.preView)
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры серии", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры генерации карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.count_label.setText(QtGui.QApplication.translate("Dialog", "Количество", None, QtGui.QApplication.UnicodeUTF8))
        self.pin_label.setText(QtGui.QApplication.translate("Dialog", "Длина пина", None, QtGui.QApplication.UnicodeUTF8))
        self.series_label.setText(QtGui.QApplication.translate("Dialog", "Серия", None, QtGui.QApplication.UnicodeUTF8))
        self.nominal_label.setText(QtGui.QApplication.translate("Dialog", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.l_checkBox.setText(QtGui.QApplication.translate("Dialog", "Буквы (a-Z)", None, QtGui.QApplication.UnicodeUTF8))
        self.numbers_checkBox.setText(QtGui.QApplication.translate("Dialog", "Цифры (0-9)", None, QtGui.QApplication.UnicodeUTF8))
        self.period_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Период действия", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_template.setTitle(QtGui.QApplication.translate("Dialog", "Шаблон для печати", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_preview.setText(QtGui.QApplication.translate("Dialog", "Предросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))

    def accept(self):
        """
        понаставить проверок
        """
        try:
            if self.l_checkBox.checkState()==0 and self.numbers_checkBox.checkState()==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не выбрали состав PIN-кода"))
                return
            
            if self.nominal_lineEdit.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан номинал"))
                return
            
            if self.count_spinBox.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано количество генерируемых карточек"))
                return
            
            if self.pin_spinBox.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана длина PIN-кода"))
                return        
            
            
            
            mask=[]
            if self.l_checkBox.checkState()==2:
                mask+=string.letters
            if self.numbers_checkBox.checkState()==2:
                mask+=string.digits
                
            now = datetime.datetime.now()
            for x in xrange(0, self.count_spinBox.text().toInt()[0]):
                model = Object()
                #model.card_group_id = self.group
                model.series = unicode(self.series_spinBox.text())
                model.pin = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=mask)
                model.nominal = self.nominal_lineEdit.text()
                model.start_date = self.start_dateTimeEdit.dateTime().toPyDateTime()
                model.end_date = self.end_dateTimeEdit.dateTime().toPyDateTime()
                model.template = self.comboBox_templates.currentText()
                model.created = now()
                #model.sold=False
                #model.activated=False
                
                print model.pin
                
                self.connection.create(model.save("billservice_card"))
            
            self.connection.commit()
        except:
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Во время генерации карт возникла непредвиденная ошибка."))
            return

        QtGui.QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        #end=datetime.datetime.now()

        self.series_spinBox.setMinimum(self.last_series)
        self.start_dateTimeEdit.setMinimumDate(start)
        self.end_dateTimeEdit.setMinimumDate(start)
        self.updateTemplates()

    def preView(self):
        tmplt = str(self.comboBox_templates.currentText())
        if not tmplt:
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Вы не выбрали шаблон!")
            return
        mask=[]
        if self.l_checkBox.checkState()==2:
            mask+=string.letters
        if self.numbers_checkBox.checkState()==2:
            mask+=string.digits
        tdct = {}
        tdct["pin"] = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=mask)
        wr_files, i = write_cards(templatedir + "/" + tmplt, [tdct], strict=None)
        if i:
            print wr_files
            child = CardPreviewDialog(wr_files[0])
            child.exec_()
            os.remove(wr_files[0])
        else:
            QtGui.QMessageBox.warning(self, u"Внимание!", u"При создании шаблона для предпросмотра произошли ошибки!")
        
        
    def updateTemplates(self):
        #print os.listdir("cards")
        #print [unicode(os.path.basename(tmplt)) for tmplt in os.listdir(templatedir) if (tmplt.find("__printandum__" == -1))]
        self.comboBox_templates.addItems([unicode(tmplt) for tmplt in os.listdir(templatedir) if ((tmplt.find("_printandum_") == -1) and os.path.isfile(''.join((templatedir, '/',tmplt))))])
        #templates = [unicode(os.path.basename(tmplt)) for tmplt in os.listdir(templatedir) if (tmplt.find("__printandum__" == -1))]
        #for tstr in templates:
            #self.comboBox_templates.addItem(unicode(tstr))

class CardsChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        bhdr = HeaderUtil.getBinaryHeader("cards_frame_header")
        self.splname = "cards_frame_splitter"
        bspltr = SplitterUtil.getBinarySplitter(self.splname)
        super(CardsChild, self).__init__()
        
        self.connection = connection
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        
        self.setObjectName("CardsMDI")
        self.resize(947, 619)
        self.setIconSize(QtCore.QSize(24, 24))
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        #self.statusbar = QtGui.QStatusBar(self)
        #self.statusbar.setObjectName("statusbar")
        #self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.toolBar_filter = QtGui.QToolBar(self)
        self.toolBar_filter.setMovable(False)
        self.toolBar_filter.setAllowedAreas(QtCore.Qt.BottomToolBarArea)
        #self.toolBar_filter.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar_filter.setFloatable(False)
        self.toolBar_filter.setObjectName("toolBar_filter")
        ###################### Filter
        self.comboBox_nominal = QtGui.QComboBox(self)
        
        self.comboBox_nominal.setGeometry(QtCore.QRect(0,0,60,20))
        #self.comboBox_nominal.setValidator(QtGui.QIntValidator)
        self.comboBox_nominal.setEditable(True)
        
        self.date_start = QtGui.QDateTimeEdit(self)
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")

        self.date_end = QtGui.QDateTimeEdit(self)
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")

        self.label_date_start = QtGui.QLabel(self)
        self.label_date_start.setMargin(10)
        self.label_date_start.setObjectName("date_start_label")

        self.label_date_end = QtGui.QLabel(self)
        self.label_date_end.setMargin(10)
        self.label_date_end.setObjectName("date_end_label")
        
        self.label_nominal = QtGui.QLabel(self)
        self.label_nominal.setMargin(10)
        
        self.label_filter = QtGui.QLabel(self)
        self.label_filter.setMargin(10)
        
        self.checkBox_sold = QtGui.QCheckBox(self)
        self.checkBox_activated = QtGui.QCheckBox(self)
        
        self.checkBox_filter = QtGui.QCheckBox(self)
        
        self.pushButton_go = QtGui.QPushButton(self)
        
        self.toolBar_filter.addWidget(self.checkBox_filter)
        self.toolBar_filter.addWidget(self.label_nominal)
        self.toolBar_filter.addWidget(self.comboBox_nominal)
        self.toolBar_filter.addWidget(self.checkBox_sold)
        self.toolBar_filter.addWidget(self.checkBox_activated)
        self.toolBar_filter.addWidget(self.label_date_start)
        self.toolBar_filter.addWidget(self.date_start)
        self.toolBar_filter.addWidget(self.label_date_end)
        self.toolBar_filter.addWidget(self.date_end)

        self.toolBar_filter.addWidget(self.pushButton_go)

        ######################
        
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_filter)
        self.insertToolBarBreak(self.toolBar_filter)
        
        self.actionGenerate_Cards = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGenerate_Cards.setIcon(icon)
        self.actionGenerate_Cards.setObjectName("actionGenerate_Cards")

        self.actionDelete_Cards = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete_Cards.setIcon(icon)
        self.actionDelete_Cards.setObjectName("actionDelete_Cards")
        
        self.actionEnable_Card = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("E:/tango-icon-theme-0.8.1/22x22/actions/go-first.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEnable_Card.setIcon(icon1)
        self.actionEnable_Card.setObjectName("actionEnable_Card")
        self.actionDisable_Card = QtGui.QAction(self)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("E:/tango-icon-theme-0.8.1/22x22/actions/go-last.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDisable_Card.setIcon(icon2)
        self.actionDisable_Card.setObjectName("actionDisable_Card")
        self.actionSell_Card = QtGui.QAction(self)
        
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("E:/tango-icon-theme-0.8.1/22x22/actions/edit-clear.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSell_Card.setIcon(icon3)
        self.actionSell_Card.setObjectName("actionSell_Card")
        
        self.toolBar.addAction(self.actionGenerate_Cards)
        self.toolBar.addAction(self.actionDelete_Cards)
        self.toolBar.addAction(self.actionEnable_Card)
        self.toolBar.addAction(self.actionDisable_Card)
        self.toolBar.addAction(self.actionSell_Card)        
        
        tableHeader = self.tableWidget.horizontalHeader()
        
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.actionGenerate_Cards, QtCore.SIGNAL("triggered()"),  self.generateCards)
        self.connect(self.actionDelete_Cards, QtCore.SIGNAL("triggered()"),  self.deleteCards)
        self.connect(self.actionEnable_Card, QtCore.SIGNAL("triggered()"),  self.enableCard)
        self.connect(self.actionDisable_Card, QtCore.SIGNAL("triggered()"),  self.disableCard)
        self.connect(self.pushButton_go, QtCore.SIGNAL("clicked()"),  self.refresh)
        self.connect(self.checkBox_filter, QtCore.SIGNAL("stateChanged(int)"), self.filterActions)
        
        self.retranslateUi()
        
        HeaderUtil.nullifySaved("cards_frame_header")
        
        self.filterActions()
        self.fixtures()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("cards_frame_header", bhdr)
            HeaderUtil.getHeader("cards_frame_header", self.tableWidget)
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("cards_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("cards_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex
        #===============================================================================

        
    def retranslateUi(self):

        self.tableWidget.clear()
        
        columns=['#', u'Серия', u'Номинал', u'PIN', u"Продано", u"Активиовано", u'Активировать c', u'Активировать по']
        makeHeaders(columns, self.tableWidget)
        
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Система карт оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_filter.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGenerate_Cards.setText(QtGui.QApplication.translate("MainWindow", "Сгенерировать партию", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete_Cards.setText(QtGui.QApplication.translate("MainWindow", "Удалить карты", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEnable_Card.setText(QtGui.QApplication.translate("MainWindow", "Активна", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisable_Card.setText(QtGui.QApplication.translate("MainWindow", "Неактивна", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSell_Card.setText(QtGui.QApplication.translate("MainWindow", "Продать", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nominal.setText(QtGui.QApplication.translate("MainWindow", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_filter.setText(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_start.setText(QtGui.QApplication.translate("MainWindow", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_end.setText(QtGui.QApplication.translate("MainWindow", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_sold.setText(QtGui.QApplication.translate("MainWindow", "Проданные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_activated.setText(QtGui.QApplication.translate("MainWindow", "Активированные", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_go.setText(QtGui.QApplication.translate("MainWindow", "Фильтровать", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.setColumnHidden(0, True)

        
    def fixtures(self):
        nominals = self.connection.sql("SELECT nominal FROM billservice_card GROUP BY nominal")
        self.comboBox_nominal.clear()
        for nom in nominals:
            
            self.comboBox_nominal.addItem(unicode(nom.nominal))
            
    def filterActions(self):
        if self.checkBox_filter.checkState()==2:
            self.label_nominal.setDisabled(False)
            self.comboBox_nominal.setDisabled(False)
            self.label_date_start.setDisabled(False)
            self.date_start.setDisabled(False)
            self.label_date_end.setDisabled(False)
            self.date_end.setDisabled(False)
            self.checkBox_sold.setDisabled(False)
            self.checkBox_activated.setDisabled(False)
            self.pushButton_go.setDisabled(False)
        else:
            self.label_nominal.setDisabled(True)
            self.comboBox_nominal.setDisabled(True)
            self.label_date_start.setDisabled(True)
            self.date_start.setDisabled(True)
            self.label_date_end.setDisabled(True)
            self.date_end.setDisabled(True)
            self.checkBox_sold.setDisabled(True)
            self.checkBox_activated.setDisabled(True)
            self.pushButton_go.setDisabled(True)
            self.refresh()
            
    def enableCard(self):
        for index in self.tableWidget.selectedIndexes():
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=False
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()
 
            except Exception, e:
                pass   
        
        self.refresh()
    
    def disableCard(self):
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=True
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()

            except Exception, e:
                pass        
        
        self.refresh()
        
    def deleteCards(self):
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                self.connection.iddelete("billservice_card", int(i))
            except Exception, e:
                pass  
            
        self.connection.commit()    
        self.refresh()     

    def generateCards(self):

        #print model.id
        
        last_series = self.connection.get("SELECT MAX(series) as series FROM billservice_card").series
        if last_series==None:
            last_series=0
        else:
            last_series+=1
        child=AddCards(connection=self.connection, last_series=last_series)
        if child.exec_()==1:
            self.refresh()
            self.fixtures()
        
        
    def refresh(self, widget=None):
        
        sql = """SELECT * FROM billservice_card"""
        if self.checkBox_filter.checkState()==2:
            start_date = self.date_start.dateTime().toPyDateTime()
            end_date = self.date_end.dateTime().toPyDateTime()
            sql+=" WHERE id>0 "
            if unicode(self.comboBox_nominal.currentText())!="":
                sql+=" AND nominal = '%s'" % unicode(self.comboBox_nominal.currentText())
                
            if self.checkBox_activated.checkState() == 2:
                sql+=" AND activated>'%s' and activated<'%s'" % (start_date, end_date)
            
            if self.checkBox_sold.checkState() == 2:
                sql+=" AND sold>'%s' and sold<'%s'" % (start_date, end_date)
                
            if self.checkBox_sold.checkState() == 0 and self.checkBox_activated.checkState() == 0:
                sql+=" AND start_date>'%s' and end_date<'%s'" % (start_date, end_date)
            
        self.tableWidget.setSortingEnabled(False)

            
        self.tableWidget.clearContents()

        nodes = self.connection.sql(sql)
        self.tableWidget.setRowCount(len(nodes))
        sql+=" ORDER BY id ASC"
        i=0        
        
        for node in nodes:

            self.addrow(node.id, i,0, status = node.disabled, activated=node.activated)
            self.addrow(node.series, i,1, status = node.disabled, activated=node.activated)
            self.addrow(node.nominal, i,2, status = node.disabled, activated=node.activated)
            self.addrow(node.pin, i,3, status = node.disabled, activated=node.activated)
            self.addrow(node.sold, i,4, status = node.disabled, activated=node.activated)
            self.addrow(node.activated, i,5, status = node.disabled, activated=node.activated)
            self.addrow(node.start_date.strftime(self.strftimeFormat), i,6, status = node.disabled, activated=node.activated)
            self.addrow(node.end_date.strftime(self.strftimeFormat), i,7, status = node.disabled, activated=node.activated)
            #self.tableWidget.setRowHeight(i, 17)
            i+=1
            
        self.tableWidget.setColumnHidden(0, False)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader("cards_frame_header", self.tableWidget)
        self.tableWidget.setSortingEnabled(True)
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("cards_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("cards_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex


    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("cards_frame_header", self.tableWidget)
            
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

    def getTimeperiodId(self):
        return self.treeWidget.currentItem().id
    

    def addrow(self, value, x, y, status, activated):
        headerItem = QtGui.QTableWidgetItem()
        
        #print 'activated',activated
        if value == None:
            value = ""
        headerItem.setText(unicode(value))
        if status==True:
            headerItem.setTextColor(QtGui.QColor('#FF0100'))
        if activated == None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/ok.png"))
        elif activated!=None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/false.png"))
    
        self.tableWidget.setItem(x,y,headerItem)
        

        
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delConsAction.setDisabled(True)
        else:
            self.delConsAction.setDisabled(False)


    def addNodeLocalAction(self):
        if self.treeWidget.currentItem() is None:
            self.addConsAction.setDisabled(True)
            self.delConsAction.setDisabled(True)
            self.delPeriodAction.setDisabled(True)
        else:
            self.addConsAction.setDisabled(False)
            self.delConsAction.setDisabled(False)
            self.delPeriodAction.setDisabled(False)
            


class CardPreviewDialog(QtGui.QDialog):
    def __init__(self, url):
        
        super(CardPreviewDialog, self).__init__()
        self.setObjectName("CardPreviewDialog")
        #self.filelist=[]
        self.url = url
        self.resize(636, 454)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.card_webView = QtWebKit.QWebView()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.card_webView.sizePolicy().hasHeightForWidth())
        self.card_webView.setSizePolicy(sizePolicy)
        self.card_webView.setUrl(QtCore.QUrl("about:blank"))
        self.card_webView.setObjectName("card_webView")
        self.gridLayout.addWidget(self.card_webView, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)
        self.retranslateUi()
        self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("CardPreviewDialog", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        
    def fixtures(self):
        lfurl = QtCore.QUrl.fromLocalFile(os.path.abspath(self.url))
        self.card_webView.load(lfurl)