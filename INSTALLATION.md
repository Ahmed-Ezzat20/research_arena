# Installation & Running Guide

This guide will help you set up and run **Research Arena** on your system.

## Prerequisites

- **Python 3.11+** (recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Ahmed-Ezzat20/research_arena.git
cd research_arena
```

### 2. Create a Virtual Environment (Recommended)

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key, visit: https://ai.google.dev/

## Running the Application

### Option 1: Using the Launch Scripts (Recommended)

**On Windows:**
```cmd
run.bat
```

**On macOS/Linux:**
```bash
./run.sh
```

### Option 2: Using Python Directly

**From the project root directory:**
```bash
python demo.py
```

**Or:**
```bash
python app.py
```

### Option 3: Using the src/main.py File

**Important:** If you want to run `src/main.py` directly, you must run it from the project root with the `-m` flag:

```bash
python -m src.main
```

**Do NOT run it like this:**
```bash
python src/main.py  # This will cause import errors!
```

## Accessing the Application

Once the application starts, you'll see output like:

```
Running on local URL:  http://127.0.0.1:7860
```

Open your web browser and navigate to `http://127.0.0.1:7860` to use Research Arena!

## Troubleshooting

### Import Errors (ModuleNotFoundError: No module named 'src')

**Solution:** Always run the application from the project root directory using one of the recommended methods above.

### Missing Dependencies

**Solution:** Make sure you've installed all requirements:
```bash
pip install -r requirements.txt
```

### Gemini API Key Not Found

**Solution:** Make sure your `.env` file exists in the project root and contains:
```
GEMINI_API_KEY=your_actual_api_key
```

### Port Already in Use

**Solution:** If port 7860 is already in use, you can specify a different port by modifying `src/main.py`:

```python
app.launch(
    server_name="0.0.0.0",
    server_port=7861,  # Change this to any available port
    share=False,
    show_error=True,
)
```

## Development Mode

For development, you may want to enable auto-reload:

```python
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True,
    debug=True,  # Enable debug mode
)
```

## Deployment

### HuggingFace Spaces

To deploy to HuggingFace Spaces:

1. Create a new Space on HuggingFace
2. Select "Gradio" as the SDK
3. Push your code to the Space repository
4. Add your `GEMINI_API_KEY` as a secret in the Space settings

### Docker (Coming Soon)

A Dockerfile will be provided for containerized deployment.

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/Ahmed-Ezzat20/research_arena/issues)
- Check the [README.md](README.md) for more information

---

**Happy Researching! 🔬**
