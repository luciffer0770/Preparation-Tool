@echo off
title PS-ETW Tracker
cd /d "%~dp0"
REM Python 3 is required (Python 2 fails with SyntaxError on UTF-8 / modern syntax).
where py >nul 2>&1 && py -3 main.py && goto :eof
where python3 >nul 2>&1 && python3 main.py && goto :eof
python main.py
if errorlevel 1 (
  echo.
  echo This app requires Python 3. Try: py -3 main.py
  echo Or install Python 3 from https://www.python.org/downloads/
  pause
)
