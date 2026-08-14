@echo off
echo Stopping Kanban Studio server...

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /F /PID %%a
)

echo Server stopped.
pause
