#!/bin/bash

ftp_site=ip
username=ebs
passwd=ebs
remote_dir=EBS
backupdir=/collector/flow/netflow.`date --date='1 days ago' +'%Y-%m-%d'`*
filename="backup-$(date '+%F-%H%M').tar.gz"

echo "Creating a backup file $filename of $backupdir."

# Make a tar gzipped backup file
tar -cvzf  "$filename" $backupdir

ftp -in <<EOF
open $ftp_site
user $username $passwd
bin
cd $remote_dir
put $filename.
close.
bye
EOF

RET_CODE=$?

if [ $? -ne 0 ]; then
    echo "nf archivation problem"
    rm $filename
    exit $RET_CODE
fi

rm $backupdir
rm $filename


