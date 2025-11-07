# Source Tree

**Repository Type:** Monorepo
**Organization Strategy:** Service-based directories with shared configuration at root level

## Complete Project Structure

```plaintext
lightrag-cv/
├── .env.example                      # Environment variable template
├── .env                              # Actual environment config (DO NOT COMMIT)
├── .gitignore                        # Git exclusions
├── docker-compose.yml                # Main orchestration file
├── docker-compose.gpu.yml            # GPU profile overrides
├── README.md                         # Project overview and setup
├── LICENSE
│
├── services/                         # Microservices implementations
│   ├── docling/                      # Docling REST API service
│   │   ├── Dockerfile
│   │   ├── Dockerfile.gpu
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── lightrag/                     # LightRAG service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   ├── storage/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── mcp-server/                   # MCP protocol server
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── server.py
│   │   │   ├── tools/
│   │   │   ├── services/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   └── postgres/                     # PostgreSQL configuration
│       ├── Dockerfile
│       ├── init/
│       │   ├── 01-init-db.sql
│       │   └── 02-create-tables.sql
│       └── conf/
│           └── postgresql.conf
│
├── data/                             # Data files (NOT committed)
│   ├── cigref/
│   ├── cvs/
│   └── lightrag/
│
├── docs/                             # Documentation
│   ├── prd.md
│   ├── architecture.md               # This document
│   ├── setup.md
│   └── testing/
│
├── scripts/                          # Infrastructure scripts only (Epic 2.5)
│   ├── setup.sh                      # Environment setup
│   ├── health-check.sh               # Service health checks (shell)
│   ├── health-check.py               # Service health checks (Python)
│   ├── start-docling-gpu.sh          # Start Docling with GPU
│   ├── restart-docling-gpu.sh        # Restart Docling GPU service
│   └── validate-ollama.py            # Validate Ollama connectivity
│
├── app/                              # Application workflows (Epic 2.5)
│   ├── __init__.py
│   ├── README.md                     # Application documentation
│   ├── requirements.txt              # Application dependencies
│   ├── pyproject.toml                # Python project configuration
│   │
│   ├── shared/                       # Shared services and utilities
│   │   ├── __init__.py
│   │   ├── config.py                 # Centralized configuration (multi-provider)
│   │   └── llm_client.py             # LLM provider abstraction (Ollama, OpenAI, LiteLLM)
│   │
│   ├── cigref_ingest/                # CIGREF nomenclature workflows
│   │   ├── __init__.py
│   │   ├── cigref_1_parse.py         # CIGREF parsing via Docling
│   │   └── cigref_2_import.py        # CIGREF ingestion to LightRAG
│   │
│   ├── cv_ingest/                    # CV processing workflows
│   │   ├── __init__.py
│   │   ├── cv1_download.py           # CV dataset download
│   │   ├── cv2_parse.py              # CV parsing via Docling
│   │   ├── cv3_classify.py           # CV classification using LLM
│   │   ├── cv4_import.py             # CV ingestion to LightRAG
│   │   └── create_parsed_manifest.py # Manifest generation
│   │
│   └── tests/                        # Tests and development artifacts
│       ├── __init__.py
│       ├── README.md
│       ├── query-entities.sql        # Entity query examples
│       └── test_llm_client.py        # LLM client tests
│
└── volumes/                          # Docker volume mount points
    └── postgres-data/
```

## Key Structural Decisions (Epic 2.5)

### Infrastructure vs. Application Separation

**scripts/**: Infrastructure scripts for environment setup and service management. NO workflow logic.

**app/**: All data processing workflows organized by domain (CIGREF vs. CV) with shared utilities.

### Numbered Workflow Naming Convention

Scripts follow `{domain}{step}_{action}.py` pattern:
- CIGREF: `cigref_1_parse.py`, `cigref_2_import.py`
- CV: `cv1_download.py`, `cv2_parse.py`, `cv3_classify.py`, `cv4_import.py`

Numbers indicate execution order within workflow.

### LLM Abstraction Layer

`app/shared/llm_client.py` provides unified interface for multiple LLM providers:
- Ollama (local)
- OpenAI-compatible APIs (LiteLLM, remote)
- Configured via `app/shared/config.py`

See [Tech Stack](tech-stack.md) for provider details and [Coding Standards](coding-standards.md) for usage patterns.

---
