"""
UI handlers for source verification functionality.
"""

from src.tools.source_verifier import verify_document_sources, quick_verify_references, quick_verify_claims
from src.tools import extract_text_from_pdf
from src.logging import logger


def verify_text_input(text_input: str, verify_refs: bool, verify_claims_flag: bool) -> str:
    """
    Verify sources in text input.

    Args:
        text_input: Document text to verify
        verify_refs: Whether to verify references
        verify_claims_flag: Whether to verify claims

    Returns:
        Verification report
    """
    if not text_input or text_input.strip() == "":
        return "⚠️ Please provide document text to verify."

    if not verify_refs and not verify_claims_flag:
        return "⚠️ Please select at least one verification option (References or Claims)."

    logger.info(f"🔍 UI REQUEST: Verify text ({len(text_input)} chars, refs={verify_refs}, claims={verify_claims_flag})")

    try:
        result = verify_document_sources(text_input, verify_claims=verify_claims_flag, verify_references=verify_refs)
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in verify_text_input: {str(e)}")
        return f"❌ Error during verification: {str(e)}"


def verify_pdf_input(pdf_path: str, verify_refs: bool, verify_claims_flag: bool) -> str:
    """
    Verify sources in uploaded PDF.

    Args:
        pdf_path: Path to uploaded PDF
        verify_refs: Whether to verify references
        verify_claims_flag: Whether to verify claims

    Returns:
        Verification report
    """
    if not pdf_path:
        return "⚠️ Please upload a PDF file first (use the 'Upload PDF' tab)."

    if not verify_refs and not verify_claims_flag:
        return "⚠️ Please select at least one verification option (References or Claims)."

    logger.info(f"🔍 UI REQUEST: Verify PDF: {pdf_path}")

    try:
        # Extract text from PDF
        logger.info("📄 Extracting text from PDF...")
        paper_text = extract_text_from_pdf(pdf_path)

        if paper_text.startswith("Error"):
            return paper_text

        # Verify the extracted text
        result = verify_document_sources(paper_text, verify_claims=verify_claims_flag, verify_references=verify_refs)
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in verify_pdf_input: {str(e)}")
        return f"❌ Error processing PDF: {str(e)}"


def quick_verify_text_references(text_input: str) -> str:
    """Quick reference-only verification from text."""
    if not text_input or text_input.strip() == "":
        return "⚠️ Please provide document text to verify."

    logger.info(f"🔍 UI REQUEST: Quick reference verification ({len(text_input)} chars)")

    try:
        result = quick_verify_references(text_input)
        return result
    except Exception as e:
        logger.error(f"❌ ERROR in quick_verify_text_references: {str(e)}")
        return f"❌ Error: {str(e)}"


def quick_verify_text_claims(text_input: str) -> str:
    """Quick claim-only verification from text."""
    if not text_input or text_input.strip() == "":
        return "⚠️ Please provide document text to verify."

    logger.info(f"🔍 UI REQUEST: Quick claim verification ({len(text_input)} chars)")

    try:
        result = quick_verify_claims(text_input)
        return result
    except Exception as e:
        logger.error(f"❌ ERROR in quick_verify_text_claims: {str(e)}")
        return f"❌ Error: {str(e)}"
