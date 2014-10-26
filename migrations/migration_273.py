#-*-coding= utf-8 -*-

from lib import get_cursor
import datetime
from dateutil.relativedelta import relativedelta

cur = get_cursor()


def pre_migrate():
    pass


def post_migrate():
    cur.execute("select tablename FROM pg_tables WHERE schemaname='public' and tablename LIKE 'billservice_balancehistory%';")
    
    for table in cur.fetchall():
        dt = table[0].replace('billservice_balancehistory', '')
        
        p_dt = datetime.datetime.strptime(dt, "%Y%m%d")
        
        f_dt = p_dt.strftime("%Y-%m-%d")
        t_dt = (p_dt+relativedelta(months=1)).strftime("%Y-%m-%d")
        
        if not dt: continue
        sql = """ ALTER TABLE %s DROP CONSTRAINT billservice_balancehistory%s_datetime_check;
                ALTER TABLE %s ADD CONSTRAINT billservice_balancehistory%s_datetime_check
            CHECK (datetime >= '%s'::timestamp without time zone AND datetime < '%s'::timestamp without time zone)
            """ % (table[0], dt, table[0], 
                     dt, f_dt, t_dt,
                     )
        print sql

        cur.execute(sql)
        
    cur.connection.commit()