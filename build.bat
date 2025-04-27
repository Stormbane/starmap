@echo off
echo Building Starmap application...
python utils/build.py
if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo The executable and config file are in the 'dist' folder.
) else (
    echo Build failed. Check build.log for details.
)
pause 