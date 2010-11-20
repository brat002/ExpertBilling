nf_oldpids=`ps -C nf -o pid=`
for nf_oldpid in $nf_oldpids; do 
 	kill -9 $nf_oldpid;
done
./nf & 
nf_pid=`ps -C nf -o pid=`

nfroutine_oldpids=`ps -C nfroutine -o pid=`
for nfroutine_oldpid in $nfroutine_oldpids; do 
 	kill -9 $nfroutine_oldpid;
done
./nfroutine & 
nfroutine_pid=`ps -C nfroutine -o pid=`

pidstat -p $nf_pid -rtu 600 > pidstat.nf &
pidstat -p $nfroutine_pid -rtu 600 > pidstat.nfroutine &