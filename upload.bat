@echo off
chcp 437 >nul
:: --- Auto push script (ASCII only) ---
cd /d "C:\Users\JTST\OxfordTime"

:: Commit current changes
git add .
git commit -m "auto update" 2>nul

:: Pull remote updates before pushing
echo Pulling latest changes from remote...
git pull --rebase origin main
if errorlevel 1 (
    echo Rebase failed or conflicts detected.
    echo Please fix conflicts manually, then run:
    echo   git add <file>
    echo   git rebase --continue
    echo Or cancel with:
    echo   git rebase --abort
    pause
    exit /b 1
)

:: Push local commits
echo Pushing to remote...
git push origin main

echo.
echo Upload completed.
pause
