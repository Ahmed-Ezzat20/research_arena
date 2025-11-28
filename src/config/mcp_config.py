"""
MCP Server Configuration

This module contains configuration settings specific to the MCP server,
including server metadata, feature flags, and resource paths.
"""

import os
from pathlib import Path

# Server Metadata
MCP_SERVER_NAME = "research-assistant"
MCP_SERVER_VERSION = "1.0.0"
MCP_SERVER_DESCRIPTION = "Agentic Research Assistant with advanced paper analysis capabilities"

# Feature Flags
ENABLE_TOOLS = True  # Enable MCP tools
ENABLE_PROMPTS = True  # Enable MCP prompts
ENABLE_RESOURCES = True  # Enable MCP resources
ENABLE_SESSIONS = True  # Enable ClientSession management

# Transport Configuration
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")  # stdio or sse
MCP_PORT = int(os.getenv("MCP_PORT", "5173"))  # Port for SSE transport

# Resource Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"
INFOGRAPHICS_DIR = RESOURCES_DIR / "infographics"
PDFS_DIR = RESOURCES_DIR / "pdfs"
CONVERSATIONS_DIR = RESOURCES_DIR / "conversations"

# Ensure resource directories exist
INFOGRAPHICS_DIR.mkdir(parents=True, exist_ok=True)
PDFS_DIR.mkdir(parents=True, exist_ok=True)
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Resource URI Schemes
RESOURCE_SCHEMES = {
    "infographic": str(INFOGRAPHICS_DIR),
    "pdf": str(PDFS_DIR),
    "conversation": str(CONVERSATIONS_DIR),
}

# Session Configuration
SESSION_MAX_AGE_HOURS = 24  # Auto-cleanup sessions after 24 hours
SESSION_CLEANUP_INTERVAL_MINUTES = 60  # Run cleanup every hour
MAX_SESSIONS = 100  # Maximum concurrent sessions

# Tool Configuration
TOOL_TIMEOUT_SECONDS = 120  # Maximum execution time for tools
TOOL_RETRY_ATTEMPTS = 2  # Number of retries for failed tool calls

# Prompt Configuration
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# MCP Server Capabilities
MCP_CAPABILITIES = {
    "tools": ENABLE_TOOLS,
    "prompts": ENABLE_PROMPTS,
    "resources": ENABLE_RESOURCES,
    "experimental": {
        "sessions": ENABLE_SESSIONS,
    }
}

# Logging
MCP_LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
MCP_LOG_FORMAT = "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
