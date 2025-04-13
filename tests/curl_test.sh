#!/bin/bash

SID=$(curl http://localhost:3000/session?start=1)
if [ -z "${SID//[0-9]}" ]; then
    echo "Got session_id=${SID}"
    sleep 2
    STATS=$(curl http://localhost:3000/session?stop=all_stats&id=${SID})
    echo "Stats=${STATS}"
else
    echo "Invalid session id"
    exit 1
fi
