# -*- coding: utf-8 -*-


from django_tables2.tables import Table
from django_tables2_reports.tables import TableReport


class EbsadminTable(Table):

    def __init__(self, *args, **argv):
        super(EbsadminTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        attrs = {
            'class': 'table table-disable-hover table-bordered table-condensed'
        }


class EbsadminTableReport(TableReport):

    def __init__(self, *args, **argv):
        super(EbsadminTableReport, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        attrs = {
            'class': 'table table-bordered table-condensed'
        }
