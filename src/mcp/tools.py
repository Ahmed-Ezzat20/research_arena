"""
MCP Tools Registration

This module registers all research assistant tools as MCP tools,
making them accessible to MCP clients like Claude Desktop.
"""

import logging
from typing import Dict, Any

# Import async tools
from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
    generate_paper_infographic,
    verify_document_sources,
    recommend_similar_papers,
)

# Import provider factory (uses LLM_PROVIDER env var for multi-provider support)
from src.core.llm_provider import get_llm

logger = logging.getLogger(__name__)

# Initialize global provider for MCP tools
_provider = None


def get_provider():
    """
    Get or create the global provider instance.

    Uses the provider factory which respects LLM_PROVIDER environment variable.
    This enables multi-provider support (Gemini, OpenAI, Anthropic, etc.)
    """
    global _provider
    if _provider is None:
        _provider = get_llm()  # Uses factory pattern - respects LLM_PROVIDER env var
        logger.info(f"✅ MCP tools using provider: {_provider.provider_name}")
    return _provider


# ============================================================================
# Tool Schemas (for MCP registration)
# ============================================================================

TOOL_SCHEMAS = {
    "retrieve_related_papers": {
        "name": "retrieve_related_papers",
        "description": "Retrieve up to 5 recent arXiv papers matching the query. Uses LLM-refined queries and intelligent ranking.",
        "input_schema": {
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
    "explain_research_paper": {
        "name": "explain_research_paper",
        "description": "Explain a research paper in clear, non-technical language (Modern Standard Arabic with technical terms in English). Generates 500-600 word summaries with pros/cons tables.",
        "input_schema": {
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
    "write_social_media_post": {
        "name": "write_social_media_post",
        "description": "Create a social-media-friendly post (Arabic with Egyptian dialect) summarizing the paper. 200-300 words with multi-step generation.",
        "input_schema": {
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
    "process_uploaded_pdf": {
        "name": "process_uploaded_pdf",
        "description": "Process and analyze an uploaded PDF research paper. Extracts text and provides structured summary.",
        "input_schema": {
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
    "generate_paper_infographic": {
        "name": "generate_paper_infographic",
        "description": "Generate a beautiful academic infographic visualization from a research paper summary. Creates a visually stunning image perfect for social media sharing and presentations with 10 structured sections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_info": {
                    "type": "string",
                    "description": "The research paper information or summary to visualize as an infographic",
                }
            },
            "required": ["paper_info"],
        },
    },
    "verify_document_sources": {
        "name": "verify_document_sources",
        "description": "Perform advanced source verification on a research document. Validates references against academic databases (Semantic Scholar, CrossRef), extracts and fact-checks verifiable claims, and detects potential issues like hallucinated citations. Returns comprehensive verification report.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_text": {
                    "type": "string",
                    "description": "The full document text to verify (research paper, article, report, etc.)",
                },
                "verify_claims": {
                    "type": "boolean",
                    "description": "Whether to extract and verify claims (default: true)",
                },
                "verify_references": {
                    "type": "boolean",
                    "description": "Whether to validate references and citations (default: true)",
                }
            },
            "required": ["document_text"],
        },
    },
    "recommend_similar_papers": {
        "name": "recommend_similar_papers",
        "description": "Recommend similar research papers based on a given paper's DOI, arXiv ID, title, or content. Uses Semantic Scholar's recommendation engine to find contextually similar papers for literature review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_info": {
                    "type": "string",
                    "description": "Paper information: DOI (e.g., '10.xxxx/xxxx'), arXiv ID (e.g., 'arXiv:2101.12345'), paper title, or paper content/abstract",
                },
                "num_recommendations": {
                    "type": "integer",
                    "description": "Number of similar papers to recommend (default: 10, max: 20)",
                }
            },
            "required": ["paper_info"],
        },
    },
}


# ============================================================================
# Async Tool Wrappers (Updated to use async tools with provider)
# ============================================================================

async def mcp_retrieve_related_papers(query: str) -> str:
    """
    MCP wrapper for retrieve_related_papers.

    Args:
        query: Search query for arXiv papers

    Returns:
        Formatted string with paper results
    """
    logger.info(f"🔍 MCP Tool: retrieve_related_papers(query='{query[:50]}...')")
    provider = get_provider()
    result = await retrieve_related_papers(query, provider)
    return result


async def mcp_explain_research_paper(paper_info: str) -> str:
    """
    MCP wrapper for explain_research_paper.

    Args:
        paper_info: Paper information to explain

    Returns:
        Explanation text
    """
    logger.info(f"🔍 MCP Tool: explain_research_paper")
    provider = get_provider()
    result = await explain_research_paper(paper_info, provider)
    return result


async def mcp_write_social_media_post(explanation: str) -> str:
    """
    MCP wrapper for write_social_media_post.

    Args:
        explanation: Explanation to convert to post

    Returns:
        Social media post text
    """
    logger.info(f"🔍 MCP Tool: write_social_media_post")
    provider = get_provider()
    result = await write_social_media_post(explanation, provider)
    return result


async def mcp_process_uploaded_pdf(pdf_path: str) -> str:
    """
    MCP wrapper for process_uploaded_pdf.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Processed PDF summary
    """
    logger.info(f"🔍 MCP Tool: process_uploaded_pdf(pdf_path='{pdf_path}')")
    provider = get_provider()
    result = await process_uploaded_pdf(pdf_path, provider)
    return result


async def mcp_generate_paper_infographic(paper_info: str) -> str:
    """
    MCP wrapper for generate_paper_infographic.

    Args:
        paper_info: Paper information for infographic

    Returns:
        Result message with infographic path or structured data
    """
    logger.info(f"🔍 MCP Tool: generate_paper_infographic")
    provider = get_provider()
    result = await generate_paper_infographic(paper_info, provider)
    return result


async def mcp_verify_document_sources(
    document_text: str,
    verify_claims: bool = True,
    verify_references: bool = True
) -> str:
    """
    MCP wrapper for verify_document_sources.

    Args:
        document_text: Document text to verify
        verify_claims: Whether to verify claims
        verify_references: Whether to verify references

    Returns:
        Verification report
    """
    logger.info(f"🔍 MCP Tool: verify_document_sources")
    provider = get_provider()
    result = await verify_document_sources(document_text, provider, verify_claims, verify_references)
    return result


async def mcp_recommend_similar_papers(
    paper_info: str,
    num_recommendations: int = 10
) -> str:
    """
    MCP wrapper for recommend_similar_papers.

    Args:
        paper_info: Paper information
        num_recommendations: Number of recommendations

    Returns:
        Recommendations text
    """
    logger.info(f"🔍 MCP Tool: recommend_similar_papers")
    result = await recommend_similar_papers(paper_info, num_recommendations)
    return result


# ============================================================================
# Tool Registry
# ============================================================================

# Map tool names to their async wrapper functions
TOOL_FUNCTIONS = {
    "retrieve_related_papers": mcp_retrieve_related_papers,
    "explain_research_paper": mcp_explain_research_paper,
    "write_social_media_post": mcp_write_social_media_post,
    "process_uploaded_pdf": mcp_process_uploaded_pdf,
    "generate_paper_infographic": mcp_generate_paper_infographic,
    "verify_document_sources": mcp_verify_document_sources,
    "recommend_similar_papers": mcp_recommend_similar_papers,
}


def get_tool_schemas() -> Dict[str, Any]:
    """Get all tool schemas for MCP registration."""
    return TOOL_SCHEMAS


def get_tool_function(tool_name: str):
    """Get a tool function by name."""
    return TOOL_FUNCTIONS.get(tool_name)


def list_tool_names() -> list:
    """Get list of all tool names."""
    return list(TOOL_FUNCTIONS.keys())
