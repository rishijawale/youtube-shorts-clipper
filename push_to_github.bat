@echo off
title Push to GitHub
cd /d "%~dp0"
echo ======================================================
echo   Pushing youtube-shorts-clipper to GitHub
echo   Target: https://github.com/rishijawale/youtube-shorts-clipper
echo ======================================================
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Your repository is now live on GitHub!
    echo Visit: https://github.com/rishijawale/youtube-shorts-clipper
) else (
    echo [ERROR] Push failed. Make sure you are signed in to GitHub.
)
echo.
pause
