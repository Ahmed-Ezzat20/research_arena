@echo off
REM Research Arena - Windows Launch Script

echo Starting Research Arena...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the application
python demo.py

pause
