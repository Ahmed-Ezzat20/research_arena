"""
LLM Provider Factory and Management

This module provides centralized LLM provider management, allowing easy switching
between different providers (Gemini, OpenAI, Anthropic, etc.) via configuration.
"""

import os
import logging
from typing import Optional
from src.providers.base import BaseLLMProvider
from src.providers.gemini import GeminiProvider

logger = logging.getLogger(__name__)


class LLMProviderManager:
    """
    Manages LLM provider instances with singleton pattern.

    This ensures we don't create multiple instances of the same provider,
    which would waste resources and API connections.
    """

    _instance: Optional['LLMProviderManager'] = None
    _provider: Optional[BaseLLMProvider] = None

    def __new__(cls):
        """Singleton pattern - only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_provider(
        self,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Get or create an LLM provider instance.

        Args:
            provider_name: Name of the provider ('gemini', 'openai', 'anthropic').
                         If None, reads from LLM_PROVIDER env var (default: 'gemini')
            api_key: API key for the provider. If None, reads from provider-specific env var
            model_name: Model name override. If None, uses provider's default

        Returns:
            BaseLLMProvider instance

        Raises:
            ValueError: If provider_name is not supported
            ValueError: If API key is not provided or found in environment
        """
        # Determine provider name
        if provider_name is None:
            provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()

        logger.info(f"🔧 Initializing LLM provider: {provider_name}")

        # Create provider based on name
        if provider_name == "gemini":
            # Get Gemini API key
            if api_key is None:
                api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Gemini API key not provided. Set GEMINI_API_KEY environment variable."
                )

            # Get model name from env or config if not provided
            if model_name is None:
                # Import here to avoid circular dependency
                from src.config.settings import GEMINI_MODEL_NAME
                model_name = os.getenv("GEMINI_MODEL_NAME", GEMINI_MODEL_NAME)

            self._provider = GeminiProvider(api_key=api_key, model_name=model_name)

        elif provider_name == "openai":
            # Future: OpenAI provider
            raise NotImplementedError(
                "OpenAI provider not yet implemented. "
                "Set LLM_PROVIDER=gemini or implement OpenAI provider in src/providers/openai.py"
            )

        elif provider_name == "anthropic":
            # Future: Anthropic provider
            raise NotImplementedError(
                "Anthropic provider not yet implemented. "
                "Set LLM_PROVIDER=gemini or implement Anthropic provider in src/providers/anthropic.py"
            )

        else:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: gemini, openai (future), anthropic (future)"
            )

        logger.info(
            f"✅ LLM provider initialized: {self._provider.provider_name} "
            f"(model: {self._provider.model_name})"
        )

        return self._provider

    def reset(self):
        """Reset the provider instance (useful for testing)."""
        self._provider = None
        logger.info("🔄 LLM provider reset")


# Global singleton instance
_manager = LLMProviderManager()


def get_llm(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseLLMProvider:
    """
    Convenience function to get the current LLM provider.

    This is the primary way tools should access the LLM provider.

    Args:
        provider_name: Name of the provider ('gemini', 'openai', 'anthropic').
                     If None, reads from LLM_PROVIDER env var (default: 'gemini')
        api_key: API key for the provider. If None, reads from provider-specific env var
        model_name: Model name override. If None, uses provider's default

    Returns:
        BaseLLMProvider instance

    Example:
        ```python
        from src.core.llm_provider import get_llm

        async def my_tool():
            llm = get_llm()
            response = await llm.generate_simple("What is quantum computing?")
            return response
        ```
    """
    return _manager.get_provider(
        provider_name=provider_name,
        api_key=api_key,
        model_name=model_name
    )


def reset_llm_provider():
    """
    Reset the LLM provider singleton.

    Useful for testing or when switching providers mid-session.
    """
    _manager.reset()
