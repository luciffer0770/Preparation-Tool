@echo off
title PS-ETW Tracker
cd /d "%~dp0"
python main.py
if errorlevel 1 pause
