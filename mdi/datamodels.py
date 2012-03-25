from PyQt4 import QtCore, QtGui
import datetime

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, columns=[], parent=None, *args):
        """
        @var datain: AttrDict model object
        @keyword columns: list of column names
        
        """
        
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.columns =columns
        self.int_columns = ['id', 'username', 'contract',  'tariff', 'ballance', 'credit', 'fullname',  'address',  'vpn_ips', 'ipn_ips', 'ipn_macs', 'balance_blocked', 'disabled_by_limit', 'account_online', 'created', 'comment']

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if self.arraydata:
            return len(self.int_columns)
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        try:
            value = getattr(self.arraydata[index.row()], self.int_columns[index.column()])
            status = getattr(self.arraydata[index.row()], 'status')
        except Exception, e:
            return QtCore.QVariant()
        column = self.int_columns[index.column()]
        #print "column=", column
        if role == QtCore.Qt.ForegroundRole:
            if self.int_columns[index.column()]=='ballance':
                if value<0:
                    return QtGui.QBrush(QtGui.QColor('#ffffff')) 
            return QtCore.QVariant()
        elif role == QtCore.Qt.BackgroundRole:
            if status!=1:
                return QtGui.QBrush(QtGui.QColor('#dadada')) 
            if self.int_columns[index.column()]=='ballance':
                if value<0:
                    return QtGui.QBrush(QtGui.QColor('red')) 
                elif value==0:
                    return QtGui.QBrush(QtGui.QColor('#ffdc51')) 
                else:
                    return QtCore.QVariant()
                    
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.DecorationRole:
            if column=='username':
                return QtCore.QVariant(QtGui.QIcon("images/user.png"))
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        
        
        if column=='fullname':

            return QtCore.QVariant(unicode(value if value else getattr(self.arraydata[index.row()], 'org_name')))
        
        if isinstance(value,datetime.datetime):
            return QtCore.QDateTime(value)

        return QtCore.QVariant(unicode(value))
    def currentIdByIndex(self, index):
        return  getattr(self.arraydata[index.row()], 'id')
    
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role ==QtCore.Qt.DisplayRole:
            if col<=len(self.columns):
                try:
                    return QtCore.QVariant(self.columns[col])
                except Exception, e:
                    pass
        return QtCore.QVariant()
    