"""
Logs tab components and handlers.
"""

from src.logging import log_buffer, logger


def get_logs(level_filter):
    """Retrieve formatted logs from the buffer."""
    return log_buffer.format_logs(level_filter)


def clear_logs():
    """Clear the log buffer."""
    log_buffer.clear()
    logger.info("🗑️  Log buffer cleared")
    return "Logs cleared!"


def refresh_logs(level_filter):
    """Refresh the log display."""
    return log_buffer.format_logs(level_filter)
