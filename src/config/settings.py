"""
Configuration and environment setup for the Agentic Research Assistant.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configuration
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Logging configuration
MAX_LOG_BUFFER_SIZE = 1000
DEFAULT_LOG_LEVEL = "INFO"

# PDF processing configuration
MAX_PDF_CHARS = 10000

# Agentic loop configuration
MAX_ITERATIONS = 10
MAX_FUNCTION_ARG_LENGTH = 50000
