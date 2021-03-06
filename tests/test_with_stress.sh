#!/bin/bash

SERVER="http://192.168.99.112:3000"
SLEEP=60
STRESSTIME=120
INC=4
STRESS_CPU_RANGE=56
VM=1
IO=1
HDD=1
GPU=1

log_it () {
	curl --silent "$SERVER/log?$1" > /dev/null
	if [ ! "$?" -eq "0" ]; then
		echo "Message send failed."
		exit 1
	fi
}

send_uptime () {
	UTENC=$(uptime | python -c "import urllib.parse;print (urllib.parse.quote(input()))")
	log_it "$1_uptime_enc=$UTENC"
}

echo "Testing connection to ipmiserve"
log_it "test=test_with_stress&cpurange=${STRESS_CPU_RANGE}&vm=${VM}&io=${IO}&hdd=${HDD}&gpu=${GPU}"

START=0
END=$STRESS_CPU_RANGE
for (( CPU=$START; CPU<=$END; CPU+=$INC ))
do
	echo
	echo "Starting a stress test with cpu=$CPU"

	echo "Start a timed sleep = $SLEEP"
	log_it "sleep=$SLEEP"
	sleep $SLEEP

	echo "Launch stress cpu=$CPU"
	log_it "stress=1&time=$STRESSTIME&cpu=$CPU"
	send_uptime "before_stress"
	if [ "$CPU" -eq "0" ]; then
		sleep $STRESSTIME
	else
		if [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ] && [ "$HDD" -eq "1" ]; then
			stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU --hdd $CPU
		elif [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ]; then
			stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU
		elif [ "$VM" -eq "1" ]; then
			stress --timeout $STRESSTIME --cpu $CPU --vm $CPU
		else
			stress --timeout $STRESSTIME --cpu $CPU
		fi
	fi
	send_uptime "after_stress"

	echo "Stop stress"
	log_it "stress=0"

done
	
if [ "$GPU" -eq "1" ]; then
	echo "Start a timed sleep = $SLEEP"
	log_it "sleep=$SLEEP"
	sleep $SLEEP
	
	echo "Launch stress cpu=gpu"
	log_it "stress=1&time=$STRESSTIME&cpu=gpu"
	send_uptime "before_stress"
		
	if [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ] && [ "$HDD" -eq "1" ]; then
		stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU --hdd $CPU &
		./run_gpu_burn.sh $STRESSTIME &
	elif [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ]; then
		stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU &
		./run_gpu_burn.sh $STRESSTIME &
	elif [ "$VM" -eq "1" ]; then
		stress --timeout $STRESSTIME --cpu $CPU --vm $CPU &
		./run_gpu_burn.sh $STRESSTIME &
	else
		stress --timeout $STRESSTIME --cpu $CPU &
		./run_gpu_burn.sh $STRESSTIME &
	fi
		
	wait

	echo "Stop stress"
	log_it "stress=0"
fi
	
echo "Done."
log_it "done=1"
exit 0
