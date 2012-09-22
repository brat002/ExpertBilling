#!/bin/sh -e
#$1 - project name $2 users $3 key $4 license string $5 additional flags
users="32"
testdrive="true"
if [ $2 ]; then
    users=$2
    testdrive="false"
fi

python lic_generator.py $1 $2 $4
if [ ! -d builds ]; then
	mkdir builds
fi
reskey=""
karg=""

if [ $3 ]; then
	karg="-k"
	reskey=$3`cat license_$1.lic`
elif [ $testdrive=="false" ]; then
    karg="-k"
    reskey=`cat license_$1.lic`
fi

if [ $reskey ]; then
	echo $reskey;
else
    echo "No key entered - test drive";
fi

rm -rf modules
rm -rf builds/$1

mkdir builds/$1

echo "Additional keys: " $5


crypto_build="core"
simple_build="rad nf nfroutine"
total_build="$crypto_build $simple_build"

cp license.lic license.lic.old
cp license_$1.lic license.lic

for bld in $crypto_build; do
	python freezer/freezer_rec.py  -i $5 $karg $reskey $bld.py > builds/$1.$bld.buildlog;
done

for bld in $simple_build; do
    python freezer/freezer_rec.py  -i $5 '' '' $bld.py > builds/$1.$bld.buildlog;
done

#python freezer/freezer_rec.py --nloc=chartprovider.pychartdir26,chartprovider.pychartdir25,chartprovider.pychartdir27 --order=chartprovider.bpplotadapter,chartprovider.pychartdir,chartprovider.bpbl,chartprovider.bpcdplot,chartprovider -i $5 $karg $reskey rpc.py > builds/$1.rpc.buildlog;

cp license.lic builds/$1/license.lic
cp license.lic.old license.lic
cp ebs_config.ini builds/$1/ebs_config.ini
#cp upgrade.py builds/$1/upgrade.py
cp ebs_config_runtime.ini builds/$1/ebs_config_runtime.ini
cp -rf modules builds/$1
mkdir builds/$1/nf_dump
mkdir builds/$1/log
mkdir builds/$1/etc
mkdir builds/$1/pid
mkdir builds/$1/temp
mkdir builds/$1/init.d
mkdir builds/$1/ebscab/
mkdir builds/$1/soft/
#cp -rf dicts builds/$1/dicts
#cp -rf fonts builds/$1/fonts
#cp -rf scripts builds/$1/scripts
#rm -rf builds/$1/modules/chartprovider
#cp chartprovider/pychartdir.pyc chartprovider/pychartdir25.pyd chartprovider/pychartdir25.so chartprovider/libchartdir.so builds/$1/modules
#cp chartprovider/pychartdir.pyc chartprovider/pychartdir26.pyd chartprovider/pychartdir26.so builds/$1/modules
#cp chartprovider/pychartdir.pyc chartprovider/pychartdir27.pyd chartprovider/pychartdir27.so builds/$1/modules
mkdir builds/$1/ebscab
svn export webadmin/ebscab builds/$1/ebscab/ebscab/ --force
svn export webadmin/blankpage builds/$1/ebscab/blankpage/ --force
echo >builds/$1/ebscab/ebscab/log/django.log
chmod 0777 builds/$1/ebscab/ebscab/log/django.log
echo >builds/$1/ebscab/ebscab/log/webcab_log
chmod 0777 builds/$1/ebscab/ebscab/log/webcab_log
svn export soft/django builds/$1/ebscab/django/ --force
cp webadmin/django.wsgi builds/$1/ebscab/
cp webadmin/default builds/$1/ebscab/
cp webadmin/blankpage builds/$1/ebscab/
cp soft/billing builds/$1/soft/
svn export soft/hotspot/ builds/$1/soft/hotspot/
#cp -r ebscab/ builds/$1/ebscab/
mkdir builds/$1/sql
cp sql/ebs_dump.sql builds/$1/sql/
cp sql/changes.sql builds/$1/sql/
#cp -r sql/upgrade builds/$1/sql/
svn export sql/upgrade/ builds/$1/sql/upgrade/
svn export dicts/ builds/$1/dicts/
svn export fonts/ builds/$1/fonts/
svn export scripts/ builds/$1/scripts/
svn export mail/ builds/$1/modules/mail/
cp sendmail.py builds/$1/scripts/
cp sendsms.py builds/$1/scripts/
cp install.txt builds/$1/

for bldd in $total_build; do
	cp $bldd builds/$1
	cp init/ebs_$bldd builds/$1/init.d/ebs_$bldd
	chmod +x builds/$1/init.d/ebs_$bldd
	if [ -f $bldd ]; then
	     rm $bldd;
	fi
	if [ -f $bldd.c ]; then
	     rm $bldd.c;
	fi
done

rm -rf modules

find $1 -name '.svn' -type d | xargs rm -rf

if [ $SUDO_USER ]; then
	chown -hR $SUDO_USER: builds/$1
fi

cd builds/$1/
tar -czvf ../ebs-`svnversion ../../`.tar.gz .
cd ../ 
chmod +x ../ebs_manage.py
tar -czvf $1.tar.gz ebs-`svnversion ../`.tar.gz ../ebs_manage.py
cd ../

