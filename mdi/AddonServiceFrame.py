#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil
from decimal import Decimal
from ebsWindow import ebsTableWindow

poolt_types=['VPN', 'IPN']

class AddServiceFrame(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(AddServiceFrame, self).__init__()
        self.model = model
        #print "model=", model
        self.connection = connection
        self.connection.commit()
        self.setObjectName("AddServiceFrame")
        self.resize(487, 737)
        self.gridLayout_3 = QtGui.QGridLayout(self)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_name = QtGui.QLabel(self)
        self.label_name.setObjectName("label_name")
        self.gridLayout_3.addWidget(self.label_name, 0, 1, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout_3.addWidget(self.lineEdit_name, 0, 2, 1, 1)
        self.label_comment = QtGui.QLabel(self)
        self.label_comment.setObjectName("label_comment")
        self.gridLayout_3.addWidget(self.label_comment, 1, 1, 1, 1)
        self.lineEdit_comment = QtGui.QLineEdit(self)
        self.lineEdit_comment.setObjectName("lineEdit_comment")
        self.gridLayout_3.addWidget(self.lineEdit_comment, 1, 2, 1, 1)
        self.checkBox_allow_activation = QtGui.QCheckBox(self)
        self.checkBox_allow_activation.setObjectName("checkBox_allow_activation")
        self.gridLayout_3.addWidget(self.checkBox_allow_activation, 2, 1, 1, 2)
        self.label_service_type = QtGui.QLabel(self)
        self.label_service_type.setObjectName("label_service_type")
        self.gridLayout_3.addWidget(self.label_service_type, 3, 1, 1, 1)
        self.comboBox_service_type = QtGui.QComboBox(self)
        self.comboBox_service_type.setObjectName("comboBox_service_type")
        self.gridLayout_3.addWidget(self.comboBox_service_type, 3, 2, 1, 1)
        self.label_sp_type = QtGui.QLabel(self)
        self.label_sp_type.setObjectName("label_sp_type")
        self.gridLayout_3.addWidget(self.label_sp_type, 4, 1, 1, 1)
        self.comboBox_sp_type = QtGui.QComboBox(self)
        self.comboBox_sp_type.setObjectName("comboBox_sp_type")

        self.gridLayout_3.addWidget(self.comboBox_sp_type, 4, 2, 1, 1)
        self.label_sp_period = QtGui.QLabel(self)
        self.label_sp_period.setObjectName("label_sp_period")
        self.gridLayout_3.addWidget(self.label_sp_period, 5, 1, 1, 1)
        self.comboBox_sp_period = QtGui.QComboBox(self)
        self.comboBox_sp_period.setObjectName("comboBox_sp_period")
        self.gridLayout_3.addWidget(self.comboBox_sp_period, 5, 2, 1, 1)
        self.label_timeperiod = QtGui.QLabel(self)
        self.label_timeperiod.setObjectName("label_timeperiod")
        self.gridLayout_3.addWidget(self.label_timeperiod, 6, 1, 1, 1)
        self.comboBox_timeperiod = QtGui.QComboBox(self)
        self.comboBox_timeperiod.setObjectName("comboBox_timeperiod")
        self.gridLayout_3.addWidget(self.comboBox_timeperiod, 6, 2, 1, 1)
        self.label_cost = QtGui.QLabel(self)
        self.label_cost.setObjectName("label_cost")
        self.gridLayout_3.addWidget(self.label_cost, 7, 1, 1, 1)
        self.lineEdit_cost = QtGui.QLineEdit(self)
        self.lineEdit_cost.setObjectName("lineEdit_cost")
        self.gridLayout_3.addWidget(self.lineEdit_cost, 7, 2, 1, 1)
        self.groupBox_cancel_subscription = QtGui.QGroupBox(self)
        self.groupBox_cancel_subscription.setCheckable(True)
        self.groupBox_cancel_subscription.setChecked(False)
        self.groupBox_cancel_subscription.setObjectName("groupBox_cancel_subscription")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_cancel_subscription)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_wyte_period = QtGui.QLabel(self.groupBox_cancel_subscription)
        self.label_wyte_period.setObjectName("label_wyte_period")
        self.gridLayout_4.addWidget(self.label_wyte_period, 0, 0, 1, 1)
        self.comboBox_wyte_period = QtGui.QComboBox(self.groupBox_cancel_subscription)
        self.comboBox_wyte_period.setObjectName("comboBox_wyte_period")
        self.gridLayout_4.addWidget(self.comboBox_wyte_period, 0, 1, 1, 1)
        self.label_wyte_cost = QtGui.QLabel(self.groupBox_cancel_subscription)
        self.label_wyte_cost.setObjectName("label_wyte_cost")
        self.gridLayout_4.addWidget(self.label_wyte_cost, 1, 0, 1, 1)
        self.lineEdit_wyte_cost = QtGui.QLineEdit(self.groupBox_cancel_subscription)
        self.lineEdit_wyte_cost.setObjectName("lineEdit_wyte_cost")
        self.gridLayout_4.addWidget(self.lineEdit_wyte_cost, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_cancel_subscription, 8, 1, 1, 2)
        self.groupBox_action = QtGui.QGroupBox(self)
        self.groupBox_action.setCheckable(True)
        self.groupBox_action.setChecked(False)
        self.groupBox_action.setObjectName("groupBox_action")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_action)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_nas = QtGui.QLabel(self.groupBox_action)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_2.addWidget(self.label_nas, 0, 0, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_action)
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout_2.addWidget(self.comboBox_nas, 0, 1, 1, 1)
        self.label_service_activation_action = QtGui.QLabel(self.groupBox_action)
        self.label_service_activation_action.setObjectName("label_service_activation_action")
        self.gridLayout_2.addWidget(self.label_service_activation_action, 1, 0, 1, 1)
        self.lineEdit_service_activation_action = QtGui.QLineEdit(self.groupBox_action)
        self.lineEdit_service_activation_action.setObjectName("lineEdit_service_activation_action")
        self.gridLayout_2.addWidget(self.lineEdit_service_activation_action, 1, 1, 1, 1)
        self.label_service_deactivation_action = QtGui.QLabel(self.groupBox_action)
        self.label_service_deactivation_action.setObjectName("label_service_deactivation_action")
        self.gridLayout_2.addWidget(self.label_service_deactivation_action, 2, 0, 1, 1)
        self.lineEdit_service_deactivation_action = QtGui.QLineEdit(self.groupBox_action)
        self.lineEdit_service_deactivation_action.setObjectName("lineEdit_service_deactivation_action")
        self.gridLayout_2.addWidget(self.lineEdit_service_deactivation_action, 2, 1, 1, 1)
        self.checkBox_deactivate_service_for_blocked_account = QtGui.QCheckBox(self.groupBox_action)
        self.checkBox_deactivate_service_for_blocked_account.setObjectName("checkBox_deactivate_service_for_blocked_account")
        self.gridLayout_2.addWidget(self.checkBox_deactivate_service_for_blocked_account, 3, 0, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_action, 9, 1, 1, 2)
        self.groupBox_change_speed = QtGui.QGroupBox(self)
        self.groupBox_change_speed.setCheckable(True)
        self.groupBox_change_speed.setChecked(False)
        self.groupBox_change_speed.setObjectName("groupBox_change_speed")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_change_speed)
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_speed_add = QtGui.QRadioButton(self.groupBox_change_speed)
        self.radioButton_speed_add.setChecked(True)
        self.radioButton_speed_add.setObjectName("radioButton_speed_add")
        self.gridLayout.addWidget(self.radioButton_speed_add, 0, 1, 1, 1)
        self.radioButton_speed_abs = QtGui.QRadioButton(self.groupBox_change_speed)
        self.radioButton_speed_abs.setObjectName("radioButton_speed_abs")
        self.gridLayout.addWidget(self.radioButton_speed_abs, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_change_speed)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.comboBox_unit = QtGui.QComboBox(self.groupBox_change_speed)
        self.comboBox_unit.setObjectName("comboBox_unit")
        self.gridLayout.addWidget(self.comboBox_unit, 1, 1, 1, 2)
        self.label_tx = QtGui.QLabel(self.groupBox_change_speed)
        self.label_tx.setObjectName("label_tx")
        self.gridLayout.addWidget(self.label_tx, 2, 1, 1, 1)
        self.label_rx = QtGui.QLabel(self.groupBox_change_speed)
        self.label_rx.setObjectName("label_rx")
        self.gridLayout.addWidget(self.label_rx, 2, 2, 1, 1)
        self.label_max = QtGui.QLabel(self.groupBox_change_speed)
        self.label_max.setObjectName("label_max")
        self.gridLayout.addWidget(self.label_max, 3, 0, 1, 1)
        self.spinBox_max_tx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_max_tx.setMaximum(100000)
        self.spinBox_max_tx.setObjectName("spinBox_max_tx")
        self.gridLayout.addWidget(self.spinBox_max_tx, 3, 1, 1, 1)
        self.spinBox_max_rx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_max_rx.setMaximum(100000)
        self.spinBox_max_rx.setObjectName("spinBox_max_rx")
        self.gridLayout.addWidget(self.spinBox_max_rx, 3, 2, 1, 1)
        self.pushButton_advanced = QtGui.QPushButton(self.groupBox_change_speed)
        self.pushButton_advanced.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_advanced.setMaximumSize(QtCore.QSize(16777215, 16))
        self.pushButton_advanced.setObjectName("pushButton_advanced")
        self.gridLayout.addWidget(self.pushButton_advanced, 4, 1, 1, 2)
        self.label_burst = QtGui.QLabel(self.groupBox_change_speed)
        self.label_burst.setObjectName("label_burst")
        self.gridLayout.addWidget(self.label_burst, 5, 0, 1, 1)
        self.spinBox_burst_tx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_tx.setMaximum(100000)
        self.spinBox_burst_tx.setObjectName("spinBox_burst_tx")
        self.gridLayout.addWidget(self.spinBox_burst_tx, 5, 1, 1, 1)
        self.spinBox_burst_rx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_rx.setMaximum(100000)
        self.spinBox_burst_rx.setObjectName("spinBox_burst_rx")
        self.gridLayout.addWidget(self.spinBox_burst_rx, 5, 2, 1, 1)
        self.label_burst_treshold = QtGui.QLabel(self.groupBox_change_speed)
        self.label_burst_treshold.setObjectName("label_burst_treshold")
        self.gridLayout.addWidget(self.label_burst_treshold, 6, 0, 1, 1)
        self.spinBox_burst_treshold_tx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_treshold_tx.setMaximum(100000)
        self.spinBox_burst_treshold_tx.setObjectName("spinBox_burst_treshold_tx")
        self.gridLayout.addWidget(self.spinBox_burst_treshold_tx, 6, 1, 1, 1)
        self.spinBox_burst_treshold_rx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_treshold_rx.setMaximum(100000)
        self.spinBox_burst_treshold_rx.setObjectName("spinBox_burst_treshold_rx")
        self.gridLayout.addWidget(self.spinBox_burst_treshold_rx, 6, 2, 1, 1)
        self.label_burst_time = QtGui.QLabel(self.groupBox_change_speed)
        self.label_burst_time.setObjectName("label_burst_time")
        self.gridLayout.addWidget(self.label_burst_time, 7, 0, 1, 1)
        self.spinBox_burst_time_tx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_time_tx.setMaximum(100000)
        self.spinBox_burst_time_tx.setObjectName("spinBox_burst_time_tx")
        self.gridLayout.addWidget(self.spinBox_burst_time_tx, 7, 1, 1, 1)
        self.spinBox_burst_time_rx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_burst_time_rx.setMaximum(100000)
        self.spinBox_burst_time_rx.setObjectName("spinBox_burst_time_rx")
        self.gridLayout.addWidget(self.spinBox_burst_time_rx, 7, 2, 1, 1)
        self.label_min = QtGui.QLabel(self.groupBox_change_speed)
        self.label_min.setObjectName("label_min")
        self.gridLayout.addWidget(self.label_min, 8, 0, 1, 1)
        self.spinBox_min_tx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_min_tx.setMaximum(100000)
        self.spinBox_min_tx.setObjectName("spinBox_min_tx")
        self.gridLayout.addWidget(self.spinBox_min_tx, 8, 1, 1, 1)
        self.spinBox_min_rx = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_min_rx.setMaximum(100000)
        self.spinBox_min_rx.setObjectName("spinBox_min_rx")
        self.gridLayout.addWidget(self.spinBox_min_rx, 8, 2, 1, 1)
        self.label_priority = QtGui.QLabel(self.groupBox_change_speed)
        self.label_priority.setObjectName("label_priority")
        self.gridLayout.addWidget(self.label_priority, 9, 0, 1, 1)
        self.spinBox_priority = QtGui.QSpinBox(self.groupBox_change_speed)
        self.spinBox_priority.setMinimum(1)
        self.spinBox_priority.setMaximum(8)
        self.spinBox_priority.setProperty("value", QtCore.QVariant(1))
        self.spinBox_priority.setObjectName("spinBox_priority")
        self.gridLayout.addWidget(self.spinBox_priority, 9, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_change_speed, 10, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_3.addWidget(self.buttonBox, 11, 2, 1, 1)
        self.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.pushButton_advanced, QtCore.SIGNAL("clicked()"), self.advancedAction)
        QtCore.QObject.connect(self.comboBox_service_type, QtCore.SIGNAL("currentIndexChanged(int)"), self.sp_typeAction)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        self.advancedAction()
        
        self.fixtures()
        #важен порядок
        self.sp_typeAction()
        self.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Дополнительные услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_name.setText(QtGui.QApplication.translate("Dialog", "Название услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_comment.setText(QtGui.QApplication.translate("Dialog", "Описание", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_activation.setText(QtGui.QApplication.translate("Dialog", "Разрешить активацию при отрицательном балансе или блокировках", None, QtGui.QApplication.UnicodeUTF8))
        self.label_service_type.setText(QtGui.QApplication.translate("Dialog", "Тип услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sp_type.setText(QtGui.QApplication.translate("Dialog", "Способ списания", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sp_period.setToolTip(QtGui.QApplication.translate("Dialog", "Для разовых услуг - время действия услуги с момента активации. Для периодических услуг - расчётный период, в течении которого с лицевого счёта абонента должны списываться деньги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sp_period.setWhatsThis(QtGui.QApplication.translate("Dialog", "Для разовых услуг - время действия услуги с момента активации. Для периодических услуг - расчётный период, в течении которого с лицевого счёта абонента должны списываться деньги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sp_period.setText(QtGui.QApplication.translate("Dialog", "Период действия", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_sp_period.setToolTip(QtGui.QApplication.translate("Dialog", "Для разовых услуг - время действия услуги с момента активации. Для периодических услуг - расчётный период, в течении которого с лицевого счёта абонента должны списываться деньги", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_sp_period.setWhatsThis(QtGui.QApplication.translate("Dialog", "Для разовых услуг - время действия услуги с момента активации. Для периодических услуг - расчётный период, в течении которого с лицевого счёта абонента должны списываться деньги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_timeperiod.setToolTip(QtGui.QApplication.translate("Dialog", "Период времени, в течении которого абоненту разрешено активировать данную услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.label_timeperiod.setWhatsThis(QtGui.QApplication.translate("Dialog", "Период времени, в течении которого абоненту разрешено активировать данную услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.label_timeperiod.setText(QtGui.QApplication.translate("Dialog", "Период активации", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_timeperiod.setToolTip(QtGui.QApplication.translate("Dialog", "Период времени, в течении которого абоненту разрешено активировать данную услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_timeperiod.setWhatsThis(QtGui.QApplication.translate("Dialog", "Период времени, в течении которого абоненту разрешено активировать данную услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.label_cost.setText(QtGui.QApplication.translate("Dialog", "Стоимость", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_cancel_subscription.setTitle(QtGui.QApplication.translate("Dialog", "Разрешить досрочное окончание подписки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_period.setToolTip(QtGui.QApplication.translate("Dialog", "Период времени, до истечения которого при окончании подписки у абонента снимется штрафная сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_period.setWhatsThis(QtGui.QApplication.translate("Dialog", "Период времени, до истечения которого при окончании подписки у абонента снимется штрафная сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_period.setText(QtGui.QApplication.translate("Dialog", "Штрафуемое время", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_wyte_period.setToolTip(QtGui.QApplication.translate("Dialog", "Период времени, до истечения которого при окончании подписки у абонента снимется штрафная сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_wyte_period.setWhatsThis(QtGui.QApplication.translate("Dialog", "Период времени, до истечения которого при окончании подписки у абонента снимется штрафная сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_cost.setToolTip(QtGui.QApplication.translate("Dialog", "Сумма штрафа за досрочное окончание подписки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_cost.setWhatsThis(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Сумма штрафа за досрочное окончание подписки</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wyte_cost.setText(QtGui.QApplication.translate("Dialog", "Стоимость", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_wyte_cost.setToolTip(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Сумма штрафа за досрочное окончание подписки</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_wyte_cost.setWhatsThis(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Сумма штрафа за досрочное окончание подписки</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_action.setTitle(QtGui.QApplication.translate("Dialog", "Действие", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("Dialog", "Выполнить на", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_nas.setItemText(0, QtGui.QApplication.translate("Dialog", "Сервер доступа абонента", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_nas.setItemText(1, QtGui.QApplication.translate("Dialog", "Mikrotik1", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_nas.setItemText(2, QtGui.QApplication.translate("Dialog", "MikroTik2", None, QtGui.QApplication.UnicodeUTF8))
        self.label_service_activation_action.setText(QtGui.QApplication.translate("Dialog", "Активировать услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.label_service_deactivation_action.setText(QtGui.QApplication.translate("Dialog", "Деактивировать услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_deactivate_service_for_blocked_account.setText(QtGui.QApplication.translate("Dialog", "Делать услугу неактивной при блокировке аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_change_speed.setTitle(QtGui.QApplication.translate("Dialog", "Изменить скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_add.setText(QtGui.QApplication.translate("Dialog", "Добавить к текущей", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_abs.setText(QtGui.QApplication.translate("Dialog", "Абсолютные значения", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Единицы измерения", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_unit.setItemText(0, QtGui.QApplication.translate("Dialog", "Kbps", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_unit.setItemText(1, QtGui.QApplication.translate("Dialog", "Mbps", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_unit.setItemText(2, QtGui.QApplication.translate("Dialog", "% от текущей скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.label_tx.setText(QtGui.QApplication.translate("Dialog", "TX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rx.setText(QtGui.QApplication.translate("Dialog", "RX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_max.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_advanced.setText(QtGui.QApplication.translate("Dialog", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst.setText(QtGui.QApplication.translate("Dialog", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_treshold.setText(QtGui.QApplication.translate("Dialog", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_time.setText(QtGui.QApplication.translate("Dialog", "Burst time(фиксировано)", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_tx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_rx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.label_min.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_priority.setText(QtGui.QApplication.translate("Dialog", "Priority(фиксировано)", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def sp_typeAction(self):
        if self.comboBox_service_type.itemData(self.comboBox_service_type.currentIndex()).toString()=='onetime':
            self.comboBox_sp_type.setDisabled(True)
        else:
            self.comboBox_sp_type.setDisabled(False)
        
    def advancedAction(self):
        if self.label_burst.isHidden()==False:
            self.label_burst.hide()
            self.spinBox_burst_tx.hide()
            self.spinBox_burst_rx.hide()
            self.label_burst_treshold.hide()
            self.spinBox_burst_treshold_tx.hide()
            self.spinBox_burst_treshold_rx.hide()
            self.label_burst_time.hide()
            self.spinBox_burst_time_tx.hide()
            self.spinBox_burst_time_rx.hide()
            self.label_min.hide()
            self.spinBox_min_tx.hide()
            self.spinBox_min_rx.hide()
            self.label_priority.hide()
            self.spinBox_priority.hide()
        else:
            self.label_burst.show()
            self.spinBox_burst_tx.show()
            self.spinBox_burst_rx.show()
            self.label_burst_treshold.show()
            self.spinBox_burst_treshold_tx.show()
            self.spinBox_burst_treshold_rx.show()
            self.label_burst_time.show()
            self.spinBox_burst_time_tx.show()
            self.spinBox_burst_time_rx.show()
            self.label_min.show()
            self.spinBox_min_tx.show()
            self.spinBox_min_rx.show()
            self.label_priority.show()
            self.spinBox_priority.show()

            

    def fixtures(self):
        self.comboBox_service_type.addItem(u"Разовая")
        self.comboBox_service_type.setItemData(0, QtCore.QVariant("onetime"))
        self.comboBox_service_type.addItem(u"Периодическая")
        self.comboBox_service_type.setItemData(1, QtCore.QVariant("periodical"))
        
        self.comboBox_sp_type.addItem(u"AT_START")
        self.comboBox_sp_type.setItemData(0, QtCore.QVariant("AT_START"))
        self.comboBox_sp_type.addItem(u"AT_END")
        self.comboBox_sp_type.setItemData(1, QtCore.QVariant("AT_END"))
        self.comboBox_sp_type.addItem(u"GRADUAL")
        self.comboBox_sp_type.setItemData(2, QtCore.QVariant("GRADUAL"))

        settlementperiods = self.connection.get_models("billservice_settlementperiod", where={'autostart':True})
        self.connection.commit()
        i=0
        self.comboBox_wyte_period.addItem(u"---Нет---")
        self.comboBox_wyte_period.setItemData(i, QtCore.QVariant(0))
        for sp in settlementperiods:
           self.comboBox_sp_period.addItem(unicode(sp.name))
           self.comboBox_sp_period.setItemData(i, QtCore.QVariant(sp.id))
           self.comboBox_wyte_period.addItem(unicode(sp.name))
           self.comboBox_wyte_period.setItemData(i+1, QtCore.QVariant(sp.id))
           i+=1 
        
        
        timeperiods = self.connection.get_models("billservice_timeperiod")
        self.connection.commit()
        i=0
        for tp in timeperiods:
           self.comboBox_timeperiod.addItem(unicode(tp.name))
           self.comboBox_timeperiod.setItemData(i, QtCore.QVariant(tp.id))
           i+=1
           
        nasses = self.connection.get_models("nas_nas")
        self.connection.commit()
        
        self.comboBox_nas.addItem(unicode(u"-Сервер доступа абонента-"))
        self.comboBox_nas.setItemData(i, QtCore.QVariant(0))
        
        i=1
        for nas in nasses:
           self.comboBox_nas.addItem(unicode(nas.name))
           self.comboBox_nas.setItemData(i, QtCore.QVariant(nas.id))
           i+=1 
           
        x = ['Kbps', 'Mbps','%']
        i=0
        for a in x:
            self.comboBox_unit.addItem(unicode(a))
            if self.model:
                if self.model.speed_units == a:
                    self.comboBox_unit.setCurrentIndex(i)
            i+=1
                   
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            self.lineEdit_comment.setText(unicode(self.model.comment))
            self.lineEdit_cost.setText(unicode(self.model.cost))
            self.checkBox_allow_activation.setChecked(self.model.allow_activation)
            
            for i in xrange(self.comboBox_service_type.count()):
                if self.comboBox_service_type.itemData(i).toString()==self.model.service_type:
                    self.comboBox_service_type.setCurrentIndex(i)

            for i in xrange(self.comboBox_sp_type.count()):
                if self.comboBox_sp_type.itemData(i).toString()==self.model.sp_type:
                    self.comboBox_sp_type.setCurrentIndex(i)

 
            for i in xrange(self.comboBox_sp_period.count()):
                if self.comboBox_sp_period.itemData(i).toInt()[0]==self.model.sp_period_id:
                    self.comboBox_sp_period.setCurrentIndex(i)           

            for i in xrange(self.comboBox_timeperiod.count()):
                if self.comboBox_timeperiod.itemData(i).toInt()[0]==self.model.timeperiod_id:
                    self.comboBox_timeperiod.setCurrentIndex(i)           

            if self.model.cancel_subscription:
                self.groupBox_cancel_subscription.setChecked(True)

                for i in xrange(self.comboBox_wyte_period.count()):
                    if self.comboBox_wyte_period.itemData(i).toInt()[0]==self.model.wyte_period_id:
                        self.comboBox_wyte_period.setCurrentIndex(i)
                        
                self.lineEdit_wyte_cost.setText(unicode(self.model.wyte_cost))     
            
            if self.model.action:
                self.groupBox_action.setChecked(True)
                for i in xrange(self.comboBox_nas.count()):
                    print self.comboBox_nas.itemData(i).toInt()[0]==self.model.nas_id, self.comboBox_nas.itemData(i).toInt()[0], self.model.nas_id
                    if self.comboBox_nas.itemData(i).toInt()[0]==self.model.nas_id:
                        self.comboBox_nas.setCurrentIndex(i)                
                self.lineEdit_service_activation_action.setText(unicode(self.model.service_activation_action))
                self.lineEdit_service_deactivation_action.setText(unicode(self.model.service_deactivation_action))
                self.checkBox_deactivate_service_for_blocked_account.setChecked(self.model.deactivate_service_for_blocked_account)
            
            if self.model.change_speed:
                self.groupBox_change_speed.setChecked(True)
                if self.model.change_speed_type=='abs':
                    self.radioButton_speed_abs.setChecked(True)

                self.spinBox_max_tx.setValue(int(self.model.max_tx))
                self.spinBox_max_rx.setValue(int(self.model.max_rx))
                if int(self.model.burst_tx) or int(self.model.burst_rx) or int(self.model.burst_treshold_tx) or int(self.model.burst_treshold_rx) or int(self.model.burst_time_tx) or int(self.model.burst_time_rx) or int(self.model.min_tx) or int(self.model.min_rx):
                    self.spinBox_burst_tx.setValue(int(self.model.burst_tx))
                    self.spinBox_burst_rx.setValue(int(self.model.burst_rx))
        
                    self.spinBox_burst_treshold_tx.setValue(int(self.model.burst_treshold_tx))
                    self.spinBox_burst_treshold_rx.setValue(int(self.model.burst_treshold_rx))
        
                    self.spinBox_burst_time_tx.setValue(int(self.model.burst_time_tx))
                    self.spinBox_burst_time_rx.setValue(int(self.model.burst_time_rx))
                    
                    self.spinBox_min_tx.setValue(int(self.model.min_tx))
                    self.spinBox_min_rx.setValue(int(self.model.min_rx))
                    
                    self.spinBox_priority.setValue(int(self.model.priority))
                    self.label_burst.show()
                    self.spinBox_burst_tx.show()
                    self.spinBox_burst_rx.show()
                    self.label_burst_treshold.show()
                    self.spinBox_burst_treshold_tx.show()
                    self.spinBox_burst_treshold_rx.show()
                    self.label_burst_time.show()
                    self.spinBox_burst_time_tx.show()
                    self.spinBox_burst_time_rx.show()
                    self.label_min.show()
                    self.spinBox_min_tx.show()
                    self.spinBox_min_rx.show()
                    self.label_priority.show()
                    self.spinBox_priority.show()
                else:
                    #self.spinBox_max_tx.setValue(0)
                    #self.spinBox_max_rx.setValue(0)
                    
                    self.spinBox_burst_tx.setValue(0)
                    self.spinBox_burst_rx.setValue(0)
        
                    self.spinBox_burst_treshold_tx.setValue(0)
                    self.spinBox_burst_treshold_rx.setValue(0)
        
                    self.spinBox_burst_time_tx.setValue(0)
                    self.spinBox_burst_time_rx.setValue(0)
                    
                    self.spinBox_min_tx.setValue(0)
                    self.spinBox_min_rx.setValue(0)
                    
                    self.spinBox_priority.setValue(8)
                    self.label_burst.hide()
                    self.spinBox_burst_tx.hide()
                    self.spinBox_burst_rx.hide()
                    self.label_burst_treshold.hide()
                    self.spinBox_burst_treshold_tx.hide()
                    self.spinBox_burst_treshold_rx.hide()
                    self.label_burst_time.hide()
                    self.spinBox_burst_time_tx.hide()
                    self.spinBox_burst_time_rx.hide()
                    self.label_min.hide()
                    self.spinBox_min_tx.hide()
                    self.spinBox_min_rx.hide()
                    self.label_priority.hide()
                    self.spinBox_priority.hide()
                
            else:
                self.spinBox_max_tx.setValue(0)
                self.spinBox_max_rx.setValue(0)
                
                self.spinBox_burst_tx.setValue(0)
                self.spinBox_burst_rx.setValue(0)
    
                self.spinBox_burst_treshold_tx.setValue(0)
                self.spinBox_burst_treshold_rx.setValue(0)
    
                self.spinBox_burst_time_tx.setValue(0)
                self.spinBox_burst_time_rx.setValue(0)
                
                self.spinBox_min_tx.setValue(0)
                self.spinBox_min_rx.setValue(0)
                
                self.spinBox_priority.setValue(8)
                self.label_burst.hide()
                self.spinBox_burst_tx.hide()
                self.spinBox_burst_rx.hide()
                self.label_burst_treshold.hide()
                self.spinBox_burst_treshold_tx.hide()
                self.spinBox_burst_treshold_rx.hide()
                self.label_burst_time.hide()
                self.spinBox_burst_time_tx.hide()
                self.spinBox_burst_time_rx.hide()
                self.label_min.hide()
                self.spinBox_min_tx.hide()
                self.spinBox_min_rx.hide()
                self.label_priority.hide()
                self.spinBox_priority.hide()


    def accept(self):
        if self.model:
            model = self.model
        else:
            model = Object()
            
        
        model.name = unicode(self.lineEdit_name.text())
        model.comment = unicode(self.lineEdit_comment.text())
        model.cost = Decimal(unicode(self.lineEdit_cost.text() or 0))
        model.allow_activation = self.checkBox_allow_activation.isChecked()==True
        model.service_type = unicode(self.comboBox_service_type.itemData(self.comboBox_service_type.currentIndex()).toString())
        
        model.sp_type = unicode(self.comboBox_sp_type.itemData(self.comboBox_sp_type.currentIndex()).toString())
        model.sp_period_id = self.comboBox_sp_period.itemData(self.comboBox_sp_period.currentIndex()).toInt()[0]
        model.timeperiod_id = self.comboBox_timeperiod.itemData(self.comboBox_timeperiod.currentIndex()).toInt()[0]
        model.cancel_subscription = self.groupBox_cancel_subscription.isChecked()==True
        
        if model.cancel_subscription==True:
            model.wyte_period_id = None if self.comboBox_wyte_period.itemData(self.comboBox_wyte_period.currentIndex()).toInt()[0]==0 else self.comboBox_wyte_period.itemData(self.comboBox_wyte_period.currentIndex()).toInt()[0]
            model.wyte_cost = Decimal(unicode(self.lineEdit_wyte_cost.text() or 0))
        
        model.action = self.groupBox_action.isChecked()==True
        
        if model.action == True:
            #print "nas_id=", self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
            model.nas_id = None if self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0] == 0 else self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
            model.service_activation_action = unicode(self.lineEdit_service_activation_action.text())
            model.service_deactivation_action = unicode(self.lineEdit_service_deactivation_action.text())
            model.deactivate_service_for_blocked_account = self.checkBox_deactivate_service_for_blocked_account.isChecked() == True
            
        model.change_speed = self.groupBox_change_speed.isChecked()==True
        if model.change_speed:
            model.speed_units = unicode(self.comboBox_unit.currentText())
            model.change_speed_type = "add" if self.radioButton_speed_add.isChecked() == True else "abs"
            model.max_tx = unicode(self.spinBox_max_tx.value())
            model.max_rx = unicode(self.spinBox_max_rx.value())
        
            if self.label_burst.isHidden()==False:
                model.burst_tx = unicode(self.spinBox_burst_tx.value())
                model.burst_rx = unicode(self.spinBox_burst_rx.value())
        
                model.burst_treshold_tx = unicode(self.spinBox_burst_treshold_tx.value())
                model.burst_treshold_rx = unicode(self.spinBox_burst_treshold_rx.value())
        
                model.burst_time_tx = unicode(self.spinBox_burst_time_tx.value())
                model.burst_time_rx = unicode(self.spinBox_burst_time_rx.value())
        
                model.min_tx = unicode(self.spinBox_min_tx.value())
                model.min_rx = unicode(self.spinBox_min_rx.value())
        
                model.priority = unicode(self.spinBox_priority.value())
            else:
                model.burst_tx = 0
                model.burst_rx = 0
        
                model.burst_treshold_tx = 0
                model.burst_treshold_rx = 0
        
                model.burst_time_tx = 0
                model.burst_time_rx = 0
        
                model.min_tx = 0
                model.min_rx = 0
        
                model.priority = 8
                

                 
        #try:
        self.connection.save(model, "billservice_addonservice")
        self.connection.commit()       
#===============================================================================
#        except Exception, e:
#            print e
#            self.connection.rollback()
#            QtGui.QMessageBox.warning(self, u"Непредвиденная ошибка", unicode(u"Данные не были сохранены."))
#            return 
#===============================================================================
        QtGui.QDialog.accept(self)



class AddonServiceEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u"#", u"Название", u"Тип услуги", u"Стоимость", u"Досрочное окончание", u"Выполнить действие", u"Изменить скорость"]
        initargs = {"setname":"addonservice_frame_header", "objname":"AddonServiceEbs", "winsize":(0,0,750,400), "wintitle":"Подключаемые услуги", "tablecolumns":columns}
        super(AddonServiceEbs, self).__init__(connection, initargs)
        
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
        self.connection.commit()
        
    def retranslateUI(self, initargs):
        super(AddonServiceEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))

        

    
    def addframe(self):
        addf = AddServiceFrame(self.connection)
        if addf.exec_()==1:
            self.refresh()


    def delete(self):
        id=self.getSelectedId()
        if (QtGui.QMessageBox.question(self, u"Удалить подключаемую услугу?" , u'''Удалить подключаемую услугу?.''', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes):
            self.connection.iddelete(id, 'billservice_addonservice')
            self.connection.commit()
            self.refresh()
    
        
    def editframe(self):
        try:
            model=self.connection.get_model(self.getSelectedId(), "billservice_addonservice")
        except:
            model=None

        addf = AddServiceFrame(connection=self.connection, model=model)
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
        self.statusBar().showMessage(u"Ожидание ответа")
        addonservices = self.connection.get_models("billservice_addonservice")
        self.connection.commit()
        self.tableWidget.setRowCount(len(addonservices))
        i=0
        for a in addonservices:
            self.addrow(a.id, i,0)
            self.addrow(a.name, i,1)
            self.addrow(a.service_type, i,2)
            self.addrow(a.cost, i,3)
            self.addrow(a.cancel_subscription, i,4)
            self.addrow(a.action, i,5)
            self.addrow(a.change_speed, i,6)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        self.statusBar().showMessage(u"Данные получены")
        self.tableWidget.setColumnHidden(0, True)

        HeaderUtil.getHeader(self.setname, self.tableWidget)
        #self.delNodeLocalAction()
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.setSortingEnabled(True)
        self.statusBar().showMessage(u"Готово")
    

    def delNodeLocalAction(self):
        super(AddonServiceEbs, self).delNodeLocalAction([self.delAction])
        
