# Epic 3: MCP Server & OpenWebUI Integration

> 🎯 **Development Artifacts**: [Epic 3 Card](../epics/epic-3.md) | [Stories 3.1-3.8](../stories/README.md#epic-3-mcp-server--openwebui-integration-8-stories)
>

> 📋 **Architecture References**:
> - [Components - MCP Server](../architecture/components.md#component-3-mcp-server) - MCP protocol implementation
> - [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query) - Query flow
> - [External APIs - Ollama](../architecture/external-apis.md) - LLM integration

**Epic Goal**: Build Model Context Protocol (MCP) server exposing core LightRAG-CV tools, configure OpenWebUI to discover and invoke MCP tools, enable end-to-end natural language querying from chat interface to candidate results, and validate conversational refinement capabilities.

## Story 3.1: MCP Server Scaffold and Protocol Implementation

**As a** developer,
**I want** MCP server skeleton implementing the Model Context Protocol specification,
**so that** I can expose tools and resources to MCP-compatible clients like OpenWebUI.

### Acceptance Criteria

1. MCP server implementation created in `/services/mcp-server/` using:
   - Python with `mcp` library, OR
   - TypeScript with `@modelcontextprotocol/sdk`
   - Decision based on OpenWebUI compatibility testing (Week 1 technical spike findings)

2. MCP server implements protocol fundamentals:
   - Server initialization and capability negotiation
   - Tool discovery mechanism (list available tools)
   - Tool invocation handler (receive requests, return responses)
   - Resource serving capability (for match explanations)
   - Error handling per MCP specification

3. Docker service definition added to `docker-compose.yml`:
   - Port mapping (default 3000, configurable via `.env`)
   - Environment variables for LightRAG API endpoint
   - Depends on `lightrag` service

4. MCP server starts successfully and exposes protocol endpoint

5. Basic connectivity test using MCP client or curl validates:
   - Server responds to capability negotiation
   - Tool discovery returns empty list (tools added in subsequent stories)
   - Health check endpoint returns success

6. Documentation added to `/docs/mcp-server.md` describing architecture and protocol flow

## Story 3.2: Core Search Tool - Profile Match Query

**As a** recruiter,
**I want** to query for candidates matching a specific CIGREF profile,
**so that** I can find candidates aligned to standardized job requirements.

### Acceptance Criteria

1. MCP tool implemented: `search_by_profile`
   - Parameters:
     - `profile_name` (string): CIGREF profile name (e.g., "Cloud Architect")
     - `experience_years` (optional number): Minimum years of experience
     - `top_k` (optional number, default 5): Number of results to return
   - Returns: List of candidate matches with IDs and brief summaries

2. Tool implementation:
   - Translates parameters to LightRAG API query
   - Uses LightRAG's "local" or "hybrid" retrieval mode (targets entities directly related to profile)
   - Calls LightRAG REST API with constructed query
   - Parses response and formats as structured JSON for MCP client

3. Tool exposed via MCP protocol (appears in tool discovery list)

4. Manual test validates functionality:
   - Invoke `search_by_profile` with profile_name="Cloud Architect"
   - Returns 5 relevant candidates from knowledge base
   - Response includes candidate IDs and summary text

5. Error handling for edge cases:
   - Profile name not found → returns helpful error message
   - No candidates match criteria → returns empty list with explanation
   - LightRAG API timeout → returns error with retry guidance

6. Tool schema documented with parameter descriptions and example invocations

## Story 3.3: Core Search Tool - Multi-Criteria Skill Search

**As a** recruiter,
**I want** to query for candidates by specific skills and technologies,
**so that** I can find candidates with precise technical expertise regardless of profile classification.

### Acceptance Criteria

1. MCP tool implemented: `search_by_skills`
   - Parameters:
     - `required_skills` (array of strings): Must-have skills (e.g., ["Kubernetes", "AWS"])
     - `preferred_skills` (optional array of strings): Nice-to-have skills
     - `experience_level` (optional enum: "junior", "mid", "senior")
     - `top_k` (optional number, default 5): Number of results
   - Returns: List of candidate matches with skill overlap details

2. Tool implementation:
   - Constructs natural language query from structured parameters (e.g., "Find candidates with Kubernetes and AWS experience at senior level")
   - Calls LightRAG API with appropriate retrieval mode (likely "hybrid" for multi-criteria)
   - Post-processes results to highlight skill matches
   - Ranks candidates by skill coverage

3. Tool handles semantic similarity:
   - Query for "Kubernetes" should surface candidates mentioning "K8s" or "container orchestration"
   - Relies on LightRAG's embedding-based semantic search

4. Manual test validates:
   - Query: required_skills=["Python", "Machine Learning"], experience_level="senior"
   - Returns candidates with relevant skills
   - Results show which required/preferred skills each candidate possesses

5. Empty results handled gracefully (e.g., "No candidates found with required skill combination. Try broadening criteria.")

6. Tool registered in MCP protocol and documented with usage examples

## Story 3.4: OpenWebUI Configuration and MCP Integration

**As a** recruiter,
**I want** OpenWebUI connected to the MCP server and able to discover LightRAG-CV tools,
**so that** I can interact with the system through a conversational chat interface.

### Acceptance Criteria

1. OpenWebUI installed and running (external service or Docker container based on Week 1 technical spike)

2. OpenWebUI configured to connect to MCP server:
   - MCP server endpoint configured in OpenWebUI settings
   - Connection protocol/transport validated (stdio, SSE, or HTTP based on compatibility)
   - Authentication handled if required (likely none for POC single-user)

3. OpenWebUI successfully discovers MCP tools:
   - Can see `search_by_profile` tool in available tools list
   - Can see `search_by_skills` tool in available tools list
   - Tool descriptions and parameters visible

4. Manual test of tool invocation from OpenWebUI:
   - Type query in chat that should trigger tool (e.g., "Find Cloud Architects with 5+ years experience")
   - OpenWebUI's LLM interprets query and invokes `search_by_profile` tool
   - Results returned from MCP server and displayed in chat

5. Error messages from MCP server render clearly in OpenWebUI chat interface

6. Documentation in `/docs/openwebui-setup.md`:
   - OpenWebUI installation instructions
   - MCP server configuration steps
   - Screenshots or examples of successful tool invocation
   - Troubleshooting common connection issues

## Story 3.5: Natural Language Query Interpretation

**As a** recruiter,
**I want** to ask questions in plain English without knowing tool names or parameters,
**so that** the system feels conversational and natural.

### Acceptance Criteria

1. OpenWebUI's LLM (configured to use Ollama qwen3:8b or OpenWebUI's default model) successfully interprets natural language queries and invokes appropriate MCP tools:
   - "Show me senior DevOps engineers with AWS and Terraform" → `search_by_skills` with parsed parameters
   - "Find candidates matching Cloud Architect profile" → `search_by_profile`
   - "Who has Kubernetes experience?" → `search_by_skills` with required_skills=["Kubernetes"]

2. Query interpretation tested with 10 sample natural language queries covering:
   - Profile-based searches
   - Skill-based searches
   - Multi-criteria combinations
   - Varied phrasings (formal vs casual)

3. Success rate documented:
   - Target: 70%+ of test queries invoke correct tool with reasonable parameters
   - Failures analyzed (ambiguous queries, misinterpreted criteria, tool selection errors)

4. Query interpretation limitations documented in `/docs/query-capabilities.md`:
   - Types of queries that work well
   - Query patterns that struggle
   - Tips for users to phrase effective queries

5. If interpretation quality below 70%, mitigation documented:
   - Tool description refinement
   - System prompt tuning for OpenWebUI
   - Consider larger Ollama model (qwen2.5:14b) for better parsing
   - Acceptable limitation for POC if edge cases

6. Successful queries demonstrate end-to-end flow: Chat input → LLM interprets → MCP tool invoked → LightRAG retrieval → Results in chat

## Story 3.6: Conversational Query Refinement

**As a** recruiter,
**I want** to refine my search with follow-up questions in the same chat session,
**so that** I can iteratively narrow results without starting over.

### Acceptance Criteria

1. Multi-turn conversation support validated:
   - Initial query: "Find senior cloud architects"
   - Follow-up: "Now show only those with AWS certification"
   - Follow-up: "Which have 8+ years experience?"
   - System maintains context and refines results progressively

2. Context handling mechanisms:
   - OpenWebUI maintains conversation history (built-in capability)
   - LLM uses conversation context to interpret follow-up queries
   - MCP tool invocations reflect refined criteria

3. Test scenarios covering:
   - Adding filter criteria (narrowing results)
   - Removing/relaxing criteria (broadening results)
   - Switching focus (e.g., from profile search to skill search mid-conversation)
   - Asking clarifying questions about results

4. Conversational refinement tested with 5 multi-turn scenarios:
   - Each scenario has 3-5 turns
   - Final results correctly reflect cumulative refinements
   - Success: 4 out of 5 scenarios work as expected

5. Limitations documented:
   - How many turns can the system maintain context reliably?
   - When does context window become issue?
   - Known failure modes (e.g., contradictory refinements)

6. User guidance added to documentation: Best practices for conversational search (explicit vs. implicit refinement)

## Story 3.7: Result Rendering and Display in Chat

**As a** recruiter,
**I want** candidate results displayed clearly in the chat interface with key information highlighted,
**so that** I can quickly assess matches without being overwhelmed by data.

### Acceptance Criteria

1. MCP tool responses formatted for optimal OpenWebUI rendering:
   - Use markdown formatting (headings, bold, lists, tables)
   - Structured layout: Candidate name/ID, key skills, experience summary, match reason
   - Concise (each candidate result: 3-5 lines) with option to expand

2. Result format includes:
   - Candidate identifier (e.g., "Candidate #12" or filename)
   - Top 3-5 matching skills/competencies
   - Experience level or years
   - Brief match explanation (1 sentence: "Matched due to Kubernetes and AWS expertise")
   - Link or reference for viewing full details (Story 3.8 or Epic 4)

3. Multiple results rendered as numbered list or structured cards

4. Empty results display helpful message:
   - "No candidates found matching your criteria. Try broadening your search or adjusting requirements."

5. Long result sets (10+ candidates) handled gracefully:
   - Option to paginate or initially show top 5 with "Show more" capability
   - Or progressive rendering in chat

6. Manual review of 5 different query result renderings:
   - All are readable and scannable
   - Key information stands out visually
   - No information overload or truncation of critical data

7. Example result rendering documented in `/docs/result-format.md` with screenshots or markdown examples

## Story 3.8: Basic Candidate Detail View

**As a** recruiter,
**I want** to view detailed information about a specific candidate from search results,
**so that** I can make informed decisions about candidate suitability.

### Acceptance Criteria

1. MCP tool implemented: `get_candidate_details`
   - Parameters:
     - `candidate_id` (string): Identifier from search results
   - Returns: Full candidate information including parsed CV content

2. Candidate detail includes:
   - Complete skills list
   - Work history (companies, roles, durations, descriptions)
   - Education and certifications
   - Projects or notable accomplishments
   - Original CV content or parsed structured data

3. Tool callable from OpenWebUI chat:
   - After seeing search results, user can ask: "Show me details for Candidate #3"
   - OpenWebUI interprets and invokes `get_candidate_details`
   - Full details rendered in chat (may be lengthy, uses collapsible sections or markdown formatting)

4. Manual test:
   - Search returns 5 candidates
   - Request details for one candidate
   - Details are comprehensive and readable

5. Detail view uses markdown formatting for structure:
   - Headings for sections (Skills, Experience, Education)
   - Tables for structured data if appropriate
   - Readable on desktop and tablet displays

6. If CV content is very long, truncate with "View full CV" instruction (full details could be added in Phase 2)

---
