"""
Social media post generation tool using customizable prompts.
"""

import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME
from src.logging import logger


def load_post_prompt():
    """Load the social media post prompt from file."""
    with open("prompts/paper_to_post.txt", "r", encoding="utf-8") as f:
        return f.read()


def write_social_media_post(explanation: str) -> str:
    """Create a social-media-friendly post using Gemini API."""
    logger.info(f"🔍 FUNCTION CALL: write_social_media_post(explanation length={len(explanation)} chars)")
    try:
        # Use Gemini to create an engaging social media post
        logger.debug("📤 LLM REQUEST: Social media post generation")
        post_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        post_prompt = load_post_prompt()
        prompt = f"{post_prompt}\n{explanation}"
        logger.debug(f"  Using POST_PROMPT ({len(post_prompt)} chars) + explanation")
        response = post_model.generate_content(prompt)
        logger.info(f"📥 LLM RESPONSE: Post generated ({len(response.text)} chars)")
        logger.debug(f"  Preview: {response.text[:150]}...")
        return response.text
    except Exception as e:
        logger.error(f"❌ ERROR in write_social_media_post: {str(e)}")
        return f"Error creating post: {str(e)}"
