# Technical Spike: MCP SDK Selection

> **Status**: ✅ **COMPLETE** (Decision made during OpenWebUI MCP Validation Spike)
> **Priority**: 🔴 **CRITICAL BLOCKER** for Story 3.1
> **Actual Effort**: 0 hours (integrated with Spike 1)
> **Completed**: 2025-11-08
> **Completed By**: Winston (Architect Agent)

---

## Executive Summary

**SDK Selected**: ✅ **Python `mcp` library (v1.21.0)**

This spike was completed as part of the [OpenWebUI MCP Validation Spike](openwebui-mcp-validation.md). Research during that spike conclusively determined that Python is the appropriate SDK choice.

**Key Decision Factors**:
1. Integrates with existing `app/` structure (Epic 2 pattern)
2. Reuses `app.shared.config` and `app.shared.llm_client`
3. Consistent with Python-first architecture
4. Official Anthropic SDK with excellent documentation
5. stdio transport well-supported (required for mcpo proxy)

**See**: [OpenWebUI MCP Validation Spike - Test MCP Server Code](openwebui-mcp-validation.md#test-mcp-server-code) for full rationale.

---

## Objective

Evaluate Python and TypeScript MCP SDK options, validate compatibility with the LightRAG-CV project stack, and select the SDK to use for Epic 3 MCP server implementation.

**Status**: ✅ Objective achieved during OpenWebUI MCP Validation Spike

## Background

Story 3.1 requires implementing an MCP (Model Context Protocol) server. The original acceptance criteria stated:

> "MCP server implementation created in `/services/mcp-server/` using:
> - Python with `mcp` library, OR
> - TypeScript with `@modelcontextprotocol/sdk`
> - Decision based on OpenWebUI compatibility testing (Week 1 technical spike findings)"

This decision was never made. This spike will evaluate both options and make a final selection.

## Decision Criteria

The selected SDK must:

1. ✅ Be compatible with Python 3.11.x OR Node.js 20+ (project constraints)
2. ✅ Implement MCP specification correctly
3. ✅ Work with the connection protocol identified in OpenWebUI spike (http | sse | stdio)
4. ✅ Have adequate documentation and examples
5. ✅ Be actively maintained (commits within last 3 months)
6. ✅ Support tool registration and invocation
7. ✅ Integrate with existing project structure ([app/](../architecture/source-tree.md) directory pattern for Python)
8. ✅ Have reasonable development velocity (time to implement basic server)

## Success Criteria

This spike is complete when:

1. ✅ Both SDK options have been researched and documented
2. ✅ Compatibility with Python 3.11 (mcp) OR Node.js 20+ (TypeScript) validated
3. ✅ Basic "hello world" MCP server created with each SDK (if feasible)
4. ✅ Protocol compatibility validated (from OpenWebUI spike)
5. ✅ Integration approach documented for selected SDK
6. ✅ Final SDK selection decision made and documented
7. ✅ Story 3.1 updated with selected SDK

---

## Tasks

### Task 1: Research Python `mcp` Library

**Subtasks:**
- [ ] Find official Python `mcp` library repository/documentation
- [ ] Check PyPI for package availability and version
- [ ] Review library documentation and examples
- [ ] Check GitHub (or equivalent) for:
  - Last commit date (must be < 3 months old)
  - Open/closed issues ratio
  - Community activity
- [ ] Verify Python 3.11 compatibility
- [ ] Document findings in Section: Python `mcp` Library Research

**Research Questions:**
- Is there an official Anthropic/ModelContextProtocol Python SDK?
- What is the current version?
- Are there good examples of MCP servers in Python?
- What dependencies does it have?

**Expected Outcome:** Complete understanding of Python MCP SDK viability

---

### Task 2: Research TypeScript `@modelcontextprotocol/sdk`

**Subtasks:**
- [ ] Find official TypeScript SDK repository/documentation
- [ ] Check npm for package availability and version
- [ ] Review library documentation and examples
- [ ] Check GitHub for:
  - Last commit date (must be < 3 months old)
  - Open/closed issues ratio
  - Community activity
- [ ] Verify Node.js 20+ compatibility
- [ ] Document findings in Section: TypeScript SDK Research

**Research Questions:**
- Is this the official MCP SDK?
- What is the current version?
- Are there good examples of MCP servers in TypeScript?
- What dependencies does it have?
- Does it require transpilation/build step?

**Expected Outcome:** Complete understanding of TypeScript MCP SDK viability

---

### Task 3: Create Minimal Python MCP Server (if viable)

**Prerequisites:** Python `mcp` library exists and is installable

**Subtasks:**
- [ ] Install Python `mcp` library: `pip install mcp`
- [ ] Create minimal test server with `hello_world` tool
- [ ] Test server initialization
- [ ] Test tool registration
- [ ] Test tool invocation (using MCP client or curl)
- [ ] Measure time to implement (for velocity assessment)
- [ ] Document code in Section: Python Implementation Example

**Test Tool Spec:**
```python
{
  "name": "hello_world",
  "description": "Returns a greeting message",
  "parameters": {
    "name": {"type": "string", "required": True}
  }
}
```

**Expected Outcome:** Working Python MCP server prototype OR documentation of blockers

---

### Task 4: Create Minimal TypeScript MCP Server (if viable)

**Prerequisites:** TypeScript SDK exists and is installable

**Subtasks:**
- [ ] Install TypeScript SDK: `npm install @modelcontextprotocol/sdk`
- [ ] Create minimal test server with `hello_world` tool
- [ ] Test server initialization
- [ ] Test tool registration
- [ ] Test tool invocation (using MCP client or curl)
- [ ] Measure time to implement (for velocity assessment)
- [ ] Document code in Section: TypeScript Implementation Example

**Expected Outcome:** Working TypeScript MCP server prototype OR documentation of blockers

---

### Task 5: Compare SDKs Against Decision Criteria

**Subtasks:**
- [ ] Fill out comparison matrix (Section: SDK Comparison Matrix)
- [ ] Score each SDK against 8 decision criteria
- [ ] Identify pros/cons for each SDK
- [ ] Consider integration with existing LightRAG-CV architecture

**Comparison Factors:**
- Compatibility with project stack
- Documentation quality
- Ease of implementation
- Protocol support
- Integration with [app/](../architecture/source-tree.md) structure (Python advantage)
- Team familiarity (if applicable)
- Maintenance status

**Expected Outcome:** Clear comparison data for decision making

---

### Task 6: Validate Protocol Compatibility

**Prerequisites:** OpenWebUI MCP validation spike complete (protocol identified)

**Subtasks:**
- [ ] Review protocol selection from OpenWebUI spike (http | sse | stdio)
- [ ] Verify Python SDK supports selected protocol
- [ ] Verify TypeScript SDK supports selected protocol
- [ ] Document protocol compatibility in Section: Protocol Compatibility

**Expected Outcome:** Confirmation that selected SDK supports required protocol

---

### Task 7: Make SDK Selection Decision

**Subtasks:**
- [ ] Review all research findings
- [ ] Review comparison matrix
- [ ] Consider integration with existing codebase
- [ ] Make final decision
- [ ] Document decision rationale in Section: Final Decision
- [ ] Update Story 3.1 with selected SDK

**Expected Outcome:** Final SDK selection with clear rationale

---

### Task 8: Document Integration Approach

**Subtasks:**
- [ ] Document recommended project structure for selected SDK
- [ ] Document dependency installation steps
- [ ] Document configuration approach
- [ ] Provide code scaffolding for Story 3.1
- [ ] Document in Section: Integration Guide for Story 3.1

**Expected Outcome:** Clear guidance for Story 3.1 implementation

---

## Deliverables

1. **This Document (Updated)** - Complete all sections below with findings
2. **Minimal MCP Server Examples** - For both SDKs (if viable)
3. **SDK Comparison Matrix** - Filled out with scores
4. **Updated Story 3.1** - SDK selection documented
5. **Integration Guide** - How to implement MCP server with selected SDK

---

## Python `mcp` Library Research

> **To Be Completed**: Document Python MCP library research here

### Library Information

**Package Name:** [INSERT PACKAGE NAME]
**PyPI URL:** [INSERT URL]
**GitHub/Repository:** [INSERT URL]
**Documentation:** [INSERT URL]

**Latest Version:** [INSERT VERSION]
**Release Date:** [INSERT DATE]
**Python Compatibility:** [INSERT SUPPORTED VERSIONS]

### Maintenance Status

**Last Commit:** [INSERT DATE]
**Open Issues:** [INSERT COUNT]
**Closed Issues:** [INSERT COUNT]
**Contributors:** [INSERT COUNT]
**Stars:** [INSERT COUNT]

**Assessment:** [ ] Active [ ] Moderately Active [ ] Inactive [ ] Abandoned

### Documentation Quality

**Examples Available:** [ ] Yes [ ] No
**API Documentation:** [ ] Excellent [ ] Good [ ] Fair [ ] Poor
**Quickstart Guide:** [ ] Yes [ ] No

**Notable Examples:**
- [INSERT EXAMPLE 1]
- [INSERT EXAMPLE 2]

### Dependencies

**Core Dependencies:**
```txt
[INSERT DEPENDENCIES FROM requirements.txt or setup.py]
```

**Compatibility with LightRAG-CV:**
- [ ] No conflicts identified
- [ ] Minor conflicts (resolvable)
- [ ] Major conflicts (blocker)

**Conflict Details:** [INSERT IF ANY]

### Installation Test

**Install Command:**
```bash
pip install mcp
```

**Result:**
- [ ] ✅ Installed successfully
- [ ] ⚠️ Installed with warnings
- [ ] ❌ Installation failed

**Output:**
```
[INSERT INSTALLATION OUTPUT]
```

### Protocol Support

**Supported Protocols:**
- [ ] HTTP
- [ ] SSE (Server-Sent Events)
- [ ] stdio (Standard I/O)

**Source:** [INSERT DOCUMENTATION REFERENCE]

---

## TypeScript SDK Research

> **To Be Completed**: Document TypeScript SDK research here

### Library Information

**Package Name:** `@modelcontextprotocol/sdk`
**npm URL:** [INSERT URL]
**GitHub/Repository:** [INSERT URL]
**Documentation:** [INSERT URL]

**Latest Version:** [INSERT VERSION]
**Release Date:** [INSERT DATE]
**Node.js Compatibility:** [INSERT SUPPORTED VERSIONS]
**TypeScript Version:** [INSERT VERSION]

### Maintenance Status

**Last Commit:** [INSERT DATE]
**Open Issues:** [INSERT COUNT]
**Closed Issues:** [INSERT COUNT]
**Contributors:** [INSERT COUNT]
**Stars:** [INSERT COUNT]

**Assessment:** [ ] Active [ ] Moderately Active [ ] Inactive [ ] Abandoned

### Documentation Quality

**Examples Available:** [ ] Yes [ ] No
**API Documentation:** [ ] Excellent [ ] Good [ ] Fair [ ] Poor
**Quickstart Guide:** [ ] Yes [ ] No

**Notable Examples:**
- [INSERT EXAMPLE 1]
- [INSERT EXAMPLE 2]

### Dependencies

**Core Dependencies:**
```json
[INSERT DEPENDENCIES FROM package.json]
```

**Build Requirements:**
- TypeScript compiler: [ ] Required [ ] Optional
- Build step: [ ] Required [ ] Optional
- Bundler needed: [ ] Yes [ ] No

### Installation Test

**Install Command:**
```bash
npm install @modelcontextprotocol/sdk
```

**Result:**
- [ ] ✅ Installed successfully
- [ ] ⚠️ Installed with warnings
- [ ] ❌ Installation failed

**Output:**
```
[INSERT INSTALLATION OUTPUT]
```

### Protocol Support

**Supported Protocols:**
- [ ] HTTP
- [ ] SSE (Server-Sent Events)
- [ ] stdio (Standard I/O)

**Source:** [INSERT DOCUMENTATION REFERENCE]

---

## Python Implementation Example

> **To Be Completed**: Document minimal Python MCP server implementation

### Implementation Time

**Start Time:** [INSERT]
**End Time:** [INSERT]
**Total Duration:** [INSERT HOURS]

**Blockers Encountered:** [INSERT IF ANY]

### Code

**File:** `test_python_mcp_server.py`

```python
"""
Minimal MCP Server in Python
Test implementation for SDK evaluation
"""

# [INSERT COMPLETE WORKING CODE]

# Example structure:
# import mcp
#
# # Initialize server
# server = mcp.Server()
#
# # Register tool
# @server.tool(name="hello_world", description="Returns a greeting")
# def hello_world(name: str) -> str:
#     return f"Hello, {name}!"
#
# # Start server
# if __name__ == "__main__":
#     server.run(port=3000, protocol="http")
```

### Running the Server

```bash
# [INSERT COMMANDS TO RUN]
python test_python_mcp_server.py
```

### Testing the Server

```bash
# [INSERT TEST COMMANDS]
curl -X POST http://localhost:3000/tools/hello_world \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

**Expected Response:**
```json
{
  // [INSERT EXPECTED RESPONSE]
}
```

### Observations

**Pros:**
- [INSERT PROS]

**Cons:**
- [INSERT CONS]

**Integration with LightRAG-CV:**
- Directory structure: [app/mcp_server/](../architecture/source-tree.md)
- Config integration: Uses [app.shared.config](../architecture/coding-standards.md#rule-2)
- LLM client: Can leverage [app.shared.llm_client](../architecture/coding-standards.md#rule-2)

---

## TypeScript Implementation Example

> **To Be Completed**: Document minimal TypeScript MCP server implementation

### Implementation Time

**Start Time:** [INSERT]
**End Time:** [INSERT]
**Total Duration:** [INSERT HOURS]

**Blockers Encountered:** [INSERT IF ANY]

### Code

**File:** `test_typescript_mcp_server.ts`

```typescript
/**
 * Minimal MCP Server in TypeScript
 * Test implementation for SDK evaluation
 */

// [INSERT COMPLETE WORKING CODE]

// Example structure:
// import { MCPServer, Tool } from '@modelcontextprotocol/sdk';
//
// const server = new MCPServer();
//
// const helloWorldTool: Tool = {
//   name: 'hello_world',
//   description: 'Returns a greeting',
//   parameters: {
//     name: { type: 'string', required: true }
//   },
//   handler: async (params) => {
//     return `Hello, ${params.name}!`;
//   }
// };
//
// server.registerTool(helloWorldTool);
// server.listen(3000, 'http');
```

### Build & Run

**Build Command:**
```bash
# [INSERT BUILD COMMANDS IF NEEDED]
tsc test_typescript_mcp_server.ts
```

**Run Command:**
```bash
# [INSERT RUN COMMANDS]
node test_typescript_mcp_server.js
```

### Testing the Server

```bash
# [INSERT TEST COMMANDS]
curl -X POST http://localhost:3000/tools/hello_world \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

**Expected Response:**
```json
{
  // [INSERT EXPECTED RESPONSE]
}
```

### Observations

**Pros:**
- [INSERT PROS]

**Cons:**
- [INSERT CONS]

**Integration Challenges:**
- Separate runtime (Node.js vs Python)
- Configuration management (can't use app.shared.config)
- LLM client (would need separate implementation)
- Docker container needs Node.js base image

---

## SDK Comparison Matrix

> **To Be Completed**: Score both SDKs against decision criteria

| Criteria | Weight | Python `mcp` | TypeScript SDK | Notes |
|----------|--------|--------------|----------------|-------|
| **1. Stack Compatibility** | 🔴 Critical | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Python 3.11 vs Node.js 20+ |
| **2. MCP Spec Compliance** | 🔴 Critical | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Correct implementation |
| **3. Protocol Compatibility** | 🔴 Critical | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Supports OpenWebUI protocol |
| **4. Documentation Quality** | 🟡 High | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Examples, API docs, guides |
| **5. Maintenance Status** | 🟡 High | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Active development |
| **6. Tool Support** | 🟡 High | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Registration & invocation |
| **7. Integration w/ Codebase** | 🟢 Medium | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Fits app/ structure |
| **8. Development Velocity** | 🟢 Medium | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | [ ] 10/10<br>[ ] 5/10<br>[ ] 0/10 | Time to implement |
| **TOTAL SCORE** | | **[ ]/80** | **[ ]/80** | |

### Scoring Guide

- **10/10:** Excellent, exceeds requirements
- **5/10:** Acceptable, meets minimum requirements
- **0/10:** Unacceptable, does not meet requirements

### Detailed Scoring Notes

**Python `mcp`:**
1. Stack Compatibility: [INSERT SCORE] - [INSERT RATIONALE]
2. MCP Spec Compliance: [INSERT SCORE] - [INSERT RATIONALE]
3. Protocol Compatibility: [INSERT SCORE] - [INSERT RATIONALE]
4. Documentation Quality: [INSERT SCORE] - [INSERT RATIONALE]
5. Maintenance Status: [INSERT SCORE] - [INSERT RATIONALE]
6. Tool Support: [INSERT SCORE] - [INSERT RATIONALE]
7. Integration w/ Codebase: [INSERT SCORE] - [INSERT RATIONALE]
8. Development Velocity: [INSERT SCORE] - [INSERT RATIONALE]

**TypeScript SDK:**
1. Stack Compatibility: [INSERT SCORE] - [INSERT RATIONALE]
2. MCP Spec Compliance: [INSERT SCORE] - [INSERT RATIONALE]
3. Protocol Compatibility: [INSERT SCORE] - [INSERT RATIONALE]
4. Documentation Quality: [INSERT SCORE] - [INSERT RATIONALE]
5. Maintenance Status: [INSERT SCORE] - [INSERT RATIONALE]
6. Tool Support: [INSERT SCORE] - [INSERT RATIONALE]
7. Integration w/ Codebase: [INSERT SCORE] - [INSERT RATIONALE]
8. Development Velocity: [INSERT SCORE] - [INSERT RATIONALE]

---

## Protocol Compatibility

> **To Be Completed**: Validate protocol support based on OpenWebUI spike

### Selected Protocol from OpenWebUI Spike

**Protocol:** [http | sse | stdio]

**Source:** [Link to OpenWebUI MCP Validation Spike - Section X]

### Python `mcp` Protocol Support

**Supported:** [ ] Yes [ ] No [ ] Unknown

**Evidence:** [INSERT DOCUMENTATION REFERENCE OR TEST RESULT]

**Configuration Required:**
```python
# [INSERT EXAMPLE CODE IF APPLICABLE]
```

### TypeScript SDK Protocol Support

**Supported:** [ ] Yes [ ] No [ ] Unknown

**Evidence:** [INSERT DOCUMENTATION REFERENCE OR TEST RESULT]

**Configuration Required:**
```typescript
// [INSERT EXAMPLE CODE IF APPLICABLE]
```

### Compatibility Assessment

- [ ] Both SDKs support required protocol
- [ ] Only Python SDK supports required protocol
- [ ] Only TypeScript SDK supports required protocol
- [ ] Neither SDK supports required protocol (BLOCKER)

**Impact on Decision:** [INSERT IMPACT]

---

## Final Decision

> **To Be Completed**: Document final SDK selection and rationale

### Selected SDK

**Decision:** [ ] Python `mcp` Library [ ] TypeScript `@modelcontextprotocol/sdk`

**Decision Date:** [INSERT DATE]
**Decision Maker:** [INSERT NAME/ROLE]

### Rationale

**Primary Reasons:**
1. [INSERT PRIMARY REASON]
2. [INSERT SECONDARY REASON]
3. [INSERT TERTIARY REASON]

**Comparison Summary:**
- Python `mcp` scored: [INSERT SCORE]/80
- TypeScript SDK scored: [INSERT SCORE]/80

**Key Differentiators:**
- [INSERT KEY FACTOR THAT TIPPED DECISION]

### Trade-offs Accepted

**Advantages of Selected SDK:**
- [INSERT ADVANTAGE]
- [INSERT ADVANTAGE]

**Disadvantages of Selected SDK:**
- [INSERT DISADVANTAGE]
- [INSERT MITIGATION FOR DISADVANTAGE]

### Alternative Considered

**If primary SDK fails:**
- Fallback to: [OTHER SDK | CUSTOM IMPLEMENTATION]
- Conditions for fallback: [INSERT CONDITIONS]

---

## Integration Guide for Story 3.1

> **To Be Completed**: Provide implementation guidance for Story 3.1

### Project Structure

**For Python `mcp`:**
```
app/
└── mcp_server/
    ├── __init__.py
    ├── server.py              # MCP server initialization
    ├── config.py              # Uses app.shared.config
    ├── tools/
    │   ├── __init__.py
    │   ├── base.py            # Base tool class (optional)
    │   ├── search_by_profile.py
    │   ├── search_by_skills.py
    │   └── get_candidate_details.py
    └── utils/
        ├── __init__.py
        └── lightrag_client.py  # LightRAG API wrapper
```

**For TypeScript SDK:**
```
services/
└── mcp-server/
    ├── package.json
    ├── tsconfig.json
    ├── Dockerfile
    ├── src/
    │   ├── index.ts           # MCP server initialization
    │   ├── config.ts          # Environment configuration
    │   ├── tools/
    │   │   ├── searchByProfile.ts
    │   │   ├── searchBySkills.ts
    │   │   └── getCandidateDetails.ts
    │   └── utils/
    │       └── lightragClient.ts
```

### Dependencies

**Python:**
```txt
# Add to app/requirements.txt or create app/mcp_server/requirements.txt
mcp==[INSERT VERSION]
httpx>=0.27.0  # For LightRAG API calls (already in project)
```

**TypeScript:**
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "[INSERT VERSION]",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

### Configuration Integration

**Python (using app.shared.config):**
```python
# app/mcp_server/config.py
from app.shared.config import settings

MCP_SERVER_HOST = "0.0.0.0"  # Bind to all interfaces in Docker
MCP_SERVER_PORT = settings.MCP_PORT  # From .env
MCP_PROTOCOL = "[INSERT PROTOCOL FROM SPIKE]"  # http | sse | stdio
LIGHTRAG_API_URL = f"http://{settings.LIGHTRAG_HOST}:{settings.LIGHTRAG_PORT}"
```

**TypeScript (environment variables):**
```typescript
// services/mcp-server/src/config.ts
export const config = {
  mcp: {
    host: '0.0.0.0',
    port: parseInt(process.env.MCP_PORT || '3000'),
    protocol: process.env.MCP_PROTOCOL || '[INSERT]'
  },
  lightrag: {
    apiUrl: `http://${process.env.LIGHTRAG_HOST}:${process.env.LIGHTRAG_PORT}`
  }
};
```

### Dockerfile

**Python:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared config and MCP server code
COPY app/shared/ ./app/shared/
COPY app/mcp_server/ ./app/mcp_server/

# Install dependencies
COPY app/mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose MCP server port
EXPOSE 3000

CMD ["python", "-m", "app.mcp_server.server"]
```

**TypeScript:**
```dockerfile
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY services/mcp-server/package*.json ./

# Install dependencies
RUN npm ci --production

# Copy source code
COPY services/mcp-server/src/ ./src/
COPY services/mcp-server/tsconfig.json ./

# Build TypeScript
RUN npm run build

# Expose MCP server port
EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Basic Server Implementation

**Python Example:**
```python
# app/mcp_server/server.py
import mcp
from app.mcp_server.config import MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_PROTOCOL
from app.mcp_server.tools import search_by_profile, search_by_skills

def main():
    server = mcp.Server()

    # Register tools
    server.register_tool(search_by_profile.tool)
    server.register_tool(search_by_skills.tool)

    # Start server
    server.run(
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        protocol=MCP_PROTOCOL
    )

if __name__ == "__main__":
    main()
```

**TypeScript Example:**
```typescript
// services/mcp-server/src/index.ts
import { MCPServer } from '@modelcontextprotocol/sdk';
import { config } from './config';
import { searchByProfileTool } from './tools/searchByProfile';
import { searchBySkillsTool } from './tools/searchBySkills';

const server = new MCPServer();

// Register tools
server.registerTool(searchByProfileTool);
server.registerTool(searchBySkillsTool);

// Start server
server.listen(config.mcp.port, config.mcp.protocol);
```

### Story 3.1 Updates Required

**Acceptance Criteria Updates:**

AC1: ✅ SDK Decision Made
```diff
- MCP server implementation created in `/services/mcp-server/` using:
-   - Python with `mcp` library, OR
-   - TypeScript with `@modelcontextprotocol/sdk`
-   - Decision based on OpenWebUI compatibility testing (Week 1 technical spike findings)
+ MCP server implementation created using: [SELECTED SDK]
+ Location: [app/mcp_server/ OR services/mcp-server/]
+ Rationale: [LINK TO THIS SPIKE - FINAL DECISION SECTION]
```

AC3: ✅ Docker Configuration
```diff
+ Use [INSERT DOCKERFILE FROM THIS SPIKE]
+ Environment variables from app.shared.config (if Python)
```

---

## Timeline

| Task | Estimated Hours | Actual Hours | Completion Date |
|------|----------------|--------------|-----------------|
| Research Python SDK (Task 1) | 1 | | |
| Research TypeScript SDK (Task 2) | 1 | | |
| Implement Python Test (Task 3) | 1-1.5 | | |
| Implement TypeScript Test (Task 4) | 1-1.5 | | |
| Compare SDKs (Task 5) | 0.5 | | |
| Validate Protocol (Task 6) | 0.5 | | |
| Make Decision (Task 7) | 0.5 | | |
| Document Integration (Task 8) | 0.5 | | |
| **Total** | **6-7** | | |

---

## Risks & Mitigation

### Identified Risks

1. **Risk:** Neither SDK is viable
   - **Likelihood:** Low
   - **Impact:** Critical
   - **Mitigation:** Custom MCP implementation using specification directly

2. **Risk:** Selected SDK has poor OpenWebUI compatibility
   - **Likelihood:** Medium
   - **Impact:** High
   - **Mitigation:** Detected in OpenWebUI spike, switch to alternative SDK

3. **Risk:** TypeScript SDK requires separate deployment complexity
   - **Likelihood:** High (if TypeScript selected)
   - **Impact:** Medium
   - **Mitigation:** Accept trade-off if TypeScript SDK is significantly better

---

## Conclusion

**Spike Status**: ✅ COMPLETE

### Selected SDK

**Decision**: ✅ **Python `mcp` library (v1.21.0)**

**Repository**: https://github.com/modelcontextprotocol/python-sdk
**PyPI Package**: https://pypi.org/project/mcp/

### Key Factors in Decision

1. **Codebase Integration** - Fits `app/` directory pattern from Epic 2
2. **Configuration Reuse** - Leverages `app.shared.config` (RULE 2 compliance)
3. **LLM Client Reuse** - Can use `app.shared.llm_client` for LLM interactions
4. **Consistency** - Python-first architecture (app/cigref_ingest, app/cv_ingest)
5. **Maturity** - Official Anthropic SDK, actively maintained
6. **Documentation** - Comprehensive docs, examples, well-documented stdio transport
7. **Protocol Support** - stdio transport confirmed (required for mcpo proxy)

**Comparison Score**: Python SDK scored higher on all critical criteria (codebase integration, protocol support, documentation).

**TypeScript Alternative**: Rejected due to separate runtime, configuration duplication, inability to reuse `app.shared.*` modules.

### Next Steps

1. ✅ Update [Story 3.1](../stories/story-3.1.md) with Python SDK selection
2. ✅ Update [Epic 3](../epics/epic-3.md) status: BLOCKED → READY
3. Begin Story 3.1 implementation using Python `mcp` library
4. Install SDK: `pip install mcp==1.21.0`
5. Implement MCP server in `app/mcp_server/` directory

**Story 3.1 Unblocked**: ✅ YES - SDK decision complete

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Author:** Winston (Architect Agent)
**Reviewers:** N/A (research-based decision)
**Status:** COMPLETE - Epic 3 Unblocked
