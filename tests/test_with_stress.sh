#!/bin/bash

SERVER="http://192.168.99.35:3000"

# Make sure to start the ipmiserve on a remote machine

curl -i $SERVER
echo "$?"
