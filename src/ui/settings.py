"""
Settings tab components and handlers.
"""

from src.logging import set_log_level


def change_log_level(level):
    """Change the logging level."""
    set_log_level(level)
    return f"Log level set to {level}"
