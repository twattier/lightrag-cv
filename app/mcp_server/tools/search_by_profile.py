"""
Search by CIGREF Profile MCP Tool.

Story 3.2: Implements profile-based candidate search using LightRAG hybrid retrieval.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from mcp.types import Tool, TextContent

from app.shared.config import settings

# Configure logging (RULE 7: Structured logging with context)
logger = logging.getLogger(__name__)


class SearchByProfileTool:
    """
    MCP tool for searching candidates by CIGREF profile.

    Translates profile search parameters into LightRAG queries and returns
    formatted candidate results.
    """

    # Tool definition for MCP protocol (AC1, AC6)
    TOOL_DEFINITION = Tool(
        name="search_by_profile",
        description=(
            "Find candidates matching a specific CIGREF IT profile. "
            "Searches the knowledge base using hybrid vector-graph retrieval "
            "to find candidates aligned with standardized job requirements. "
            "Example: 'Cloud Architect', 'Data Engineer', 'DevOps Engineer'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "profile_name": {
                    "type": "string",
                    "description": "CIGREF profile name (e.g., 'Cloud Architect', 'Data Engineer')"
                },
                "experience_years": {
                    "type": "number",
                    "description": "Minimum years of experience (optional)",
                    "minimum": 0
                },
                "top_k": {
                    "type": "number",
                    "description": "Number of results to return (default: 5)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                }
            },
            "required": ["profile_name"]
        }
    )

    def __init__(self):
        """Initialize tool with LightRAG configuration."""
        self.lightrag_url = settings.lightrag_url
        self.timeout = httpx.Timeout(60.0)  # 60s for complex queries

    def _construct_query(
        self,
        profile_name: str,
        experience_years: Optional[int] = None
    ) -> str:
        """
        Construct natural language query from parameters (AC2).

        Args:
            profile_name: CIGREF profile name
            experience_years: Optional minimum years of experience

        Returns:
            Natural language query string for LightRAG
        """
        query = f"Find candidates matching {profile_name} profile"

        if experience_years is not None and experience_years > 0:
            query += f" with at least {experience_years} years of experience"

        logger.info(
            "Constructed query",
            extra={
                "profile_name": profile_name,
                "experience_years": experience_years,
                "query": query
            }
        )

        return query

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Execute profile search tool (AC1, AC2, AC5).

        Args:
            arguments: Tool parameters (profile_name, experience_years, top_k)

        Returns:
            List of TextContent with candidate results or error message
        """
        # Extract and validate parameters
        profile_name = arguments.get("profile_name", "").strip()
        experience_years = arguments.get("experience_years")
        top_k = arguments.get("top_k", 5)

        # Validate required parameter
        if not profile_name:
            error_msg = "Parameter 'profile_name' is required and cannot be empty"
            logger.warning("Invalid parameters", extra={"error": error_msg})
            return [TextContent(type="text", text=error_msg)]

        logger.info(
            "Executing search_by_profile",
            extra={
                "profile_name": profile_name,
                "experience_years": experience_years,
                "top_k": top_k
            }
        )

        try:
            # Construct query (AC2)
            query_text = self._construct_query(profile_name, experience_years)

            # Prepare LightRAG API request (AC2)
            # Use hybrid mode for profile matching (combines vector + graph)
            payload = {
                "query": query_text,
                "mode": "hybrid",  # AC2: Use hybrid for profile + experience
                "top_k": int(top_k)
            }

            # Call LightRAG API (AC2) - RULE 9: Async I/O
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(
                    "Calling LightRAG API",
                    extra={
                        "url": f"{self.lightrag_url}/query",
                        "mode": "hybrid",
                        "top_k": top_k
                    }
                )

                response = await client.post(
                    f"{self.lightrag_url}/query",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()

            # Parse and format response (AC2)
            formatted_result = self._format_response(
                result,
                profile_name,
                experience_years,
                top_k
            )

            logger.info(
                "Search completed successfully",
                extra={
                    "profile_name": profile_name,
                    "result_length": len(formatted_result)
                }
            )

            return [TextContent(type="text", text=formatted_result)]

        except httpx.TimeoutException as e:
            # AC5: LightRAG API timeout
            error_msg = (
                f"LightRAG API timeout after {self.timeout.read}s. "
                f"The query may be too complex. Please try again or reduce top_k. "
                f"Error: {str(e)}"
            )
            logger.error(
                "LightRAG API timeout",
                extra={
                    "profile_name": profile_name,
                    "timeout": self.timeout.read,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except httpx.HTTPStatusError as e:
            # AC5: Profile name not found or other HTTP errors
            if e.response.status_code == 404:
                error_msg = (
                    f"Profile '{profile_name}' not found in knowledge base. "
                    f"Please verify the profile name matches a CIGREF IT profile. "
                    f"Common profiles: Cloud Architect, Data Engineer, DevOps Engineer"
                )
            else:
                error_msg = (
                    f"LightRAG API error (HTTP {e.response.status_code}): {str(e)}. "
                    f"Please try again later."
                )

            logger.error(
                "LightRAG API HTTP error",
                extra={
                    "profile_name": profile_name,
                    "status_code": e.response.status_code,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except httpx.HTTPError as e:
            # AC5: Other HTTP errors (connection, etc.)
            error_msg = (
                f"Failed to connect to LightRAG service: {str(e)}. "
                f"Please ensure the LightRAG service is running and try again."
            )
            logger.error(
                "LightRAG API connection error",
                extra={
                    "profile_name": profile_name,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except Exception as e:
            # AC5: Unexpected errors (RULE 6: Custom exceptions)
            error_msg = f"Unexpected error during search: {str(e)}. Please try again."
            logger.error(
                "Unexpected error in search_by_profile",
                extra={
                    "profile_name": profile_name,
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

    def _format_response(
        self,
        result: Any,
        profile_name: str,
        experience_years: Optional[int],
        top_k: int
    ) -> str:
        """
        Format LightRAG response for MCP client (AC2, AC4).

        Args:
            result: Raw LightRAG API response
            profile_name: Profile name searched
            experience_years: Experience filter applied
            top_k: Number of results requested

        Returns:
            Formatted markdown response with candidate matches
        """
        # Check if result is empty (AC5: No candidates match)
        if not result or (isinstance(result, str) and len(result.strip()) < 50):
            return (
                f"## No Candidates Found\n\n"
                f"No candidates found matching profile '{profile_name}'"
                + (f" with {experience_years}+ years experience" if experience_years else "")
                + ".\n\n"
                "**Suggestions:**\n"
                "- Try searching without experience filter\n"
                "- Verify the profile name\n"
                "- Check if CVs have been ingested into the knowledge base"
            )

        # Format successful response (AC4)
        response_lines = [
            f"## Search Results: {profile_name}",
            ""
        ]

        if experience_years:
            response_lines.append(f"**Experience Filter:** {experience_years}+ years")
            response_lines.append("")

        response_lines.append(f"**Results:** Top {top_k} candidates")
        response_lines.append("")
        response_lines.append("---")
        response_lines.append("")

        # LightRAG returns text response - format it nicely
        if isinstance(result, str):
            response_lines.append(result)
        elif isinstance(result, dict):
            # If dict, try to extract meaningful content
            if "response" in result:
                response_lines.append(result["response"])
            elif "results" in result:
                response_lines.append(str(result["results"]))
            else:
                response_lines.append(str(result))
        else:
            response_lines.append(str(result))

        response_lines.append("")
        response_lines.append("---")
        response_lines.append(f"*Query: Find candidates matching {profile_name} profile*")

        return "\n".join(response_lines)


# Module-level instance for easy access
search_by_profile_tool = SearchByProfileTool()
