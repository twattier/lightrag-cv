#!/usr/bin/env python3
"""
LightRAG-CV MCP Server

Model Context Protocol server implementation using Python mcp SDK.
Exposes LightRAG-CV search capabilities as MCP tools for OpenWebUI consumption.

Story 3.1: Scaffold implementation with empty tool registry.
Tools will be added in Stories 3.2, 3.3, and 3.8.
"""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ListResourcesResult,
    ReadResourceResult,
)

from app.shared.config import settings

# MCP Server Configuration (RULE 2: All Environment Variables via app.shared.config)
MCP_SERVER_NAME = "lightrag-cv-mcp"
MCP_SERVER_VERSION = "0.1.0"
MCP_TRANSPORT = "stdio"

# Configure structured logging (RULE 7: Structured logging with context)
# Note: Use simple format for stdio transport compatibility
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class LightRAGMCPServer:
    """LightRAG-CV MCP Server implementation."""

    def __init__(self):
        """Initialize MCP server with configuration."""
        self.server = Server(MCP_SERVER_NAME)
        self.tools_registry = {}  # Will be populated in Stories 3.2, 3.3, 3.8
        self.resources_registry = {}  # Will be used in Epic 4

        # Register handlers
        self._register_handlers()

        # Log initialization (RULE 7: Structured logging)
        logger.info(
            f"MCP server initialized: {MCP_SERVER_NAME} v{MCP_SERVER_VERSION} "
            f"(transport={MCP_TRANSPORT}, lightrag_url={settings.lightrag_url})"
        )

    def _register_handlers(self):
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """
            List available tools (AC2: Tool Discovery).

            Story 3.1: Returns empty list.
            Tools will be registered in:
            - Story 3.2: search_by_profile
            - Story 3.3: search_by_skills
            - Story 3.8: get_candidate_details
            """
            logger.info(f"Tool discovery requested (tool_count={len(self.tools_registry)})")
            return list(self.tools_registry.values())

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """
            Tool invocation handler (AC2: Tool Invocation).

            Story 3.1: Scaffold only - no tools registered yet.
            Tool implementations will be added in Stories 3.2, 3.3, 3.8.
            """
            logger.info(
                f"Tool invocation requested (tool_name={name}, has_arguments={bool(arguments)})"
            )

            # AC2: Handle invocation even with no tools (error response)
            if name not in self.tools_registry:
                error_msg = f"Tool '{name}' not found. No tools are registered yet (Story 3.1 scaffold)."
                logger.warning(f"Tool not found: {name} (available_tools={list(self.tools_registry.keys())})")
                return [
                    TextContent(
                        type="text",
                        text=error_msg,
                    )
                ]

            # Future: Tool execution will happen here in Stories 3.2, 3.3, 3.8
            # Example: return await self.tools_registry[name].execute(arguments)
            return [TextContent(type="text", text="Tool execution not implemented (Story 3.1)")]

        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """
            List available resources (AC2: Resource Serving Capability).

            Story 3.1: Returns empty list.
            Resources will be used in Epic 4 for match explanations.
            """
            logger.info(f"Resource discovery requested (resource_count={len(self.resources_registry)})")
            return ListResourcesResult(resources=list(self.resources_registry.values()))

        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """
            Resource retrieval handler (AC2: Resource Serving Capability).

            Story 3.1: Scaffold only - no resources available yet.
            """
            logger.info(f"Resource read requested (uri={uri})")

            if uri not in self.resources_registry:
                error_msg = f"Resource '{uri}' not found. No resources available yet (Story 3.1 scaffold)."
                logger.warning(f"Resource not found: {uri} (available_resources={list(self.resources_registry.keys())})")
                # Return empty resource result
                return ReadResourceResult(contents=[TextContent(type="text", text=error_msg)])

            # Future: Resource retrieval will happen here in Epic 4
            return ReadResourceResult(contents=[TextContent(type="text", text="Resource not implemented")])

    async def run(self):
        """
        Start MCP server with stdio transport (AC4: Server Startup).

        Uses stdio transport as identified in OpenWebUI MCP validation spike.
        mcpo proxy will bridge stdio <-> OpenAPI for OpenWebUI connectivity.
        """
        logger.info(
            f"Starting MCP server: {MCP_SERVER_NAME} v{MCP_SERVER_VERSION} (transport=stdio)"
        )

        try:
            # AC2: Protocol version handling and capability negotiation
            # The mcp SDK handles this automatically via stdio_server
            async with stdio_server() as (read_stream, write_stream):
                logger.info(
                    f"MCP server started successfully (transport=stdio, lightrag_url={settings.lightrag_url}, "
                    f"postgres_host={settings.POSTGRES_HOST})"
                )
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        except Exception as e:
            # AC2: Error handling with structured logging (RULE 7)
            logger.error(f"MCP server error (error_type={type(e).__name__}, error_message={str(e)})", exc_info=True)
            raise


async def main():
    """Main entry point for MCP server."""
    # AC4: Startup logging (RULE 7: Structured logging)
    # RULE 8: No sensitive data - only log postgres host, not password
    postgres_info = settings.postgres_dsn.split("@")[1] if "@" in settings.postgres_dsn else "N/A"
    logger.info(
        f"Initializing LightRAG-CV MCP Server v{MCP_SERVER_VERSION} "
        f"(transport={MCP_TRANSPORT}, lightrag_url={settings.lightrag_url}, postgres={postgres_info})"
    )

    server = LightRAGMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error (error_type={type(e).__name__}, error_message={str(e)})", exc_info=True)
        sys.exit(1)
