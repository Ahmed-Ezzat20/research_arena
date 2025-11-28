"""
UI handlers for infographic generation functionality.
"""

import os
from src.tools import generate_paper_infographic
from src.logging import logger


def generate_infographic_from_text(paper_text: str) -> tuple[str, str]:
    """
    Generate infographic from paper text input.

    Args:
        paper_text: Research paper text or summary

    Returns:
        tuple: (status_message, image_path or empty string)
    """
    if not paper_text or paper_text.strip() == "":
        return "⚠️ Please provide paper text or summary.", None

    logger.info(f"🎨 UI REQUEST: Generate infographic from text ({len(paper_text)} chars)")

    try:
        result = generate_paper_infographic(paper_text)

        # Check if the result contains a file path
        if "generated_infographics" in result:
            # Extract the file path from the success message
            for line in result.split('\n'):
                if "Saved to:" in line or "generated_infographics" in line:
                    # Find the path
                    import re
                    path_match = re.search(r'generated_infographics[/\\][\w_]+\.jpg', result)
                    if path_match:
                        filepath = path_match.group(0)
                        if os.path.exists(filepath):
                            return result, filepath

        # If no image was generated but we got a structured summary
        return result, None

    except Exception as e:
        logger.error(f"❌ ERROR in generate_infographic_from_text: {str(e)}")
        return f"Error generating infographic: {str(e)}", None


def generate_infographic_from_pdf(pdf_path_store: str) -> tuple[str, str]:
    """
    Generate infographic from uploaded PDF.

    Args:
        pdf_path_store: Path to the uploaded PDF file

    Returns:
        tuple: (status_message, image_path or empty string)
    """
    if not pdf_path_store:
        return "⚠️ Please upload a PDF file first.", None

    logger.info(f"🎨 UI REQUEST: Generate infographic from PDF: {pdf_path_store}")

    try:
        # First extract text from the PDF
        from src.tools import extract_text_from_pdf

        paper_text = extract_text_from_pdf(pdf_path_store)
        if paper_text.startswith("Error"):
            return paper_text, None

        # Generate the infographic
        return generate_infographic_from_text(paper_text)

    except Exception as e:
        logger.error(f"❌ ERROR in generate_infographic_from_pdf: {str(e)}")
        return f"Error processing PDF: {str(e)}", None
