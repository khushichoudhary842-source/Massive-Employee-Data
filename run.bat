@echo off
REM Quick Start Guide for Employee Analytics Dashboard (Windows)
REM Run this script from PowerShell or Command Prompt

echo =====================================
echo Employee Analytics Dashboard Setup
echo =====================================
echo.

REM Check Python installation
echo [1] Checking Python installation...
python --version
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo O Python found
echo.

REM Install dependencies
echo [2] Installing required packages...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ! Some packages may not have installed. Attempting individual installation...
    pip install streamlit pandas numpy plotly -q
)
echo O Packages installed successfully
echo.

REM Verify data file
echo [3] Verifying data file...
if exist "cleaned_employee_dataset_for_dashboard.csv" (
    echo O Data file found
    for /f %%i in ('python -c "import pandas as pd; print(len(pd.read_csv('cleaned_employee_dataset_for_dashboard.csv')))"') do set ROWS=%%i
    echo   Loaded %ROWS% employee records
) else (
    echo X Data file 'cleaned_employee_dataset_for_dashboard.csv' not found!
    pause
    exit /b 1
)
echo.

REM Launch dashboard
echo [4] Launching dashboard...
echo The dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo =====================================
echo.

streamlit run app.py

pause
