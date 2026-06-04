#!/bin/bash

# SQL Security HUD - Linux/macOS Startup Script

echo "========================================"
echo "SQL Server Security HUD"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "ERROR: Python $REQUIRED_VERSION+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating .env from .env.example..."

    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo "Created .env file. Please edit it with your SQL Server credentials:"
        echo ""
        echo "  vim .env"
        echo ""
        read -p "Press Enter after editing .env..."
    else
        echo "ERROR: .env.example not found"
        exit 1
    fi
fi

# Check if dependencies are installed
echo ""
echo "Checking Python dependencies..."
python3 -c "import flask, pyodbc, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Start the application
echo ""
echo "========================================"
echo "Starting SQL Security HUD..."
echo "========================================"
echo ""
echo "Access the application at: http://localhost:5000"
echo ""
echo "Demo Login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 app.py
