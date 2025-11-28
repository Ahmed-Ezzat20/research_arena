# 🤖 Research Arena - Agentic Research Assistant

An AI-powered research assistant built with Google Gemini API and Gradio. This application helps you find, understand, and share scientific research papers through an intuitive web interface with comprehensive LLM logging capabilities.

## ✨ Features

- **📚 arXiv Paper Search**: Search for research papers with LLM-enhanced query refinement and intelligent ranking
- **📄 PDF Analysis**: Upload and analyze research papers in PDF format
- **💡 Research Explanation**: Get clear, simplified explanations of complex research papers in Modern Standard Arabic (MSA)
- **📱 Social Media Posts**: Generate engaging LinkedIn posts from research papers
- **💬 Multimodal Chat**: Interactive chat interface supporting text and file uploads (PDFs, images)
- **📊 LLM Logging**: Comprehensive logging of all LLM interactions and tool executions
- **🔧 MCP Server**: Built-in Model Context Protocol server for external tool access

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ahmed-Ezzat20/research_arena.git
   cd research_arena
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python demo.py
   ```

The application will launch a Gradio web interface with public sharing enabled. You can access it through your browser at the provided URL.

## 📖 Usage

### Chat Interface

The chat interface allows you to interact with the research assistant using natural language. You can:

- Ask questions about research topics
- Upload PDF files for analysis
- Request paper searches on specific topics
- Get explanations of research concepts

**Example queries:**
- "Find recent papers about transformer architectures"
- "Explain this research paper in simple terms"
- "Create a LinkedIn post about this paper"

### PDF Upload

The PDF Upload tab provides three dedicated actions:

1. **Analyze PDF**: Get a structured summary of the paper's content
2. **Get Detailed Explanation**: Receive a comprehensive explanation in Arabic (MSA)
3. **Create Social Media Post**: Generate a LinkedIn-ready post in Egyptian Arabic

### Logs

The Logs tab displays real-time information about the LLM's thinking process, including:

- User messages and file uploads
- LLM API calls and responses
- Tool executions and results
- Error messages and warnings

You can filter logs by severity level (DEBUG, INFO, WARNING, ERROR) and refresh or clear them as needed.

### Settings

Configure the logging verbosity to control how much detail is displayed in the logs.

## 🏗️ Architecture

The project follows a modular architecture:

```
research_arena/
├── demo.py                 # Application entry point
├── prompts/                # LLM prompt templates
│   ├── Explainer_prompt.txt
│   └── paper_to_post.txt
└── src/
    ├── config/             # Configuration and settings
    ├── logging/            # Custom logging system
    ├── models/             # Gemini model wrappers
    ├── tools/              # Agentic tools (search, explain, etc.)
    ├── ui/                 # Gradio UI components
    └── utils/              # Tool registry and utilities
```

### Core Components

- **Agentic Loop**: Handles iterative tool calling and response generation
- **Tool System**: Four registered tools for paper retrieval, explanation, social posts, and PDF processing
- **Logging System**: Custom log buffer with emoji-based visual indicators
- **Multimodal Support**: Native support for PDFs and images through Gemini API

## 🛠️ Available Tools

The assistant has access to four tools:

1. **retrieve_related_papers**: Searches arXiv with LLM-refined queries and ranked results
2. **explain_research_paper**: Generates clear explanations using the explainer prompt
3. **write_social_media_post**: Creates LinkedIn posts using the post prompt
4. **process_uploaded_pdf**: Analyzes uploaded PDF files

## 🔧 Customization

### Modifying Prompts

To change the AI's behavior:

- **For paper explanations**: Edit `prompts/Explainer_prompt.txt`
- **For social media posts**: Edit `prompts/paper_to_post.txt`

Changes take effect immediately without restarting the application.

### Configuration

Adjust settings in `src/config/settings.py`:

- `GEMINI_MODEL_NAME`: The Gemini model to use (default: "gemini-2.5-flash")
- `MAX_LOG_BUFFER_SIZE`: Maximum number of log entries to store (default: 1000)
- `MAX_PDF_CHARS`: Maximum characters to extract from PDFs (default: 10000)
- `MAX_ITERATIONS`: Maximum agentic loop iterations (default: 10)

## 📝 Development

### Project Structure

The codebase is organized into clear modules with separation of concerns:

- **config**: Environment setup and configuration constants
- **logging**: Custom logging system with buffer and handlers
- **models**: Gemini API model initialization
- **tools**: Individual tool implementations
- **ui**: Gradio interface components
- **utils**: Tool registry and function mapping

### Adding New Tools

To add a new tool:

1. Create a new file in `src/tools/`
2. Implement your tool function
3. Add the tool declaration to `src/utils/tool_registry.py`
4. Add the function to the `function_map` dictionary
5. (Optional) Register an API endpoint in `src/main.py` for MCP access

## 🐛 Troubleshooting

### Common Issues

**PDF processing errors**: Make sure `pypdf` is installed:
```bash
pip install pypdf
```

**API key errors**: Verify that your `.env` file contains a valid `GEMINI_API_KEY`

**Malformed function calls**: The application automatically handles these and attempts to recover gracefully

## 📄 License

This project is open source. Please add an appropriate license file (e.g., MIT, Apache 2.0) to clarify usage terms.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with [Google Gemini API](https://ai.google.dev/)
- UI powered by [Gradio](https://gradio.app/)
- Paper search via [arXiv API](https://arxiv.org/)

---

**Note**: This application uses the Gemini 2.5 Flash model for all LLM operations. Make sure you have appropriate API quotas and understand the [Gemini API pricing](https://ai.google.dev/pricing).
