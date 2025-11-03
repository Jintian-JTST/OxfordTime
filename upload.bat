@echo off
chcp 65001 >nul
:: === 智能上传脚本 ===
:: 把路径改成你的仓库文件夹，比如 C:\Users\JTST\OxfordTime
cd /d "C:\Users\JTST\OxfordTime"

:: 提示用户输入提交说明
set /p msg=What did you update?：

:: 如果用户没有输入内容，就退出
if "%msg%"=="" (
    echo No input, no submit.
    pause
    exit /b
)

:: 执行上传操作
git add .
git commit -m "%msg%"
git push

echo.
echo complete.
pause
