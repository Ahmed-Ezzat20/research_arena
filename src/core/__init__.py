"""Core business logic for the Agentic Research Assistant."""

from .llm_provider import get_llm, LLMProviderManager

__all__ = ["get_llm", "LLMProviderManager"]
