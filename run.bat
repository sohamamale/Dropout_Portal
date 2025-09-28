@echo off
echo Starting Student Dropout Prevention Portal...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup...
    python setup.py
    if errorlevel 1 (
        echo Setup failed. Please check the errors above.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if config files exist
if not exist "email_config.py" (
    echo email_config.py not found. Please copy from email_config.py.example and configure.
    pause
    exit /b 1
)

REM Run the application
echo Starting Flask application...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
