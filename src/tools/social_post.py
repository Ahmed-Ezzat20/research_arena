"""
Social Media Post Generator - Refactored with async and provider abstraction
Creates engaging social media posts from research paper explanations.
"""

from src.logging import logger
from src.providers.base import BaseLLMProvider


def load_post_prompt() -> str:
    """Load the social media post prompt from file."""
    try:
        with open("prompts/paper_to_post.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("⚠️ paper_to_post.txt not found, using default prompt")
        return """You are a social media content creator. Convert the following research explanation into an engaging social media post.

Requirements:
- Use Arabic with Egyptian dialect
- 200-300 words
- Make it accessible and engaging
- Include relevant hashtags
- Maintain scientific accuracy"""


async def write_social_media_post(
    explanation: str,
    provider: BaseLLMProvider
) -> str:
    """
    Create a social-media-friendly post from a research explanation.
    
    Args:
        explanation: Research paper explanation
        provider: LLM provider instance
        
    Returns:
        Engaging social media post
    """
    logger.info(f"🔍 Creating social media post ({len(explanation)} chars input)")
    
    try:
        # Load custom prompt
        post_prompt = load_post_prompt()
        
        # Combine prompt with explanation
        full_prompt = f"{post_prompt}\n\n{explanation}"
        
        logger.debug("📤 LLM REQUEST: Social media post generation")
        
        # Generate post
        post = await provider.generate_simple(
            prompt=full_prompt,
            temperature=0.8,  # Higher temperature for creativity
            max_tokens=800
        )
        
        logger.info(f"✅ Social media post generated ({len(post)} chars)")
        return post
        
    except Exception as e:
        logger.error(f"❌ Error creating post: {str(e)}")
        return f"Error creating post: {str(e)}"
