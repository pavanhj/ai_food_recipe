@echo off
title AI Food Recipe Preparation & Recommendation System
echo ========================================================
echo Starting AI Food Recipe System...
echo ========================================================

cd /d "%~dp0"

REM Check if .venv python exists, otherwise use system python
if exist ".venv\Scripts\python.exe" (
    set "PY_EXE=.venv\Scripts\python.exe"
) else (
    set "PY_EXE=python"
)

echo Opening Web Browser at http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000

echo Starting Flask Server...
"%PY_EXE%" app.py

pause
