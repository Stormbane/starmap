@echo off
set TASKNAME=StarMapWallpaperUpdater
set PYTHONW=C:\ProgramData\anaconda3\pythonw.exe
set SCRIPT=C:\Projects\starmap\starmap.py

echo Creating scheduled task "%TASKNAME%"...
echo Runs hourly, 24/7, as the current user, via pythonw.exe (no console flash).

schtasks /delete /tn "%TASKNAME%" /f >nul 2>&1

schtasks /create ^
  /tn "%TASKNAME%" ^
  /tr "\"%PYTHONW%\" \"%SCRIPT%\" --setAsWallpaper" ^
  /sc daily ^
  /st 00:00 ^
  /ri 60 ^
  /du 24:00 ^
  /rl HIGHEST ^
  /f

echo Task "%TASKNAME%" created successfully.
pause
