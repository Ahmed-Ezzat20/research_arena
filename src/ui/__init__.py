"""UI module for Research Arena - Streamlined 2-tab interface."""

from .chat import chat
from .pdf_upload import (
    handle_pdf_upload,
    analyze_uploaded_pdf,
    explain_pdf,
    post_from_pdf,
)
from .logs import get_logs, clear_logs, refresh_logs
from .logs import change_log_level
from .infographic import (
    generate_infographic_from_text,
    generate_infographic_from_pdf,
)
from .verification import (
    verify_text_input,
    verify_pdf_input,
    quick_verify_text_references,
    quick_verify_text_claims,
)
from .recommendations import (
    recommend_from_text,
    recommend_from_pdf,
    quick_recommend_by_id,
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
    "verify_text_input",
    "verify_pdf_input",
    "quick_verify_text_references",
    "quick_verify_text_claims",
    "recommend_from_text",
    "recommend_from_pdf",
    "quick_recommend_by_id",
]
