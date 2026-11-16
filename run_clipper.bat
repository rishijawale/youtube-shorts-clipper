@echo off
title YouTube Shorts Highlight Clipper
echo ======================================================
echo       YouTube Shorts Highlight Clipper
echo ======================================================
echo.
set /p YOUTUBE_URL="Enter YouTube Video URL: "
if "%YOUTUBE_URL%"=="" goto end

echo.
echo Select Framing Mode:
echo [1] Blurred Background (Recommended for 16:9 widescreen)
echo [2] Center Crop (Full vertical crop)
echo [3] Letterbox Fit
set /p MODE_CHOICE="Choice (default 1): "

set CLIP_MODE=blur
if "%MODE_CHOICE%"=="2" set CLIP_MODE=crop
if "%MODE_CHOICE%"=="3" set CLIP_MODE=fit

set /p CLIP_DUR="Enter Clip Duration in seconds (default 45): "
if "%CLIP_DUR%"=="" set CLIP_DUR=45

set /p TOP_N="How many top highlight clips to generate (default 1): "
if "%TOP_N%"=="" set TOP_N=1

echo.
echo [*] Processing video with NVIDIA GPU NVENC acceleration...
python "%~dp0scripts\clipper.py" "%YOUTUBE_URL%" --duration %CLIP_DUR% --top-n %TOP_N% --mode %CLIP_MODE% --output-dir "%~dp0output"

echo.
echo ======================================================
echo [Done] Check the output folder: %~dp0output
echo ======================================================
pause

:end
