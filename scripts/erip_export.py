import psycopg2
import sys
import datetime
import codecs
try:
    conn = psycopg2.connect("dbname='ebs' user='ebs' host='127.0.0.1' password='ebspassword' port='5432'");
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(1)
conn.set_client_encoding('UTF8')
cursor = conn.cursor()

version = 3
sender_code = 32100214
message_number = datetime.datetime.now().strftime("%d%m%Y")
message_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
unp = 190832724
bank_code = 739
rs = 3012741610015
service_id = 1
currency = 974
ftp_host="host"
ftp_username = "user"
ftp_password = "password" 
ftp_remote_path = "11111111/in"
cursor.execute("SELECT username, fullname, COALESCE((SELECT name FROM billservice_street WHERE id=acc.street_id) ||', ' || (SELECT name FROM billservice_house WHERE id=acc.house_id) ||', ' || acc.room, '') FROM billservice_account as acc")

items = cursor.fetchall()
header_mask = u"%s^%s^%s^%s^%s^%s^%s^%s^%s^%s\n"
row_mask = "%s^%s^%s^%s^^0^^^^^^^\n"

header = header_mask % (version, sender_code, message_number, message_date, len(items),unp, bank_code, rs,service_id, currency)
outfile = codecs.open("out.txt", "wb", "cp1251")
outfile.write(header)
i=1
for item in items:
    username, fullname, address = item
    #print i, "%s" % unicode(username), unicode(fullname), unicode(address)
    #print row_mask % (i, unicode(username), unicode(fullname), unicode(address),'',0,'','','','','','','')
    #print username, fullname, address
    #print "1 %s" % username
    #print "2 %s" % fullname
    #print "3 %s" % address
    #s=""+str(i)+"^"+"^"+username+"^"+fullname+"^"+address+"^"+"^"+"^"+"^"+"^"+"^"+"^\n"
    s= row_mask % (i, username, fullname, address)
    #print s
    outfile.write(s.decode("utf-8"))
    i+=1
    
outfile.close()

import ftplib

s = ftplib.FTP(ftp_host, ftp_username, ftp_password) # Connect


f = open('out.txt','rb')                # file to send

s.storbinary('STOR %s/%s.202' % (ftp_remote_path, message_number), f)         # Send the file

f.close()                                # Close file and FTP
s.quit()
