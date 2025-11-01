@echo off
chcp 65001 >nul
cd /d "C:\Users\JTST\OxfordTime"

set /p msg=What did you update? Press Enter to escape:

if "%msg%"=="" (
    echo No commit, no update.
    pause
    exit /b
)

git add .
git commit -m "%msg%"
git push

echo.
echo Uploaded!
pause
