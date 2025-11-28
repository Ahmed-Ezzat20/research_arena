"""
Gemini model initialization and configuration.
"""

import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME


def get_model_with_tools(tools):
    """
    Initialize a Gemini model with tool calling capabilities.

    Args:
        tools: List of tool declarations for function calling

    Returns:
        GenerativeModel instance configured with tools
    """
    return genai.GenerativeModel(model_name=GEMINI_MODEL_NAME, tools=tools)


def get_model():
    """
    Initialize a basic Gemini model without tools.

    Returns:
        GenerativeModel instance
    """
    return genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
