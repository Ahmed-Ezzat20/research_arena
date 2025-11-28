"""
Research paper explanation tool using customizable prompts.
"""

import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME
from src.logging import logger


def load_explainer_prompt():
    """Load the explainer prompt from file."""
    with open("prompts/Explainer_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()


def explain_research_paper(paper_info: str) -> str:
    """Explain a research paper using Gemini API."""
    logger.info(f"🔍 FUNCTION CALL: explain_research_paper(paper_info length={len(paper_info)} chars)")
    try:
        # Use Gemini to explain the paper without function calling
        logger.debug("📤 LLM REQUEST: Paper explanation")
        explain_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        explainer_prompt = load_explainer_prompt()
        prompt = f"{explainer_prompt}\n\nUser Input:\n{paper_info}"
        logger.debug(f"  Using EXPLAINER_PROMPT ({len(explainer_prompt)} chars) + paper info")
        response = explain_model.generate_content(prompt)
        logger.info(f"📥 LLM RESPONSE: Explanation generated ({len(response.text)} chars)")
        logger.debug(f"  Preview: {response.text[:150]}...")
        return response.text
    except Exception as e:
        logger.error(f"❌ ERROR in explain_research_paper: {str(e)}")
        return f"Error explaining paper: {str(e)}"
