@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title JIT API Publisher
cd /d "%~dp0"

if not exist .venv (
    echo [ERROR] Python virtual environment venv not found.
    echo Please run run.ps1 first to setup the environment.
    pause
    exit /b
)

echo Launching JIT API Publisher UI...
".venv\Scripts\python.exe" publisher_ui.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Script execution failed.
    pause
)
