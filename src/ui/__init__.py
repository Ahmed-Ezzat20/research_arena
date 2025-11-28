"""UI module for the Agentic Research Assistant."""

from .chat import chat
from .pdf_upload import (
    handle_pdf_upload,
    analyze_uploaded_pdf,
    explain_pdf,
    post_from_pdf,
)
from .logs import get_logs, clear_logs, refresh_logs
from .settings import change_log_level
from .infographic import (
    generate_infographic_from_text,
    generate_infographic_from_pdf,
)

__all__ = [
    "chat",
    "handle_pdf_upload",
    "analyze_uploaded_pdf",
    "explain_pdf",
    "post_from_pdf",
    "get_logs",
    "clear_logs",
    "refresh_logs",
    "change_log_level",
    "generate_infographic_from_text",
    "generate_infographic_from_pdf",
]
