"""
MCP Server Entry Point

This is the main entry point for running the Agentic Research Assistant as an MCP server.
Can be used with Claude Desktop, VSCode, or any MCP-compatible client.

Usage:
    python mcp_server.py                    # Run with stdio transport (for Claude Desktop)
    python mcp_server.py --transport sse    # Run with SSE transport
    python mcp_server.py --port 5173        # Custom port for SSE
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.server import create_mcp_server
from src.config.mcp_config import (
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    MCP_TRANSPORT,
    MCP_PORT,
    MCP_LOG_LEVEL,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, MCP_LOG_LEVEL),
    format="[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for MCP server."""
    parser = argparse.ArgumentParser(
        description=f"{MCP_SERVER_NAME} MCP Server v{MCP_SERVER_VERSION}"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=MCP_TRANSPORT,
        help="Transport protocol (default: stdio for Claude Desktop)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=MCP_PORT,
        help=f"Port for SSE transport (default: {MCP_PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 70)
    logger.info(f"🚀 Starting {MCP_SERVER_NAME} MCP Server v{MCP_SERVER_VERSION}")
    logger.info("=" * 70)
    logger.info(f"Transport: {args.transport}")
    if args.transport == "sse":
        logger.info(f"Port: {args.port}")
    logger.info("=" * 70)

    try:
        # Create MCP server
        mcp = create_mcp_server()

        # Run server with appropriate transport
        if args.transport == "stdio":
            logger.info("📡 Starting stdio transport (for Claude Desktop)...")
            logger.info("Waiting for MCP client connection...")
            mcp.run(transport="stdio")

        elif args.transport == "sse":
            logger.info(f"📡 Starting SSE transport on port {args.port}...")
            logger.info(f"Server will be available at: http://localhost:{args.port}")
            mcp.run(transport="sse", port=args.port)

    except KeyboardInterrupt:
        logger.info("\n⏹️ Server stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
