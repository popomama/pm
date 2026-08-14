#!/bin/bash

echo "Stopping Kanban Studio server..."

PID=$(lsof -ti:8000)

if [ -z "$PID" ]; then
    echo "No server running on port 8000"
else
    echo "Killing process $PID"
    kill -9 $PID
    echo "Server stopped."
fi
