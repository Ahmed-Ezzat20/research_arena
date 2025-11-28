"""
FastMCP Server Configuration

This module creates and configures the FastMCP server instance,
registering all tools, prompts, and resources.
"""

import logging
from fastmcp import FastMCP

from src.config.mcp_config import (
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    MCP_SERVER_DESCRIPTION,
    ENABLE_TOOLS,
    ENABLE_PROMPTS,
    ENABLE_RESOURCES,
)

from .tools import TOOL_SCHEMAS, TOOL_FUNCTIONS
from .prompts import get_prompt_registry
from .resources import get_resource_manager
from .sessions import get_session_manager

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """
    Create and configure the FastMCP server.

    Returns:
        Configured FastMCP instance
    """
    logger.info(f"🚀 Creating MCP server: {MCP_SERVER_NAME} v{MCP_SERVER_VERSION}")

    # Create FastMCP instance
    mcp = FastMCP(
        name=MCP_SERVER_NAME,
        version=MCP_SERVER_VERSION,
        description=MCP_SERVER_DESCRIPTION,
    )

    # Initialize managers
    session_manager = get_session_manager()
    prompt_registry = get_prompt_registry()
    resource_manager = get_resource_manager()

    logger.info(f"✅ Initialized session manager, prompt registry, and resource manager")

    # ========================================================================
    # Register Tools
    # ========================================================================
    if ENABLE_TOOLS:
        logger.info("🛠️ Registering MCP tools...")

        # Register each tool individually (FastMCP requires separate decorator calls)

        @mcp.tool()
        async def retrieve_related_papers(query: str) -> str:
            """Retrieve up to 5 recent arXiv papers matching the query."""
            return await TOOL_FUNCTIONS["retrieve_related_papers"](query)

        @mcp.tool()
        async def explain_research_paper(paper_info: str) -> str:
            """Explain a research paper in clear, non-technical language."""
            return await TOOL_FUNCTIONS["explain_research_paper"](paper_info)

        @mcp.tool()
        async def write_social_media_post(explanation: str) -> str:
            """Create a social-media-friendly post summarizing the paper."""
            return await TOOL_FUNCTIONS["write_social_media_post"](explanation)

        @mcp.tool()
        async def process_uploaded_pdf(pdf_path: str) -> str:
            """Process and analyze an uploaded PDF research paper."""
            return await TOOL_FUNCTIONS["process_uploaded_pdf"](pdf_path)

        @mcp.tool()
        async def generate_paper_infographic(paper_info: str) -> str:
            """Generate a beautiful academic infographic visualization."""
            return await TOOL_FUNCTIONS["generate_paper_infographic"](paper_info)

        @mcp.tool()
        async def verify_document_sources(
            document_text: str,
            verify_claims: bool = True,
            verify_references: bool = True
        ) -> str:
            """Perform advanced source verification on a research document."""
            return await TOOL_FUNCTIONS["verify_document_sources"](
                document_text, verify_claims, verify_references
            )

        @mcp.tool()
        async def recommend_similar_papers(
            paper_info: str,
            num_recommendations: int = 10
        ) -> str:
            """Recommend similar research papers based on given paper info."""
            return await TOOL_FUNCTIONS["recommend_similar_papers"](
                paper_info, num_recommendations
            )

        logger.info(f"✅ Registered 7 MCP tools")

    # ========================================================================
    # Register Prompts (Simplified for testing)
    # ========================================================================
    if ENABLE_PROMPTS:
        logger.info("📝 Prompts available but not registered yet (TODO)")
        # TODO: Implement proper prompt registration
        # For now, prompts are accessible via prompt_registry.get_prompt()

    # ========================================================================
    # Register Resources (Simplified for testing)
    # ========================================================================
    if ENABLE_RESOURCES:
        logger.info("📚 Resources available but not registered yet (TODO)")
        # TODO: Implement proper resource registration
        # For now, resources are accessible via resource_manager methods

    logger.info(f"🎉 MCP server '{MCP_SERVER_NAME}' fully configured")

    return mcp


# For convenience, create a singleton instance
_mcp_server = None


def get_mcp_server() -> FastMCP:
    """
    Get or create the MCP server instance.

    Returns:
        FastMCP singleton
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = create_mcp_server()
    return _mcp_server
