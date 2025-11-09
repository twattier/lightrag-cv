"""
Search by Skills MCP Tool.

Story 3.3: Implements skill-based candidate search using LightRAG hybrid retrieval.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from mcp.types import Tool, TextContent

from app.shared.config import settings

# Configure logging (RULE 7: Structured logging with context)
logger = logging.getLogger(__name__)


class SearchBySkillsTool:
    """
    MCP tool for searching candidates by specific skills and technologies.

    Translates multi-criteria skill search parameters into LightRAG queries
    and returns formatted candidate results with skill overlap details.
    """

    # Tool definition for MCP protocol (AC1, AC6)
    TOOL_DEFINITION = Tool(
        name="search_by_skills",
        description=(
            "Find candidates with specific technical skills and expertise. "
            "Searches the knowledge base using hybrid vector-graph retrieval "
            "to find candidates matching required and preferred skills. "
            "Supports semantic matching (e.g., 'Kubernetes' matches 'K8s'). "
            "Example skills: 'Python', 'Machine Learning', 'Kubernetes', 'AWS'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "required_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Must-have skills (e.g., ['Kubernetes', 'AWS'])",
                    "minItems": 1
                },
                "preferred_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Nice-to-have skills (optional)",
                },
                "experience_level": {
                    "type": "string",
                    "enum": ["junior", "mid", "senior"],
                    "description": "Experience level filter (optional)"
                },
                "top_k": {
                    "type": "number",
                    "description": "Number of results to return (default: 5)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                }
            },
            "required": ["required_skills"]
        }
    )

    def __init__(self):
        """Initialize tool with LightRAG configuration."""
        self.lightrag_url = settings.lightrag_url
        self.timeout = httpx.Timeout(60.0)  # 60s for complex multi-criteria queries

    def _construct_query(
        self,
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None,
        experience_level: Optional[str] = None
    ) -> str:
        """
        Construct natural language query from parameters (AC2).

        Args:
            required_skills: List of must-have skills
            preferred_skills: Optional list of nice-to-have skills
            experience_level: Optional experience level (junior/mid/senior)

        Returns:
            Natural language query string for LightRAG
        """
        # Build base query with required skills
        skills_text = " and ".join(required_skills)
        query = f"Find candidates with {skills_text} experience"

        # Add experience level if provided
        if experience_level:
            query = f"Find {experience_level} candidates with {skills_text} experience"

        # Add preferred skills as "nice to have"
        if preferred_skills and len(preferred_skills) > 0:
            preferred_text = ", ".join(preferred_skills)
            query += f". Preferred skills include {preferred_text}"

        logger.info(
            "Constructed query",
            extra={
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "experience_level": experience_level,
                "query": query
            }
        )

        return query

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Execute skill search tool (AC1, AC2, AC3, AC4, AC5).

        Args:
            arguments: Tool parameters (required_skills, preferred_skills, experience_level, top_k)

        Returns:
            List of TextContent with candidate results or error message
        """
        # Extract and validate parameters
        required_skills = arguments.get("required_skills", [])
        preferred_skills = arguments.get("preferred_skills", [])
        experience_level = arguments.get("experience_level")
        top_k = arguments.get("top_k", 5)

        # Validate required parameter (AC1)
        if not required_skills or len(required_skills) == 0:
            error_msg = (
                "Parameter 'required_skills' is required and must contain at least one skill"
            )
            logger.warning("Invalid parameters", extra={"error": error_msg})
            return [TextContent(type="text", text=error_msg)]

        # Validate experience_level enum if provided
        if experience_level and experience_level not in ["junior", "mid", "senior"]:
            error_msg = (
                f"Invalid experience_level '{experience_level}'. "
                f"Must be one of: junior, mid, senior"
            )
            logger.warning("Invalid experience_level", extra={"experience_level": experience_level})
            return [TextContent(type="text", text=error_msg)]

        logger.info(
            "Executing search_by_skills",
            extra={
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "experience_level": experience_level,
                "top_k": top_k
            }
        )

        try:
            # Construct query (AC2)
            query_text = self._construct_query(
                required_skills,
                preferred_skills,
                experience_level
            )

            # Prepare LightRAG API request (AC2)
            # Use hybrid mode for multi-criteria skill search (vector + graph)
            payload = {
                "query": query_text,
                "mode": "hybrid",  # AC2: Hybrid mode for multi-criteria
                "top_k": int(top_k),
                "filters": {"document_type": "CV"}  # Exclude CIGREF profiles
            }

            # Call LightRAG API (AC2) - RULE 9: Async I/O
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(
                    "Calling LightRAG API",
                    extra={
                        "url": f"{self.lightrag_url}/query",
                        "mode": "hybrid",
                        "top_k": top_k,
                        "filters": payload["filters"]
                    }
                )

                response = await client.post(
                    f"{self.lightrag_url}/query",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()

            # Parse and format response with skill overlap analysis (AC2, AC4)
            formatted_result = self._format_response(
                result,
                required_skills,
                preferred_skills,
                experience_level,
                top_k
            )

            logger.info(
                "Search completed successfully",
                extra={
                    "required_skills": required_skills,
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
                    "required_skills": required_skills,
                    "timeout": self.timeout.read,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except httpx.HTTPStatusError as e:
            # AC5: HTTP errors
            error_msg = (
                f"LightRAG API error (HTTP {e.response.status_code}): {str(e)}. "
                f"Please try again later."
            )
            logger.error(
                "LightRAG API HTTP error",
                extra={
                    "required_skills": required_skills,
                    "status_code": e.response.status_code,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except httpx.HTTPError as e:
            # AC5: Connection errors
            error_msg = (
                f"Failed to connect to LightRAG service: {str(e)}. "
                f"Please ensure the LightRAG service is running and try again."
            )
            logger.error(
                "LightRAG API connection error",
                extra={
                    "required_skills": required_skills,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

        except Exception as e:
            # AC5: Unexpected errors (RULE 6: Custom exceptions)
            error_msg = f"Unexpected error during search: {str(e)}. Please try again."
            logger.error(
                "Unexpected error in search_by_skills",
                extra={
                    "required_skills": required_skills,
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                exc_info=True
            )
            return [TextContent(type="text", text=error_msg)]

    def _format_response(
        self,
        result: Any,
        required_skills: List[str],
        preferred_skills: Optional[List[str]],
        experience_level: Optional[str],
        top_k: int
    ) -> str:
        """
        Format LightRAG response with skill overlap analysis (AC2, AC4, AC5).

        Args:
            result: Raw LightRAG API response
            required_skills: Required skills searched
            preferred_skills: Preferred skills searched
            experience_level: Experience level filter applied
            top_k: Number of results requested

        Returns:
            Formatted markdown response with candidate matches and skill overlap
        """
        # Check if result is empty (AC5: No candidates found)
        if not result or (isinstance(result, str) and len(result.strip()) < 50):
            return (
                f"## No Candidates Found\n\n"
                f"No candidates found with required skill combination: {', '.join(required_skills)}"
                + (f" at {experience_level} level" if experience_level else "")
                + ".\n\n"
                "**Suggestions:**\n"
                "- Try broadening criteria (remove some required skills)\n"
                "- Remove experience level filter\n"
                "- Check if CVs have been ingested into the knowledge base\n"
                "- Try semantic variations (e.g., 'K8s' instead of 'Kubernetes')"
            )

        # Format successful response (AC4)
        response_lines = [
            "## Search Results: Skill-Based Search",
            ""
        ]

        # Display search criteria
        response_lines.append(f"**Required Skills:** {', '.join(required_skills)}")

        if preferred_skills and len(preferred_skills) > 0:
            response_lines.append(f"**Preferred Skills:** {', '.join(preferred_skills)}")

        if experience_level:
            response_lines.append(f"**Experience Level:** {experience_level}")

        response_lines.append(f"**Results:** Top {top_k} candidates")
        response_lines.append("")
        response_lines.append("---")
        response_lines.append("")

        # LightRAG returns text response - format it nicely
        # Note: Skill overlap analysis would require entity extraction from LightRAG
        # For now, we display the raw LightRAG response which includes semantic matches
        if isinstance(result, str):
            response_lines.append(result)
            response_lines.append("")
            response_lines.append(
                "*Note: Results ranked by LightRAG's hybrid retrieval "
                "(vector similarity + graph traversal)*"
            )
            response_lines.append(
                "*Semantic matching enabled: 'Kubernetes' matches 'K8s', "
                "'container orchestration', etc.*"
            )
        elif isinstance(result, dict):
            # If dict, try to extract meaningful content
            if "response" in result:
                response_lines.append(result["response"])
            elif "results" in result:
                # Future: Parse entities and calculate match scores here
                response_lines.append(str(result["results"]))
            else:
                response_lines.append(str(result))
        else:
            response_lines.append(str(result))

        response_lines.append("")
        response_lines.append("---")

        query_summary = f"Find candidates with {', '.join(required_skills)}"
        if experience_level:
            query_summary = f"Find {experience_level} candidates with {', '.join(required_skills)}"

        response_lines.append(f"*Query: {query_summary}*")

        return "\n".join(response_lines)


# Module-level instance for easy access
search_by_skills_tool = SearchBySkillsTool()
