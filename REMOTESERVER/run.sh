#!/usr/bin/env bash

echo "Building frontend"

npm run build --prefix ./client

echo "Starting backend"

npm start build --prefix ./server