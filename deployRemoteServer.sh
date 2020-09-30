#!/usr/bin/env bash

ALARM_SERVER_USER="goosealert@<REDACTED>"
ALARM_SERVER_PATH="/home/goosealert/GooseAlert"

echo "Building front end"

npm run-script build --prefix ./REMOTESERVER/client

echo "Starting deployment"

rsync -ar --exclude 'node_modules' REMOTESERVER/*  $ALARM_SERVER_USER:$ALARM_SERVER_PATH

echo "Files copied"

echo "Restarting server..."

ssh $ALARM_SERVER_USER "tmux kill-server; sudo pkill node; tmux new-session -d \"cd $ALARM_SERVER_PATH; npm install --prefix ./server; npm start --prefix ./server; read;\""

echo "Done."
