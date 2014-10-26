#-*-coding= utf-8 -*-

from lib import get_cursor


cur = get_cursor()


def pre_migrate():
    pass


def post_migrate():
    cur.connection.set_isolation_level(0)
    cur.execute("select tablename FROM pg_tables WHERE schemaname='public' and tablename LIKE 'billservice_balancehistory%';")
....
    for table in cur.fetchall():
        dt = table[0].replace('billservice_balancehistory', '')
        if not dt: continue
        if not dt.startswith('20131201'): continue
        try:
            cur.execute(""".
                       CREATE INDEX CONCURRENTLY billservice_balancehistory%s_id_account_id_datetime
      ON billservice_balancehistory%s
      USING btree
      (id,account_id, datetime);""" % (dt, dt))
            #cur.connection.commit()
        except Exception, e:
            print e
