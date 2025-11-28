"""Tools module for the Agentic Research Assistant."""

from .arxiv_search import retrieve_related_papers
from .explainer import explain_research_paper
from .social_post import write_social_media_post
from .pdf_processor import extract_text_from_pdf, process_uploaded_pdf
from .infographic_generator import generate_paper_infographic
from .source_verifier import verify_document_sources, quick_verify_references, quick_verify_claims

__all__ = [
    "retrieve_related_papers",
    "explain_research_paper",
    "write_social_media_post",
    "extract_text_from_pdf",
    "process_uploaded_pdf",
    "generate_paper_infographic",
    "verify_document_sources",
    "quick_verify_references",
    "quick_verify_claims",
]
