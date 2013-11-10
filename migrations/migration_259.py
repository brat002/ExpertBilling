#-*-coding= utf-8 -*-

from lib import get_cursor


cur = get_cursor()


def pre_migrate():
    pass


def post_migrate():
    cur.execute("select tablename FROM pg_tables WHERE schemaname='public' and tablename LIKE 'billservice_balancehistory%';")
    
    for table in cur.fetchall():
        dt = table[0].replace('billservice_balancehistory', '')
        if not dt: continue
        cur.execute("""ALTER TABLE billservice_balancehistory%s DROP INDEX billservice_balancehistory%s_account_id; 
                       CREATE INDEX billservice_balancehistory%s_account_id_datetime
      ON billservice_balancehistory%s
      USING btree
      (account_id, datetime);""" % (dt, dt, dt))
        
    cur.connection.commit()