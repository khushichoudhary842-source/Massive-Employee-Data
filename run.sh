#!/bin/bash
# Quick Start Guide for Employee Analytics Dashboard

# This script helps you get the dashboard running quickly

echo "====================================="
echo "Employee Analytics Dashboard Setup"
echo "====================================="
echo ""

# Check Python installation
echo "[1] Checking Python installation..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python found"
echo ""

# Install dependencies
echo "[2] Installing required packages..."
pip install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo "✓ Packages installed successfully"
else
    echo "⚠ Some packages may not have installed. Attempting individual installation..."
    pip install streamlit pandas numpy plotly -q
fi
echo ""

# Verify data file
echo "[3] Verifying data file..."
if [ -f "cleaned_employee_dataset_for_dashboard.csv" ]; then
    echo "✓ Data file found"
    # Show row count
    ROWS=$(python -c "import pandas as pd; print(len(pd.read_csv('cleaned_employee_dataset_for_dashboard.csv')))")
    echo "  Loaded $ROWS employee records"
else
    echo "❌ Data file 'cleaned_employee_dataset_for_dashboard.csv' not found!"
    exit 1
fi
echo ""

# Launch dashboard
echo "[4] Launching dashboard..."
echo "The dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "====================================="
echo ""

streamlit run app.py

