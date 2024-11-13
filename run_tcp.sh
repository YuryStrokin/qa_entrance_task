#!/bin/bash
ILIST=($(ifconfig | grep "inet " | awk '{print $2}'))

mkdir -p ./tmp

MINPORT=60000

for i in "${!ILIST[@]}"; do
    SERVER_IP=${ILIST[$i]}
    PORT=$((MINPORT + i))
    python main.py --role recieve --ip $SERVER_IP --port $PORT > "./tmp/reciever_${SERVER_IP}_${PORT}.log" &
    python main.py --role send --server $SERVER_IP > "./tmp/sender_${SERVER_IP}_${PORT}.log" &
done

wait