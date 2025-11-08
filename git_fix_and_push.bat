@echo off
REM === Automatically fix Git lock error and push changes ===
setlocal

REM Change this path to your repository
set REPO_PATH=C:\Users\JTST\OxfordTime

cd /d "%REPO_PATH%"

echo Checking for index.lock file...

if exist ".git\index.lock" (
    echo Found lock file. Removing it...
    del /f /q ".git\index.lock"
) else (
    echo No lock file found.
)

echo.
echo Adding all changes...
git add .

echo.
set /p commitMsg="Enter commit message (default: Auto commit): "
if "%commitMsg%"=="" set commitMsg=Auto commit

echo Committing changes...
git commit -m "%commitMsg%"

echo.
echo Pushing to remote...
git push

echo.
echo Complete.
pause
