@echo off
title PS-ETW Tracker — Desktop Shortcut
setlocal
cd /d "%~dp0"

set "SCRIPT=%~dp0Launch_PS_ETW.bat"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\PS-ETW Tracker.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT%'); ^
   $s.TargetPath='%SCRIPT%'; ^
   $s.WorkingDirectory='%~dp0'; ^
   $s.Description='PS-ETW Engine Build-Up Tracker'; ^
   $s.Save()"

if exist "%SHORTCUT%" (
  echo Shortcut created: %SHORTCUT%
) else (
  echo Failed to create shortcut.
)
pause
