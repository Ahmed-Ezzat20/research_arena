"""
Unified Chat Interface - Refactored with async and provider abstraction
Agentic loop with tool calling and multimodal support.
"""

import json
import asyncio
import google.generativeai as genai
from typing import Dict, Any, List
from src.config import MAX_ITERATIONS, MAX_FUNCTION_ARG_LENGTH
from src.logging import logger
from src.providers.gemini import GeminiProvider
from src.providers.base import Message, MessageRole, Tool, FunctionCall
from src.utils import get_async_function_map, get_tool_schemas


async def chat(message: Any, history: List) -> str:
    """
    Agentic chat function with tool calling and file support.
    
    Args:
        message: User message (string or dict with text and files)
        history: Chat history (currently unused, but kept for Gradio compatibility)
        
    Returns:
        str: Assistant's response
    """
    # Handle both string messages and multimodal messages with files
    if isinstance(message, dict):
        user_message = message.get("text", "")
        files = message.get("files", [])
    else:
        user_message = message
        files = []
    
    logger.info("="*80)
    logger.info(f"💬 NEW CHAT MESSAGE: '{user_message}'")
    if files:
        logger.info(f"📎 FILES ATTACHED: {len(files)} file(s)")
        for file in files:
            logger.info(f"  - {file}")
    logger.info("="*80)
    
    try:
        # Initialize provider
        import os
        from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
        provider = GeminiProvider(api_key=GEMINI_API_KEY, model_name=GEMINI_MODEL_NAME)
        
        # Get async function map and tool schemas
        function_map = get_async_function_map(provider)
        tool_schemas = get_tool_schemas()
        
        # Prepare the message content
        message_parts = []
        
        # Add uploaded files (PDFs, images, etc.) to the message
        if files:
            for file_path in files:
                logger.debug(f"📎 Processing file: {file_path}")
                try:
                    # Upload file to Gemini
                    uploaded_file = genai.upload_file(file_path)
                    logger.info(f"✅ File uploaded to Gemini: {uploaded_file.name}")
                    message_parts.append(uploaded_file)
                except Exception as e:
                    logger.error(f"❌ Error uploading file {file_path}: {str(e)}")
                    return f"Error uploading file: {str(e)}"
        
        # Add the text message
        if user_message:
            message_parts.append(user_message)
        
        # If no message parts, return error
        if not message_parts:
            return "Please provide a message or upload a file."
        
        # For multimodal messages with files, use Gemini's native API
        # (Provider abstraction doesn't support file uploads yet)
        if files:
            return await _handle_multimodal_message(message_parts, function_map, tool_schemas)
        
        # For text-only messages, use provider abstraction
        return await _handle_text_message(user_message, provider, function_map, tool_schemas)
    
    except Exception as e:
        logger.error(f"❌ ERROR in chat function: {str(e)}")
        logger.info("="*80)
        return f"Error: {str(e)}"


async def _handle_multimodal_message(
    message_parts: List,
    function_map: Dict,
    tool_schemas: List[Dict]
) -> str:
    """Handle messages with file attachments using Gemini's native API."""
    from src.models import get_model_with_tools
    from src.utils import tools
    
    # Initialize model with tools
    model = get_model_with_tools(tools)
    
    # Start a chat session
    logger.debug("🔧 Starting new chat session (multimodal)")
    chat_session = model.start_chat(history=[])
    
    # Send the message (with files)
    logger.debug("📤 LLM REQUEST: Sending multimodal message to Gemini")
    
    # Run synchronous API call in executor
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: chat_session.send_message(message_parts)
    )
    logger.debug("📥 LLM RESPONSE: Received response from Gemini")
    
    # Handle tool calls in a loop
    iteration = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        logger.debug(f"🔄 AGENTIC LOOP: Iteration {iteration}")
        
        # Check if response is valid
        if not response.candidates or not response.candidates[0].content.parts:
            logger.debug("⚠️  No candidates or parts in response")
            break
        
        # Check for finish reason issues
        candidate = response.candidates[0]
        if hasattr(candidate, 'finish_reason'):
            finish_reason = str(candidate.finish_reason)
            if 'MALFORMED' in finish_reason:
                logger.warning(f"⚠️  Malformed function call detected: {finish_reason}")
                # Try to extract any text response that might exist
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            logger.info(f"💭 Recovered partial response ({len(part.text)} chars)")
                            return part.text
                return "I encountered an issue processing the function call. Please try rephrasing your request."
        
        part = candidate.content.parts[0]
        
        # Check if there's a function call
        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            
            try:
                function_args = dict(function_call.args)
            except Exception as e:
                logger.error(f"❌ ERROR parsing function arguments: {str(e)}")
                return "I encountered an issue with the function call format. Please try again."
            
            logger.info(f"🛠️  TOOL CALL REQUESTED: {function_name}")
            logger.debug(f"  Arguments: {json.dumps(function_args, ensure_ascii=False)[:200]}")
            
            # Execute the function
            if function_name in function_map:
                try:
                    # Truncate very long arguments to prevent issues
                    for key, value in function_args.items():
                        if isinstance(value, str) and len(value) > MAX_FUNCTION_ARG_LENGTH:
                            logger.warning(f"⚠️  Truncating {key} from {len(value)} to {MAX_FUNCTION_ARG_LENGTH} chars")
                            function_args[key] = value[:MAX_FUNCTION_ARG_LENGTH] + "\n\n[Truncated due to length...]"
                    
                    logger.info(f"⚙️  EXECUTING TOOL: {function_name}")
                    result = await function_map[function_name](**function_args)
                    result_preview = result[:150] if len(result) > 150 else result
                    logger.info(f"✅ TOOL EXECUTION COMPLETE: {function_name}")
                    logger.debug(f"  Result preview: {result_preview}...")
                    
                    # Send function response back to model
                    logger.debug("📤 LLM REQUEST: Sending tool result back to Gemini")
                    response = await loop.run_in_executor(
                        None,
                        lambda: chat_session.send_message({
                            "function_response": {
                                "name": function_name,
                                "response": {"result": result},
                            }
                        })
                    )
                    logger.debug("📥 LLM RESPONSE: Received response after tool execution")
                except Exception as e:
                    logger.error(f"❌ ERROR executing function: {str(e)}")
                    return f"Error executing {function_name}: {str(e)}"
            else:
                logger.error(f"❌ ERROR: Unknown function '{function_name}'")
                return f"Unknown function: {function_name}"
        
        # Check if there's text response
        elif hasattr(part, "text") and part.text:
            logger.info(f"💭 FINAL RESPONSE: Generated text response ({len(part.text)} chars)")
            logger.debug(f"  Preview: {part.text[:200]}...")
            logger.info("="*80)
            return part.text
        else:
            logger.debug("⚠️  No more parts to process, breaking loop")
            break
    
    # If we exit the loop without returning, get the final text
    if response.text:
        logger.info(f"💭 FINAL RESPONSE: Generated text response ({len(response.text)} chars)")
        logger.info("="*80)
        return response.text
    else:
        logger.warning("⚠️  No response text generated")
        logger.info("="*80)
        return "I processed your request but didn't generate a response."


async def _handle_text_message(
    user_message: str,
    provider: GeminiProvider,
    function_map: Dict,
    tool_schemas: List[Dict]
) -> str:
    """Handle text-only messages using provider abstraction."""
    # Convert tool schemas to Tool objects
    tools = []
    for schema in tool_schemas:
        tools.append(Tool(
            name=schema["name"],
            description=schema["description"],
            parameters=schema["input_schema"]
        ))
    
    # Create initial message
    messages = [Message(role=MessageRole.USER, content=user_message)]
    
    # Agentic loop
    iteration = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        logger.debug(f"🔄 AGENTIC LOOP: Iteration {iteration}")
        
        # Generate response with tools
        logger.debug("📤 LLM REQUEST: Sending message to provider")
        response = await provider.generate(
            messages=messages,
            temperature=0.7,
            tools=tools
        )
        logger.debug("📥 LLM RESPONSE: Received response from provider")
        
        # Check if there are function calls
        if response.function_calls:
            for func_call in response.function_calls:
                function_name = func_call.name
                function_args = func_call.arguments
                
                logger.info(f"🛠️  TOOL CALL REQUESTED: {function_name}")
                logger.debug(f"  Arguments: {json.dumps(function_args, ensure_ascii=False)[:200]}")
                
                # Execute the function
                if function_name in function_map:
                    try:
                        # Truncate very long arguments
                        for key, value in function_args.items():
                            if isinstance(value, str) and len(value) > MAX_FUNCTION_ARG_LENGTH:
                                logger.warning(f"⚠️  Truncating {key} from {len(value)} to {MAX_FUNCTION_ARG_LENGTH} chars")
                                function_args[key] = value[:MAX_FUNCTION_ARG_LENGTH] + "\n\n[Truncated due to length...]"
                        
                        logger.info(f"⚙️  EXECUTING TOOL: {function_name}")
                        result = await function_map[function_name](**function_args)
                        result_preview = result[:150] if len(result) > 150 else result
                        logger.info(f"✅ TOOL EXECUTION COMPLETE: {function_name}")
                        logger.debug(f"  Result preview: {result_preview}...")
                        
                        # Add function result to messages
                        messages.append(Message(
                            role=MessageRole.FUNCTION,
                            content=result,
                            name=function_name
                        ))
                    except Exception as e:
                        logger.error(f"❌ ERROR executing function: {str(e)}")
                        return f"Error executing {function_name}: {str(e)}"
                else:
                    logger.error(f"❌ ERROR: Unknown function '{function_name}'")
                    return f"Unknown function: {function_name}"
        
        # Check if there's text response
        elif response.content:
            logger.info(f"💭 FINAL RESPONSE: Generated text response ({len(response.content)} chars)")
            logger.debug(f"  Preview: {response.content[:200]}...")
            logger.info("="*80)
            return response.content
        else:
            logger.debug("⚠️  No content or function calls, breaking loop")
            break
    
    logger.warning("⚠️  Max iterations reached or no response generated")
    logger.info("="*80)
    return "I processed your request but didn't generate a response."
