#!/bin/bash
# Research Arena - Unix/Linux Launch Script

echo "Starting Research Arena..."
echo

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the application
python3 demo.py
