"""
PDF upload tab components and handlers.
"""

from src.logging import logger
from src.tools import extract_text_from_pdf, process_uploaded_pdf, explain_research_paper, write_social_media_post


# Global variable to store uploaded PDF path
uploaded_pdf_path = {"path": None}


def handle_pdf_upload(pdf_file):
    """Handle PDF file upload and store the path."""
    if pdf_file is None:
        return "No file uploaded.", ""

    logger.info(f"📄 PDF uploaded: {pdf_file.name}")
    uploaded_pdf_path["path"] = pdf_file.name

    # Extract and preview text
    preview_text = extract_text_from_pdf(pdf_file.name)

    if preview_text.startswith("Error") or preview_text.startswith("PDF support"):
        return preview_text, ""

    # Show preview (first 500 chars)
    preview = preview_text[:500] + "..." if len(preview_text) > 500 else preview_text

    return f"✅ PDF uploaded successfully!\n\n**Preview:**\n{preview}", pdf_file.name


def analyze_uploaded_pdf(pdf_path):
    """Analyze the uploaded PDF."""
    if not pdf_path:
        return "Please upload a PDF file first."

    logger.info(f"🔍 Analyzing uploaded PDF: {pdf_path}")
    result = process_uploaded_pdf(pdf_path)
    return result


def explain_pdf(pdf_path):
    """Generate detailed explanation of the uploaded PDF."""
    if not pdf_path:
        return "Please upload a PDF file first."
    text = extract_text_from_pdf(pdf_path)
    if len(text) > 8000:
        text = text[:8000] + "\n\n[Text truncated...]"
    return explain_research_paper(text)


def post_from_pdf(pdf_path):
    """Create social media post from the uploaded PDF."""
    if not pdf_path:
        return "Please upload a PDF file first."
    analysis = analyze_uploaded_pdf(pdf_path)
    return write_social_media_post(analysis)
