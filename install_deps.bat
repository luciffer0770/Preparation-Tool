@echo off
title PS-ETW Tracker — Setup
echo ==========================================
echo  PS-ETW Engine Build-Up Tracker
echo  Dependency Setup
echo ==========================================
echo.
echo Only 1 dependency needed: openpyxl
echo.
call conda activate base 2>nul || echo (Using system Python)
conda install openpyxl -y 2>nul || pip install openpyxl -r "%~dp0requirements.txt"
echo.
echo ==========================================
echo  Done! Launch the app with:
echo    Launch_PS_ETW.bat
echo    or: python main.py
echo ==========================================
pause
