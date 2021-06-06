#!/bin/bash

SERVER="http://192.168.99.112:3000"
SLEEP=60
STRESSTIME=120
REPEAT=3

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

do_test() {

	CPU=$1
	VM=$2
	IO=$3
	HDD=$4
	GPU=$5
	
	echo "Start a timed sleep = $SLEEP"
	log_it "sleep=$SLEEP"
	sleep $SLEEP
	echo "Launch stress cpu=$CPU,vm=$VM,io=$IO,hdd=$HDD,gpu=$GPU""
	log_it "stress=1&time=$STRESSTIME&cpu=$CPU&vm=$VM&io=$IO&hdd=$HDD&gpu=$GPU"
	send_uptime "before_stress"
	
	if [ "$CPU" -eq "0" ]; then
		if [ "$GPU" -eq "1" ]; then
			./run_gpu_burn.sh $STRESSTIME 
		else
			sleep $STRESSTIME
		fi
	else
		if [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ] && [ "$HDD" -eq "1" ]; then
			if [ "$GPU" -eq "1" ]; then
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU --hdd $CPU &
				./run_gpu_burn.sh $STRESSTIME &
				wait
			else
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU --hdd $CPU
			fi
		elif [ "$VM" -eq "1" ] && [ "$IO" -eq "1" ]; then
			if [ "$GPU" -eq "1" ]; then
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU &
				./run_gpu_burn.sh $STRESSTIME &
				wait
			else
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU --io $CPU
			fi
		elif [ "$VM" -eq "1" ]; then
			if [ "$GPU" -eq "1" ]; then
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU &
				./run_gpu_burn.sh $STRESSTIME &
				wait
			else
				stress --timeout $STRESSTIME --cpu $CPU --vm $CPU
			fi
		else
			echo "Unsupported Test"
			exit 1
		fi
	fi

	echo "Stop stress"
	log_it "stress=0"
}

echo "Testing connection to ipmiserve"
log_it "test=variety&repeat=${REPEAT}"

START=1
END=$REPEAT
for (( N=$START; N<=$END; N+=1 ))
do
	#SLEEP 
	do_test 0 0 0 0 0

	#CPU=X (nothing else)
	do_test 1 0 0 0 0
	
	do_test 14 0 0 0 0
	
	do_test 28 0 0 0 0
	
	do_test 42 0 0 0 0
	
	do_test 56 0 0 0 0
	
	#VM=1
	do_test 1 1 0 0 0
	
	do_test 14 1 0 0 0
	
	do_test 28 1 0 0 0
	
	do_test 42 1 0 0 0
	
	do_test 56 1 0 0 0
	
	#IO=1
	do_test 1 1 1 0 0
	
	do_test 14 1 1 0 0
	
	do_test 28 1 1 0 0
	
	do_test 42 1 1 0 0
	
	do_test 56 1 1 0 0
	
	#HDD=1
	do_test 1 1 1 1 0
	
	do_test 14 1 1 1 0
	
	do_test 28 1 1 1 0
	
	do_test 42 1 1 1 0
	
	do_test 56 1 1 1 0
	
	#GPU=1
	do_test 0 0 0 0 1

	do_test 1 1 1 1 1
	
	do_test 14 1 1 1 1
	
	do_test 28 1 1 1 1
	
	do_test 42 1 1 1 1
	
	do_test 56 1 1 1 1

done
	
echo "Done."
log_it "done=1"
exit 0
