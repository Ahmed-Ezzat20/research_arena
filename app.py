"""
Research Arena Application Entry Point
Run this file to start the Gradio application.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main application
from src.main import main

if __name__ == "__main__":
    main()
