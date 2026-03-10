@echo off
echo ========================================
echo Azure Agent Chatbot - Quick Install
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r app\requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created!
    echo.
    echo IMPORTANT: Please verify the values in .env file
    echo.
) else (
    echo .env file already exists
    echo.
)

echo Step 3: Running setup checker...
python setup_azure_agent.py
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the chatbot, run:
echo   python -m uvicorn app.main:app --reload --port 8000
echo.
echo Then open: http://localhost:8000
echo.
pause

