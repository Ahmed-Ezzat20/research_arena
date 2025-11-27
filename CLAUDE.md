# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agentic Research Assistant** built with Google Gemini API and Gradio. It provides an AI-powered interface for finding, explaining, and sharing scientific research papers with comprehensive LLM logging capabilities.

## Running the Application

```bash
# Start the application
python demo.py
```

The application launches a Gradio web interface with:
- Public sharing enabled (`share=True`)
- MCP server enabled for external tool access
- Multiple tabs: Chat, PDF Upload, Logs, and Settings

## Environment Setup

### Required Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

### Dependencies

Install required packages:

```bash
pip install gradio google-generativeai arxiv python-dotenv pypdf
```

## Architecture

### Core Components

**1. LLM Integration (`demo.py:1-100`)**
- Uses **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) as the primary model
- Configured with function calling (tools) for agentic behavior
- All LLM interactions logged with emoji-based visual indicators

**2. Tool/Function System (`demo.py:350-420`)**
The assistant has 4 registered tools that Gemini can call:

- `retrieve_related_papers(query)` - Searches arXiv with LLM-refined queries and LLM-ranked results
- `explain_research_paper(paper_info)` - Explains papers using the explainer prompt
- `write_social_media_post(explanation)` - Creates LinkedIn posts using the post prompt
- `process_uploaded_pdf(pdf_path)` - Analyzes uploaded PDFs

**3. Multimodal Chat (`demo.py:426-570`)**
- Handles both text and file uploads (PDFs, images)
- Files uploaded directly to Gemini API using `genai.upload_file()`
- Agentic loop handles tool calls with malformed call detection and recovery
- Max 10 iterations with argument truncation (50,000 char limit) to prevent API issues

**4. Logging System (`demo.py:18-86`)**
- Custom `LogBuffer` class stores last 1000 log entries in memory
- Dual output: console (INFO level) and buffer (DEBUG level)
- Structured format: `[timestamp] LEVEL | module | message`
- Log levels: DEBUG, INFO, WARNING, ERROR

### Prompt Files

**Explainer_prompt.txt**
- Generates 500-600 word summaries in Modern Standard Arabic (MSA)
- Keeps technical terms in English
- Includes pros/cons tables and related topics list

**paper_to_post.txt**
- Creates 200-300 word LinkedIn posts in Arabic with Egyptian dialect
- Multi-step generation with self-asking and self-reflection
- Includes evaluation table of iterative improvements

### Error Handling Patterns

**Malformed Function Calls (`demo.py:491-503`)**
When Gemini creates malformed function calls:
1. Detect via `finish_reason: MALFORMED_FUNCTION_CALL`
2. Attempt to extract partial text response
3. Return user-friendly error message
4. Log warning for debugging

**PDF Processing Fallbacks**
- Primary: `pypdf` library
- Fallback: `PyPDF2` API compatibility
- Text extraction limited to 10,000 chars for LLM processing

**arXiv Search Fallbacks**
If LLM-based refinement/ranking fails:
- Falls back to basic arXiv search
- Uses relevance sorting without LLM assistance
- Returns up to 5 papers

## Gradio Interface Structure

**Tab 1: Chat (Multimodal)**
- `gr.ChatInterface` with `multimodal=True`
- Accepts text messages and file uploads
- Files sent directly to Gemini's native multimodal API

**Tab 2: PDF Upload**
- Dedicated upload interface with 3 actions:
  - Analyze PDF (structured summary)
  - Get Detailed Explanation (uses explainer prompt)
  - Create Social Media Post (uses post prompt)

**Tab 3: LLM Thinking Process Logs**
- Real-time log viewer with level filtering
- Manual refresh button (no auto-refresh due to Gradio version compatibility)
- Displays formatted logs from `LogBuffer`

**Tab 4: Settings**
- Dynamic log level control (DEBUG/INFO/WARNING/ERROR)
- Emoji legend for log interpretation

## Important Implementation Details

### Gemini Function Calling Flow

1. User sends message (optionally with files)
2. Gemini analyzes and either:
   - Returns text directly, OR
   - Calls one or more tools
3. For tool calls:
   - Extract function name and arguments
   - Execute Python function
   - Send result back to Gemini as `function_response`
4. Repeat until Gemini returns final text response
5. All steps logged with specific emoji indicators

### MCP Server Integration

The application registers 4 API endpoints accessible via MCP:
- `retrieve_papers`
- `explain_paper`
- `write_social_post`
- `process_pdf`

These allow external tools (like Claude Desktop) to call the functions directly.

### Logging Emoji Convention

- 💬 User message received
- 📤 LLM request sent
- 📥 LLM response received
- 🛠️ Tool call requested by LLM
- ⚙️ Tool executing
- ✅ Operation completed
- 🔄 Agentic loop iteration
- 💭 Final response generation
- ❌ Error occurred
- ⚠️ Warning/fallback
- 🔍 Function called
- 📚 Data retrieved
- 📎 File attached/uploaded

## Modifying Prompts

To change AI behavior:

1. **For paper explanations**: Edit `Explainer_prompt.txt`
   - Changes language, structure, or detail level of explanations
   - Reloaded on each function call (no restart needed)

2. **For social media posts**: Edit `paper_to_post.txt`
   - Changes tone, length, or format of generated posts
   - Reloaded on each function call (no restart needed)

## Common Gotchas

1. **Long text in function arguments**: Automatically truncated at 50,000 chars to prevent malformed calls

2. **PDF text extraction**: If pypdf/PyPDF2 not installed, users get clear error with installation instructions

3. **Gradio version compatibility**: The code avoids newer Gradio features like `theme`, `show_copy_button`, and `every` parameter

4. **Agentic loops**: Limited to 10 iterations to prevent infinite loops from malformed responses

5. **Large PDFs**: First 10,000 characters used for processing to stay within token limits

## Development Notes

When adding new tools/functions:

1. Define the function in `demo.py`
2. Add tool declaration to `tools` list with proper schema
3. Add function to `function_map` dictionary
4. Register API endpoint with `gr.api()` if needed for MCP access
5. Add logging statements following emoji convention
