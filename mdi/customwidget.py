#-*-coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import datetime
from dateutil.relativedelta import relativedelta
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class CustomDateTimeWidget(QtGui.QWidget):
    
    def __init__(self):      
        super(CustomDateTimeWidget, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        #self.setMinimumSize(1, 30)
        #self.value = 75
        #self.num = [75, 150, 225, 300, 375, 450, 525, 600, 675]
        
        #self.connect(self, QtCore.SIGNAL("updateBurningWidget(int)"), 
        #    self.setValue)
        self.setObjectName(_fromUtf8("CustomDateTimeWidget"))
        self.resize(230, 22)
        #self.setMinimumHeight(32)
        
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.dateTimeEdit = QtGui.QDateTimeEdit(self)
        self.dateTimeEdit.setAutoFillBackground(False)
        self.dateTimeEdit.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName(_fromUtf8("dateTimeEdit"))
        self.dateTimeEdit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.dateTimeEdit.setFrame(True)
        self.dateTimeEdit.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.dateTimeEdit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.horizontalLayout.addWidget(self.dateTimeEdit)
        self.toolButton_now = QtGui.QToolButton(self)
        #self.toolButton_now.setMinimumSize(QtCore.QSize(22, 0))
        self.toolButton_now.setObjectName(_fromUtf8("toolButton_now"))
        self.horizontalLayout.addWidget(self.toolButton_now)
        self.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.nowAct = QtGui.QAction(u"&Сейчас", self)
        self.connect(self.nowAct, QtCore.SIGNAL("triggered()"), self.set_now)

        self.nowAct_00 = QtGui.QAction(u"&Сегодня 00:00:00", self)
        self.connect(self.nowAct_00, QtCore.SIGNAL("triggered()"), self.set_now_00)
        
        self.yesterdayAct = QtGui.QAction(u"&Вчера", self)
        self.connect(self.yesterdayAct, QtCore.SIGNAL("triggered()"), self.set_yesterday)

        self.yesterdayAct_00 = QtGui.QAction(u"&Вчера 00:00:00", self)
        self.connect(self.yesterdayAct_00, QtCore.SIGNAL("triggered()"), self.set_yesterday_00)

        self.tomorrowAct = QtGui.QAction(u"&Завтра", self)
        self.connect(self.tomorrowAct, QtCore.SIGNAL("triggered()"), self.set_tomorrow)

        self.tomorrowAct_00 = QtGui.QAction(u"&Завтра 00:00:00", self)
        self.connect(self.tomorrowAct_00, QtCore.SIGNAL("triggered()"), self.set_tomorrow_00)

        self.monthAct = QtGui.QAction(u"&Месяц назад", self)
        self.connect(self.monthAct, QtCore.SIGNAL("triggered()"), self.set_month)

        self.monthAct_00 = QtGui.QAction(u"&Начало месяца", self)
        self.connect(self.monthAct_00, QtCore.SIGNAL("triggered()"), self.set_month_00)

        self.monthAct_last_day = QtGui.QAction(u"&Конец месяца", self)
        self.connect(self.monthAct_last_day, QtCore.SIGNAL("triggered()"), self.set_month_last_day)
        
        self.yearAct_00 = QtGui.QAction(u"&Начало года", self)
        self.connect(self.yearAct_00, QtCore.SIGNAL("triggered()"), self.set_year_00)

        self.yearAct_end = QtGui.QAction(u"&Конец года", self)
        self.connect(self.yearAct_end, QtCore.SIGNAL("triggered()"), self.set_year_end)                 
        
        self.toolButton_now.addAction(self.nowAct)
        self.toolButton_now.addAction(self.nowAct_00)
        self.toolButton_now.addAction(self.yesterdayAct)
        self.toolButton_now.addAction(self.yesterdayAct_00)
        self.toolButton_now.addAction(self.tomorrowAct)
        self.toolButton_now.addAction(self.tomorrowAct_00)
        self.toolButton_now.addAction(self.monthAct)
        self.toolButton_now.addAction(self.monthAct_00)
        self.toolButton_now.addAction(self.monthAct_last_day)
        
        self.toolButton_now.addAction(self.yearAct_00)
        self.toolButton_now.addAction(self.yearAct_end)
        
        self.toolButton_now.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.toolButton_now.setPopupMode(2)
        
        self.toolButton_now.setIcon(QtGui.QIcon("images/calendar.png"))
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("CustomDateTimeWIdget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("CustomDateTimeWIdget", "dd.MM.yyyy HH:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_now.setToolTip(QtGui.QApplication.translate("CustomDateTimeWIdget", "Сейчас", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_now.setText(QtGui.QApplication.translate("CustomDateTimeWIdget", "", None, QtGui.QApplication.UnicodeUTF8))


    def setDateTime(self, now):
        self.dateTimeEdit.setDateTime(now)
        
    def setDate(self, now):
        self.dateTimeEdit.setDate(now)
                
    def currentDate(self):
        return self.dateTimeEdit.dateTime().toPyDateTime() 

    def dateTime(self):
        return self.dateTimeEdit.dateTime()
    
    def toPyDateTime(self):
        return self.dateTimeEdit.dateTime().toPyDateTime()
    
    def setCalendarPopup(self,*args,**kwargs):
        pass
    
    def setMinimumDate(self, *args, **kwargs):
        pass
    
    def setFrame(self,*args,**kwargs):
        pass
    def set_now(self):
        self.dateTimeEdit.setDateTime(datetime.datetime.now())
    
    def set_now_00(self):
        now=datetime.datetime.now()
        dt=datetime.datetime(now.year,now.month,now.day)
        self.dateTimeEdit.setDateTime(dt)

    def set_yesterday(self):
        dt=datetime.datetime.now()-datetime.timedelta(days=1)
        self.dateTimeEdit.setDateTime(dt)

    def set_yesterday_00(self):
        now=datetime.datetime.now()-datetime.timedelta(days=1)
        dt=datetime.datetime(now.year,now.month,now.day)
        self.dateTimeEdit.setDateTime(dt)
    
    def set_tomorrow(self):
        dt=datetime.datetime.now()+datetime.timedelta(days=1)
        self.dateTimeEdit.setDateTime(dt)

    def set_tomorrow_00(self):
        now=datetime.datetime.now()+datetime.timedelta(days=1)
        dt=datetime.datetime(now.year,now.month,now.day)
        self.dateTimeEdit.setDateTime(dt)   

    def set_month(self):
        dt=datetime.datetime.now()-relativedelta(months=1)
        self.dateTimeEdit.setDateTime(dt)

    def set_month_00(self):
        now=datetime.datetime.now()
        dt=datetime.datetime(now.year,now.month,1)
        self.dateTimeEdit.setDateTime(dt)  
        
    def set_year_00(self):
        now=datetime.datetime.now()
        dt=datetime.datetime(now.year,1,1)
        self.dateTimeEdit.setDateTime(dt)    
        
    def set_year_end(self):
        now=datetime.datetime.now()
        dt=datetime.datetime(now.year+1,1,1)
        self.dateTimeEdit.setDateTime(dt)    
        
    def setDisplayFormat(self,*args,**kwargs):
        pass
    
    def set_month_last_day(self):
        now=datetime.datetime.now()
        dt=datetime.datetime(now.year,now.month,1)+relativedelta(months=1)
        self.dateTimeEdit.setDateTime(dt)  
        
    