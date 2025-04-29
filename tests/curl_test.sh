#!/bin/bash

PORT=$1
if [ -z "${PORT//[0-9]}" ]; then
    echo "Got port=$PORT"
else
    echo "ERROR: Please specific port"
    exit 1
fi

SID=$(curl http://localhost:${PORT}/session?start=1)
if [ -z "${SID//[0-9]}" ]; then
    echo "Got session_id=${SID}"
    sleep 5
    STATS=$(curl http://localhost:${PORT}/session?stop=all_stats&id=${SID})
    echo "Stats=${STATS}"
else
    echo "WARNING: Invalid session id was returned ($SID)"
    exit 1
fi
