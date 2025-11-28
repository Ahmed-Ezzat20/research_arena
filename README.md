# 🤖 Agentic Research Assistant

An AI-powered research assistant built with Google Gemini API and Gradio. Find, explain, visualize, and share scientific research papers with comprehensive LLM logging capabilities.

## ✨ Features

### 💬 Multimodal Chat Interface
- Interactive chat with AI assistant
- Upload and analyze PDFs, images, and other files
- Natural language queries for research papers
- Agentic tool calling for complex tasks

### 📄 PDF Analysis
- Upload research papers in PDF format
- Automated analysis and summarization
- Detailed explanations in Modern Standard Arabic (MSA)
- Social media post generation

### 🎨 **Paper-to-Infographic Generator (NEW!)**
Generate beautiful, visually stunning infographics from research papers:
- **Automated Design**: AI creates professional infographics automatically
- **Structured Content**: Breaks papers into Background, Methods, Results, and Conclusions
- **Social Media Ready**: Perfect for LinkedIn, Twitter, Instagram, and presentations
- **Two Input Methods**: Generate from text summaries or PDF files
- **Downloadable**: Save and share infographics instantly

### 📊 LLM Thinking Process Logs
- Real-time visualization of AI decision-making
- Comprehensive logging of all API calls
- Filter by log level (DEBUG, INFO, WARNING, ERROR)
- Emoji-based visual indicators

### ⚙️ Settings & Configuration
- Dynamic log level control
- Customizable prompts for explanations and social posts
- Environment-based API key management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Comp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python demo.py
   ```

The application will launch a Gradio web interface with public sharing enabled.

## 📖 Usage

### Generating Infographics

#### Method 1: From Text
1. Navigate to the **🎨 Generate Infographic** tab
2. Select **📝 From Text** sub-tab
3. Paste your paper summary or full text (500-2000 words recommended)
4. Click **🎨 Generate Infographic**
5. View and download your infographic

#### Method 2: From PDF
1. First, upload a PDF in the **📄 Upload PDF** tab
2. Navigate to **🎨 Generate Infographic** → **📄 From PDF**
3. Click **🎨 Generate Infographic from PDF**
4. View and download your infographic

**Note:** Infographics are automatically saved in the `generated_infographics/` folder.

### Searching for Papers
Use the chat interface to search for papers:
```
Find me recent papers on quantum computing
```

### Explaining Papers
Get detailed explanations in Arabic:
```
Explain this paper about neural networks
```

### Creating Social Media Posts
Generate LinkedIn-ready posts:
```
Create a social media post about this research
```

## 🏗️ Architecture

### Core Components

- **LLM Integration** (`src/models/gemini.py`): Google Gemini 2.5 Flash integration
- **Tool System** (`src/tools/`): Modular tools for paper search, explanation, social posts, and infographics
- **UI Components** (`src/ui/`): Gradio-based interface modules
- **Logging System** (`src/logging/`): Comprehensive LLM activity logging
- **Configuration** (`src/config/`): Environment and settings management

### Available Tools

1. **retrieve_related_papers** - Search arXiv with AI-refined queries
2. **explain_research_paper** - Generate detailed explanations
3. **write_social_media_post** - Create LinkedIn posts
4. **process_uploaded_pdf** - Analyze PDF files
5. **generate_paper_infographic** - Create visual infographics ✨ NEW

## 🛠️ MCP Server Integration

All tools are exposed as API endpoints for external access:
- `retrieve_papers`
- `explain_paper`
- `write_social_post`
- `process_pdf`
- `generate_infographic` ✨ NEW

## 🎨 Customization

### Modifying Prompts

#### Explanation Style
Edit `prompts/Explainer_prompt.txt` to change how papers are explained.

#### Social Media Format
Edit `prompts/paper_to_post.txt` to customize post generation.

#### Infographic Design
Edit `prompts/infographic_prompt.txt` to adjust visual style and layout.

All prompts are reloaded dynamically—no restart required!

## 📝 Logging

The application uses a custom logging system with visual indicators:

- 💬 User message
- 📤 LLM request
- 📥 LLM response
- 🛠️ Tool call
- ✅ Success
- ❌ Error
- 🎨 Infographic generation
- 📊 Structured summary

View logs in the **📊 LLM Thinking Process Logs** tab.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |

### Configuration Files

- `.env` - Environment variables
- `prompts/` - Customizable AI prompts
- `src/config/settings.py` - Application settings

## 📂 Project Structure

```
Comp/
├── demo.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── src/
│   ├── main.py                  # Gradio app creation
│   ├── config/                  # Configuration
│   ├── logging/                 # Logging system
│   ├── models/                  # LLM integration
│   ├── tools/                   # AI tools
│   │   ├── arxiv_search.py
│   │   ├── explainer.py
│   │   ├── social_post.py
│   │   ├── pdf_processor.py
│   │   └── infographic_generator.py  ✨ NEW
│   ├── ui/                      # UI components
│   │   ├── chat.py
│   │   ├── pdf_upload.py
│   │   ├── infographic.py       ✨ NEW
│   │   ├── logs.py
│   │   └── settings.py
│   └── utils/                   # Utilities
├── prompts/                     # AI prompts
│   ├── Explainer_prompt.txt
│   ├── paper_to_post.txt
│   └── infographic_prompt.txt   ✨ NEW
└── generated_infographics/      # Generated images ✨ NEW
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Google Gemini API](https://ai.google.dev/)
- UI powered by [Gradio](https://gradio.app/)
- Paper search via [arXiv API](https://arxiv.org/)

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ using Google Gemini and Gradio**
