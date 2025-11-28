"""
Chat interface with agentic loop for tool calling and multimodal support.
"""

import json
import google.generativeai as genai
from src.config import MAX_ITERATIONS, MAX_FUNCTION_ARG_LENGTH
from src.logging import logger
from src.models import get_model_with_tools
from src.utils import tools, function_map


def chat(message, history):
    """Agentic chat function using Gemini API with tool calling and file support."""
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
        # Initialize model with tools
        model = get_model_with_tools(tools)

        # Start a chat session
        logger.debug("🔧 Starting new chat session")
        chat_session = model.start_chat(history=[])

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

        # Send the message (with files if any)
        logger.debug("📤 LLM REQUEST: Sending message to Gemini")
        response = chat_session.send_message(message_parts)
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
                        result = function_map[function_name](**function_args)
                        result_preview = result[:150] if len(result) > 150 else result
                        logger.info(f"✅ TOOL EXECUTION COMPLETE: {function_name}")
                        logger.debug(f"  Result preview: {result_preview}...")

                        # Send function response back to model
                        logger.debug("📤 LLM REQUEST: Sending tool result back to Gemini")
                        response = chat_session.send_message(
                            {
                                "function_response": {
                                    "name": function_name,
                                    "response": {"result": result},
                                }
                            }
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

    except Exception as e:
        logger.error(f"❌ ERROR in chat function: {str(e)}")
        logger.info("="*80)
        return f"Error: {str(e)}"
