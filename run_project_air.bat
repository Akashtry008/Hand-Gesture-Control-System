@echo off
title Project Air - Spatial Gesture Control
echo ========================================================
echo   PROJECT AIR : SPATIAL GESTURE CONTROL SYSTEM
echo   AI Air Mouse, Node Constellation, Macro Engine & Virtual Cam
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    echo Starting Project Air via Virtual Environment...
    .\.venv\Scripts\python.exe main_v3.py
) else (
    echo Virtual environment not found, attempting global Python...
    python main_v3.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error code.
    pause
)
