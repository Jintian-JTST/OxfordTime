@echo off
chcp 437 >nul
:: --- Auto upload with pull/resolve logic (ASCII only) ---
:: Edit the REPO path below to your repository folder
set "REPO=C:\Users\JTST\OxfordTime"
set "BRANCH=main"

cd /d "%REPO%" 2>nul
if errorlevel 1 (
  echo ERROR: Could not change directory to "%REPO%".
  echo Check the REPO path in this script and try again.
  pause
  exit /b 1
)

echo.
set /p MSG=What did you update? Press Enter to escape: 
if "%MSG%"=="" (
  echo No commit message entered. Exiting without commit or push.
  pause
  exit /b 0
)

echo.
echo Staging changes...
git add .
echo Committing...
git commit -m "%MSG%" 2>nul

echo.
echo Attempting to pull latest changes (rebase + autostash)...
git pull --rebase --autostash origin %BRANCH%
if errorlevel 1 (
    echo.
    echo Rebase failed or produced conflicts. Trying ordinary pull (merge) as fallback...
    git pull origin %BRANCH%
    if errorlevel 1 (
        echo.
        echo *****************************************************************
        echo CONFLICTS OR ERROR DURING PULL. Automatic merge failed.
        echo You must resolve conflicts manually. Follow these steps:
        echo 1) Run: git status
        echo    - Files with conflicts will be marked as "both modified" or "unmerged".
        echo 2) Edit each conflicted file and fix the conflict markers:
        echo    <<<<<<< HEAD
        echo    (your local changes)
        echo    =======
        echo    (incoming changes from remote)
        echo    >>>>>>> branch
        echo 3) For each file you fixed run:
        echo    git add <file>
        echo 4) If you used rebase and it stopped, continue rebase with:
        echo    git rebase --continue
        echo    OR if you used merge, commit the merge:
        echo    git commit -m "Resolve merge conflicts"
        echo 5) Finally push your branch:
        echo    git push origin %BRANCH%
        echo *****************************************************************
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Pushing local commits to remote...
git push origin %BRANCH%
if errorlevel 1 (
  echo.
  echo ERROR: push failed. Try running:
  echo   git status
  echo   git pull --rebase origin %BRANCH%
  echo   resolve conflicts if any, then:
  echo   git push origin %BRANCH%
  pause
  exit /b 1
)

echo.
echo Upload completed successfully.
pause
exit /b 0
