# -*- coding: utf-8 -*-

import MySQLdb
import datetime
import psycopg2
import psycopg2.extras
import ipaddr
from period_utilities import settlement_period_info
import sys

#utm_tarif_id:ebs_tarif_id
tarifs={'1':'29','8':'11','9':'13','10':'12','49':'20','50':'21','51':'14','61':'15','62':'16','63': '17','64':'18','71':'5','72': '7','73': '8','74':'22','75':'23','76': '24','78':'6','79':'9','80':'10','81':'25','82':'26','999':'27','1117':'28'}

payment_types={1: "BANK", 2:'ACTIVATION_CARD', 4:'COMPENSATION', 5: 'CORRECTION', 6:'COMPENSATION', 7:'MONEY_TRANSFER'}
secret_key = "test12345678901234567890"
db1=MySQLdb.connect(host="127.0.0.1",user="root", passwd="",db="abills")

db1.set_character_set('utf8')

m_cursor1=db1.cursor()

db=MySQLdb.connect(host="127.0.0.1",user="root", passwd="",db="abills")
db.set_character_set('utf8')

m_cursor=db.cursor()



try:
    conn = psycopg2.connect("dbname='ebs' user='ebs' host='127.0.0.1' password='ebs' port='5433'");
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(1)
#p_cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
p_cursor = conn.cursor()
nas_id=4
status=2
transfer_accounts=True
transfer_ballances=True
transaction_per_day_for_gradual = 1

def transfer_accounts():
    m_cursor.execute("""
    SELECT u.id, DECODE(u.password, %s),  u.registration, u.uid, u.gid, u.disable, u.company_id, u.deleted, pi.fio, pi.phone, pi.city, pi.address_street, pi.address_build, pi._address_pod, pi._address_flor, pi.address_flat, pi.contract_id, pi.pasport_num, pi.pasport_date, pi.pasport_grant, pi._address_korp, pi._address_pod, pi._address_flor, pi._cel_phone, pi.comments, dv.tp_id, dv.registration, dv.ip,
    (SELECT deposit FROM bills WHERE uid=u.uid LIMIT 1) as deposit, u.credit, pi._address_kossp
     FROM users as u
    LEFT JOIN users_pi as pi ON pi.uid=u.uid
    LEFT JOIN dv_main as dv ON dv.uid=u.uid
    ;
    """, (secret_key))
    city_id, house_id, street_id = None, None, None
    for x in m_cursor.fetchall():
        
        a_username, a_password, a_created, a_uid, a_gid, a_disable, a_company_id, a_deleted, a_fio, a_phone, a_city, a_address_street, a_address_build, a_address_pod, a_address_flor, a_address_flat, a_contract_id, a_pasport_num, a_pasport_date, a_pasport_grant, a__address_korp, a__address_pod, a__address_flor, a__cel_phone, a_comments, a_tp_id, a_registration, a_ip, a_deposit, a_credit, a_crossport = x
        #print unicode(x[-1],  'cp1251').encode('utf-8') 

        print a_username
        #continue
        
        a_city = a_city or u"Минск"
        p_cursor.execute("SELECT id FROM billservice_city WHERE name=%s;", (a_city,))
        city = p_cursor.fetchone()
        if city:
            city_id = city[0]
        elif a_city:
            p_cursor.execute("INSERT INTO billservice_city(name) VALUES(%s) RETURNING id;", (a_city,))
            city_id = p_cursor.fetchone()[0]
        if city_id:
            p_cursor.execute("SELECT id FROM billservice_street WHERE city_id=%s and name=%s;", (city_id, a_address_street,))
            street = p_cursor.fetchone()
            if street:
                street_id = street[0]
            else:
                a_address_street = a_address_street or u"Не указана"
                p_cursor.execute("INSERT INTO billservice_street(city_id, name) VALUES(%s, %s) RETURNING id;", (city_id, a_address_street,))
                street_id = p_cursor.fetchone()[0]
                
            p_cursor.execute("SELECT id FROM billservice_house WHERE street_id=%s and name=%s;", (street_id, a_address_build,))
            house = p_cursor.fetchone()
            if house:
                house_id = house[0]
            else:
                a_address_build = a_address_build or u"Не указан"
                p_cursor.execute("INSERT INTO billservice_house(street_id, name) VALUES(%s, %s) RETURNING id;", (street_id, a_address_build,))
                house_id = p_cursor.fetchone()[0]
        
        status = 1 if a_disable == 0 else 2

        p_cursor.execute("""
        INSERT INTO billservice_account(
                 username, "password", fullname, contract, city_id, street_id, house_id, entrance, row, room, contactperson, passport, private_passport_number,  passport_given, passport_date, phone_h, phone_m, deleted,
                created, 
                allow_webcab, allow_expresscards, comment, credit, status, elevator_direction)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
               %s,
                True, True, %s, %s, %s, %s) RETURNING id;    
        """, (a_username, a_password, a_fio, a_contract_id, city_id, street_id, house_id, a_address_pod, a_address_flor, a_address_flat, a_fio, a_pasport_num, '',a_pasport_grant, a_pasport_date,  a_phone, a__cel_phone, None,
              a_created, a_comments, a_credit, status, a_crossport
              ))
        
        account_id=p_cursor.fetchone()[0]
        
        p_cursor.execute(""" 
        INSERT INTO billservice_subaccount(
            account_id, username, "password", vpn_ip_address, ipn_ip_address, 
            ipn_mac_address, nas_id, ipn_added, ipn_enabled, 
            allow_dhcp, allow_dhcp_with_null, 
            allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
            allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, 
            associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, 
            vpn_ipinuse_id, ipn_ipinuse_id, allow_ipn_with_null, 
            allow_ipn_with_minus, allow_ipn_with_block)
        VALUES (%s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, 
            %s, %s, %s, 
            %s, %s, %s, %s, 
            %s);    
        """, (account_id, a_username, a_password, str(ipaddr.IPv4Address(a_ip)),
          '0.0.0.0','', None,False,False,
          False, False,
          False,False,False,
          False,False,False,
          False,'','',True,
          None, None, False, False, False, 
          ))
        
        print a_username, a_comments
        if not tarifs.get(str(a_tp_id)):continue
        p_cursor.execute("""
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s) RETURNING id
        """, (account_id, tarifs.get(str(a_tp_id)), a_registration))
        
        accounttarif_id = p_cursor.fetchone()[0]
        
        p_cursor.execute("""
        SELECT ps.id, ps.cash_method,  sp.autostart, sp.time_start, sp.length, sp.length_in  FROM billservice_periodicalservice as ps
        JOIN billservice_settlementperiod as sp ON sp.id=ps.settlement_period_id
        WHERE tarif_id=get_tarif(%s)
        """, (account_id, ))
        for item in p_cursor.fetchall():
            ps_id, ps_type, autostart, time_start, length, length_in = item
            if autostart:
                time_start = a_registration
            time_start = datetime.datetime(*(time_start.timetuple()[:6]))
            #print time_start
            start, end, length = settlement_period_info(time_start, repeat_after=length_in, repeat_after_seconds=length)
            if ps_type == 'GRADUAL':
                start, end, length = settlement_period_info(start, repeat_after='', repeat_after_seconds=86400/transaction_per_day_for_gradual)
                
            p_cursor.execute("INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(%s,%s,%s)", (ps_id, accounttarif_id, start))

        p_cursor.execute("SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1;", (account_id,))
        accounttarif_id=p_cursor.fetchone()[0]
        
        m_cursor1.execute("SELECT `date`, `sum`, `dsc`, `id`, `method`, `ext_id`, `bill_id`, `inner_describe` FROM `payments` WHERE uid=%s", (a_uid, ))
        t_sum = 0
        for payment_item in m_cursor1.fetchall():
            p_date, p_sum, p_dsc, p_id, p_method, p_ext_id, p_bill_id, p_inner_describe = payment_item
            
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
    print "==="*10
        
    conn.commit()

def transfer_cards():
    #transfer cards
    m_cursor.execute("""
    SELECT number,  expire, sum, serial, DECODE(pin, %s), created FROM cards_users WHERE status=0
    """, (secret_key, ))
    for card in m_cursor.fetchall():
        number,  expire, sum, serial, pin, created = card
        print number,  expire, sum, serial, pin, created
        if number == 2159:continue
        try:
            p_cursor.execute(""" 
            INSERT INTO billservice_card(
                    series, pin, sold, nominal, start_date, 
                    end_date, created, type, ext_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,0, %s);
            """, (1, pin, created, sum, created, expire, created, u"%s%s" % (serial, number)))
        except Exception, e:
            print e
        
    conn.commit()
    
if __name__ == '__main__':
    if sys.argv[1]=='accounts':
        transfer_accounts()
    if sys.argv[1]=='cards':
        transfer_cards()
        
