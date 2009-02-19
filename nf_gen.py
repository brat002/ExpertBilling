import os,sys, random
import psycopg2
from IPy import IP, IPint, parseAddress
from DBUtils.PooledDB import PooledDB
import ConfigParser

def main():
    connection = pool.connection()
    connection._con._con.set_client_encoding('UTF8')
    
    
    cur = connection.cursor()
    a = time.clock()
    
    ptime =  time.time()
    ptime = ptime - (ptime % 20)
    tmpDate = datetime.datetime.fromtimestamp(ptime)
    cur.execute("""SELECT ba.id,  CASE WHEN (bap.access_type='IPN' OR bap.ipn_for_vpn) THEN ba.ipn_ip_address ELSE ba.vpn_ip_address END AS ips
        FROM billservice_account as ba
        JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
        JOIN billservice_tariff AS bt ON bt.id=act.tarif_id JOIN billservice_accessparameters AS bap ON bap.id=bt.access_parameters_id;""", (tmpDate,))
    acctf = cur.fetchall()
    cur.execute("SELECT ip, ipaddress FROM nas_nas;")                
    nasvals = cur.fetchall()
    cur.execute("SELECT traffic_class_id, src_ip, dst_ip, next_hop FROM nas_trafficnode AS tn JOIN nas_trafficclass AS tc ON tn.traffic_class_id=tc.id ORDER BY tc.weight, tc.passthrough;")
    nnodes = cur.fetchall()
    connection.commit()
    cur.close()
    
    #nas cache creation
    nascache = dict(nasvals)
    del nasvals  
    
    accscache = dict(acctf)
    
    
    #forms a class->nodes structure                
    ndTmp = [[0, []]]
    tc_id = nnodes[0][0]
    for nnode in nnodes:
        if nnode[0] != tc_id:
            ndTmp.append([0, []])
        nclTmp = ndTmp[-1]
        nclTmp[0] = nnode[0]
        tc_id = nnode[0]
        nlist = []
        n_hp = parseAddress(nnode[3])[0]
        d_ip = IPint(nnode[2])
        s_ip = IPint(nnode[1])
        nlist.append(s_ip.int())
        nlist.append(s_ip.broadcast())
        nlist.append(d_ip.int())
        nlist.append(d_ip.broadcast())
        nlist.append(n_hp)
        nclTmp[1].append(tuple(nlist))
    if ndTmp[0][0]:
        nodesCache = ndTmp
    del ndTmp
    inum = 1000
    accounts = accscache.keys()
    
    for i in xrange(inum):
        acct = 
            

            
            
if __name__=='__main__':
      

    config = ConfigParser.ConfigParser()

    #binary strings lengthes
    flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
    headerLENGTH = struct.calcsize("!HHIIIIBBH")
    
    config.read("ebs_config.ini")

    pool = PooledDB(
        mincached=1,  maxcached=9,
        blocking=True,creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                               config.get("db", "host"), config.get("db", "password")))
    