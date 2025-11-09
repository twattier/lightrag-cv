"""
Tests for search_by_profile MCP tool.

Story 3.2: Test coverage for profile-based candidate search.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.mcp_server.tools.search_by_profile import SearchByProfileTool


@pytest.fixture
def tool():
    """Create SearchByProfileTool instance for testing."""
    return SearchByProfileTool()


@pytest.mark.asyncio
async def test_construct_query_basic(tool):
    """Test query construction with profile name only."""
    query = tool._construct_query("Cloud Architect")
    assert query == "Find candidates matching Cloud Architect profile"


@pytest.mark.asyncio
async def test_construct_query_with_experience(tool):
    """Test query construction with experience filter."""
    query = tool._construct_query("Cloud Architect", experience_years=5)
    assert query == "Find candidates matching Cloud Architect profile with at least 5 years of experience"


@pytest.mark.asyncio
async def test_construct_query_with_zero_experience(tool):
    """Test query construction with zero experience (should be ignored)."""
    query = tool._construct_query("Data Engineer", experience_years=0)
    assert query == "Find candidates matching Data Engineer profile"


@pytest.mark.asyncio
async def test_execute_missing_profile_name(tool):
    """Test error handling for missing profile_name."""
    arguments = {}
    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "profile_name" in result[0].text.lower()
    assert "required" in result[0].text.lower()


@pytest.mark.asyncio
async def test_execute_empty_profile_name(tool):
    """Test error handling for empty profile_name."""
    arguments = {"profile_name": "   "}
    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "profile_name" in result[0].text.lower()
    assert "required" in result[0].text.lower()


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_successful_search(mock_client_class, tool):
    """Test successful search with valid response."""
    # Mock httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.json.return_value = "Candidate 1: John Doe with 5 years AWS experience.\nCandidate 2: Jane Smith with 7 years cloud architecture experience."
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Cloud Architect",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "Cloud Architect" in result[0].text
    assert "Candidate 1" in result[0].text or "John Doe" in result[0].text


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_with_experience_filter(mock_client_class, tool):
    """Test search with experience filter."""
    mock_response = MagicMock()
    mock_response.json.return_value = "Senior candidate with 8 years experience"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "DevOps Engineer",
        "experience_years": 5,
        "top_k": 3
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "5+" in result[0].text or "years" in result[0].text.lower()


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_empty_results(mock_client_class, tool):
    """Test handling of empty results."""
    mock_response = MagicMock()
    mock_response.json.return_value = ""
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Nonexistent Profile",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "No Candidates Found" in result[0].text or "No candidates found" in result[0].text


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_timeout_error(mock_client_class, tool):
    """Test handling of LightRAG API timeout."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Cloud Architect",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "timeout" in result[0].text.lower()
    assert "try again" in result[0].text.lower()


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_404_error(mock_client_class, tool):
    """Test handling of 404 profile not found."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=mock_response
        )
    )

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Invalid Profile",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "not found" in result[0].text.lower()
    assert "CIGREF" in result[0].text


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_http_error(mock_client_class, tool):
    """Test handling of HTTP connection errors."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Cloud Architect",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "connect" in result[0].text.lower() or "service" in result[0].text.lower()


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_execute_unexpected_error(mock_client_class, tool):
    """Test handling of unexpected errors."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(side_effect=ValueError("Unexpected error"))

    mock_client_class.return_value = mock_client

    arguments = {
        "profile_name": "Cloud Architect",
        "top_k": 5
    }

    result = await tool.execute(arguments)

    assert len(result) == 1
    assert "unexpected" in result[0].text.lower() or "error" in result[0].text.lower()


def test_tool_definition():
    """Test that TOOL_DEFINITION is properly configured."""
    tool = SearchByProfileTool()

    assert tool.TOOL_DEFINITION.name == "search_by_profile"
    assert "CIGREF" in tool.TOOL_DEFINITION.description
    assert "profile_name" in tool.TOOL_DEFINITION.inputSchema["properties"]
    assert "experience_years" in tool.TOOL_DEFINITION.inputSchema["properties"]
    assert "top_k" in tool.TOOL_DEFINITION.inputSchema["properties"]
    assert "profile_name" in tool.TOOL_DEFINITION.inputSchema["required"]
