"""
Tool registry and declarations for function calling.
Maps tool names to their implementations and defines schemas.
Supports both sync (legacy) and async (new) function maps.
"""

from typing import Dict, Callable, List
from src.providers.base import BaseLLMProvider
from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
    generate_paper_infographic,
    verify_document_sources,
    recommend_similar_papers,
)


# Define tool declarations for Gemini (legacy format)
tools = [
    {
        "function_declarations": [
            {
                "name": "retrieve_related_papers",
                "description": "Retrieve up to 5 recent arXiv papers matching the query. Uses LLM-refined queries and intelligent ranking.",
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
                "description": "Explain a research paper in clear, non-technical language (Modern Standard Arabic with technical terms in English). Generates 500-600 word summaries with pros/cons tables.",
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
                "description": "Create a social-media-friendly post (Arabic with Egyptian dialect) summarizing the paper. 200-300 words with multi-step generation.",
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
                "description": "Process and analyze an uploaded PDF research paper. Extracts text and provides structured summary.",
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
            {
                "name": "generate_paper_infographic",
                "description": "Generate a beautiful academic infographic visualization from a research paper summary. Creates a visually stunning image perfect for social media sharing and presentations with 10 structured sections.",
                "parameters": {
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
            {
                "name": "verify_document_sources",
                "description": "Perform advanced source verification on a research document. Validates references against academic databases (Semantic Scholar, CrossRef), extracts and fact-checks verifiable claims, and detects potential issues like hallucinated citations or unsubstantiated claims. Returns a comprehensive verification report.",
                "parameters": {
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
            {
                "name": "recommend_similar_papers",
                "description": "Recommend similar research papers based on a given paper's DOI, arXiv ID, title, or content. Uses Semantic Scholar's recommendation engine to find contextually similar papers that may be relevant for literature review.",
                "parameters": {
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
        ]
    }
]


# Legacy synchronous function map (for backward compatibility)
function_map = {
    "retrieve_related_papers": retrieve_related_papers,
    "explain_research_paper": explain_research_paper,
    "write_social_media_post": write_social_media_post,
    "process_uploaded_pdf": process_uploaded_pdf,
    "generate_paper_infographic": generate_paper_infographic,
    "verify_document_sources": verify_document_sources,
    "recommend_similar_papers": recommend_similar_papers,
}


def get_async_function_map(provider: BaseLLMProvider) -> Dict[str, Callable]:
    """
    Get async function map with provider injected.
    
    Args:
        provider: LLM provider instance to inject into tools
        
    Returns:
        Dictionary mapping function names to async callables
    """
    return {
        "retrieve_related_papers": lambda query: retrieve_related_papers(query, provider),
        "explain_research_paper": lambda paper_info: explain_research_paper(paper_info, provider),
        "write_social_media_post": lambda explanation: write_social_media_post(explanation, provider),
        "process_uploaded_pdf": lambda pdf_path: process_uploaded_pdf(pdf_path, provider),
        "generate_paper_infographic": lambda paper_info: generate_paper_infographic(paper_info, provider),
        "verify_document_sources": lambda document_text, verify_claims=True, verify_references=True: 
            verify_document_sources(document_text, provider, verify_claims, verify_references),
        "recommend_similar_papers": lambda paper_info, num_recommendations=10: 
            recommend_similar_papers(paper_info, provider, num_recommendations),
    }


def get_tool_schemas() -> List[Dict]:
    """
    Get tool schemas in a flat list format.
    
    Returns:
        List of tool schema dictionaries
    """
    return tools[0]["function_declarations"]
