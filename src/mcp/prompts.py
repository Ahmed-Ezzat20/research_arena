"""
MCP Prompts Registry

This module registers custom prompts as MCP prompts, making them accessible
to MCP clients like Claude Desktop.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.config.mcp_config import PROMPTS_DIR

logger = logging.getLogger(__name__)


class PromptRegistry:
    """
    Registry for MCP prompts.

    Manages loading and providing access to prompt templates.
    """

    def __init__(self):
        """Initialize the prompt registry."""
        self._prompts: Dict[str, Dict[str, Any]] = {}
        self._load_prompts()
        logger.info(f"📝 Prompt registry initialized with {len(self._prompts)} prompts")

    def _load_prompt_file(self, filepath: Path) -> str:
        """Load a prompt from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Failed to load prompt from {filepath}: {e}")
            return ""

    def _load_prompts(self):
        """Load all prompts from the prompts directory."""
        prompts_to_load = [
            {
                "name": "explainer",
                "file": "Explainer_prompt.txt",
                "description": "Explain a research paper in clear, non-technical language (Modern Standard Arabic with technical terms in English)",
                "arguments": [
                    {
                        "name": "paper_info",
                        "description": "The research paper information to explain",
                        "required": True
                    }
                ]
            },
            {
                "name": "paper_to_post",
                "file": "paper_to_post.txt",
                "description": "Create a social-media-friendly post (Arabic with Egyptian dialect) summarizing a research paper",
                "arguments": [
                    {
                        "name": "explanation",
                        "description": "The paper explanation to convert into a social media post",
                        "required": True
                    }
                ]
            },
            {
                "name": "infographic",
                "file": "infographic_prompt.txt",
                "description": "Generate design guidelines for creating an academic infographic from a research paper",
                "arguments": [
                    {
                        "name": "paper_info",
                        "description": "The research paper information to visualize",
                        "required": True
                    }
                ]
            },
            {
                "name": "claim_extraction",
                "file": "claim_extraction_prompt.txt",
                "description": "Extract verifiable scientific claims from a research document",
                "arguments": [
                    {
                        "name": "document_text",
                        "description": "The document text to extract claims from",
                        "required": True
                    }
                ]
            },
            {
                "name": "claim_verification",
                "file": "claim_verification_prompt.txt",
                "description": "Verify a scientific claim using provided evidence with confidence scoring",
                "arguments": [
                    {
                        "name": "claim",
                        "description": "The claim to verify",
                        "required": True
                    },
                    {
                        "name": "evidence",
                        "description": "Supporting and contradicting evidence",
                        "required": True
                    }
                ]
            },
        ]

        for prompt_def in prompts_to_load:
            filepath = PROMPTS_DIR / prompt_def["file"]
            if filepath.exists():
                content = self._load_prompt_file(filepath)
                self._prompts[prompt_def["name"]] = {
                    "name": prompt_def["name"],
                    "description": prompt_def["description"],
                    "arguments": prompt_def["arguments"],
                    "content": content
                }
                logger.debug(f"✅ Loaded prompt: {prompt_def['name']}")
            else:
                logger.warning(f"⚠️ Prompt file not found: {filepath}")

    def get_prompt(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a prompt by name.

        Args:
            name: Prompt name

        Returns:
            Prompt dictionary or None if not found
        """
        return self._prompts.get(name)

    def get_prompt_content(
        self,
        name: str,
        arguments: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Get prompt content with arguments injected.

        Args:
            name: Prompt name
            arguments: Dictionary of argument values

        Returns:
            Formatted prompt content or None if not found
        """
        prompt = self.get_prompt(name)
        if not prompt:
            return None

        content = prompt["content"]

        # Inject arguments if provided
        if arguments:
            for arg_name, arg_value in arguments.items():
                placeholder = f"{{{arg_name}}}"
                content = content.replace(placeholder, str(arg_value))

        return content

    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts.

        Returns:
            List of prompt metadata (without full content)
        """
        return [
            {
                "name": p["name"],
                "description": p["description"],
                "arguments": p["arguments"]
            }
            for p in self._prompts.values()
        ]

    def get_prompt_names(self) -> List[str]:
        """Get list of all prompt names."""
        return list(self._prompts.keys())


# Global singleton instance
_prompt_registry = PromptRegistry()


def get_prompt_registry() -> PromptRegistry:
    """
    Get the global prompt registry instance.

    Returns:
        PromptRegistry singleton
    """
    return _prompt_registry


def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Convenience function to get a prompt with arguments.

    Args:
        name: Prompt name
        arguments: Argument values

    Returns:
        Formatted prompt content
    """
    return _prompt_registry.get_prompt_content(name, arguments)
