"""
Logs Tab Components and Handlers
Provides log viewing, filtering, and management functionality.
"""

from src.logging import log_buffer, logger


def get_logs() -> str:
    """
    Retrieve all logs from the buffer.
    
    Returns:
        Formatted log string
    """
    return log_buffer.format_logs("INFO")


def clear_logs() -> str:
    """
    Clear the log buffer.
    
    Returns:
        Confirmation message
    """
    log_buffer.clear()
    logger.info("🗑️  Log buffer cleared by user")
    return "✅ Logs cleared!"


def refresh_logs() -> str:
    """
    Refresh the log display.
    
    Returns:
        Current formatted logs
    """
    return log_buffer.format_logs("INFO")


def change_log_level(level: str) -> str:
    """
    Change the log level filter and return filtered logs.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Filtered log string
    """
    logger.info(f"🎚️  Log level changed to: {level}")
    return log_buffer.format_logs(level)
