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
message_number = datetime.datetime.now().strftime("%d%m%Y")
message_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
sender_code = 32300112
unp = 390150916
bank_code = 307
rs = 3012116607010
service_id = 2
currency = 974
ftp_host="host"
ftp_username = "user"
ftp_password = "password" 
ftp_remote_path = "11111111/in"
cursor.execute("SELECT username, fullname, street ||', ' || house ||', ' || acc.room FROM billservice_account as acc")

items = cursor.fetchall()
header_mask = u"%s^%s^%s^%s^%s^%s^%s^%s^%s^%s\n"
row_mask = "%s^%s^%s^%s^^0^^^^^^^\n"

header = header_mask % (version, sender_code, message_number, message_date, len(items),unp, bank_code, rs,service_id, currency)
outfile = codecs.open("out.txt", "wb", "cp1251")
outfile.write(header)
i=1
for item in items:
    username, fullname, address = item

    s= row_mask % (i, username, fullname, address)

    outfile.write(s.decode("utf-8"))
    i+=1
    
outfile.close()

import ftplib

s = ftplib.FTP(ftp_host, ftp_username, ftp_password) # Connect


f = open('out.txt','rb')                # file to send

s.storbinary('STOR %s/%s.202' % (ftp_remote_path, message_number), f)         # Send the file

f.close()                                # Close file and FTP
s.quit()
