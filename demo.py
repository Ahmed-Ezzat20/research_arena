import gradio as gr
import arxiv
import google.generativeai as genai
import os
import logging
import json
from typing import Dict, Any
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
try:
    import pypdf
except ImportError:
    try:
        import PyPDF2 as pypdf
    except ImportError:
        pypdf = None

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create custom log handler that stores logs in memory
class LogBuffer:
    def __init__(self):
        self.buffer = []
        self.max_size = 1000  # Keep last 1000 log entries

    def add(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.buffer.append({
            "timestamp": timestamp,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })
        # Keep only the last max_size entries
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_logs(self, level_filter="ALL"):
        if level_filter == "ALL":
            return self.buffer
        return [log for log in self.buffer if log["level"] == level_filter]

    def clear(self):
        self.buffer = []

    def format_logs(self, level_filter="ALL"):
        logs = self.get_logs(level_filter)
        return "\n".join([
            f"[{log['timestamp']}] {log['level']:8} | {log['module']:20} | {log['message']}"
            for log in logs
        ])

# Global log buffer
log_buffer = LogBuffer()

class BufferHandler(logging.Handler):
    def emit(self, record):
        log_buffer.add(record)

# Configure logging
logger = logging.getLogger("LLM_Assistant")
logger.setLevel(logging.DEBUG)  # Capture all levels

# Add buffer handler
buffer_handler = BufferHandler()
buffer_handler.setLevel(logging.DEBUG)
logger.addHandler(buffer_handler)

# Add console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log level control (can be changed at runtime)
current_log_level = {"level": "INFO"}

def set_log_level(level: str):
    """Set the logging level dynamically."""
    levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    logger.setLevel(levels.get(level, logging.INFO))
    current_log_level["level"] = level
    logger.info(f"Log level changed to {level}")

# Load prompts from files
with open("Explainer_prompt.txt", "r", encoding="utf-8") as f:
    EXPLAINER_PROMPT = f.read()

with open("paper_to_post.txt", "r", encoding="utf-8") as f:
    POST_PROMPT = f.read()


def retrieve_related_papers(query: str) -> str:
    """Retrieve up to 5 recent arXiv papers matching the query."""
    logger.info(f"🔍 FUNCTION CALL: retrieve_related_papers(query='{query}')")
    try:
        # Use Gemini to refine and expand the search query for better results
        logger.debug("📤 LLM REQUEST: Query refinement")
        query_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        refine_prompt = f"""Given this research topic query: "{query}"

Create an optimized arXiv search query that will find the most relevant papers. Consider:
- Technical terms and synonyms
- Related concepts
- Common paper titles in this area

Provide ONLY the search query text, no explanation. Make it specific and focused.
For example, if user asks about "transformers", return something like: "transformer architecture attention mechanism deep learning"
"""
        logger.debug(f"  Prompt: {refine_prompt[:100]}...")
        refined_query = query_model.generate_content(refine_prompt).text.strip()
        logger.info(f"📥 LLM RESPONSE: Refined query = '{refined_query}'")

        # Search with refined query, sorted by relevance
        logger.debug(f"🔎 Searching arXiv with refined query: '{refined_query}'")
        client = arxiv.Client()
        search = arxiv.Search(
            query=refined_query,
            max_results=10,  # Get more results to filter
            sort_by=arxiv.SortCriterion.Relevance,  # Sort by relevance instead of date
        )

        # Get results and use Gemini to filter for relevance
        all_results = list(client.results(search))
        logger.info(f"📚 Found {len(all_results)} papers from arXiv")

        # Use Gemini to rank results by relevance to original query
        papers_for_ranking = "\n\n".join([
            f"Paper {i+1}:\nTitle: {r.title}\nAbstract: {r.summary[:200]}..."
            for i, r in enumerate(all_results)
        ])

        ranking_prompt = f"""Given the user's search query: "{query}"

Rank these papers by relevance (most relevant first). Return ONLY the paper numbers in order, comma-separated.
For example: "3,1,5,2,4"

{papers_for_ranking}

Return only the top 5 most relevant paper numbers:"""

        logger.debug("📤 LLM REQUEST: Ranking papers by relevance")
        ranking_response = query_model.generate_content(ranking_prompt).text.strip()
        logger.info(f"📥 LLM RESPONSE: Ranking = '{ranking_response}'")
        ranked_indices = [int(x.strip()) - 1 for x in ranking_response.split(",")[:5]]
        logger.debug(f"  Top 5 indices: {ranked_indices}")

        # Build final results
        results = []
        for idx, paper_idx in enumerate(ranked_indices, 1):
            if paper_idx < len(all_results):
                result = all_results[paper_idx]
                title = result.title.strip().replace("\n", " ")
                authors = ", ".join([author.name for author in result.authors[:3]])
                if len(result.authors) > 3:
                    authors += " et al."
                published = result.published.strftime("%Y-%m-%d")
                summary = result.summary.strip().replace("\n", " ")[:300] + "..." if len(result.summary) > 300 else result.summary.strip().replace("\n", " ")
                url = result.pdf_url

                paper_info = f"""Paper {idx}:
Title: {title}
Authors: {authors}
Published: {published}
Summary: {summary}
PDF: {url}"""
                results.append(paper_info)

        logger.info(f"✅ FUNCTION COMPLETE: Returning {len(results)} papers")
        return "\n\n" + "="*80 + "\n\n".join(results) if results else "No papers found."

    except Exception as e:
        logger.error(f"❌ ERROR in retrieve_related_papers: {str(e)}")
        logger.warning("⚠️  Falling back to basic arXiv search without LLM ranking")
        # Fallback to basic search if Gemini fails
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = []
        for idx, result in enumerate(client.results(search), 1):
            title = result.title.strip().replace("\n", " ")
            authors = ", ".join([author.name for author in result.authors[:3]])
            if len(result.authors) > 3:
                authors += " et al."
            published = result.published.strftime("%Y-%m-%d")
            summary = result.summary.strip().replace("\n", " ")[:300] + "..." if len(result.summary) > 300 else result.summary.strip().replace("\n", " ")
            url = result.pdf_url

            paper_info = f"""Paper {idx}:
Title: {title}
Authors: {authors}
Published: {published}
Summary: {summary}
PDF: {url}"""
            results.append(paper_info)

        return "\n\n" + "="*80 + "\n\n".join(results) if results else "No papers found."


def explain_research_paper(paper_info: str) -> str:
    """Explain a research paper using Gemini API."""
    logger.info(f"🔍 FUNCTION CALL: explain_research_paper(paper_info length={len(paper_info)} chars)")
    try:
        # Use Gemini to explain the paper without function calling
        logger.debug("📤 LLM REQUEST: Paper explanation")
        explain_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        prompt = f"{EXPLAINER_PROMPT}\n\nUser Input:\n{paper_info}"
        logger.debug(f"  Using EXPLAINER_PROMPT ({len(EXPLAINER_PROMPT)} chars) + paper info")
        response = explain_model.generate_content(prompt)
        logger.info(f"📥 LLM RESPONSE: Explanation generated ({len(response.text)} chars)")
        logger.debug(f"  Preview: {response.text[:150]}...")
        return response.text
    except Exception as e:
        logger.error(f"❌ ERROR in explain_research_paper: {str(e)}")
        return f"Error explaining paper: {str(e)}"


def write_social_media_post(explanation: str) -> str:
    """Create a social-media-friendly post using Gemini API."""
    logger.info(f"🔍 FUNCTION CALL: write_social_media_post(explanation length={len(explanation)} chars)")
    try:
        # Use Gemini to create an engaging social media post
        logger.debug("📤 LLM REQUEST: Social media post generation")
        post_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        prompt = f"{POST_PROMPT}\n{explanation}"
        logger.debug(f"  Using POST_PROMPT ({len(POST_PROMPT)} chars) + explanation")
        response = post_model.generate_content(prompt)
        logger.info(f"📥 LLM RESPONSE: Post generated ({len(response.text)} chars)")
        logger.debug(f"  Preview: {response.text[:150]}...")
        return response.text
    except Exception as e:
        logger.error(f"❌ ERROR in write_social_media_post: {str(e)}")
        return f"Error creating post: {str(e)}"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    logger.info(f"🔍 FUNCTION CALL: extract_text_from_pdf(pdf_path='{pdf_path}')")

    if pypdf is None:
        error_msg = "PDF support not available. Please install pypdf: pip install pypdf"
        logger.error(f"❌ {error_msg}")
        return error_msg

    try:
        logger.debug(f"📄 Opening PDF file: {pdf_path}")

        # Try pypdf first
        if hasattr(pypdf, 'PdfReader'):
            reader = pypdf.PdfReader(pdf_path)
            logger.info(f"📚 PDF loaded: {len(reader.pages)} pages")

            text_content = []
            for i, page in enumerate(reader.pages, 1):
                logger.debug(f"  Extracting text from page {i}/{len(reader.pages)}")
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {i} ---\n{text}")

            full_text = "\n\n".join(text_content)
            logger.info(f"✅ PDF text extracted: {len(full_text)} characters")
            return full_text

        # Fallback to PyPDF2 API
        elif hasattr(pypdf, 'PdfFileReader'):
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfFileReader(file)
                logger.info(f"📚 PDF loaded: {reader.numPages} pages")

                text_content = []
                for i in range(reader.numPages):
                    logger.debug(f"  Extracting text from page {i+1}/{reader.numPages}")
                    page = reader.getPage(i)
                    text = page.extractText()
                    if text.strip():
                        text_content.append(f"--- Page {i+1} ---\n{text}")

                full_text = "\n\n".join(text_content)
                logger.info(f"✅ PDF text extracted: {len(full_text)} characters")
                return full_text
        else:
            error_msg = "Unsupported pypdf version"
            logger.error(f"❌ {error_msg}")
            return error_msg

    except Exception as e:
        error_msg = f"Error extracting PDF text: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return error_msg


def process_uploaded_pdf(pdf_path: str) -> str:
    """Process an uploaded PDF and return a summary of its content."""
    logger.info(f"🔍 FUNCTION CALL: process_uploaded_pdf(pdf_path='{pdf_path}')")

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    if pdf_text.startswith("Error") or pdf_text.startswith("PDF support"):
        return pdf_text

    # Limit text length for LLM processing (first 10000 chars)
    if len(pdf_text) > 10000:
        logger.debug(f"  Truncating PDF text from {len(pdf_text)} to 10000 chars")
        pdf_text = pdf_text[:10000] + "\n\n[Text truncated for processing...]"

    try:
        logger.debug("📤 LLM REQUEST: PDF content analysis")
        pdf_model = genai.GenerativeModel(model_name="gemini-2.5-flash")

        prompt = f"""Analyze this research paper PDF and provide:

1. **Title and Authors** (if identifiable)
2. **Main Topic/Field**
3. **Key Contributions**
4. **Methodology Overview**
5. **Main Results/Findings**
6. **Conclusions**

PDF Content:
{pdf_text}

Provide a clear, structured summary in Arabic (MSA) or English, depending on what seems more appropriate."""

        response = pdf_model.generate_content(prompt)
        logger.info(f"📥 LLM RESPONSE: PDF analysis complete ({len(response.text)} chars)")
        logger.debug(f"  Preview: {response.text[:150]}...")

        return response.text

    except Exception as e:
        error_msg = f"Error analyzing PDF: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return error_msg


# Define tool functions for Gemini
tools = [
    {
        "function_declarations": [
            {
                "name": "retrieve_related_papers",
                "description": "Retrieve up to 5 recent arXiv papers matching the query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for arXiv papers",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "explain_research_paper",
                "description": "Explain a research paper in clear, non-technical language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paper_info": {
                            "type": "string",
                            "description": "The research paper information to explain",
                        }
                    },
                    "required": ["paper_info"],
                },
            },
            {
                "name": "write_social_media_post",
                "description": "Create a social-media-friendly post summarizing the paper",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "The explanation to convert into a social media post",
                        }
                    },
                    "required": ["explanation"],
                },
            },
            {
                "name": "process_uploaded_pdf",
                "description": "Process and analyze an uploaded PDF research paper",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_path": {
                            "type": "string",
                            "description": "The file path to the uploaded PDF",
                        }
                    },
                    "required": ["pdf_path"],
                },
            },
        ]
    }
]

# Map function names to actual functions
function_map = {
    "retrieve_related_papers": retrieve_related_papers,
    "explain_research_paper": explain_research_paper,
    "write_social_media_post": write_social_media_post,
    "process_uploaded_pdf": process_uploaded_pdf,
}

# Initialize Gemini model with tools
model = genai.GenerativeModel(model_name="gemini-2.5-flash", tools=tools)


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
        max_iterations = 10  # Prevent infinite loops

        while iteration < max_iterations:
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
                            if isinstance(value, str) and len(value) > 50000:
                                logger.warning(f"⚠️  Truncating {key} from {len(value)} to 50000 chars")
                                function_args[key] = value[:50000] + "\n\n[Truncated due to length...]"

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


# ============================================================================
# LOG VIEWER FUNCTIONS
# ============================================================================

def get_logs(level_filter):
    """Retrieve formatted logs from the buffer."""
    return log_buffer.format_logs(level_filter)

def clear_logs():
    """Clear the log buffer."""
    log_buffer.clear()
    logger.info("🗑️  Log buffer cleared")
    return "Logs cleared!"

def change_log_level(level):
    """Change the logging level."""
    set_log_level(level)
    return f"Log level set to {level}"

def refresh_logs(level_filter):
    """Refresh the log display."""
    return log_buffer.format_logs(level_filter)

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

# ============================================================================
# PDF UPLOAD HANDLER
# ============================================================================

# Global variable to store uploaded PDF path
uploaded_pdf_path = {"path": None}

def handle_pdf_upload(pdf_file):
    """Handle PDF file upload and store the path."""
    if pdf_file is None:
        return "No file uploaded.", ""

    logger.info(f"📄 PDF uploaded: {pdf_file.name}")
    uploaded_pdf_path["path"] = pdf_file.name

    # Extract and preview text
    preview_text = extract_text_from_pdf(pdf_file.name)

    if preview_text.startswith("Error") or preview_text.startswith("PDF support"):
        return preview_text, ""

    # Show preview (first 500 chars)
    preview = preview_text[:500] + "..." if len(preview_text) > 500 else preview_text

    return f"✅ PDF uploaded successfully!\n\n**Preview:**\n{preview}", pdf_file.name

def analyze_uploaded_pdf(pdf_path):
    """Analyze the uploaded PDF."""
    if not pdf_path:
        return "Please upload a PDF file first."

    logger.info(f"🔍 Analyzing uploaded PDF: {pdf_path}")
    result = process_uploaded_pdf(pdf_path)
    return result

with gr.Blocks(title="Agentic Research Assistant with Logging") as demo:
    gr.Markdown("# 🤖 Agentic Research Assistant")
    gr.Markdown("AI-powered research assistant using Gemini API with **comprehensive LLM thinking process logging**")

    with gr.Tabs():
        # Chat Tab
        with gr.Tab("💬 Chat"):
            gr.Markdown("""
            ### 💬 Multimodal Research Assistant
            Upload PDFs, images, or any files directly in the chat! The AI can:
            - 📄 Read and analyze PDF research papers
            - 🖼️ Analyze images and figures
            - 🔍 Search for papers on arXiv
            - 📝 Explain research in simple terms
            - 📱 Create social media posts
            """)
            gr.ChatInterface(
                fn=chat,
                title="Research Assistant Chat",
                description="Type a message or attach files (PDFs, images, etc.). The AI will analyze them directly!",
                multimodal=True,
            )

        # PDF Upload Tab
        with gr.Tab("📄 Upload PDF"):
            gr.Markdown("### Upload and Analyze Research Papers")
            gr.Markdown("Upload a PDF file of a research paper and get an AI-powered analysis, explanation, or social media post.")

            with gr.Row():
                with gr.Column():
                    pdf_upload = gr.File(
                        label="📎 Upload PDF File",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    upload_status = gr.Textbox(
                        label="Status",
                        lines=10,
                        interactive=False
                    )

                with gr.Column():
                    pdf_path_store = gr.Textbox(
                        label="Uploaded PDF Path",
                        visible=False
                    )
                    analyze_btn = gr.Button("🔍 Analyze PDF", variant="primary", size="lg")
                    explain_btn = gr.Button("📝 Get Detailed Explanation", variant="secondary")
                    post_btn = gr.Button("📱 Create Social Media Post", variant="secondary")

            pdf_output = gr.Textbox(
                label="📋 Analysis Result",
                lines=20,
                interactive=False
            )

            # Event handlers
            pdf_upload.change(
                fn=handle_pdf_upload,
                inputs=[pdf_upload],
                outputs=[upload_status, pdf_path_store]
            )

            analyze_btn.click(
                fn=analyze_uploaded_pdf,
                inputs=[pdf_path_store],
                outputs=[pdf_output]
            )

            def explain_pdf(pdf_path):
                if not pdf_path:
                    return "Please upload a PDF file first."
                text = extract_text_from_pdf(pdf_path)
                if len(text) > 8000:
                    text = text[:8000] + "\n\n[Text truncated...]"
                return explain_research_paper(text)

            def post_from_pdf(pdf_path):
                if not pdf_path:
                    return "Please upload a PDF file first."
                analysis = analyze_uploaded_pdf(pdf_path)
                return write_social_media_post(analysis)

            explain_btn.click(
                fn=explain_pdf,
                inputs=[pdf_path_store],
                outputs=[pdf_output]
            )

            post_btn.click(
                fn=post_from_pdf,
                inputs=[pdf_path_store],
                outputs=[pdf_output]
            )

        # Logs Tab
        with gr.Tab("📊 LLM Thinking Process Logs"):
            gr.Markdown("### View the LLM's Thinking Process")
            gr.Markdown("See detailed logs of all LLM API calls, tool executions, and the agentic decision-making process. Click 'Refresh Logs' to update.")

            with gr.Row():
                with gr.Column(scale=3):
                    log_level_dropdown = gr.Dropdown(
                        choices=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
                        value="INFO",
                        label="🎚️ Log Level Filter",
                        info="Filter logs by severity level"
                    )
                with gr.Column(scale=1):
                    refresh_btn = gr.Button("🔄 Refresh Logs", variant="secondary")
                    clear_btn = gr.Button("🗑️ Clear Logs", variant="stop")

            log_output = gr.Textbox(
                label="📋 Log Output",
                lines=25,
                max_lines=50,
                value=log_buffer.format_logs("INFO"),
                interactive=False
            )

            status_text = gr.Textbox(label="Status", visible=False)

            # Event handlers
            refresh_btn.click(
                fn=refresh_logs,
                inputs=[log_level_dropdown],
                outputs=[log_output]
            )

            clear_btn.click(
                fn=clear_logs,
                outputs=[status_text]
            ).then(
                fn=refresh_logs,
                inputs=[log_level_dropdown],
                outputs=[log_output]
            )

            log_level_dropdown.change(
                fn=refresh_logs,
                inputs=[log_level_dropdown],
                outputs=[log_output]
            )

        # Settings Tab
        with gr.Tab("⚙️ Settings"):
            gr.Markdown("### Logging Configuration")
            gr.Markdown("Control the verbosity of logging for the LLM system.")

            with gr.Row():
                log_level_radio = gr.Radio(
                    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                    value="INFO",
                    label="🎚️ Global Log Level",
                    info="DEBUG = All details | INFO = Key events | WARNING = Issues only | ERROR = Errors only"
                )

            change_level_btn = gr.Button("💾 Apply Log Level", variant="primary")
            level_status = gr.Textbox(label="Status", interactive=False)

            change_level_btn.click(
                fn=change_log_level,
                inputs=[log_level_radio],
                outputs=[level_status]
            )

            gr.Markdown("---")
            gr.Markdown("### Log Legend")
            gr.Markdown("""
            **Emoji Guide:**
            - 💬 User message received
            - 📤 LLM request sent
            - 📥 LLM response received
            - 🛠️ Tool call requested by LLM
            - ⚙️ Tool executing
            - ✅ Operation completed successfully
            - 🔄 Agentic loop iteration
            - 💭 Final response generation
            - ❌ Error occurred
            - ⚠️ Warning or fallback
            - 🔍 Function called
            - 📚 Data retrieved
            """)

    # Register API endpoints
    gr.api(retrieve_related_papers, api_name="retrieve_papers")
    gr.api(explain_research_paper, api_name="explain_paper")
    gr.api(write_social_media_post, api_name="write_social_post")
    gr.api(process_uploaded_pdf, api_name="process_pdf")

logger.info("🚀 Starting Agentic Research Assistant with Logging...")
demo.launch(mcp_server=True, share=True)
