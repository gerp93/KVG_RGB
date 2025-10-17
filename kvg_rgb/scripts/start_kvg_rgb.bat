@echo off
REM KVG RGB Controller - Windows Startup Script
REM This script starts the KVG RGB web interface minimized in the background
REM 
REM To set up auto-start:
REM 1. Right-click this file and select "Create shortcut"
REM 2. Press Win+R, type: shell:startup
REM 3. Move the shortcut to the Startup folder

start /min cmd /c "kvg-rgb web"
