"""
Research Paper Explainer Tool - Refactored with async and provider abstraction
Explains research papers using customizable prompts.
"""

from src.logging import logger
from src.providers.base import BaseLLMProvider


def load_explainer_prompt() -> str:
    """Load the explainer prompt from file."""
    try:
        with open("prompts/Explainer_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("⚠️ Explainer_prompt.txt not found, using default prompt")
        return """You are a research assistant. Explain the following research paper in clear, accessible language.
        
Include:
- Main research question
- Methodology
- Key findings
- Significance and implications

Use Modern Standard Arabic with technical terms in English."""


async def explain_research_paper(
    paper_info: str,
    provider: BaseLLMProvider
) -> str:
    """
    Explain a research paper using LLM.
    
    Args:
        paper_info: Research paper information or text
        provider: LLM provider instance
        
    Returns:
        Detailed explanation of the paper
    """
    logger.info(f"🔍 Explaining research paper ({len(paper_info)} chars)")
    
    try:
        # Load custom prompt
        explainer_prompt = load_explainer_prompt()
        
        # Combine prompt with paper info
        full_prompt = f"{explainer_prompt}\n\nUser Input:\n{paper_info}"
        
        logger.debug("📤 LLM REQUEST: Paper explanation")
        
        # Generate explanation
        explanation = await provider.generate_simple(
            prompt=full_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        logger.info(f"✅ Explanation generated ({len(explanation)} chars)")
        return explanation
        
    except Exception as e:
        logger.error(f"❌ Error explaining paper: {str(e)}")
        return f"Error explaining paper: {str(e)}"
