@echo off
title Minecraft Printer - Setup
color 0A

echo.
echo  ==========================================
echo   MINECRAFT PRINTER - AUTO SETUP
echo  ==========================================
echo.
echo  This will install everything needed and
echo  launch the printer. Sit tight.
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: Python is not installed or not in PATH.
    echo.
    echo  Download it from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo  [1/5] Python found. Good.
echo.

echo  [2/5] Updating pip...
python -m pip install --upgrade pip --quiet

echo  [3/5] Installing mss, pillow, pygetwindow...
python -m pip install mss pillow pygetwindow --quiet
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install packages.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo  [4/5] Installing pywin32 (silent printer control)...
python -m pip install pywin32 --quiet
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install pywin32.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo  [5/5] All packages installed.
echo.
echo  ==========================================
echo   Launching Minecraft Printer...
echo   Make sure Minecraft is already open.
echo  ==========================================
echo.

python minecraft_printer.py

if errorlevel 1 (
    echo.
    echo  The script exited with an error. See above.
    pause
)
