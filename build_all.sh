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



simple_build="core rad nf nfroutine"
total_build="$simple_build rpc"

cp license.lic license.lic.old
cp license_$1.lic license.lic

for bld in $simple_build; do
	python freezer/freezer_rec.py  -i $5 $karg $reskey $bld.py > builds/$1.$bld.buildlog;
done

python freezer/freezer_rec.py --nloc=chartprovider.pychartdir25 --order=chartprovider.bpplotadapter,chartprovider.pychartdir,chartprovider.bpbl,chartprovider.bpcdplot,chartprovider -i $5 $karg $reskey rpc.py > builds/$1.rpc.buildlog;

cp license.lic builds/$1/license.lic
cp license.lic.old license.lic
cp ebs_config.ini builds/$1/ebs_config.ini 
cp ebs_config_runtime.ini builds/$1/ebs_config_runtime.ini 
cp -rf modules builds/$1
mkdir builds/$1/nf_dump
mkdir builds/$1/log
mkdir builds/$1/pid
mkdir builds/$1/temp
mkdir builds/$1/init.d
cp -rf dicts builds/$1/dicts
cp -rf fonts builds/$1/fonts
rm -rf builds/$1/modules/chartprovider
cp chartprovider/pychartdir.pyc chartprovider/pychartdir25.pyd chartprovider/pychartdir25.so chartprovider/libchartdir.so builds/$1/modules
svn export --username dolphinik --password planeta svn://127.0.0.1/mikrobill/trunk/webadmin/ebscab ebscab/ --force

mkdir builds/$1/ebscab
cp -r ebscab/ builds/$1/ebscab/
mkdir builds/$1/sql
cp sql/ebs_dump.sql builds/$1/sql/
cp sql/changes.sql builds/$1/sql/
cp -r mail/ builds/$1/modules/
cp sendmail.py builds/$1/

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
tar -czvf ../$1.tar.gz .
cd ../../

