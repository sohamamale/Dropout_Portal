#!/bin/bash

echo "Starting Student Dropout Prevention Portal..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please check the errors above."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if config files exist
if [ ! -f "email_config.py" ]; then
    echo "email_config.py not found. Please copy from email_config.py.example and configure."
    exit 1
fi

# Run the application
echo "Starting Flask application..."
echo "Open http://localhost:5000 in your browser"
echo "Press Ctrl+C to stop the server"
echo
python app.py
