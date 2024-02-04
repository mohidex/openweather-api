#!/bin/bash

# Usage: ./wait-for-it.sh <host> <port> [timeout]

host="$1"
port="$2"
timeout="${3:-120}" # Default timeout is 120 seconds

echo "Waiting for $host:$port to be reachable..."

# Loop until the port is open or the timeout is reached
until nc -z "$host" "$port" >/dev/null 2>&1; do
    sleep 1
    ((timeout--))

    if [ "$timeout" -le 0 ]; then
        echo "Timeout reached. Port $port on $host is not reachable."
        exit 1
    fi
done

echo "Port $port on $host is now reachable!"
exit 0
