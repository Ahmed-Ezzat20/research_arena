"""
Logging system for the Agentic Research Assistant.
Provides custom log buffer and handlers for tracking LLM interactions.
"""

import logging
from datetime import datetime
from src.config import MAX_LOG_BUFFER_SIZE, DEFAULT_LOG_LEVEL


class LogBuffer:
    """Custom log buffer that stores logs in memory."""

    def __init__(self):
        self.buffer = []
        self.max_size = MAX_LOG_BUFFER_SIZE

    def add(self, record):
        """Add a log record to the buffer."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.buffer.append({
            "timestamp": timestamp,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })
        # Keep only the last max_size entries
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_logs(self, level_filter="ALL"):
        """Get logs filtered by level."""
        if level_filter == "ALL":
            return self.buffer
        return [log for log in self.buffer if log["level"] == level_filter]

    def clear(self):
        """Clear all logs from the buffer."""
        self.buffer = []

    def format_logs(self, level_filter="ALL"):
        """Format logs as a string for display."""
        logs = self.get_logs(level_filter)
        return "\n".join([
            f"[{log['timestamp']}] {log['level']:8} | {log['module']:20} | {log['message']}"
            for log in logs
        ])


class BufferHandler(logging.Handler):
    """Custom logging handler that writes to LogBuffer."""

    def __init__(self, log_buffer):
        super().__init__()
        self.log_buffer = log_buffer

    def emit(self, record):
        """Emit a log record to the buffer."""
        self.log_buffer.add(record)


# Global log buffer
log_buffer = LogBuffer()

# Configure logging
logger = logging.getLogger("LLM_Assistant")
logger.setLevel(logging.DEBUG)

# Add buffer handler
buffer_handler = BufferHandler(log_buffer)
buffer_handler.setLevel(logging.DEBUG)
logger.addHandler(buffer_handler)

# Add console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log level control (can be changed at runtime)
current_log_level = {"level": DEFAULT_LOG_LEVEL}


def set_log_level(level: str):
    """Set the logging level dynamically."""
    levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    logger.setLevel(levels.get(level, logging.INFO))
    current_log_level["level"] = level
    logger.info(f"Log level changed to {level}")


def get_logger():
    """Get the configured logger instance."""
    return logger


def get_log_buffer():
    """Get the global log buffer instance."""
    return log_buffer
