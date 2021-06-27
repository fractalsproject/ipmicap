
SERVER="http://192.168.99.112:3000"

set -e
set -x

log_it () {
    #curl --silent "$SERVER/log?$1" > /dev/null
	curl  "$SERVER/log?$1" 
	if [ ! "$?" -eq "0" ]; then
		echo "Message send failed."
		exit 1
	fi
}

session_it () {
    #curl --silent "$SERVER/log?$1" > /dev/null
	curl  "$SERVER/session?$1" 
	if [ ! "$?" -eq "0" ]; then
		echo "Message send failed."
		exit 1
	fi
}

sleep 1

log_it "ping=1"
sleep 1

session_it "start=1&id=ababababab"
sleep 1

session_it "start=1&id=cdcdcdcd"
sleep 1

session_it "stop=1&id=cdcdcdcd"
sleep 1

session_it "stop=1&id=ababababab"
sleep 1

session_it "start=1&id=efefefefef"
session_it "stop=1&id=efefefefef"
