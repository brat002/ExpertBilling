import MySQLdb
import datetime
import psycopg2
import psycopg2.extras
import sys
from period_utilities import settlement_period_info
#utm_tarif_id:ebs_tarif_id
tarifs={'1':'23','2':'23','4':'23','5':'23','6':'23','7':'23','8':'27','9':'22','10':'19','11': '17','12':'23','13':'22','14': '22','15': '19','16':'17','21':'23','22': '22','23':'19','24':'17','25':'18','26':'20','27':'27','28':'6','29':'7','30':'8','31':'25'}


db=MySQLdb.connect(host="localhost",user="root", passwd="",db="utm")

start_date = datetime.datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0)
m_cursor=db.cursor()

m_cursor.execute("""
SELECT a.id, u.id, u.login, u.password, u.ic_status, u.passport, u.comments, u.full_name, u.is_deleted, u.actual_address, u.work_telephone, u.home_telephone,
u.mobile_telephone,u.flat_number, u.connect_date, u.entrance, u.floor,a.balance,atl.tariff_id, atl.link_date
h.city, h.street, h.number, h.building, 
 FROM users as u
JOIN accounts as a ON a.id=u.basic_account
JOIN account_tariff_link as atl ON atl.account_id=u.basic_account
LEFT JOIN houses as h ON h.id=u.house_id
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
transaction_per_day_for_gradual = 1
transfer_accounts=True
transfer_ballances=True
city_id, house_id, street_id = None, None, None
for x in m_cursor.fetchall():

    #for i in x:
    #    print i
    
    utm_account_id, user_id, username, password, status, passport, comments, fullname, deleted, address, work_phone, home_phone, mobile_phone, flat_number, created, entrance, floor, ballance, tarif_id, link_date, city, street, house_number,  house_building = x
    created=datetime.datetime.fromtimestamp(created)
    
    status = 1 if status==2 else 3   
    try: 
        print username, password
    except Exception, e:
        print e
    
    a_city = city or u"Не указан"
    p_cursor.execute("SELECT id FROM billservice_city WHERE name=%s;", (a_city,))
    city = p_cursor.fetchone()
    if city:
        city_id = city[0]
    elif a_city:
        p_cursor.execute("INSERT INTO billservice_city(name) VALUES(%s) RETURNING id;", (a_city,))
        city_id = p_cursor.fetchone()[0]
    if city_id:
        p_cursor.execute("SELECT id FROM billservice_street WHERE city_id=%s and name=%s;", (city_id, street,))
        street = p_cursor.fetchone()
        if street:
            street_id = street[0]
        else:
            a_address_street = street or u"Не указана"
            p_cursor.execute("INSERT INTO billservice_street(city_id, name) VALUES(%s, %s) RETURNING id;", (city_id, a_address_street,))
            street_id = p_cursor.fetchone()[0]
            
        p_cursor.execute("SELECT id FROM billservice_house WHERE street_id=%s and name=%s;", (street_id, house_number,))
        house = p_cursor.fetchone()
        if house:
            house_id = house[0]
        else:
            a_address_build = house_number or u"Не указан"
            p_cursor.execute("INSERT INTO billservice_house(street_id, name) VALUES(%s, %s) RETURNING id;", (street_id, a_address_build,))
            house_id = p_cursor.fetchone()[0]
                
        p_cursor.execute("""
        INSERT INTO billservice_account(
                 username, "password", fullname, contract, city_id, street, house, entrance, row, room, contactperson, passport, private_passport_number,  passport_given, passport_date, phone_h, phone_m, deleted,
                created, 
                allow_webcab, allow_expresscards, comment, credit, status)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
               %s,
                %s, %s, %s, %s, %s) RETURNING id;    
        """, (username, password, fullname, username, city_id, street, house, entrance, floor, flat_number, fullname, passport, '', '', '', home_phone, mobile_phone, deleted, 
              created, True, True, comments, 0, status
              ))
        
        account_id=p_cursor.fetchone()[0]
        
        p_cursor.execute("""select l.login, l.password from dialup_service_links as l  JOIN service_links as sl ON sl.id=l.id WHERE l.is_deleted=0 and sl.is_deleted=0 and sl.user_id=%s;""", (user_id, ))
        d = p_cursor.fetchall()
        
        if len(d)>1:
            print 'two or more logins for account', d
            
        login, password = p_cursor.fetchone()
        
        p_cursor.execute(""" 
        INSERT INTO billservice_subaccount(
            account_id, username, "password")
        VALUES (%s, %s, %s);    
        """, (account_id, login, password),
     
          )
        
        if not tarifs.get(str(tarif_id)):continue
        p_cursor.execute("""
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s) RETURNING id
        """, (account_id, tarifs.get(str(tarif_id)), link_date))
        
        accounttarif_id = p_cursor.fetchone()[0]
        
        
        p_cursor.execute("""
        SELECT ps.id, ps.cash_method,  sp.autostart, sp.time_start, sp.length, sp.length_in  FROM billservice_periodicalservice as ps
        JOIN billservice_settlementperiod as sp ON sp.id=ps.settlement_period_id
        WHERE tarif_id=get_tarif(%s)
        """, (account_id, ))
        for item in p_cursor.fetchall():
            ps_id, ps_type, autostart, time_start, length, length_in = item
            if autostart:
                time_start = link_date
            time_start = datetime.datetime(*(time_start.timetuple()[:6]))
            #print time_start
            start, end, length = settlement_period_info(time_start, repeat_after=length_in, repeat_after_seconds=length)
            if ps_type == 'GRADUAL':
                start, end, length = settlement_period_info(start, repeat_after='', repeat_after_seconds=86400/transaction_per_day_for_gradual)
                
            p_cursor.execute("INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(%s,%s,%s)", (ps_id, accounttarif_id, start))

        p_cursor.execute("SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1;", (account_id,))
        accounttarif_id=p_cursor.fetchone()[0]
        
        m_cursor.execute("select payment_absolute, payment_enter_date from payment_transactions WHERE account_id=%s", (utm_account_id, ))
        t_sum = 0
        for payment_item in m_cursor.fetchall():
            p_sum, p_date = payment_item
            
            p_date = p_date or datetime.datetime.now()
            p_cursor.execute(u"""
                INSERT INTO billservice_transaction(
                            bill, account_id, type_id, approved, summ, description, 
                            created,  accounttarif_id)
                    VALUES (%s, %s, %s, True, %s, %s, %s, %s);
            """, (p_ext_id, account_id, payment_types.get(p_method), p_sum, p_inner_describe, p_date, accounttarif_id))
            t_sum+=p_sum
        p_cursor.execute(u"""
        INSERT INTO billservice_transaction(
                    account_id, type_id, approved, summ, description, 
                    created)
            VALUES (%s, %s, True, %s, %s, %s);
    """, (account_id, "CORRECTION", t_sum-a_deposit, u"Корректирующее списание", datetime.datetime.now(),))

conn.rollback()
