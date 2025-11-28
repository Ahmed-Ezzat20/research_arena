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
The assistant has 7 registered tools that Gemini can call:

- `retrieve_related_papers(query)` - Searches arXiv with LLM-refined queries and LLM-ranked results
- `explain_research_paper(paper_info)` - Explains papers using the explainer prompt
- `write_social_media_post(explanation)` - Creates LinkedIn posts using the post prompt
- `process_uploaded_pdf(pdf_path)` - Analyzes uploaded PDFs
- `generate_paper_infographic(paper_info)` - Generates visual infographics from paper summaries
- `verify_document_sources(document_text, verify_claims, verify_references)` - Advanced source verification with reference validation and claim fact-checking
- `recommend_similar_papers(paper_info, num_recommendations)` - **NEW!** Finds contextually similar papers using Semantic Scholar's recommendation engine

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

**infographic_prompt.txt**
- Guides infographic design with professional layout principles
- Defines visual hierarchy, color psychology, and iconography
- Specifies modern, academic-yet-accessible aesthetic
- Optimized for social media and presentation formats

**claim_extraction_prompt.txt** ✨ **NEW!**
- Instructs LLM to extract verifiable scientific claims
- Focuses on empirical, comparative, causal, statistical, and novel claims
- Provides classification guidelines (type, importance, specificity)
- Excludes background information and vague statements

**claim_verification_prompt.txt** ✨ **NEW!**
- Guides rigorous fact-checking of scientific claims
- Defines verification statuses (SUPPORTED, CONTRADICTED, NO CONSENSUS, etc.)
- Specifies confidence scoring methodology (0-100%)
- Emphasizes skepticism and scientific rigor

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

**Tab 3: Generate Infographic**
- Two input methods:
  - **From Text**: Paste paper summary or full text directly
  - **From PDF**: Use uploaded PDF from Tab 2
- Real-time image generation with status updates
- Inline preview of generated infographics
- Download button for saving images
- Automated saving to `generated_infographics/` folder

**Tab 4: Verify Sources**
- Advanced source verification with two sub-tabs:
  - **From Text**: Paste document text directly
  - **From PDF**: Use uploaded PDF from Tab 2
- Configurable verification options (checkboxes):
  - Verify References & Citations
  - Verify Claims
- Comprehensive verification report showing:
  - Reference validation results (DOI checks, metadata accuracy)
  - Claim verification results (status, confidence scores, evidence)
  - Detailed issue tracking and explanations
- Processing time: 2-10 minutes depending on document size
- Rate-limited API calls to respect academic database policies

**Tab 5: Find Similar Papers** ✨ **NEW!**
- Discover contextually similar research papers
- Two input methods:
  - **By DOI/arXiv/Title**: Direct identifier or title input
  - **From PDF**: Use uploaded PDF from Tab 2
- Adjustable number of recommendations (1-20, default: 10)
- Displays for each recommended paper:
  - Title and authors
  - Year and venue/journal
  - Citation count (impact indicator)
  - Abstract (truncated to 400 chars)
  - Direct links (DOI, arXiv, Semantic Scholar)
- Powered by Semantic Scholar's recommendation API
- Based on citation network and content similarity

**Tab 6: LLM Thinking Process Logs**
- Real-time log viewer with level filtering
- Manual refresh button (no auto-refresh due to Gradio version compatibility)
- Displays formatted logs from `LogBuffer`

**Tab 7: Settings**
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

The application registers 7 API endpoints accessible via MCP:
- `retrieve_papers`
- `explain_paper`
- `write_social_post`
- `process_pdf`
- `generate_infographic`
- `verify_sources`
- `recommend_papers` ✨ **NEW!**

These allow external tools (like Claude Desktop) to call the functions directly.

### Source Verification Pipeline ✨ **NEW!**

The verification system uses a multi-stage pipeline:

**Phase 1: Reference Validation** (`src/tools/reference_validator.py`)
1. **Extraction**: LLM extracts references from document with fallback regex
2. **Validation**: For each reference:
   - Try DOI lookup via Semantic Scholar → CrossRef
   - If no DOI, search by title/author in CrossRef
   - Compare extracted metadata with database metadata
   - Check URL accessibility
3. **Scoring**: Categorize as Verified, With Issues, Failed, or Unverifiable

**Phase 2: Claim Verification** (`src/tools/claim_verifier.py`)
1. **Extraction**: LLM extracts 5-10 verifiable claims (using `claim_extraction_prompt.txt`)
2. **Evidence Gathering**: For each claim:
   - Search Semantic Scholar for relevant papers
   - Collect abstracts, titles, citation counts
3. **Verification**: LLM acts as fact-checker (using `claim_verification_prompt.txt`):
   - Analyzes claim against evidence
   - Returns status: SUPPORTED | PARTIALLY SUPPORTED | CONTRADICTED | NO CONSENSUS | INSUFFICIENT EVIDENCE
   - Provides confidence score (0-100%)
   - Explains reasoning with cited evidence

**API Clients** (`src/utils/api_clients.py`)
- **SemanticScholarAPI**: Paper search and DOI lookup
- **CrossRefAPI**: DOI validation and title search
- **RateLimiter**: Respects API rate limits (2.0 calls/sec default)

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

3. **For infographic design**: Edit `prompts/infographic_prompt.txt`
   - Customizes visual style, layout, and design principles
   - Adjusts section structure and content organization
   - Modifies target audience and presentation format
   - Reloaded on each function call (no restart needed)

4. **For claim extraction** ✨ **NEW!**: Edit `prompts/claim_extraction_prompt.txt`
   - Adjusts which types of claims to extract (empirical, comparative, causal, etc.)
   - Modifies importance and specificity thresholds
   - Changes claim selection criteria
   - Reloaded on each function call (no restart needed)

5. **For claim verification** ✨ **NEW!**: Edit `prompts/claim_verification_prompt.txt`
   - Customizes verification rigor and confidence scoring
   - Adjusts status definitions (SUPPORTED, CONTRADICTED, etc.)
   - Modifies evidence evaluation criteria
   - Reloaded on each function call (no restart needed)

## Common Gotchas

1. **Long text in function arguments**: Automatically truncated at 50,000 chars to prevent malformed calls

2. **PDF text extraction**: If pypdf/PyPDF2 not installed, users get clear error with installation instructions

3. **Gradio version compatibility**: The code avoids newer Gradio features like `theme`, `show_copy_button`, and `every` parameter

4. **Agentic loops**: Limited to 10 iterations to prevent infinite loops from malformed responses

5. **Large PDFs**: First 10,000 characters used for processing to stay within token limits

6. **Infographic generation model availability** ✨ **NEW!**: Image generation requires Gemini 2.0 or later with image generation capabilities. If unavailable, the system provides a structured summary that can be used with external design tools (Canva, Adobe Express, etc.)

7. **Generated infographics storage**: Images are saved to `generated_infographics/` folder with timestamped filenames. The folder is in `.gitignore` to avoid repository bloat.

8. **Source verification API rate limits** ✨ **NEW!**: Verification respects API rate limits (2 calls/sec default) to avoid being blocked by Semantic Scholar and CrossRef. Large documents with many references may take 5-10 minutes.

9. **Verification accuracy limitations** ✨ **NEW!**:
   - Reference validation depends on DOI or accurate title/author matches
   - Claim verification depends on available research evidence
   - Non-English papers may have lower matching success rates
   - Very new papers (<6 months) may not be in databases yet

10. **LLM extraction limitations**: Reference and claim extraction quality depends on document format and structure. PDFs with poor OCR or unusual formatting may have extraction failures.

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
