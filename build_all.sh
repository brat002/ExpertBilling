#!/bin/sh
#$1 - project name $2 users $3 key 

python lic_generator.py $1 $2

rm -rf modules
rm -rf $1

mkdir $1

karg=""

if [ $3 ]; then
	karg="-k"
fi

simple_build="core rad nf nfroutine"
total_build="$simple_build rpc"

cp license.lic license.lic.old
cp license_$1.lic license.lic

for bld in $simple_build; do
	python freezer/freezer.py  -i $karg $3 $bld.py > $1.$bld.buildlog;
done

python freezer/freezer.py --nloc=chartprovider.pychartdir25 --order=chartprovider.bpplotadapter,chartprovider.pychartdir,chartprovider.bpbl,chartprovider.bpcdplot,chartprovider -i $karg $3 rpc.py > $1.rpc.buildlog;

cp license.lic $1/license.lic
cp license.old.lic license.lic
cp ebs_config.ini 1/ebs_config.ini 
cp ebs_config_runtime.ini 1/ebs_config_runtime.ini 
cp -rf modules $1
mkdir $1/nf_temp
mkdir $1/log
mkdir $1/init.d
cp -rf $1/dicts
cp -rf $1/fonts
cp pychartdir.pyc pychartdir25.pyd libchartdir.so $1/modules/chartprovider

for bldd in $total_build; do
	cp $bldd $1
	cp init/ebs_$bldd $1/init.d/ebs_$bldd
	chmod +x $1/init.d/ebs_$bldd
done

find $1 -name '.svn' -type d | xargs rm -rf