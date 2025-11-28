"""
Base LLM Provider Interface

This module defines the abstract base class that all LLM providers must implement.
It provides a consistent interface for interacting with different LLM providers
(Gemini, OpenAI, Anthropic, etc.) throughout the application.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """Message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None  # Function name for function messages
    function_call: Optional[Dict[str, Any]] = None  # Function call details


@dataclass
class Tool:
    """Represents a tool/function that the LLM can call."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema


@dataclass
class FunctionCall:
    """Represents a function call made by the LLM."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""
    content: Optional[str] = None
    function_calls: List[FunctionCall] = None
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.function_calls is None:
            self.function_calls = []


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers (Gemini, OpenAI, Anthropic, etc.) must implement this interface
    to ensure consistent behavior across the application.
    """

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for the provider
            model_name: Optional model name override
        """
        self.api_key = api_key
        self.model_name = model_name or self.default_model

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g., 'gemini', 'openai', 'anthropic')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model name for this provider."""
        pass

    @property
    @abstractmethod
    def supports_tools(self) -> bool:
        """Return whether this provider supports function/tool calling."""
        pass

    @property
    @abstractmethod
    def supports_vision(self) -> bool:
        """Return whether this provider supports image inputs."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Return whether this provider supports streaming responses."""
        pass

    @abstractmethod
    async def generate_simple(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a simple text response from a prompt.

        This is the simplest interface for text generation, suitable for
        straightforward use cases without conversation history or tools.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            The generated text response

        Raises:
            Exception: If the API call fails
        """
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None
    ) -> LLMResponse:
        """
        Generate a response with full conversation support and optional tools.

        This is the main interface for complex interactions with conversation history
        and tool/function calling support.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            tools: Optional list of tools the LLM can call

        Returns:
            LLMResponse object containing the response and any function calls

        Raises:
            Exception: If the API call fails
        """
        pass

    @abstractmethod
    async def generate_with_image(
        self,
        prompt: str,
        image_path: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from a prompt and image (multimodal).

        Only available if supports_vision is True.

        Args:
            prompt: The input prompt
            image_path: Path to the image file
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            The generated text response

        Raises:
            NotImplementedError: If provider doesn't support vision
            Exception: If the API call fails
        """
        pass

    def validate_supports_tools(self):
        """Raise an error if provider doesn't support tools."""
        if not self.supports_tools:
            raise NotImplementedError(
                f"{self.provider_name} does not support function/tool calling"
            )

    def validate_supports_vision(self):
        """Raise an error if provider doesn't support vision."""
        if not self.supports_vision:
            raise NotImplementedError(
                f"{self.provider_name} does not support vision/multimodal inputs"
            )
