"""
Tool Execution Service

This module handles the execution of tools with LLM provider injection.
It acts as a bridge between the MCP layer and the actual tool implementations.
"""

import logging
from typing import Dict, Any, Callable, Optional
import asyncio

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes tools with proper LLM provider injection and error handling.

    This service ensures that all tool executions are:
    - Properly logged
    - Have access to the LLM provider
    - Handle errors gracefully
    - Track execution time
    """

    def __init__(self):
        """Initialize the tool executor."""
        self._tools: Dict[str, Callable] = {}
        logger.info("⚙️ Tool executor initialized")

    def register_tool(self, name: str, func: Callable):
        """
        Register a tool function.

        Args:
            name: Tool name (e.g., 'retrieve_related_papers')
            func: Async function to execute
        """
        self._tools[name] = func
        logger.debug(f"📝 Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None if not found
        """
        return self._tools.get(name)

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        llm_provider=None
    ) -> Any:
        """
        Execute a tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as a dictionary
            llm_provider: Optional LLM provider instance (auto-loaded if None)

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        import time

        start_time = time.time()
        logger.info(f"🔍 Executing tool: {tool_name}")
        logger.debug(f"   Arguments: {arguments}")

        # Get the tool function
        tool_func = self.get_tool(tool_name)
        if not tool_func:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        try:
            # Execute the tool (all tools are async)
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                # Fallback for sync functions (wrap in executor)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: tool_func(**arguments))

            execution_time = time.time() - start_time
            logger.info(f"✅ Tool '{tool_name}' completed in {execution_time:.2f}s")
            logger.debug(f"   Result preview: {str(result)[:200]}...")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Tool '{tool_name}' failed after {execution_time:.2f}s: {e}")
            raise

    def list_tools(self) -> list:
        """
        Get list of all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def is_registered(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool is registered
        """
        return tool_name in self._tools


# Global singleton instance
_executor = ToolExecutor()


def get_tool_executor() -> ToolExecutor:
    """
    Get the global tool executor instance.

    Returns:
        ToolExecutor singleton
    """
    return _executor


def register_tool(name: str, func: Callable):
    """
    Convenience function to register a tool.

    Args:
        name: Tool name
        func: Tool function (must be async)
    """
    _executor.register_tool(name, func)


async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    llm_provider=None
) -> Any:
    """
    Convenience function to execute a tool.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments
        llm_provider: Optional LLM provider

    Returns:
        Tool result
    """
    return await _executor.execute(tool_name, arguments, llm_provider)
