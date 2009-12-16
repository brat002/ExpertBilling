#!/bin/sh
#$Id: run_script.sh 2077 2008-12-30 14:12:15Z valera $
if [ $# != 1 ]; then
    echo "Usage run.sh path_to_python_script/blahblah.py"
    exit
fi
export PYTHONPATH="$(pwd)"
export DJANGO_SETTINGS_MODULE="settings"
python2.5 $1
