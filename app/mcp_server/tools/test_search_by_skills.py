"""
Unit and integration tests for search_by_skills MCP tool.

Story 3.3: Validates query construction, API integration, and skill matching logic.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.mcp_server.tools.search_by_skills import SearchBySkillsTool, search_by_skills_tool


class TestSearchBySkillsTool:
    """Test suite for SearchBySkillsTool."""

    def test_tool_definition(self):
        """Test that tool definition matches AC1 specification."""
        tool_def = SearchBySkillsTool.TOOL_DEFINITION

        # Verify tool name
        assert tool_def.name == "search_by_skills"

        # Verify description mentions key features
        assert "specific technical skills" in tool_def.description.lower()
        assert "semantic matching" in tool_def.description.lower()

        # Verify required parameters
        assert "required_skills" in tool_def.inputSchema["properties"]
        assert "required_skills" in tool_def.inputSchema["required"]

        # Verify optional parameters
        assert "preferred_skills" in tool_def.inputSchema["properties"]
        assert "experience_level" in tool_def.inputSchema["properties"]
        assert "top_k" in tool_def.inputSchema["properties"]

        # Verify experience_level enum
        exp_level_schema = tool_def.inputSchema["properties"]["experience_level"]
        assert exp_level_schema["enum"] == ["junior", "mid", "senior"]

    def test_query_construction_basic(self):
        """Test basic query construction with required skills only."""
        tool = SearchBySkillsTool()

        query = tool._construct_query(
            required_skills=["Python", "Machine Learning"]
        )

        # Should construct natural language query
        assert "Python" in query
        assert "Machine Learning" in query
        assert "candidates" in query.lower()
        assert "experience" in query.lower()

    def test_query_construction_with_experience_level(self):
        """Test query construction with experience level (AC2)."""
        tool = SearchBySkillsTool()

        query = tool._construct_query(
            required_skills=["Kubernetes", "AWS"],
            experience_level="senior"
        )

        # Should include experience level
        assert "senior" in query.lower()
        assert "Kubernetes" in query
        assert "AWS" in query

    def test_query_construction_with_preferred_skills(self):
        """Test query construction with preferred skills (AC2)."""
        tool = SearchBySkillsTool()

        query = tool._construct_query(
            required_skills=["Python"],
            preferred_skills=["Docker", "Terraform"]
        )

        # Should include preferred skills
        assert "Python" in query
        assert "Docker" in query
        assert "Terraform" in query
        assert "preferred" in query.lower() or "nice to have" in query.lower()

    def test_query_construction_full_parameters(self):
        """Test query construction with all parameters."""
        tool = SearchBySkillsTool()

        query = tool._construct_query(
            required_skills=["Kubernetes", "AWS"],
            preferred_skills=["Terraform"],
            experience_level="senior"
        )

        # Should include all elements
        assert "senior" in query.lower()
        assert "Kubernetes" in query
        assert "AWS" in query
        assert "Terraform" in query

    @pytest.mark.asyncio
    async def test_execute_missing_required_skills(self):
        """Test validation of missing required_skills parameter (AC1)."""
        tool = SearchBySkillsTool()

        # Test with empty array
        result = await tool.execute({"required_skills": []})
        assert len(result) == 1
        assert "required" in result[0].text.lower()

        # Test with missing parameter
        result = await tool.execute({})
        assert len(result) == 1
        assert "required" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_execute_invalid_experience_level(self):
        """Test validation of experience_level enum (AC1)."""
        tool = SearchBySkillsTool()

        result = await tool.execute({
            "required_skills": ["Python"],
            "experience_level": "expert"  # Invalid - not in enum
        })

        assert len(result) == 1
        assert "invalid" in result[0].text.lower()
        assert "junior, mid, senior" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_execute_success_with_mocked_lightrag(self):
        """Test successful execution with mocked LightRAG API (AC2, AC4)."""
        tool = SearchBySkillsTool()

        # Mock successful LightRAG response
        mock_response = MagicMock()
        mock_response.json.return_value = "Candidate 1: Python expert with 5 years ML experience..."
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await tool.execute({
                "required_skills": ["Python", "Machine Learning"],
                "experience_level": "senior",
                "top_k": 5
            })

            # Verify result formatting
            assert len(result) == 1
            assert "Search Results" in result[0].text
            assert "Python" in result[0].text
            assert "Machine Learning" in result[0].text
            assert "senior" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_execute_empty_results(self):
        """Test graceful handling of empty results (AC5)."""
        tool = SearchBySkillsTool()

        # Mock empty LightRAG response
        mock_response = MagicMock()
        mock_response.json.return_value = ""  # Empty result
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await tool.execute({
                "required_skills": ["NonexistentSkill123"]
            })

            # Verify graceful error message
            assert len(result) == 1
            assert "No candidates found" in result[0].text or "No Candidates Found" in result[0].text
            assert "Try broadening criteria" in result[0].text or "Suggestions" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_api_timeout(self):
        """Test handling of LightRAG API timeout (AC5)."""
        tool = SearchBySkillsTool()

        with patch('httpx.AsyncClient') as mock_client:
            # Mock timeout exception
            import httpx
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            result = await tool.execute({
                "required_skills": ["Python"]
            })

            # Verify timeout error handling
            assert len(result) == 1
            assert "timeout" in result[0].text.lower()
            assert "try again" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_execute_http_error(self):
        """Test handling of HTTP errors (AC5)."""
        tool = SearchBySkillsTool()

        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP error
            import httpx
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
            )

            result = await tool.execute({
                "required_skills": ["Python"]
            })

            # Verify HTTP error handling
            assert len(result) == 1
            assert "error" in result[0].text.lower()
            assert "500" in result[0].text or "HTTP" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_connection_error(self):
        """Test handling of connection errors (AC5)."""
        tool = SearchBySkillsTool()

        with patch('httpx.AsyncClient') as mock_client:
            # Mock connection error
            import httpx
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            result = await tool.execute({
                "required_skills": ["Python"]
            })

            # Verify connection error handling
            assert len(result) == 1
            assert "connect" in result[0].text.lower() or "connection" in result[0].text.lower()
            assert "service is running" in result[0].text.lower()

    def test_module_level_instance(self):
        """Test that module-level instance is properly initialized."""
        assert search_by_skills_tool is not None
        assert isinstance(search_by_skills_tool, SearchBySkillsTool)
        assert search_by_skills_tool.TOOL_DEFINITION.name == "search_by_skills"


# Manual integration test script (run separately with live services)
async def manual_integration_test():
    """
    Manual integration test for Story 3.3 validation scenarios.

    Prerequisites:
    - LightRAG service running on http://lightrag:9621
    - Knowledge base populated with CVs containing test skills

    Validation Scenarios (from Story 3.3):
    1. Required skills match: Query ["Python", "Machine Learning"]
    2. Semantic matching: Query ["Kubernetes"] matches "K8s"
    3. Experience level filtering: Query with experience_level="senior"
    4. Preferred skills ranking: Candidates with preferred skills ranked higher
    5. Empty results: Query ["NonexistentSkill123"] returns graceful message
    """
    tool = SearchBySkillsTool()

    print("\n=== Story 3.3 Manual Integration Tests ===\n")

    # Scenario 1: Required skills match
    print("Scenario 1: Required skills match (Python + Machine Learning)")
    result = await tool.execute({
        "required_skills": ["Python", "Machine Learning"],
        "top_k": 5
    })
    print(result[0].text)
    print("\n" + "="*80 + "\n")

    # Scenario 2: Semantic matching
    print("Scenario 2: Semantic matching (Kubernetes -> K8s)")
    result = await tool.execute({
        "required_skills": ["Kubernetes"],
        "top_k": 5
    })
    print(result[0].text)
    print("\n" + "="*80 + "\n")

    # Scenario 3: Experience level filtering
    print("Scenario 3: Experience level filtering (senior)")
    result = await tool.execute({
        "required_skills": ["Python", "Machine Learning"],
        "experience_level": "senior",
        "top_k": 5
    })
    print(result[0].text)
    print("\n" + "="*80 + "\n")

    # Scenario 4: Preferred skills
    print("Scenario 4: Preferred skills (Python required, AWS preferred)")
    result = await tool.execute({
        "required_skills": ["Python"],
        "preferred_skills": ["AWS", "Docker"],
        "top_k": 5
    })
    print(result[0].text)
    print("\n" + "="*80 + "\n")

    # Scenario 5: Empty results
    print("Scenario 5: Empty results (NonexistentSkill123)")
    result = await tool.execute({
        "required_skills": ["NonexistentSkill123"],
        "top_k": 5
    })
    print(result[0].text)
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Run manual integration tests
    print("Running manual integration tests...")
    print("Note: Requires LightRAG service to be running with populated knowledge base")
    asyncio.run(manual_integration_test())
