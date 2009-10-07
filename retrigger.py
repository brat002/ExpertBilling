import ConfigParser
import psycopg2, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from dateutil.relativedelta import relativedelta
import datetime

from utilites import get_connection

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    db_dsn = "dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                                config.get("db", "host"), config.get("db", "password"))
    conn = get_connection(db_dsn)
    cur = conn.cursor()
    start_date = datetime.datetime(2008,9,1)
    end_date   = datetime.datetime.now()
    month = relativedelta(months=1)
    
    while start_date < end_date:
        d1 = "CREATE TRIGGER acc_psh_trg AFTER UPDATE OR DELETE ON psh%s FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();" % start_date.strftime("%Y%m01")
        try:
            cur = conn.cursor()
            cur.execute(str(d1))
        except:
            pass
        cur.connection.commit()
        start_date += month
