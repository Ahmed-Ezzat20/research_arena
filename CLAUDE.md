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
- Multiple tabs: Chat, PDF Upload, Generate Infographic, Logs, and Settings

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

**2. Tool/Function System**
The assistant has 5 registered tools that Gemini can call:

- `retrieve_related_papers(query)` - Searches arXiv with LLM-refined queries and LLM-ranked results
- `explain_research_paper(paper_info)` - Explains papers using the explainer prompt
- `write_social_media_post(explanation)` - Creates LinkedIn posts using the post prompt
- `process_uploaded_pdf(pdf_path)` - Analyzes uploaded PDFs
- `generate_paper_infographic(paper_info)` - **NEW!** Generates visual infographics from paper summaries

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

**infographic_prompt.txt** ✨ **NEW!**
- Guides infographic design with professional layout principles
- Defines visual hierarchy, color psychology, and iconography
- Specifies modern, academic-yet-accessible aesthetic
- Optimized for social media and presentation formats

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

**Infographic Generation Fallbacks** ✨ **NEW!**
If image generation model is unavailable:
- Returns structured summary with all key sections
- Provides suggestions for external design tools (Canva, Adobe Express, etc.)
- Logs detailed error information for debugging
- Graceful degradation ensures users still get valuable content

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

**Tab 3: Generate Infographic** ✨ **NEW!**
- Two input methods:
  - **From Text**: Paste paper summary or full text directly
  - **From PDF**: Use uploaded PDF from Tab 2
- Real-time image generation with status updates
- Inline preview of generated infographics
- Download button for saving images
- Automated saving to `generated_infographics/` folder

**Tab 4: LLM Thinking Process Logs**
- Real-time log viewer with level filtering
- Manual refresh button (no auto-refresh due to Gradio version compatibility)
- Displays formatted logs from `LogBuffer`

**Tab 5: Settings**
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

The application registers 5 API endpoints accessible via MCP:
- `retrieve_papers`
- `explain_paper`
- `write_social_post`
- `process_pdf`
- `generate_infographic` ✨ **NEW!**

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
- 🎨 Infographic generation (NEW!)
- 📊 Structured summary (NEW!)
- 🖼️ Image generation (NEW!)

## Modifying Prompts

To change AI behavior:

1. **For paper explanations**: Edit `prompts/Explainer_prompt.txt`
   - Changes language, structure, or detail level of explanations
   - Reloaded on each function call (no restart needed)

2. **For social media posts**: Edit `prompts/paper_to_post.txt`
   - Changes tone, length, or format of generated posts
   - Reloaded on each function call (no restart needed)

3. **For infographic design** ✨ **NEW!**: Edit `prompts/infographic_prompt.txt`
   - Customizes visual style, layout, and design principles
   - Adjusts section structure and content organization
   - Modifies target audience and presentation format
   - Reloaded on each function call (no restart needed)

## Common Gotchas

1. **Long text in function arguments**: Automatically truncated at 50,000 chars to prevent malformed calls

2. **PDF text extraction**: If pypdf/PyPDF2 not installed, users get clear error with installation instructions

3. **Gradio version compatibility**: The code avoids newer Gradio features like `theme`, `show_copy_button`, and `every` parameter

4. **Agentic loops**: Limited to 10 iterations to prevent infinite loops from malformed responses

5. **Large PDFs**: First 10,000 characters used for processing to stay within token limits

6. **Infographic generation model availability** ✨ **NEW!**: Image generation requires Gemini 2.0 or later with image generation capabilities. If unavailable, the system provides a structured summary that can be used with external design tools (Canva, Adobe Express, etc.)

7. **Generated infographics storage**: Images are saved to `generated_infographics/` folder with timestamped filenames. The folder is in `.gitignore` to avoid repository bloat.

## Development Notes

### Adding New Tools/Functions

Follow this pattern (see `src/tools/infographic_generator.py` as reference):

1. **Create tool module**: Define function in `src/tools/your_tool.py`
   - Add comprehensive logging with emoji indicators
   - Include error handling and fallbacks
   - Load any required prompts from `prompts/` directory

2. **Update tool registry**: Edit `src/utils/tool_registry.py`
   - Add tool declaration with proper schema
   - Add function to `function_map` dictionary

3. **Update imports**:
   - Add to `src/tools/__init__.py`
   - Import in `src/main.py`

4. **Create UI handler** (optional): Add module to `src/ui/`
   - Create user-facing functions
   - Add to `src/ui/__init__.py`

5. **Add to main UI**: Update `src/main.py`
   - Add tab or interface elements
   - Wire up event handlers
   - Register API endpoint with `gr.api()` for MCP access

6. **Update documentation**:
   - Add to `CLAUDE.md` with implementation details
   - Update `README.md` with user-facing information
   - Add relevant emojis to logging legend
