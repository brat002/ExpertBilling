#!/usr/bin/env python

import ftplib
import os, sys

# Connection information
server = '10.54.1.1'
username = 'qwerty'
password = '12345'

# Directory and matching information
directory = 'out/'
filematch = ['*.206', '*.216']
to_directory = '/opt/ebs/payments/erip/in/'
# Establish the connection
ftp = ftplib.FTP(server)
ftp.login(username, password)

# Change to the proper directory
ftp.cwd(directory)

# Loop through matching files and download each one individually

for fmatch in filematch:
    for filename in ftp.nlst(fmatch):
        fhandle = open(os.path.join(to_directory, filename), 'wb')
        print 'Getting ' + filename
        try:
            ftp.retrbinary('RETR ' + filename, fhandle.write)
            ftp.delete(filename)
        except:
            sys.exit()
        finally:
            fhandle.close()
