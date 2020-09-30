#!/usr/bin/env bash

ALARM_SERVER_USER="pi@10.8.0.9"
ALARM_SERVER_PATH="/home/pi/GooseAlert/ALARMSERVER"

echo "Killing watchdog"

ssh $ALARM_SERVER_USER "tmux kill-server; sudo pkill python3;"

echo "Starting deployment"

scp -i ~/.ssh/id_rsa -r ALARMSERVER/* $ALARM_SERVER_USER:$ALARM_SERVER_PATH

echo "Files copied"

echo "Restarting server..."

ssh $ALARM_SERVER_USER "tmux new-session -d \"cd $ALARM_SERVER_PATH; sudo python3 heartbeat.py; read;\"; tmux new-session -d \"cd $ALARM_SERVER_PATH; sudo python3 server.py; read;\""

echo "Done."