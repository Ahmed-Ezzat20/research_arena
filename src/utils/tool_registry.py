"""
Tool registry and declarations for Gemini function calling.
Maps tool names to their implementations and defines schemas.
"""

from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
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
        ]
    }
]

# Map function names to actual functions
function_map = {
    "retrieve_related_papers": retrieve_related_papers,
    "explain_research_paper": explain_research_paper,
    "write_social_media_post": write_social_media_post,
    "process_uploaded_pdf": process_uploaded_pdf,
}
