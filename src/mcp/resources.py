"""
MCP Resources Manager

This module manages dynamic resources (infographics, PDFs, conversations)
and exposes them via the MCP protocol.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from threading import Lock
import base64

from src.config.mcp_config import (
    INFOGRAPHICS_DIR,
    PDFS_DIR,
    CONVERSATIONS_DIR,
    RESOURCE_SCHEMES,
)

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages MCP resources.

    Resources are files that can be accessed by MCP clients:
    - Infographics (generated images)
    - PDFs (uploaded research papers)
    - Conversations (session transcripts)
    """

    def __init__(self):
        """Initialize the resource manager."""
        self._lock = Lock()
        self._resource_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("📚 Resource manager initialized")

    def _scan_directory(self, directory: Path, scheme: str) -> List[Dict[str, Any]]:
        """
        Scan a directory for resources.

        Args:
            directory: Directory to scan
            scheme: URI scheme (e.g., 'infographic', 'pdf')

        Returns:
            List of resource metadata
        """
        resources = []

        if not directory.exists():
            logger.warning(f"⚠️ Resource directory does not exist: {directory}")
            return resources

        for file_path in directory.iterdir():
            if file_path.is_file():
                uri = f"{scheme}://{file_path.name}"
                resources.append({
                    "uri": uri,
                    "name": file_path.stem,
                    "description": f"{scheme.capitalize()}: {file_path.stem}",
                    "mime_type": self._get_mime_type(file_path),
                    "size": file_path.stat().st_size,
                })

        return resources

    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for a file."""
        extension = file_path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".json": "application/json",
            ".md": "text/markdown",
        }
        return mime_types.get(extension, "application/octet-stream")

    def list_resources(self, scheme: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available resources.

        Args:
            scheme: Optional filter by URI scheme

        Returns:
            List of resource metadata
        """
        resources = []

        schemes_to_scan = [scheme] if scheme else ["infographic", "pdf", "conversation"]

        for resource_scheme in schemes_to_scan:
            if resource_scheme == "infographic":
                resources.extend(self._scan_directory(INFOGRAPHICS_DIR, "infographic"))
            elif resource_scheme == "pdf":
                resources.extend(self._scan_directory(PDFS_DIR, "pdf"))
            elif resource_scheme == "conversation":
                resources.extend(self._scan_directory(CONVERSATIONS_DIR, "conversation"))

        logger.debug(f"📋 Listed {len(resources)} resources")
        return resources

    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """
        Get a resource by URI.

        Args:
            uri: Resource URI (e.g., 'infographic://paper_summary.png')

        Returns:
            Resource data with content, or None if not found
        """
        try:
            # Parse URI
            if "://" not in uri:
                logger.error(f"❌ Invalid URI format: {uri}")
                return None

            scheme, filename = uri.split("://", 1)

            # Get directory for scheme
            if scheme == "infographic":
                directory = INFOGRAPHICS_DIR
            elif scheme == "pdf":
                directory = PDFS_DIR
            elif scheme == "conversation":
                directory = CONVERSATIONS_DIR
            else:
                logger.error(f"❌ Unknown scheme: {scheme}")
                return None

            file_path = directory / filename

            if not file_path.exists():
                logger.warning(f"⚠️ Resource not found: {uri}")
                return None

            # Read file content
            mime_type = self._get_mime_type(file_path)

            # For binary files (images, PDFs), encode as base64
            if mime_type.startswith("image/") or mime_type == "application/pdf":
                with open(file_path, "rb") as f:
                    content = base64.b64encode(f.read()).decode("utf-8")
                    encoding = "base64"
            else:
                # Text files
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    encoding = "utf-8"

            logger.debug(f"📖 Retrieved resource: {uri}")

            return {
                "uri": uri,
                "name": file_path.stem,
                "mime_type": mime_type,
                "content": content,
                "encoding": encoding,
                "size": file_path.stat().st_size,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get resource {uri}: {e}")
            return None

    def register_resource(
        self,
        scheme: str,
        filename: str,
        content: bytes,
        description: Optional[str] = None
    ) -> str:
        """
        Register a new resource.

        Args:
            scheme: URI scheme ('infographic', 'pdf', 'conversation')
            filename: Filename
            content: File content (bytes)
            description: Optional description

        Returns:
            URI of the registered resource
        """
        try:
            # Get directory for scheme
            if scheme == "infographic":
                directory = INFOGRAPHICS_DIR
            elif scheme == "pdf":
                directory = PDFS_DIR
            elif scheme == "conversation":
                directory = CONVERSATIONS_DIR
            else:
                raise ValueError(f"Unknown scheme: {scheme}")

            # Write file
            file_path = directory / filename
            with open(file_path, "wb") as f:
                f.write(content)

            uri = f"{scheme}://{filename}"
            logger.info(f"✅ Registered resource: {uri}")

            return uri

        except Exception as e:
            logger.error(f"❌ Failed to register resource: {e}")
            raise

    def delete_resource(self, uri: str) -> bool:
        """
        Delete a resource.

        Args:
            uri: Resource URI

        Returns:
            True if deleted, False otherwise
        """
        try:
            # Parse URI
            if "://" not in uri:
                return False

            scheme, filename = uri.split("://", 1)

            # Get directory for scheme
            if scheme == "infographic":
                directory = INFOGRAPHICS_DIR
            elif scheme == "pdf":
                directory = PDFS_DIR
            elif scheme == "conversation":
                directory = CONVERSATIONS_DIR
            else:
                return False

            file_path = directory / filename

            if file_path.exists():
                file_path.unlink()
                logger.info(f"🗑️ Deleted resource: {uri}")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to delete resource {uri}: {e}")
            return False

    def get_resource_count(self, scheme: Optional[str] = None) -> int:
        """Get count of resources."""
        return len(self.list_resources(scheme))


# Global singleton instance
_resource_manager = ResourceManager()


def get_resource_manager() -> ResourceManager:
    """
    Get the global resource manager instance.

    Returns:
        ResourceManager singleton
    """
    return _resource_manager
