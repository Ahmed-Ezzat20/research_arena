"""
PDF processing tools for extracting and analyzing research papers.
"""

try:
    import pypdf
except ImportError:
    try:
        import PyPDF2 as pypdf
    except ImportError:
        pypdf = None

import asyncio
from src.config import MAX_PDF_CHARS
from src.logging import logger
from src.core.llm_provider import get_llm


async def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    logger.info(f"🔍 FUNCTION CALL: extract_text_from_pdf(pdf_path='{pdf_path}')")

    if pypdf is None:
        error_msg = "PDF support not available. Please install pypdf: pip install pypdf"
        logger.error(f"❌ {error_msg}")
        return error_msg

    def _extract_sync():
        """Synchronous PDF extraction wrapped for async execution."""
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

    # Run PDF extraction in thread pool to avoid blocking
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract_sync)
    except Exception as e:
        error_msg = f"Error in async PDF extraction: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return error_msg


async def process_uploaded_pdf(pdf_path: str) -> str:
    """Process an uploaded PDF and return a summary of its content."""
    logger.info(f"🔍 FUNCTION CALL: process_uploaded_pdf(pdf_path='{pdf_path}')")

    # Extract text from PDF (now async)
    pdf_text = await extract_text_from_pdf(pdf_path)

    if pdf_text.startswith("Error") or pdf_text.startswith("PDF support"):
        return pdf_text

    # Limit text length for LLM processing
    if len(pdf_text) > MAX_PDF_CHARS:
        logger.debug(f"  Truncating PDF text from {len(pdf_text)} to {MAX_PDF_CHARS} chars")
        pdf_text = pdf_text[:MAX_PDF_CHARS] + "\n\n[Text truncated for processing...]"

    try:
        logger.debug("📤 LLM REQUEST: PDF content analysis")

        # Use provider abstraction instead of hardcoded Gemini
        llm = get_llm()

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

        response = await llm.generate_simple(prompt)
        logger.info(f"📥 LLM RESPONSE: PDF analysis complete ({len(response)} chars)")
        logger.debug(f"  Preview: {response[:150]}...")

        return response

    except Exception as e:
        error_msg = f"Error analyzing PDF: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return error_msg
