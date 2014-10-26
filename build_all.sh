#!/bin/bash

#$1 - project name $2 users $3 key $4 license string $5 additional flags
source ../venv/bin/activate
users="32"
testdrive="true"
if [ $2 ]; then
    users=$2
    testdrive="false"
fi

VENV_PATH="../venv/"






#checking for first run and create env
if [ ! -d $VENV_PATH ]; then
    virtualenv --python=python2.7 $VENV_PATH && $VENV_PATH/bin/pip install -r soft/requirements.txt
fi
    $VENV_PATH/bin/pip install -r soft/requirements.txt

curdate=`date +%Y%m%d%H%M%S`
python lic_gen.py $1 $2 $3
if [ ! -d builds ]; then
	mkdir builds
fi

rm -rf modules
rm -rf cmodules
rm -rf builds/$1
rm -rf builds/$1.tar.gz

mkdir -p builds/$1/data

echo "Additional keys: " $5


#crypto_build="core rad_auth rad_acct nf nfroutine nffilter nfwriter"
simple_build="core rad_auth rad_acct nfroutine nfwriter"
total_build="$crypto_build $simple_build"

modules="db utilites dictionary packet auth bidict cacherouter IPy isdlogger log_adapter logger option_parser period_utilities saver ssh_paramiko ssh_utilities syslog_dummy tools dictfile queues"
mkdir -p cmodules

for bld in $modules; do
    cython $bld.py -2 -o cmodules/$bld.c;
    gcc $CFLAGS -I/usr/include/python2.7 --shared -o cmodules/$bld.so cmodules/$bld.c -lpython2.7 -lpthread -lm -lutil -ldl -fPIC
done

current_dir=`pwd`
blddirs="classes radius"
for blddir in $blddirs;do
    for line in `find $blddir  -name "*.py" -type f`;do
        dir=`dirname $line`;
        fl=`basename $line`;
        bld=${fl%.*}
        echo $dir;
        echo $bld;
        mkdir -p cmodules/$dir;
        touch cmodules/$dir/__init__.pyc;
        touch cmodules/$dir/__init__.py;
        cython -v $dir/$bld.py -2 -o cmodules/$dir/$bld.c;
        gcc $CFLAGS -I/usr/include/python2.7 --shared -o cmodules/$dir/$bld.so cmodules/$dir/$bld.c -lpython2.7 -lpthread -lm -lutil -ldl  -fPIC;
        rm -rf cmodules/$dir/*.c;
    done
done

#cython $bld
#gcc $CFLAGS -I/usr/include/python2.7 --shared -o cmodules/$bld.so $bld.c -lpython2.7 -lpthread -lm -lutil -ldl

for bld in $crypto_build; do
	python freezer/freezer_rec.py -l -i $5 $karg $reskey $bld.py > builds/$1.$bld.buildlog;
done

#gcc $CFLAGS -I/usr/include/python2.7 -o hw core.c -lpython2.7 -lpthread -lm -lutil -ldl

for bld in $simple_build; do
    #python freezer/freezer_rec.py  -i $5 '' '' $bld.py > builds/$1.$bld.buildlog;
    cython -v --embed $bld.py ;
    gcc $CFLAGS -I/usr/include/python2.7  -o $bld $bld.c -lpython2.7 -lpthread -lm -lutil -ldl
    rm -rf cmodules/*.c;
done

#python freezer/freezer_rec.py -i $5 $karg $reskey rpc.py > builds/$1.rpc.buildlog;

cp license_$1.lic builds/$1/data/license.lic
cp -r cmodules builds/$1/data/
cp -r workers builds/$1/data/workers
cp ../nf/output/bin/nf builds/$1/data/
cp ../nf/output/bin/nffilter builds/$1/data/

cp license.lic.old license.lic
cp ebs_config.ini.tmpl builds/$1/data/ebs_config.ini.tmpl
#cp upgrade.py builds/$1/data/upgrade.py
#cp ebs_config_runtime.ini builds/$1/ebs_config_runtime.ini
cp -rf modules builds/$1/data
mkdir builds/$1/data/nf_dump
mkdir builds/$1/data/log
mkdir builds/$1/data/etc
mkdir builds/$1/data/pid
mkdir builds/$1/data/temp
mkdir builds/$1/data/init.d
#mkdir builds/$1/ebscab/
mkdir builds/$1/data/soft/
#mkdir builds/$1/ebscab
rm -rf builds/$1/web
mkdir -p builds/$1/web/ebscab
cp -r webadmin/ebscab builds/$1/web/ --force
cp -r webadmin/blankpage builds/$1/web/blankpage/
#echo >builds/$1/ebscab/ebscab/log/django.log
echo >builds/$1/web/ebscab/log/django.log
chmod 0777 builds/$1/web/ebscab/log/django.log
echo >builds/1$/web/ebscab/log/webcab_log
chmod 0777 builds/$1/web/ebscab/log/webcab_log


cp webadmin/django.wsgi builds/$1/web/
cp webadmin/default builds/$1/web/
cp webadmin/blankpage_config builds/$1/web/
cp webadmin/blankpage builds/$1/web/
cp soft/billing builds/$1/data/soft/
cp -r migrations builds/$1/data/
cp soft/backup_and_ftp_netflow.sh builds/$1/data/soft/
cp -r soft/hotspot/ builds/$1/data/soft/hotspot/
cp soft/requirements.txt builds/$1/data/soft/
cp soft/del_requirements.txt builds/$1/data/soft/
#cp -r ebscab/ builds/$1/ebscab/
mkdir builds/$1/data/sql
cp sql/ebs_dump.sql builds/$1/data/sql/
cp sql/changes.sql builds/$1/data/sql/
#cp -r sql/upgrade builds/$1/sql/
cp -r sql/upgrade/ builds/$1/data/sql/upgrade/
cp -r dicts/ builds/$1/data/dicts/
cp -r scripts/ builds/$1/data/scripts/
cp -r mail/ builds/$1/data/modules/mail/
cp sendmail.py builds/$1/data/scripts/
cp sendsms.py builds/$1/data/scripts/
cp install.txt builds/$1/data/

echo $curdate >builds/$1/data/version
echo $curdate >builds/$1/web/version

for bldd in $total_build; do
	cp $bldd builds/$1/data
	cp init/ebs_$bldd builds/$1/data/init.d/ebs_$bldd
	chmod +x builds/$1/data/init.d/ebs_$bldd
	if [ -f $bldd ]; then
	     rm $bldd;
	fi
	if [ -f $bldd.c ]; then
	     rm $bldd.c;
	fi
done
cp init/ebs_celery builds/$1/data/init.d/ebs_celery
chmod +x builds/$1/data/init.d/ebs_celery
cp soft/celeryd builds/$1/data/soft/

rm -rf modules

find $1/data -name '.git' -type d | xargs rm -rf

if [ $SUDO_USER ]; then
	chown -hR $SUDO_USER: builds/$1/data
fi

cd builds/$1/
tar -czvf ../ebs.tar.gz data

rm -f web.tar.gz
tar -czvf ../web.tar.gz web
chmod +x ../ebs_manage.py
cd ../
tar -czvf $1.tar.gz ebs.tar.gz ../fabfile.py ../install.txt web.tar.gz
cd ../


