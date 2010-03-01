# -*- coding=utf-8 -*-

from __future__ import with_statement

import IPy
import time
import zlib
import signal
import hashlib
import datetime
import operator
import itertools
import traceback
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import twisted.internet
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.protocols.basic import LineReceiver, Int32StringReceiver
try:
    from twisted.internet import pollreactor
    pollreactor.install()
except:
    print 'No poll(). Using select() instead.'
from twisted.internet import reactor

import isdlogger
import saver, utilites, commands

from IPy import intToIp
from hashlib import md5
from utilites import PoD, cred, ssh_client
from decimal import Decimal
#from db import Object as Object
from daemonize import daemonize
from threading import Thread, Lock
from chartprovider.bpcdplot import cdDrawer, bpbl
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted
from utilites import settlement_period_info, readpids, killpids, savepid, rempid, getpid, check_running, in_period
from saver import allowedUsersChecker, setAllowedUsers, graceful_loader, graceful_saver
    
from classes.vars import RpcVars
from constants import rules

from rpc2.server_producer import install_logger as serv_install_logger, DBProcessingThread, PersistentDBConnection, TCP_IntStringReciever, RPCFactory
from rpc2.rpc_protocol import install_logger as proto_install_logger, RPCProtocol, ProtocolException, MD5_Authenticator, Object as Object
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from encodings import idna, ascii
NAME = 'rpc'
DB_NAME = 'db'
DEFAULT_PORT = 7771

class RPCServer(object):

    def testCredentials(self, host, login, password, cur=None, connection=None, add_data = {}):
        try:
            #print host, login, password
            a=ssh_client(host, login, password, '')
        except Exception, e:
            logger.error("Can not test credentials for nas %s %s", (host, e))
            return False
        return True

    
    def configureNAS(self, id, pptp_enable,auth_types_pap, auth_types_chap, auth_types_mschap2, pptp_ip, radius_enable, radius_server_ip,interim_update, configure_smtp, configure_gateway,protect_malicious_trafic, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT ipaddress, login, password, secret FROM nas_nas WHERE id=%s" % id)
        row = cur.fetchone()
        connection.commit()
        #print row
        confstring = ''
        #print 1
        if pptp_enable:
            auth_types=''
            #print 2
            if auth_types_pap==auth_types_chap==auth_types_mschap2:
                #print 3
                auth_types="pap, chap, mschap2"
            else:    
                if auth_types_pap==True:
                    auth_types='pap'
                    
                if auth_types_chap==True and auth_types_pap==True:
                    auth_types+=','
                    
                if auth_types_chap==True:
                    auth_types+='chap'
                    
                if auth_types_mschap2==True and (auth_types_chap==True or auth_types_pap==True):
                    auth_types+=','
                    
                if auth_types_mschap2==True:
                    auth_types+='mschap2'
                
            confstring = unicode(rules['allow_pptp'] % (pptp_ip, auth_types))
            #print 4
            #print rules['allow_pptp'] % (pptp_ip, auth_types)
            
        if radius_enable==True:
            #print rules['allow_radius'],{'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            #print rules['allow_radius'] % {'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            data = rules['allow_radius'] % (interim_update, row['secret'], radius_server_ip)
            #print data
            confstring+=unicode(data)
            #print 5
            
        if configure_smtp==True:
            confstring+=rules['smtp_protect']
            #print 6
            
        if configure_gateway==True:
            confstring+=rules['gateway']
            #print 7
        
        if protect_malicious_trafic==True:
        
            confstring+=rules['malicious_trafic']
            #print 8
        
        #print confstring
        try:
            a=ssh_client(row["ipaddress"],row["login"], row["password"], confstring)
        except Exception, e:
            logger.error("configureNAS exception %s:", repr(e))
            return False
        return True


    
    def accountActions(self, account_id, action, cur=None, connection=None, add_data = {}):

        if type(account_id) is not list:
            account_id=[account_id]
            
        for account in account_id:
            cur.execute("""SELECT account.id as account_id, account.username as username, account.password as password, account.ipn_ip_address as ipn_ip_address,
                             account.vpn_ip_address as vpn_ip_address, account.ipn_mac_address as  ipn_mac_address,
                             nas.login as nas_login, nas.password as nas_password, nas.ipaddress as nas_ipaddress,
                             nas.user_add_action as user_add_action, nas.user_delete_action as user_delete_action, 
                             nas.user_enable_action as user_enable_action, nas.user_disable_action as user_disable_action, ap.access_type as access_type 
                             FROM billservice_account as account
                             JOIN nas_nas as nas ON nas.id = account.nas_id
                             JOIN billservice_tariff as tarif on tarif.id = get_tarif(account.id)
                             JOIN billservice_accessparameters as ap ON ap.id=tarif.access_parameters_id
                             WHERE account.id=%s
                             """, (account,))
    
            row = cur.fetchone()
            connection.commit()
            #print "actions", row
            #print action
            if row==None:
                return False
    
            if row['ipn_ip_address']=="0.0.0.0":
                return False
    
            if action=='disable':
                command = row['user_disable_action']
            elif action=='enable':
                command = row['user_enable_action']
            elif action=='create':
                command = row['user_add_action']
            elif action =='delete':
                command = row['user_delete_action']
            #print command
    
            sended = cred(account_id=row['account_id'], account_name=row['username'], account_password=row['password'], access_type = row['access_type'],
                          account_vpn_ip=row['vpn_ip_address'], account_ipn_ip=row['ipn_ip_address'], 
                          account_mac_address=row['ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], 
                          nas_password=row['nas_password'], format_string=command)
 
            if action=='create' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, True, row['account_id']))
                cur.execute("UPDATE billservice_accountipnspeed SET state=False WHERE account_id=%s", (row['account_id'],))
                
            elif action=='create' and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("UPDATE billservice_accountipnspeed SET state=False WHERE account_id=%s", (row['account_id'],))
            
            if action =='delete'  and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("DELETE FROM billservice_accountipnspeed WHERE account_id=%s", (row['account_id'],))
                
            elif action =='delete'  and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("DELETE FROM billservice_accountipnspeed WHERE account_id=%s", (row['account_id'],))

            if action=='disable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, row['account_id'],))
                
            if action=='enable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (True, row['account_id'],))
        
        connection.commit()

        log_string = u"""Пользователь %s выполнил nas_action %s для аккаунта %s""" % (add_data['USER_ID'][0], action, row['username'],)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        
        del account_id
        del row
        del account
        return sended

    
    def transaction_delete(self, ids, cur=None, connection=None, add_data = {}):
        for i in ids:
            #print "delete %s transaction" % i
            delete_transaction(cur, int(i))
        connection.commit()
        log_string = u"""Пользователь %s выполнил отмену проводок %s""" % (add_data['USER_ID'][0], str(ids),)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return
    
    def flush(self, cur=None, connection=None, add_data = {}):
        pass
    
    
    def get(self, sql, cur=None, connection=None, add_data = {}):
        #print sql
        if not cur:
            cur = self.cur
        cur.execute(sql)
        #connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception('Query returned more than 1 result!')
        if r==[]:
            return None
        log_string = u"""Пользователь %s выполнил SQL запрос %s""" % (add_data['USER_ID'][0], sql,)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return Object(r[0])

    
    def get_log_messages(self, systemuser_id=None, start_date=None, end_date=None, cur=None, connection=None, add_data = {}):
        sql = u"SELECT * FROM billservice_log %s"
        #cur.execute()
        
        if systemuser_id:
            sql = sql % " WHERE systemuser_id=%s and created between '%s' and '%s' ORDER BY created DESC" % (systemuser_id, start_date, end_date)
        else:
            sql = sql % " WHERE created between '%s' and '%s' ORDER BY created DESC" % (start_date, end_date)
        
        cur.execute(sql)
        result = map(Object, cur.fetchall())
        
        log_string = u"""Пользователь %s получил список логируемых действий""" % (add_data['USER_ID'][0], )
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result
    
    def get_list(self, sql, cur=None, connection=None, add_data = {}):
        #print sql
        listconnection = pool.connection()
        listconnection._con._con.set_client_encoding('UTF8')
        listcur = listconnection.cursor()
        listcur.execute(sql)
        retres = listcur.fetchall()
        listconnection.commit()
        listcur.close()
        listconnection.close()
        return retres

    
    def pay(self, account, summ, document, description, created, promise, end_promise, systemuser_id, cur=None, connection=None, add_data = {}):
        
        transaction = Object()
        transaction.account_id=account
        transaction.type_id = "CASSA_TRANSACTION"
        transaction.approved = True
        transaction.description = description
        transaction.summ=summ*(-1)
        transaction.bill=document
        transaction.systemuser_id = systemuser_id
        transaction.created = created
        
        transaction.promise = promise
        if end_promise:
            transaction.end_promise = end_promise
        
        log_string = u"""Пользователь %s выполнил платёж %s для аккаунта %s""" % (add_data['USER_ID'][0], str(transaction.__dict__).decode('unicode-escape'), account)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        
        try:
            sql = transaction.save("billservice_transaction")
            #sql = "INSERT INTO billservice_transaction(account_id, type_id, approved, description, bill, summ, created) VALUES(%s,'%s', True, '', '%s',%s, '%s') RETURNING id;" % (account, "MANUAL_TRANSACTION", document, sum*(-1), datetime.datetime.now())
            cur.execute(sql)
            id=cur.fetchall()[0]
            connection.commit()
            return Object(id)
        except Exception, e:
            logger.error('pay exception: %s', repr(e))
            return False
    
    
    def createAccountTarif(self, account, tarif, datetime, cur=None, connection=None, add_data = {}):
        
        o = Object()
        o.account_id = account
        o.tarif_id=tarif
        o.datetime = datetime
        
        log_string = u"""Пользователь %s перевёл аккаунт %s на тарифный план %s""" % (add_data['USER_ID'][0], account, tarif)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        try:
            #sql = "UPDATE billservice_account SET ballance = ballance - %f WHERE id = %d;" % (sum*(-1), account)
            sql = o.save("billservice_accounttarif")
            
            cur.execute(sql)
            connection.commit()
            return True
        except Exception, e:
            logger.error('createAccountTarif exception: %s', repr(e))
            return False

    
    def dbaction(self, fname, *args, **kwargs):
        return dbRoutine.execRoutine(fname, *args, **kwargs)
    
    
    def delete(self, model, table, cur=None, connection=None, add_data = {}):
        sql = model.delete(table)
        #print sql
        cur.execute(sql)
        #connection.commit()
        del sql
        return

    
    def list_logfiles(self, cur=None, connection=None, add_data = {}):
        return os.listdir('log/')

        
    def get_tail_log(self, log_name, count=10, all_file=False, cur=None, connection=None, add_data = {}):

        if all_file:
            return commands.getstatusoutput("cat log/%s" % log_name)
        
        return commands.getstatusoutput("tail -n %s log/%s" % (count, log_name))
    
    
    def activate_card(self, login, pin, cur=None, connection=None, add_data = {}):
        status_ok = 1
        status_bad_userpassword = 2
        status_card_was_activated =3
        now = datetime.datetime.now()
        connection.commit()
        if login and pin:
            try:
                return_status = 0
                cur.execute("SELECT * FROM billservice_card WHERE login=%s and pin=%s and sold is not Null and disabled=False FOR UPDATE;",  (login, pin, ))
                card = cur.fetchone()
                if not card: 
                    return_status =  status_bad_userpassword                
                elif card['activated'] or card['start_date']>now or card['end_date']<now: 
                    return_status =  status_card_was_activated
                if not return_status:                
                    cur.execute("SELECT * FROM billservice_ippool WHERE id=(SELECT pool_id FROM billservice_ipinuse WHERE id=%s);", (card['ipinuse_id'],))
                    pool = cur.fetchone()
                    
                    # 0 -VPN, 1 - IPN
                    if pool['type']==1:
                        cur.execute("""INSERT INTO billservice_account(username, "password", nas_id, ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
                        VALUES(%s, %s, %s, %s, False, 1, now(), False, True, True, False, False, False, False) RETURNING id;""", (login, pin, card['nas_id'], card['ip'], ))
                    else:
                        cur.execute("""INSERT INTO billservice_account(username, "password", nas_id, vpn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
                        VALUES(%s, %s, %s, %s, False, 1, now(), False, True, True, False, False, False, False) RETURNING id;""", (login, pin, card['nas_id'], card['ip'], ))
                        
                    account_id = cur.fetchone()['id']
            
                    cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s);", (account_id, card['tarif_id'], now))
                    
                    cur.execute(u"""
                    INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
                    VALUES('Активация карты доступа', %s, 'ACCESS_CARD', True, %s, %s*(-1),'', %s, False, Null);
                    """, (account_id, card["tarif_id"], card['nominal'], now))
            
                    cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s WHERE id = %s;", (now, account_id, card['id']))
                    return_status = status_ok
                    
                connection.commit()    
                return return_status
            except Exception, e:
                logger.error("Error activate card %s, %s", (login, repr(e)))
                connection.rollback()
                return
                            
        #cur.execute(sql)
        #connection.commit()
        #del sql
        return
    
    
    def change_tarif(self, accounts, tarif, date, cur=None, connection=None, add_data = {}):
        connection.commit()
        for account in accounts:
            try:
                log_string = u"""Пользователь %s перевёл аккаунты %s на тарифный план %s""" % (add_data['USER_ID'][0], str(accounts), tarif)
                
                cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
                cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s,%s,%s)", (account, tarif, date))
            except Exception, e:
                connection.rollback()
                logger.error("Error change tarif for account %s, %s", (account, e))
                return False
        connection.commit()
        return True
                
            

    
    def activate_pay_card(self, account_id, serial, card_id, pin, cur=None, connection=None, add_data = {}):
        status_ok = 1
        status_bad_userpassword = 2
        status_card_was_activated =3
        now = datetime.datetime.now()
        connection.commit()
        try:
            if serial and pin and card_id and account_id:
                return_value = ''
                cur.execute("SELECT * FROM billservice_card WHERE id=%s and series=%s and pin=%s and disabled=False FOR UPDATE;",  (card_id, serial, pin ))
                card = cur.fetchone()
                if not card:
                    return_value =  "CARD_NOT_FOUND"                
                elif card["sold"] is None: 
                    return_value = "CARD_NOT_SOLD"                
                elif card['activated']: 
                    return_value = "CARD_ALREADY_ACTIVATED"                
                elif card['start_date']>now or card['end_date']<now: 
                    return_value =  "CARD_EXPIRED"
                if not return_value:           
                    cur.execute(u"""
                    INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
                    VALUES('Активация карты оплаты', %s, 'PAY_CARD', True, %s, %s*(-1),'', %s, False, Null);
                    """, (account_id, card["tarif_id"], card['nominal'], now))            
                    cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s WHERE id = %s;", (now, account_id, card['id']))
                    logger.info("Card #%s series #%s pin #%s was activated", (card_id, serial, pin))
                    return_value = "CARD_ACTIVATED"
                    
                connection.commit()                
                return return_value
        except Exception, e:
            logger.error("Error activate card %s, %s", (card_id, e))
            connection.rollback()
            return "CARD_ACTIVATION_ERROR"
                            
    
    
    def iddelete(self, id, table, cur=None, connection=None, add_data = {}):
        sql = u"DELETE FROM %s where id=%d;" % (table, id)
        #print sql
        cur.execute(sql)
        log_string = u"""Пользователь %s удалил id %s из таблицы %s;""" % (add_data['USER_ID'][0], id, table)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now());""", (add_data['USER_ID'][1],log_string,))
        del table
        del id
        #connection.commit()
        return

    
    def command(self, sql, cur=None, connection=None, add_data = {}):

        cur.execute(sql)
        #connection.commit()
        del sql
        return         

    
    def commit(self, cur=None, connection=None, add_data = {}):
        connection.commit()

    
    def text_report(self, options, cur=None, connection=None, add_data = {}):
        F_NAME = 'TEXT_REP'
        NAME_PREF = 'netflow.'
        STRFTEMPLATE = '%Y-%m-%d_%H-%M'
        state_got = options[0]
        DEF_FILE_NUM = 100
        SCRIPT_STR = """ls -1 %s | mawk 'BEGIN {lines = 0}; $0 > "%s" && $0 <= "%s" { print $0; lines +=1; if (lines >=""" + str(DEF_FILE_NUM) + """) exit }'"""
        DATA_SCRIPT_STR = """mawk 'BEGIN {FS = ","; lines = 0; filename = ""; -- acc_num = split("338,368", accounts, ","); for (item in accounts) {accounts[accounts[item]] = 1; delete accounts[item]};--}; --$21 in accounts-- {print $21,$1,$10,$2,$11,$7,$22; lines = lines + 1; if (filename != FILENAME) {if (lines >= 2000) {print FILENAME; exit} else {filename = FILENAME}}}'"""
        lambda file_date: ''.join((NAME_PREF, file_date.strftime(STRFTEMPLATE)))
        def check_state():
            if (state_got in ('next', 'prev', 'home') and
                    (not F_NAME in add_data or not add_data[F_NAME])):
                raise Exception('Wrong state detected. Please load(reload) the report.')
        
        def get_first_filename(flow_dir):
            return commands.getstatusoutput('ls -1 %s | head -n 1' % flow_dir)
        def get_last_filename(flow_dir):
            return commands.getstatusoutput('ls -1 %s | head -n 1' % flow_dir)
        def check_filename(filename, name_pref):
            return filename.startswith(name_pref)
        def check_filename_exists(filename):
            return os.path.exists(filename)
        def check_filename_date(filename, date_filename):
            if filename == date_filename:
                return 0
            elif date_filename > filename:
                return 1
            else:
                return -1
        def get_next_filename(flow_dir, last_date, period, get_filename_fn):
            last_filename = get_last_filename(flow_dir)
            date_filename = get_filename_fn(last_date + period)
            if check_filename_date(last_filename, date_filename) == -1:
                pass
            else:
                raise Exception('End reached.')
        def get_files(flow_dir, start_filename, end_filename, script_str):
            return commands.getstatusoutput(script_str % (flow_dir, start_filename, end_filename))
            #[0].split('/n')
        def get_data(textReportInfo):
            #check awk for file options
            take_index = textReportInfo.last_file_num[-1]
            data_strs = []
            total_count = 0
            while True:
                if total_count >= textReportInfo.take_data_by:
                    break
                fnames = map(lambda x: ''.join((textReportInfo.flow_dir, x)), files[take_index:textReportInfo.take_files_by])
                if not fnames:
                    break                
                scr_output = commands.getstatusoutput(textReportInfo.data_script % ','.join(fnames))
                if scr_output[0]:
                    raise Exception('Text report: get data error!')
                if not scr_output[1]:
                    take_index += + len(fnames)
                    continue
                data_str = scr_output[1]
                last_str_index = data_str.rfind('\n')
                if last_str_index == -1:
                    take_index += len(fnames)
                    data_strs.append(data_str)
                    total_count +=1
                    continue
                last_str = data_str[last_str_index+1:]
                if last_str.find(textReportInfo.name_prefix) == -1:                    
                    take_index += len(fnames)
                else:
                    take_index += fnames.index(last_str)
                    data_str = data_str[:last_str_index]
                
                total_count += data_str.count('\n')
                data_strs.append(data_str)
            return (take_index, total_count, '\n'.join(data_strs).split['\n'])
        
        def get_saved_data(textReportInfo):
            return textReportInfo.read_data[textReportInfo.last_datum_num[-1], textReportInfo.take_data_by]
                    
        class TextReportInfo(object):
            start_date = None
            end_date   = None
            current_data_file = None
            got_more_files = False
            files      = []
            last_file_num = [0]
            got_more_data = False
            read_data  = []
            last_datum_num = [0]
            read_data_num = 0
            data_script = ''
            flow_dir = ''
            name_prefix = 'netflow.'
            take_files_by = 20
            take_data_by = 2000
            
            
        check_state()
        if state_got == 'start':
            add_data['text_report'] = None
            first_filename = get_first_filename(vars.FLOW_DIR)
            last_filename = get_last_filename(vars.FLOW_DIR)
            #check start_date
            #check end_date
            
            #get files
            #save files
            #get data
            #send data
        elif state_got == 'next':
            prev_data = add_data[F_NAME]
            #calc next
            #send data
        elif state_got == 'prev':
            prev_data = add_data[F_NAME]
            #calc prev
            #send data
        elif state_got == 'home':
            prev_data = add_data[F_NAME]
            #calc home
            #send data
        else:
            raise Exception('TEXT REPORT: Unknown state: %s' % state_got)
        
    def makeChart(self, *args, **kwargs):
        kwargs['cur']=None
        kwargs['connection']=None
        with vars.graph_connection_lock:
            bpbl.bpplotAdapter.rCursor = vars.graph_connection
            #bpplotAdapter.rCursor = listcur
            cddrawer = cdDrawer()
            imgs = cddrawer.cddraw(*args, **kwargs)
            vars.graph_connection.commit()
            gc.collect()
        return imgs

    
    def rollback(self, cur=None, connection=None, add_data = {}):
        connection.rollback()

    
    def sql(self, sql, return_response=True, pickler=False, cur=None, connection=None, add_data = {}):
        #print self.ticket
        #print sql
        cur.execute(unicode(sql))
        #connection.commit()
        
        #print dir(connection)
        result=[]
        a=time.clock()
        if return_response:
            result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s выполнил SQL запрос %s""" % (add_data['USER_ID'][0], unicode(sql),)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        #print "Query length=", time.clock()-a
        return result

    
    def get_limites(self, account_id, cur=None, connection=None, add_data = {}):
        limites = cur.execute("""SELECT lim.name, lim.size, lim.group_id, lim.mode, sp.time_start, sp.length, sp.length_in, sp.autostart FROM billservice_trafficlimit as lim
        JOIN billservice_settlementperiod as sp ON sp.id=lim.settlement_period_id
        WHERE lim.tarif_id=get_tarif(%s)""", (account_id,))
        limites = cur.fetchall()

        cur.execute("SELECT datetime FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY ID DESC LIMIT 1", (account_id,))
        accounttarif_date = cur.fetchone()["datetime"]
        connection.commit()
        res = []
        for limit in limites:
            limit_name = limit["name"]
            limit_size = limit["size"]
            group_id = limit["group_id"]
            mode = limit["mode"] 
            time_start = limit["time_start"]
            length = limit["length"]
            length_in = limit["length_in"]
            autostart = limit["autostart"]
            #print limit_name
            #print 3
            if autostart:
                time_start = accounttarif_date
            
            settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start, length_in, length)
            if settlement_period_start<accounttarif_date:
                settlement_period_start = accounttarif_date
            #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
            

            if mode==True:
                now = datetime.datetime.now()
                settlement_period_start=now-datetime.timedelta(seconds=delta)
                settlement_period_end=now
            
            connection.commit()

            #print 4
            cur.execute("""
            SELECT sum(bytes) as size FROM billservice_groupstat
            WHERE group_id=%s and account_id=%s and datetime>%s and datetime<%s
            """ , (group_id, account_id, settlement_period_start, settlement_period_end,))
            
            size=cur.fetchone()
            res.append({'settlement_period_start':settlement_period_start, 'settlement_period_end':settlement_period_end, 'limit_name': limit_name, 'limit_size':limit_size or 0, 'size':size["size"] or 0,})
            connection.commit()
        
        return res


    
    def get_prepaid_traffic(self, account_id, cur=None, connection=None, add_data = {}):
        cur.execute("""SELECT   ppt.id, ppt.account_tarif_id, ppt.prepaid_traffic_id,  ppt.size, ppt.datetime, pp.size, (SELECT name FROM billservice_group WHERE id=pp.group_id) as group_name FROM billservice_accountprepaystrafic as ppt
                            JOIN billservice_prepaidtraffic as pp ON pp.id=ppt.prepaid_traffic_id
                            WHERE account_tarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=175 and datetime<now() ORDER BY datetime DESC LIMIT 1);""", (account_id,))

        result = map(Object, cur.fetchall())
        return result
    
    
    def get_models(self, table='', fields = [], where={}, cur=None, connection=None, add_data = {}):
        log_string = u"""Пользователь %s получил список записей из таблицы  %s""" % (add_data['USER_ID'][0], table,)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        
        cur.execute("SELECT %s FROM %s WHERE %s ORDER BY id ASC;" % (",".join(fields) or "*", table, " AND ".join("%s=%s" % (wh, where[wh]) for wh in where) or 'id>0'))
        
        result = map(Object, cur.fetchall())
        return result


    def get_messages(self, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT * FROM billservice_news ORDER BY created DESC;")

        result = map(Object, cur.fetchall())
        return result
    
    def get_model(self, id, table='', fields = [], cur=None, connection=None, add_data = {}):
        #print "SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        sql = u"SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        
        #print sql
        cur.execute(sql)
        result=[]
        result = map(Object, cur.fetchall())
        
        #print 
        #a = open("c:/1.txt", "wb")
        #a.write("Пользователь %s получил параметры объекта %s из таблицы %s" % (add_data['USER_ID'][0], repr(result[0]), table))
        #a.close()
        log_string = u"""Пользователь %s получил параметры объекта %s из таблицы %s""" % (add_data['USER_ID'][0], str(result[0].__dict__).decode('unicode-escape'), table)
        #print s
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result[0]
    
        
    def get_notsold_cards(self, cards, cur=None, connection=None, add_data = {}):
        if len(cards)>0:
            crd = "(" + ",".join(cards) + ")"
        else:
            crd = "(0)" 
        
        cur.execute("SELECT * FROM billservice_card WHERE id IN %s AND sold is Null;" % crd)
        result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s получил список не проданных карт""" % (add_data['USER_ID'][0], )
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result
    
    
    def get_operator(self, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT * FROM billservice_operator LIMIT 1;")
        result = map(Object,cur.fetchall())
        log_string = u"""Пользователь %s получил параметры оператора %s""" % (add_data['USER_ID'][0], str(result[0].__dict__).decode('unicode-escape'))
        
        cur.execute("""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))

        return result
    
    
    def get_operator_info(self, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT operator.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_operator as operator JOIN billservice_bankdata as bankdata ON bankdata.id=operator.bank_id LIMIT 1")
        result = Object(cur.fetchone())
        cur.execute("SELECT * FROM billservice_operator LIMIT 1;")
        result = map(Object,cur.fetchall())
        log_string = u"""Пользователь %s получил параметры оператора %s""" % (add_data['USER_ID'][0], str(result[0].__dict__).decode('unicode-escape'))
        
        cur.execute("""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result[0]

    
    def get_dealer_info(self, id, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT dealer.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_dealer as dealer JOIN billservice_bankdata as bankdata ON bankdata.id=dealer.bank_id WHERE dealer.id=%s", (id, ))
        result = Object(cur.fetchone())

        log_string = u"""Пользователь %s получил параметры дилера %s """ % (add_data['USER_ID'][0], str(result.__dict__).decode('unicode-escape'))
        
        cur.execute("""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result


          
    def get_bank_for_operator(self, operator, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT * FROM billservice_bankdata WHERE id=(SELECT bank_id FROM billservice_operator WHERE id=%s)", (operator,))
        result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s получил параметры банка оператора %s """ % (add_data['USER_ID'][0], str(result[0].__dict__).decode('unicode-escape'))
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result[0]
    
          
    def get_cards_nominal(self, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT nominal FROM billservice_card GROUP BY nominal")
        result = map(Object, cur.fetchall())

        return result
    
     
    def get_accounts_for_tarif(self, tarif_id, cur=None, connection=None, add_data = {}):
        if tarif_id!=-1000:
            cur.execute("""SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name 
            FROM billservice_account AS acc 
            WHERE %s=get_tarif(acc.id) and %s IN (SELECT id FROM billservice_tariff WHERE systemgroup_id is Null or systemgroup_id IN (SELECT systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s)) ORDER BY acc.username ASC;""", (tarif_id, tarif_id, add_data['USER_ID'][1],) )
        else:
            cur.execute("""SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tarif_name
            FROM billservice_account AS acc 
            WHERE get_tarif(acc.id) IN (SELECT id FROM billservice_tariff WHERE systemgroup_id is Null or systemgroup_id IN (SELECT systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s)) ORDER BY acc.username ASC;""", (add_data['USER_ID'][1],) )
   
        result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s получил список аккаунтов для тарифного плана""" % (add_data['USER_ID'][0],)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result

    def get_accounts_for_cachier(self, fullname, city, street, house, bulk, room, username, cur=None, connection=None, add_data = {}):
        
        res={'fullname':fullname, 'city':city, 'street':street, 'house':house, 'house_bulk':bulk, 'room':room, 'username': username}
        if fullname or city or street or house or bulk or room or username:
            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name FROM billservice_account as account WHERE %s and get_tarif(id)IN (SELECT id FROM billservice_tariff WHERE systemgroup_id is Null or systemgroup_id IN (SELECT systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s))  ORDER BY username ASC;" % (' AND '.join([u"%s LIKE '%s%s%s'" % (key, "%",res[key],"%") for key in res]), add_data['USER_ID'][1],)
        else:
            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name  FROM billservice_account as account WHERE get_tarif(id)IN (SELECT id FROM billservice_tariff WHERE systemgroup_id is Null or systemgroup_id IN (SELECT systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s))ORDER BY username ASC;" % (add_data['USER_ID'][1],)

        cur.execute(sql)
        result = map(Object, cur.fetchall())
        log_string = u"""Кассир %s получил список аккаунтов""" % (add_data['USER_ID'][0],)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result
        
    def get_tariffs(self, cur=None, connection=None, add_data = {}):
        
        
        cur.execute("""SELECT id, name, active, (SELECT bsap.access_type
                   FROM billservice_accessparameters AS bsap WHERE (bsap.id=tariff.access_parameters_id) ORDER BY bsap.id LIMIT 1) AS ttype 
                   FROM billservice_tariff as tariff  
                   WHERE tariff.deleted = False and (tariff.systemgroup_id is Null or tariff.systemgroup_id in (SELECT systemgroup_id FROM billservice_systemuser_group WHERE systemuser_id=%s) )
                   ORDER BY ttype, name;""" % (add_data['USER_ID'][1]))
        result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s получил список тарифных планов""" % (add_data['USER_ID'][0],)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result
    
  
    def get_class_nodes(self, class_id, cur=None, connection=None, add_data = {}):
        cur.execute("""SELECT * FROM nas_trafficnode WHERE traffic_class_id=%s;""" % class_id)
        result = map(Object, cur.fetchall())
        
        log_string = u"""Пользователь %s получил список составляющих класса %s""" % (add_data['USER_ID'][0], class_id, )
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result  
    
      
    def delete_card(self, id, cur=None, connection=None, add_data = {}):
        cur.execute("DELETE FROM billservice_card WHERE id=%s", (id,))
        
        log_string = u"""Пользователь %s удалил карту %s""" % (add_data['USER_ID'][0], class_id, )
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return
    
      
    def get_next_cardseries(self, cur=None, connection=None, add_data = {}):
        cur.execute("SELECT MAX(series) as series FROM billservice_card")
        result = cur.fetchone()['series']
        if result==None:
            result=0
        else:
            result+=1
        #print result
        return result
    
    def create_class_node(self, class_id, name, direction, protocol=0, src_net='0.0.0.0/0', src_port=0, dst_net='0.0.0.0/0', dst_port=0, next_hop='0.0.0.0', cur=None, connection=None, add_data = {}):
        
        cur.execute("""INSERT INTO nas_trafficnode(traffic_class_id, "name", direction, protocol, src_ip, src_port, dst_ip, dst_port, next_hop)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s, %s)""", (class_id, name, direction, protocol, src_net, src_port, dst_net, dst_port, next_hop,)
                    )
        
        log_string = u"""Пользователь %s создал составляющую класса %s с параметрами""" % (add_data['USER_ID'][0], class_id, str(name, direction, protocol, src_net, src_port, dst_net, dst_port, next_hop))
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))


    def get_class_nodes(self, class_id, cur=None, connection=None, add_data = {}):
        
        cur.execute("""SELECT * FROM nas_trafficnode WHERE traffic_class_id=%s ORDER BY name, DIRECTION""", (class_id,))
        
        result = map(Object, cur.fetchall())
        log_string = u"""Пользователь %s получил составляющие класса %s""" % (add_data['USER_ID'][0], class_id,)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return result
        
    def sql_as_dict(self, sql, return_response=True, cur=None, connection=None, add_data = {}):
        #print sql
        cur.execute(sql)
        result=[]
        a=time.clock()
        if return_response:

            result =cur.fetchall()
        #print "Query length=", time.clock()-a
        return result


    
    def transaction(self, sql, cur=None, connection=None, add_data = {}):
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    
    def save(self, model, table, cur=None, connection=None, add_data = {}):

        sql = model.save(table)

        cur.execute(sql)
        
        id_fetch = cur.fetchone()
        id = id_fetch if not id_fetch else id_fetch['id']
        #a1 = cur.fetchone()
        #id = cur.fetchone()['id']
        if model.__dict__.get("id", None):
            log_string = u"""Пользователь %s обновил запись %s в таблице таблице %s""" % (add_data['USER_ID'][0], str(model.__dict__).decode('unicode-escape'), table)
        else:
            log_string = u"""Пользователь %s создал запись %s в таблице таблице %s""" % (add_data['USER_ID'][0], str(model.__dict__).decode('unicode-escape'), table)
        #log_string = "Пользователь %s получил составляющие класса %s" % (add_data['USER_ID'][0], class_id,)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return id

    
    def test(self, cur=None, connection=None, add_data = {}):
        pass

    
    def add_addonservice(self, account_id, service_id, ignore_locks = False, activation_date = None, cur=None, connection=None, add_data = {}):
        #Получаем параметры абонента
        sql = "SELECT id, ballance, balance_blocked, disabled_by_limit, status, get_tarif(id) as tarif_id,(SELECT datetime FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif_date FROM billservice_account as acc WHERE id=%s" %account_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_DOES_NOT_EXIST'
                
        account = Object(r[0]) 
        #print account_id
        
        sql = "SELECT id FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and (deactivated>now() or deactivated is Null)" % (account_id, service_id, )
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()

        if r!=[]:
            return 'SERVICE_ARE_ALREADY_ACTIVATED'
                

                
        #Получаем нужные параметры услуги
        sql = "SELECT id, name, allow_activation,timeperiod_id, change_speed FROM billservice_addonservice WHERE id = %s" % service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDON_SERVICE_DOES_NOT_EXIST'
                
        service = Object(r[0]) 

        sql = "SELECT time_start, length, repeat_after FROM billservice_timeperiodnode WHERE id IN (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=%s)" % service.timeperiod_id

        cur.execute(sql)
        connection.commit()

        timeperiods = map(Object, cur.fetchall())

        res = False
        for timeperiod in timeperiods:
            if res==True or in_period(timeperiod.time_start, timeperiod.length, timeperiod.repeat_after):
                res=True

        if res == False and ignore_locks==False:
            return "NOT_IN_PERIOD"

        if service.change_speed and ignore_locks==False:

            try:
                cur.execute("SELECT id FROM billservice_accountaddonservice WHERE deactivated is Null and service_id IN (SELECT id FROM billservice_addonservice WHERE change_speed=True) and account_id=%s" % account.id)

            except Exception, e:
                logger.error("Can not add addonservice for account %s, %s", (account_id, e))
            if cur.fetchall():

                return "ALERADY_HAVE_SPEED_SERVICE"

        # Проверка на возможность активации услуги при наличии блокировок
        if not ignore_locks:
            if service.allow_activation==False and (account.ballance<=0 or account.balance_blocked==True or account.disabled_by_limit==True or account.status!=1):
                return "ACCOUNT_BLOCKED"
        

        #Получаем нужные параметры услуги из тарифного плана
        sql = "SELECT id, activation_count, activation_count_period_id FROM billservice_addonservicetarif WHERE tarif_id=%s and service_id = %s" % (account.tarif_id, service_id)
        #print account.tarif_id, service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED'

        tarif_service = Object(r[0]) 

        if tarif_service.activation_count!=0 and ignore_locks==False:

            if tarif_service.activation_count_period_id:

                sql = "SELECT time_start, length, length_in, autostart  FROM billservice_settlementperiod WHERE id = %s" % tarif_service.activation_count_period_id

                cur.execute(sql)
                connection.commit()
                result=[]
                r=cur.fetchall()
                if len(r)>1:
                    raise Exception
        
                if r==[]:
                    return None

                settlement_period = Object(r[0]) 
                if settlement_period.autostart:
                    settlement_period.time_start = account.accounttarif_date
                    
                settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
                
                sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and activated>'%s' and activated<'%s'" % (account.id, service.id, settlement_period_start, settlement_period_end,)
            else:
                sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s" % (account.id, service.id,)
            
            cur.execute(sql)
            connection.commit()
            result=[]
            r=cur.fetchall()
            if len(r)>1:
                raise Exception
    
            if r==[]:
                return None
                    
            activations_count = Object(r[0]) 
            if activations_count.cnt>=tarif_service.activation_count: return "TOO_MUCH_ACTIVATIONS"
            
        #   log_string = u"Пользователь %s создал запись %s в таблице таблице %s" % (add_data['USER_ID'][0], str(model.__dict__).decode('unicode-escape').encode('utf-8'), table)
        log_string = u"""Пользователь %s добавил пользователю %s подключаемую услугу %s""" % (add_data['USER_ID'][0], account_id, service.name)
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        
        if activation_date:
            sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,'%s')" % (service.id, account.id, activation_date)
        else:
            sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,now())" % (service.id, account.id,)
        try:
            cur.execute(sql)
            connection.commit()
            return True
        except Exception, e:
            logger.error("Error add addonservice to account, %s", e)
            connection.rollback()
            return False
        
        
    
    def del_addonservice(self, account_id, account_service_id, cur=None, connection=None, add_data = {}):
 
        #Получаем нужные параметры аккаунта
        #connection.commit()
        cur.execute("SELECT acc.id, get_tarif(id) as tarif_id, (SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif_id FROM billservice_account as acc WHERE id = %s;", (account_id,))
        
        result=[]
        r=cur.fetchall()
        connection.commit()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_DOES_NOT_EXIST'
                
        account = Object(r[0]) 
        #Получаем нужные параметры услуги абонента
        sql = "SELECT id, service_id, account_id, activated, deactivated, action_status FROM billservice_accountaddonservice  WHERE id = %s" % account_service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST'
        accountservice = Object(r[0]) 
        #print accounservice
        #Получаем нужные параметры услуги
        sql = "SELECT id, name, service_type, cancel_subscription, wyte_period_id, wyte_cost FROM billservice_addonservice WHERE id = %s" % accountservice.service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDON_SERVICE_DOES_NOT_EXIST'
                
        service = Object(r[0]) 
        
        if service.cancel_subscription:
            
            if service.wyte_period_id:
                sql = "SELECT time_start, length, length_in, autostart  FROM billservice_settlementperiod WHERE id = %s" % service.wyte_period_id
                cur.execute(sql)
                connection.commit()
                result=[]
                r=cur.fetchall()
                if len(r)>1:
                    raise Exception
        
                if r==[]:
                    return None
                        
                settlement_period = Object(r[0]) 
                try:
                    settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
                except Exception, e:
                    logger.error("Error cannot delete addonservice for account %s, %s", (account_id, e))
            else:
                delta = 0
            now = datetime.datetime.now()
            
            if (((now-accountservice.activated).seconds+(now-accountservice.activated).days*86400)<delta) or (service.wyte_cost and delta == 0):
                try:
                    model = Object()
                    model.account_id = account_id
                    model.type_id = 'ADDONSERVICE_WYTE_PAY'
                    model.summ = service.wyte_cost
                    model.service_id = service.id
                    model.service_type = service.service_type
                    model.created = "now()"
                    model.summ = service.wyte_cost
                    model.accounttarif_id = account.accounttarif_id
                    model.accountaddonservice_id = account_service_id
                except Exception, e:
                    logger.error("Error cannot make wyte transaction for account %s, %s", (account_id, e))
                sql = model.save("billservice_addonservicetransaction")
                cur.execute(sql)
            #Отключаем услугу

            sql = "UPDATE billservice_accountaddonservice SET deactivated=now() WHERE id=%s" % accountservice.id
            cur.execute(sql)
            connection.commit()
            log_string = u"""Пользователь %s удалил пользователю %s подключаемую услугу %s""" % (add_data['USER_ID'][0], account_id, service.name)
            
            cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
            return True
        else:
            return 'NO_CANCEL_SUBSCRIPTION'
        return False

        
    
    def get_allowed_users(self, cur=None, connection=None, add_data = {}):
        return allowedUsers()
    
    
    def pod(self, session, cur=None, connection=None, add_data = {}):
        #print "Start POD"
        cur.execute("""
                    SELECT nas.ipaddress as nas_ip, nas.type as nas_type, nas.name as nas_name, nas.secret as nas_secret, nas.login as nas_login, nas.password as nas_password,
                    nas.reset_action as reset_action, account.id as account_id, account.username as account_name, account.vpn_ip_address as vpn_ip_address,
                    account.ipn_ip_address as ipn_ip_address, account.ipn_mac_address as ipn_mac_address, session.framed_protocol as framed_protocol
                    FROM radius_activesession as session
                    JOIN billservice_account as account ON account.id=session.account_id
                    JOIN nas_nas as nas ON nas.id=account.nas_id
                    WHERE  session.sessionid='%s'
                    """ % session)

        row = cur.fetchone()
        connection.commit()
        res = PoD(dict=dict,
            account_id=row['account_id'], 
            account_name=str(row['account_name']), 
            account_vpn_ip=row['vpn_ip_address'], 
            account_ipn_ip=row['ipn_ip_address'], 
            account_mac_address=row['ipn_mac_address'], 
            access_type=str(row['framed_protocol']), 
            nas_ip=row['nas_ip'], 
            nas_type=row['nas_type'], 
            nas_name=row['nas_name'], 
            nas_secret=row['nas_secret'], 
            nas_login=row['nas_login'], 
            nas_password=row['nas_password'], 
            session_id=str(session), 
            format_string=str(row['reset_action'])
        )
        log_string = u"""Пользователь %s послал пакет на разрыв сессии %s пользователя %s""" % (add_data['USER_ID'][0], session, str(row['account_name']))
        
        cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
        return res


def reread_pids():
    global vars
    newpids, newpiddate = readpids(vars.piddir, vars.piddate, exclude = [vars.name + '.pid'])
    if newpids:
        with vars.pidLock:
            vars.pids    = newpids
            vars.piddate = newpiddate
        
def broadcast_SIGUSR1():
    global vars
    reread_pids()
    logger.warning("Broadcasting SIGUSR1 to known pids, except self: %s {%s/%s}", (repr(vars.pids),vars.piddir, vars.piddate)) 
    if vars.pids:
        killpids(itertools.imap(operator.itemgetter(1), vars.pids), 10)
        
    
    
def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
    graceful_save()
    
def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("rpc", "log_level")))
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")
        
def SIGUSR1_handler(signum, frame):
    logger.lprint("SIGUSR1 received!")
    try:
        broadcast_SIGUSR1()
    except Exception, ex:
        logger.error("Exception diring SIGUSR1 broadcast: %s \n %s", (repr(ex), traceback.format_exc()))

def graceful_save():
    global threads, vars
    for th in threads:
        if isinstance(th, RPCServer):
            th.daemon.shutdown(disconnect=True)
    logger.lprint("About to stop gracefully.")
    pool.close()
    time.sleep(2)
    rempid(vars.piddir, vars.name)
    logger.lprint("Stopping gracefully.")
    sys.exit()
    
    
def check_login(login, asserted_role):
    global vars
    result = None
    with vars.db_connection_lock:
        try:
            vars.db_connection.execute('''SELECT username, text_password, host FROM billservice_systemuser WHERE username = %s AND status IS TRUE AND (role = %s OR role = '0');''', (login, int(asserted_role.strip())))
            result = vars.db_connection.fetchall()
            vars.db_connection.commit()
        except Exception, ex:
            result = ex
    if isinstance(result, Exception):
        raise result
    else:
        return result
    
def post_login(args):
    if len(args) == 4:
        login, ip, login_date, add_data = args
    else:
        logger.error("Post_login error: no args: %s", (args,))
        return
    #global vars
    #add_data['USER_ID'][0] = login
    add_data['USER_ID'][0] = login
    with vars.db_connection_lock:
        try:
            #print dir(ip)
            vars.db_connection.execute('''UPDATE billservice_systemuser SET last_ip = %s, last_login = %s::timestamp without time zone WHERE username = %s RETURNING id;''', (str(ip.host), login_date, login))
            systemuser_id = vars.db_connection.fetchone()[0]
            #add_data['USER_ID'][1] = systemuser_id
            #logger.info('Logged in user info: %s', (add_data['USER_ID'],))
            add_data['USER_ID'][1] = systemuser_id
            logger.info('Logged in user info: %s', (add_data['USER_ID'],))
            vars.db_connection.commit()
        except Exception, ex:
            logger.error("Exception during post_login: %s \n %s", (repr(ex), traceback.format_exc()))

def get_producer(addr):
    global vars
    authenticator = MD5_Authenticator('server', 'AUTH', check_login, addr)
    protocol = RPCProtocol(authenticator)
    db_conn = PersistentDBConnection(psycopg2, vars.db_dsn, cursor_factory = psycopg2.extras.RealDictCursor)
    rpc_ = RPCServer()
    producer = DBProcessingThread(protocol, db_conn, rpc_, reactor, post_login = post_login)
    return producer

def main():
    global threads, vars
    threads=[]
    '''
    threads.append(RPCServer())
    for th in threads:	
        th.start()
        time.sleep(0.1)'''
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    #main thread should not exit!
    #print "ebs: rpc: started"


    #reactor.listenUDP(vars.PORT, NfTwistedServer(), maxPacketSize=vars.MAX_DATAGRAM_LEN)
    fact = RPCFactory(TCP_IntStringReciever, get_producer)
    #fact.protocol = TCP_LineReciever
    #fact.protocol = TCP_IntStringReciever
    p = reactor.listenTCP(vars.LISTEN_PORT, fact)
    logger.info("Listening on: %s", p.getHost())

    
    print "ebs: rpc: started"
    savepid(vars.piddir, vars.name)
    reactor.run(installSignalHandlers=False)
        
if __name__ == "__main__":
    if "-D" in sys.argv:
        pass
        #daemonize("/dev/null", "log.txt", "log.txt")
     
    
    config = ConfigParser.ConfigParser()    
    config.read("ebs_config.ini")
    
    try:
        vars = RpcVars()        
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file)
        utilites.log_adapt = logger.log_adapt
        saver.log_adapt    = logger.log_adapt
        serv_install_logger(logger)
        proto_install_logger(logger)
        vars.db_connection = PersistentDBConnection(psycopg2, vars.db_dsn)
        vars.db_connection.connect()
        vars.graph_connection = PersistentDBConnection(psycopg2, vars.db_dsn)
        vars.graph_connection.connect()
        vars.graph_connection.connection.set_isolation_level(0)
        logger.lprint('Ebs RPC start')
        #=======================================
        #!!! debug options, comment out when not needed
        #from ssh_paramiko import install_logger as ssh_install_logger
        #import socket
        #socket.setdefaulttimeout(30)
        #ssh_install_logger(logger)
        import sys
        stderr_log = open(vars.log_file + '.err', 'ab')
        #redirect_stderr(stderr_log)
        sys.stderr = stderr_log
        #main thread should not exit!
        #=======================================
        
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        maxUsers = int(config.get("rpc", "max_users"))

        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i(), vars.db_connection)               
        allowedUsers()
        #-------------------
        print "ebs: rpc: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rpc, exiting: ', repr(ex), traceback.format_exc()
        logger.error('Exception in rpc , exiting: %s', repr(ex))
