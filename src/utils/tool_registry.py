"""
Tool registry and declarations for Gemini function calling.
Maps tool names to their implementations and defines schemas.
"""

from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
    generate_paper_infographic,
    verify_document_sources,
)


# Define tool declarations for Gemini
tools = [
    {
        "function_declarations": [
            {
                "name": "retrieve_related_papers",
                "description": "Retrieve up to 5 recent arXiv papers matching the query",
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
                "description": "Explain a research paper in clear, non-technical language",
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
                "description": "Create a social-media-friendly post summarizing the paper",
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
                "description": "Process and analyze an uploaded PDF research paper",
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
                "description": "Generate a beautiful infographic visualization from a research paper summary. Creates a visually stunning image perfect for social media sharing and presentations.",
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
        ]
    }
]

# Map function names to actual functions
function_map = {
    "retrieve_related_papers": retrieve_related_papers,
    "explain_research_paper": explain_research_paper,
    "write_social_media_post": write_social_media_post,
    "process_uploaded_pdf": process_uploaded_pdf,
    "generate_paper_infographic": generate_paper_infographic,
    "verify_document_sources": verify_document_sources,
}
