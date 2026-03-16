@echo off
title Minecraft Printer - Compiler
color 0A

echo.
echo  ==========================================
echo   MINECRAFT PRINTER - COMPILER
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: Python not found.
    echo  Download from: https://www.python.org/downloads/
    echo  Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo  [1/6] Python found.

:: Install dependencies
echo  [2/6] Installing dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install mss pillow pygetwindow pywin32 pyinstaller --quiet
if errorlevel 1 (
    color 0C
    echo  ERROR: pip install failed. Check your internet.
    pause
    exit /b 1
)

echo  [3/6] Dependencies installed.

:: Compile to exe
echo  [4/6] Compiling to .exe (this will take a minute)...
pyinstaller --onefile --noconsole --name "MinecraftPrinter" --hidden-import=win32print --hidden-import=win32ui --hidden-import=PIL.ImageWin --hidden-import=pygetwindow --hidden-import=mss minecraft_printer.py >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: Compilation failed.
    echo  Re-run this script and check the output.
    pause
    exit /b 1
)

echo  [5/6] Compiled successfully.

:: Move exe to current folder for convenience
if exist "dist\MinecraftPrinter.exe" (
    copy /Y "dist\MinecraftPrinter.exe" "MinecraftPrinter.exe" >nul
    rmdir /S /Q dist >nul 2>&1
    rmdir /S /Q build >nul 2>&1
    del /Q MinecraftPrinter.spec >nul 2>&1
    echo  [6/6] Cleaned up build files.
) else (
    color 0C
    echo  ERROR: EXE not found after build. Something went wrong.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   MinecraftPrinter.exe is ready.
echo   Launching now...
echo   Make sure Minecraft is open first.
echo  ==========================================
echo.

start "" "MinecraftPrinter.exe"
exit
