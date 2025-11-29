"""
Gemini LLM Provider Implementation

This module implements the BaseLLMProvider interface for Google's Gemini API.
Supports all Gemini capabilities including function calling and multimodal inputs.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from .base import (
    BaseLLMProvider,
    Message,
    MessageRole,
    Tool,
    FunctionCall,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider implementation.

    Supports:
    - Text generation
    - Function/tool calling
    - Vision/multimodal inputs
    - Streaming (future)
    """

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash-exp"

    @property
    def supports_tools(self) -> bool:
        return True

    @property
    def supports_vision(self) -> bool:
        return True

    @property
    def supports_streaming(self) -> bool:
        return True

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """Initialize Gemini provider and configure API."""
        super().__init__(api_key, model_name)
        genai.configure(api_key=self.api_key)
        logger.info(f"🔧 Initialized Gemini provider with model: {self.model_name}")

    def _convert_message_to_gemini_format(self, message: Message) -> Dict[str, Any]:
        """Convert our Message format to Gemini's format."""
        # Gemini uses 'user' and 'model' roles (not 'assistant')
        role = "model" if message.role == MessageRole.ASSISTANT else "user"

        gemini_message = {
            "role": role,
            "parts": [{"text": message.content}]
        }

        # Add function response if present
        if message.role == MessageRole.FUNCTION and message.function_call:
            gemini_message["parts"] = [{
                "function_response": {
                    "name": message.name,
                    "response": {"result": message.content}
                }
            }]

        return gemini_message

    def _convert_tools_to_gemini_format(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """Convert our Tool format to Gemini's function declarations format."""
        return [{
            "function_declarations": [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            } for tool in tools]
        }]

    def _extract_function_calls(self, response) -> List[FunctionCall]:
        """Extract function calls from Gemini response."""
        function_calls = []

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        # Convert Gemini's function call to our format
                        args = dict(fc.args) if hasattr(fc.args, 'items') else {}
                        function_calls.append(FunctionCall(
                            name=fc.name,
                            arguments=args
                        ))

        return function_calls

    async def generate_simple(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a simple text response from a prompt."""
        logger.debug(f"📤 Gemini simple generation request: {prompt[:100]}...")

        try:
            # Create model without tools
            model = genai.GenerativeModel(model_name=self.model_name)

            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            )

            result = response.text
            logger.debug(f"📥 Gemini response: {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None
    ) -> LLMResponse:
        """Generate a response with conversation history and optional tools."""
        logger.debug(f"📤 Gemini generation request with {len(messages)} messages")

        try:
            # Convert messages to Gemini format
            gemini_messages = [
                self._convert_message_to_gemini_format(msg)
                for msg in messages
            ]

            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # Create model with or without tools
            if tools:
                gemini_tools = self._convert_tools_to_gemini_format(tools)
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    tools=gemini_tools
                )
            else:
                model = genai.GenerativeModel(model_name=self.model_name)

            # Start chat with history (all but last message)
            chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

            # Send last message
            last_message_content = messages[-1].content

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: chat.send_message(
                    last_message_content,
                    generation_config=generation_config
                )
            )

            # Extract function calls if present
            function_calls = self._extract_function_calls(response)

            # Extract text content
            content = None
            # Only try to get text if there are no function calls
            if not function_calls:
                if hasattr(response, 'text'):
                    try:
                        content = response.text
                    except Exception as e:
                        # Response might not have text if it's a function call
                        logger.debug(f"Could not extract text from response: {e}")
                        pass
            else:
                # If there are function calls, don't try to extract text
                logger.debug("Response contains function calls, skipping text extraction")

            # Get finish reason
            finish_reason = "stop"
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)

            # Get usage info if available
            usage = None
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }

            logger.debug(f"📥 Gemini response - content: {content[:100] if content else 'None'}..., function_calls: {len(function_calls)}")

            return LLMResponse(
                content=content,
                function_calls=function_calls,
                finish_reason=finish_reason,
                usage=usage
            )

        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise

    async def generate_with_image(
        self,
        prompt: str,
        image_path: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from a prompt and image."""
        self.validate_supports_vision()
        logger.debug(f"📤 Gemini multimodal generation request: {prompt[:100]}... with image: {image_path}")

        try:
            # Create model
            model = genai.GenerativeModel(model_name=self.model_name)

            # Upload image file
            loop = asyncio.get_event_loop()
            uploaded_file = await loop.run_in_executor(
                None,
                lambda: genai.upload_file(image_path)
            )

            logger.debug(f"📎 Uploaded file: {uploaded_file.name}")

            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # Generate content with image
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    [prompt, uploaded_file],
                    generation_config=generation_config
                )
            )

            result = response.text
            logger.debug(f"📥 Gemini multimodal response: {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"❌ Gemini multimodal generation failed: {e}")
            raise
