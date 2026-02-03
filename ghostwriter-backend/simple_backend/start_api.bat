@echo off
echo Starting Story Generator API...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the API server
echo.
echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main_with_db.py

pause
