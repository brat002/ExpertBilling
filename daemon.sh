#!/bin/bash
PIDFILE=/tmp/django-fcgi.pid
stop() {
    kill `cat -- $PIDFILE`
}

start() {
    pid=$(cat $PIDFILE ) 2>&-

    if [ "X""$pid" != "X" ] ; then
        check=$(ps ax | grep python |grep $pid)
            if [ "X""$check" != "X" ]; then
                echo "Error: process is already running pid - $pid"
            exit 1;
        fi
    fi
    source ../bin/activate && /usr/bin/env python manage.py runfcgi daemonize=true pidfile=$PIDFILE  host=127.0.0.1 port=7777
}

restart() {
    stop
    start
}

status() {
    pid=$( cat $PIDFILE ) 2>&-
    if [ "X"${pid} = "X" ]; then
                echo "Status: $host is down"
                exit 0;
        fi
        check=$(ps aux|awk '{print $2}'| grep $pid)
        if [ "X"${check} = "X" ]; then
                echo "Status: $host is down"
        else
                echo "Status: $host is up and running pid $pid"
        fi
}
# checking we've got valid number of args
if [ $# != 1 ]; then
        echo 'Usage: daemon.sh start|stop|restart'
        exit 1
fi
#actual job
case "$1" in
        start) start ;;
        stop) stop  ;;
        status) status ;;
        restart) restart ;;
esac

