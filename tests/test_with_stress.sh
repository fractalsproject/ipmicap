#!/bin/bash

SERVER="http://192.168.99.112:3000"
SLEEP=20
STRESSTIME=60
STRESS_CPU_RANGE=56
VM=1

log_it () {
	curl --silent "$SERVER/log?$1" > /dev/null
	if [ ! "$?" -eq "0" ]; then
		echo "Message send failed."
		exit 1
	fi
}

echo "Testing connection to ipmiserve"
log_it "test=test_with_stress_cpu_$STRESS_CPU_RANGE_vm_$VM""

START=0
END=$STRESS_CPU_RANGE
for (( CPU=$START; CPU<=$END; CPU++ ))
do
	echo
	echo "Starting a stress test with cpu=$CPU"

	echo "Start a timed sleep = $SLEEP"
	log_it "sleep=$SLEEP"
	sleep $SLEEP

	echo "Launch stress cpu=$CPU"
	log_it "stress=1&time=$STRESSTIME&cpu=$CPU"
	if [ "$CPU" -eq "0" ]; then
		sleep $STRESSTIME
	else
		if [ "$VM" -eq "1" ]; then
			stress --timeout $STRESSTIME --cpu $CPU --vm $CPU
		else
			stress --timeout $STRESSTIME --cpu $CPU
		fi
	fi

	echo "Stop stress"
	log_it "stress=0"

done
	
echo "Done."
log_it "done=1"
exit 0
