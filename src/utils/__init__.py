"""Utils module for the Agentic Research Assistant."""

from .tool_registry import tools, get_function_map, get_async_function_map, get_tool_schemas
from .api_clients import SemanticScholarAPI, CrossRefAPI, RateLimiter

# For backward compatibility - lazy load function_map
def __getattr__(name):
    if name == "function_map":
        return get_function_map()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "tools",
    "get_function_map",
    "function_map",
    "get_async_function_map",
    "get_tool_schemas",
    "SemanticScholarAPI",
    "CrossRefAPI",
    "RateLimiter",
]
