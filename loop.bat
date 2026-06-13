@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo     AUTONOMOUS MICRO-API FACTORY LOOP STARTING
echo ==================================================

:loop
echo.
echo [FACTORY] Launching main orchestrator to plan, build, and test a new API...
python main.py
set RUN_STATUS=%ERRORLEVEL%

if %RUN_STATUS% NEQ 0 (
    echo.
    echo [FACTORY] [ERROR] Orchestrator exited with error. Retrying in 10 seconds...
    timeout /t 10 >nul
    goto loop
)

echo [FACTORY] API cycle completed successfully. Starting next build in 15 seconds...
timeout /t 15 >nul
goto loop
