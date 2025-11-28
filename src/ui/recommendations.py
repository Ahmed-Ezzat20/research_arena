"""
UI handlers for paper recommendation functionality.
"""

from src.tools.paper_recommender import recommend_similar_papers, quick_recommend
from src.tools import extract_text_from_pdf
from src.logging import logger


def recommend_from_text(paper_info: str, num_papers: int = 10) -> str:
    """
    Get similar paper recommendations from text input.

    Args:
        paper_info: Paper information (DOI, arXiv ID, title, or content)
        num_papers: Number of recommendations to return

    Returns:
        Formatted recommendations report
    """
    if not paper_info or paper_info.strip() == "":
        return "⚠️ Please provide paper information (DOI, arXiv ID, title, or content)."

    if num_papers < 1 or num_papers > 20:
        return "⚠️ Number of recommendations must be between 1 and 20."

    logger.info(f"🔍 UI REQUEST: Get recommendations ({len(paper_info)} chars, limit={num_papers})")

    try:
        result = recommend_similar_papers(paper_info, num_recommendations=num_papers)
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in recommend_from_text: {str(e)}")
        return f"❌ Error getting recommendations: {str(e)}"


def recommend_from_pdf(pdf_path: str, num_papers: int = 10) -> str:
    """
    Get similar paper recommendations from uploaded PDF.

    Args:
        pdf_path: Path to uploaded PDF
        num_papers: Number of recommendations to return

    Returns:
        Formatted recommendations report
    """
    if not pdf_path:
        return "⚠️ Please upload a PDF file first (use the 'Upload PDF' tab)."

    if num_papers < 1 or num_papers > 20:
        return "⚠️ Number of recommendations must be between 1 and 20."

    logger.info(f"🔍 UI REQUEST: Get recommendations from PDF: {pdf_path}")

    try:
        # Extract text from PDF
        logger.info("📄 Extracting text from PDF...")
        paper_text = extract_text_from_pdf(pdf_path)

        if paper_text.startswith("Error"):
            return paper_text

        # Get recommendations based on extracted text
        result = recommend_similar_papers(paper_text, num_recommendations=num_papers)
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in recommend_from_pdf: {str(e)}")
        return f"❌ Error processing PDF: {str(e)}"


def quick_recommend_by_id(paper_id: str, num_papers: int = 5) -> str:
    """
    Quick recommendations by DOI or arXiv ID.

    Args:
        paper_id: DOI or arXiv ID
        num_papers: Number of recommendations

    Returns:
        Formatted recommendations report
    """
    if not paper_id or paper_id.strip() == "":
        return "⚠️ Please provide a DOI or arXiv ID."

    if num_papers < 1 or num_papers > 20:
        return "⚠️ Number of recommendations must be between 1 and 20."

    logger.info(f"🔍 UI REQUEST: Quick recommend for ID: {paper_id}")

    try:
        result = quick_recommend(paper_id, num_papers=num_papers)
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in quick_recommend_by_id: {str(e)}")
        return f"❌ Error: {str(e)}"
