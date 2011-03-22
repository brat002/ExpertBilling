import MySQLdb
import datetime
import psycopg2
import psycopg2.extras

#utm_tarif_id:ebs_tarif_id
tarifs={'1':'23','2':'23','4':'23','5':'23','6':'23','7':'23','8':'27','9':'22','10':'19','11': '17','12':'23','13':'22','14': '22','15': '19','16':'17','21':'23','22': '22','23':'19','24':'17','25':'18','26':'20','27':'27','28':'6','29':'7','30':'8','31':'25'}


db=MySQLdb.connect(host="localhost",user="root", passwd="",db="utm")

start_date = datetime.datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0)
m_cursor=db.cursor()

m_cursor.execute("""
SELECT u.login, u.password, u.passport, u.full_name, u.actual_address, u.work_telephone, u.home_telephone,
u.mobile_telephone,u.flat_number, u.connect_date, a.balance,atl.tariff_id FROM users as u
JOIN accounts as a ON a.id=u.basic_account
JOIN account_tariff_link as atl ON atl.account_id=u.basic_account
WHERE atl.is_deleted=0;
""")

try:
    conn = psycopg2.connect("dbname='ebs_new' user='ebs' host='127.0.0.1' password='ebspassword' port='5432'");
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(1)
p_cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
nas_id=4
status=2
transfer_accounts=True
transfer_ballances=True
for x in m_cursor.fetchall():

    #for i in x:
    #    print i
    
    created=datetime.datetime.fromtimestamp(float(x[9]))   
    try: 
        print x[0],x[2], x[4]
    except Exception, e:
        print e
    if transfer_accounts:
        p_cursor.execute("""
        INSERT INTO billservice_account(
                 username, "password", fullname, street, nas_id,  
                assign_ipn_ip_from_dhcp, created, 
                room, allow_webcab, allow_expresscards, 
                assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block, 
                passport, phone_h, phone_m, 
                status 
                )
        VALUES ( %s, %s, %s, %s, %s, 
                True, %s, %s,
                True, True, True, True, True, True, %s, %s, %s,%s) RETURNING id;    
        """, (x[0], x[1], x[3], x[4], nas_id, created, x[8],x[2],x[6],x[7], status))
        
        account_id=p_cursor.fetchone()['id']
        print x[11]
        p_cursor.execute("""
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s)
        """, (account_id, tarifs.get(str(x[11]), 23), start_date))
    if transfer_ballances:
        cur.execute("SELECT id FROM billservise_account WHERE username=%s;", (x[0],))
        account_id=cur.fetchone()['id']
        cur.execute("SELECT id FROM billservise_accountttarif WHERE account_id=%s and datetime<now() ORDER BY DESC LIMIT 1;", (account_id,))
        accounttarif_id=cur.fetchone()['id']
        
        cur.execute("UPDATE billservice_account SET ballance=%s WHERE id=%s", (x[10], account_id))
        cur.execute(u"""
            INSERT INTO billservice_transaction(
                        bill, account_id, type_id, approved, summ, description, 
                        created,  accounttarif_id)
                VALUES ('', %s, 'MANUAL_TRANSACTION', True, %s, 'Перенос баланса', now(), %s);
        """, (account_id,x[10],accounttarif_id))
    print "==="*10

conn.rollback()
