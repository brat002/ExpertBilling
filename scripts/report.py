#-*- coding= utf-8 -*-

import psycopg2
import psycopg2.extras
import datetime

host = '127.0.0.1'
port = '5430'
database = 'ebs'
user = 'ebs'
password = 'ebspassword'

start_date=datetime.datetime.now()-datetime.timedelta(days=570)
end_date = datetime.datetime.now()
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(0)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
tarif_id=36
cur.execute("""SELECT id, username, (SELECT traffic_transmit_service_id FROM billservice_tariff WHERE id=%s) as traffic_transmit_service_id FROM billservice_account WHERE get_tarif(id)=%s""", (tarif_id,tarif_id,))


rows = cur.fetchall()

for row in rows:
    cur.execute("""
    SELECT group_id, sum(bytes) as size, (SELECT name FROM billservice_group WHERE id=gpst.group_id) as group_name FROM billservice_groupstat as gpst
            WHERE account_id=%s and datetime>%s and datetime<%s GROUP BY group_id;
    """, (row['id'], start_date, end_date))
    print 
    groups = cur.fetchall()
    print "ACCOUNT %s(%s)" % (row['username'], row['id'])
    print "\t Usage of traffic:"
    for group in groups:
        
        print "\t %s " % group['group_name'].decode("utf-8")
        print "\t %s " % group['size']

    cur.execute("""
            SELECT   ppt.size as size, ppt.datetime, pp.size as pp_size, (SELECT name FROM billservice_group WHERE id=pp.group_id) as group_name FROM billservice_accountprepaystrafic as ppt
            JOIN billservice_prepaidtraffic as pp ON pp.id=ppt.prepaid_traffic_id
            WHERE account_tarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1);""", (row['id'],)  )
    prepaids=cur.fetchall()
    print "\t Prepaid:"
    for prepaid in prepaids:
        print "\t %s " % prepaid['group_name'].decode("utf-8")
        print u"Начислено/Остаток\t %s/%s" % (prepaid['pp_size'],  prepaid['size'])

    cur.execute("""SELECT sum(summ) as summ from billservice_traffictransaction WHERE account_id=%s and datetime between %s and %s """, (row['id'], start_date, end_date))
    sum=cur.fetchone()
    print u"Списано за трафик на: %s" % sum['summ']
         
    cur.execute("""SELECT sum(summ) as summ from billservice_periodicalservicehistory WHERE account_id=%s and datetime between %s and %s """, (row['id'], start_date, end_date))
    sum=cur.fetchone()
    print u"Списано периодических услуг на: %s" % sum['summ']
    print "===="*10
    
    
    