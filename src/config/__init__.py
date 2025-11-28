"""Configuration module for the Agentic Research Assistant."""

from .settings import (
    GEMINI_MODEL_NAME,
    MAX_LOG_BUFFER_SIZE,
    DEFAULT_LOG_LEVEL,
    MAX_PDF_CHARS,
    MAX_ITERATIONS,
    MAX_FUNCTION_ARG_LENGTH,
)

__all__ = [
    "GEMINI_MODEL_NAME",
    "MAX_LOG_BUFFER_SIZE",
    "DEFAULT_LOG_LEVEL",
    "MAX_PDF_CHARS",
    "MAX_ITERATIONS",
    "MAX_FUNCTION_ARG_LENGTH",
]
