@echo off
setlocal enabledelayedexpansion
:: Change to project root directory (one level up from utils)
cd /d %~dp0\..

:: Verify we're in the correct directory by checking for key files
if not exist starmap.py (
    echo ERROR: Could not find starmap.py. Please run this script from the project root directory.
    exit /b 1
)

if not exist config.yaml (
    echo ERROR: Could not find config.yaml. Please run this script from the project root directory. 
    exit /b 1
)

:: Set up logging
set LOGFILE=build.log
echo %date% %time% - INFO - Build script started >> %LOGFILE%

:: Run PyInstaller with spec file
echo %date% %time% - INFO - Running PyInstaller with spec file... >> %LOGFILE%
pyinstaller starmap.spec
if %ERRORLEVEL% neq 0 (
    echo %date% %time% - ERROR - PyInstaller failed >> %LOGFILE%
    exit /b 1
)

echo %date% %time% - INFO - PyInstaller completed successfully >> %LOGFILE%

:: Copy config.yaml to dist folder
echo %date% %time% - INFO - Copying config file to dist folder >> %LOGFILE%
copy config.yaml dist\config.yaml
if %ERRORLEVEL% neq 0 (
    echo %date% %time% - ERROR - Failed to copy config file >> %LOGFILE%
    exit /b 1
)

echo %date% %time% - INFO - Build process completed successfully >> %LOGFILE%

endlocal



