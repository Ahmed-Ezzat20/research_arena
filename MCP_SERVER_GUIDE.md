# MCP Server Guide for Research Arena

## Overview

Research Arena includes a **dedicated MCP server** that exposes all 7 research tools to MCP-compatible clients like Claude Desktop, VSCode with Cline, and other MCP-enabled applications.

The MCP server is built with **FastMCP** and runs independently from the Gradio UI, allowing external applications to access your research tools programmatically.

---

## 🚀 Quick Start

### Running the MCP Server

From the project root directory:

```bash
python mcp_server.py
```

This will start the MCP server with **stdio transport** (default), which is compatible with Claude Desktop.

### Alternative Transports

**SSE Transport** (for web-based clients):
```bash
python mcp_server.py --transport sse --port 5173
```

**Debug Mode**:
```bash
python mcp_server.py --debug
```

---

## 🛠️ Available MCP Tools

The MCP server exposes **7 powerful research tools**:

| Tool Name | Description | Input Parameters |
|-----------|-------------|------------------|
| `retrieve_related_papers` | Search arXiv for relevant papers with AI-refined queries | `query` (string) |
| `explain_research_paper` | Generate clear explanations in Arabic/English | `paper_info` (string) |
| `write_social_media_post` | Create engaging social media posts | `explanation` (string) |
| `process_uploaded_pdf` | Extract and analyze PDF research papers | `pdf_path` (string) |
| `generate_paper_infographic` | Create beautiful academic infographics | `paper_info` (string) |
| `verify_document_sources` | Advanced source and claim verification | `document_text` (string), `verify_claims` (bool), `verify_references` (bool) |
| `recommend_similar_papers` | Find similar papers using Semantic Scholar | `paper_info` (string), `num_recommendations` (int) |

---

## 🔌 Connecting to Claude Desktop

### 1. Install Claude Desktop

Download from: https://claude.ai/download

### 2. Configure MCP Server

Edit your Claude Desktop configuration file:

**On macOS/Linux:**
```bash
~/.config/claude/claude_desktop_config.json
```

**On Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 3. Add Research Arena MCP Server

Add this configuration to the file:

```json
{
  "mcpServers": {
    "research_arena": {
      "command": "python",
      "args": [
        "/path/to/research_arena/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

**Important:** Replace `/path/to/research_arena/` with the actual path to your project directory.

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. You should see the Research Arena tools available in the MCP tools panel.

---

## 💬 Using MCP Tools in Claude

Once connected, you can use the tools in your Claude conversations:

**Example 1: Search for Papers**
```
Use the retrieve_related_papers tool to find recent papers on quantum computing.
```

**Example 2: Explain a Paper**
```
Use the explain_research_paper tool to explain this paper: [paste paper info]
```

**Example 3: Verify Sources**
```
Use the verify_document_sources tool to check the references and claims in this document: [paste document]
```

Claude will automatically call the appropriate MCP tool and return the results.

---

## 🔧 Architecture

### How It Works

```
Claude Desktop (MCP Client)
        ↓
    stdio transport
        ↓
mcp_server.py (FastMCP Server)
        ↓
src/mcp/server.py (Tool Registration)
        ↓
src/mcp/tools.py (Async Wrappers)
        ↓
src/tools/*.py (Research Tools)
        ↓
Google Gemini API
```

### Key Components

1. **`mcp_server.py`**: Entry point for the MCP server
2. **`src/mcp/server.py`**: FastMCP server configuration and tool registration
3. **`src/mcp/tools.py`**: Async wrappers for all research tools
4. **`src/tools/`**: The actual research tool implementations

---

## 📝 Configuration

### Environment Variables

The MCP server requires the following environment variables:

```bash
GEMINI_API_KEY=your_gemini_api_key
```

You can set these in:
- `.env` file in the project root
- System environment variables
- Claude Desktop configuration (as shown above)

### MCP Server Settings

Edit `src/config/mcp_config.py` to customize:

```python
MCP_SERVER_NAME = "research_arena"
MCP_SERVER_VERSION = "1.0.0"
MCP_TRANSPORT = "stdio"  # or "sse"
MCP_PORT = 5173
MCP_LOG_LEVEL = "INFO"
ENABLE_TOOLS = True
ENABLE_PROMPTS = False
ENABLE_RESOURCES = False
```

---

## 🐛 Troubleshooting

### MCP Server Won't Start

**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Check dependencies:**
```bash
pip install -r requirements.txt
```

**Check environment variables:**
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### Claude Desktop Can't Connect

**Check the configuration file path:**
- Make sure the path to `mcp_server.py` is absolute, not relative
- Use forward slashes `/` even on Windows

**Check the logs:**
- Claude Desktop logs are in `~/.config/claude/logs/` (macOS/Linux)
- Look for error messages related to MCP server connection

**Restart Claude Desktop:**
- Close Claude Desktop completely
- Reopen it and check the MCP tools panel

### Tools Return Errors

**Check the MCP server logs:**
```bash
python mcp_server.py --debug
```

**Check the Gemini API key:**
- Make sure your API key is valid
- Check your API quota at https://ai.google.dev/

---

## 🎯 For Competition Judges

This MCP server demonstrates:

1. **Proper MCP Implementation**: Using FastMCP with stdio and SSE transports
2. **7+ Production-Ready Tools**: All tools are async, well-documented, and tested
3. **Provider Abstraction**: Easy to switch between LLM providers
4. **Clean Architecture**: Separation between UI and MCP server
5. **Real-World Use Case**: Advanced research assistant with source verification

The MCP server can be used standalone (without the Gradio UI) by any MCP-compatible client, making it a true MCP application, not just a Gradio app with MCP support.

---

## 📚 Additional Resources

- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Claude Desktop**: https://claude.ai/download
- **Research Arena GitHub**: https://github.com/Ahmed-Ezzat20/research_arena

---

**Built for the MCP 1st Birthday Competition** 🎉
