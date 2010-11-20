import re

USER_OK = 1
NO_USER = 2
DB_FAIL = 3

class ByFlatIPNIPCheck():
    def __init__(self):
        self.reobj = re.compile(r"[\d]{4,12}\Z")
	
    def pre_check(self, username):
	if len(username) > 12: return False
	if self.reobj.match(username):
	    return True
	else:
	    return False
	
    def check_db(self, username, connection):
	try:
	    cur = connection.cursor()
	    cur.execute("SELECT id FROM billservice_account WHERE replace(host(ipn_ip_address), '.', '') = %s;", (username,))
	except Exception, ex:
	    return (DB_FAIL, ex)
	data = None
	try:
	    data = cur.fetchone()[0]
	except:
	    pass
	try:
	    cur.connection.commit()
	    cur.close()
	except Exception, ex:
	    return (DB_FAIL, ex)
	if not data:
	    return (NO_USER, None)
	return(USER_OK, None)
    
    
    def get_db(self, username, connection, tx_datetime):
	try:
	    cur = connection.cursor()
	    cur.execute("SELECT ba.id, act.id, act.tarif_id FROM billservice_account as ba JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1) WHERE replace(host(ipn_ip_address), '.', '') = %s;", (tx_datetime, username,))
	except Exception, ex:
	    return (DB_FAIL, ex)
	data = None
	try:
	    data = cur.fetchone()
	except:
	    pass
	try:
	    cur.connection.commit()
	    cur.close()
	except Exception, ex:
	    return (DB_FAIL, ex)
	if not data:
	    return (NO_USER, None)
	return(USER_OK, data)
    
    def pay_db(self, connection, account_id, acctf_id, tarif_id, summ, tx_date):
	try:
	    cur = connection.cursor()
	    cur.execute("""INSERT INTO billservice_transaction(bill,
                    account_id, approved, type_id, tarif_id, accounttarif_id, summ, description, created)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                    """ , ('', account_id, True, 'OSMP_BILL', tarif_id, acctf_id, summ, '', tx_date))
	except Exception, ex:
	    return (DB_FAIL, ex)
	data = None
	try:
	    data = cur.fetchone()[0]
	except:
	    pass
	try:
	    cur.connection.commit()
	    cur.close()
	except Exception, ex:
	    return (DB_FAIL, ex)
	if not data:
	    return (NO_USER, None)
	return(USER_OK, data)