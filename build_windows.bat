@echo off
REM Build script for Windows executable

echo ============================================================
echo Income Summary Generator - Windows Build
echo ============================================================

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install PyInstaller
pip install pyinstaller

REM Clean old builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build executable
echo.
echo Building Windows executable...
pyinstaller income_summary.spec

REM Check if build was successful
if exist "dist\IncomeSummaryGenerator.exe" (
    echo.
    echo Build successful!
    echo Executable created: dist\IncomeSummaryGenerator.exe
    echo.
    echo The .exe file is portable and can be shared with the accounting team.
) else (
    echo.
    echo Build failed!
)

pause